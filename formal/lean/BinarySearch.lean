import SortedIndex

/-!
# Soundness of one lower-bound binary-search narrowing step

For an arbitrary sorted finite list and arbitrary target, a pivot below
the target proves that everything at or before that pivot is not a hit.
Conversely, a pivot above the target proves that the pivot and every
following entry are not hits.

These are universal mathematical loop-invariant lemmas, not a verification
of the compiled Mojo index bounds, arithmetic narrowing, or termination.
-/

namespace EulerPowers

/-- Discarding the entire prefix through a pivot smaller than the target
cannot hide a matching element. This is exactly the strict-left branch
of the Mojo `contains_sorted` lower-bound implementation. -/
theorem lowerBound_discard_prefix (xs : List Nat) (target mid : Nat)
    (hSort : xs.Pairwise (· ≤ ·)) (hMid : mid < xs.length)
    (hPivot : xs[mid] < target)
    (i : Nat) (hi : i < xs.length) (hBefore : i ≤ mid) :
    xs[i] ≠ target := by
  have hle : xs[i] ≤ xs[mid] := by
    rcases Nat.lt_or_eq_of_le hBefore with hlt | heq
    · exact hSort.rel_getElem_of_lt hi hMid hlt
    · subst i
      exact Nat.le_refl _
  omega

/-- If the target is strictly below the pivot, the pivot and all later
entries cannot equal the target; narrowing the search to the strict
prefix is safe. -/
theorem lowerBound_discard_suffix (xs : List Nat) (target mid : Nat)
    (hSort : xs.Pairwise (· ≤ ·)) (hMid : mid < xs.length)
    (hPivot : target < xs[mid])
    (i : Nat) (hi : i < xs.length) (hAfter : mid ≤ i) :
    xs[i] ≠ target := by
  have hle : xs[mid] ≤ xs[i] := by
    rcases Nat.lt_or_eq_of_le hAfter with hlt | heq
    · exact hSort.rel_getElem_of_lt hMid hi hlt
    · subst i
      exact Nat.le_refl _
  omega

/-- The returned pivot itself is a sufficient exact membership witness. -/
theorem lowerBound_equal_witness (xs : List Nat) (target mid : Nat)
    (hMid : mid < xs.length) (hEq : xs[mid] = target) :
    target ∈ xs := by
  rw [← hEq]
  exact List.getElem_mem hMid

end EulerPowers
