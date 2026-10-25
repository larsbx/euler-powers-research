# Euler powers — literature reviews

This directory stores **dated, evidence-labeled literature reviews** relevant to the project's primitive fifth-power equation, formal verification and Diophantine research roadmap. Reviews are historical snapshots; future findings get their own dated file instead of overwriting earlier conclusions.

## Reviews

- [2026-10-25 — Initial periodic literature review and monitoring protocol](2026-10-25-periodic-literature-review.md): edited repository version of the completed Deep Research document. Includes initial primary-source bibliography, solution/sign conventions, topic- and author-watchlists, search queries, a reproducible weekly review workflow, metrics, templates, research priorities and review caveats.

- [2026-10-25 — Braun v4 primary-source audit](2026-10-25-braun-v4-source-audit.md): source-grounded sign/domain, exact integer verification, author-reported search coverage, implementation differences and follow-up proof obligations. See also the [machine-readable source ledger](../../data/literature/braun_2603_05549_v4.json).

## Review conventions

- Every mathematical finding must identify its exact equation, sign domain and primitivity convention; distinguish the fourth reported **signed** primitive example from the two reported **positive** primitive examples.
- Link to primary articles (versioned arXiv/DOI where available), classify them as preprint, refereed paper, computational report or secondary summary, and preserve publication/update dates.
- Compare with [conjectures](../CONJECTURES.md) and the [research plan](../RESEARCH_PLAN.md); never upgrade E5-1 through E5-5 by inference from computations.
- Separate **PROVED**, **COMPUTATIONALLY VERIFIED**, **HEURISTIC**, **CONJECTURAL** and **REFUTED**, and include negative results or “no material updates” where appropriate.
- The existing weekly **Research Repos Literature Review** task has a mandatory Euler Powers section. This folder records literature research; it does not itself install a bot or schedule GitHub Actions.

Maintain the [project proof/verification boundary](../FORMAL_VERIFICATION.md) alongside every new computational claim.
