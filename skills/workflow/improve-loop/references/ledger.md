# Ledger and final report

The ledger is the loop's memory: it lets a run resume after a turn end, a compaction, or an interruption, keeps decided proposals from returning, and gives the user an audit trail. It is written as the loop goes, never saved up for the end of a round. A **version** is a commit sha in a repo, or a `<name>.r<n>.<ext>` file beside a document.

Location: `.scratch/improve-loop/<yyyy-mm-dd>-<slug>.md` inside a repo; `<name>.improve-loop.md` beside a document. Briefs as sent, screenshots, and other evidence files go in `.scratch/improve-loop/<slug>/r<n>/`, or a folder beside the document. None of these files is part of a round's change.

## Format

```markdown
# Improve loop: <target> (started <date>)

## Run state
- Round: <n> of <N>. Step: <charter | observe | review | proposal gate | improve | round gate | version | stopped | finished>
- Last version: <version>
- Pending calls: <model id: brief file, clientRequestId, started at; task id and child thread once known> | none
- Received this round: <model ids> | none
- Paused by: <harness: what it refused; resume scheduled for <time> | resume by user message> | nothing
- Next action: <the one thing the next turn does first>

## Charter
<charter v1; later versions below it, each with the user's approval>

## Round <n>
Reviewers: <model ids>. Anchor: <model id>.

### Scores (state scored: <version>)
| Criterion | <reviewer> | <reviewer> | Anchor |

### Proposals and decisions
| Id | Raised by | Severity | Change | Decision | Reason or check |

### Changes
- <id>: <what changed> | carried to round <n+1> (change budget) | reverted: <reason>

### Checks
- <check>: pass | fail | failing at baseline
- Change size: <measured> of <budget>

### Round gate
PASS | FAIL: <reason>, then <repaired | reverted> <what>, then PASS | FAIL again: whole round reverted
Version: <version> | none (no change)

## Parked
- <idea> (<id>, round <n>): <reason>

## Escalated
- <question> (<id>, round <n>)
```

## Final report

Append it to the ledger and show it to the user. Each score column names the state scored, not the round that scored it.

```markdown
## Final report

| Anchor mean | Baseline | After R1 | After R2 | ... | Final |

| Final panel | <criterion> | <criterion> | Mean |
| <reviewer> | | | |

- R1: <one line> (<version>)
- R2: <one line> (<version>)

Stop reason: <budget | plateau | no major proposals | target reached | alarm: what>
Accepted, not implemented: <carried ids> | none
Parked for you: <count, see Parked>
Needs your decision: <escalations>
Main rejection reasons: <top 2-3>
Usage: <as reported | not reported by the harness>
```
