"""Machine-readable traces from the *production* Mojo lower-bound engine.

Protocol v1:
 CASE <id> <signed-target> <length>
 VAL <signed-value>                 (exactly length records, in order)
 STEP <lo> <hi> <mid> <signed-pivot> (one per executed iteration)
 STOP <lower-bound-index>
 RESULT <lower-bound-index> <0|1>
 END

Each case checks its traced and untraced execution returned the same result
before emitting END. The independent Lean validator replays every step.
"""
from pair_index import contains_sorted, trace_contains_sorted


def emit_case(case_id: Int, values: List[Int64], target: Int64) raises:
    print("CASE", case_id, target, len(values))
    for value in values:
        print("VAL", value)
    var observed = trace_contains_sorted(values, target)
    if observed != contains_sorted(values, target):
        raise Error("traced production lookup disagrees with untraced lookup")
    print("END")


def main() raises:
    var empty = List[Int64]()
    emit_case(0, empty, 0)
    emit_case(1, empty, -1)

    var ones = List[Int64]()
    ones.append(-7)
    emit_case(2, ones, -8)
    emit_case(3, ones, -7)
    emit_case(4, ones, -6)

    var sorted = List[Int64]()
    for x in [-20, -13, -7, -7, -7, 0, 0, 1, 4, 9, 9, 11]:
        sorted.append(Int64(x))
    emit_case(5, sorted, -21)
    emit_case(6, sorted, -7)
    emit_case(7, sorted, 2)
    emit_case(8, sorted, 9)
    emit_case(9, sorted, 12)

    var duplicates = List[Int64]()
    for _ in range(31):
        duplicates.append(0)
    emit_case(10, duplicates, 0)
    emit_case(11, duplicates, 1)

    var extreme = List[Int64]()
    extreme.append(Int64.MIN)
    extreme.append(-1)
    extreme.append(0)
    extreme.append(0)
    extreme.append(1)
    extreme.append(Int64.MAX)
    emit_case(12, extreme, Int64.MIN)
    emit_case(13, extreme, Int64.MIN + 1)
    emit_case(14, extreme, Int64.MAX)
    emit_case(15, extreme, Int64.MAX - 1)

    var sums = List[Int64]()
    for a in range(1, 13):
        for b in range(a, 13):
            var left = Int64(a)
            var right = Int64(b)
            sums.append(left * left * left * left * left +
                        right * right * right * right * right)
    sort(sums)
    emit_case(16, sums, 0)
    emit_case(17, sums, 32)
    emit_case(18, sums, 33)
    emit_case(19, sums, 2 * 11 * 11 * 11 * 11 * 11)
    emit_case(20, sums, 2 * 12 * 12 * 12 * 12 * 12 + 1)
