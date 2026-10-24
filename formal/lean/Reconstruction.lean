import LowerBoundInvariant

/-!
# Exhaustive abstract E5 reconstruction

The candidate-reconstruction stage loops over c ≤ d < e and then over
a ≤ b ≤ c. Pair-index membership is only a prefilter; reconstruction
must enumerate *every* admissible pair representation, including pair
sum collisions. This module proves that the combined mathematical stages
accept precisely the valid positive primitive E5 tuples.

These are proofs about finite list specifications, not an independent
verification of the Mojo compiler or the concrete nested loops.
-/

namespace EulerPowers

theorem orderedPairs_necessary {a b e : Nat}
    (h : (a, b) ∈ orderedPairs e) :
    0 < a ∧ a ≤ b ∧ b < e := by
  have hf : (a, b) ∈ rawPairs e ∧
      decide (0 < a ∧ a ≤ b) = true := by
    exact List.mem_filter.mp (by simpa only [orderedPairs] using h)
  have hguard : 0 < a ∧ a ≤ b := by
    simpa only [decide_eq_true_eq] using hf.2
  have hraw := hf.1
  unfold rawPairs at hraw
  obtain ⟨x, hx, hmap⟩ := List.mem_flatMap.mp hraw
  obtain ⟨y, hy, hxy⟩ := List.mem_map.mp hmap
  have hby : y = b := congrArg Prod.snd hxy
  have hb : b < e := by
    rw [← hby]
    exact List.mem_range.mp hy
  exact ⟨hguard.1, hguard.2, hb⟩

/-- Only pairs with b ≤ c are eligible for the reconstruction stage. -/
def reconstructAB (e c : Nat) : List (Nat × Nat) :=
  (orderedPairs e).filter fun ab => decide (ab.2 ≤ c)

theorem reconstructAB_complete {a b c e : Nat}
    (ha : 0 < a) (hab : a ≤ b) (hbc : b ≤ c) (hce : c < e) :
    (a, b) ∈ reconstructAB e c := by
  unfold reconstructAB
  apply List.mem_filter.mpr
  constructor
  · exact orderedPairs_complete ha hab (by omega)
  · simpa [hbc]

theorem reconstructAB_necessary {a b c e : Nat}
    (h : (a, b) ∈ reconstructAB e c) :
    0 < a ∧ a ≤ b ∧ b ≤ c ∧ b < e := by
  have hf : (a, b) ∈ orderedPairs e ∧ decide (b ≤ c) = true := by
    exact List.mem_filter.mp (by simpa only [reconstructAB] using h)
  obtain ⟨ha, hab, hb⟩ := orderedPairs_necessary hf.1
  have hbc : b ≤ c := by
    simpa only [decide_eq_true_eq] using hf.2
  exact ⟨ha, hab, hbc, hb⟩

/-- Combined mathematical acceptance criterion for a candidate.
The sorted index is an early membership check; the exact reconstruction
test still checks the particular four summands and their GCD. -/
def StagedCandidate (t : Quintuple) : Prop :=
  (t.c, t.d) ∈ orderedPairs t.e ∧
  (t.a, t.b) ∈ reconstructAB t.e t.c ∧
  (sortedPairSums t.e).contains
      (t.e ^ 5 - (t.c ^ 5 + t.d ^ 5)) = true ∧
  t.c ^ 5 + t.d ^ 5 ≤ t.e ^ 5 ∧
  t.a ^ 5 + t.b ^ 5 = t.e ^ 5 - (t.c ^ 5 + t.d ^ 5) ∧
  Primitive t

/-- Soundness AND completeness of the abstract reconstruction stages
for arbitrary positive primitive quintuplets and arbitrary heights. -/
theorem stagedCandidate_iff_valid (t : Quintuple) :
    StagedCandidate t ↔ Valid t := by
  constructor
  · intro hs
    rcases hs with ⟨hcd, hab, _hindex, hnonneg, heq, hprim⟩
    obtain ⟨hc, hcdLe, hde⟩ := orderedPairs_necessary hcd
    obtain ⟨ha, habLe, hbc, _hb⟩ := reconstructAB_necessary hab
    have heqn : Identity t := by
      exact (pair_complement_iff t.a t.b t.c t.d t.e).mpr
        ⟨hnonneg, heq⟩
    have hord : OrderedPositive t := by
      exact ⟨ha, habLe, hbc, hcdLe, hde⟩
    exact ⟨heqn, hord, hprim⟩
  · intro hv
    obtain ⟨ha, hab, hbc, hcd, hde⟩ := hv.2.1
    have hc : 0 < t.c := by omega
    have hce : t.c < t.e := by omega
    have hcomplement :=
      (pair_complement_iff t.a t.b t.c t.d t.e).mp hv.1
    exact ⟨orderedPairs_complete hc hcd hde,
      reconstructAB_complete ha hab hbc hce,
      valid_sorted_hit t hv,
      hcomplement.1, hcomplement.2, hv.2.2⟩

end EulerPowers
