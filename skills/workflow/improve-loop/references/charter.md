# Charter

The charter is the fixed reference every gate decision cites. Fill every field, show it to the user, and change nothing until they approve it. A later change becomes charter v2 and needs its own approval.

## Template

```markdown
## Charter v1: <target>

- Target: <path or document>. Baseline: <commit sha | name.r0.ext>.
- Profile: <code | interactive | writing | idea | general>
- Goals (1-3, each observable): <what "better" means>
- In scope: <what may change>
- Out of scope: <what stays untouched>
- Invariants: <what no round may change: profile defaults plus the user's>
- Rubric (3-6 criteria, scored 0-10):
  | Criterion | What a 10 looks like | Evidence used |
- Panel: <short name = exact model id (role), ...>. Anchor: <model id>. Gatekeeper: <model id or "fresh subagent on <provider>">. Strategy: <hybrid | rotate | panel>, per-round <k>.
- Reviewer schedule: (table, see below)
- Budgets: rounds <N> (<ceiling | full>); at most 5 ACCEPTs per round; change per round at most <profile default or user's>, measured as <how>.
- Required checks: <command>: <result on the baseline>. Failing at baseline: <checks, required only when a goal is to fix them | none>
- Mode: <auto | checkpoint>
```

Measure change the same way every round. For lines, the default is to stage the round (`git add -A`, so new files count) and add insertions and deletions from `git diff --cached --shortstat <last version>`, test files included unless the charter excludes them.

## Reviewer schedule

- `hybrid`: round 1 is every reviewer. From round 2, each round takes the next `per-round` reviewers in list order, starting at the first reviewer and wrapping, with no reviewer twice in one round: a `per-round` of the panel size or more means the full panel.
- `rotate`: the same rotation, starting in round 1.
- `panel`: every reviewer, every round.
- The anchor scores every round. It needs a separate score-only call only in rounds where it is not reviewing.

Reviewers `sol, opus, grok`, `hybrid`, `per-round 2`, 5 rounds:

| Round | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| Reviewers | sol, opus, grok | sol, opus | grok, sol | opus, grok | sol, opus |
| Anchor score | sol | sol | sol | sol | sol |

Same panel, `per-round 1`, anchor `opus`:

| Round | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| Reviewers | sol, opus, grok | sol | opus | grok | sol |
| Anchor score | opus (review) | opus (score-only) | opus (review) | opus (score-only) | opus (score-only) |

## Example: a journal abstract

```markdown
## Charter v1: abstract.md

- Target: abstract.md. Baseline: abstract.r0.md.
- Profile: writing
- Goals: (1) a reader states the objective and main result after one read; (2) it meets the target journal's abstract rules.
- In scope: wording, order, and structure of the abstract.
- Out of scope: title, analyses, the full manuscript.
- Invariants: every number and result; conclusion strength; the author's voice; no citation without a verified source.
- Rubric:
  | Criterion | What a 10 looks like | Evidence used |
  | Clarity | One read gives objective, design, main result | sentence-level read |
  | Journal fit | Headings and word limit match the guideline | guideline + word count |
  | Claim accuracy | Every claim matches results.csv, no overstatement | claim-to-source map |
- Panel: opus = claude-opus-5-5 (journal-editor), sol = gpt-6.1-sol (methodologist). Anchor: claude-opus-5-5. Gatekeeper: fresh subagent on Claude. Strategy: hybrid, per-round 1.
- Budgets: rounds 3 (ceiling); at most 5 ACCEPTs per round; at most 15% of words changed per round, measured by a word diff against the last version.
- Required checks: word count ≤ 250: 238 on the baseline; every number appears in results.csv: pass. Failing at baseline: none.
- Mode: auto
```
