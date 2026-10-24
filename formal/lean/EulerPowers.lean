import Lean

/-!
# Euler's fifth-power equation: trusted arithmetic boundary

All arithmetic statements below are Lean 4 theorems over exact naturals.
The check function is a reflection of its *specified* predicate, not
proof that the externally implemented Mojo enumerator visits every case.
-/

namespace EulerPowers

structure Quintuple where
  a : Nat
  b : Nat
  c : Nat
  d : Nat
  e : Nat
  deriving Repr, DecidableEq

def Identity (t : Quintuple) : Prop :=
  t.a ^ 5 + t.b ^ 5 + t.c ^ 5 + t.d ^ 5 = t.e ^ 5

def OrderedPositive (t : Quintuple) : Prop :=
  0 < t.a ∧ t.a ≤ t.b ∧ t.b ≤ t.c ∧ t.c ≤ t.d ∧ t.d < t.e

def Primitive (t : Quintuple) : Prop :=
  Nat.gcd t.a (Nat.gcd t.b (Nat.gcd t.c (Nat.gcd t.d t.e))) = 1

def Valid (t : Quintuple) : Prop :=
  Identity t ∧ OrderedPositive t ∧ Primitive t

instance (t : Quintuple) : Decidable (Valid t) := by
  unfold Valid Identity OrderedPositive Primitive
  infer_instance

def check (t : Quintuple) : Bool := decide (Valid t)

/-- Exact certificate acceptance is sound for the Lean predicate. -/
theorem check_sound (t : Quintuple) (h : check t = true) : Valid t := by
  simp only [check, decide_eq_true_eq] at h
  exact h

/-- The checker accepts every tuple satisfying the Lean specification. -/
theorem check_complete (t : Quintuple) (h : Valid t) : check t = true := by
  simpa only [check, decide_eq_true_eq] using h

/-- Subtracting two fifth powers is safe only after proving nonnegativity. -/
theorem pair_complement_iff (a b c d e : Nat) :
    a ^ 5 + b ^ 5 + c ^ 5 + d ^ 5 = e ^ 5 ↔
    c ^ 5 + d ^ 5 ≤ e ^ 5 ∧
      a ^ 5 + b ^ 5 = e ^ 5 - (c ^ 5 + d ^ 5) := by
  omega

/-- Every finite height interval splits at a successor boundary. -/
theorem partition_cover {lo split hi e : Nat}
    (hlo : lo ≤ e) (hhi : e ≤ hi) (hs : lo ≤ split) (ht : split < hi) :
    (lo ≤ e ∧ e ≤ split) ∨ (split + 1 ≤ e ∧ e ≤ hi) := by
  omega

/-- Adjacent closed height intervals have no shared target height. -/
theorem partition_disjoint {lo split hi e : Nat} :
    ¬ ((lo ≤ e ∧ e ≤ split) ∧ (split + 1 ≤ e ∧ e ≤ hi)) := by
  omega

/-- Every height in [2,144] belongs to a prescribed shard. -/
theorem shards_cover {e : Nat} (hl : 2 ≤ e) (hh : e ≤ 144) :
    (2 ≤ e ∧ e ≤ 72) ∨ (73 ≤ e ∧ e ≤ 144) := by
  omega

/-- The two closed height shards cannot duplicate a candidate height. -/
theorem shards_disjoint {e : Nat} :
    ¬ ((2 ≤ e ∧ e ≤ 72) ∧ (73 ≤ e ∧ e ≤ 144)) := by
  omega

def landerParkin : Quintuple := ⟨27, 84, 110, 133, 144⟩

/-- A reproducible, kernel-checked calculation with exact fifth powers. -/
theorem landerParkin_valid : Valid landerParkin := by decide

theorem landerParkin_check : check landerParkin = true := by
  exact check_complete _ landerParkin_valid

/-- A one-digit mutation must not be silently accepted. -/
theorem corrupt_target_rejected :
    check ⟨27, 84, 110, 133, 145⟩ = false := by decide

/-- A nonprimitive scaling is not admitted, even when the identity holds. -/
theorem scaled_example_rejected :
    check ⟨54, 168, 220, 266, 288⟩ = false := by decide

end EulerPowers
