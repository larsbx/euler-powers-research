# Foundations: definitions, geometry, and modular lemmas

## 1. Primitive positive problem

Let \(S_5^+\) consist of \((a,b,c,d,e)\in\mathbb{Z}_{>0}^5\) satisfying
\(a\le b\le c\le d<e\), \(a^5+b^5+c^5+d^5=e^5\), and
\(\gcd(a,b,c,d,e)=1\).

Primitivity removes scalar duplicates. The restriction to positive summands excludes solutions with a negative base.

## 2. PROVED: modulo-11 divisibility

**Lemma.** For a primitive integer solution (signed bases permitted), the number of entries divisible by 11 is exactly **one or three**.

**Proof.** Every fifth power modulo 11 is in \(\{0,1,-1\}\), and a fifth power is zero modulo 11 exactly when its base is divisible by 11. Moving the target to the left, the five terms each contribute \(0,\pm1\). With \(k\) nonzero contributions, \(k\le5\), their sum can vanish modulo 11 only if their ordinary integer sum is zero, since its absolute value is at most 5. Such a sum must have an even number \(k\) of terms. Thus the number \(5-k\) of zero terms is odd, hence 1, 3, or 5. Five zero entries contradict primitivity. QED.

## 3. PROVED: modulo-25 divisibility

**Lemma.** For a primitive integer solution (signed bases permitted), the number of entries divisible by 5 is exactly **one or three**.

**Proof.** Fifth-power residues modulo 25 are \(0,\pm1,\pm7\), with residue zero iff the base is divisible by 5. In a signed sum of five fifth powers the nonzero contributions therefore belong to \(\{\pm1,\pm7\}\). For an odd number \(k=1,3,5\) of nonzero contributions, the integer sum is odd. For \(k=1\) or \(3\), its absolute value is at most 21, so it cannot vanish modulo 25. For \(k=5\), its absolute value is at most 35; a multiple of 25 would have absolute value 25. If at most three contributions have magnitude 7, the sum has absolute value at most \(3\cdot7+2=23\). If exactly four have magnitude 7, the possible absolute values of the sum (including the \(\pm1\)) are \(1,13,15,27,29\). If all five have magnitude 7, possible absolute values are \(7,21,35\). None equals 25. Thus \(k\) cannot be odd; among five entries the number divisible by 5 is odd. Primitivity again excludes five. QED.

**Caution.** The two lemmas do not say the same entry must be divisible by both 5 and 11.

## 4. PROVED: smooth projective hypersurface

Put
\[
X_5=\{[a:b:c:d:e]\in\mathbb P^4_{\mathbb Q}:
a^5+b^5+c^5+d^5-e^5=0\}.
\]
The partial derivatives vanish simultaneously only at the origin of affine five-space, which is not a projective point. Hence \(X_5\) is a smooth threefold.

By adjunction,
\[
K_{X_5}\cong\mathcal O_{X_5}(5-5)\cong\mathcal O_{X_5}.
\]
Thus \(X_5\) is a Calabi–Yau quintic threefold.

Positive rational projective points, modulo permutation of the four summands, correspond to primitive positive integer solutions. This geometric identification **does not** itself show infinitude.

## 5. PROVED: near-cancellation identity and bound

With \(\delta=e-d>0\),
\[
a^5+b^5+c^5
=5\delta d^4+10\delta^2d^3+10\delta^3d^2+5\delta^4d+\delta^5.
\]
For fixed \(\delta\), each of \(a,b,c\) is \(O_\delta(d^{4/5})\). The fixed-\(\delta\) arithmetic classification remains open.

## 6. Verification limits

The residue claims are general proofs. A program enumerating finitely many solutions, moduli, or height bounds is not a substitute for a proof of infinitude, finiteness, or density.
