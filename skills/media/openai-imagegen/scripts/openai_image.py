#!/usr/bin/env python3
"""
Direct OpenAI Image API client (no OpenRouter, no Grok).

Text-to-image goes to POST /v1/images/generations as JSON. With --ref the call
goes to POST /v1/images/edits as multipart/form-data, one image[] part per
reference. Saves every returned image and prints its absolute path.

Auth: OPENAI_API_KEY from the environment, else the first line of
~/.openai_api_key or --api-key-file, else (Windows) the user-level variable
saved with `setx`, read from the registry. OPENAI_BASE_URL overrides the API
base, as in the official SDK.

Examples
  python openai_image.py --prompt "a red panda astronaut" --out ./out
  python openai_image.py --prompt-file brief.txt --aspect-ratio 2:3 --quality high
  python openai_image.py --prompt "make the sky navy" --ref v1.png --out ./out
  python openai_image.py --list-models
  python openai_image.py --prompt "..." --dry-run
"""

from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import os
import pathlib
import re
import sys
import time
import urllib.error
import urllib.request
import uuid

DEFAULT_BASE_URL = "https://api.openai.com/v1"

# GPT Image 2.6 launched 2026-11-04. Flare is the speed tier, Sunburst the precision tier.
DEFAULT_MODEL = "gpt-image-2.6-flare"
FALLBACK_MODELS = ["gpt-image-2.5-flare", "gpt-image-2"]
# Only these statuses mean "try another model": unknown model, rate limit, server trouble.
FALLBACK_STATUSES = {404, 429, 500, 502, 503, 504}

# Aspect ratio -> size. Every size keeps both edges a multiple of 16.
ASPECT_SIZES = {
    "1:1": "1024x1024",
    "3:2": "1536x1024",
    "2:3": "1024x1536",
    "4:3": "1280x960",
    "3:4": "960x1280",
    "16:9": "1536x864",
    "9:16": "864x1536",
    "21:9": "1792x768",
}
QUALITIES = ["auto", "low", "medium", "high", "xhigh", "max"]
BACKGROUNDS = ["auto", "transparent", "opaque"]
OUTPUT_FORMATS = ["png", "jpeg", "webp"]
COMPLEXITIES = ["low", "medium", "high"]

# USD per 1M tokens: (text input, image input, image output). Source: OpenAI model pages, 2026-11.
PRICING = {
    "gpt-image-2.6-flare": (5.0, 8.0, 30.0),
    "gpt-image-2.6-sunburst": (5.0, 8.0, 30.0),
    "gpt-image-2.5-flare": (5.0, 8.0, 30.0),
    "gpt-image-2.5-sunburst": (5.0, 8.0, 30.0),
}


class ApiError(RuntimeError):
    def __init__(self, status: int, message: str):
        super().__init__(f"HTTP {status}: {message}")
        self.status = status


def eprint(*args: object) -> None:
    print(*args, file=sys.stderr)


def base_url() -> str:
    return (os.environ.get("OPENAI_BASE_URL") or DEFAULT_BASE_URL).rstrip("/")


def load_api_key(explicit_file: str | None) -> str:
    key = os.environ.get("OPENAI_API_KEY", "").strip()
    if key:
        return key
    candidates = [pathlib.Path(explicit_file)] if explicit_file else []
    candidates.append(pathlib.Path.home() / ".openai_api_key")
    for path in candidates:
        try:
            lines = path.read_text(encoding="utf-8").strip().splitlines()
        except OSError:
            continue
        if lines and lines[0].strip():
            return lines[0].strip()
    # A key saved with `setx` is invisible to processes started before it was set
    # (an already-running Claude Code app), so read it from the registry.
    if sys.platform == "win32" and not os.environ.get("OPENAI_API_KEY_SKIP_REGISTRY"):
        import winreg

        for hive, subkey in (
            (winreg.HKEY_CURRENT_USER, r"Environment"),
            (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment"),
        ):
            try:
                with winreg.OpenKey(hive, subkey) as reg:
                    value, _ = winreg.QueryValueEx(reg, "OPENAI_API_KEY")
            except OSError:
                continue
            if isinstance(value, str) and value.strip():
                return value.strip()
    eprint(
        "ERROR: no OpenAI API key found.\n"
        "Set OPENAI_API_KEY (PowerShell: setx OPENAI_API_KEY \"sk-...\" then open a new terminal), or\n"
        "write the key on the first line of ~/.openai_api_key, or pass --api-key-file."
    )
    sys.exit(2)


def validate_size(size: str) -> str | None:
    """Return an error message when `size` breaks OpenAI's custom-size rules, else None."""
    if size == "auto":
        return None
    match = re.fullmatch(r"(\d+)x(\d+)", size)
    if not match:
        return f"size must look like 1536x1024 or be 'auto', got {size!r}"
    width, height = int(match.group(1)), int(match.group(2))
    if width % 16 or height % 16:
        return f"size {size}: width and height must each be a multiple of 16"
    if max(width, height) > 3840:
        return f"size {size}: the longest edge may be at most 3840"
    if max(width, height) > 3 * min(width, height):
        return f"size {size}: aspect ratio must stay between 1:3 and 3:1"
    if not 655_360 <= width * height <= 8_294_400:
        return f"size {size}: total pixels must be between 655,360 and 8,294,400"
    return None


def request_fields(args: argparse.Namespace, prompt: str, model: str) -> dict:
    fields: dict = {"model": model, "prompt": prompt, "n": args.n}
    size = args.size or ASPECT_SIZES.get(args.aspect_ratio)
    if size and size != "auto":
        fields["size"] = size
    if args.quality != "auto":
        fields["quality"] = args.quality
    if args.background != "auto":
        fields["background"] = args.background
    fields["output_format"] = args.output_format
    if args.output_compression is not None:
        fields["output_compression"] = args.output_compression
    if args.complexity:
        fields["complexity"] = args.complexity
    if args.moderation != "auto":
        fields["moderation"] = args.moderation
    return fields


def upload_files(args: argparse.Namespace) -> list[tuple[str, str]]:
    files = [("image[]", ref) for ref in args.ref]
    if args.mask:
        files.append(("mask", args.mask))
    return files


def multipart_body(fields: dict, files: list[tuple[str, str]]) -> tuple[bytes, str]:
    boundary = f"----openai-imagegen-{uuid.uuid4().hex}"
    parts: list[bytes] = []
    for name, value in fields.items():
        parts.append(
            f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"\r\n\r\n{value}\r\n'.encode("utf-8")
        )
    for name, path_str in files:
        path = pathlib.Path(path_str)
        mime = mimetypes.guess_type(path.name)[0] or "image/png"
        header = (
            f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"; filename="{path.name}"\r\n'
            f"Content-Type: {mime}\r\n\r\n"
        ).encode("utf-8")
        parts.append(header + path.read_bytes() + b"\r\n")
    parts.append(f"--{boundary}--\r\n".encode("utf-8"))
    return b"".join(parts), f"multipart/form-data; boundary={boundary}"


def http(method: str, path: str, api_key: str, body: bytes | None = None,
         content_type: str = "application/json", timeout: int = 600) -> dict:
    headers = {"Authorization": f"Bearer {api_key}"}
    if body is not None:
        headers["Content-Type"] = content_type
    req = urllib.request.Request(base_url() + path, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        text = exc.read().decode("utf-8", errors="replace")
        try:
            message = json.loads(text).get("error", {}).get("message", text)
        except ValueError:
            message = text
        raise ApiError(exc.code, message) from None


def call_api(args: argparse.Namespace, fields: dict, api_key: str) -> dict:
    files = upload_files(args)
    if files:
        body, ctype = multipart_body(fields, files)
        return http("POST", "/images/edits", api_key, body, ctype)
    return http("POST", "/images/generations", api_key, json.dumps(fields).encode("utf-8"))


def save_images(result: dict, out_dir: pathlib.Path, stem: str, output_format: str) -> list[pathlib.Path]:
    items = result.get("data") or []
    if not items:
        raise RuntimeError(f"API returned no images: {json.dumps(result)[:800]}")
    out_dir.mkdir(parents=True, exist_ok=True)
    ext = "jpg" if output_format == "jpeg" else output_format
    saved = []
    for idx, item in enumerate(items):
        if item.get("b64_json"):
            raw = base64.b64decode(item["b64_json"])
        elif item.get("url"):
            with urllib.request.urlopen(item["url"], timeout=120) as resp:
                raw = resp.read()
        else:
            raise RuntimeError(f"image item {idx} has neither b64_json nor url")
        suffix = "" if len(items) == 1 else f"_{idx + 1}"
        path = out_dir / f"{stem}{suffix}.{ext}"
        path.write_bytes(raw)
        saved.append(path.resolve())
    return saved


def estimate_cost(model: str, usage: dict) -> float | None:
    rates = PRICING.get(model)
    if not rates or "output_tokens" not in usage:
        return None
    text_rate, image_rate, output_rate = rates
    details = usage.get("input_tokens_details") or {}
    if details:
        input_cost = details.get("text_tokens", 0) * text_rate + details.get("image_tokens", 0) * image_rate
    else:
        input_cost = usage.get("input_tokens", 0) * text_rate
    return round((input_cost + usage["output_tokens"] * output_rate) / 1_000_000, 6)


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    src = ap.add_mutually_exclusive_group()
    src.add_argument("--prompt", help="prompt text")
    src.add_argument("--prompt-file", help="read the prompt from a UTF-8 text file")
    ap.add_argument("--model", default=DEFAULT_MODEL, help=f"OpenAI image model id (default: {DEFAULT_MODEL})")
    ap.add_argument("--no-fallback", action="store_true", help="never retry with an older model")
    ap.add_argument("--aspect-ratio", default="auto", choices=[*ASPECT_SIZES, "auto"],
                    help="mapped to a size; 2:3 for portrait posters, 3:2 landscape, 16:9 slides")
    ap.add_argument("--size", default=None, help="explicit WIDTHxHEIGHT (multiples of 16, up to 3840) or auto; "
                                                 "overrides --aspect-ratio")
    ap.add_argument("--quality", default="high", choices=QUALITIES)
    ap.add_argument("--complexity", default=None, choices=COMPLEXITIES,
                    help="2.5/2.6 only; the API defaults to high")
    ap.add_argument("--background", default="auto", choices=BACKGROUNDS)
    ap.add_argument("--output-format", default="png", choices=OUTPUT_FORMATS)
    ap.add_argument("--output-compression", type=int, default=None, help="0-100, jpeg/webp only")
    ap.add_argument("--moderation", default="auto", choices=["auto", "low"])
    ap.add_argument("--n", type=int, default=1, help="number of images (1-10)")
    ap.add_argument("--ref", action="append", default=[],
                    help="local reference image for editing (repeatable, max 16); switches to /images/edits")
    ap.add_argument("--mask", default=None, help="PNG mask with alpha, same size as the first --ref")
    ap.add_argument("--out", default="./generated_images", help="output directory")
    ap.add_argument("--name", default=None, help="output file stem (default: timestamped)")
    ap.add_argument("--api-key-file", default=None)
    ap.add_argument("--list-models", action="store_true", help="list gpt-image models your key can use, then exit")
    ap.add_argument("--dry-run", action="store_true", help="print the request and exit without calling the API")
    ap.add_argument("--json", action="store_true", help="print a JSON summary on stdout")
    args = ap.parse_args()

    if args.list_models:
        return args
    if args.prompt_file:
        args.prompt_text = pathlib.Path(args.prompt_file).read_text(encoding="utf-8").strip()
    else:
        args.prompt_text = (args.prompt or "").strip()
    if not args.prompt_text:
        ap.error("--prompt or --prompt-file is required (or use --list-models)")
    if not 1 <= args.n <= 10:
        ap.error("--n must be between 1 and 10")
    if len(args.ref) > 16:
        ap.error("at most 16 --ref images are supported")
    for path in [*args.ref, *([args.mask] if args.mask else [])]:
        if path.startswith(("http://", "https://")):
            ap.error(f"download the image first; --ref and --mask take local files: {path}")
        if not pathlib.Path(path).is_file():
            ap.error(f"image not found: {path}")
    if args.mask and not args.ref:
        ap.error("--mask needs at least one --ref")
    if args.size and (problem := validate_size(args.size)):
        ap.error(problem)
    if args.background == "transparent" and args.output_format == "jpeg":
        ap.error("a transparent background needs --output-format png or webp")
    if args.output_compression is not None and args.output_format == "png":
        ap.error("--output-compression applies to jpeg or webp only")
    return args


def main() -> int:
    args = parse_args()

    if args.list_models:
        models = http("GET", "/models", load_api_key(args.api_key_file)).get("data", [])
        for model in sorted((m for m in models if "gpt-image" in m.get("id", "")),
                            key=lambda m: m.get("created", 0), reverse=True):
            print(f"{model['id']}  created={model.get('created')}")
        return 0

    fields = request_fields(args, args.prompt_text, args.model)
    if args.dry_run:
        files = upload_files(args)
        print(json.dumps({
            "endpoint": "/images/edits" if files else "/images/generations",
            "body": fields,
            "files": [{"field": name, "path": path} for name, path in files],
        }, indent=2, ensure_ascii=False))
        return 0

    api_key = load_api_key(args.api_key_file)
    out_dir = pathlib.Path(args.out)
    stem = args.name or f"image_{time.strftime('%Y%m%d_%H%M%S')}"
    candidates = [args.model] + ([] if args.no_fallback else [m for m in FALLBACK_MODELS if m != args.model])

    for model in candidates:
        fields["model"] = model
        eprint(f"generating with {model} ...")
        started = time.time()
        try:
            result = call_api(args, fields, api_key)
        except ApiError as exc:
            eprint(f"  failed: {exc}")
            if exc.status in FALLBACK_STATUSES and model != candidates[-1]:
                continue
            eprint("ERROR: image request failed.")
            return 1
        saved = save_images(result, out_dir, stem, args.output_format)
        usage = result.get("usage") or {}
        summary = {
            "model": model,
            "files": [str(p) for p in saved],
            "elapsed_s": round(time.time() - started, 1),
            "usage": usage,
            "estimated_cost_usd": estimate_cost(model, usage),
        }
        if args.json:
            print(json.dumps(summary, indent=2))
        else:
            for path in saved:
                print(path)
            eprint(f"done in {summary['elapsed_s']}s, model={model}, "
                   f"estimated_cost_usd={summary['estimated_cost_usd']}")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
