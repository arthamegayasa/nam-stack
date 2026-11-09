---
name: grok-imagegen
description: Generate or edit images with xAI Grok Imagine, the default image route on this machine. Use whenever the user asks to generate, draw, render, or mock up a new image, or to edit, restyle, or derive variants from an existing one (illustration, sprite, icon, thumbnail, poster mockup, reference picture), or says "gambar", "bikin gambar", "generate image", or "imagegen".
---

# Grok Imagegen

Every image goes through xAI Grok Imagine: `image_gen` creates from text, `image_edit` transforms reference images (likeness, style transfer, variants). Only Grok carries these tools, so the route depends on which agent you are.

## Pick the route

| You are | Route |
|---|---|
| Grok (any harness) | Call `image_gen` / `image_edit` yourself and follow **Worker rules**. |
| Claude Code or Codex with T3 Code tools | **Delegate in T3** to a Grok child agent. |
| Any agent with a shell and no T3 tools | **Delegate headless** to the Grok CLI. |

A child agent returns the files to you for inspection and integration. Open a new top-level thread only when the user asks for a separate image session.

## Write the brief

The Grok worker sees only the brief, so it carries everything:

- Destination: absolute folder plus exact filenames.
- Per image: subject, composition, style, palette, aspect ratio (`1:1`, `16:9`, `9:16`, `3:2`, `2:3`, ...), and any text that must appear, quoted exactly; otherwise "no lettering".
- References: absolute paths of images for `image_edit` (style anchor, character sheet, the attempt being corrected).
- Series: one anchor image first, then every variant derived from it with `image_edit`, so the style holds.
- Background: Imagine returns opaque JPEG; ask for a flat `#FF00FF` chroma-key background when the subject will be cut out later.
- Scope: the worker produces and copies image files only; code, git, and other files stay untouched.
- Report: the final message lists each file as `absolute path | tool | prompt | references`, plus the total `image_gen` and `image_edit` call count.

Batch a whole coherent set into one brief. Each worker spawn costs Grok model tokens on top of the Imagine calls, so one worker for twelve sprites beats twelve workers. Run parallel workers only across unrelated sets.

## Delegate in T3

Call `delegate_task` with:

- `target`: `{ providerInstanceId: "grok", model: "grok-4.7-build-fast" }`; `grok-4.7` when the worker must judge art direction itself across a series.
- `role: "design"`, `title: "Images: <subject>"`, default shared isolation so files land in your checkout.
- `mode: "wait"` when your next step needs the images; otherwise async, following the returned `next`.

If `orchestrator_capabilities` lists no usable Grok provider, go to **Fallback**.

## Delegate headless

Write the brief to a file, then run (PowerShell):

```powershell
grok -p "Read and follow the image brief at <absolute brief path>." -m grok-4.7-build-fast --cwd "<project root>" --always-approve --output-format json
```

The JSON `text` field holds the worker's report. Headless Grok carries `image_gen` and `image_edit` (verified on Grok CLI 1.0.77).

## Worker rules

- Game art (sprites, sprite sheets, tilesets, UI, icons): read your bundled `game-assets` skill first.
- Each call returns the saved image's absolute path inside the Grok session folder; copy it to the destination filename from the brief. Convert formats only when the brief asks.
- Create original designs; existing characters, logos, and trademarked art stay out.
- End with the report the brief asks for.

## Inspect and deliver

View every output file before using it. Done when each requested file exists at its destination and matches its spec. On a mismatch, send a corrective brief that passes the failed file to `image_edit` with the specific change. Tell the user the file paths, that Grok Imagine made them, and the call count.

## Fallback

When Grok is unavailable (no provider, auth error, Imagine quota), report it and ask before switching routes. When the user asks for OpenRouter or GPT Image, or approves the fallback, follow the `openrouter-imagegen` skill at `~/.skills-manager/skills/openrouter-imagegen/SKILL.md` and run its script from that library folder; that skill stays undeployed.

`paper-poster-imagegen` still owns poster prompts; send its generation step here. If Grok garbles dense poster text, show the user and offer OpenRouter.
