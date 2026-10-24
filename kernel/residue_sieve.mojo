"""Exact fifth-power residue census over finite rings.

The program computes residue sets and complete 5-term modular feasibility
for base classes modulo m (four plus terms, one negative target term).
Index z records how many of the five bases are divisible by the specified
prime p. No statistical or independence assumptions are made.
"""
def fifth_mod(x: Int, modulus: Int) -> Int:
    var v = 1
    for _ in range(5):
        v = (v * x) % modulus
    return v


def profile(modulus: Int, prime: Int) raises -> String:
    if modulus < 2 or modulus > 1000 or prime < 2 or modulus % prime != 0:
        raise Error("unsupported modulus/prime")
    var residues = List[Bool](length=modulus, fill=False)
    for x in range(modulus):
        residues[fifth_mod(x, modulus)] = True
    var distinct = 0
    for possible in residues:
        if possible:
            distinct += 1

    # DP state (zero_count, residue) after the first k signed entries.
    # States are Boolean, not probabilities.
    var states = List[Bool](length=6 * modulus, fill=False)
    states[0] = True
    for slot in range(5):
        var next_states = List[Bool](length=6 * modulus, fill=False)
        for zeros in range(slot + 1):
            for remainder in range(modulus):
                if not states[zeros * modulus + remainder]:
                    continue
                for x in range(modulus):
                    var power = fifth_mod(x, modulus)
                    var delta = power
                    if slot == 4:
                        delta = (modulus - power) % modulus
                    var next_zeros = zeros
                    if x % prime == 0:
                        next_zeros += 1
                    var next_rem = (remainder + delta) % modulus
                    next_states[next_zeros * modulus + next_rem] = True
        states = next_states^
    var mask = 0
    for z in range(6):
        if states[z * modulus]:
            mask |= 1 << z
    # Mask includes all-divisible tuples, which are nonprimitive.
    if (modulus == 11 or modulus == 25) and mask != 42:
        raise Error("proved divisibility restriction not reproduced")
    return String(modulus) + " " + String(distinct) + " " + String(mask)


def main() raises:
    for row in [(7, 7), (11, 11), (25, 5), (31, 31)]:
        print("MOD", profile(row[0], row[1]))
