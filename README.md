# nam-stack

The agent skills I wrote for my own work, kept in one repo so they install and
update from a single place. They work in Claude Code, Codex, and Grok Build.

## Skills

| Skill | Category | Say | What it does |
|---|---|---|---|
| `grok-imagegen` | media | "bikin gambar", "generate image" | Generates and edits images with xAI Grok Imagine. Grok uses its own image tools; Claude Code and Codex hand the work to a Grok agent. |
| `openrouter-imagegen` | media | "pakai GPT Image" | Generates images with GPT Image through the OpenRouter Images API. The fallback when Grok Imagine is unavailable. |
| `whats-next` | engineering | `/whats-next` | Scouts a repo for the five most valuable things to do next, ranked and evidence-backed. |
| `improve-loop` | workflow | "improve loop" | Improves code, a game, a manuscript, a research idea, or any document in rounds: a panel of models reviews, an independent gatekeeper keeps only changes that serve the charter, and the main agent applies them. Rounds, reviewers, and rotation are configurable. |

My book-writing suite lives in its own repo:
[nam-book-studio](https://github.com/arthamegayasa/nam-book-studio).

## Layout

Each skill lives at `skills/<category>/<skill>/SKILL.md`, and its folder name
matches the `name` in its frontmatter.

## Install

With [Skills Manager](https://github.com/xingkongliang/skills-manager):

```bash
skills-manager-cli skills install https://github.com/arthamegayasa/nam-stack/tree/main/skills/media/grok-imagegen
skills-manager-cli skills deploy grok-imagegen --agent claude_code --agent codex
```

Or copy them by hand:

```bash
git clone https://github.com/arthamegayasa/nam-stack
cp -R nam-stack/skills/*/* ~/.claude/skills/   # Claude Code
cp -R nam-stack/skills/*/* ~/.codex/skills/    # Codex
```

## Update

Edit the skill here and merge it to `main`, then pull it into every agent:

```bash
skills-manager-cli skills update <skill>   # or: --all
```

## Requirements

- `grok-imagegen`: a signed-in [Grok Build](https://x.ai/cli) CLI. Claude Code
  and Codex reach Grok through [T3 Code](https://github.com/pingdotgg/t3code)'s
  `delegate_task`, or through `grok -p` without it.
- `openrouter-imagegen`: Python 3.10+ and an `OPENROUTER_API_KEY`.

## License

[MIT](LICENSE)
