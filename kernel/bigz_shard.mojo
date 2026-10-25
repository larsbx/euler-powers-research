"""Independent bounded BigZ E5 height shards with exact indexed sums.

CLI: mojo run -I kernel -I .deps/finite-math-kernels/kernel
     kernel/bigz_shard.mojo START_E END_E PARTITION_MODULUS

This does NOT replace the existing B<=256 packed search. It supplies
separately auditable exact shards, each bounded by <= 4 target heights
and e<=320; there is no claim of a complete 2..320 census without
separate shard coverage and independent replay.
"""
from std.sys import argv
from certified_records.codec import parse_canonical
from finite_exact.bigint_z import (
    BigZ, bigz_add, bigz_sub, bigz_lt, bigz_eq, bigz_from_i64
)
from finite_polynomial.polynomial_fp import Modulus
from finite_polynomial.pair_power_residue import PairPowerResiduePrefix
from euler_exact import fifth_bigz, primitive5
from bigz_pair_index import indexed_exact_pairs, matching_exact_pairs


def shard(start_e: Int, end_e: Int, modulus: Int) raises:
    if (start_e < 2 or end_e > 320 or start_e > end_e or
        end_e - start_e >= 4 or modulus < 1 or modulus > 35):
        raise Error("require 2<=start<=end<=320, width<=4, 1<=M<=35")
    # Modulus(1) is intentionally unsupported in the shared ring API;
    # exact ring arithmetic here uses the canonical >=2 implementation.
    # A separate B256 packed lane retains M=1 support.
    if modulus < 2:
        raise Error("BigZ shard requires partition modulus >=2")
    var owners = Modulus(modulus)
    var digits = Modulus(99000)
    var powers = List[BigZ]()
    for x in range(end_e + 1):
        powers.append(fifth_bigz(Int64(x)))
    var all_visits = 0
    var all_hits = 0
    print("DOMAIN E5BIGSHARDv1", start_e, end_e, modulus)
    for e in range(start_e, end_e + 1):
        var index = indexed_exact_pairs(powers, e)
        var digit_filter = PairPowerResiduePrefix(99000, 5)
        var visits = List[Int](length=modulus * modulus, fill=0)
        var hits = List[Int](length=modulus * modulus, fill=0)
        for c in range(1, e):
            _ = digit_filter.advance()
            for d in range(c, e):
                var right = bigz_add(powers[c], powers[d])
                var target = bigz_sub(powers[e], right)
                if target.sign <= 0:
                    continue
                var target_mod = owners.reduce_bigz(target)
                var right_mod = owners.reduce_bigz(right)
                var lo = min(target_mod, right_mod)
                var hi = max(target_mod, right_mod)
                var at = lo * modulus + hi
                visits[at] += 1
                all_visits += 1
                if not digit_filter.contains(digits.reduce_bigz(target)):
                    continue
                var matches = matching_exact_pairs(index, target, c)
                for p in matches:
                    if primitive5(Int64(p[0]), Int64(p[1]),
                                  Int64(c), Int64(d), Int64(e)):
                        # A fresh exact fifth-power identity check is cheap
                        # and keeps certificate authority outside the index.
                        var left = bigz_add(powers[p[0]], powers[p[1]])
                        if not bigz_eq(left, target):
                            raise Error("indexed witness failed exact identity")
                        print("CERT E5v1", p[0], p[1], c, d, e)
                        hits[at] += 1
                        all_hits += 1
        for lo in range(modulus):
            for hi in range(lo, modulus):
                if (lo + hi) % modulus != owners.reduce_bigz(powers[e]):
                    continue
                var at = lo * modulus + hi
                print("PART", e, lo, hi, visits[at], hits[at])
    print("SHARD", start_e, end_e, modulus, all_visits, all_hits)


def main() raises:
    var args = List[String]()
    for arg in argv():
        args.append(String(arg))
    if len(args) != 4:
        raise Error("usage: bigz_shard START_E END_E MODULUS")
    var a = parse_canonical(args[1], 32)
    var b = parse_canonical(args[2], 32)
    var m = parse_canonical(args[3], 32)
    if not a or not b or not m:
        raise Error("noncanonical shard argument")
    shard(Int(a.value()), Int(b.value()), Int(m.value()))
