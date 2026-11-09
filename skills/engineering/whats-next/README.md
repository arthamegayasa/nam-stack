# whats-next

A [Claude Code](https://claude.com/claude-code) skill. When nothing is in flight, it scouts a repo for the five most valuable things to do next: ranked, evidence-backed, product quality first.

Value means correctness, reliability, speed, usability, accessibility, trust, and maintainability. Growth, pricing, and conversion work is out of scope.

## What it does

1. **Orient**: reads the repo's context files, git history, and open issues, then writes a four-line product brief.
2. **Gather evidence**: runs three read-only subagents in parallel (Product & UX, Code health, Ops & tracker) against the checklists in `EVIDENCE.md`.
3. **Generate candidates**: 15 or more, through four lenses (User, Craft, Engineer, Safety). Every candidate carries a citation: `file:line`, issue, commit, advisor finding, or observed behaviour.
4. **Score and select**: Impact, Confidence, Effort, Cost of delay. Picks five with a mix of categories, carries over still-open items from the previous run.
5. **Report**: saves `.scratch/whats-next/YYYY-MM-DD.md` using `REPORT.md` and shows the top five in chat.
6. **Hand off**: when you pick one, creates the ticket and names the skill to start with.

## Install

User scope (available in every project):

```sh
git clone https://github.com/arthamegayasa/whats-next-skill.git ~/.claude/skills/whats-next
```

On Windows the target is `C:\Users\<you>\.claude\skills\whats-next`.

Project scope: clone into `.claude/skills/whats-next` inside the repo instead.

The skill is user-invoked only (`disable-model-invocation: true`), so it never fires on its own and costs no context until you call it.

## Use

```
/whats-next
/whats-next performance
/whats-next bugs only
/whats-next 2 hours
```

A focus narrows the categories. A time budget is an appetite: candidates above that effort are dropped.

## Files

| File | Role |
|---|---|
| `SKILL.md` | The steps the agent follows, with a completion criterion per step |
| `EVIDENCE.md` | Three evidence briefs, one per subagent, branching by stack (Next.js, Expo, research repo, marketing site) and by available tools (`gh`, Supabase advisors, Vercel runtime errors, EAS) |
| `REPORT.md` | The report template: summary table, one card per task, bench, since-last-time, portfolio note |

## Dependencies

- Step 1 reads `docs/agents/issue-tracker.md` when present (written by `/setup-matt-pocock-skills`); otherwise it falls back to `gh issue list` for GitHub remotes or `.scratch/` for local tracking.
- Step 6 picks the entry skill using the Engineering Flow table in the user's global `CLAUDE.md` and hands off to skills from the `mattpocock-skills` plugin (`/implement`, `/grill-with-docs`, `/diagnosing-bugs`, and friends).
- Supabase and Vercel checks in `EVIDENCE.md` use their MCP servers when connected, and are reported as `N/A` otherwise.

## Updating

The installed folder is the git checkout. Edit the files in place, then:

```sh
git commit -am "Describe the change"
git push
```
