# Profile: interactive

For games, web apps, and anything a person plays or clicks.

- **Roles**: player and UX critic (feel, clarity, feedback, difficulty, onboarding) and engineer (bugs, performance, structure).
- **Evidence**: run the app. Capture screenshots of the key states with the harness's preview or browser tools, run automated simulations or tests, and record frame time or load time and console errors. Store screenshots under the ledger's evidence folder and pass their paths: reviewers that read images view them, the others get a written description of each.
- **Rubric starters**: feel and responsiveness, visual readability, bugs and crashes, performance, onboarding.
- **Invariants by default**: the core loop, controls, and save compatibility, unless the charter frees them.
- **Helpers**: `grok-imagegen` for new or revised art; `tdd` for logic changes.
- **Versioning**: branch `improve-loop/<slug>`, one commit per round, with before and after screenshots in the ledger.
- **Change budget default**: at most 300 changed lines or 5 replaced assets per round.
