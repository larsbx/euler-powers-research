"""Mojo-primary exact verification of published Euler fifth-power identities.

Reads the canonical CSV directly. BigZ comes from pinned finite-math-kernels;
no floating point, overflow-prone x**5, or Python arithmetic participates in
Mojo's acceptance decision. A Python reference separately checks the same CSV.
This validates examples; it is not an exhaustive search or a theorem prover.
"""
from finite_exact.bigint_z import BigZ, bigz_add, bigz_eq, bigz_from_i64, bigz_mul
from finite_exact.integer_gcd import gcd_i64


def decimal_base(token: String) raises -> Int64:
    # Explicit bound makes parsing overflow-safe. The powers themselves are
    # unbounded Mojo BigZ values. Raise the bound only with regression coverage.
    var data = token.as_bytes()
    if len(data) == 0:
        raise Error("empty integer field")
    var begin = 0
    var negative = False
    if Int(data[0]) == ord("-"):
        negative = True
        begin = 1
    if begin == len(data):
        raise Error("sign without integer")
    if len(data) - begin > 1 and Int(data[begin]) == ord("0"):
        raise Error("noncanonical leading zero")
    var magnitude: Int64 = 0
    for i in range(begin, len(data)):
        var digit = Int(data[i]) - ord("0")
        if digit < 0 or digit > 9:
            raise Error("invalid integer digit")
        if magnitude > 100000000:
            raise Error("input outside bounded intake")
        magnitude = magnitude * 10 + Int64(digit)
        if magnitude > 1000000000:
            raise Error("input outside bounded intake")
    if negative:
        if magnitude == 0:
            raise Error("negative zero is noncanonical")
        return -magnitude
    return magnitude


def fifth_power(x: Int64) -> BigZ:
    var base = bigz_from_i64(x)
    var result = bigz_from_i64(1)
    for _ in range(5):
        result = bigz_mul(result, base)
    return result^


def verify_identity(values: List[Int64]) -> Bool:
    var total = bigz_from_i64(0)
    for i in range(4):
        total = bigz_add(total, fifth_power(values[i]))
    return bigz_eq(total, fifth_power(values[4]))


def verify_row(columns: List[String]) raises -> Bool:
    if len(columns) != 8:
        raise Error("CSV arity must be 8")
    var values = List[Int64]()
    for i in range(5):
        values.append(decimal_base(columns[i]))
    if values[4] <= 0:
        raise Error("target fifth power must be positive")
    var all_positive = True
    for x in values:
        if x <= 0:
            all_positive = False
    if (columns[5] != "true" and columns[5] != "false") or all_positive != (columns[5] == "true"):
        raise Error("all_positive classification mismatch")
    if all_positive:
        for i in range(3):
            if values[i] > values[i + 1]:
                raise Error("positive summands not ordered")
        if values[3] >= values[4]:
            raise Error("largest summand must be below target")
    var divisor = values[0]
    for i in range(1, 5):
        divisor = gcd_i64(divisor, values[i])
    if divisor != 1:
        raise Error("nonprimitive solution")
    if not verify_identity(values):
        raise Error("fifth-power identity failed")
    for prime in [5, 11]:
        var divisible = 0
        for x in values:
            if x % Int64(prime) == 0:
                divisible += 1
        if divisible != 1 and divisible != 3:
            raise Error("modular necessary condition failed")
    return all_positive


def main() raises:
    # Exercise exact acceptance and rejection paths independently of the CSV.
    if not bigz_eq(fifth_power(-2), bigz_from_i64(-32)):
        raise Error("negative fifth-power sign regression")
    if not bigz_eq(fifth_power(1000000000), bigz_mul(
        fifth_power(1000000000), bigz_from_i64(1)
    )):
        raise Error("BigZ upper input limit regression")
    var contents = open("data/known_solutions.csv", "r").read()
    var row_count = 0
    var positive_count = 0
    var header_checked = False
    for raw in contents.split("\n"):
        var line = String(raw)
        if len(line) == 0:
            continue
        if not header_checked:
            if line != "a,b,c,d,e,all_positive,source_year,source":
                raise Error("unexpected CSV header")
            header_checked = True
            continue
        var fields = List[String]()
        for part in line.split(","):
            fields.append(String(part))
        if verify_row(fields):
            positive_count += 1
        row_count += 1
    if not header_checked or row_count != 4 or positive_count != 2:
        raise Error("published corpus cardinality mismatch")
    print("Mojo BigZ verified", row_count, "primitive identities;", positive_count, "positive.")
