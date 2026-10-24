"""Adversarial black-box tests for the Lean E5v1 witness replay executable.

A verified *set of reported witnesses* is not proof that a bounded census
is complete. Explicitly test the missing-witness case as admissible to the
replay layer, so no one accidentally advertises a soundness guarantee that
does not exist.
"""
from __future__ import annotations

from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
LEAN = ROOT / "formal/lean"
GOOD = (ROOT / "certificates/census_e144.txt").read_text(encoding="ascii")


def replay(text: str, bound: int = 144) -> subprocess.CompletedProcess[str]:
    with TemporaryDirectory(prefix="e5-lean-") as directory:
        path = Path(directory) / "candidate.txt"
        path.write_text(text, encoding="utf-8")
        return subprocess.run(
            ["lake", "exe", "replay", str(path), str(bound)],
            cwd=LEAN,
            capture_output=True,
            text=True,
            check=False,
        )


def main() -> None:
    accepted = replay(GOOD)
    assert accepted.returncode == 0, accepted.stdout + accepted.stderr
    assert "accepted 1 exact E5v1" in accepted.stdout, accepted.stdout
    negatives = {
        "wrong-target": GOOD.replace("133 144", "133 145"),
        "scaled-nonprimitive": "CERT E5v1 54 168 220 266 288\nCENSUS 288 1\n",
        "negative-base": GOOD.replace("27 84", "-27 84"),
        "out-of-height": GOOD.replace("CENSUS 144 1", "CENSUS 143 1"),
        "wrong-count": GOOD.replace("CENSUS 144 1", "CENSUS 144 2"),
        "duplicate": "CERT E5v1 27 84 110 133 144\n" * 2 + "CENSUS 144 2\n",
        "leading-zero": GOOD.replace("27 84", "027 84"),
        "extra-space": GOOD.replace("27 84", "27  84"),
        "bad-tag": GOOD.replace("CERT E5v1", "CERT E4v1"),
        "internal-blank": GOOD.replace("CENSUS 144 1", "\nCENSUS 144 1"),
        "missing-newline": GOOD.rstrip("\n"),
        "trailing-junk": GOOD + "surprise\n",
        "zero-base": GOOD.replace("27 84", "0 84"),
    }
    for name, contents in negatives.items():
        limit = 288 if name == "scaled-nonprimitive" else 144
        result = replay(contents, limit)
        assert result.returncode != 0, (name, result.stdout, result.stderr)

    # This is intentionally accepted. Checking every reported solution does
    # not prove the report contains every solution. The separate Mojo/Python
    # search agreement and bounded coverage proof are still required.
    incomplete = replay("CENSUS 144 0\n")
    assert incomplete.returncode == 0, incomplete.stdout + incomplete.stderr
    print(f"Lean E5v1 replay: valid corpus accepted, {len(negatives)} corruptions refused.")
    print("Omitted-witness corpus remains admissible: completeness is NOT implied.")


if __name__ == "__main__":
    main()
