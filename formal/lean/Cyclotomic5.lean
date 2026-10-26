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

/-! A coefficient model of the implemented quotient multiplication. This is
not a proof about compiler lowering or the imported BigZ implementation. -/
structure Cyclo5Int where
  c0 : Int
  c1 : Int
  c2 : Int
  c3 : Int
  deriving Repr, DecidableEq

def cyclo5Mul (a b : Cyclo5Int) : Cyclo5Int :=
  let r := a.c1*b.c3+a.c2*b.c2+a.c3*b.c1
  ⟨a.c0*b.c0+a.c2*b.c3+a.c3*b.c2-r,
   a.c0*b.c1+a.c1*b.c0+a.c3*b.c3-r,
   a.c0*b.c2+a.c1*b.c1+a.c2*b.c0-r,
   a.c0*b.c3+a.c1*b.c2+a.c2*b.c1+a.c3*b.c0-r⟩

theorem cyclo5_mul_comm (a b : Cyclo5Int) : cyclo5Mul a b = cyclo5Mul b a := by
  cases a; cases b
  simp only [cyclo5Mul]
  congr 1 <;> grind

theorem cyclo5_mul_assoc (a b c : Cyclo5Int) :
    cyclo5Mul (cyclo5Mul a b) c = cyclo5Mul a (cyclo5Mul b c) := by
  cases a; cases b; cases c
  simp only [cyclo5Mul]
  congr 1 <;> grind

theorem cyclo5_mul_one (a : Cyclo5Int) : cyclo5Mul a ⟨1,0,0,0⟩ = a := by
  cases a
  simp [cyclo5Mul]

/-- The four conjugates of x-y*z multiply to the scalar Q(x,y). -/
theorem cyclo5_difference_norm (x y : Int) :
    cyclo5Mul (cyclo5Mul ⟨x,-y,0,0⟩ ⟨x,0,-y,0⟩)
      (cyclo5Mul ⟨x,0,0,-y⟩ ⟨x+y,y,y,y⟩) = ⟨phi5 x y,0,0,0⟩ := by
  simp only [cyclo5Mul, phi5]
  congr 1 <;> grind

end EulerPowers
