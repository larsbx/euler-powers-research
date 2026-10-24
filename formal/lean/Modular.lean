import EulerPowers

/-!
Certified elementary modular obstructions for Euler's fifth-power equation.
No numeric approximation and no enumeration over all integer quintuplets.
The only finite computations have 11 or 25 residue cases; proofs are
checked by the Lean kernel rather than accepted from Mojo output.
-/

namespace EulerPowers

def zeroCount (a b c d e p : Nat) : Nat :=
  (if a % p = 0 then 1 else 0) +
  (if b % p = 0 then 1 else 0) +
  (if c % p = 0 then 1 else 0) +
  (if d % p = 0 then 1 else 0) +
  (if e % p = 0 then 1 else 0)

def zeroResidues (a b c d e : Nat) : Nat :=
  (if a = 0 then 1 else 0) +
  (if b = 0 then 1 else 0) +
  (if c = 0 then 1 else 0) +
  (if d = 0 then 1 else 0) +
  (if e = 0 then 1 else 0)

theorem fifth_residue_11 (x : Nat) :
    x ^ 5 % 11 = 0 ∨ x ^ 5 % 11 = 1 ∨ x ^ 5 % 11 = 10 := by
  have h : ∀ r : Fin 11,
      (r.val ^ 5 % 11 = 0 ∨ r.val ^ 5 % 11 = 1 ∨
       r.val ^ 5 % 11 = 10) := by decide
  have hr := h ⟨x % 11, Nat.mod_lt _ (by decide)⟩
  simpa only [Nat.pow_mod] using hr

theorem fifth_residue_25 (x : Nat) :
    x ^ 5 % 25 = 0 ∨ x ^ 5 % 25 = 1 ∨
    x ^ 5 % 25 = 7 ∨ x ^ 5 % 25 = 18 ∨
    x ^ 5 % 25 = 24 := by
  have h : ∀ r : Fin 25,
      (r.val ^ 5 % 25 = 0 ∨ r.val ^ 5 % 25 = 1 ∨
       r.val ^ 5 % 25 = 7 ∨ r.val ^ 5 % 25 = 18 ∨
       r.val ^ 5 % 25 = 24) := by decide
  have hr := h ⟨x % 25, Nat.mod_lt _ (by decide)⟩
  simpa only [Nat.pow_mod] using hr

theorem fifth_zero_11 (x : Nat) :
    (x ^ 5 % 11 = 0) ↔ (x % 11 = 0) := by
  have h : ∀ r : Fin 11,
      ((r.val ^ 5 % 11 = 0) ↔ (r.val = 0)) := by decide
  have hr := h ⟨x % 11, Nat.mod_lt _ (by decide)⟩
  simpa only [Nat.pow_mod] using hr

theorem fifth_zero_25 (x : Nat) :
    (x ^ 5 % 25 = 0) ↔ (x % 5 = 0) := by
  have h : ∀ r : Fin 25,
      ((r.val ^ 5 % 25 = 0) ↔ (r.val % 5 = 0)) := by decide
  have hr := h ⟨x % 25, Nat.mod_lt _ (by decide)⟩
  have hm : (x % 25) % 5 = x % 5 := by omega
  simpa only [Nat.pow_mod, hm] using hr

private theorem residues11_parity (a b c d e : Nat)
    (ha : a = 0 ∨ a = 1 ∨ a = 10)
    (hb : b = 0 ∨ b = 1 ∨ b = 10)
    (hc : c = 0 ∨ c = 1 ∨ c = 10)
    (hd : d = 0 ∨ d = 1 ∨ d = 10)
    (he : e = 0 ∨ e = 1 ∨ e = 10)
    (hsum : (a + b + c + d) % 11 = e) :
    zeroResidues a b c d e = 1 ∨
    zeroResidues a b c d e = 3 ∨
    zeroResidues a b c d e = 5 := by
  unfold zeroResidues
  omega

private theorem residues25_parity (a b c d e : Nat)
    (ha : a = 0 ∨ a = 1 ∨ a = 7 ∨ a = 18 ∨ a = 24)
    (hb : b = 0 ∨ b = 1 ∨ b = 7 ∨ b = 18 ∨ b = 24)
    (hc : c = 0 ∨ c = 1 ∨ c = 7 ∨ c = 18 ∨ c = 24)
    (hd : d = 0 ∨ d = 1 ∨ d = 7 ∨ d = 18 ∨ d = 24)
    (he : e = 0 ∨ e = 1 ∨ e = 7 ∨ e = 18 ∨ e = 24)
    (hsum : (a + b + c + d) % 25 = e) :
    zeroResidues a b c d e = 1 ∨
    zeroResidues a b c d e = 3 ∨
    zeroResidues a b c d e = 5 := by
  unfold zeroResidues
  omega

private theorem sum_fifth_mod (a b c d e m : Nat)
    (h : a ^ 5 + b ^ 5 + c ^ 5 + d ^ 5 = e ^ 5) :
    (a ^ 5 % m + b ^ 5 % m + c ^ 5 % m + d ^ 5 % m) % m =
      e ^ 5 % m := by
  have hm := congrArg (fun n : Nat => n % m) h
  simpa only [Nat.add_mod, Nat.mod_mod] using hm

theorem fifth_11_zero_count (a b c d e : Nat)
    (h : a ^ 5 + b ^ 5 + c ^ 5 + d ^ 5 = e ^ 5) :
    zeroCount a b c d e 11 = 1 ∨
    zeroCount a b c d e 11 = 3 ∨
    zeroCount a b c d e 11 = 5 := by
  have hr := residues11_parity
    (a ^ 5 % 11) (b ^ 5 % 11) (c ^ 5 % 11)
    (d ^ 5 % 11) (e ^ 5 % 11)
    (fifth_residue_11 a) (fifth_residue_11 b)
    (fifth_residue_11 c) (fifth_residue_11 d)
    (fifth_residue_11 e) (sum_fifth_mod a b c d e 11 h)
  unfold zeroResidues at hr
  unfold zeroCount
  simp only [fifth_zero_11] at hr
  exact hr

theorem fifth_5_zero_count (a b c d e : Nat)
    (h : a ^ 5 + b ^ 5 + c ^ 5 + d ^ 5 = e ^ 5) :
    zeroCount a b c d e 5 = 1 ∨
    zeroCount a b c d e 5 = 3 ∨
    zeroCount a b c d e 5 = 5 := by
  have hr := residues25_parity
    (a ^ 5 % 25) (b ^ 5 % 25) (c ^ 5 % 25)
    (d ^ 5 % 25) (e ^ 5 % 25)
    (fifth_residue_25 a) (fifth_residue_25 b)
    (fifth_residue_25 c) (fifth_residue_25 d)
    (fifth_residue_25 e) (sum_fifth_mod a b c d e 25 h)
  unfold zeroResidues at hr
  unfold zeroCount
  simp only [fifth_zero_25] at hr
  exact hr

end EulerPowers
