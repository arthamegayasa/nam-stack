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
| per-round | 1 | Reviewers per rotation round, taken in list order and wrapping, never more than the whole panel. |
| anchor | first reviewer | Scores every round, so the score trend compares like with like. |
| gatekeeper | fresh subagent on your own provider | A named model when the user asks. |
| mode | `auto` | `auto`: once the charter is approved, the loop asks the user nothing until an alarm or the final report. `checkpoint`: the user also approves each round's gate decisions. |
| profile | detected | `code`, `interactive`, `writing`, `idea`, `general`. |

Map short names to the newest matching model the harness lists (`sol` → newest GPT Sol, `opus` → newest Claude Opus) and resolve every one before round 1; in T3 use `orchestrator_capabilities`. The charter records each exact model id, and every round, resume, and retry uses that id, even after a newer model appears. Report a model that cannot run; never substitute another. Run reviewers and the gatekeeper at high reasoning effort where the harness exposes it.

## Calls

Start each reviewer on its own model. In T3, a model on another provider goes through `delegate_task` (`role: "review"`, `mode: "wait"`), one on your own provider through your native subagent tool in its blocking form; `references/harness.md` has the exact calls per harness. Reviewers and the gatekeeper get no history, so the brief carries everything. Start all of a round's calls, the anchor's score-only call included, in one message, and wait for every reply: silence or an error is not a review.

### When a call fails

Name the failure first. Each kind has one response, and none allows a substitute model. Gatekeeper calls follow the same table.

| Failure | Kind | Response |
|---|---|---|
| A wait returns before the reply, or a completion wake never comes | harness delay | Not a failure. End the turn as **Run state** says; the next turn checks the call once. |
| The harness refuses to start the call because your own run is gone (T3 `parent_not_active`) | harness pause | Retry once. Refused again: end the turn as **Run state** says, naming the harness pause. The next turn starts the calls that never started. Not an alarm. |
| The call errors, ends without a reply, or replies without a score for every criterion | reviewer fault | Start that reviewer again once, same brief and model id. A second fault raises the reviewer-unavailable alarm. |
| The harness no longer lists the model | reviewer unavailable | Alarm. |

## Run state

The loop outlives a single turn: a reply can land after your turn ends, and a compaction can erase what you knew. The ledger's **run state** (`references/ledger.md`) is the loop's single source of truth.

- Write it at every step boundary and before every turn end: round, step, pending calls with their ids and brief files, replies received, gate history, next action.
- Start every turn (a completion wake, any user message, the first turn after a compaction) by reading it, then take its next action. Finished steps stay finished; check a pending call once, never in a loop.
- End a turn mid-loop only when the harness forces it or the skill puts a question to the user. Before a harness-forced end, write the run state and tell the user in one line what is running, that its reply resumes the loop, and that any message from them resumes it too, with no new approval needed.

## 0. Charter

1. Pick the profile and read `references/profiles/<profile>.md`.
2. Draft the charter from `references/charter.md`: baseline, goals, scope, invariants, rubric, panel with exact model ids and roles, the reviewer schedule for every round, budgets and how change is measured, required checks with their baseline results.
3. Record the baseline: a commit on a new branch `improve-loop/<slug>` for a repo; a `<name>.r0.<ext>` copy for a document. When the tree holds uncommitted work, ask the user whether it belongs in the baseline and leave it untouched until they answer.
4. Run the required checks on the baseline. A check that already fails there is marked `failing at baseline` and becomes required only when a goal is to fix it.
5. Start the ledger from `references/ledger.md`.
6. Show the charter and wait for the user's approval. It authorizes edits inside its scope only. Changing the charter mid-loop pauses the loop for a new approval.

## Each round

### 1. Observe

Run the profile's checks and gather evidence for every rubric criterion: test output, screenshots, citation status, literature hits. Round 1 covers the whole target; later rounds cover what changed plus open items. Done when every criterion has evidence or is marked `no evidence`.

### 2. Review

Send this round's scheduled reviewers the reviewer brief from `references/briefs.md`, with the charter, evidence pack, target location, and the ledger's decided items. The anchor scores every round; when it is not reviewing this round, send it the score-only brief. Each reviewer returns rubric scores and at most 7 ranked proposals.

Scores taken in round n rate the state round n started from, so record them against that commit or version. Check the alarms as soon as they arrive. When every score is 9 or more, or no proposal arrives, skip to the stop check.

### 3. Proposal gate

Merge duplicate proposals, recording how many reviewers raised each and keeping the highest severity any of them gave; drop nothing. Proposals `carried` from the previous round go first, to be decided again. Send the list to the gatekeeper with the proposal-gate brief, which decides each proposal in order:

1. Breaks an invariant: **REJECT**, or **ESCALATE** when strong evidence shows the invariant itself blocks a goal.
2. Outside scope: **PARK**, kept for the user whatever its evidence.
3. Needs clinical or scientific interpretation, or pivots the goal: **ESCALATE**.
4. Otherwise it must pass **direction** (serves a named charter goal), **evidence** (observed, and stronger when only one reviewer raised it), **value vs risk** (a small change in the right direction passes), and **consistency** (keeps earlier ledger decisions unless it brings new evidence). Any failure: **REJECT**, naming the test. All pass: **ACCEPT**, with an acceptance check.

At most 5 ACCEPTs per round, highest value first; the rest that pass are parked for the round cap. You may appeal a decision once with new evidence; the second answer stands. An ESCALATE about an invariant is an alarm, because only a charter v2 can free an invariant; any other ESCALATE waits in the ledger for the final report while the round goes on without it. In `checkpoint` mode, show the decisions and wait for the user.

### 4. Improve

Implement only ACCEPTed proposals, highest value first, each with the smallest change that meets its acceptance check, using the profile's helper skills. Logic changes in code get a failing test first. Keep the round's changes uncommitted until the round gate passes. Measure the change against the round's budget as you go, the way the charter measures it; an ACCEPTed proposal that would push past it waits, marked `carried`.

### 5. Round gate

Run the required checks. When a check fails and the change that broke it cannot be fixed inside its own acceptance check, revert that change and mark it `reverted`. Then send the gatekeeper the round-gate brief: the round's changes, the ACCEPT list, the charter, the measured change size, and the cumulative change since baseline. It confirms that every change traces to an ACCEPTed proposal, invariants hold, the round stayed inside its change budget, and the target still points where the charter does.

On ROUND FAIL, repair the named change once so it meets its acceptance check inside the budget, or revert it (the whole round, when the verdict says so); then rerun the checks and the round gate. A second FAIL in the same round reverts the whole round. A round with any FAIL counts as a failed round gate. Reverts happen in the working tree before the commit; history is never rewritten.

### 6. Version

Commit as `improve-loop R<n>: <summary>`, or save `<name>.r<n>.<ext>`; a round left with no change gets no new version. Update the ledger: proposals, decisions with reasons, scores per reviewer per criterion, changes, check results, parked and escalated items, and the run state.

## Stop

After each round, stop when any of these holds (in `full` mode only the first applies):

- the rounds budget is spent;
- from round 2, the anchor's mean score rose by less than 0.5 over the previous round's;
- the round accepted no proposal of severity `major` or higher;
- every score this round was 9 or more.

An **alarm** stops the loop at once and goes to the user, with the target left at its last version and any uncommitted changes saved as a patch or copy in the evidence folder:

- a needed change would touch an invariant (an invariant ESCALATE), or a committed one did;
- the round gate failed in two consecutive rounds;
- the anchor's mean score fell below baseline;
- a reviewer or the gatekeeper became unavailable.

A harness pause is neither a stop nor an alarm: the next turn continues the same round.

## Finish

1. Run one score-only pass with the full panel, skipping any reviewer that already scored the final state (possible only when the last round changed nothing).
2. Write the final report from `references/ledger.md`: scores from baseline through every round to final, one line per round with its commit or version, carried proposals left unimplemented, parked ideas, escalations, the main rejection reasons, the stop reason, and usage if the harness reports it. When the final anchor mean is below baseline, say so first.
3. Deliver by profile: code goes through the user's normal delivery path (a PR when Ship was agreed); documents and ideas end as the final version plus a change summary. Sending, submitting, and publishing stay with the user.
