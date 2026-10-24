# Open questions and conjectures

Every statement below is **OPEN**. E5-3 to E5-5 are explicitly **speculative**. Naming them is not an assertion of their truth.

Define \(N_5(B)\) as in the README for positive primitive ordered solutions.

## E5-1 — Primitive infinitude

**Conjecture.** \(N_5(B)\to\infty\) as \(B\to\infty\).

**Equivalent question.** Does the equation admit arbitrarily large primitive positive solutions?

**Possible routes.** Produce an infinite positive rational family, or prove existence through an arithmetic-geometric method. A repeated scaling construction does not suffice.

## E5-2 — Zariski density

**Conjecture.** The positive rational projective points of the smooth quintic
\(X_5:a^5+b^5+c^5+d^5=e^5\subset\mathbb P^4_{\mathbb Q}\)
are Zariski dense in \(X_5\).

**Implication.** E5-2 implies E5-1. The converse need not hold: infinitely many points could lie on a proper subvariety.

**Subproblem.** Find a rational curve in \(X_5\) that has infinitely many rational points with all coordinates strictly positive. (Do not confuse this with cancellation lines that leave the positive region.)

## E5-3 — Logarithmic counting

**Speculative conjecture.** There is \(C_5>0\) with
\[
N_5(B)\sim C_5\log B.
\]

**Heuristic, not proof.** Near height \(B\), there are \(O(B^4)\) ordered choices of four summands; the gap between consecutive target fifth powers is \(O(B^4)\). A naive random-value estimate suggests \(O(1)\) coincidences per dyadic interval and hence logarithmic accumulation. Congruence effects and contributions from rational curves may invalidate this model.

**Falsification targets.** Any proven finiteness, a lower bound growing faster than \(\log B\), or a provably incompatible count on a subfamily.

## E5-4 — Boundary accumulation

**Speculative conjecture.** There exist distinct positive primitive solutions with \(e\to\infty\) and
\[
(e-d)/e\to0.
\]

**Unproved refinements, not additional assumptions.** Classify fixed \(\delta=e-d\) and sublinear \(\delta=O(e^\theta)\), \(0\le\theta<1\).

The two known positive solutions have gaps \(11\) and \(77\); this is too little information to assert a divisibility law for all gaps.

## E5-5 — Arithmetic shape equidistribution

Normalize each solution by \(e\). Write
\[
\Omega=\{0<x_1\le x_2\le x_3\le x_4<1:\sum_{i=1}^4x_i^5=1\}.
\]
Let \(\mu\) be the normalized Leray measure on this ordered positive real locus, obtained on regular coordinate patches by \(dx_1\,dx_2\,dx_3/(5x_4^4)\). Let \(N_5(B;U)\) count primitive positive solutions with height \(e\le B\) whose normalized shape lies in \(U\).

**Very speculative conjecture.** For each sufficiently regular relatively open \(U\subset\Omega\) with \(\mu(U)>0\),
\[
N_5(B;U)\sim C_5\mu(U)\log B
\]
for a single \(C_5>0\).

If true, E5-5 implies E5-3, E5-2, and E5-4 (by choosing successively smaller open neighborhoods toward \(x_4=1\)), hence E5-1. The precise candidate measure and even logarithmic growth are unverified; alternative height distributions must be tested.

## Dependency map

- E5-2 \(\Rightarrow\) E5-1.
- E5-3 \(\Rightarrow\) E5-1.
- E5-4 \(\Rightarrow\) E5-1.
- E5-5 \(\Rightarrow\) E5-2, E5-3, E5-4, and therefore E5-1.
- No implication between E5-2 and E5-3 is asserted.

## Separate higher-exponent question

For \(n\ge6\), investigate positive primitive solutions of
\[
a_1^n+\cdots+a_{n-1}^n=b^n.
\]
Do **not** confuse this with equal sums having several terms on each side or treat counterexamples for \(n=4,5\) as evidence of universal failure for all \(n\).

## Status protocol

Record date, precise domain (positive vs signed), hypothesis, evidence, counterexample search, and the strongest logically justified conclusion for every new conjecture.
