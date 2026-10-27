import EulerPowers

/-! Integer reductions used by P21. Native traversal, BigZ implementation,
resource accounting and sorting are independently tested, not kernel proofs. -/
namespace EulerPowers

theorem signed_box_pair_triple (a b c d e : Int) :
    a^5+b^5+c^5+d^5+e^5=0 ↔ a^5+b^5= -(c^5+d^5+e^5) := by omega

theorem signed_box_global_sign (a b c d e : Int) :
    a^5+b^5+c^5+d^5+e^5=0 ↔
    (-e)^5+(-d)^5+(-c)^5+(-b)^5+(-a)^5=0 := by
  grind

theorem signed_box_reverse_order (a b c d e : Int)
    (hab : a≤b) (hbc : b≤c) (hcd : c≤d) (hde : d≤e) :
    -e ≤ -d ∧ -d ≤ -c ∧ -c ≤ -b ∧ -b ≤ -a := by omega

theorem signed_box_median_orientation (c : Int) (hc : c≠0) :
    0<c ∨ 0< -c := by omega

theorem signed_box_positive_tail (c d e : Int)
    (hc : 0<c) (hcd : c≤d) (hde : d≤e) : 0<d ∧ 0<e := by omega

end EulerPowers
