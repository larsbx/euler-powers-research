"""Deterministic black-box conformance vectors for the *actual* Mojo lookup.

All fifth-power pair sums (including duplicates), immediate misses,
negative target, empty list, and boundary misses for e=2..24.
Output: INDEX e signed_target (0|1).
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
