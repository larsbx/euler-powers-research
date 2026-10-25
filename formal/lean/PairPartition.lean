import PairIndex

/-! Pair-sum residues, not individual base residues. No injectivity assumption.
These are source-level list/filter theorems; Mojo refinement is tested separately. -/
namespace EulerPowers

def residueKey (m s t : Nat) : Nat × Nat :=
  (min (s % m) (t % m), max (s % m) (t % m))

def compatibleKey (m target : Nat) (k : Nat × Nat) : Prop :=
  k.1 < m ∧ k.1 ≤ k.2 ∧ k.2 < m ∧ (k.1 + k.2) % m = target % m

instance (m target : Nat) (k : Nat × Nat) : Decidable (compatibleKey m target k) := by
  unfold compatibleKey
  infer_instance

theorem residueKey_swap (m s t : Nat) : residueKey m s t = residueKey m t s := by
  simp [residueKey, Nat.min_comm, Nat.max_comm]

theorem residueKey_sum (m s t : Nat) :
    (residueKey m s t).1 + (residueKey m s t).2 = s % m + t % m := by
  unfold residueKey
  dsimp
  omega

/-- All exact pair sums have one compatible owner. -/
theorem partition_coverage {m s t target : Nat} (hm : 0 < m) (h : s + t = target) :
    compatibleKey m target (residueKey m s t) := by
  have hs := Nat.mod_lt s hm
  have ht := Nat.mod_lt t hm
  have heq : (s % m + t % m) % m = target % m := by
    rw [← Nat.add_mod, h]
  unfold compatibleKey
  rw [residueKey_sum]
  dsimp [residueKey]
  omega

/-- Ownership is an equality, so no pair of distinct keys can share a record. -/
theorem partition_nonoverlap {m s t : Nat} {k l : Nat × Nat}
    (hk : residueKey m s t = k) (hl : residueKey m s t = l) : k = l := by
  exact hk.symm.trans hl

theorem partition_unique {m s t target : Nat} (hm : 0 < m) (h : s + t = target) :
    ∃ k, (residueKey m s t = k ∧ compatibleKey m target k) ∧
      ∀ l, residueKey m s t = l → l = k := by
  refine ⟨residueKey m s t, ⟨rfl, partition_coverage hm h⟩, ?_⟩
  intro k hk
  exact hk.symm

/-- A list of pair-sum records, partitioned without deduplication. -/
def keyPartition (m : Nat) (k : Nat × Nat) (xs : List (Nat × Nat)) :=
  xs.filter fun p => decide (residueKey m p.1 p.2 = k)

theorem keyPartition_mem {m : Nat} {k p : Nat × Nat} {xs : List (Nat × Nat)} :
    p ∈ keyPartition m k xs ↔ p ∈ xs ∧ residueKey m p.1 p.2 = k := by
  simp [keyPartition]

theorem keyPartition_cover {m : Nat} {p : Nat × Nat} {xs : List (Nat × Nat)}
    (hp : p ∈ xs) : p ∈ keyPartition m (residueKey m p.1 p.2) xs := by
  exact keyPartition_mem.mpr ⟨hp, rfl⟩

theorem keyPartition_disjoint {m : Nat} {k l p : Nat × Nat} {xs : List (Nat × Nat)}
    (hk : p ∈ keyPartition m k xs) (hl : p ∈ keyPartition m l xs) : k = l := by
  exact partition_nonoverlap (keyPartition_mem.mp hk).2 (keyPartition_mem.mp hl).2

theorem keyPartition_multiplicity (m : Nat) (p : Nat × Nat) (xs : List (Nat × Nat)) :
    (keyPartition m (residueKey m p.1 p.2) xs).count p = xs.count p := by
  induction xs with
  | nil => simp [keyPartition]
  | cons x xs ih =>
    by_cases h : x = p
    · subst x
      simp [keyPartition] at ih ⊢
    · simp [keyPartition, List.filter_cons, h] at ih ⊢
      split <;> simp_all

/-- Filtering uses list records, so colliding sums retain every representation. -/
def residueBucket (m r : Nat) (xs : List (Nat × Nat)) : List (Nat × Nat) :=
  xs.filter fun p => decide ((p.1 ^ 5 + p.2 ^ 5) % m = r)

theorem bucket_complete {m : Nat} {p : Nat × Nat} {xs : List (Nat × Nat)}
    (hp : p ∈ xs) : p ∈ residueBucket m ((p.1 ^ 5 + p.2 ^ 5) % m) xs := by
  simp [residueBucket, hp]

/-- Even repeated identical records retain their full multiplicity. -/
theorem bucket_multiplicity (m : Nat) (p : Nat × Nat) (xs : List (Nat × Nat)) :
    (residueBucket m ((p.1 ^ 5 + p.2 ^ 5) % m) xs).count p = xs.count p := by
  induction xs with
  | nil => simp [residueBucket]
  | cons x xs ih =>
    by_cases h : x = p
    · subst x
      simp [residueBucket] at ih ⊢
    · simp [residueBucket, List.filter_cons, h] at ih ⊢
      split <;> simp_all

/-- Link the partition theorem to the existing positive E5 definition. -/
theorem valid_partition (q : Quintuple) (h : Valid q) {m : Nat} (hm : 0 < m) :
    compatibleKey m (q.e ^ 5)
      (residueKey m (q.a ^ 5 + q.b ^ 5) (q.c ^ 5 + q.d ^ 5)) := by
  apply partition_coverage hm
  have hi := h.1
  unfold Identity at hi
  omega

end EulerPowers
