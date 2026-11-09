#!/usr/bin/env python3
"""
OpenRouter image generation client for Claude Code skills.

Calls the dedicated OpenRouter Images API (POST /api/v1/images) and saves the
returned image(s) to disk. Default model is OpenAI's newest GPT Image tier on
OpenRouter; pass --model auto to resolve the newest openai/gpt-image-* model at
run time.

Auth: reads OPENROUTER_API_KEY from the environment, or from the file
~/.openrouter_api_key (first line), or from --api-key-file.

Examples
  python openrouter_image.py --prompt "a red panda astronaut" --out ./out
  python openrouter_image.py --prompt-file brief.txt --aspect-ratio 2:3 --quality high
  python openrouter_image.py --prompt "make it navy" --ref poster_v1.png --out ./out
  python openrouter_image.py --list-models
  python openrouter_image.py --model auto --prompt "..." --dry-run
"""

from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import os
import pathlib
import sys
import time
import urllib.error
import urllib.request

API_BASE = "https://openrouter.ai/api/v1"
IMAGES_URL = f"{API_BASE}/images"
MODELS_URL = f"{API_BASE}/images/models"

# Newest OpenAI image model on OpenRouter at the time of writing (2026-09-17).
# "sunburst" is the precision tier, "flare" is the speed tier.
DEFAULT_MODEL = "openai/gpt-image-2.5-sunburst"
FALLBACK_MODELS = [
    "openai/gpt-image-2.5-flare",
    "openai/gpt-image-2",
    "openai/gpt-image-1",
]

# Aspect ratios accepted by the GPT Image 2.x family on OpenRouter.
ASPECT_RATIOS = ["1:1", "3:2", "2:3", "4:3", "3:4", "16:9", "9:16", "21:9", "auto"]
QUALITIES = ["auto", "low", "medium", "high", "xhigh", "max"]
BACKGROUNDS = ["auto", "transparent", "opaque"]
OUTPUT_FORMATS = ["png", "jpeg", "webp"]


def eprint(*args: object) -> None:
    print(*args, file=sys.stderr)


def load_api_key(explicit_file: str | None) -> str:
    key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if key:
        return key
    candidates = []
    if explicit_file:
        candidates.append(pathlib.Path(explicit_file))
    candidates.append(pathlib.Path.home() / ".openrouter_api_key")
    for path in candidates:
        try:
            if path.is_file():
                text = path.read_text(encoding="utf-8").strip().splitlines()
                if text and text[0].strip():
                    return text[0].strip()
        except OSError:
            continue
    # Windows: a key saved with `setx` is not visible to processes started before it
    # was set (e.g. an already-running Claude Code app). Read it from the registry.
    if sys.platform == "win32":
        try:
            import winreg

            for hive, subkey in (
                (winreg.HKEY_CURRENT_USER, r"Environment"),
                (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment"),
            ):
                try:
                    with winreg.OpenKey(hive, subkey) as reg:
                        value, _ = winreg.QueryValueEx(reg, "OPENROUTER_API_KEY")
                        if isinstance(value, str) and value.strip():
                            return value.strip()
                except OSError:
                    continue
        except ImportError:
            pass
    eprint(
        "ERROR: no OpenRouter API key found.\n"
        "Set the OPENROUTER_API_KEY environment variable (PowerShell: "
        "setx OPENROUTER_API_KEY \"sk-or-...\" then open a new terminal), or\n"
        "write the key on the first line of ~/.openrouter_api_key, or pass --api-key-file."
    )
    sys.exit(2)


def http_json(url: str, api_key: str | None, payload: dict | None = None, timeout: int = 600) -> dict:
    headers = {
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/LEON-gittech/Skill2Poster",
        "X-Title": "Claude Code openrouter-imagegen",
    }
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(url, data=data, headers=headers, method="POST" if data else "GET")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        try:
            parsed = json.loads(body)
            msg = parsed.get("error", {}).get("message", body)
        except ValueError:
            msg = body
        raise RuntimeError(f"HTTP {exc.code} from {url}: {msg}") from None


def list_image_models(api_key: str | None, only_openai: bool = False) -> list[dict]:
    raw = http_json(MODELS_URL, api_key)
    models = raw.get("data", raw) if isinstance(raw, dict) else raw
    if only_openai:
        models = [m for m in models if str(m.get("id", "")).startswith("openai/")]
    models.sort(key=lambda m: m.get("created", 0), reverse=True)
    return models


def resolve_auto_model(api_key: str | None) -> str:
    models = list_image_models(api_key, only_openai=True)
    gpt_image = [m for m in models if "gpt-image" in str(m.get("id", ""))]
    if not gpt_image:
        eprint(f"WARN: could not find any openai/gpt-image-* model; using {DEFAULT_MODEL}")
        return DEFAULT_MODEL
    chosen = gpt_image[0]["id"]
    eprint(f"auto model -> {chosen}")
    return chosen


def file_to_data_url(path: str) -> str:
    p = pathlib.Path(path)
    if not p.is_file():
        eprint(f"ERROR: reference image not found: {path}")
        sys.exit(2)
    mime, _ = mimetypes.guess_type(p.name)
    if not mime or not mime.startswith("image/"):
        mime = "image/png"
    b64 = base64.b64encode(p.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{b64}"


def build_payload(args: argparse.Namespace, prompt: str, model: str) -> dict:
    payload: dict = {"model": model, "prompt": prompt, "n": args.n}
    if args.aspect_ratio != "auto":
        payload["aspect_ratio"] = args.aspect_ratio
    if args.quality != "auto":
        payload["quality"] = args.quality
    if args.background != "auto":
        payload["background"] = args.background
    if args.output_format:
        payload["output_format"] = args.output_format
    if args.output_compression is not None:
        payload["output_compression"] = args.output_compression
    if args.seed is not None:
        payload["seed"] = args.seed
    if args.resolution:
        payload["resolution"] = args.resolution
    if args.ref:
        payload["input_references"] = [
            {"type": "image_url", "image_url": {"url": r if r.startswith("http") else file_to_data_url(r)}}
            for r in args.ref
        ]
    return payload


def ext_for(media_type: str, fallback: str) -> str:
    mapping = {
        "image/png": "png",
        "image/jpeg": "jpg",
        "image/webp": "webp",
        "image/svg+xml": "svg",
    }
    return mapping.get(media_type, fallback)


def save_images(result: dict, out_dir: pathlib.Path, stem: str, fallback_ext: str) -> list[pathlib.Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    saved: list[pathlib.Path] = []
    items = result.get("data", [])
    if not items:
        raise RuntimeError(f"API returned no images. Full response: {json.dumps(result)[:800]}")
    for idx, item in enumerate(items):
        b64 = item.get("b64_json")
        if not b64 and item.get("url"):
            with urllib.request.urlopen(item["url"], timeout=120) as resp:
                raw = resp.read()
        elif b64:
            raw = base64.b64decode(b64)
        else:
            raise RuntimeError(f"image item {idx} has neither b64_json nor url")
        ext = ext_for(item.get("media_type", ""), fallback_ext)
        suffix = "" if len(items) == 1 else f"_{idx + 1}"
        path = out_dir / f"{stem}{suffix}.{ext}"
        path.write_bytes(raw)
        saved.append(path)
    return saved


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    src = ap.add_mutually_exclusive_group()
    src.add_argument("--prompt", help="prompt text")
    src.add_argument("--prompt-file", help="read the prompt from a UTF-8 text file")
    ap.add_argument("--model", default=DEFAULT_MODEL,
                    help=f"OpenRouter image model id, or 'auto' for newest openai/gpt-image-* (default: {DEFAULT_MODEL})")
    ap.add_argument("--no-fallback", action="store_true", help="do not retry with fallback OpenAI models on failure")
    ap.add_argument("--aspect-ratio", default="auto", choices=ASPECT_RATIOS,
                    help="use 2:3 for A0 portrait posters, 3:2 for landscape")
    ap.add_argument("--quality", default="high", choices=QUALITIES)
    ap.add_argument("--background", default="auto", choices=BACKGROUNDS)
    ap.add_argument("--resolution", default=None, help="optional tier such as 1K, 2K, 4K (provider dependent)")
    ap.add_argument("--output-format", default="png", choices=OUTPUT_FORMATS)
    ap.add_argument("--output-compression", type=int, default=None, help="0-100 for jpeg/webp")
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--n", type=int, default=1, help="number of images (1-10)")
    ap.add_argument("--ref", action="append", default=[],
                    help="reference image path or URL for image-to-image / editing (repeatable, max 16)")
    ap.add_argument("--out", default="./generated_images", help="output directory")
    ap.add_argument("--name", default=None, help="output file stem (default: timestamped)")
    ap.add_argument("--api-key-file", default=None)
    ap.add_argument("--list-models", action="store_true", help="list image models on OpenRouter and exit")
    ap.add_argument("--all-providers", action="store_true", help="with --list-models: include non-OpenAI models")
    ap.add_argument("--dry-run", action="store_true", help="print the request payload and exit without calling the API")
    ap.add_argument("--json", action="store_true", help="print a JSON summary to stdout instead of plain text")
    args = ap.parse_args()

    if args.list_models:
        models = list_image_models(None, only_openai=not args.all_providers)
        for m in models:
            sp = m.get("supported_parameters", {})
            ar = ",".join(sp.get("aspect_ratio", {}).get("values", [])) or "-"
            q = ",".join(sp.get("quality", {}).get("values", [])) or "-"
            print(f"{m.get('id')}\n    created={m.get('created')} aspect={ar} quality={q}")
        return 0

    if args.prompt_file:
        prompt = pathlib.Path(args.prompt_file).read_text(encoding="utf-8").strip()
    elif args.prompt:
        prompt = args.prompt.strip()
    else:
        ap.error("--prompt or --prompt-file is required (or use --list-models)")
        return 2
    if not prompt:
        ap.error("prompt is empty")
        return 2
    if not 1 <= args.n <= 10:
        ap.error("--n must be between 1 and 10")
        return 2
    if len(args.ref) > 16:
        ap.error("at most 16 --ref images are supported")
        return 2

    api_key = None if args.dry_run else load_api_key(args.api_key_file)
    model = resolve_auto_model(api_key) if args.model == "auto" else args.model
    payload = build_payload(args, prompt, model)

    if args.dry_run:
        preview = dict(payload)
        if "input_references" in preview:
            preview["input_references"] = [
                {"type": "image_url", "image_url": {"url": r["image_url"]["url"][:60] + "...(truncated)"}}
                for r in preview["input_references"]
            ]
        print(json.dumps(preview, indent=2, ensure_ascii=False))
        return 0

    out_dir = pathlib.Path(args.out)
    stem = args.name or f"image_{time.strftime('%Y%m%d_%H%M%S')}"
    candidates = [model] + ([] if args.no_fallback else [m for m in FALLBACK_MODELS if m != model])

    last_error: Exception | None = None
    for attempt_model in candidates:
        payload["model"] = attempt_model
        eprint(f"generating with {attempt_model} ...")
        started = time.time()
        try:
            result = http_json(IMAGES_URL, api_key, payload)
            saved = save_images(result, out_dir, stem, args.output_format)
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            eprint(f"  failed: {exc}")
            continue
        elapsed = round(time.time() - started, 1)
        usage = result.get("usage", {})
        summary = {
            "model": attempt_model,
            "files": [str(p.resolve()) for p in saved],
            "elapsed_s": elapsed,
            "cost_usd": usage.get("cost"),
            "total_tokens": usage.get("total_tokens"),
        }
        if args.json:
            print(json.dumps(summary, indent=2))
        else:
            for p in saved:
                print(str(p.resolve()))
            eprint(f"done in {elapsed}s, model={attempt_model}, cost_usd={usage.get('cost')}")
        return 0

    eprint(f"ERROR: all models failed. Last error: {last_error}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
