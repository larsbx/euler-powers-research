"""Finite signed two-gap search. All powers and inversions use exact BigZ.

For each b and both orientations, invert the strictly increasing positive
function F(r,h)=(r+h)^5-r^5 on the full declared geometric interval.
No restriction abs(a)<=b; every admitted witness instead has u>b.
"""
from std.sys import argv
from finite_exact.bigint_z import BigZ, bigz_from_i64, bigz_sub, bigz_lt, bigz_eq
from finite_polynomial.polynomial_fp import Modulus
from euler_exact import fifth_bigz, primitive5
from verify_known import decimal_base


def difference(r: Int, h: Int) -> BigZ:
    return bigz_sub(fifth_bigz(Int64(r+h)), fifth_bigz(Int64(r)))


def search(e: Int, delta: Int, h: Int, b_lo: Int, b_hi: Int) raises:
    if (e < 5 or e > 4000000 or delta < 1 or delta >= e or
        delta > 65536 or h < 1 or h >= e or h > 65536 or
        b_lo < 1 or b_lo > b_hi or b_hi >= e or b_hi-b_lo >= 65536):
        raise Error("two-gap finite resource scope exceeded")
    var d = e-delta
    var residual = bigz_sub(fifth_bigz(Int64(e)), fifth_bigz(Int64(d)))
    var ring = Modulus(99000)
    var ring41 = Modulus(41)
    var ring61 = Modulus(61)
    var image = List[Bool](length=99000, fill=False)
    var image41 = List[Bool](length=41, fill=False)
    var image61 = List[Bool](length=61, fill=False)
    for r in range(99000):
        image[(ring.pow(r+h,5)+99000-ring.pow(r,5))%99000] = True
    for r in range(41):
        image41[(ring41.pow(r+h,5)+41-ring41.pow(r,5))%41] = True
    for r in range(61):
        image61[(ring61.pow(r+h,5)+61-ring61.pow(r,5))%61] = True
    var rem0 = ring.reduce_bigz(residual)
    var rem41 = ring41.reduce_bigz(residual)
    var rem61 = ring61.reduce_bigz(residual)
    var trials = 0
    var geometry = 0
    var reject0 = 0
    var reject41 = 0
    var reject61 = 0
    var nonpositive = 0
    var roots = 0
    var hits = 0
    var primitives = 0
    print("DOMAIN E5-TWO-GAP-v1", e, delta, h, b_lo, b_hi)
    for orientation in range(2):
        for b in range(b_lo,b_hi+1):
            trials += 1
            # orientation 0: u=r,c=r+h; orientation 1: c=r,u=r+h.
            var lo = b+1
            var hi = d-h
            if orientation == 1:
                lo = b
                hi = min(d,e-1-h)
            if lo > hi:
                geometry += 1
                continue
            var q0 = (rem0+99000-ring.pow(b,5))%99000
            var q41 = (rem41+41-ring41.pow(b,5))%41
            var q61 = (rem61+61-ring61.pow(b,5))%61
            if orientation == 1:
                q0 = (99000-q0)%99000
                q41 = (41-q41)%41
                q61 = (61-q61)%61
            if not image[q0]:
                reject0 += 1
                continue
            if not image41[q41]:
                reject41 += 1
                continue
            if not image61[q61]:
                reject61 += 1
                continue
            var target = bigz_sub(residual,fifth_bigz(Int64(b)))
            if orientation == 1:
                target = bigz_sub(fifth_bigz(Int64(b)),residual)
            if not bigz_lt(bigz_from_i64(0),target):
                nonpositive += 1
                continue
            roots += 1
            var upper = hi+1
            # Least r with F(r,h)>=target, or original hi+1.
            while lo < upper:
                var mid = lo+(upper-lo)//2
                if bigz_lt(difference(mid,h),target):
                    lo = mid+1
                else:
                    upper = mid
            if lo <= hi and bigz_eq(difference(lo,h),target):
                hits += 1
                var c = lo+h
                var u = lo
                if orientation == 1:
                    c = lo
                    u = lo+h
                # Never let inversion or residues substitute for identity.
                if not bigz_eq(bigz_sub(bigz_sub(bigz_sub(
                    fifth_bigz(Int64(e)),fifth_bigz(Int64(d))),
                    fifth_bigz(Int64(b))),fifth_bigz(Int64(c))),
                    bigz_sub(bigz_from_i64(0),fifth_bigz(Int64(u)))):
                    raise Error("two-gap final identity mismatch")
                var primitive = primitive5(Int64(u),Int64(b),Int64(c),Int64(d),Int64(e))
                if primitive:
                    primitives += 1
                print("HIT", orientation, b, lo, u, c, d, e, Int(primitive))
    print("SUMMARY",trials,geometry,reject0,reject41,reject61,nonpositive,roots,hits,primitives)


def main() raises:
    var args = argv()
    if len(args) != 6:
        raise Error("usage: two_gap E DELTA H B_LO B_HI")
    search(Int(decimal_base(args[1])),Int(decimal_base(args[2])),
           Int(decimal_base(args[3])),Int(decimal_base(args[4])),Int(decimal_base(args[5])))
