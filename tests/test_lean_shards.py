"""Adversarial checks for the *Lean* shard and contiguous-plan CLI.

All inputs are synthetic local files. This verifies precise refusal rules;
it does not turn a witness-only certificate into exhaustive evidence.
"""
from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess

ROOT = Path(__file__).resolve().parents[1]
LEAN = ROOT / "formal/lean"
CERT = "CERT E5v1 27 84 110 133 144\n"
GOOD_LO = "CENSUS 2 72 0\n"
GOOD_HI = CERT + "CENSUS 73 144 1\n"


def call(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["lake", "exe", "replay", *args],
        cwd=LEAN, text=True, capture_output=True, check=False,
    )


def try_shard(contents: str, lo: int, hi: int):
    with TemporaryDirectory(prefix="lean-e5-shard-") as directory:
        path = Path(directory) / "shard.txt"
        path.write_text(contents, encoding="utf-8")
        return call("shard", str(path), str(lo), str(hi))


def main() -> None:
    for contents, lo, hi in [(GOOD_LO, 2, 72), (GOOD_HI, 73, 144)]:
        result = try_shard(contents, lo, hi)
        assert result.returncode == 0, result.stdout + result.stderr
    valid = call("plan", "144", "2", "72", "73", "144")
    assert valid.returncode == 0, valid.stdout + valid.stderr

    invalid_plans = [
        ("144", "2", "72", "74", "144"),   # gap
        ("144", "2", "72", "72", "144"),   # overlap
        ("144", "2", "72"),                # missing tail
        ("144", "2", "72", "73", "145"),   # goes beyond bound
        ("144", "3", "72", "73", "144"),   # missing start
        ("144", "2", "144", "145", "144"), # empty final interval
        ("144", "2", "72", "73"),          # odd arity
        ("0144", "2", "72", "73", "144"),  # noncanonical bound
        ("144", "02", "72", "73", "144"),  # noncanonical coordinate
        ("144",),                          # incomplete nonempty request
        ("144", "2", "144", "145", "146"), # extraneous shard
    ]
    for tokens in invalid_plans:
        result = call("plan", *tokens)
        assert result.returncode != 0, (tokens, result.stdout, result.stderr)

    invalid_shards = [
        (CERT + "CENSUS 2 72 1\n", 2, 72),             # target outside shard
        (GOOD_HI.replace("CENSUS 73 144 1", "CENSUS 72 144 1"), 73, 144),
        (GOOD_HI.replace("CENSUS 73 144 1", "CENSUS 73 144 2"), 73, 144),
        (GOOD_HI.replace("27 84", "027 84"), 73, 144),
        (GOOD_HI.replace("133 144", "133 145"), 73, 144),
        (CERT + CERT + "CENSUS 73 144 2\n", 73, 144),
        (GOOD_HI.rstrip("\n"), 73, 144),             # must end with newline
        ("CENSUS 073 144 0\n", 73, 144),
        ("CENSUS 73 144 0\n\n", 73, 144),
        ("CENSUS 144 73 0\n", 73, 144),
        ("CENSUS 73 144 0\n", 2, 72),
    ]
    for contents, lo, hi in invalid_shards:
        result = try_shard(contents, lo, hi)
        assert result.returncode != 0, (contents, result.stdout, result.stderr)

    # Deliberately admissible: a well-formed shard may omit a true witness.
    incomplete = try_shard("CENSUS 73 144 0\n", 73, 144)
    assert incomplete.returncode == 0, incomplete.stdout + incomplete.stderr

    print(
        "Lean shard replay: valid shard cases accepted; "
        f"{len(invalid_plans)} invalid plans and "
        f"{len(invalid_shards)} corrupt shard reports refused. "
        "Missing-witness report remains admissible by design."
    )


if __name__ == "__main__":
    main()
