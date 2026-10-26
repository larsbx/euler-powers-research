"""Independent Python exact tuple oracle for the actual Mojo BigZ mergesort.

Not a simulated native sorter. The full raw IN/OUT records are emitted
by compiled production sort_exact_pairs and checked against Python's
separate arbitrary-precision sorted() and Counter() implementations.
"""
from __future__ import annotations

from collections import Counter
from pathlib import Path
import argparse
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def fixtures() -> list[list[tuple[int, int, int]]]:
    huge = 2**63
    wide = huge**2
    return [
        [],
        [(huge, 1, 1)],
        [(i - 5, i + 1, i + 1) for i in range(12)],
        [(8 - i, 12 - i, 12 - i) for i in range(12)],
        [(huge, 16 - i, 16 - i) for i in range(16)] +
        [(huge, 1, 1), (huge, 1, 1)],
        [(wide, 4, 4), (-wide, 1, 1), (huge, 4, 4), (0, 2, 2),
         (wide, 2, 2), (-wide, 3, 3), (huge, 2, 2)],
        [((i * 37 + 13) % 41 - 20, (i * 11) % 19 + 1, (i * 7) % 23 + 1)
         for i in range(64)],
        [(a**5 + b**5, a, b) for a in range(1, 13) for b in range(a, 13)],
    ]


def parse(raw: str) -> list[tuple[list[tuple[int, int, int]],
                                  list[tuple[int, int, int]]]]:
    if not raw.endswith("\n") or raw.endswith("\n\n") or not raw.isascii():
        raise ValueError("noncanonical native terminal bytes")
    rows = raw[:-1].split("\n")
    cursor = 0
    result = []
    for n, expected in enumerate(fixtures()):
        if cursor >= len(rows):
            raise ValueError("missing sort case")
        if rows[cursor] != f"CASE {n} {len(expected)}":
            raise ValueError("invalid case id, length or ordering")
        cursor += 1
        input_rows, output_rows = [], []
        for marker, dest in (("IN", input_rows), ("OUT", output_rows)):
            for _ in range(len(expected)):
                if cursor >= len(rows):
                    raise ValueError("missing native record")
                tokens = rows[cursor].split(" ")
                cursor += 1
                if len(tokens) != 4 or tokens[0] != marker:
                    raise ValueError("invalid record tag")
                record = tuple(map(int, tokens[1:]))
                if " ".join(map(str, record)) != " ".join(tokens[1:]):
                    raise ValueError("noncanonical exact integer serialization")
                dest.append(record)
        if cursor >= len(rows) or rows[cursor] != "END":
            raise ValueError("missing END")
        cursor += 1
        if input_rows != expected:
            raise ValueError("the actual native input is not the pinned case")
        if output_rows != sorted(expected):
            raise ValueError("Mojo BigZ sorted result differs from independent oracle")
        if Counter(output_rows) != Counter(input_rows):
            raise ValueError("Mojo BigZ result lost or duplicated records")
        result.append((input_rows, output_rows))
    if cursor != len(rows):
        raise ValueError("unexpected extra output")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    run = subprocess.run(
        ["bash", "scripts/run_mojo.sh", "kernel/bigz_sort_probe.mojo"],
        cwd=ROOT, text=True, capture_output=True,
    )
    assert run.returncode == 0, run.stderr + run.stdout
    parsed = parse(run.stdout)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(run.stdout, encoding="ascii")
    assert len(parsed) == 8
    assert len(parsed[-1][1]) == 78
    assert parsed[5][1][0][0] < -(2**63)
    assert parsed[5][1][-1][0] > 2**100
    assert parsed[4][1].count((2**63, 1, 1)) == 3
    corruptions = {
        "missing-item": run.stdout.replace("OUT ", "DROP ", 1),
        "reordered": run.stdout.replace("CASE 0 0", "CASE 1 0", 1),
        "extra": run.stdout + "END\n",
        "missing-final": run.stdout.removesuffix("END\n"),
        "duplicate": run.stdout.replace("IN ", "OUT ", 1),
        "bad-number": run.stdout.replace("OUT 0 2 2", "OUT 00 2 2", 1),
    }
    for name, bad in corruptions.items():
        assert bad != run.stdout, name
        try:
            parse(bad)
        except (ValueError, IndexError):
            continue
        raise AssertionError(f"accepted corruption {name}")
    print("Actual Mojo BigZ mergesort: 8 independent exact Python case/replay "
          f"checks passed, {len(corruptions)} corrupted records rejected.")


if __name__ == "__main__":
    main()
