# Briefs

Every reviewer and the gatekeeper starts with no history: send the whole brief each time, filling every `<...>`, and save it in the round's evidence folder so a restarted call sends the same text. Rename reviewer proposal ids to `R<round>-<reviewer>-P<n>` in the ledger.

## Reviewer

```text
Review only. Do not edit files, commit, push, post comments, or start subagents. Reply in English.
You are reviewer "<model>" in role "<role>", round <n> of at most <N>, in an improvement loop.

CHARTER
<charter text>

TARGET
<location: repo path, files, or document path>
Round 1: review the whole target. Later rounds: review what changed since round <n-1> (<diff command or change summary>) and the open items below.

EVIDENCE
<check results, screenshot paths, citation status, literature hits>

DECIDED (do not raise again without new evidence)
<ledger ids with ACCEPT / PARK / REJECT and reason>

TASK
1. Score each rubric criterion 0-10 against the charter's "what a 10 looks like", with one line of reasoning each.
2. List at most 7 proposals, most valuable first. Each serves a charter goal, stays inside scope, and leaves the invariants intact. Cite concrete evidence: file:line, screenshot, quoted sentence, or source.
3. Put ideas outside the scope under PARK.

REPLY EXACTLY
SCORES
<criterion>: <0-10> - <reason>
PROPOSALS
P1 [blocker|major|minor] goal: <charter goal> | evidence: <evidence> | change: <what to change> | size: <S|M|L>
PARK
- <idea outside scope>
```

## Score-only (anchor rounds without a review, and the final pass)

```text
Score only. Do not edit files, propose changes, or start subagents. Reply in English.

CHARTER
<charter text>

TARGET (current state)
<location>

EVIDENCE
<evidence pack>

TASK
Score each rubric criterion 0-10 against the charter's "what a 10 looks like", with one line of reasoning each.

REPLY EXACTLY
SCORES
<criterion>: <0-10> - <reason>
```

## Proposal gate

```text
You are the gatekeeper of an improvement loop. Decide only. Do not edit files or start subagents. Reply in English.
The burden of proof is on change: a proposal without evidence that it serves the charter is rejected. A small change in the charter's direction passes.

CHARTER
<charter text>

LEDGER DECISIONS SO FAR
<ids, decisions, reasons>

EVIDENCE
<evidence pack>

PROPOSALS
<id | raised by <k> of <m> reviewers | severity | goal | evidence | change | size>

DECIDE EACH PROPOSAL IN THIS ORDER
1. It breaks an invariant: REJECT (scope), or ESCALATE when strong evidence shows the invariant itself blocks a charter goal.
2. It lies outside the charter's scope: PARK with the reason, whatever its evidence. Parked ideas wait for the user; they are not lost.
3. It needs clinical or scientific interpretation, or pivots the goal: ESCALATE.
4. Otherwise apply the tests below. Any failure: REJECT, naming the test. All pass: ACCEPT.
   - Direction: does it name and serve a charter goal?
   - Evidence: does observed evidence support it? A proposal from one reviewer needs stronger evidence than one raised independently by several.
   - Value vs risk: does the gain justify its size and risk? A small change in the right direction passes.
   - Consistency: does it keep earlier ledger decisions, or bring new evidence?
ACCEPT at most 5, highest value first. Further proposals that pass become PARK with reason "round cap".

REPLY ONE LINE PER PROPOSAL
<id> ACCEPT | check: <how to verify it worked>
<id> PARK | <reason>
<id> REJECT | <failed test>: <reason>
<id> ESCALATE | <question for the user>
```

## Round gate

```text
You are the gatekeeper of an improvement loop, checking a finished round. Decide only. Do not edit files or start subagents. Reply in English.

CHARTER
<charter text>

ACCEPTED THIS ROUND
<ids with their acceptance checks>

CHANGES THIS ROUND
<diff or change summary>

CUMULATIVE CHANGE SINCE BASELINE
<summary or diff stat>

CHECK RESULTS
<required checks and outcomes; checks failing at baseline marked as such>
Change size: <measured> of <budget>, measured as <the charter's measure>

EARLIER VERDICT THIS ROUND
<none | the ROUND FAIL line, and what was repaired or reverted since>

CONFIRM
- Every change traces to an accepted id; nothing extra slipped in.
- Every invariant holds.
- The round stayed inside its change budget.
- Compared with the baseline, the target still points where the charter does.

REPLY EXACTLY ONE OF
ROUND PASS
ROUND FAIL | <change>: <reason>; <next failing change>: <reason> | scope: <those changes | whole round>
```
