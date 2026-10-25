import PairPartition

/-!
Source-level refinement obligation for a single-pass right-pair traversal:
every valid positive E5 tuple has an enumerated right pair, a left pair
in the owning residue bucket and one canonical unordered pair-sum key.

All lists are mathematical multisets (repeated entries remain repeated).
This does not establish compilation correctness for Mojo's List or sort.
-/
namespace EulerPowers

/-- A right pair is emitted exactly at its owning key. -/
def indexedRight (m e : Nat) (k : Nat × Nat) (c d : Nat) : Prop :=
  (c, d) ∈ orderedPairs e ∧
    residueKey m (e ^ 5 - (c ^ 5 + d ^ 5)) (c ^ 5 + d ^ 5) = k

/-- Every primitive positive solution survives the right-pair enumeration,
residue-key routing, and left-bucket membership stages. -/
theorem valid_bucket_traversal (q : Quintuple) (h : Valid q) (m : Nat)
    (_hm : 0 < m) :
    indexedRight m q.e
      (residueKey m (q.a ^ 5 + q.b ^ 5) (q.c ^ 5 + q.d ^ 5))
      q.c q.d ∧
    (q.a, q.b) ∈
      residueBucket m ((q.a ^ 5 + q.b ^ 5) % m) (orderedPairs q.e) := by
  obtain ⟨ha, hab, hbc, hcd, hde⟩ := h.2.1
  have hc : 0 < q.c := by omega
  have hbLt : q.b < q.e := by omega
  have hcomplement :=
    ((pair_complement_iff q.a q.b q.c q.d q.e).mp h.1).2
  constructor
  · unfold indexedRight
    constructor
    · exact orderedPairs_complete hc hcd hde
    · rw [← hcomplement]
  · exact bucket_complete (orderedPairs_complete ha hab hbLt)

/-- The source-level routing key is compatible with the target equation. -/
theorem valid_traversal_compatible (q : Quintuple) (h : Valid q)
    {m : Nat} (hm : 0 < m) :
    compatibleKey m (q.e ^ 5)
      (residueKey m (q.a ^ 5 + q.b ^ 5) (q.c ^ 5 + q.d ^ 5)) :=
  valid_partition q h hm

/-- A visited record cannot be assigned to two different partition keys,
including equal-residue keys and noninjective fifth-power moduli. -/
theorem indexedRight_unique {m e c d : Nat} {k l : Nat × Nat}
    (hk : indexedRight m e k c d) (hl : indexedRight m e l c d) : k = l :=
  hk.2.symm.trans hl.2

/-- Filtering a bucket does not discard duplicate exact pair records.
This remains true when distinct pairs have the same sum. -/
theorem traversal_preserves_multiplicity (m : Nat) (p : Nat × Nat)
    (pairs : List (Nat × Nat)) :
    (residueBucket m ((p.1 ^ 5 + p.2 ^ 5) % m) pairs).count p =
      pairs.count p :=
  bucket_multiplicity m p pairs

end EulerPowers
