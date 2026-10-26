"""Check actual Mojo BigZ trace against Python and kernel-checked Lean.

All values are exact signed integers, including several values >2^63
and < -2^63; independent Python replays every midpoint decision.
The Lean executable rechecks the same actual raw native observations
using its universally proven signed lower-bound algorithm.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import re
import subprocess
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
LEAN = ROOT / "formal/lean"
DEC = re.compile(r"-?(?:0|[1-9][0-9]*)\Z", flags=re.ASCII)
NAT = re.compile(r"(?:0|[1-9][0-9]*)\Z", flags=re.ASCII)


def number(text: str, unsigned: bool = False) -> int:
    if (NAT if unsigned else DEC).fullmatch(text) is None or text == "-0":
        raise ValueError("noncanonical signed/unsigned decimal")
    return int(text)


def replay_python(data: str) -> int:
    if not data.endswith("\n") or data.endswith("\n\n") or not data.isascii():
        raise ValueError("noncanonical ASCII transcript terminator")
    lines = data[:-1].split("\n")
    pos = 0
    max_above = 0
    min_below = 0
    for case in range(18):
        if pos >= len(lines):
            raise ValueError("truncated cases")
        heading = lines[pos].split(" ")
        pos += 1
        if len(heading) != 4 or heading[0] != "CASE":
            raise ValueError("invalid CASE")
        identifier, target, count = (
            number(heading[1], True), number(heading[2]), number(heading[3], True)
        )
        if identifier != case or count > 100:
            raise ValueError("incorrect CASE id or size")
        values = []
        for _ in range(count):
            cols = lines[pos].split(" ") if pos < len(lines) else []
            if len(cols) != 2 or cols[0] != "VAL":
                raise ValueError("truncated or malformed VAL")
            values.append(number(cols[1]))
            pos += 1
        if values != sorted(values):
            raise ValueError("unsorted native case")
        max_above = max(max_above, target, *(values or [0]))
        min_below = min(min_below, target, *(values or [0]))
        lo, hi = 0, count
        while lo < hi:
            if pos >= len(lines):
                raise ValueError("missing STEP")
            cols = lines[pos].split(" ")
            pos += 1
            mid = lo + (hi - lo) // 2
            expected = ["STEP", str(lo), str(hi), str(mid), str(values[mid])]
            if cols != expected:
                raise ValueError("wrong BigZ STEP/pivot/window")
            if values[mid] < target:
                lo = mid + 1
            else:
                hi = mid
        if pos + 2 >= len(lines):
            raise ValueError("truncated terminal")
        flag = int(lo < len(values) and values[lo] == target)
        expected = [f"STOP {lo}", f"RESULT {lo} {flag}", "END"]
        if lines[pos:pos + 3] != expected:
            raise ValueError("wrong native terminal index or membership")
        if flag != int(target in values):
            raise ValueError("incorrect exact signed sorted membership")
        pos += 3
    if pos != len(lines):
        raise ValueError("extraneous native cases")
    assert max_above > 2**100 and min_below < -(2**63)
    return 18


def run_lean(data: str) -> subprocess.CompletedProcess[str]:
    with TemporaryDirectory(prefix="bigz-lean-replay-") as d:
        path = Path(d) / "trace.txt"
        path.write_text(data, encoding="ascii")
        return subprocess.run(
            ["lake", "exe", "bigz-trace-replay", str(path)],
            cwd=LEAN, text=True, capture_output=True,
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--python-only", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    process = subprocess.run(
        ["bash", "scripts/run_mojo.sh", "kernel/bigz_trace_probe.mojo"],
        cwd=ROOT, check=False, capture_output=True, text=True,
    )
    assert process.returncode == 0, (
        f"native BigZ trace failed: {process.stderr}\n{process.stdout}"
    )
    source = process.stdout
    assert replay_python(source) == 18
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(source, encoding="ascii")
    corrupted = {
        "forged-pivot": source.replace("STEP ", "STEP 999 ", 1),
        "truncated": source.rsplit("END\n", 1)[0],
        "duplicate-case": source + source.split("END\n", 1)[0] + "END\n",
        "bad-case-id": source.replace("CASE 0 ", "CASE 1 ", 1),
        "wrong-terminal": source.replace("RESULT ", "RESULT 999 ", 1),
        "signed-negative-zero": source.replace("VAL -7\n", "VAL -0\n", 1),
        "leading-zero": source.replace("CASE 0 0 0", "CASE 00 0 0", 1),
        "extra-newline": source + "\n",
        "invalid-marker": source.replace("END\n", "NOEND\n", 1),
    }
    for name, bad in corrupted.items():
        try:
            replay_python(bad)
        except (ValueError, IndexError):
            pass
        else:
            raise AssertionError(f"corrupt BigZ trace accepted: {name}")
    if not args.python_only:
        valid = run_lean(source)
        assert valid.returncode == 0, valid.stdout + valid.stderr
        assert "replayed 18" in valid.stdout
        for name, bad in corrupted.items():
            answer = run_lean(bad)
            assert answer.returncode != 0, (name, answer.stdout, answer.stderr)
    print(
        "Actual compiled Mojo BigZ lower-bound: 18 arbitrary-precision cases, "
        f"{len(corrupted)} corruptions refused by Python" +
        (" and Lean." if not args.python_only else ".")
    )


if __name__ == "__main__":
    main()
