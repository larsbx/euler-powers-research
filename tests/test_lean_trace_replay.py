"""Adversarial cross-language replay of the actual Mojo lower-bound trace.

The same source function is used by the production census, the ordinary
conformance probe, and this trace probe. Lean independently checks signed
pivots, exact window updates, termination, and final membership.
"""
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
LEAN = ROOT / "formal/lean"


def check_lean(data: str) -> subprocess.CompletedProcess[str]:
    with TemporaryDirectory(prefix="e5-trace-") as directory:
        target = Path(directory) / "trace.txt"
        target.write_text(data, encoding="utf-8")
        return subprocess.run(
            ["lake", "exe", "trace-replay", str(target)],
            cwd=LEAN, capture_output=True, text=True, check=False,
        )


def corrupt_tag(trace: str, tag: str, new_row: str) -> str:
    lines = trace.splitlines()
    index = next(i for i, line in enumerate(lines) if line.startswith(tag))
    lines[index] = new_row
    return "\n".join(lines) + "\n"


def main() -> None:
    source = subprocess.run(
        ["bash", "scripts/run_mojo.sh", "kernel/pair_index_trace_probe.mojo"],
        cwd=ROOT, capture_output=True, text=True, check=True,
    ).stdout
    assert source.count("\nCASE ") == 20 and source.startswith("CASE 0 ")
    assert source.count("\nEND\n") == 20 and source.endswith("END\n")
    checked = check_lean(source)
    assert checked.returncode == 0, checked.stdout + checked.stderr
    assert "replayed 21" in checked.stdout, checked.stdout

    rows = source.splitlines()
    case = next(line for line in rows if line.startswith("CASE "))
    values = next(line for line in rows if line.startswith("VAL "))
    steps = next(line for line in rows if line.startswith("STEP "))
    stop = next(line for line in rows if line.startswith("STOP "))
    result = next(line for line in rows if line.startswith("RESULT "))

    tests = {
        "truncated": source.rsplit("END\n", 1)[0],
        "extra-newline": source + "\n",
        "extra-case": source + "CASE 21 0 0\nSTOP 0\nRESULT 0 0\nEND\n",
        "wrong-id": corrupt_tag(source, "CASE ", case.replace("CASE 0 ", "CASE 5 ", 1)),
        "wrong-case-count": corrupt_tag(source, "CASE ", case.replace(" 0\n", " 1\n", 1)) if False else
            corrupt_tag(source, "CASE ", "CASE 0 0 1"),
        "wrong-value": corrupt_tag(source, "VAL ", "VAL 999"),
        "noncanonical-signed": corrupt_tag(source, "VAL ", "VAL -0"),
        "forge-step": corrupt_tag(source, "STEP ", "STEP 0 1 0 999"),
        "skip-step": source.replace(steps + "\n", "", 1),
        "wrong-stop": corrupt_tag(source, "STOP ", "STOP 99"),
        "wrong-result": corrupt_tag(source, "RESULT ", "RESULT 0 9"),
        "missing-marker": source.replace("\nEND\n", "\nNOEND\n", 1),
    }
    for name, text in tests.items():
        replayed = check_lean(text)
        assert replayed.returncode != 0, (name, replayed.stdout, replayed.stderr)
    print(
        "Actual Mojo lower-bound trace replay: 21 deterministic cases accepted; "
        f"{len(tests)} corrupted transcripts rejected by Lean."
    )


if __name__ == "__main__":
    main()
