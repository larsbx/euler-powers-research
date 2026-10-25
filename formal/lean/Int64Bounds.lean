import EulerPowers

/-!
# Exact machine-range safety obligations for the bounded Mojo search

The native enumerator refuses upper height > 1000 and uses Int64 for
fifth powers, pair sums and signed complements. These kernel-checked
inequalities certify that all *mathematical intermediate values* of
those expressions lie in Int64's closed range for accepted heights.
This proves the arithmetic bound, not correctness of machine lowering.
-/

namespace EulerPowers

def MaxSearchHeight : Nat := 1000
def FifthCap : Nat := 1000000000000000
def PairCap : Nat := 2000000000000000
def Int64Max : Nat := 9223372036854775807

/-- A fifth power of an admitted nonnegative base never exceeds 10^15. -/
theorem fifth_bound (x : Nat) (h : x ≤ MaxSearchHeight) :
    x ^ 5 ≤ FifthCap := by
  have hp := Nat.pow_le_pow_left h 5
  have hnum : MaxSearchHeight ^ 5 = FifthCap := by decide
  simpa only [hnum] using hp

/-- The pair-sum array never exceeds 2·10^15. -/
theorem pair_sum_bound (a b : Nat)
    (ha : a ≤ MaxSearchHeight) (hb : b ≤ MaxSearchHeight) :
    a ^ 5 + b ^ 5 ≤ PairCap := by
  have h1 := fifth_bound a ha
  have h2 := fifth_bound b hb
  unfold FifthCap PairCap at *
  omega

/-- All individual cached fifth powers and pair sums fit signed Int64. -/
theorem pair_fits_int64 (a b : Nat)
    (ha : a ≤ MaxSearchHeight) (hb : b ≤ MaxSearchHeight) :
    a ^ 5 + b ^ 5 ≤ Int64Max := by
  have hsum := pair_sum_bound a b ha hb
  unfold PairCap Int64Max at *
  omega

/-- The signed mathematical subtraction performed by the Mojo prefilter.
The subtraction MUST NOT be interpreted as Nat subtraction. -/
def signedComplement (e c d : Nat) : Int :=
  Int.ofNat (e ^ 5) - Int.ofNat (c ^ 5) - Int.ofNat (d ^ 5)

/-- The prefilter complement is in [-2·10^15, 10^15].
In particular, a negative complement is representable, not wrapped. -/
theorem signed_complement_bound (e c d : Nat)
    (he : e ≤ MaxSearchHeight)
    (hc : c ≤ MaxSearchHeight)
    (hd : d ≤ MaxSearchHeight) :
    -(PairCap : Int) ≤ signedComplement e c d ∧
    signedComplement e c d ≤ (FifthCap : Int) := by
  have e5 := fifth_bound e he
  have c5 := fifth_bound c hc
  have d5 := fifth_bound d hd
  have hei : Int.ofNat (e ^ 5) ≤ (FifthCap : Int) :=
    Int.ofNat_le.mpr e5
  have hci : Int.ofNat (c ^ 5) ≤ (FifthCap : Int) :=
    Int.ofNat_le.mpr c5
  have hdi : Int.ofNat (d ^ 5) ≤ (FifthCap : Int) :=
    Int.ofNat_le.mpr d5
  have heNonneg : (0 : Int) ≤ Int.ofNat (e ^ 5) := Int.natCast_nonneg _
  have hcNonneg : (0 : Int) ≤ Int.ofNat (c ^ 5) := Int.natCast_nonneg _
  have hdNonneg : (0 : Int) ≤ Int.ofNat (d ^ 5) := Int.natCast_nonneg _
  unfold signedComplement
  unfold PairCap FifthCap at *
  constructor <;> omega

/-- All signed complement values fit the Int64 range. -/
theorem complement_fits_int64 (e c d : Nat)
    (he : e ≤ MaxSearchHeight)
    (hc : c ≤ MaxSearchHeight)
    (hd : d ≤ MaxSearchHeight) :
    -(9223372036854775808 : Int) ≤ signedComplement e c d ∧
    signedComplement e c d ≤ (9223372036854775807 : Int) := by
  have hbound := signed_complement_bound e c d he hc hd
  unfold PairCap FifthCap at hbound
  omega

/-- The Mojo source uses five successive multiplications by the base.
Those exact natural operations agree with the fifth-power expression. -/
theorem fifth_mul_expansion (x : Nat) :
    x * x * x * x * x = x ^ 5 := by
  simp [Nat.pow_succ, Nat.mul_assoc]

/-- Bounds at all intermediate multiplications, including x=0. -/
theorem intermediate_power_bound (x k : Nat) (hx : x ≤ MaxSearchHeight)
    (hk : k ≤ 5) : x ^ k ≤ FifthCap := by
  by_cases hz : x = 0
  · subst x
    cases k with
    | zero => decide
    | succ k => simp [FifthCap]
  · have hxpos : 0 < x := by omega
    exact Nat.le_trans (Nat.pow_le_pow_right hxpos hk) (fifth_bound x hx)

end EulerPowers
