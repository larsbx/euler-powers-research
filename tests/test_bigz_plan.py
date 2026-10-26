"""Adversarial tests of canonical, gap-free BigZ shard evidence.

Synthetic streams below only test the receipt verifier's refusals; the
native execution gate separately runs the real compiled Mojo binary.
"""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import bigz_shard_plan as plan


def refused(action):
    try:
        action()
    except (OSError, ValueError):
        return
    raise AssertionError("unsafe plan/transcript unexpectedly accepted")


def test_plan():
    p = plan.make_plan(16, 4, 35)
    assert p["intervals"] == [[2, 5], [6, 9], [10, 13], [14, 16]]
    plan.check_plan(p)
    for bound in (2, 16, 144, 256, 320):
        p = plan.make_plan(bound, 4, 35)
        assert p["intervals"][0][0] == 2
        assert p["intervals"][-1][1] == bound
        plan.check_plan(p)
    malformed = [
        [[2, 5], [7, 9], [10, 13], [14, 16]],  # gap
        [[2, 5], [5, 9], [10, 13], [14, 16]],  # overlap
        [[2, 5], [6, 9], [14, 16]],  # missing shard
        [[2, 5], [6, 9], [10, 13], [14, 15]],  # missing tail
        [[2, 5], [6, 9], [10, 13], [14, 17]],  # excess
        [[6, 9], [2, 5], [10, 13], [14, 16]],  # order
        [[2, 6], [7, 9], [10, 13], [14, 16]],  # too-wide
    ]
    for ranges in malformed:
        bad = deepcopy(plan.make_plan(16, 4, 35))
        bad["intervals"] = ranges
        refused(lambda: plan.check_plan(bad))
    for bound, width, modulus in ((1, 4, 35), (321, 4, 35),
                                   (16, 0, 35), (16, 5, 35),
                                   (16, 4, 1), (16, 4, 36)):
        refused(lambda: plan.make_plan(bound, width, modulus))
    for spelling in ("016", "-2", "+2", " 2", "02", "2.0", "2\n"):
        refused(lambda: plan.natural(spelling))
    stale = plan.make_plan(16, 4, 35)
    stale["source"]["finite_math_kernels_pin"] = "0" * 40
    refused(lambda: plan.check_plan(stale))


def test_receipt_tampering():
    p = plan.make_plan(9, 4, 35)
    plan_hash = plan.digest(plan.canonical(p))
    with tempfile.TemporaryDirectory() as td:
        folder = Path(td)
        plan.atomic(folder / "plan.json", plan.canonical(p))
        for a, b in p["intervals"]:
            raw = plan.oracle(a, b, 35)
            observation = plan.validate_stream(raw, a, b, 35, 1048576)
            receipt = plan.expected_receipt(plan_hash, p, a, b, observation)
            base = plan.filename(a, b)
            plan.atomic(folder / (base + ".txt"), raw)
            plan.atomic(folder / (base + ".receipt.json"), plan.canonical(receipt))
        accepted = plan.validate_acceptance(folder, p, 1048576)
        assert accepted["shards"] == 2
        assert accepted["scope"]["max_e"] == 9
        assert accepted["certificates"] == []
        plan.atomic(folder / "accepted.json", plan.canonical(accepted))
        first = plan.filename(2, 5)
        second = plan.filename(6, 9)
        target = folder / (first + ".txt")
        correct = target.read_bytes()
        target.write_bytes(correct.replace(b"SHARD 2 5", b"SHARD 2 6"))
        refused(lambda: plan.validate_acceptance(folder, p, 1048576))
        target.write_bytes(correct)
        target.write_bytes(correct + correct)
        refused(lambda: plan.validate_acceptance(folder, p, 1048576))
        target.write_bytes(correct)
        other = folder / (second + ".receipt.json")
        content = other.read_bytes()
        other.unlink()
        refused(lambda: plan.validate_acceptance(folder, p, 1048576))
        other.write_bytes(content)
        tampered = json.loads(content)
        tampered["right_pair_visits"] += 1
        other.write_bytes(plan.canonical(tampered))
        refused(lambda: plan.validate_acceptance(folder, p, 1048576))
        other.write_bytes(content)
        assert plan.validate_acceptance(folder, p, 1048576) == accepted
        orphan = folder / "e010-011.txt"
        orphan.write_bytes(b"DOMAIN E5BIGSHARDv1 10 11 35\\n")
        refused(lambda: plan.validate_acceptance(folder, p, 1048576))
        orphan.unlink()
        bad = deepcopy(p)
        bad["intervals"] = [[2, 5], [7, 9]]
        refused(lambda: plan.validate_acceptance(folder, bad, 1048576))
    # Rejection on invalid witness count and malformed PART row.
    raw = plan.oracle(143, 144, 35)
    assert b"CERT E5v1 27 84 110 133 144" in raw
    refused(lambda: plan.validate_stream(raw.replace(
        b"CERT E5v1 27 84 110 133 144", b"CERT E5v1 27 84 110 133 145"
    ), 143, 144, 35, 1048576))
    refused(lambda: plan.validate_stream(raw, 143, 144, 35, 100))


if __name__ == "__main__":
    test_plan()
    test_receipt_tampering()
    print("Gap-free plans, replay receipts, missing/duplicate/stale evidence refused.")
