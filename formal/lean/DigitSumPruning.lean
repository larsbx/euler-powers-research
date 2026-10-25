import PrimePowerSieve

/-!
The production digit/CRT filter is a prefix sieve rather than the broad
all-pairs-at-height-e sieve from PrimePowerSieve. For a valid ordered
positive tuple, its left pair lies in the prefix through c. These proofs
are mathematical; native Mojo conformance is checked independently.
-/
namespace EulerPowers

/-- All left-pair sums whose bases are in the ordered prefix through c. -/
def finitePairPrefix (m c : Nat) : List Nat :=
  finiteLeftPairResidues m (c + 1)

/-- Stronger than membership in the full left-pair image at target e:
a<=b<=c forces complement membership in the exact prefix at c. -/
theorem valid_digit_prefix (t : Quintuple) (h : Valid t) (m : Nat) :
    (t.e ^ 5 - (t.c ^ 5 + t.d ^ 5)) % m ∈
      finitePairPrefix m t.c := by
  obtain ⟨ha, hab, hbc, hcd, hde⟩ := h.2.1
  have hb : t.b < t.c + 1 := by omega
  have hcomp := ((pair_complement_iff t.a t.b t.c t.d t.e).mp h.1).2
  rw [← hcomp]
  unfold finitePairPrefix finiteLeftPairResidues
  exact List.mem_map.mpr
    ⟨(t.a, t.b), orderedPairs_complete ha hab hb, rfl⟩

/-- An absent modular pair residue rejects *only* impossible solutions.
The modulus is arbitrary; 2475 need not be a field or prime power. -/
theorem missing_digit_prefix_rejects (t : Quintuple) (m : Nat)
    (absent :
      (t.e ^ 5 - (t.c ^ 5 + t.d ^ 5)) % m ∉
        finitePairPrefix m t.c) : ¬ Valid t := by
  intro valid
  exact absent (valid_digit_prefix t valid m)

end EulerPowers
