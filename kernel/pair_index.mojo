"""Shared sorted-array membership kernel for the exact E5 census.

Input contract: `values` is nondecreasing. The caller sorts the exact
pair-sum index first. Return membership, not a witness index: all candidate
pairs are subsequently reconstructed without discarding collisions.
"""


def contains_sorted(values: List[Int64], target: Int64) -> Bool:
    var lo = 0
    var hi = len(values)
    while lo < hi:
        # Invariant: if target occurs, it occurs in [lo, hi), assuming sorted.
        var mid = lo + (hi - lo) // 2
        if values[mid] < target:
            lo = mid + 1
        else:
            hi = mid
    return lo < len(values) and values[lo] == target
