# P0 primary-source audit: Braun's fourth primitive fifth-power solution

**Audit date:** 2026-10-25  
**Scope:** Jeffrey M. Braun, *The fourth known primitive solution to* `a^5+b^5+c^5+d^5=e^5`, [arXiv:2603.05549v4](https://arxiv.org/html/2603.05549v4), originally submitted 2026-03-05; v4 revised 2026-08-21.  
**Repository record:** [data/literature/braun_2603_05549_v4.json](../../data/literature/braun_2603_05549_v4.json)  
**Machine-checking entrypoint:** `python3 tests/verify_braun_primary_evidence.py`

This document records **what the paper reports** and which smaller facts have actually been checked inside this repository. It does not adopt Braun's computational exhaustiveness claim as our own.

## 1. Reported fourth primitive solution: exact check

Braun's §3 reports the **signed** integer solution

```
  719115^5 + 1331622^5 + (-1340632)^5 + 1956213^5
    = 1956878^5
```

The exact values are recorded in `data/known_solutions.csv` and pinned in the source evidence JSON. The Python audit independently evaluates both sides with unbounded integers, checks the five-way GCD equals 1, checks the negative summand remains negative, and verifies congruence-count restrictions at 5 and 11. The existing Mojo BigZ known-solution verifier independently checks the CSV. This suffices to certify **this tuple's arithmetic**, not its uniqueness or discovery provenance.

Of the four currently recorded primitive solutions, exactly **two** have all four left-hand summands positive (1966 Lander–Parkin, 2004 Frye). The 1996 Scher–Seidl and 2026 Braun examples contain negative summands. A fourth known primitive **signed** solution is not a third primitive **positive** solution, and cannot increase `N_5(B)` in the positive-only count used by E5-1 through E5-5.

Source: [Braun §2, table 1, and §3, equation (3)](https://arxiv.org/html/2603.05549v4).

## 2. Coverage: author report only, domains carefully separated

Braun §6 table 3 states:

| Variable domain | Author-reported exhaustive `e` range | Author-reported partial `e` range |
|---|---:|---:|
| Nonnegative integers, `ℤ≥0` | `e ≤ 2,760,000` | `2,760,000 < e ≤ 4,000,000` |
| Signed integers, `ℤ` | `e ≤ 1,450,000` | `1,450,000 < e ≤ 2,000,000` |

These are **reported** coverage limits, not height ranges independently enumerated by this repository. Partial means only a subset of search partitions was evaluated. Do **not** describe the nonnegative search as exhaustive to four million, or the signed search as exhaustive to two million.

The paper reports a completed-target-count check for the exhaustive ranges and a baseline regression comparison (§6). Neither suffices to establish that our unrelated Mojo kernel fully implements Braun's algorithm. The reported nonnegative domain admits zero terms; the project's `N_5(B)` requires all summands **strictly positive**, primitive, and ordered. The sign/zero/height distinction must accompany all transferred numerical results.

Reference: [Braun §6, table 3 and coverage discussion](https://arxiv.org/html/2603.05549v4).

## 3. Implementation and resource evidence

The author's §4–§5 algorithm forms sorted sums of pairs of fifth powers, then applies a **two-pointer search** for pair-sum complements at each target `e`. For fixed-memory scaling it partitions by unordered *pair-sum residue classes* modulo `M`, where the chosen prime factors satisfy `gcd(5,p−1)=1`, ensuring the fifth-power map is injective modulo each prime. Each compatible pair of sum residues is assigned to one partition. The author adds filters modulo 11 and 25, alternative signed-domain and zero-term handling, and explicit primitive-GCD reconstruction.

The implementation described in §5 is **C++ with signed `__int128` arithmetic, OpenMP and an in-place parallel sort**. §6 reports approximately **5.4×10¹⁸ target-condition evaluations**, **10.5 million vCPU-hours** and about **nine months** of work. These are author-reported measurements; we did not execute or independently benchmark the paper's code/hardware.

Our current Mojo census instead builds pair sums **for each `e`**, uses sorted membership lookup and reconstructs all qualifying `a,b` candidates, and is guarded by `e ≤ 1000` with Lean-proved Int64 value bounds. Its search and complexity are **not** the same as Braun's. Do not borrow the author's speedup factors or much larger search coverage for our implementation.

The project formally proves universal mathematical claims (e.g. primitive 5/11 obstructions, abstract pair-index completeness and a signed lower-bound algorithm) and runs bounded Mojo/Python conformance. These do **not** prove full compiler-level refinement or import third-party computational search completeness.

Sources: [Braun §4, algorithms/partitioning](https://arxiv.org/html/2603.05549v4) and [§5–§6, implementation/results](https://arxiv.org/html/2603.05549v4).

## 4. Evidence ledger: what is established here?

| Claim | Status in this repository | Reason |
|---|---|---|
| Braun's tuple satisfies the displayed integer equation | **COMPUTATIONALLY VERIFIED** | Exact Python integers and existing Mojo BigZ CSV lane |
| Braun's tuple has gcd 1 and one negative summand | **COMPUTATIONALLY VERIFIED** | Independent tuple parsing, GCD and sign tests |
| Four reported primitive examples comprise two positive and two signed-only | **REPORTED + ROW-WISE COMPUTATIONALLY VERIFIED** | Historical sourcing + current exact CSV checks, not a proof no others exist |
| Braun v4 reports the two distinct exhaustive/partial domains above | **PRIMARY-SOURCE VERIFIED** | Direct statement in §6 table 3, pinned as author-reported metadata |
| Braun's search **actually exhausts** every required partition in its advertised range | **NOT INDEPENDENTLY REPRODUCED** | Would require inspection of all work units, code, inputs, target coverage, completion manifests and external independent implementation |
| Our Mojo search exhausts the ranges in Braun §6 | **FALSE / NOT CLAIMED** | Current native program has a guard at `e ≤ 1000` and is separately certified at smaller bounds |
| E5-1 through E5-5 | **OPEN / SPECULATIVE** | No infinity, density or distribution proof supplied by this finite discovery |

## 5. Follow-up research, prioritized

**P0 — Primary-source provenance.** Preserve a versioned extract or digest of Braun v4 plus the original source URL. Investigate availability of source code, parameters, partition manifests and checksums, independently of arXiv prose. If those artifacts cannot be obtained, keep the author-reported completeness status explicit.

**P1 — Exact residue partition contracts.** Implement a small bounded reference partitioner around *unordered pair-sum residue pairs*, not naive independent summand residues. Prove coverage and non-overlap of residue-pair partitions; validate arbitrary `M` used only when the fifth-power map has the required property. Do not use Braun's nonnegative partition routine as a signed search without handling negative and zero terms explicitly.

**P1 — Comparison experiment.** For the **same small height range** and positivity convention, compare the current Mojo per-target sorted membership implementation against a two-pointer pair-sum partition prototype, a distinct Python oracle, and exact certificate sets. Include complete input coverage proofs, collision multiplicity handling, deterministic digests, memory and iteration costs. Benchmarks need stated hardware.

**P2 — Structural/theoretical implications.** Braun §7 investigates dominance ratios of known solutions. Its finite-data observation is *not* evidence for E5-3, E5-4 or E5-5 until separate arithmetic arguments or substantially more primitive **positive** examples exist.

## 6. Regression requirements

```sh
python3 tests/verify_braun_primary_evidence.py
python3 tests/verify_known_solutions.py
pixi run --locked verify
```

The literature audit is offline and has no runtime dependency on arXiv availability; it checks frozen *primary-source transcription* against the dataset and runs six deliberate metadata corruptions. It fails closed if the tuple, domain, version, coverage ranges or evidence classification change unexpectedly. If a later arXiv version revises the claims, add a **new** source record/review or explicitly document a version migration—do not silently replace the old primary-source facts.

No numerical operation in this test pretends to reproduce 10.5 million vCPU-hours or cover millions of possible targets.

---

**Source:** Braun, Jeffrey M. (2026), *The fourth known primitive solution to a^5+b^5+c^5+d^5=e^5*, arXiv:2603.05549v4, [versioned primary text](https://arxiv.org/html/2603.05549v4). Posted March 5, 2026; last revised August 21, 2026.
