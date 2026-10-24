import EulerPowers

/-!
# Exhaustive abstract pair-sum index

The mathematical candidate index enumerates all ordered pairs
1 ≤ a ≤ b < e using finite List.range, then maps each pair to a^5+b^5.
These theorems prove no admissible complement is absent from this
*abstract* list. They do not prove the Mojo sorted-array/binary-search
implementation refines these definitions.
-/

namespace EulerPowers

def rawPairs (e : Nat) : List (Nat × Nat) :=
  (List.range e).flatMap fun a =>
    (List.range e).map fun b => (a, b)

def orderedPairs (e : Nat) : List (Nat × Nat) :=
  (rawPairs e).filter fun pair => decide (0 < pair.1 ∧ pair.1 ≤ pair.2)

def pairSums (e : Nat) : List Nat :=
  (orderedPairs e).map fun pair => pair.1 ^ 5 + pair.2 ^ 5

theorem rawPairs_complete {a b e : Nat} (ha : a < e) (hb : b < e) :
    (a, b) ∈ rawPairs e := by
  unfold rawPairs
  apply List.mem_flatMap.mpr
  refine ⟨a, List.mem_range.mpr ha, ?_⟩
  apply List.mem_map.mpr
  exact ⟨b, List.mem_range.mpr hb, rfl⟩

theorem orderedPairs_complete {a b e : Nat}
    (ha : 0 < a) (hab : a ≤ b) (hb : b < e) :
    (a, b) ∈ orderedPairs e := by
  have hae : a < e := by omega
  unfold orderedPairs
  apply List.mem_filter.mpr
  constructor
  · exact rawPairs_complete hae hb
  · simp [ha, hab]

theorem pairSums_complete {a b e : Nat}
    (ha : 0 < a) (hab : a ≤ b) (hb : b < e) :
    a ^ 5 + b ^ 5 ∈ pairSums e := by
  unfold pairSums
  apply List.mem_map.mpr
  exact ⟨(a, b), orderedPairs_complete ha hab hb, rfl⟩

/-- Every valid fifth-power identity has its required two-summand
complement in the exhaustive mathematical pair-sum list. -/
theorem valid_pair_hit (t : Quintuple) (h : Valid t) :
    t.e ^ 5 - (t.c ^ 5 + t.d ^ 5) ∈ pairSums t.e := by
  obtain ⟨ha, hab, hbc, hcd, hde⟩ := h.2.1
  have hb : t.b < t.e := by omega
  have hcomplement :=
    ((pair_complement_iff t.a t.b t.c t.d t.e).mp h.1).2
  rw [← hcomplement]
  exact pairSums_complete ha hab hb

end EulerPowers
