import BigZLowerBound

/-!
Source-level sorted-permutation theorem for exact signed BigZ record keys.

The mathematical model is a signed sum with two natural pair indices,
ordered lexicographically. The concrete native Mojo stable bottom-up
mergesort is tested separately against an independent Python oracle.
These proofs do not prove the compiler implements the source.
-/

namespace EulerPowers

abbrev ExactSignedPair := Int × Nat × Nat

def exactSignedPairLE (x y : ExactSignedPair) : Bool :=
  if x.1 < y.1 then true
  else if y.1 < x.1 then false
  else if x.2.1 < y.2.1 then true
  else if y.2.1 < x.2.1 then false
  else decide (x.2.2 ≤ y.2.2)

def exactSignedPairSort (xs : List ExactSignedPair) : List ExactSignedPair :=
  xs.mergeSort exactSignedPairLE

theorem exactSignedPairLE_iff (x y : ExactSignedPair) :
    exactSignedPairLE x y = true ↔
      x.1 < y.1 ∨
        (x.1 = y.1 ∧ (x.2.1 < y.2.1 ∨
          (x.2.1 = y.2.1 ∧ x.2.2 ≤ y.2.2))) := by
  unfold exactSignedPairLE
  split_ifs <;> simp_all <;> omega

theorem exactSignedPairLE_trans (x y z : ExactSignedPair)
    (hxy : exactSignedPairLE x y = true)
    (hyz : exactSignedPairLE y z = true) :
    exactSignedPairLE x z = true := by
  apply (exactSignedPairLE_iff x z).2
  have ha := (exactSignedPairLE_iff x y).1 hxy
  have hb := (exactSignedPairLE_iff y z).1 hyz
  omega

theorem exactSignedPairLE_total (x y : ExactSignedPair) :
    (exactSignedPairLE x y || exactSignedPairLE y x) = true := by
  by_cases h : exactSignedPairLE x y = true
  · simp [h]
  · have hback : exactSignedPairLE y x = true := by
      apply (exactSignedPairLE_iff y x).2
      have hn : ¬ (x.1 < y.1 ∨
        (x.1 = y.1 ∧ (x.2.1 < y.2.1 ∨
          (x.2.1 = y.2.1 ∧ x.2.2 ≤ y.2.2)))) := by
        intro hh
        exact h ((exactSignedPairLE_iff x y).2 hh)
      omega
    simp [hback]

theorem exactSignedPairSort_permutation (xs : List ExactSignedPair) :
    (exactSignedPairSort xs).Perm xs := by
  simpa [exactSignedPairSort] using
    List.mergeSort_perm xs exactSignedPairLE

theorem exactSignedPairSort_sorted (xs : List ExactSignedPair) :
    (exactSignedPairSort xs).Pairwise
      (fun x y => exactSignedPairLE x y = true) := by
  exact List.pairwise_mergeSort
    exactSignedPairLE_trans exactSignedPairLE_total xs

theorem exactSignedPairSort_preserves_all (xs : List ExactSignedPair)
    (record : ExactSignedPair) :
    record ∈ exactSignedPairSort xs ↔ record ∈ xs := by
  simpa [exactSignedPairSort] using
    (List.mem_mergeSort (a := record) (l := xs)
      (le := exactSignedPairLE))

theorem exactSignedPairLE_sum_monotone (x y : ExactSignedPair)
    (h : exactSignedPairLE x y = true) :
    x.1 ≤ y.1 := by
  have h' := (exactSignedPairLE_iff x y).1 h
  omega

/-- The precise sorted-list hypothesis used by BigZLowerBound is now
proved for the mathematical sorted output, rather than assumed. -/
theorem exactSignedPairSort_sum_order (xs : List ExactSignedPair) :
    (bigzRecordSums (exactSignedPairSort xs)).Pairwise (· ≤ ·) := by
  exact (exactSignedPairSort_sorted xs).map
    (fun record => record.1)
    (fun x y h => exactSignedPairLE_sum_monotone x y h)

theorem exactSignedPairSort_lowerBound_correct
    (xs : List ExactSignedPair) (target : Int) :
    (∃ h : (signedLowerBound
        (bigzRecordSums (exactSignedPairSort xs)) target 0
        (bigzRecordSums (exactSignedPairSort xs)).length
        (exactSignedPairSort_sum_order xs)
        (signedInitial (bigzRecordSums (exactSignedPairSort xs)) target)).1 <
            (bigzRecordSums (exactSignedPairSort xs)).length,
      (bigzRecordSums (exactSignedPairSort xs))[
        (signedLowerBound
          (bigzRecordSums (exactSignedPairSort xs)) target 0
          (bigzRecordSums (exactSignedPairSort xs)).length
          (exactSignedPairSort_sum_order xs)
          (signedInitial (bigzRecordSums (exactSignedPairSort xs)) target)).1] =
          target) ↔ ∃ record ∈ xs, record.1 = target := by
  rw [bigzRecordLowerBound_correct
    (exactSignedPairSort xs) target (exactSignedPairSort_sum_order xs)]
  constructor
  · rintro ⟨record, hr, heq⟩
    exact ⟨record, (exactSignedPairSort_preserves_all xs record).1 hr, heq⟩
  · rintro ⟨record, hr, heq⟩
    exact ⟨record, (exactSignedPairSort_preserves_all xs record).2 hr, heq⟩

end EulerPowers
