"""Native exact right-pair pruning counters from shared prefix-residue kernel.

This is a measurement probe, separate from canonical E5PARTv1 output.
It reports candidate visits, modular rejects and survivors, not speedup.
"""
from euler_exact import checked_fifth_int, complement
from finite_polynomial.pair_power_residue import PairPowerResiduePrefix


def scan(bound: Int, modulus: Int) raises:
    var powers = List[Int64]()
    for x in range(bound + 1):
        powers.append(checked_fifth_int(x))
    var prefix = PairPowerResiduePrefix(modulus, 5)
    var visits = 0
    var rejected = 0
    # One prefix per c makes the work and set membership independently
    # inspectable; the production search rebuilds this prefix per e.
    for c in range(1, bound):
        _ = prefix.advance()
        for e in range(c + 1, bound + 1):
            for d in range(c, e):
                var target = complement(powers[e], powers[c], powers[d])
                if target <= 0:
                    continue
                visits += 1
                if not prefix.contains(Int(target)):
                    rejected += 1
    print("SIEVE", bound, modulus, visits, rejected, visits - rejected)


def main() raises:
    for bound in [8, 48, 144]:
        for modulus in [9, 11, 25, 99, 2475]:
            scan(bound, modulus)
    var witness = PairPowerResiduePrefix(2475, 5)
    for _ in range(110):
        _ = witness.advance()
    var t = checked_fifth_int(144) - checked_fifth_int(110) - checked_fifth_int(133)
    if not witness.contains(Int(t)):
        raise Error("legitimate primitive witness filtered")
    print("WITNESS", Int(t % 2475))
