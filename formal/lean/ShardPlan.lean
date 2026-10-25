import EulerPowers

/-!
# Canonical coverage of closed height intervals

A plan is an ordered list of closed intervals with an exact first height,
successor-adjacent boundaries, and a final height. Every entry is checked
against the declared bound. The verifier is finite and executable, while
the theorem establishes what a passing verification means.
-/

namespace EulerPowers

def contiguousPlan (cursor bound : Nat) : List (Nat × Nat) → Bool
  | [] => decide (cursor = bound + 1)
  | (lo, hi) :: rest =>
      decide (cursor = lo ∧ lo ≤ hi ∧ hi ≤ bound) &&
        contiguousPlan (hi + 1) bound rest

def validPlan (bound : Nat) (intervals : List (Nat × Nat)) : Bool :=
  contiguousPlan 2 bound intervals

/-- If a finite plan passes verification, every height between its
starting cursor and the declared upper bound belongs to an interval. -/
theorem contiguousPlan_covers (cursor bound : Nat)
    (intervals : List (Nat × Nat))
    (hv : contiguousPlan cursor bound intervals = true)
    (e : Nat) (hstart : cursor ≤ e) (hend : e ≤ bound) :
    ∃ lo hi, (lo, hi) ∈ intervals ∧ lo ≤ e ∧ e ≤ hi := by
  induction intervals generalizing cursor with
  | nil =>
      have hendpoint : cursor = bound + 1 := by
        simpa only [contiguousPlan, decide_eq_true_eq] using hv
      omega
  | cons pair rest ih =>
      rcases pair with ⟨lo, hi⟩
      have hh : (cursor = lo ∧ lo ≤ hi ∧ hi ≤ bound) ∧
          contiguousPlan (hi + 1) bound rest = true := by
        simpa only [contiguousPlan, Bool.and_eq_true, decide_eq_true_eq] using hv
      rcases hh with ⟨⟨hcursor, hlohi, hhibound⟩, hrest⟩
      by_cases hthis : e ≤ hi
      · exact ⟨lo, hi, by simp, by omega, hthis⟩
      · obtain ⟨nextLo, nextHi, hmem, hnextLo, hnextHi⟩ :=
          ih (hi + 1) hrest (by omega)
        exact ⟨nextLo, nextHi, by simp [hmem], hnextLo, hnextHi⟩

/-- An accepted plan covers every requested height. Its definition also
checks every interval's upper bound, so extraneous intervals fail. -/
theorem validPlan_covers (bound : Nat) (intervals : List (Nat × Nat))
    (hv : validPlan bound intervals = true)
    (e : Nat) (hlo : 2 ≤ e) (hhi : e ≤ bound) :
    ∃ lo hi, (lo, hi) ∈ intervals ∧ lo ≤ e ∧ e ≤ hi := by
  exact contiguousPlan_covers 2 bound intervals hv e hlo hhi

theorem fixture_plan_accepted :
    validPlan 144 [(2, 72), (73, 144)] = true := by decide

theorem fixture_gap_rejected :
    validPlan 144 [(2, 72), (74, 144)] = false := by decide

theorem fixture_overlap_rejected :
    validPlan 144 [(2, 72), (72, 144)] = false := by decide

theorem fixture_missing_tail_rejected :
    validPlan 144 [(2, 72)] = false := by decide

theorem fixture_outside_rejected :
    validPlan 144 [(2, 72), (73, 145)] = false := by decide

end EulerPowers
