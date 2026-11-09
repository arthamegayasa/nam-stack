# Harness calls

The calls behind the rules in `SKILL.md`: how to start reviewers and the gatekeeper so your turn holds until they reply, how to check a call after a turn ends, and how to resume after a refused launch.

## T3 Code

- **Models.** `orchestrator_capabilities` lists them. Call it before round 1, and once before restarting any call.
- **Another provider.** `delegate_task` with `role: "review"`, `mode: "wait"`, `target.model` set to the charter's id, high effort in `target.options` when listed, and a `clientRequestId` naming the run, round, model, and attempt. The default `async` mode returns at once and leaves the round hanging on a completion wake, so set `wait` every time. Keep the default `timeoutMs`; a longer review is a late reply.
- **Your own provider.** The native subagent tool in its blocking form: Claude `Agent` with `run_in_background: false`; Codex `spawn_agent`, then wait. When the tool takes an alias such as `opus`, the charter records the alias and the id it resolves to.
- **Together.** Every call of a round goes in one message, waits included.
- **Wait returned early.** The child keeps running. Record its `taskId` and child thread, follow the tool's `next` (end the turn), and let the completion wake or the next user message bring you back. T3 forbids polling a running child, so a late reply gets no scheduled resume.
- **Checking.** Read a pending child's thread with `t3_thread_read`; when it shows the final reply, take the result with `task_status`. A pending call with no task id may have started before a compaction: start it again with the same `clientRequestId`, as the same attempt rather than a restart. If two children reply, use the first and cancel the other.
- **Stuck call.** Stop it with `task_cancel` before the restart.
- **Restart.** A new `delegate_task` with the next attempt's `clientRequestId`, never a message into the old child thread.
- **Resume after a refused launch.** Nothing is running, so no completion wake will come. Schedule one: `schedule_task` with `schedule: {type: "once", runAt: <two minutes from now>}`, bound to this thread, with a prompt that names the ledger and says to resume the improve loop from its run state. One per round.

## Claude Code, Codex, and other harnesses

Start each reviewer as a blocking subagent on its model, all in one message. Where the harness has no scheduled resume, a refused launch ends the turn with the status line, and the user's next message resumes the loop.
