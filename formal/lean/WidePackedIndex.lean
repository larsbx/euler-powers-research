import PackedPairIndex

/-!
P6 extends the production search from height<=144 to height<=256
using radix 257 whenever bound>144. The older radix-145 proofs remain
the source-level contract for admitted B<=144 runs. These are pure
natural-number theorems, not compiler correctness claims.
-/
namespace EulerPowers

def widePackedPair (sum a b : Nat) : Nat :=
  (sum * 257 + a) * 257 + b

/-- A complete (sum,a,b) encoding has unique base-257 digits. -/
theorem widePackedPair_decode (sum a b : Nat)
    (ha : a < 257) (hb : b < 257) :
    widePackedPair sum a b / 66049 = sum ∧
    (widePackedPair sum a b / 257) % 257 = a ∧
    widePackedPair sum a b % 257 = b := by
  dsimp [widePackedPair]
  omega

/-- Equal encoded records imply exactly equal sum and pair indices. -/
theorem widePackedPair_injective
    {s t a b c d : Nat}
    (ha : a < 257) (hb : b < 257)
    (hc : c < 257) (hd : d < 257)
    (h : widePackedPair s a b = widePackedPair t c d) :
    s = t ∧ a = c ∧ b = d := by
  have left := widePackedPair_decode s a b ha hb
  have right := widePackedPair_decode t c d hc hd
  rw [h] at left
  omega

/-- Equal exact pair sums remain contiguous in the sorted encoded index. -/
theorem widePackedPair_interval
    (sum a b : Nat) (ha : a < 257) (hb : b < 257) :
    sum * 66049 ≤ widePackedPair sum a b ∧
    widePackedPair sum a b < (sum + 1) * 66049 := by
  dsimp [widePackedPair]
  omega

/-- Mathematical packed values at B<=256 fit signed 64-bit integers.
The production checked packer refuses overflows instead of wrapping. -/
theorem widePackedPair_int64_safe
    (sum a b : Nat)
    (hs : sum ≤ 2 * 256 ^ 5) (ha : a < 257) (hb : b < 257) :
    widePackedPair sum a b < 2 ^ 63 := by
  dsimp [widePackedPair]
  omega

end EulerPowers
