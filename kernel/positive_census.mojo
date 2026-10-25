"""Complete bounded positive primitive E5 census (not an unbounded theorem).

Enumerates every e <= bound, and every ordered a<=b<=c<=d<e by
meeting in the middle: sort all a^5+b^5 for 1<=a<=b<e, then for
each c<=d<e binary-search e^5-c^5-d^5. A hit is reconstructed with
a<=b<=c; no modulus-based pruning or floating-point approximations.
The input guard <=1000 proves all cached fifth powers and two-term sums
fit Int64: 2*1000^5 = 2*10^15 < 2^63.
"""
from std.sys import argv
from certified_records.codec import parse_canonical
from euler_exact import checked_fifth_int, pair_sum, complement, primitive5
from pair_index import contains_sorted



# Compatibility facade retained for previously recorded P2 benchmark source.
# Both wrappers delegate to the same checked shared-kernel adapter.
def fifth_int(x: Int) raises -> Int64:
    return checked_fifth_int(x)


def primitive(a: Int, b: Int, c: Int, d: Int, e: Int) raises -> Bool:
    return primitive5(Int64(a), Int64(b), Int64(c), Int64(d), Int64(e))

def census(start_e: Int, bound: Int, sharded: Bool = False) raises:
    if start_e < 2 or start_e > bound or bound > 1000:
        raise Error("bound must lie between 2 and 1000")
    var powers = List[Int64]()
    for i in range(bound + 1):
        powers.append(fifth_int(i))
    var matches = 0
    for e in range(start_e, bound + 1):
        var pair_sums = List[Int64]()
        for a in range(1, e):
            for b in range(a, e):
                pair_sums.append(pair_sum(powers[a], powers[b]))
        sort(pair_sums)
        for c in range(1, e):
            for d in range(c, e):
                # Since a,b are positive, only strictly positive target sums.
                var target = complement(powers[e], powers[c], powers[d])
                if target <= 0 or not contains_sorted(pair_sums, target):
                    continue
                # A pair sum might have multiple representations: enumerate
                # all admissible pairs so no collision or ordering is lost.
                for a in range(1, c + 1):
                    for b in range(a, c + 1):
                        if pair_sum(powers[a], powers[b]) == target and primitive5(
                            Int64(a), Int64(b), Int64(c), Int64(d), Int64(e)
                        ):
                            print("CERT E5v1", a, b, c, d, e)
                            matches += 1
    if sharded:
        print("CENSUS", start_e, bound, matches)
    else:
        print("CENSUS", bound, matches)


def main() raises:
    var args = List[String]()
    for arg in argv():
        args.append(String(arg))
    if len(args) != 2 and len(args) != 3:
        raise Error("usage: positive_census <max_e> OR <start_e> <max_e>")
    var requested = parse_canonical(args[len(args) - 1], 32)
    if not requested:
        raise Error("invalid canonical maximum height")
    if len(args) == 3:
        var start = parse_canonical(args[1], 32)
        if not start:
            raise Error("invalid canonical starting height")
        census(Int(start.value()), Int(requested.value()), True)
    else:
        census(2, Int(requested.value()))
