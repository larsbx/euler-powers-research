"""Compare each runtime Mojo binary-search result against an independent
Python integer set, without relying on the candidate census output."""
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def rows():
    yield (0, 0, 0)
    yield (0, -1, 0)
    for e in range(2, 25):
        vals = [a**5 + b**5 for a in range(1, e) for b in range(a, e)]
        truth = set(vals)
        queries = [-1, 0]
        for val in sorted(vals):
            queries.extend((val - 1, val, val + 1))
        queries.append(2 * (e - 1)**5 + 1)
        for target in queries:
            yield (e, target, int(target in truth))


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
        assert len(fields) == 4 and fields[0] == "INDEX", (index, actual)
        result = tuple(map(int, fields[1:]))
        assert result == expected, (index, result, expected)
    print(
        f"Mojo sorted-array lower-bound lookup agreed with independent "
        f"Python membership on {len(reference)} queries (e=2..24, "
        f"including duplicates and empty/negative/boundary misses)."
    )


if __name__ == "__main__":
    main()
