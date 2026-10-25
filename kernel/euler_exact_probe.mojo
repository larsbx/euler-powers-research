"""Executable contract probes for the shared Euler exact-arithmetic bridge.

These test only arithmetic, never search completeness or theorem acceptance.
"""
from euler_exact import fifth_int, pair_sum, complement, checked_pack_pair, primitive5, fifth_bigz
from finite_exact.exact_decimal import bigz_decimal


def main() raises:
    for x in [-6208, -1000, -144, -2, -1, 0, 1, 2, 144, 1000, 6208]:
        print("FIFTH", x, fifth_int(x))
    for x in [-1000000000, -6209, 6209, 1000000000]:
        print("BIGZ", x, bigz_decimal(fifth_bigz(Int64(x))))
    print("SUM", pair_sum(Int64(123), Int64(456)))
    print("COMPLEMENT", complement(Int64(100), Int64(20), Int64(30)))
    print("PACK", checked_pack_pair(Int64(5), 1, 4, 145))
    print("PACK", checked_pack_pair(Int64(5), 2, 3, 145))
    if not primitive5(27, 84, 110, 133, 144):
        raise Error("valid primitive witness rejected")
    if primitive5(54, 168, 220, 266, 288):
        raise Error("scaled tuple incorrectly primitive")
    print("PRIMITIVE ACCEPT")
    print("NONPRIMITIVE REJECT")
    for x in [-6209, 6209]:
        var refused = False
        try:
            var result = fifth_int(x)
        except:
            refused = True
        if not refused:
            raise Error("Int64 fifth-power overflow was not refused")
        print("REFUSED FIFTH", x)

    var pair_refused = False
    try:
        var impossible_sum = pair_sum(Int64.MAX, Int64(1))
    except:
        pair_refused = True
    if not pair_refused:
        raise Error("Int64 addition overflow accepted")
    print("REFUSED PAIR")

    var complement_refused = False
    try:
        var impossible_complement = complement(Int64.MIN, Int64(1), Int64(0))
    except:
        complement_refused = True
    if not complement_refused:
        raise Error("Int64 complement underflow accepted")
    print("REFUSED COMPLEMENT")

    var packed_refused = False
    try:
        var impossible_packed = checked_pack_pair(Int64.MAX, 1, 1, 145)
    except:
        packed_refused = True
    if not packed_refused:
        raise Error("packed overflow accepted")
    print("REFUSED PACK")

    var digit_refused = False
    try:
        var invalid_digit = checked_pack_pair(Int64(5), 145, 0, 145)
    except:
        digit_refused = True
    if not digit_refused:
        raise Error("noncanonical packed digit accepted")
    print("REFUSED DIGIT")
