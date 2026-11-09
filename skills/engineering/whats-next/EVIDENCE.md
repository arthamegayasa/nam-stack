# Evidence briefs

Three briefs, one subagent each, run in parallel. Each subagent receives the product brief from step 1 and its section below, works read-only, and returns findings as `citation → observation` lines grouped by source. A source that does not apply to this stack comes back as `N/A: <reason>`, so nothing is skipped silently.

Spend the budget where the product lives: for a Next.js app the routes, server actions, and data layer; for Expo the screens, navigation, and offline paths; for a research repo the pipeline scripts, notebooks, and data contracts; for a marketing site the pages, forms, and Core Web Vitals.

## Brief A: Product & UX

Goal: how the product feels to the person using it, and what it is missing.

- **Entry points**: every route, screen, or CLI command. Which have loading, empty, and error states; which fail silently.
- **Core flows**: trace the two or three flows the product exists for (from the product brief) end to end in code. Note dead ends, manual steps, and places the user re-enters data the product already holds.
- **Feedback**: toasts, validation messages, confirmations. Which say what went wrong, which are generic.
- **Accessibility**: labels on inputs and buttons, focus order, contrast tokens, keyboard paths, touch-target sizes on mobile.
- **Consistency**: components that repeat a pattern with drift (two date pickers, three button styles).
- **Promised vs shipped**: README, ROADMAP, CONTEXT, and in-app copy that mention capability the code does not have.
- **Hard-coded**: strings, constants, and lists in code that a user would expect to configure.

## Brief B: Code health

Goal: where the code is wrong, slow, fragile, or hard to change.

- **Checks**: read `package.json` scripts (or the repo's equivalent) and run the type check, lint, and test commands it defines. Report failures with counts and `file:line`.
- **Tests**: which modules carry tests, which core flows have none, which tests are skipped or flaky (`.skip`, `.only`, retries).
- **Markers**: `TODO`, `FIXME`, `HACK`, `XXX`, `@ts-ignore`, `eslint-disable`, `any` in exported signatures. Each with `file:line` and the comment text.
- **Hot spots**: largest files, longest functions, modules with the most incoming imports. Churn: `git log --format= --name-only | sort | uniq -c | sort -rn | head -20`.
- **Performance**: N+1 query patterns, unbounded lists without pagination, client components that could be server components, missing indexes implied by query filters, images without dimensions, heavy dependencies in client bundles.
- **Error handling**: empty catch blocks, swallowed promise rejections, unchecked `null`, missing error boundaries.
- **Dependencies**: `npm outdated` (or the pnpm / bun equivalent) and `npm audit --audit-level=high`. Majors behind, and advisories.
- **Dev loop**: build time, missing scripts, env vars referenced in code but absent from `.env.example`.

## Brief C: Ops & tracker

Goal: what the running product and the backlog already say.

- **Tracker**: all open issues and tickets with title, labels, age. Flag `ready-for-agent` or equivalent: that is already-specified work.
- **Git**: branches with no commits in 30+ days, stashes, large uncommitted changes, reverted commits, commits titled `fix` / `wip` / `hotfix` (what kept breaking).
- **Supabase** (when the repo has a `supabase/` folder or Supabase env vars): `get_advisors` for security and performance; `list_tables` and check RLS is enabled wherever user data lives; local migrations vs remote drift.
- **Vercel** (when the repo deploys there): `get_runtime_errors` and recent `get_runtime_logs` for production; failed or slow builds.
- **Expo / EAS** (mobile): `eas build:list` recent failures; permissions in `app.json` the app does not use.
- **Observability**: is any error reporting wired in; are there logs nobody reads.
- **Docs drift**: setup steps in README that no longer match the scripts; ADRs whose decision the code has since reversed.

## Output shape

```
## Brief B: Code health
### Checks
- src/lib/eeg/parse.ts:142 → tsc: Object is possibly 'undefined'
- N/A: no lint script in package.json
### Tests
- src/features/report/ (0 test files) → core flow "generate report" untested
```
