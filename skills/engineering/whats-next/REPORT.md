# Report template

Save as `.scratch/whats-next/YYYY-MM-DD.md`. Show the table and the five cards in chat; the file carries everything.

```markdown
# What's next: <product name>, <YYYY-MM-DD>

**Product brief**: <four lines from step 1>
**Focus / appetite**: <$ARGUMENTS, or "full scan">
**Scan coverage**: <sources reported vs marked N/A, one line>

## Top five

| # | Task | Category | Impact | Confidence | Effort | Entry skill |
|---|------|----------|--------|------------|--------|-------------|
| 1 | ... | bug | H | Confirmed | S | /diagnosing-bugs |

## Cards

### 1. <Title>  `<category>`

**What**: one sentence, outcome-phrased (what the user can do or rely on afterwards).
**Why now**: impact and cost of delay, two sentences.
**Evidence**:
- `path/to/file.ts:42` → observation
- #123 → observation
**Confidence**: Confirmed / Likely / Hypothesis, and the one thing that would change it.
**Effort**: S / M / L, and what the size hinges on.
**First step**: the first concrete action (reproduce X, read Y, write failing test Z).
**Entry skill**: `/...`, and why that one.
**Assumptions to validate**: the one or two beliefs this task rests on.

## Bench

- <Task>  `<category>`  Impact M, Effort S  → citation
- ...

## Since last time

- Shipped: <tasks from the previous report now done, with commit or PR>
- Carried over: <still open; kept or dropped, and why>

## Portfolio note

<one or two lines: how the five spread across categories, or why they do not>
```
