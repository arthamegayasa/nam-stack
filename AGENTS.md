# nam-stack

Personal agent skills. Skills Manager installs each one from this repo and pulls changes with `skills-manager-cli skills update <skill>` after they merge to `main`.

- Each skill lives at `skills/<category>/<skill>/SKILL.md`, and the folder name equals the frontmatter `name`. Categories: `media` (images and other generated media), `engineering` (software work). Start a new category only for a skill that fits neither.
- `python scripts/validate.py` passes before every push.
- Moving a skill to another category changes its subpath, so re-point it: `skills-manager-cli skills set-source <skill> --git-url https://github.com/arthamegayasa/nam-stack/tree/main/skills/<category>/<skill>`.
- Every skill has a row in the README table.
