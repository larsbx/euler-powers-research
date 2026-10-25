import PairTraversal

/-!
Exact mathematical contract of the fixed-radix Mojo (sum,a,b) index.
Radix 145 is strictly greater than every positive a,b<e<=144.
Sorting encoded naturals orders by exact sum, then a, then b.
Machine representation and compiler behaviour require separate testing.
-/
namespace EulerPowers

def packedPair (sum a b : Nat) : Nat :=
  (sum * 145 + a) * 145 + b

/-- Reversible pair representation: no collisions from equal fifth-power sums. -/
theorem packedPair_decode (sum a b : Nat)
    (ha : a < 145) (hb : b < 145) :
    packedPair sum a b / 21025 = sum ∧
    (packedPair sum a b / 145) % 145 = a ∧
    packedPair sum a b % 145 = b := by
  dsimp [packedPair]
  omega

/-- Equal packed records force equal sums AND equal pair coordinates. -/
theorem packedPair_injective
    {s t a b c d : Nat}
    (ha : a < 145) (hb : b < 145)
    (hc : c < 145) (hd : d < 145)
    (h : packedPair s a b = packedPair t c d) :
    s = t ∧ a = c ∧ b = d := by
  have left := packedPair_decode s a b ha hb
  have right := packedPair_decode t c d hc hd
  rw [h] at left
  omega

/-- Every packed pair with given exact sum belongs to one contiguous
half-open interval of size 145². The existing lower_bound contract
can therefore find the entire interval without omitting collisions. -/
theorem packedPair_interval
    (sum a b : Nat) (ha : a < 145) (hb : b < 145) :
    sum * 21025 ≤ packedPair sum a b ∧
    packedPair sum a b < (sum + 1) * 21025 := by
  dsimp [packedPair]
  omega

/-- Conservative Int64 bound for all positive pair sums at height<=144.
All intermediate nonnegative additions/products are no larger than the
final nonnegative packed value. -/
theorem packedPair_int64_safe
    (sum a b : Nat)
    (hs : sum ≤ 2 * 144 ^ 5) (ha : a < 145) (hb : b < 145) :
    packedPair sum a b < 2 ^ 63 := by
  dsimp [packedPair]
  omega

end EulerPowers
