"""Black-box conformance of the same Mojo lower-bound lookup used by E5.

An independent Python set supplies expected membership results for pair
sums, arbitrary signed sorted arrays, repeated values and Int64 extremes.
"""
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def rows():
    yield ("INDEX", 0, 0, 0)
    yield ("INDEX", 0, -1, 0)
    for e in range(2, 25):
        vals = [a**5 + b**5 for a in range(1, e) for b in range(a, e)]
        truth = set(vals)
        queries = [-1, 0]
        for val in sorted(vals):
            queries.extend((val - 1, val, val + 1))
        queries.append(2 * (e - 1)**5 + 1)
        for target in queries:
            yield ("INDEX", e, target, int(target in truth))

    for size in range(65):
        vals = sorted((i * 37 + size * 13) % 41 - 20 for i in range(size))
        truth = set(vals)
        for target in range(-25, 26):
            yield ("SIGNED", size, target, int(target in truth))

    for size in range(1, 65):
        vals = {-7}
        for target in range(-8, -5):
            yield ("SIGNED", size, target, int(target in vals))

    extremes = {-(2**63), 0, 2**63 - 1}
    for target in (-(2**63), -(2**63) + 1, -1, 0, 1, 2**63 - 2, 2**63 - 1):
        yield ("SIGNED", 999, target, int(target in extremes))


def main():
    process = subprocess.run(
        ["bash", "scripts/run_mojo.sh", "kernel/pair_index_probe.mojo"],
        cwd=ROOT, capture_output=True, text=True, check=True,
    )
    lines = process.stdout.splitlines()
    reference = list(rows())
    assert len(lines) == len(reference), (len(lines), len(reference))
    for index, (actual, expected) in enumerate(zip(lines, reference)):
        fields = actual.split(" ")
        assert len(fields) == 4 and fields[0] == expected[0], (index, actual)
        result = (fields[0], *(int(field) for field in fields[1:]))
        assert result == expected, (index, result, expected)
    assert len(reference) > 10000
    print(
        f"Actual Mojo sorted-array lower-bound lookup agreed with Python on "
        f"{len(reference)} deterministic queries: fifth-power pair sums, "
        f"signed arrays, duplicate runs and Int64 extremes."
    )


if __name__ == "__main__":
    main()
