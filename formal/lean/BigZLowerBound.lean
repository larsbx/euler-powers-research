import SignedLowerBound
import BigPairIndex

/-!
Exact mathematical lower-bound contract for radix-free BigZ records.

Arbitrary signed sums are modeled by Lean Int, not machine Int64.
Provided the projection of structured records is sorted, the
certified recursive search returns precisely the first possible
equal-sum record, even through duplicate keys and >2^63 magnitudes.
The native trace-replay gate separately checks observed Mojo branches.
-/

namespace EulerPowers

def bigzRecordSums (records : List (Int × Nat × Nat)) : List Int :=
  records.map (fun r => r.1)

/-- Every exact record sum occurs in the lossless projected list. -/
theorem bigzRecordSums_mem (records : List (Int × Nat × Nat))
    (target : Int) :
    target ∈ bigzRecordSums records ↔
    ∃ record ∈ records, record.1 = target := by
  simp [bigzRecordSums, List.mem_map]

/-- Given sorted exact sums, binary search retrieves an exact
record if and only if any record has that sum. No Int64 bound. -/
theorem bigzRecordLowerBound_correct
    (records : List (Int × Nat × Nat)) (target : Int)
    (hSort : (bigzRecordSums records).Pairwise (· ≤ ·)) :
    (∃ h : (signedLowerBound (bigzRecordSums records) target
        0 (bigzRecordSums records).length hSort
        (signedInitial (bigzRecordSums records) target)).1 <
          (bigzRecordSums records).length,
      (bigzRecordSums records)[
        (signedLowerBound (bigzRecordSums records) target
          0 (bigzRecordSums records).length hSort
          (signedInitial (bigzRecordSums records) target)).1] = target)
      ↔ ∃ record ∈ records, record.1 = target := by
  rw [signedLowerBound_correct (bigzRecordSums records) target hSort]
  exact bigzRecordSums_mem records target

/-- Every prefix before the certified index has strictly smaller
sums; duplicate equal-sum records cannot be skipped. -/
theorem bigzRecordLowerBound_first
    (records : List (Int × Nat × Nat)) (target : Int)
    (hSort : (bigzRecordSums records).Pairwise (· ≤ ·))
    (i : Nat) (hi : i < (bigzRecordSums records).length)
    (hBefore : i < (signedLowerBound
      (bigzRecordSums records) target 0 (bigzRecordSums records).length
      hSort (signedInitial (bigzRecordSums records) target)).1) :
    (bigzRecordSums records)[i] < target := by
  let result := signedLowerBound (bigzRecordSums records) target 0
    (bigzRecordSums records).length hSort
    (signedInitial (bigzRecordSums records) target)
  exact result.2.2.2.1 i hi hBefore

/-- Every suffix position at/after the lower bound has sum >= target. -/
theorem bigzRecordLowerBound_suffix
    (records : List (Int × Nat × Nat)) (target : Int)
    (hSort : (bigzRecordSums records).Pairwise (· ≤ ·))
    (i : Nat) (hi : i < (bigzRecordSums records).length)
    (hAfter : (signedLowerBound
      (bigzRecordSums records) target 0 (bigzRecordSums records).length
      hSort (signedInitial (bigzRecordSums records) target)).1 ≤ i) :
    target ≤ (bigzRecordSums records)[i] := by
  let result := signedLowerBound (bigzRecordSums records) target 0
    (bigzRecordSums records).length hSort
    (signedInitial (bigzRecordSums records) target)
  exact result.2.2.2.2 i hi hAfter

end EulerPowers
