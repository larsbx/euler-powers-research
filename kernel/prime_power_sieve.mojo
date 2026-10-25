"""Exact prime-power fifth-power residue profiles over Z/p^k, not F_p.

Uses the pinned shared finite_polynomial.polynomial_fp.Modulus ring arithmetic
with canonical residues and overflow-refusing modulus intake. All profiles
are complete finite residue enumerations, not claims about integer solutions.
"""
from finite_polynomial.polynomial_fp import Modulus, prime_field
from finite_exact.integer_gcd import gcd_i64


def distinct_fifth_residues(modulus: Int) raises -> Int:
    var ring = Modulus(modulus)
    var seen = List[Bool](length=modulus, fill=False)
    var count = 0
    for x in range(modulus):
        var r = ring.pow(x, 5)
        if not seen[r]:
            seen[r] = True
            count += 1
    return count


def profile(modulus: Int, prime: Int) raises:
    if modulus < 2 or modulus > 625 or prime < 2:
        raise Error("profile outside 2 <= modulus <= 625")
    var field = prime_field(prime)
    if modulus % field.n != 0:
        raise Error("prime does not divide modulus")
    var quotient = modulus
    while quotient % prime == 0:
        quotient //= prime
    if quotient != 1:
        raise Error("modulus is not a power of the declared prime")
    var ring = Modulus(modulus)
    var values = List[Bool](length=modulus, fill=False)
    var choices_seen = List[Bool](length=2 * modulus, fill=False)
    var residues = List[Int]()
    var zero_flags = List[Int]()
    var distinct = 0
    for x in range(modulus):
        var r = ring.pow(x, 5)
        var divisible = 1 if x % prime == 0 else 0
        if not values[r]:
            values[r] = True
            distinct += 1
        if not choices_seen[2 * r + divisible]:
            choices_seen[2 * r + divisible] = True
            residues.append(r)
            zero_flags.append(divisible)
    # Boolean DP for four positive summand terms minus the fifth target.
    # The zero-count distinguishes how many of all five bases divide by p.
    var states = List[Bool](length=6 * modulus, fill=False)
    states[0] = True
    for slot in range(5):
        var next_states = List[Bool](length=6 * modulus, fill=False)
        for zeros in range(slot + 1):
            for remainder in range(modulus):
                if not states[zeros * modulus + remainder]:
                    continue
                for i in range(len(residues)):
                    var delta = residues[i]
                    if slot == 4:
                        delta = ring.sub(0, delta)
                    var next_rem = ring.add(remainder, delta)
                    var count = zeros + zero_flags[i]
                    next_states[count * modulus + next_rem] = True
        states = next_states^
    var mask = 0
    for count in range(6):
        if states[count * modulus]:
            mask |= 1 << count
    print("POWER", modulus, prime, distinct, len(residues), mask)


def crt_profile(a: Int, b: Int) raises:
    if a < 2 or b < 2 or a * b > 2500:
        raise Error("CRT profile outside bounded domain")
    if gcd_i64(Int64(a), Int64(b)) != 1:
        raise Error("CRT moduli must be coprime")
    var n = a * b
    var actual = distinct_fifth_residues(n)
    var predicted = distinct_fifth_residues(a) * distinct_fifth_residues(b)
    if actual != predicted:
        raise Error("coprime CRT fifth-power image mismatch")
    print("CRT", a, b, n, actual)


def main() raises:
    for row in [(5, 5), (25, 5), (125, 5), (625, 5),
                (11, 11), (121, 11), (31, 31), (61, 61)]:
        profile(row[0], row[1])
    for pair in [(25, 11), (125, 11), (25, 31)]:
        crt_profile(pair[0], pair[1])
