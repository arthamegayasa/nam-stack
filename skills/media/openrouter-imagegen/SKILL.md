---
name: openrouter-imagegen
description: Generate or edit images with OpenAI's newest GPT Image model via the OpenRouter Images API. Use whenever the user asks to generate, create, draw, render, mock up, or edit an image, illustration, poster mockup, thumbnail, icon, diagram concept, or reference picture, or says "gambar", "generate image", "bikin gambar", "imagegen", "nano banana", or "image generation". This is the only image generation path for Claude Code on this machine (Gemini/nanobanana was removed).
---

# OpenRouter ImageGen

## Purpose

Single entry point for image generation in Claude Code. All image generation goes
through OpenRouter's dedicated Images API and targets OpenAI's newest GPT Image
model. Do not use Gemini, nanobanana, or any other provider for images.

- Endpoint: `POST https://openrouter.ai/api/v1/images`
- Default model: `openai/gpt-image-2.5-sunburst` (precision tier)
- Speed tier: `openai/gpt-image-2.5-flare`
- Fallbacks (automatic): `openai/gpt-image-2`, then `openai/gpt-image-1`
- Script: `~/.claude/skills/openrouter-imagegen/scripts/openrouter_image.py`

The script resolves `--model auto` to the newest `openai/gpt-image-*` model that
OpenRouter lists, so use `auto` when the user asks for "the latest" model.

## Prerequisites

`OPENROUTER_API_KEY` must be available to the script, via one of:

1. Environment variable `OPENROUTER_API_KEY` in the current process.
2. First line of `~/.openrouter_api_key`, or `--api-key-file <path>`.
3. On Windows, the user-level `OPENROUTER_API_KEY` saved with `setx` is read straight from the registry, so it works even when Claude Code was started before the key was set.

Never ask the user to paste the key into chat, and never write a key into any
file yourself. If the script exits with "no OpenRouter API key found", tell the
user how to set it and stop.

Python 3.10+ is required. No third-party packages are needed (stdlib only).

## How To Run

From Git Bash or the Bash tool:

```bash
python ~/.claude/skills/openrouter-imagegen/scripts/openrouter_image.py \
  --prompt "..." --aspect-ratio 2:3 --quality high --out ./generated_images
```

From PowerShell:

```powershell
python "$env:USERPROFILE\.claude\skills\openrouter-imagegen\scripts\openrouter_image.py" --prompt "..." --out .\generated_images
```

Key flags:

| Flag | Meaning |
|------|---------|
| `--prompt` / `--prompt-file` | prompt text, or a UTF-8 file for long structured prompts |
| `--model` | model id, or `auto` for newest OpenAI GPT Image model |
| `--aspect-ratio` | `1:1`, `3:2`, `2:3`, `4:3`, `3:4`, `16:9`, `9:16`, `21:9`, `auto` |
| `--quality` | `auto`, `low`, `medium`, `high` (default), `xhigh`, `max` (2.5 only) |
| `--background` | `auto`, `transparent`, `opaque` |
| `--ref <path-or-url>` | reference image for editing or image-to-image, repeatable up to 16 |
| `--n` | number of images, 1 to 10 |
| `--out` / `--name` | output directory and file stem |
| `--list-models` | print OpenAI image models on OpenRouter with supported parameters |
| `--dry-run` | print the request payload without calling the API |
| `--json` | machine-readable summary on stdout |

The script prints the absolute path of each saved file on stdout. Show the
result to the user with the Read tool or SendUserFile so they can see it.

## Prompting Guidance

- Write the prompt as a structured spec: subject, composition, style, palette, typography, text that must appear (quoted exactly), and an explicit avoid list.
- Long prompts belong in a file passed with `--prompt-file`, not on the command line.
- For posters and layouts, use the `paper-poster-imagegen` skill, which owns the poster prompt template and calls this script.
- For edits, pass the existing image with `--ref` and describe only the change.
- Pick aspect ratio from the deliverable: `2:3` for A0/A1 portrait posters, `3:2` for landscape posters, `16:9` for slides and thumbnails, `1:1` for icons and avatars.
- Use `--quality high` by default. Use `xhigh` or `max` only when the user asks for maximum fidelity, since cost rises with output tokens.

## Cost Awareness

GPT Image 2.5 on OpenRouter bills per token: input text about $5 per 1M tokens,
input image about $8 per 1M tokens, output image about $30 per 1M tokens. A
single high-quality image is typically a few US cents. The script prints
`cost_usd` from the API's usage block after each call. Do not loop many
generations without telling the user.

## Failure Handling

- HTTP 401 or 403: key is missing or invalid. Tell the user, do not retry.
- HTTP 402: insufficient OpenRouter credits. Tell the user.
- HTTP 404 "No image model found": the model id changed. Run `--list-models` and pick the newest `openai/gpt-image-*` id, or use `--model auto`.
- HTTP 429 or 5xx: the script already falls back through the OpenAI model list. Report which model finally succeeded.
- Content moderation refusal: rephrase the prompt, do not attempt to evade the filter.

## Limitations To Tell The User

Image models distort small text, equations, tables, QR codes, and logos. Treat
generated images as visual references or illustrations, not as factual
artifacts. Anything that must be exact belongs in HTML, SVG, or real assets.
