---
name: openai-imagegen
description: Generate or edit images with GPT Image 2.6 Flare through OpenAI's own Image API, billed to the user's OPENAI_API_KEY with no OpenRouter in between. Use when the user asks for the OpenAI API directly ("pakai OpenAI langsung", "API OpenAI", "key OpenAI saya"), or picks it as the fallback when Grok Imagine (grok-imagegen) is unavailable.
---

# OpenAI ImageGen

One of two fallback routes behind `grok-imagegen`. This one calls OpenAI directly, so usage lands on the user's OpenAI bill; `openrouter-imagegen` reaches the same model family through OpenRouter credits.

- Default model: `gpt-image-2.6-flare` (speed tier). Use `gpt-image-2.6-sunburst` when the user wants maximum detail, layout, or edit accuracy.
- Automatic fallback when the model is unavailable (404) or OpenAI has a server fault (5xx): one retry on `gpt-image-2.5-flare`, without `complexity`. Every other error stops the run; report which model succeeded.
- Script: `scripts/openai_image.py`, Python 3.10+, stdlib only. With Skills Manager the skill stays undeployed, so the folder is `~/.skills-manager/skills/openai-imagegen`.

## Key

The script reads `OPENAI_API_KEY` from the environment, then the first line of `~/.openai_api_key` (or `--api-key-file`), then, on Windows, the user-level variable saved with `setx` straight from the registry, so a key set after Claude Code started still works.

Keys stay out of chat and out of files you write. When the script exits with "no OpenAI API key found", give the user the `setx OPENAI_API_KEY "sk-..."` line and stop.

## Run

```powershell
python "$env:USERPROFILE\.skills-manager\skills\openai-imagegen\scripts\openai_image.py" --prompt-file brief.txt --aspect-ratio 2:3 --out .\generated_images --name poster_v1
```

| Flag | Meaning |
|---|---|
| `--prompt` / `--prompt-file` | prompt text, or a UTF-8 file for long structured prompts |
| `--model` | default `gpt-image-2.6-flare`; `--no-fallback` pins it |
| `--aspect-ratio` | `1:1`, `3:2`, `2:3`, `4:3`, `3:4`, `16:9`, `9:16`, `21:9`, `auto`; mapped to a size |
| `--size` | explicit `WIDTHxHEIGHT` (multiples of 16, longest edge 3840, ratio within 1:3 to 3:1); overrides the ratio |
| `--quality` | `low`, `medium`, `high` (default), `xhigh`, `max`, `auto` |
| `--complexity` | `low`, `medium`, `high`; the API default is `high`, lower renders simpler scenes |
| `--background` | `auto`, `transparent` (png/webp only), `opaque` |
| `--output-format` | `png` (default), `jpeg`, `webp`; `--output-compression 0-100` for jpeg/webp |
| `--ref <path>` | local reference image, repeatable up to 16; switches to the edits endpoint |
| `--mask <path>` | PNG with alpha marking the area to change in the first `--ref` |
| `--n` | 1 to 10 images |
| `--list-models` | the `gpt-image-*` models this key can use |
| `--dry-run` | print the request without calling the API |
| `--json` | summary with files, model, usage, and `estimated_cost_usd` |

The script prints each saved file's absolute path. View every file before using it or handing it over.

## Prompting

- Write the prompt as a spec: subject, composition, style, palette, exact text in quotes, and what to leave out. Long prompts go in `--prompt-file`.
- Edits: pass the current image with `--ref` and describe only the change; add `--mask` to confine it.
- Series: generate one anchor, then derive each variant from it with `--ref` so the style holds.
- Cut-outs: `--background transparent` gives real alpha, so no chroma-key step is needed.
- Posters: `paper-poster-imagegen` owns the prompt; aspect `2:3` portrait, `3:2` landscape.

## Cost

GPT Image 2.6 bills per token: text input $5, image input $8, image output $30 per 1M tokens. A `high` 1024x1536 image runs a few US cents; `xhigh` and `max` cost more, so use them only on request. Tell the user before batches beyond a handful of images, and report `estimated_cost_usd` from the summary.

## Failures

- 401: invalid key. 403: often the organization still needs API Organization Verification at platform.openai.com. Report either and stop.
- 429: `insufficient_quota` means the OpenAI account needs billing credit; otherwise it is a rate limit, so wait and retry once.
- 400: a parameter the model rejects; fix the request instead of retrying.
- Moderation refusal: rephrase the prompt; leave the filter alone.

Image models still distort small text, equations, tables, QR codes, and logos. Anything that must be exact belongs in HTML, SVG, or real assets.
