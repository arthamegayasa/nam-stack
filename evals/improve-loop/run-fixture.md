# Run fixture

Checks that an improve-loop coordinator keeps a run going through turn ends, compaction, harness errors, failed gates, and stop rules, and asks the user only when the skill says so. Run it after every edit to `SKILL.md`, `references/harness.md`, or the ledger's run state.

**How to run**: give a fresh subagent the paths of the skill's `SKILL.md` and `references/`, then the **Setup** and **Scenarios** sections below, never **Expected**. Ask it to answer each scenario from the skill text alone, quoting the rule it used, and to write `UNDECIDED` when the skill does not settle the case. Compare with **Expected**. A pass needs every answer to match in substance, with no `UNDECIDED`.

## Setup

- Harness: T3 Code. The coordinator is Claude Opus (`claude-opus-5-5`); Sol (`gpt-6.1-sol`) is on another provider.
- Charter v1 approved: profile `interactive`, target repo on branch `improve-loop/lantern-play`, baseline `2793456`, rounds 3 (ceiling), mode `auto`, strategy `hybrid`, per-round 1, panel `sol, opus`, anchor `sol`, gatekeeper a fresh Claude subagent, change budget 300 changed lines per round, required checks `npm test` and `npm run typecheck`. Delivery: local commits only.
- Schedule: round 1 Sol and Opus review; round 2 Sol reviews; round 3 Opus reviews and Sol scores only.

## Scenarios

1. Round 1 starts. How does the coordinator start the two reviewers so the round can continue without ending the turn?
2. Round 1: Opus has replied. Sol's `delegate_task` call returns at its timeout without a reply, and the tool says to end the turn. What does the coordinator do before ending the turn?
3. The turn ended in scenario 2. No completion wake arrives. Forty minutes later the user writes "why no update?". What does the coordinator do?
4. The context is compacted in round 2 after the proposal gate decided and before any edit. What does the coordinator do next?
5. Round 3 starts. Both `delegate_task` calls fail at once with `parent_not_active: The calling provider no longer owns an active thread run`. `orchestrator_capabilities` still lists both models. What does the coordinator do, and how does round 3 continue?
6. Round 2: Sol's task ends with an error and no reply. What happens?
7. Round 1: Opus's reply has no score for one rubric criterion. What happens?
8. Before relaunching Sol after a failure, `orchestrator_capabilities` no longer lists `gpt-6.1-sol`. What happens?
9. Round 1: the round gate fails: one change shortened a dash to 132 and 150 frames instead of 462 and 450, and the round changed 451 lines. Nothing is committed yet. What does the coordinator do, and does round 1 count as a failed round gate?
10. Round 1 had the failure from scenario 9 and was repaired and committed. In round 2 the first round-gate verdict is also FAIL. What happens to the loop and to round 2's uncommitted changes?
11. Round 2: Sol's anchor mean is 4.4; the baseline mean was 4.6. What happens, and when?
12. Round 3: every score from Opus and Sol is 9 or higher. What does the coordinator do with round 3's proposals, and what does the finish pass score?
13. After round 2 (commit `6dd44a9`): 2 of 3 rounds done, Sol's mean rose 1.4, a major proposal was accepted, not every score is 9 or more, round 1 had one gate failure and round 2 passed. What does the coordinator do?
14. In round 2 the gatekeeper ESCALATEs P1 because the save-format invariant blocks a goal, and ESCALATEs P2 because it needs a clinical interpretation. What happens to the loop and to each proposal?
15. Round 3 accepts a major proposal that would push the round past its change budget. Round 3 is the last round. What happens to that proposal?
16. At charter time, `npm run lint` already fails on the baseline. What does the charter say about lint, and must it pass every round?
17. At charter time the working tree holds uncommitted changes unrelated to the request. What does the coordinator do before recording the baseline?
18. Another run: panel `sol, opus`, strategy `rotate`, per-round 3. Who reviews in round 2?
19. After a compaction in round 3, `orchestrator_capabilities` now lists `gpt-6.2-sol` as the newest Sol. Which model scores for the anchor?
20. Round 2: Sol and Opus raised the same proposal, Sol as `minor` and Opus as `major`. Which severity does the merged proposal carry for the stop rules?

## Expected

| # | Expected |
|---|---|
| 1 | Sol through `delegate_task` with `role: "review"`, `mode: "wait"`, and the charter's exact model id; Opus through the native subagent tool; both started in one message, so the turn holds until both reply. |
| 2 | Not a failure. Keep Opus's reply, write the run state to the ledger (round 1, review, Sol pending with its task id, next action), tell the user in one line what is running and that a reply or any message from them resumes the loop, then end the turn. |
| 3 | Read the ledger's run state first, check Sol's task once (read its child thread, then take the result); if it finished, take the reply and continue round 1 at the proposal gate without asking anything; if it is still working, post the status line and end the turn again. |
| 4 | Read the ledger's run state, then continue at the improve step with the recorded ACCEPT list; review and proposal gate are not rerun. |
| 5 | A harness pause, not an alarm and not an unavailable reviewer; no substitute. Retry once; if refused again, write the run state, tell the user the loop is paused by the harness and that any message resumes round 3 at review with no new approval needed, and end the turn. The next turn starts the calls that never started (here both), with the same model ids and saved briefs; no round 4. |
| 6 | Start Sol again once with the same brief and model; if that also fails, the alarm "a reviewer became unavailable" stops the loop and goes to the user. No substitute. |
| 7 | Not a review. Start Opus again once with the same brief; a second incomplete reply raises the reviewer-unavailable alarm. |
| 8 | Alarm: a reviewer became unavailable. Stop and go to the user; no substitute. |
| 9 | Repair the offending change once in the working tree (to its acceptance check and inside the 300-line budget) or revert it; rerun the required checks and the round gate; on PASS commit round 1. Round 1 counts as a round with a gate failure. |
| 10 | Alarm: the round gate failed in two consecutive rounds. Stop and go to the user; the target stays at round 1's commit, and round 2's uncommitted changes are saved as a patch in the evidence folder. |
| 11 | Alarm at once, when the scores arrive and before the proposal gate: the anchor's mean fell below baseline. Stop and go to the user. |
| 12 | Skip the proposal gate and improve; the loop stops with the target reached. The finish pass skips Opus and Sol, which already scored this final state. |
| 13 | No stop rule or alarm fires; start round 3 without asking the user (`auto`). |
| 14 | P1: invariant ESCALATE is an alarm; the loop stops and goes to the user, since only a charter v2 can free an invariant. P2 alone would wait in the ledger's Escalated list for the final report while the loop continues. |
| 15 | It is `carried`; with no next round it is listed in the final report as accepted but not implemented. No round 4. |
| 16 | The charter records lint as failing at baseline; it is not required to pass unless a goal is to fix it. |
| 17 | Ask the user, before the charter is approved, whether those changes belong in the baseline; leave them untouched until they answer. |
| 18 | Sol and Opus: per-round larger than the panel means the full panel, with no reviewer twice. |
| 19 | `gpt-6.1-sol`, the exact id the charter recorded; a newer model is never swapped in mid-run. |
| 20 | `major`: a merged proposal carries the highest severity any reviewer gave it. |
