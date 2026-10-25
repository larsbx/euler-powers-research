import CertifiedLowerBound

/-!
# Total signed-integer lower-bound correctness

The native Mojo lookup operates on signed Int64, whereas the earlier Lean
correctness theorem was over natural-valued arrays. This module proves
the same lower-bound window invariant, safe narrowing, termination,
and exact membership over ALL finite ordered lists of mathematical Int.
It makes no claim about compiled machine semantics or sorting.
-/

namespace EulerPowers

def SignedLowerBoundInv (xs : List Int) (target : Int) (lo hi : Nat) : Prop :=
  lo ≤ hi ∧ hi ≤ xs.length ∧
  (∀ i (h : i < xs.length), i < lo → xs[i] < target) ∧
  (∀ i (h : i < xs.length), hi ≤ i → target ≤ xs[i])

theorem signedInitial (xs : List Int) (target : Int) :
    SignedLowerBoundInv xs target 0 xs.length := by
  constructor
  · omega
  constructor
  · omega
  constructor
  · intro i hi hlo
    omega
  · intro i hi hafter
    omega

theorem signedMidInbounds (xs : List Int) (target : Int) (lo hi : Nat)
    (h : SignedLowerBoundInv xs target lo hi) (hMore : lo < hi) :
    lo + (hi - lo) / 2 < xs.length := by
  have hm := lowerBound_midpoint lo hi hMore
  unfold SignedLowerBoundInv at h
  omega

/-- A strict-less-than pivot advances the lower bound past the pivot.
All newly skipped values are strictly below the target. -/
theorem signedLessPreserves (xs : List Int) (target : Int) (lo hi mid : Nat)
    (hSort : xs.Pairwise (· ≤ ·)) (h : SignedLowerBoundInv xs target lo hi)
    (hlo : lo ≤ mid) (hhi : mid < hi)
    (hpivot : xs[mid]'(by
      have : hi ≤ xs.length := h.2.1
      omega) < target) :
    SignedLowerBoundInv xs target (mid + 1) hi := by
  obtain ⟨hle, hlen, hleft, hright⟩ := h
  unfold SignedLowerBoundInv
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
        exact le_refl _
    omega

/-- A pivot >= the target moves the upper bound left *without* advancing
past the pivot, so the first matching entry is not discarded. -/
theorem signedGePreserves (xs : List Int) (target : Int) (lo hi mid : Nat)
    (hSort : xs.Pairwise (· ≤ ·)) (h : SignedLowerBoundInv xs target lo hi)
    (hlo : lo ≤ mid) (hhi : mid < hi)
    (hpivot : target ≤ xs[mid]'(by
      have : hi ≤ xs.length := h.2.1
      omega)) :
    SignedLowerBoundInv xs target lo mid := by
  obtain ⟨hle, hlen, hleft, hright⟩ := h
  unfold SignedLowerBoundInv
  refine ⟨by omega, by omega, hleft, ?_⟩
  intro i hibound hafter
  by_cases hprev : hi ≤ i
  · exact hright i hibound hprev
  · have hmid : mid < xs.length := by omega
    have horder : xs[mid] ≤ xs[i] := by
      rcases Nat.lt_or_eq_of_le hafter with hlt | heq
      · exact hSort.rel_getElem_of_lt hmid hibound hlt
      · subst i
        exact le_refl _
    omega

/-- At termination, the *first* candidate is correct for any sorted
list, including duplicates: values beyond the lower bound may equal
the target, but sortedness forces the lower-bound value to equal it too. -/
theorem signedDone (xs : List Int) (target : Int) (pos : Nat)
    (hSort : xs.Pairwise (· ≤ ·))
    (h : SignedLowerBoundInv xs target pos pos) :
    (∃ hi : pos < xs.length, xs[pos] = target) ↔ target ∈ xs := by
  constructor
  · rintro ⟨hat, heq⟩
    rw [← heq]
    exact List.getElem_mem hat
  · intro hmem
    obtain ⟨i, hi, heq⟩ := List.mem_iff_getElem.mp hmem
    have hnolo : ¬ i < pos := by
      intro hlt
      have hstrict := h.2.2.1 i hi hlt
      omega
    have hpos : pos < xs.length := by omega
    have horder : xs[pos] ≤ xs[i] := by
      rcases Nat.lt_or_eq_of_le (show pos ≤ i by omega) with hlt | heqi
      · exact hSort.rel_getElem_of_lt hpos hi hlt
      · subst i
        exact le_refl _
    have hlarge : target ≤ xs[pos] := h.2.2.2 pos hpos (by omega)
    exact ⟨hpos, by omega⟩


def signedLowerBound (xs : List Int) (target : Int) (lo hi : Nat)
    (hSort : xs.Pairwise (· ≤ ·))
    (hInv : SignedLowerBoundInv xs target lo hi) :
    {pos : Nat // SignedLowerBoundInv xs target pos pos} := by
  if hMore : lo < hi then
    let mid := lo + (hi - lo) / 2
    have hmidLo : lo ≤ mid := (lowerBound_midpoint lo hi hMore).1
    have hmidHi : mid < hi := (lowerBound_midpoint lo hi hMore).2
    have hIdx : mid < xs.length :=
      signedMidInbounds xs target lo hi hInv hMore
    if hPivot : xs[mid] < target then
      exact signedLowerBound xs target (mid + 1) hi hSort
        (signedLessPreserves xs target lo hi mid hSort hInv
          hmidLo hmidHi hPivot)
    else
      have hGe : target ≤ xs[mid] := by omega
      exact signedLowerBound xs target lo mid hSort
        (signedGePreserves xs target lo hi mid hSort hInv
          hmidLo hmidHi hGe)
  else
    have hEq : hi = lo := by
      have hlo := hInv.1
      omega
    subst hi
    exact ⟨lo, hInv⟩
termination_by hi - lo
decreasing_by
  all_goals omega

/-- A proof that the *entire* recursive search returns a valid
lower bound, not just that each iteration step is locally safe. -/
theorem signedLowerBound_correct (xs : List Int) (target : Int)
    (hSort : xs.Pairwise (· ≤ ·)) :
    (∃ h : (signedLowerBound xs target 0 xs.length hSort
        (signedInitial xs target)).1 < xs.length,
      xs[(signedLowerBound xs target 0 xs.length hSort
        (signedInitial xs target)).1] = target) ↔
      target ∈ xs := by
  let result := signedLowerBound xs target 0 xs.length hSort
    (signedInitial xs target)
  exact signedDone xs target result.1 hSort result.2


end EulerPowers
