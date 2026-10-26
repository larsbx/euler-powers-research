import Cyclotomic5

/-! Exact signed-integer equations for pair reconstruction. These prove the
algebraic necessary conditions, not the native enumerator or integer sqrt. -/
namespace EulerPowers

def pairSumModel (s p : Int) : Int := s*(s^4-5*p*s^2+5*p^2)

theorem fifth_pair_sum_model (a b : Int) :
    a^5+b^5 = pairSumModel (a+b) (a*b) := by
  simp only [pairSumModel]
  grind

theorem pair_sum_divisor (a b : Int) : (a+b) ∣ a^5+b^5 := by
  exact ⟨phi10 a b, fifth_sum_factor a b⟩

theorem pair_sum_discriminant (a b : Int) :
    5*(a+b)^4+20*phi10 a b = (5*(a^2+b^2))^2 := by
  simp only [phi10]
  grind

theorem pair_model_discriminant (s p q : Int)
    (h : q=s^4-5*p*s^2+5*p^2) :
    5*s^4+20*q = (5*s^2-10*p)^2 := by
  subst q
  grind

theorem pair_recover_product (a b : Int) :
    5*(a+b)^2-5*(a^2+b^2) = 10*(a*b) := by grind

theorem pair_recover_difference (a b : Int) :
    (a+b)^2-4*(a*b) = (a-b)^2 := by grind

theorem pair_zero_sum (a b : Int) : a+b=0 ↔ a= -b := by omega

end EulerPowers
