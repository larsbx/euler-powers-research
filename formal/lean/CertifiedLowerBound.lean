import LowerBoundInvariant

/-!
# Total, proof-carrying lower-bound search in Lean

This algorithm follows the same mathematical midpoint and narrowing
rules as Mojo's `contains_sorted`. Every recursive call carries the
full lower-bound window invariant. The unchecked interval length
strictly decreases, so Lean checks termination.

The result's subtype proof states that the final window has converged
and still satisfies the search invariant. Correct membership follows
from `lowerBound_done` even when the sorted list has duplicates.

This proves the *Lean algorithm*, not compiler-level equivalence to
native Mojo or to its sorting implementation.
-/

namespace EulerPowers

def certifiedLowerBound (xs : List Nat) (target lo hi : Nat)
    (hSort : xs.Pairwise (· ≤ ·))
    (hInv : LowerBoundInv xs target lo hi) :
    {pos : Nat // LowerBoundInv xs target pos pos} := by
  if hMore : lo < hi then
    let mid := lo + (hi - lo) / 2
    have hmidLo : lo ≤ mid := (lowerBound_midpoint lo hi hMore).1
    have hmidHi : mid < hi := (lowerBound_midpoint lo hi hMore).2
    have hIdx : mid < xs.length :=
      lowerBound_midpoint_inbounds xs target lo hi hInv hMore
    if hPivot : xs[mid] < target then
      exact certifiedLowerBound xs target (mid + 1) hi hSort
        (lowerBound_less_preserves xs target lo hi mid hSort hInv
          hmidLo hmidHi hPivot)
    else
      have hGe : target ≤ xs[mid] := by omega
      exact certifiedLowerBound xs target lo mid hSort
        (lowerBound_ge_preserves xs target lo hi mid hSort hInv
          hmidLo hmidHi hGe)
  else
    have hEq : hi = lo := by
      have hlo := hInv.1
      omega
    subst hi
    exact ⟨lo, hInv⟩
termination_by hi - lo
decreasing_by
  all_goals omega

/-- A proof that the *entire* recursive search returns a valid
lower bound, not just that each iteration step is locally safe. -/
theorem certifiedLowerBound_correct (xs : List Nat) (target : Nat)
    (hSort : xs.Pairwise (· ≤ ·)) :
    (∃ h : (certifiedLowerBound xs target 0 xs.length hSort
        (lowerBound_initial xs target)).1 < xs.length,
      xs[(certifiedLowerBound xs target 0 xs.length hSort
        (lowerBound_initial xs target)).1] = target) ↔
      target ∈ xs := by
  let result := certifiedLowerBound xs target 0 xs.length hSort
    (lowerBound_initial xs target)
  exact lowerBound_done xs target result.1 hSort result.2

end EulerPowers
