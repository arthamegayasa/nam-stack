# Profile: code

For a program's architecture, structure, and code quality.

- **Roles**: architect (module depth, seams, coupling, naming) and bug hunter (correctness, edge cases, error handling).
- **Evidence**: test suite, type check, build, and lint results, with the exact commands named in the charter. For architecture goals, add a module map and the call sites of the code in question.
- **Rubric starters**: correctness, module depth and interface simplicity, testability, readability, and performance (only when a goal names it).
- **Invariants by default**: public behavior and API, persisted data formats, and configuration contracts, unless the charter frees them.
- **Helpers**: the vocabulary of `codebase-design` and `improve-codebase-architecture` for architecture proposals; `tdd` for logic changes.
- **Versioning**: branch `improve-loop/<slug>`, one commit per round.
- **Change budget default**: at most 300 changed lines per round.
