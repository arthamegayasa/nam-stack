# Profile: writing

For journal articles, manuscripts, abstracts, proposals, reports, and other prose.

- **Roles**: journal editor (structure, clarity, fit to the target journal) and methodologist or statistician (methods reporting, claim strength). Add a language editor when a goal is about the prose itself.
- **Evidence**:
  - a section map with word counts;
  - the target journal's author guidelines, fetched from the journal;
  - citation verification: every reference resolves (DOI or PubMed) and supports the claim it is attached to;
  - a claim-to-source map tying each number and claim to the results or source behind it;
  - the reporting checklist that applies (CONSORT, STROBE, PRISMA, CARE, ...).
- **Rubric starters**: clarity, argument flow, fit to the journal or guideline, accuracy of claims against evidence, reporting completeness.
- **Invariants, always**:
  - data, numbers, and results stay exactly as the source has them;
  - conclusions stay no stronger than the evidence;
  - every new claim or citation has a verified source, and references are never invented;
  - the author's voice survives.
  Questions of clinical or scientific interpretation go to the user as ESCALATE.
- **Helpers**: `academic-research-suite` for citation checks and reviewer simulation; `docx` for Word files with tracked changes.
- **Versioning**: a commit per round when the document lives in a repo; otherwise `<name>.r<n>.<ext>` plus a change summary in the ledger.
- **Change budget default**: at most one section rewritten, or 15% of the words, per round.
