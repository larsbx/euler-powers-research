import EulerPowers

/-! Exact integer polynomial identities underlying the fifth cyclotomic norm.
No analytic complex numbers, root approximations, field factorization axioms,
or assertion that the native quotient-ring implementation has been proved.
-/
namespace EulerPowers

def phi5 (x y : Int) : Int := x^4+x^3*y+x^2*y^2+x*y^3+y^4
def phi10 (x y : Int) : Int := x^4-x^3*y+x^2*y^2-x*y^3+y^4

macro "polynomial_identity" : tactic => `(tactic| (
  simp only [phi5, phi10]; grind))

theorem fifth_difference_factor (x y : Int) :
    x^5-y^5 = (x-y)*phi5 x y := by polynomial_identity

theorem fifth_sum_factor (x y : Int) :
    x^5+y^5 = (x+y)*phi10 x y := by polynomial_identity

theorem phi5_diagonal (y : Int) : phi5 y y = 5*y^4 := by
  polynomial_identity

theorem phi5_gap_remainder (x y : Int) :
    phi5 x y = (x-y)*(x^3+2*x^2*y+3*x*y^2+4*y^3)+5*y^4 := by
  polynomial_identity

theorem phi10_sum_remainder (x y : Int) :
    phi10 x y = (x+y)*(x^3-2*x^2*y+3*x*y^2-4*y^3)+5*y^4 := by
  polynomial_identity

theorem phi5_gap_expansion (y t : Int) :
    phi5 (y+t) y = t^4+5*y*t^3+10*y^2*t^2+10*y^3*t+5*y^4 := by
  polynomial_identity

theorem phi5_ramified_remainder (y k : Int) :
    phi5 (y+5*k) y =
      25*(25*k^4+25*y*k^3+10*y^2*k^2+2*y^3*k)+5*y^4 := by
  polynomial_identity

theorem phi5_ramified_mod25 (y k : Int) :
    phi5 (y+5*k) y % 25 = (5*y^4) % 25 := by
  rw [phi5_ramified_remainder]
  omega

end EulerPowers
