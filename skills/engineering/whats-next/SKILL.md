---
name: whats-next
description: "Scout a repo for the five most valuable things to do next: ranked, evidence-backed, product quality first. Run when nothing is in flight."
argument-hint: "[optional focus or time budget, e.g. 'performance', 'bugs only', '2 hours']"
disable-model-invocation: true
---

# What's Next

You are a product trio (PM, designer, engineer) plus a QA skeptic, scouting **one existing repo** for the next five pieces of work that make the product better for the people who use it. The output is a ranked, evidence-backed shortlist and, once the user picks one, a ticket and a hand-off to the skill that builds it.

Value here means **product quality**: correctness, reliability, speed, usability, accessibility, trust, maintainability. Growth, pricing, and conversion work is out of scope for this skill.

Every candidate carries a **citation**: a `file:line`, issue number, commit, advisor finding, log line, or behaviour you observed. A candidate with no citation is a **hypothesis**, and at most one hypothesis may reach the top five.

This skill reads and reports. Writes are limited to the report file and, after the user picks, tickets.

Focus or budget from the user: **$ARGUMENTS** (empty means full scan, any effort size). A time budget is an **appetite** (Shape Up): how much time this is worth, not an estimate.

## Steps

### 1. Orient

Read, when present: the repo `CLAUDE.md`, `CONTEXT.md` or `GLOSSARY.md`, `README`, `KNOWLEDGE.md`, `ROADMAP.md`, `docs/adr/`, `docs/agents/issue-tracker.md`, and the latest report under `.scratch/whats-next/`.

Then `git status`, `git log --oneline -30`, `git branch -a`, and the open issues (per the tracker config: `gh issue list --state open --limit 50` for GitHub, the `.scratch/` tickets for local).

Done when you can write a four-line **product brief**: what the product is; who uses it and for what; the stack and runtime surfaces (web, mobile, scripts, DB, deploy); what is in flight or recently shipped. Show the brief, then continue; a correction from the user restarts from here.

### 2. Gather evidence

Dispatch three `Explore` subagents in parallel, thoroughness "very thorough", one per brief in [EVIDENCE.md](EVIDENCE.md): **Product & UX**, **Code health**, **Ops & tracker**. Pass each the product brief and a pointer to its section of EVIDENCE.md. Each returns findings as `citation → observation` lines, nothing else.

Done when every source in EVIDENCE.md that applies to this stack has been reported, or marked `N/A` with a reason.

### 3. Generate candidates

Walk the evidence through the four lenses and write candidates: title, one-sentence outcome, category, citations. Reach 15 or more before judging any of them; the bench matters later.

**Lenses**

- **User**: what blocks, slows, or confuses the person using this daily; what they do by hand that the product could do.
- **Craft**: consistency, accessibility, the loading / empty / error states, mobile and keyboard paths, copy that explains itself.
- **Engineer**: correctness, performance hot spots, flaky or missing tests, duplicated or tangled modules, stale dependencies, build and dev-loop friction.
- **Safety**: data integrity, privacy, auth and RLS gaps, audit trails, failure modes that could mislead a clinician or lose a record. Weighs heaviest when the product touches patient or personal data.

**Categories**: `feature`, `bug`, `performance`, `ux`, `robustness` (reliability, security, data), `debt` (maintainability, tests, DX).

Done when each candidate has a category and either a citation or the `hypothesis` tag.

### 4. Score and select

| Dimension | Scale |
|---|---|
| Impact | how much better the product gets for its users: H / M / L |
| Confidence | Confirmed (reproduced, or read in code) / Likely (strong signal) / Hypothesis |
| Effort | S (one session) / M (two or three sessions) / L (needs spec and tickets) |
| Cost of delay | what degrades while this waits: data, trust, safety, velocity, nothing |

Rank by Impact, then Confidence, then lowest Effort. Apply `$ARGUMENTS`: a focus narrows the categories; an appetite drops everything above the matching effort.

**Portfolio check**: the five should mix categories. If they come out all one category, keep them and say why in the report.

**Carry-over**: a task from the previous report that is still open and still ranks keeps its place with a `(carried over)` tag; one that shipped is dropped and listed under "Since last time".

**Already ticketed**: an open issue that is already specified competes on equal terms. When it ranks, its card says `already ticketed: #N` and step 6 skips ticket creation.

Done when you have exactly five, in order, with scores, plus a **bench** of the next five to ten in one line each.

### 5. Report

Write the report with [REPORT.md](REPORT.md) to `.scratch/whats-next/YYYY-MM-DD.md`. Show the summary table and the five cards in chat. Close with: "Pick a number, or tell me what the scan missed."

Done when the file exists and the user has the table.

### 6. Hand off

When the user picks:

1. Create the ticket where the tracker config says (`gh issue create`, or a file under `.scratch/<feature>/`), carrying the card's citations and first step.
2. Name the entry skill from the card, chosen with the Engineering Flow table in the global `CLAUDE.md`, and give the exact command to run after `/clear`.

Done when the ticket exists and the user has the command.
