"""Lossless exact indexed pair records over the shared arbitrary-precision BigZ.

Records are (fifth-power sum, a, b); no packed radix, Int64 conversion,
hash collision assumption or machine-word ordering is used. Stable
bottom-up merge sorting preserves every repeated exact sum, then the
pair indices give canonical deterministic ordering. At equal sums
lower_bound finds the first possible record.
"""
from finite_exact.bigint_z import BigZ, bigz_add, bigz_eq, bigz_lt


struct BigPair(Copyable):
    var sum: BigZ
    var a: Int
    var b: Int

    def __init__(out self, sum: BigZ, a: Int, b: Int):
        self.sum = sum.copy()
        self.a = a
        self.b = b


def pair_less(x: BigPair, y: BigPair) -> Bool:
    if bigz_lt(x.sum, y.sum):
        return True
    if bigz_lt(y.sum, x.sum):
        return False
    if x.a != y.a:
        return x.a < y.a
    return x.b < y.b


def sort_exact_pairs(mut values: List[BigPair]):
    """Stable bottom-up mergesort O(n log n), O(n) temporary records."""
    var n = len(values)
    var width = 1
    while width < n:
        var next = List[BigPair]()
        var start = 0
        while start < n:
            var middle = min(start + width, n)
            var stop = min(start + 2 * width, n)
            var i = start
            var j = middle
            while i < middle and j < stop:
                if pair_less(values[j], values[i]):
                    next.append(values[j].copy())
                    j += 1
                else:
                    next.append(values[i].copy())
                    i += 1
            while i < middle:
                next.append(values[i].copy())
                i += 1
            while j < stop:
                next.append(values[j].copy())
                j += 1
            start = stop
        values = next^
        width *= 2


def _pair_lower_bound_core(
    values: List[BigPair], target: BigZ, emit_trace: Bool
) -> Int:
    """Identical native branching for production and observable execution."""
    var low = 0
    var high = len(values)
    while low < high:
        var mid = low + (high - low) // 2
        if emit_trace:
            from finite_exact.exact_decimal import bigz_decimal
            print("STEP", low, high, mid, bigz_decimal(values[mid].sum))
        if bigz_lt(values[mid].sum, target):
            low = mid + 1
        else:
            high = mid
    if emit_trace:
        print("STOP", low)
    return low


def pair_lower_bound(values: List[BigPair], target: BigZ) -> Int:
    """First exact sum >= target; no narrowing to Int64."""
    return _pair_lower_bound_core(values, target, False)


def trace_pair_lower_bound(values: List[BigPair], target: BigZ) -> Int:
    """Observational transcript from the exact same production branch logic."""
    return _pair_lower_bound_core(values, target, True)


def matching_exact_pairs(
    values: List[BigPair], target: BigZ, max_b: Int
) -> List[Tuple[Int, Int]]:
    """All admissible pair representations, including same-sum collisions."""
    var out = List[Tuple[Int, Int]]()
    var pos = pair_lower_bound(values, target)
    while pos < len(values) and bigz_eq(values[pos].sum, target):
        if values[pos].b <= max_b:
            out.append((values[pos].a, values[pos].b))
        pos += 1
    return out^


def indexed_exact_pairs(powers: List[BigZ], height: Int) -> List[BigPair]:
    """Full 1<=a<=b<height representation index, with no deduplication."""
    var out = List[BigPair]()
    for a in range(1, height):
        for b in range(a, height):
            var value = bigz_add(powers[a], powers[b])
            out.append(BigPair(value, a, b))
    sort_exact_pairs(out)
    return out^


def pair_index_sorted(values: List[BigPair]) -> Bool:
    for i in range(1, len(values)):
        if pair_less(values[i], values[i - 1]):
            return False
    return True
