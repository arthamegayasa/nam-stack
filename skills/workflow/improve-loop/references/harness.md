# Harness calls

How to start reviewers and the gatekeeper so your turn holds until they reply, and how to check a call after a turn ends. The rules (failure kinds, run state, turn ends) live in `SKILL.md`; this file holds the calls.

## T3 Code

- **Resolve once.** Call `orchestrator_capabilities` before round 1 and write each exact model id into the charter. Call it again only after a launch error, once, before starting that call again.
- **Another provider.** `delegate_task` with `role: "review"`, `mode: "wait"`, `target.model` set to the charter's id, and high effort in `target.options` when the capabilities list it. The default `async` mode returns at once and leaves the loop waiting on a completion wake, so set `wait` every time. For a large target, raise `timeoutMs` above the 10-minute default.
- **Your own provider.** The native subagent tool in its blocking form: Claude `Agent` with `run_in_background: false`; Codex `spawn_agent`, then wait.
- **Together.** Put every call of a round in one message, waits included.
- **Wait returned early.** A timeout does not cancel the child. Record its `taskId` and child thread in the run state, follow the tool's `next` (end the turn), and let the completion wake or the next user message bring you back.
- **Check once.** On a new turn, read a pending child's thread once with `t3_thread_read`. When it shows the final reply, take the result with `task_status`; when it is still working, end the turn again as `SKILL.md` says.
- **`parent_not_active`.** "The calling provider no longer owns an active thread run" is about your own run, not the reviewer: a harness pause. The models are still available.
- **Restart.** A restarted call is a new `delegate_task` with the saved brief and the same model id, never a message into the old child thread.

## Claude Code, Codex, and other harnesses

Start each reviewer as a blocking subagent on its model, all in one message. A model the harness cannot start is unavailable: report it and raise the alarm.
