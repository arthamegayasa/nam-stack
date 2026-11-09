# Ledger and final report

The ledger is the loop's memory: it lets a run resume after an interruption, keeps decided proposals from returning, and gives the user an audit trail. Update it at the end of every round.

Location: `.scratch/improve-loop/<yyyy-mm-dd>-<slug>.md` inside a repo; `<name>.improve-loop.md` beside a document. Screenshots and other evidence files go in `.scratch/improve-loop/<slug>/r<n>/`, or a folder beside the document.

## Format

```markdown
# Improve loop: <target> (started <date>)

## Charter
<charter v1; later versions below it, each with the user's approval>

## Round <n>
Reviewers: <models>. Anchor: <model>.

### Scores
| Criterion | <reviewer> | <reviewer> | Anchor |

### Proposals and decisions
| Id | Raised by | Severity | Change | Decision | Reason or check |

### Changes
- <id>: <what changed> (<commit sha | version file>)
- <id>: carried to round <n+1> (change budget) | reverted by the round gate: <reason>

### Checks
- <check>: pass | fail

### Round gate
PASS | FAIL: <reason>, reverted <what>

## Parked
- <idea> (<id>, round <n>): <reason>

## Escalated
- <question> (<id>, round <n>)
```

## Final report

Append it to the ledger and show it to the user:

```markdown
## Final report

| Anchor mean | Baseline | R1 | R2 | ... | Final |

| Final panel | <criterion> | <criterion> | Mean |
| <reviewer> | | | |

- R1: <one line> (<sha | version>)
- R2: <one line> (<sha | version>)

Stop reason: <budget | plateau | no major proposals | target reached | alarm: what>
Parked for you: <count, see Parked>
Needs your decision: <escalations>
Main rejection reasons: <top 2-3>
Usage: <as reported | not reported by the harness>
```
