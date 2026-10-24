import BinarySearch

/-!
# Lower-bound window invariant and finite progress

The actual Mojo binary search uses the half-open window [lo,hi). The
mathematical invariant is stronger than mere preservation of equality:
everything before lo is strictly below the target; everything starting
at hi is greater than or equal to the target. This handles duplicates.

These statements are true for arbitrary sorted lists. They prove each
branch of the search preserves the mathematical invariant, and that a
completed window yields the correct membership decision. They do not
yet prove that the compiled Mojo while-loop implements this transition.
-/

namespace EulerPowers

def LowerBoundInv (xs : List Nat) (target lo hi : Nat) : Prop :=
  lo ≤ hi ∧ hi ≤ xs.length ∧
  (∀ i (h : i < xs.length), i < lo → xs[i] < target) ∧
  (∀ i (h : i < xs.length), hi ≤ i → target ≤ xs[i])

theorem lowerBound_initial (xs : List Nat) (target : Nat) :
    LowerBoundInv xs target 0 xs.length := by
  constructor
  · omega
  constructor
  · omega
  constructor
  · intro i hi hlo
    omega
  · intro i hi hafter
    omega

/-- The midpoint is inside the window whenever there is an unexamined
position. In particular, the pivot never indexes outside the list. -/
theorem lowerBound_midpoint (lo hi : Nat) (h : lo < hi) :
    lo ≤ lo + (hi - lo) / 2 ∧
    lo + (hi - lo) / 2 < hi := by
  omega

theorem lowerBound_midpoint_inbounds (xs : List Nat) (target lo hi : Nat)
    (h : LowerBoundInv xs target lo hi) (hMore : lo < hi) :
    lo + (hi - lo) / 2 < xs.length := by
  have hm := lowerBound_midpoint lo hi hMore
  unfold LowerBoundInv at h
  omega

/-- A strict-less-than pivot advances the lower bound past the pivot.
All newly skipped values are strictly below the target. -/
theorem lowerBound_less_preserves (xs : List Nat) (target lo hi mid : Nat)
    (hSort : xs.Pairwise (· ≤ ·)) (h : LowerBoundInv xs target lo hi)
    (hlo : lo ≤ mid) (hhi : mid < hi)
    (hpivot : xs[mid]'(by
      have : hi ≤ xs.length := h.2.1
      omega) < target) :
    LowerBoundInv xs target (mid + 1) hi := by
  obtain ⟨hle, hlen, hleft, hright⟩ := h
  unfold LowerBoundInv
  refine ⟨by omega, hlen, ?_, hright⟩
  intro i hibefore hsmall
  by_cases hprev : i < lo
  · exact hleft i hibefore hprev
  · have him : i ≤ mid := by omega
    have hmid : mid < xs.length := by omega
    have horder : xs[i] ≤ xs[mid] := by
      rcases Nat.lt_or_eq_of_le him with hlt | heq
      · exact hSort.rel_getElem_of_lt hibefore hmid hlt
      · subst i
        exact Nat.le_refl _
    omega

/-- A pivot >= the target moves the upper bound left *without* advancing
past the pivot, so the first matching entry is not discarded. -/
theorem lowerBound_ge_preserves (xs : List Nat) (target lo hi mid : Nat)
    (hSort : xs.Pairwise (· ≤ ·)) (h : LowerBoundInv xs target lo hi)
    (hlo : lo ≤ mid) (hhi : mid < hi)
    (hpivot : target ≤ xs[mid]'(by
      have : hi ≤ xs.length := h.2.1
      omega)) :
    LowerBoundInv xs target lo mid := by
  obtain ⟨hle, hlen, hleft, hright⟩ := h
  unfold LowerBoundInv
  refine ⟨by omega, by omega, hleft, ?_⟩
  intro i hibound hafter
  by_cases hprev : hi ≤ i
  · exact hright i hibound hprev
  · have hmid : mid < xs.length := by omega
    have horder : xs[mid] ≤ xs[i] := by
      rcases Nat.lt_or_eq_of_le hafter with hlt | heq
      · exact hSort.rel_getElem_of_lt hmid hibound hlt
      · subst i
        exact Nat.le_refl _
    omega

/-- Both transitions strictly reduce the number of unchecked positions.
This is the termination measure of a well-formed lower-bound loop. -/
theorem lowerBound_less_progress (lo hi mid : Nat)
    (hlo : lo ≤ mid) (hhi : mid < hi) :
    hi - (mid + 1) < hi - lo := by omega

theorem lowerBound_ge_progress (lo hi mid : Nat)
    (hlo : lo ≤ mid) (hhi : mid < hi) :
    mid - lo < hi - lo := by omega

/-- With lo=hi, checking that location (if it exists) is equivalent to
searching the whole original list. No earlier or later match remains. -/
theorem lowerBound_done (xs : List Nat) (target at : Nat)
    (h : LowerBoundInv xs target at at) :
    (∃ hi : at < xs.length, xs[at] = target) ↔ target ∈ xs := by
  constructor
  · rintro ⟨hat, heq⟩
    rw [← heq]
    exact List.getElem_mem hat
  · intro hmem
    obtain ⟨i, hi, heq⟩ := List.mem_iff_getElem.mp hmem
    have hnolo : ¬ i < at := by
      intro hlt
      have hstrict := h.2.2.1 i hi hlt
      omega
    have hnohi : ¬ at < i := by
      intro hlt
      have hlarge := h.2.2.2 i hi (by omega)
      omega
    have heqi : i = at := by omega
    subst i
    exact ⟨hi, heq⟩

end EulerPowers
