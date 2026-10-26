"""Execute and independently accept a full 2..12 BigZ Mojo plan.

CI creates a real native transcript for every declared height, replays
each against a separate exact Python full ordered-pair oracle, checks
the plan and immutable receipts, and refuses tampered cached evidence.
"""
from pathlib import Path
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools/bigz_shard_plan.py"


def command(action: str, directory: Path, check: bool = True):
    return subprocess.run(
        [sys.executable, str(TOOL), action, "--output", str(directory),
         "--bound", "12", "--width", "4", "--modulus", "35",
         "--timeout", "60", "--ram-mib", "4096", "--max-bytes", "1048576"],
        cwd=ROOT, check=check, capture_output=True, text=True,
    )


def main():
    with TemporaryDirectory(prefix="euler-bigz-coverage-") as temp:
        output = Path(temp) / "verified"
        run = command("execute", output)
        assert "ACCEPTED exactly heights 2..12" in run.stdout, run.stdout
        assert command("verify", output).returncode == 0
        assert command("execute", output).stdout.count("REPLAYED") == 3
        # Verify a replacement cannot sneak through receipt validation.
        with TemporaryDirectory() as bad:
            clone = Path(bad) / "tampered"
            shutil.copytree(output, clone)
            first = clone / "e002-005.txt"
            first.write_bytes(first.read_bytes() + b"PART 2 0 0 0 0\n")
            refused = command("verify", clone, check=False)
            assert refused.returncode != 0
            assert "REFUSED:" in refused.stderr
        # Deliberate interruption: a valid prefix of accepted shard receipts
        # is NOT a complete plan until every remaining range is checked.
        with TemporaryDirectory() as partial:
            clone = Path(partial) / "partial"
            shutil.copytree(output, clone)
            (clone / "e010-012.receipt.json").unlink()
            (clone / "e010-012.txt").unlink()
            (clone / "accepted.json").unlink()
            result = command("verify", clone, check=False)
            assert result.returncode != 0
        print("Native complete heights 2..12; tampering and missing-tail verification refused.")


if __name__ == "__main__":
    main()
