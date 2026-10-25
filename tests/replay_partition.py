"""Strict independent replay of E5PARTv1 output with per-key SHA-256.

Checks the *reported records*, ownership, key-domain coverage, counts,
and (when provided) the independent exact Python candidate oracle.
It does not prove a malicious enumerator cannot omit all witnesses.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from hashlib import sha256
from math import gcd
import re

NAT = re.compile(r"(?:0|[1-9][0-9]*)", re.ASCII)


def natural(value: str) -> int:
    assert NAT.fullmatch(value) is not None, f"noncanonical decimal: {value!r}"
    return int(value)


def owner_key(a: int, b: int, c: int, d: int, modulus: int) -> tuple[int, int]:
    return tuple(sorted(((a**5 + b**5) % modulus, (c**5 + d**5) % modulus)))


def canonical_keys(bound: int, modulus: int):
    return [
        (e, lo, hi)
        for e in range(2, bound + 1)
        for lo in range(modulus)
        for hi in range(lo, modulus)
        if (lo + hi) % modulus == pow(e, 5, modulus)
    ]


def replay(
    lines: list[str], bound: int, modulus: int,
    expected_parts: list[tuple[int, ...]] | None = None,
    expected_certs: list[tuple[int, ...]] | None = None,
    expected_root: str | None = None,
) -> dict:
    """Fail-closed, context-bound replay; immutable canonical digest leaves.

    expected_parts and expected_certs MUST come from an independent oracle,
    not from the emitted Mojo report. Without them, the replay only validates
    internal consistency and mathematical soundness of supplied certificates.
    """
    assert 2 <= bound <= 144 and 1 <= modulus <= 35
    assert lines and lines[0] == f"DOMAIN E5PARTv1 {bound} {modulus}"
    assert lines[-1].startswith("TOTAL ")
    parts = []
    certificates = []
    for line in lines[1:-1]:
        assert line and line.isascii() and line.strip() == line
        tokens = line.split(" ")
        assert all(tokens), line
        if tokens[0] == "PART":
            assert len(tokens) == 6
            row = tuple(natural(x) for x in tokens[1:])
            parts.append(row)
        elif tokens[:2] == ["CERT", "E5v1"]:
            assert len(tokens) == 7
            a, b, c, d, e = tuple(natural(x) for x in tokens[2:])
            assert 1 <= a <= b <= c <= d < e <= bound
            assert a**5 + b**5 + c**5 + d**5 == e**5
            assert gcd(a, b, c, d, e) == 1
            certificates.append((a, b, c, d, e))
        else:
            raise AssertionError(f"unknown record: {line!r}")
    total = lines[-1].split(" ")
    assert len(total) == 2 and total[0] == "TOTAL"
    assert natural(total[1]) == len(certificates)
    assert len(certificates) == len(set(certificates)), "duplicate certificate"
    keys = canonical_keys(bound, modulus)
    assert [row[:3] for row in parts] == keys, "missing, duplicate, or out-of-order key"
    hits = defaultdict(list)
    for a, b, c, d, e in certificates:
        lo, hi = owner_key(a, b, c, d, modulus)
        hits[e, lo, hi].append((a, b, c, d, e))
    for e, lo, hi, visits, count in parts:
        assert count == len(hits[e, lo, hi]), "per-key witness count mismatch"
        assert count <= visits, "more witnesses than right-pair visits"
    if expected_parts is not None:
        assert parts == expected_parts, "independent oracle disagrees on partition visits/hits"
    if expected_certs is not None:
        assert Counter(certificates) == Counter(expected_certs), "independent oracle disagrees"
    leaves = []
    for row in parts:
        e, lo, hi, visits, count = row
        cert_lines = [
            "CERT E5v1 " + " ".join(map(str, certificate))
            for certificate in sorted(hits[e, lo, hi])
        ]
        payload = (
            "E5PART-LEAF-v2\n" +
            f"DOMAIN {bound} {modulus}\n" +
            "PART " + " ".join(map(str, row)) + "\n" +
            "".join(line + "\n" for line in cert_lines)
        )
        digest = sha256(payload.encode("ascii")).hexdigest()
        leaves.append((e, lo, hi, digest))
    root_payload = "E5PART-ROOT-v2\n" + "".join(
        f"{e} {lo} {hi} {digest}\n" for e, lo, hi, digest in leaves
    )
    root = sha256(root_payload.encode("ascii")).hexdigest()
    if expected_root is not None:
        assert re.fullmatch(r"[0-9a-f]{64}", expected_root)
        assert root == expected_root, "stale or corrupted domain-specific manifest"
    return {
        "schema": "E5PART-REPLAY-v2",
        "bound": bound,
        "modulus": modulus,
        "partition_rows": len(parts),
        "right_pair_visits": sum(row[3] for row in parts),
        "certificates": len(certificates),
        "root_sha256": root,
        "leaves": leaves,
    }


def digest_lines(report: dict) -> list[str]:
    return [
        f"PARTDIGEST {e} {lo} {hi} {digest}"
        for e, lo, hi, digest in report["leaves"]
    ] + [f"ROOTDIGEST {report['root_sha256']}"]


if __name__ == "__main__":
    import argparse
    from pathlib import Path
    from test_pair_partition import oracle

    parser = argparse.ArgumentParser(description="Independent canonical PART replay")
    parser.add_argument("stream", type=Path, help="Raw Mojo stdout, not regenerated records")
    parser.add_argument("bound", type=int)
    parser.add_argument("modulus", type=int)
    parser.add_argument("--expected-root", help="Pinned domain-specific SHA-256 root")
    args = parser.parse_args()
    expected_parts, expected_certs = oracle(args.bound, args.modulus)
    report = replay(
        args.stream.read_text(encoding="ascii").splitlines(),
        args.bound, args.modulus, expected_parts, expected_certs,
        args.expected_root,
    )
    print("\n".join(digest_lines(report)))
