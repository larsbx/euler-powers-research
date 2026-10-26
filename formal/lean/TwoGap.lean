import EulerPowers

/-! Exact identities behind the two-gap search and independent nested-square
reconstruction. These do not formalize the native loops, sqrt or compiler. -/
namespace EulerPowers

theorem two_gap_expansion (r h : Int) :
    (r+h)^5-r^5 = h*(5*r^4+10*h*r^3+10*h^2*r^2+5*h^3*r+h^4) := by
  grind

theorem two_gap_centered_square (r h : Int) :
    16*((r+h)^5-r^5)+4*h^5 = 5*h*((2*r+h)^2+h^2)^2 := by
  grind

theorem two_gap_quotient_square (r h : Int) :
    16*(5*r^4+10*h*r^3+10*h^2*r^2+5*h^3*r+h^4)+4*h^4 =
      5*((2*r+h)^2+h^2)^2 := by grind

theorem two_gap_successor_difference (r h : Int) :
    ((r+1+h)^5-(r+1)^5)-((r+h)^5-r^5) =
      h*(20*r^3+(30*h+30)*r^2+(20*h^2+30*h+20)*r+
        5*h^3+10*h^2+10*h+5) := by grind

theorem two_gap_signed_rearrangement (e d b r h : Int) :
    e^5-d^5-b^5 = -((r+h)^5-r^5) ↔
      -(r+h)^5+b^5+r^5+d^5=e^5 := by omega

end EulerPowers
