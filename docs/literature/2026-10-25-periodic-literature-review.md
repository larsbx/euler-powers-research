# Periodic literature review — Euler fifth-power research

**Initial review:** 2026-10-25  
**Repository:** `larsbx/euler-powers-research`  
**Status:** Research briefing and review protocol; **not** a mathematical proof or an exhaustive bibliography.  
**Provenance:** Repository-edited version of the Deep Research report *Periodic literature review* (2026-10-25). It retains the report's scope, bibliography/watchlist, monitoring procedure, metrics, templates and action items while replacing chat-only citation markers with stable references, identifying unverified claims and correcting an illustrative placeholder DOI. Future reviews should be new dated files, not silent edits to this baseline.

## Executive summary

The purpose of periodic literature review is to detect and evaluate new research concerning

\[
a^5+b^5+c^5+d^5=e^5,
\]

especially **positive, primitive, ordered** solutions and the questions E5-1 through E5-5 in [the conjecture ledger](../CONJECTURES.md). We will distinguish signed counterexamples from positive solutions, primitive solutions from common multiples, finite computational evidence from unconditional mathematics, and new preprint versions from new refereed publications.

Monitor six connected themes: (1) newly found primitive integer solutions and search completeness; (2) finite-ring and Chinese-remainder restrictions; (3) rational points and special subvarieties of the diagonal Fermat-type quintic threefold; (4) genuine parametric constructions; (5) height counts, boundary concentration and shape-distribution conjectures; and (6) exact computation and formal proof of search correctness, particularly the project's Mojo, Lean and Quint infrastructure.

At this initial baseline, a 2026 computational preprint by Jeffrey M. Braun is the highest-priority directly relevant source. It reports a fourth primitive **signed** solution, not a third positive one, and gives search methods and coverage claims that must retain their original domain and qualifications [B1]. Earlier fifth-power examples have two positive primitive solutions [L1, W1]. The conjectures about infinitude, Zariski density, logarithmic counts and equidistribution remain **open or speculative**. No new number-theoretic theorem is asserted by this review.

A **weekly Friday research-repository literature review** already exists and includes an explicit Euler Powers track. Treat that as the operational cadence for new-paper screening; use monthly or quarterly synthesis when the volume of substantive new papers justifies it. This document is a durable review specification, not evidence that a separate RSS service, GitHub Actions literature bot or Zotero integration has been installed.

## 1. Scope and evidence conventions

For positive solutions use the repository's definition

\[
0<a\le b\le c\le d<e,\qquad
\gcd(a,b,c,d,e)=1,
\]

and let `N_5(B)` count those with `e≤B`. For signed solutions, explicitly record the placement and signs of each fifth-power term; do **not** put those records into positive-only counts. Do not count scaled copies as new primitive examples.

### Known-solution baseline

| Discovery | Tuple / signed identity | Scope | Status |
|---|---|---|---|
| Lander–Parkin, 1966 | `27^5+84^5+110^5+133^5=144^5` | Positive | Historical counterexample [L1] |
| Scher–Seidl, 1996 | `(-220)^5+5027^5+6237^5+14068^5=14132^5` | Signed, one negative summand | Reported historical example [B1, W1] |
| Frye, 2004 | `55^5+3183^5+28969^5+85282^5=85359^5` | Positive | Reported historical example [W1] |
| Braun, 2026 | `719115^5+1331622^5+(-1340632)^5+1956213^5=1956878^5` | Signed, one negative summand | New computational preprint report [B1] |

**The dates of discovery and publication differ:** the Lander–Parkin example was discovered in 1966; there are both a 1966 *Bulletin of the AMS* note [L1] and a 1967 *Mathematics of Computation* treatment [L2]. Do not refer to the example's discovery date as a 1967 event. For the Braun preprint, cite the explicit arXiv version and revision date, not merely “Braun 2026.”

Braun's paper reports a computationally intensive search and a large-target primitive signed solution. The coverage statement needs precision: the paper separates exhaustive coverage of one stated domain up to **`e≤2.76×10^6`** from partial coverage toward **`4.00×10^6`** and discusses a separate signed-integer search regime [B1]. The phrase “exhaustive through four million” is not justified. Record the paper's exact domain, pruning assumptions, software, hardware and independently rechecked output before importing any of its search-height claims into our project.

**Scope of project verification:** the repository's own bounded positive census through height 144, known-solution BigZ checks, Lean proof declarations, Quint state models and execution-trace conformance checks are *different* kinds of evidence; literature-review prose must not relabel one kind as another.

## 2. Research areas and what qualifies as progress

### 2.1 New primitive solutions and computational searches

Prioritize author-supplied exact tuples; prove their fifth-power equality by arbitrary-precision integer arithmetic and check the five-way GCD. For a reported exhaustive search, require the exact height convention, positivity/sign policy, zero-value policy, parity and ordering constraints, algorithms and congruence filters, complete shard coverage, deduplication, data-provenance digests and explicit limitations. Track CPU/GPU time as reported, not as independently measured.

Relevant tools and ideas include meet-in-the-middle pair sums, sorted-array membership, two-pointer search, residue-class partitioning, fixed-memory execution, complete certificate manifests and replay. Braun's paper discusses many of these [B1]. A faster implementation is not a stronger theorem unless it has verified coverage.

### 2.2 Finite-ring and CRT obstructions

Read new work on fifth-power residues modulo prime powers and products of coprime moduli. The existing repository has Lean theorems deriving one-or-three divisibility-count restrictions modulo 5 and 11, via arithmetic modulo 25 and 11. Extend those lemmas to new moduli only with a universal proof or a rigorously scoped finite check. A table of observed congruences is **not** itself a proof of sufficiency.

Track whether a new modular filter is genuinely stronger than current filters, what fraction of candidate classes it excludes, and whether CRT combinations introduce correlations. Record deterministic test vectors that Mojo and an independent oracle can both reproduce.

### 2.3 Geometry of the diagonal quintic threefold

Track rational points, lines, curves and special loci on the projective hypersurface `X_5: a^5+b^5+c^5+d^5=e^5`. The *positive rational region* is essential: cancellation families with negative terms do not establish E5-1 or E5-2. Separate existence of a rational curve, positive rational points on that curve, infinitely many primitive points and Zariski density of all positive points.

Related work on other generalized Fermat signatures may provide methods but is not automatically a theorem about `X_5`. For example, Chen–Koutsianas analyze equations of signature `(p,p,5)` using Frey hyperelliptic curves and conditional modular-method steps [C1]. Treat this as **adjacent methodology**, not a solution of our five-term equation.

### 2.4 Parametric constructions

Look for families yielding infinitely many *distinct primitive positive* tuples in the exact 5.1.4 equation. Distinguish such a family from scaling a known tuple or from identities with **five or more summands**, or with two or more terms on both sides. Wolfram MathWorld catalogs other fifth-power partition signatures and warns against treating them as equivalent [W1]. Report positivity and primitive specialization arguments explicitly.

### 2.5 Counting, asymptotics and near-cancellation

Search for unconditional estimates on `N_5(B)`, shape distributions of `(a/e,b/e,c/e,d/e)`, and bounds involving `δ=e−d`. In the repository, `N_5(B) ~ C log B` (E5-3), boundary accumulation (E5-4) and shape equidistribution (E5-5) remain speculative. A small list of examples cannot validate a distributional law. Any proposed asymptotic must state its height model, measure normalization, exceptional algebraic loci and status of error terms.

### 2.6 Formal verification and reproducible computational evidence

Track new Lean, Coq, Isabelle and verified-program results relevant to Diophantine search. Within this repository, separate kernel-checked mathematics (Lean), bounded state exploration (Quint/Apalache), executable arithmetic (Mojo), exact comparison with an independent Python oracle and observed native execution traces. None independently establishes a universal compiler-refinement theorem for the whole Mojo enumerator. Give priority to proof-carrying bounded search, independent checking of exact records, and transparent limits on completeness claims.

## 3. Prioritized literature sources

| Priority | Source | Coverage | Collection method |
|---|---|---|---|
| High | [arXiv](https://arxiv.org/) in math.NT, math.AG and relevant cs.DS | New/revised preprints | Search submission and update dates; inspect version histories |
| High | [Crossref](https://www.crossref.org/) and journal landing pages | Published article identity, DOI and corrections | DOI and bibliography resolution |
| High | *Mathematics of Computation*, *Journal of Number Theory*, *Acta Arithmetica*, *Experimental Mathematics* | Computational and theoretical number theory | Journal search and citation following |
| High | [MathSciNet](https://mathscinet.ams.org/) / [zbMATH Open](https://zbmath.org/) | Reference coverage and professional reviews | Manual verification; access may vary |
| High | GitHub repositories and official supplemental materials linked by authors | Search code, certificates and proof scripts | Inspect revisions and reproducibility artifacts |
| Medium | [Google Scholar](https://scholar.google.com/), [Semantic Scholar](https://www.semanticscholar.org/) | Discovery and citation graph | Candidate generation; verify against primary sources |
| Medium | [Wolfram MathWorld](https://mathworld.wolfram.com/DiophantineEquation5thPowers.html), [OEIS](https://oeis.org/) | Curated numerical context | Secondary cross-check only |
| Optional | Conference proceedings, seminar archives, author pages | Unpublished leads | Require source and date before elevation |

Do not present a Google Scholar alert or a Zotero collection as connected/automated unless that integration is actually configured. ADS and social/math discussion sites may be *supplemental discovery sources*, not authoritative sources for a new theorem.

## 4. Saved queries and author/citation watchlist

Use several independent strategies. Queries below are examples and must be adapted to each service's actual syntax; broad matching alone does not establish relevance.

| Query or expression | Purpose |
|---|---|
| `"Euler's sum of powers" fifth` | General counterexample and historiography updates |
| `"a^5" "b^5" "c^5" "d^5" "e^5"` | Equation-specific preprints |
| `"sum of four fifth powers" primitive` | Searches and parametric claims |
| `"primitive solution" "fifth powers" Euler` | Mixed positive/signed solution reports |
| `"Fermat quintic threefold" rational points` | Relevant arithmetic geometry |
| `"equal sums of like powers" fifth` | Adjacent partitions and methods |
| `fifth power modular sieve 11 25 CRT` | Finite-ring optimization |
| `near cancellation fifth powers Diophantine` | E5-4 structural evidence |
| `Lean Coq Isabelle verified Diophantine search` | Formalization and certificates |
| `arXiv 2603.05549 Braun citations revisions` | Version/follow-up watch |

Search named contributions and citations for **L. J. Lander, T. R. Parkin, J. L. Selfridge, Noam D. Elkies, B. Scher, E. Seidl, J. Frye, J.-C. Meyrignac, R. L. Ekl and Jeffrey M. Braun**. Include Chen and Koutsianas only as adjacent generalized-Fermat-method references. Confirm initial papers and stable IDs rather than assuming all names describe the same exact signature.

## 5. Reproducible periodic review workflow

The existing **Friday weekly cross-repository research review** contains a mandatory Euler Powers subsection. The following is its Euler-specific operational checklist:

1. **Snapshot repository state.** Read current `main`, [conjectures](../CONJECTURES.md), [research plan](../RESEARCH_PLAN.md), [formal-verification boundary](../FORMAL_VERIFICATION.md), open issues/PRs and the previous literature review. Record the Git commit SHA.
2. **Collect a dated delta.** Search arXiv for papers newly *submitted or revised* since the previous completed cycle; follow citations via Crossref and primary-journal records. On the first review use a larger backfill and identify its window.
3. **Triage.** Reject unrelated signatures, repeat records and unsourced claims. Label candidate findings `new-solution`, `modular-filter`, `Fermat-geometry`, `parametric-family`, `counting`, `formal-verification` or `negative-result`.
4. **Verify provenance.** Record full bibliographic data, publication and revision timestamps, arXiv version, DOI if verified, evidence domain, constraints and actual source for each finding. If a numerical identity is central, verify it exactly and specify the code or independent source used.
5. **Reconcile claims.** Compare against the existing four-example record and E5-1 through E5-5. Call out a counterexample to any claim or an unsupported transfer from a related equation. Keep **PROVED**, **COMPUTATIONALLY VERIFIED**, **HEURISTIC**, **CONJECTURAL**, **REFUTED** labels.
6. **Deliver the review.** Write a short substantive findings section, annotated bibliography, changed-vs-unchanged comparison, proposed repository proof obligations and experiment requests. Limit routine briefs to 5–10 genuinely high-value findings; explicitly say “no material new literature” if warranted.
7. **Route follow-up work.** Recommend issues/PRs with priorities and acceptance tests, but **do not autonomously claim issues, PRs or notifications were created** unless tools report success. Repository mutations require separate authorization.

For deep quarterly synthesis, revisit the citation network, proposed heuristics and search coverage assumptions; produce a separate quarterly file if requested. A weekly schedule is already active outside this repository. A GitHub Actions cron, arXiv bot, Scholar alerts and Zotero integration are **proposals**, not components installed by this document.

## 6. Metrics and trend tracking

Record each item with a source and evidence label; do not interpolate coverage from unrelated searches.

| Metric | Required metadata |
|---|---|
| Known primitive solutions | Discovery/publication date, exact tuple, signed/positive classification, GCD verification |
| Search bounds | Exact target-height interval, exhaustive vs partial, signed/positive/zero domain, algorithm and release revision |
| Computational resources | Author-reported or independently measured CPU/GPU hours, hardware, wall-clock, memory, source |
| New mathematical results | Exact theorem/hypotheses, peer-review status, proof checker if formalized |
| Citation count | Database and retrieval date; counts vary across services |
| Reproducibility | Code commit, parameters, environment lock, output digest, certificate/manifest |

A discovery timeline may show the Lander–Parkin 1966, Scher–Seidl 1996, Frye 2004 and Braun 2026 examples with *scope labels*. Do not turn that historical chronology into evidence of a trend in `N_5(B)`. A comparison graph of actual citations must contain verified citation edges; do not treat “later example” as “cites earlier example” without inspecting the bibliography.

## 7. Annotated bibliography — initial baseline

These are research starting points, not an assertion that the bibliography is complete.

**[L1] Lander, L. J., and Parkin, T. R. (1966).** “Counterexample to Euler's conjecture on sums of like powers.” *Bulletin of the American Mathematical Society* **72**(6), 1079. DOI: [10.1090/S0002-9904-1966-11654-3](https://doi.org/10.1090/S0002-9904-1966-11654-3). Primary historical announcement of the positive fifth-power counterexample; distinguished from subsequent 1967 treatment.

**[L2] Lander, L. J., and Parkin, T. R. (1967).** “A Counterexample to Euler's Sum of Powers Conjecture.” *Mathematics of Computation* **21**, 101–103. [Secondary bibliographic listing](https://mathworld.wolfram.com/DiophantineEquation5thPowers.html). Historical follow-up on methods; confirm the primary journal record before asserting a DOI.

**[B1] Braun, Jeffrey M. (2026).** “The fourth known primitive solution to `a^5+b^5+c^5+d^5=e^5`.” *arXiv*, **2603.05549v4**, dated 21 August 2026. [Official arXiv preprint](https://arxiv.org/abs/2603.05549) / [versioned HTML](https://arxiv.org/html/2603.05549v4). Reports a fourth **signed** primitive solution with `e=1956878`; discusses meet-in-the-middle search, residue-class partitioning, implementation and search coverage. **Preprint/computational report, not an independently established proof of all search-height claims.** Verify each claimed exhaustive domain separately.

**[W1] Weisstein, Eric W.** “Diophantine Equation—5th Powers.” *Wolfram MathWorld*. [Reference](https://mathworld.wolfram.com/DiophantineEquation5thPowers.html), accessed 2026-10-25. Secondary catalogue of signatures 5.1.4, 5.2.3, 5.1.5 etc.; important for preventing category errors between the *exact* four-positive-summand problem and adjacent signed or mixed-sided identities.

**[C1] Chen, Imin, and Koutsianas, Angelos.** “A modular approach to Fermat equations of signature `(p,p,5)` using Frey hyperelliptic curves.” *arXiv:2210.02316*, originally posted 5 October 2022. [Official preprint](https://arxiv.org/abs/2210.02316). Relevant only as an **adjacent theoretical technique** for different generalized-Fermat equations. It does not prove any E5-1 through E5-5 statement.

**[E1] Elkies, Noam D. (1988).** “On `A^4+B^4+C^4=D^4`.” *Mathematics of Computation* **51**, 825–835. Establishes a useful **fourth-power** comparison; do not transplant its infinite-family conclusions to fifth powers.

**[G1] Guy, Richard K. (1994).** *Unsolved Problems in Number Theory*, 2nd ed., section D1 (“Sums of Like Powers. Euler's Conjecture”), pp. 139–144. Foundational question catalog; evaluate status against current primary papers.

**Bibliographic verification rule:** The original Deep Research draft included a **hypothetical DOI** for Lander–Parkin and some undifferentiated 1966/1967 dates. This repository copy replaces the placeholder with a verifiable 1966 AMS DOI and distinguishes the two publications. No invented DOI is retained. Do not infer a theorem or a search bound solely from a secondary summary.

## 8. Actionable research priorities

| Priority | Proposed follow-up | Evidence requirement | Related stage |
|---|---|---|---|
| P0 | Audit Braun v4 coverage and reported fourth signed solution | Primary-paper statements, exact tuple/GCD, signed domain, exhaustive/partial interval qualifications | Baseline/P0 |
| P0 | Keep “two positive vs four signed primitive examples” visibly separated | Dataset cross-check, tuple-wise exact arithmetic, versioned references | Baseline/P0 |
| P1 | Evaluate stronger fifth-power residue sieves or CRT partitions | Proof or finite certified residue tables, independent oracle, candidate-retention proof | P1 |
| P1 | Compare Mojo's memory-bounded pair-sum approach with Braun's partitioning strategy | Equal-domain benchmarks, pinned revisions, memory/time evidence, no omitted representations | P1/P4 |
| P1 | Improve machine-checkable search-completeness artifacts beyond witness-only certificates | Bounded coverage proof, manifests, replay and independent reconstruction | P0/P4 |
| P2 | Inventory positive rational curves on `X_5` | Correct algebraic equations, rationality and positivity proofs, primitivity handling | E5-1/E5-2 |
| P3 | Study the near-cancellation gap `δ=e−d` | New unconditional lemmas or explicit counterexample; distinguish signed cases | E5-4 |
| P4 | Test logarithmic counts and shape heuristics without promoting them | Precisely stated hypotheses; evidence sensitivity to special loci | E5-3/E5-5 |

**No automated modifications** to experiments, conjectures, the canonical solution table or issues are part of this literature review. These are proposed next tasks.

## 9. Reusable templates

### Bibliographic entry

```text
Identifier: DOI / arXiv ID + version:
Title and authors:
First publication; latest revision:
Peer-reviewed / preprint / code / secondary:
Problem signature and sign/primitive constraints:
Exact result and proof/computation status:
Search completeness domain (if relevant):
Methods / prerequisites / limitations:
Connection to E5-1..E5-5 or repository stage:
Reproduction commands or certificate links:
Novelty compared with previous review:
Proposed action; priority:
```

### Periodic briefing

```text
Report date and prior-report cutoff:
Repository main SHA:
Search databases and query/date windows:
New/revised items screened; high-value inclusions:
Top findings (full citations and exact results):
Changed vs unchanged statements:
Contradictions / retractions / negative results:
Proof or experiment tasks (priority + acceptance criteria):
Open verification limitations:
Conclusion, including "no material new findings" when appropriate:
```

### Backlog label vocabulary

`literature-review`, `new-solution`, `search-result`, `modular-constraint`, `algebraic-geometry`, `formal-verification`, `negative-result`, `needs-primary-source`.

These labels are *suggestions*. Confirm that a label exists before using it in an issue.

## 10. Schedule and ownership

**Active delivery mechanism:** The user's existing **Research Repos Literature Review** scheduled task runs weekly on Fridays and includes a required Euler Powers track. This task is outside GitHub and should not be confused with a repository GitHub Actions workflow. The initial Deep Research report described the cadence as “TBD”; the active schedule resolves that operational question.

**Cycle:** weekly candidate discovery and triage → cite and classify → compare with the previous review → actionable research briefing. Carry unfinished source verification into the next cycle rather than filling gaps with guesses. A deeper synthesis may be prepared monthly or quarterly when meaningful material accumulates.

**Ownership:** the reviewer curates evidence; mathematical promotions require proofs; computational claims require reproducibility; merges require ordinary PR validation. A literature report itself is **not** authority to modify the solution ledger or claim an open conjecture is settled.

---

**Review boundary:** This document is a research-monitoring framework and a curated starting bibliography. It does not certify that every literature source or historical search is covered, that third-party computational results were independently reproduced, or that any open conjecture has been solved.
