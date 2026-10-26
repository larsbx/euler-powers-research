import EulerPowers

/-! Exact modular identities and small-intermediate bounds for P19.
These do not prove native compiler lowering or the bounded image builder. -/
namespace EulerPowers

theorem cached_positive_residue (x y m : Int) :
    (x % m + m - y % m) % m = (x-y) % m := by
  simp [Int.sub_emod]

theorem cached_negative_residue (x y m : Int) :
    (x % m + y % m) % m = (x+y) % m := by
  exact (Int.add_emod x y m).symm

theorem cached_positive_machine_bound (l r m : Int)
    (hm : 0<m) (hmax : m<=99000)
    (hl : 0<=l ∧ l<m) (hr : 0<=r ∧ r<m) :
    0<=l+m-r ∧ l+m-r<198000 := by omega

theorem cached_negative_machine_bound (l r m : Int)
    (hm : 0<m) (hmax : m<=99000)
    (hl : 0<=l ∧ l<m) (hr : 0<=r ∧ r<m) :
    0<=l+r ∧ l+r<198000 := by omega

theorem deferred_positive_guard (positive gates : Bool) :
    (positive && gates) = (gates && positive) := by
  cases positive <;> cases gates <;> decide

end EulerPowers
