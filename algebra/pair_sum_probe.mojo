"""One deterministic signed pair query, suitable for precompiled comparison."""
from std.sys import argv
from finite_exact.bigint_z import bigz_add, bigz_from_i64
from finite_exact.exact_decimal import bigz_decimal
from euler_exact import fifth_bigz
from verify_known import decimal_base
from pair_sum import reconstruct, scan, square_root_if_exact


def main() raises:
    var args = argv()
    if len(args) != 6:
        raise Error("usage: pair_sum_probe scan|reconstruct B seed_a seed_b offset")
    var bound = Int(decimal_base(args[2]))
    var a = decimal_base(args[3])
    var b = decimal_base(args[4])
    var offset = decimal_base(args[5])
    if offset < -3 or offset > 3:
        raise Error("offset outside finite comparison scope")
    var target = bigz_add(bigz_add(fifth_bigz(a), fifth_bigz(b)), bigz_from_i64(offset))
    print("DOMAIN E5-PAIR-SUM-v1", args[1], bound, bigz_decimal(target))
    if args[1] == "scan":
        scan(target, bound)
    elif args[1] == "reconstruct":
        reconstruct(target, bound)
    else:
        raise Error("unknown pair method")
