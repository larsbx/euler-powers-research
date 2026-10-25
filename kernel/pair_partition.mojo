"""Single-pass positive pair-sum residue traversal; 2 <= B <= 256.

Buckets contain every packed (sum,a,b) representation; exact-sum
range lookup returns all matching ordered representations.
PART rows count right-pair visits and primitive certificates per owning key.
Each right pair is visited once per height, NOT once per compatible key.
"""
from std.sys import argv
from certified_records.codec import parse_canonical
from pair_index import lower_bound
from euler_exact import checked_fifth_int, pair_sum, complement, checked_pack_pair, primitive5
from finite_polynomial.pair_power_residue import PairPowerResiduePrefix


def key(s: Int64, t: Int64, modulus: Int) -> Tuple[Int, Int]:
    var r = Int(s % Int64(modulus))
    var q = Int(t % Int64(modulus))
    return (min(r, q), max(r, q))


def build_buckets(powers: List[Int64], e: Int, modulus: Int) raises -> List[List[Int64]]:
    var buckets = List[List[Int64]]()
    for _ in range(modulus):
        buckets.append(List[Int64]())
    for a in range(1, e):
        for b in range(a, e):
            var s = pair_sum(powers[a], powers[b])
            buckets[Int(s % Int64(modulus))].append(s)
    for r in range(modulus):
        sort(buckets[r])
    return buckets^


def matching_pairs(powers: List[Int64], target: Int64, c: Int) raises -> List[Tuple[Int, Int]]:
    var pairs = List[Tuple[Int, Int]]()
    for a in range(1, c + 1):
        for b in range(a, c + 1):
            if pair_sum(powers[a], powers[b]) == target:
                pairs.append((a, b))
    return pairs^


# Base-stride encoding sorts records first by exact sum, then by (a,b).
# The P1–P5 stride 145 remains canonical for B<=144. For 145<=B<=256,
# stride 257 is larger than each digit and its checked Int64 encoding fits.
def pack_pair(value: Int64, a: Int, b: Int, stride: Int) raises -> Int64:
    return checked_pack_pair(value, a, b, stride)


def build_indexed_buckets(
    powers: List[Int64], e: Int, modulus: Int, stride: Int
) raises -> List[List[Int64]]:
    var buckets = List[List[Int64]]()
    for _ in range(modulus):
        buckets.append(List[Int64]())
    for a in range(1, e):
        for b in range(a, e):
            var value = pair_sum(powers[a], powers[b])
            buckets[Int(value % Int64(modulus))].append(
                pack_pair(value, a, b, stride)
            )
    for residue in range(modulus):
        sort(buckets[residue])
    return buckets^


def matching_indexed_pairs(
    packed_bucket: List[Int64], target: Int64, c: Int, stride: Int
) raises -> List[Tuple[Int, Int]]:
    var out = List[Tuple[Int, Int]]()
    var base = Int64(stride)
    var width = base * base
    var pos = lower_bound(packed_bucket, checked_pack_pair(target, 0, 0, stride), False)
    while pos < len(packed_bucket):
        var packed = packed_bucket[pos]
        if packed // width != target:
            break
        var pair_digits = packed % width
        var a = Int(pair_digits // base)
        var b = Int(pair_digits % base)
        if b <= c:
            out.append((a, b))
        pos += 1
    return out^


def partition(bound: Int, modulus: Int) raises:
    if bound < 2 or bound > 256 or modulus < 1 or modulus > 35:
        raise Error("require 2 <= bound <= 256 and 1 <= modulus <= 35")
    print("DOMAIN E5PARTv1", bound, modulus)
    var powers = List[Int64]()
    for i in range(bound + 1):
        powers.append(checked_fifth_int(i))
    # Keep the earlier verified packing byte-for-byte for B<=144.
    # The wider radix is proved separately in WidePackedIndex.lean.
    var stride = 145 if bound <= 144 else 257
    var total = 0
    for e in range(2, bound + 1):
        # One indexed left-pair multiset per height. The same pair may share
        # an exact sum with other representations; no sum is deduplicated.
        var buckets = build_indexed_buckets(powers, e, modulus, stride)
        var digit_filter = PairPowerResiduePrefix(99000, 5)
        # Flat arrays avoid allocating a sparse list per compatible key.
        # Only 0 <= lo <= hi < modulus are ever incremented.
        var visits = List[Int]()
        var hits = List[Int]()
        for _ in range(modulus * modulus):
            visits.append(0)
            hits.append(0)
        # Crucial P2 change: visit each right pair ONCE, route it to its
        # unique key, then query only the appropriate left residue bucket.
        # No rescanning of right pairs for every compatible key.
        for c in range(1, e):
            # Includes every 1 <= a <= b <= c; independent of partition M.
            _ = digit_filter.advance()
            for d in range(c, e):
                var right = pair_sum(powers[c], powers[d])
                var target = complement(powers[e], powers[c], powers[d])
                if target <= 0:
                    continue
                var owner = key(target, right, modulus)
                var offset = owner[0] * modulus + owner[1]
                visits[offset] += 1
                # Exact composite CRT residue membership (9*11*1000).
                # No valid a<=b<=c complement is ever rejected.
                # Keep ownership/visit counters BEFORE the prefilter:
                # legacy E5PARTv1 manifests remain byte-for-byte stable.
                if not digit_filter.contains(Int(target)):
                    continue
                # The lower bound positions at the first packed pair with
                # this exact sum; decode every representation until the sum
                # changes. No O(c^2) reconstruction scan remains.
                var pairs = matching_indexed_pairs(
                    buckets[Int(target % Int64(modulus))], target, c, stride
                )
                for p in pairs:
                    if primitive5(Int64(p[0]), Int64(p[1]), Int64(c), Int64(d), Int64(e)):
                        print("CERT E5v1", p[0], p[1], c, d, e)
                        hits[offset] += 1
                        total += 1
        # Canonical row order, including zero rows, matches the P1 format.
        # The row key is compatible by target+right=e^5 (mod modulus).
        for lo in range(modulus):
            for hi in range(lo, modulus):
                if (lo + hi) % modulus != Int(powers[e] % Int64(modulus)):
                    continue
                var offset = lo * modulus + hi
                print("PART", e, lo, hi, visits[offset], hits[offset])
    print("TOTAL", total)


def main() raises:
    var args = List[String]()
    for arg in argv():
        args.append(String(arg))
    if len(args) != 3:
        raise Error("usage: pair_partition <bound> <modulus>")
    var bound = parse_canonical(args[1], 32)
    var modulus = parse_canonical(args[2], 32)
    if not bound or not modulus:
        raise Error("invalid canonical argument")
    partition(Int(bound.value()), Int(modulus.value()))
