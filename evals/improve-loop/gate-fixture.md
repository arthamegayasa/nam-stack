# Gate fixture

Checks that the improve-loop gatekeeper keeps a loop on course. Run it after every edit to the gate rules or the proposal-gate brief.

**How to run**: fill the proposal-gate brief in `skills/workflow/improve-loop/references/briefs.md` with the charter, evidence, and proposals below (ledger: none yet), and send it to a fresh subagent. Compare its decisions with **Expected**. A pass needs every decision to match and every REJECT to name the right failed test.

## Charter

```markdown
## Charter v1: pricing.py

- Target: pricing.py. Baseline: commit a1b2c3d.
- Profile: code
- Goals: (1) the discount logic is easy to read and change; (2) the discount logic is correct for every documented code.
- In scope: the body of pricing.py.
- Out of scope: currency handling, the checkout UI, new discount types.
- Invariants: the public signature `final_price(amount: float, code: str | None) -> float` and its return type.
- Rubric: readability, correctness, testability (0-10 each).
- Required checks: pytest passes.
```

## Evidence

```python
# pricing.py
 1  def final_price(amount, code):
 2      if code == "SAVE10":
 3          return amount - amount * 0.1
 4      if code == "save10":
 5          return amount - amount * 0.1
 6      if code == "HALF":
 7          return amount * 0.5
 8      if code == "VIP":
 9          return amount - amount * 0.1 - 5
10      return amount
```

- `pytest`: 6 passed.
- The documented codes are SAVE10, HALF, and VIP, and codes are case-insensitive. `final_price(100, "half")` returns 100 (expected 50).

## Proposals

| Id | Raised by | Severity | Goal | Evidence | Change | Size |
|---|---|---|---|---|---|---|
| P1 | 2 of 2 | major | correctness | lines 2-7, `final_price(100, "half")` returns 100 | Normalize the code with `.upper()` once, and drop the duplicate lowercase branch | S |
| P2 | 1 of 2 | minor | readability | `0.1` repeated on lines 3, 5, 9 | Name the rate `TEN_PERCENT = 0.1` | S |
| P3 | 1 of 2 | major | readability | none | Add multi-currency support with exchange rates | L |
| P4 | 1 of 2 | major | readability | function name is vague | Rename to `compute_final_price` and return a dict with a price breakdown | M |
| P5 | 1 of 2 | minor | readability | none: "dataclasses feel more modern" | Rewrite the module around a `Discount` dataclass | M |

## Expected

| Id | Decision | Why |
|---|---|---|
| P1 | ACCEPT | serves correctness, cites a failing case, small |
| P2 | ACCEPT | small, in scope, evidence on the cited lines |
| P3 | PARK | currency handling is out of scope |
| P4 | REJECT | scope: breaks the invariant signature and return type |
| P5 | REJECT | evidence: taste with no observed problem |
