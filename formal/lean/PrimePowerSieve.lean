import PairTraversal

/-!
Exact residue prefilters for positive E5, over arbitrary nonzero natural moduli.
A finite prime-power ring census provides necessary conditions only; it cannot
prove a bounded search complete without the independent candidate traversal.
-/

namespace EulerPowers

/-- The complete finite image of fifth powers mod m, with duplicates allowed. -/
def finiteFifthResidues (m : Nat) : List Nat :=
  (List.range m).map fun r => r ^ 5 % m

/-- Every integer fifth-power residue appears in the enumerated finite image.
No primality or injectivity hypothesis is needed. -/
theorem finiteFifthResidues_complete (m x : Nat) (hm : 0 < m) :
    x ^ 5 % m ∈ finiteFifthResidues m := by
  unfold finiteFifthResidues
  apply List.mem_map.mpr
  refine ⟨x % m, List.mem_range.mpr (Nat.mod_lt _ hm), ?_⟩
  exact (Nat.pow_mod x 5 m).symm

/-- The exact pair-sum residue image at height e.
It enumerates all positive a<=b<e without dropping collisions. -/
def finiteLeftPairResidues (m e : Nat) : List Nat :=
  (orderedPairs e).map fun p => (p.1 ^ 5 + p.2 ^ 5) % m

/-- Every valid positive E5 witness passes the mathematical modular
left-pair prefilter, for any modulus m. This also covers prime powers. -/
theorem valid_left_pair_residue (t : Quintuple) (h : Valid t) (m : Nat) :
    (t.e ^ 5 - (t.c ^ 5 + t.d ^ 5)) % m ∈
      finiteLeftPairResidues m t.e := by
  obtain ⟨ha, hab, hbc, hcd, hde⟩ := h.2.1
  have hb : t.b < t.e := by omega
  have hcomp := ((pair_complement_iff t.a t.b t.c t.d t.e).mp h.1).2
  rw [← hcomp]
  unfold finiteLeftPairResidues
  apply List.mem_map.mpr
  exact ⟨(t.a, t.b), orderedPairs_complete ha hab hb, rfl⟩

/-- A rejection by either modulus cannot be a positive primitive solution.
No assumption of probabilistic independence or CRT sampling is made. -/
theorem valid_two_modular_filters (t : Quintuple) (h : Valid t)
    (m n : Nat) :
    (t.e ^ 5 - (t.c ^ 5 + t.d ^ 5)) % m ∈
        finiteLeftPairResidues m t.e ∧
    (t.e ^ 5 - (t.c ^ 5 + t.d ^ 5)) % n ∈
        finiteLeftPairResidues n t.e := by
  exact ⟨valid_left_pair_residue t h m,
    valid_left_pair_residue t h n⟩

/-- Finite-ring reduction of the fifth-power identity is universal over
any modulus, prime, prime power, or composite. -/
theorem valid_fifth_modulus (t : Quintuple) (h : Valid t) (m : Nat) :
    (t.a ^ 5 % m + t.b ^ 5 % m +
      t.c ^ 5 % m + t.d ^ 5 % m) % m = t.e ^ 5 % m := by
  have hmod := congrArg (fun x : Nat => x % m) h.1
  simpa only [Nat.add_mod, Nat.mod_mod] using hmod

end EulerPowers
