"""Deterministic black-box conformance vectors for the *actual* Mojo lookup.

All fifth-power pair sums (including duplicates), immediate misses,
negative target, empty list, and boundary misses for e=2..24.
Output: INDEX e signed_target (0|1), plus SIGNED length target (0|1).
"""
from pair_index import contains_sorted


def power5(x: Int) -> Int64:
    var n = Int64(x)
    return n * n * n * n * n


def show(e: Int, arr: List[Int64], target: Int64):
    if contains_sorted(arr, target):
        print("INDEX", e, target, 1)
    else:
        print("INDEX", e, target, 0)


def main():
    var empty = List[Int64]()
    show(0, empty, 0)
    show(0, empty, -1)
    for e in range(2, 25):
        var sums = List[Int64]()
        for a in range(1, e):
            for b in range(a, e):
                sums.append(power5(a) + power5(b))
        sort(sums)
        show(e, sums, -1)
        show(e, sums, 0)
        for v in sums:
            show(e, sums, v - 1)
            show(e, sums, v)
            show(e, sums, v + 1)
        show(e, sums, 2 * power5(e - 1) + 1)
    signed_probe()


# Arbitrary sorted signed inputs exercise the same imported production lookup.
def show_signed(size: Int, arr: List[Int64], target: Int64):
    if contains_sorted(arr, target):
        print("SIGNED", size, target, 1)
    else:
        print("SIGNED", size, target, 0)


def signed_probe():
    for size in range(65):
        var values = List[Int64]()
        for i in range(size):
            values.append(Int64((i * 37 + size * 13) % 41 - 20))
        sort(values)
        for target in range(-25, 26):
            show_signed(size, values, Int64(target))

    for size in range(1, 65):
        var duplicates = List[Int64]()
        for _ in range(size):
            duplicates.append(Int64(-7))
        for target in range(-8, -5):
            show_signed(size, duplicates, Int64(target))

    var extremes = List[Int64]()
    extremes.append(Int64.MIN)
    extremes.append(0)
    extremes.append(Int64.MAX)
    sort(extremes)
    show_signed(999, extremes, Int64.MIN)
    show_signed(999, extremes, Int64.MIN + 1)
    show_signed(999, extremes, -1)
    show_signed(999, extremes, 0)
    show_signed(999, extremes, 1)
    show_signed(999, extremes, Int64.MAX - 1)
    show_signed(999, extremes, Int64.MAX)
