"""Exact Z[X]/(1+X+X^2+X^3+X^4), using pinned arbitrary-size BigZ.

No complex approximations, divisions, root extraction or search pruning.
Canonical basis: 1,z,z^2,z^3. The coefficient list invariant is checked at
every public arithmetic boundary; malformed representations raise.
"""
from finite_exact.bigint_z import BigZ, bigz_from_i64, bigz_add, bigz_sub, bigz_mul


struct Cyclotomic5(Copyable):
    var coefficients: List[BigZ]

    def __init__(out self):
        self.coefficients = List[BigZ]()
        for _ in range(4):
            self.coefficients.append(bigz_from_i64(0))


def canonical(x: Cyclotomic5) raises:
    if len(x.coefficients) != 4:
        raise Error("cyclotomic representation requires four coefficients")


def from_i64(a: Int64, b: Int64 = 0, c: Int64 = 0, d: Int64 = 0) -> Cyclotomic5:
    var out = Cyclotomic5()
    out.coefficients[0] = bigz_from_i64(a)
    out.coefficients[1] = bigz_from_i64(b)
    out.coefficients[2] = bigz_from_i64(c)
    out.coefficients[3] = bigz_from_i64(d)
    return out^


def add(x: Cyclotomic5, y: Cyclotomic5) raises -> Cyclotomic5:
    canonical(x)
    canonical(y)
    var out = Cyclotomic5()
    for i in range(4):
        out.coefficients[i] = bigz_add(x.coefficients[i], y.coefficients[i])
    return out^


def sub(x: Cyclotomic5, y: Cyclotomic5) raises -> Cyclotomic5:
    canonical(x)
    canonical(y)
    var out = Cyclotomic5()
    for i in range(4):
        out.coefficients[i] = bigz_sub(x.coefficients[i], y.coefficients[i])
    return out^


def mul(x: Cyclotomic5, y: Cyclotomic5) raises -> Cyclotomic5:
    canonical(x)
    canonical(y)
    # First use z^5=1; then eliminate z^4=-(1+z+z^2+z^3).
    var cyclic = List[BigZ]()
    for _ in range(5):
        cyclic.append(bigz_from_i64(0))
    for i in range(4):
        for j in range(4):
            var k = (i+j) % 5
            cyclic[k] = bigz_add(cyclic[k], bigz_mul(x.coefficients[i], y.coefficients[j]))
    var out = Cyclotomic5()
    for i in range(4):
        out.coefficients[i] = bigz_sub(cyclic[i], cyclic[4])
    return out^


def conjugate(x: Cyclotomic5, k: Int) raises -> Cyclotomic5:
    canonical(x)
    if k < 1 or k > 4:
        raise Error("Galois exponent must lie in 1..4")
    var out = Cyclotomic5()
    for i in range(4):
        var exponent = (i*k) % 5
        if exponent == 4:
            for j in range(4):
                out.coefficients[j] = bigz_sub(out.coefficients[j], x.coefficients[i])
        else:
            out.coefficients[exponent] = bigz_add(out.coefficients[exponent], x.coefficients[i])
    return out^


def norm(x: Cyclotomic5) raises -> BigZ:
    canonical(x)
    var product = from_i64(1)
    for k in range(1, 5):
        product = mul(product, conjugate(x, k))
    for i in range(1, 4):
        if not product.coefficients[i].is_zero():
            raise Error("Galois norm did not descend to an integer")
    return product.coefficients[0].copy()
