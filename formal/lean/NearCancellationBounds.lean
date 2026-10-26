import EulerPowers

/-!
Exact necessary bounds for finite near-cancellation stripes. These theorems
justify omitting an impossible c prefix; they do not prove native lowering,
binary-search implementation, or absence of solutions outside declared cells.
D+u^5=b^5+c^5 is the natural-number form of D=-u^5+b^5+c^5.
-/
namespace EulerPowers

theorem positive_two_term_bound (a b c A D : Nat)
    (ha : a ≤ A) (hb : b ≤ c) (identity : D = a^5+b^5+c^5) :
    D ≤ A^5+2*c^5 := by
  have hA := Nat.pow_le_pow_left ha 5
  have hB := Nat.pow_le_pow_left hb 5
  omega

theorem positive_prefix_impossible (a b c A D : Nat)
    (ha : a ≤ A) (hb : b ≤ c) (excluded : A^5+2*c^5 < D) :
    D ≠ a^5+b^5+c^5 := by
  intro identity
  have h := positive_two_term_bound a b c A D ha hb identity
  omega

theorem negative_two_term_bound (u b c D : Nat)
    (hb : b ≤ c) (identity : D+u^5 = b^5+c^5) :
    D ≤ 2*c^5 := by
  have hB := Nat.pow_le_pow_left hb 5
  omega

theorem negative_prefix_impossible (u b c D : Nat)
    (hb : b ≤ c) (excluded : 2*c^5 < D) :
    D+u^5 ≠ b^5+c^5 := by
  intro identity
  have h := negative_two_term_bound u b c D hb identity
  omega

theorem negative_c_upper (u b c A D : Nat)
    (hu : u ≤ A) (identity : D+u^5 = b^5+c^5) :
    c^5 ≤ D+A^5 := by
  have hU := Nat.pow_le_pow_left hu 5
  omega

end EulerPowers
