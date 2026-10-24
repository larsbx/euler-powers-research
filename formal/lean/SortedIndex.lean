import PairIndex

/-!
# Sorting does not discard complements.

This proof connects the finite exhaustive pair-sum index to a sorted
mathematical index and a decidable membership predicate. It does NOT
prove the generated native Mojo binary-search loop implements this
predicate; the compiled loop has separate adversarial conformance tests.
-/

namespace EulerPowers

def sortedPairSums (e : Nat) : List Nat :=
  (pairSums e).mergeSort (fun a b => decide (a ≤ b))

/-- Permutation preservation for the exact fifth-power index. -/
theorem sorted_membership_iff (e target : Nat) :
    target ∈ sortedPairSums e ↔ target ∈ pairSums e := by
  simp only [sortedPairSums, List.mem_mergeSort]

/-- Every target reported by a sorted mathematical membership test occurs
in the underlying exhaustive pair index, and conversely. -/
theorem sorted_contains_iff (e target : Nat) :
    ((sortedPairSums e).contains target = true) ↔ target ∈ pairSums e := by
  simpa only [List.contains_iff_mem] using sorted_membership_iff e target

/-- Sorting cannot remove the complement of any primitive positive solution. -/
theorem valid_sorted_hit (t : Quintuple) (h : Valid t) :
    (sortedPairSums t.e).contains
        (t.e ^ 5 - (t.c ^ 5 + t.d ^ 5)) = true := by
  exact (sorted_contains_iff t.e _).mpr (valid_pair_hit t h)

end EulerPowers
