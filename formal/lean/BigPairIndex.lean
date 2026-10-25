import DigitSumPruning

/-!
Mathematical, lossless structured exact-pair records, with no radix.
The ordered tuple (sum,a,b) is modeled in Nat for positive E5.
Native signed BigZ ordering and merge-sort are checked by execution
against a separate Python oracle, not proved compiler-correct here.
-/
namespace EulerPowers

def exactPairRecords (height : Nat) : List (Nat × Nat × Nat) :=
  (orderedPairs height).map fun pair =>
    (pair.1 ^ 5 + pair.2 ^ 5, pair.1, pair.2)

/-- Source-level exact tuple order: sum first, then a, then b. -/
def exactRecordLE (x y : Nat × Nat × Nat) : Bool :=
  if x.1 < y.1 then true
  else if y.1 < x.1 then false
  else if x.2.1 < y.2.1 then true
  else if y.2.1 < x.2.1 then false
  else x.2.2 ≤ y.2.2

def exactSortedRecords (height : Nat) : List (Nat × Nat × Nat) :=
  (exactPairRecords height).mergeSort exactRecordLE

/-- Sorting retains every mathematical record, including same-sum pairs. -/
theorem exactSortedRecords_mem (e : Nat) (r : Nat × Nat × Nat) :
    r ∈ exactSortedRecords e ↔ r ∈ exactPairRecords e := by
  simp only [exactSortedRecords, List.mem_mergeSort]

/-- Smaller sums always precede larger sums under the defined key order. -/
theorem exactRecord_sum_order (x y : Nat × Nat × Nat)
    (h : x.1 < y.1) : exactRecordLE x y = true := by
  simp [exactRecordLE, h]

/-- Every valid positive quintuple has an exact source pair record,
without loss from packing or reduction modulo a machine integer. -/
theorem valid_exact_pair_record (t : Quintuple) (h : Valid t) :
    (t.a ^ 5 + t.b ^ 5, t.a, t.b) ∈ exactSortedRecords t.e := by
  apply (exactSortedRecords_mem t.e _).2
  unfold exactPairRecords
  obtain ⟨ha, hab, hbc, hcd, hde⟩ := h.2.1
  have hb : t.b < t.e := by omega
  exact List.mem_map.mpr
    ⟨(t.a, t.b), orderedPairs_complete ha hab hb, rfl⟩

/-- Even if the exact pair sum is shared, distinct pair coordinates
are distinct structured records. -/
theorem exact_record_injective
    {s t a b c d : Nat}
    (h : (s, a, b) = (t, c, d)) :
    s = t ∧ a = c ∧ b = d := by
  cases h
  exact ⟨rfl, rfl, rfl⟩

end EulerPowers
