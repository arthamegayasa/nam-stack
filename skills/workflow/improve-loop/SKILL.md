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
| per-round | 1 | Reviewers per rotation round, taken in list order and wrapping, capped at the panel size. |
| anchor | first reviewer | Scores every round, so the score trend compares like with like. |
| gatekeeper | fresh subagent on your own provider | A named model when the user asks. |
| mode | `auto` | `auto`: once the charter is approved, the loop asks the user nothing until an alarm or the final report. `checkpoint`: the user also approves each round's gate decisions. |
| profile | detected | `code`, `interactive`, `writing`, `idea`, `general`. |

Map short names to the newest matching model the harness lists (`sol` → newest GPT Sol, `opus` → newest Claude Opus) and resolve every one before round 1. The charter records each exact model id, and every round, resume, and restart uses that id, even after a newer model appears. Report a model that cannot run; never substitute another. Run reviewers and the gatekeeper at high reasoning effort where the harness exposes it.

## Calls

Start each reviewer on its own model with a call that holds your turn until it replies; `references/harness.md` has the calls for each harness. Reviewers and the gatekeeper get no history, so the brief carries everything. Start all of a round's calls, the anchor's score-only call included, in one message, and wait for every reply: silence or an error is not a review. A restart repeats **the same call**: the saved brief and the charter's model id. Its reply replaces the faulty one.

### When a call fails

Name the failure first; each kind has one response. Gatekeeper calls follow the same table.

| Failure | Kind | Response |
|---|---|---|
| A wait returns before the reply, or the harness's notice that a call finished (its completion wake) never arrives | late reply | End the turn as **Run state** says. |
| A call still working an hour after it started, or a reviewer that stops to ask a question | stuck call | Cancel it, then handle it as a reviewer fault. |
| The harness refuses to start the call because your own run is gone (T3 `parent_not_active`) | launch refused | Retry once. Refused again: arrange one resume (`references/harness.md`) and end the turn as **Run state** says. The resumed turn continues the same round, starting the calls that never started, with one retry; refused there too, it raises the harness alarm. |
| The call errors, ends without a reply, or its reply lacks what the brief's REPLY section requires | reviewer fault | Restart the same call once. A second fault raises the reviewer-unavailable alarm. |
| The harness no longer lists the model | reviewer unavailable | Alarm. |

## Run state

The loop outlives a single turn: a reply can land after your turn ends, and a compaction can erase what you knew. The ledger (`references/ledger.md`) is the loop's single source of truth: its run state says where the loop stands, and the round's section holds everything decided so far.

- Write the ledger as soon as a reply, a decision, a change, or a verdict lands, and before every turn end. Record a call as pending before you start it, and add its task id when the call returns.
- Read the run state at the start of every turn (a completion wake, a scheduled resume, any user message) and right after any compaction, then take its next action. Finished steps stay finished; check each pending call once per turn.
- End a turn mid-loop only while a call is still pending, after a refused launch, or when the skill puts a question to the user. Before ending it for a pending call or a refused launch, tell the user in one line where the loop stands (what is running, or what the harness refused), what resumes it (the reply, the scheduled resume, or any message from them), and that no new approval is needed.

## 0. Charter

1. Pick the profile and read `references/profiles/<profile>.md` and `references/harness.md`.
2. Draft the charter from `references/charter.md`: baseline, goals, scope, invariants, rubric, panel with exact model ids and roles, the reviewer schedule for every round, budgets and how change is measured, required checks with their baseline results.
3. Record the baseline: a commit on a new branch `improve-loop/<slug>` for a repo; a `<name>.r0.<ext>` copy for a document. When the tree holds uncommitted work, ask the user whether it belongs in the baseline and leave it untouched until they answer.
4. Run the required checks on the baseline. A check that already fails there is marked `failing at baseline`: it is still run and reported every round, and becomes required only when a goal is to fix it.
5. Start the ledger from `references/ledger.md`.
6. Show the charter and wait for the user's approval. It authorizes edits inside its scope only. Changing the charter mid-loop pauses the loop for a new approval.

## Each round

### 1. Observe

Run the profile's checks and gather evidence for every rubric criterion: test output, screenshots, citation status, literature hits. Round 1 covers the whole target; later rounds cover what changed plus open items. Done when every criterion has evidence or is marked `no evidence`.

### 2. Review

Send this round's scheduled reviewers the reviewer brief from `references/briefs.md`, with the charter, evidence pack, target location, and the ledger's decided items. The anchor scores every round; when it is not reviewing this round, send it the score-only brief. Each reviewer returns rubric scores and at most 7 ranked proposals.

Scores taken in round n rate the state round n started from, so record them against that version. Check the alarms as soon as the scores arrive. When every score is 9 or more, or no proposal arrives, record the proposals as not gated and skip to the stop check.

### 3. Proposal gate

Merge duplicate proposals, recording how many reviewers raised each and keeping the highest severity any of them gave; drop nothing. Proposals `carried` from the previous round go first, to be decided again. Send the list to the gatekeeper with the proposal-gate brief, which decides each proposal in order:

1. Breaks an invariant: **REJECT**, or **ESCALATE** when strong evidence shows the invariant itself blocks a goal.
2. Outside scope: **PARK**, kept for the user whatever its evidence.
3. Needs clinical or scientific interpretation, or pivots the goal: **ESCALATE**.
4. Otherwise it must pass **direction** (serves a named charter goal), **evidence** (observed, and stronger when only one reviewer raised it), **value vs risk** (a small change in the right direction passes), and **consistency** (keeps earlier ledger decisions unless it brings new evidence). Any failure: **REJECT**, naming the test. All pass: **ACCEPT**, with an acceptance check.

At most 5 ACCEPTs per round, highest value first; the rest that pass are parked for the round cap. You may appeal a decision once with new evidence; the second answer stands. An ESCALATE about an invariant is an alarm, because only a charter v2 can free an invariant; any other ESCALATE waits in the ledger for the final report while the round goes on without it. In `checkpoint` mode, show the decisions and wait for the user.

### 4. Improve

Implement only ACCEPTed proposals, highest value first, each with the smallest change that meets its acceptance check, using the profile's helper skills. Logic changes in code get a failing test first. Keep the round's changes uncommitted until the round gate passes, and stage only the files the round changed. Measure the change against the round's budget as you go, the way the charter measures it; an ACCEPTed proposal that would push past it waits, marked `carried`.

### 5. Round gate

Run the required checks. When a check fails and the change that broke it cannot be fixed inside its own acceptance check, revert that change and mark it `reverted`. Then send the gatekeeper the round-gate brief: the round's changes, the ACCEPT list, the charter, the measured change size, and the cumulative change since baseline. It confirms that every change traces to an ACCEPTed proposal, invariants hold, the round stayed inside its change budget, and the target still points where the charter does.

On ROUND FAIL, check the alarms first. Otherwise make one repair pass: repair each named change so it meets its acceptance check inside the budget (a proposal dropped to fit the budget is `carried` whole), or revert it, or revert the whole round when the verdict says so; then rerun the checks and the round gate. A second FAIL in the same round reverts the whole round. A round with any FAIL counts as a failed round gate. Reverts happen in the working tree before the commit; history is never rewritten.

### 6. Version

Commit the staged round as `improve-loop R<n>: <summary>`, or save `<name>.r<n>.<ext>`; a round left with no change gets no new version. Close the round's ledger section and point the run state at the next round.

## Stop

After each round, stop when any of these holds (in `full` mode only the first applies):

- the rounds budget is spent;
- from round 2, the anchor's mean score rose by less than 0.5 over the previous round's (a fall counts);
- the round accepted no proposal of severity `major` or higher (carried ones count);
- every score this round was 9 or more.

An **alarm** stops the loop at once and goes to the user:

- a needed change would touch an invariant (an invariant ESCALATE), or a committed one did;
- the round gate failed in two consecutive rounds;
- the anchor's mean score fell below baseline;
- a reviewer or the gatekeeper became unavailable;
- the harness refused a launch again on the resumed turn (the harness alarm).

On an alarm, save the round's uncommitted changes as a patch or copy in the evidence folder, restore the round's files to the last version, and give the user the report so far in the final report's format, without the score-only pass. When the user clears the cause (a charter v2, a working harness, an available model) and says to continue, resume from the run state in the same round.

## Finish

1. Run one score-only pass with the full panel, skipping any reviewer that already scored the final state (possible only when the last round changed nothing).
2. Write the final report from `references/ledger.md`: scores from baseline through every round to final, one line per round with its version, carried proposals left unimplemented, parked ideas, escalations, the main rejection reasons, the stop reason, and usage if the harness reports it. When the final anchor mean is below baseline, say so first.
3. Deliver by profile: code goes through the user's normal delivery path (a PR when Ship was agreed); documents and ideas end as the final version plus a change summary. Sending, submitting, and publishing stay with the user.
