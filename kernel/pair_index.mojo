"""Shared sorted-array lower-bound engine for the exact E5 census.

The production call and trace-enabled call use the *same branch logic*.
The trace is an observational replay interface. Its validator checks the
executed transition sequence, not compiler-level universal equivalence.
Input contract: values must already be nondecreasing.
"""


def lower_bound(values: List[Int64], target: Int64, emit_trace: Bool) -> Int:
    var lo = 0
    var hi = len(values)
    while lo < hi:
        var mid = lo + (hi - lo) // 2
        var pivot = values[mid]
        if emit_trace:
            print("STEP", lo, hi, mid, pivot)
        if pivot < target:
            lo = mid + 1
        else:
            hi = mid
    if emit_trace:
        print("STOP", lo)
    return lo


def contains_sorted(values: List[Int64], target: Int64) -> Bool:
    var lo = lower_bound(values, target, False)
    return lo < len(values) and values[lo] == target


def trace_contains_sorted(values: List[Int64], target: Int64) -> Bool:
    var lo = lower_bound(values, target, True)
    var found = lo < len(values) and values[lo] == target
    if found:
        print("RESULT", lo, 1)
    else:
        print("RESULT", lo, 0)
    return found
