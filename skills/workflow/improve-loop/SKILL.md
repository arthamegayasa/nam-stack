---
name: improve-loop
description: Improve an existing artifact (code, game or app, manuscript, research idea, any document) in gated rounds of panel review and fixes. Use when the user says "improve loop".
---

# Improve loop

Rounds of observe → review → gate → improve → round gate → version, held to a **charter** the user approves once. Reviewers propose, an independent **gatekeeper** decides, and you, the coordinator, are the only one who edits. A change earns its place: without evidence that it serves the charter, it stays out.

## Parameters

Read them from the request; natural language counts ("10 rounds", "2 reviewers per round").

| Parameter | Default | Meaning |
|---|---|---|
| target | required | Path, repo, document, or idea text. |
| goal | required | What "better" means. Ask once if missing. |
| rounds | 3 | A ceiling: stop rules can end the loop earlier. `full` runs every round unless an alarm fires. |
| reviewers | `sol, opus` | Any models the harness offers, each with an optional role: `sol:methodologist`. |
| strategy | `hybrid` | `hybrid`: round 1 is the full panel, then rotation. `rotate`: rotation from round 1. `panel`: every reviewer every round. |
| per-round | 1 | Reviewers per rotation round, taken in list order and wrapping. |
| anchor | first reviewer | Scores every round, so the score trend compares like with like. |
| gatekeeper | fresh subagent on your own provider | A named model when the user asks. |
| mode | `auto` | `checkpoint`: the user approves each round's gate decisions. |
| profile | detected | `code`, `interactive`, `writing`, `idea`, `general`. |

Map short names to the newest matching model the harness lists (`sol` → newest GPT Sol, `opus` → newest Claude Opus) and resolve every one before round 1; in T3 use `orchestrator_capabilities`. Report a model that cannot run; never substitute another. Run reviewers and the gatekeeper at high reasoning effort where the harness exposes it.

Start each reviewer on its own model. In T3, a model on another provider goes through `delegate_task` (`role: "review"`), one on your own provider through your native subagent tool; outside T3, use the harness's subagents. Reviewers and the gatekeeper get no history, so the brief carries everything. Start a round's reviewers together and wait for every reply: silence or an error is not a review.

## 0. Charter

1. Pick the profile and read `references/profiles/<profile>.md`.
2. Draft the charter from `references/charter.md`: baseline, goals, scope, invariants, rubric, panel with roles, the reviewer schedule for every round, budgets, required checks.
3. Record the baseline: a commit on a new branch `improve-loop/<slug>` for a repo; a `<name>.r0.<ext>` copy for a document.
4. Start the ledger from `references/ledger.md`.
5. Show the charter and wait for the user's approval. It authorizes edits inside its scope only. Changing the charter mid-loop pauses the loop for a new approval.

## Each round

### 1. Observe

Run the profile's checks and gather evidence for every rubric criterion: test output, screenshots, citation status, literature hits. Round 1 covers the whole target; later rounds cover what changed plus open items. Done when every criterion has evidence or is marked `no evidence`.

### 2. Review

Send this round's scheduled reviewers the reviewer brief from `references/briefs.md`, with the charter, evidence pack, target location, and the ledger's decided items. The anchor scores every round; when it is not reviewing this round, send it the score-only brief. Each reviewer returns rubric scores and at most 7 ranked proposals. When no proposal arrives, skip to the stop check.

### 3. Proposal gate

Merge duplicate proposals and record how many reviewers raised each; drop nothing. Send the list to the gatekeeper with the proposal-gate brief, which decides each proposal in order:

1. Breaks an invariant: **REJECT**, or **ESCALATE** when strong evidence shows the invariant itself blocks a goal.
2. Outside scope: **PARK**, kept for the user whatever its evidence.
3. Needs clinical or scientific interpretation, or pivots the goal: **ESCALATE**.
4. Otherwise it must pass **direction** (serves a named charter goal), **evidence** (observed, and stronger when only one reviewer raised it), **value vs risk** (a small change in the right direction passes), and **consistency** (keeps earlier ledger decisions unless it brings new evidence). Any failure: **REJECT**, naming the test. All pass: **ACCEPT**, with an acceptance check.

At most 5 ACCEPTs per round, highest value first; the rest that pass are parked for the round cap. You may appeal a decision once with new evidence; the second answer stands. In `checkpoint` mode, show the decisions and wait for the user.

### 4. Improve

Implement only ACCEPTed proposals, highest value first, each with the smallest change that meets its acceptance check, using the profile's helper skills. Logic changes in code get a failing test first. Measure the change against the round's budget as you go; an ACCEPTed proposal that would push past it waits, marked `carried`, and opens the next round's work.

### 5. Round gate

Run the required checks until they all pass. Then send the gatekeeper the round-gate brief: the round's changes, the ACCEPT list, the charter, and the cumulative change since baseline. It confirms that every change traces to an ACCEPTed proposal, invariants hold, the round stayed inside its change budget, and the target still points where the charter does. A failure reverts the offending change or the whole round, through a new commit or by restoring the previous version; history is never rewritten.

### 6. Version

Commit as `improve-loop R<n>: <summary>`, or save `<name>.r<n>.<ext>`. Update the ledger: proposals, decisions with reasons, scores per reviewer per criterion, changes, check results, parked and escalated items.

## Stop

After each round, stop when any of these holds (in `full` mode only the first applies):

- the rounds budget is spent;
- from round 2, the anchor's mean score rose by less than 0.5;
- the round accepted no proposal of severity `major` or higher;
- every reviewer scored every criterion 9 or more.

An **alarm** stops the loop at once and goes to the user:

- a needed change would touch an invariant, or one did;
- the round gate failed in two consecutive rounds;
- the anchor's mean score fell below baseline;
- a reviewer or the gatekeeper became unavailable.

## Finish

1. Run one score-only pass with the full panel, skipping any reviewer that already scored the final state in the last round.
2. Write the final report from `references/ledger.md`: scores from baseline through every round to final, one line per round with its commit or version, parked ideas, escalations, the main rejection reasons, the stop reason, and usage if the harness reports it.
3. Deliver by profile: code goes through the user's normal delivery path (a PR when Ship was agreed); documents and ideas end as the final version plus a change summary. Sending, submitting, and publishing stay with the user.
