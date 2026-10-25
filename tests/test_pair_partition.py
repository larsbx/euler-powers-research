"""Independent exact partition oracle, strict stream comparison and manifest.

The oracle indexes all pair representations in a Python hash multimap;
Mojo uses sorted residue buckets, binary search and reconstruction.
"""
from collections import Counter, defaultdict
from hashlib import sha256
from math import gcd, isqrt
from functools import lru_cache
from pathlib import Path
import json
import subprocess
import tempfile
import sys

from check_research_kernels import certificate_digest, parse_census, python_census, run_mojo
from replay_partition import replay, digest_lines

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / 'certificates/pair_partition_e144_m35.json'


@lru_cache(maxsize=None)
def oracle(bound, modulus):
    parts, certs = [], []
    for e in range(2, bound + 1):
        pairs = defaultdict(list)
        for a in range(1, e):
            for b in range(a, e):
                pairs[a**5 + b**5].append((a, b))
        visits, found = Counter(), defaultdict(list)
        # Each right pair is visited once; no outer partition-key loop.
        for c in range(1, e):
            for d in range(c, e):
                right = c**5 + d**5
                target = e**5 - right
                if target <= 0:
                    continue
                key = tuple(sorted((target % modulus, right % modulus)))
                visits[key] += 1
                for a, b in pairs.get(target, ()):
                    if b <= c and gcd(a, b, c, d, e) == 1:
                        found[key].append((a, b, c, d, e))
        for lo in range(modulus):
            for hi in range(lo, modulus):
                if (lo + hi) % modulus == pow(e, 5, modulus):
                    parts.append((e, lo, hi, visits[lo, hi], len(found[lo, hi])))
                    certs.extend(found[lo, hi])
    return parts, certs


@lru_cache(maxsize=None)
def expected_stream(bound, modulus):
    parts, certs = oracle(bound, modulus)
    # Compare record multisets; order of certificate discovery is incidental.
    lines = [f'DOMAIN E5PARTv1 {bound} {modulus}']
    lines += ['PART ' + ' '.join(map(str, p)) for p in parts]
    lines += ['CERT E5v1 ' + ' '.join(map(str, c)) for c in certs]
    lines += [f'TOTAL {len(certs)}']
    return Counter(lines)


def validate(lines, bound, modulus):
    # Exact strings enforce canonical decimal spelling, row cardinality,
    # complete key coverage, visit counts and certificate multiplicity.
    assert lines[0] == f'DOMAIN E5PARTv1 {bound} {modulus}'
    assert lines[-1].startswith('TOTAL ')
    assert Counter(lines) == expected_stream(bound, modulus)
    reference_parts, reference_certs = oracle(bound, modulus)
    root = (
        '5b8ed68d8512bb11bf4ac57e2f79657e65893427c157c0615b784d86671af482'
        if (bound, modulus) == (144, 35) else None
    )
    report = replay(lines, bound, modulus, reference_parts, reference_certs, root)
    assert len(digest_lines(report)) == len(reference_parts) + 1
    certs = [tuple(map(int, line.split()[2:])) for line in lines if line.startswith('CERT ')]
    assert len(certs) == len(set(certs))
    assert sorted(certs) == sorted(python_census(bound))
    return certs


def manifest(lines):
    certs = validate(lines, 144, 35)
    parts = [tuple(map(int, line.split()[1:])) for line in lines if line.startswith('PART ')]
    canonical = '\n'.join(sorted(lines)) + '\n'
    return {
        'schema': 'E5PART-MANIFEST-v1',
        'domain': {'min_e': 2, 'max_e': 144, 'positive': True, 'primitive': True,
                   'ordering': '1 <= a <= b <= c <= d < e', 'modulus': 35},
        'ownership': 'sort((a^5+b^5) mod M, (c^5+d^5) mod M)',
        'partition_rows': len(parts),
        'right_pair_visits': sum(p[3] for p in parts),
        'certificates': len(certs),
        'certificate_sha256': certificate_digest(certs),
        'canonical_stream_sha256': sha256(('E5PART-STREAM-v1\n' + canonical).encode('ascii')).hexdigest(),
        'canonical_stream_encoding': 'ASCII; lexicographically sorted lines; LF after each line',
        'partition_row_encoding': '[e, low_residue, high_residue, right_pair_visits, certificates]',
        'partitions': [list(p) for p in parts],
    }


def prerequisites():
    # Independent finite exhaustive check: prerequisite is NOT needed for coverage.
    for m, factors in ((7, (7,)), (35, (5, 7))):
        assert len(set(factors)) == len(factors)
        product = 1
        for p in factors:
            assert p >= 2 and all(p % d for d in range(2, isqrt(p) + 1))
            assert gcd(5, p - 1) == 1
            assert len({pow(x, 5, p) for x in range(p)}) == p
            product *= p
        assert product == m and len({pow(x, 5, m) for x in range(m)}) == m
    assert len({pow(x, 5, 11) for x in range(11)}) != 11


def main():
    prerequisites()
    try:
        probe = run_mojo('kernel/pair_partition_probe.mojo')
    except subprocess.CalledProcessError as error:
        print(error.stderr, file=sys.stderr)
        raise
    expected = []
    for m in (1, 2, 7, 11, 35):
        for s in range(71):
            for t in range(71):
                lo, hi = sorted((s % m, t % m))
                expected.append(f'KEY {m} {s} {t} {lo} {hi}')
        for a in range(1, 5):
            for b in range(a, 5):
                expected.append(f'BUCKET {m} {(a+b) % m} {a+b}')
    for c in range(1, 5):
        for a in range(1, c+1):
            for b in range(a, c+1):
                expected.append(f'PAIR {c} {a+b} {a} {b}')
    # Independently enumerate every signed-free synthetic representation;
    # the compiled packed-index implementation is exercised on each case.
    for m in (1, 2, 7, 11, 35):
        for case, values in enumerate(((0, 1, 2, 3, 4), (0, 2, 2, 5, 5))):
            for c in range(1, 5):
                for target in range(13):
                    for a in range(1, 5):
                        for b in range(a, 5):
                            if b <= c and values[a] + values[b] == target:
                                expected.append(
                                    f'INDEX {case} {m} {c} {target} {a} {b}'
                                )
    max_packed = ((2 * 144**5) * 145 + 143) * 145 + 143
    assert max_packed < 2**63
    expected.append(f'PACK {max_packed}')
    assert Counter(probe) == Counter(expected)
    assert 'INDEX 0 1 4 5 1 4' in probe
    assert 'INDEX 0 1 4 5 2 3' in probe
    for a, b in ((1, 1), (1, 2), (2, 2)):
        assert f'INDEX 1 11 4 4 {a} {b}' in probe
    assert 'PAIR 4 5 1 4' in probe and 'PAIR 4 5 2 3' in probe
    print('25,205 ownership probes, packed index collisions and synthetic repeated-power reconstruction passed.')
    with tempfile.TemporaryDirectory() as tmp:
        binary = str(Path(tmp) / 'partition')
        subprocess.run(['mojo', 'build', '-I', 'kernel', '-I', '.deps/finite-math-kernels/kernel',
                        'kernel/pair_partition.mojo', '-o', binary], cwd=ROOT, check=True)
        for bound, modulus in ((2, 7), (8, 1), (8, 2), (8, 7), (8, 11), (8, 35), (144, 35)):
            lines = subprocess.check_output([binary, str(bound), str(modulus)], text=True).splitlines()
            certs = validate(lines, bound, modulus)
            baseline = parse_census(run_mojo('kernel/positive_census.mojo', str(bound)), bound)
            assert sorted(certs) == sorted(baseline)
            if bound == 144:
                full = lines
            print(f'Partition union equals oracle and unpartitioned Mojo: B={bound}, M={modulus}')
        for args in (('1', '7'), ('145', '7'), ('8', '0'), ('8', '36'), ('08', '7'),
                     ('-8', '7'), ('8', '07'), ('0', '0'), ('8',), ('8', '7', '1')):
            result = subprocess.run([binary, *args], capture_output=True, text=True)
            assert result.returncode != 0, args
        cert_index = next(i for i, s in enumerate(full) if s.startswith('CERT '))
        bad_streams = [full[:cert_index] + full[cert_index+1:], full + [full[cert_index]],
                       [s.replace('PART 2 0 32', 'PART 2 00 32') for s in full],
                       full[:-1] + ['TOTAL 2'], full[1:]]
        # Remove a zero-certificate partition; change a visit count.
        bad_streams += [[s for i, s in enumerate(full) if i != 1],
                        full[:1] + [full[1] + ' 0'] + full[2:]]
        for bad in bad_streams:
            assert bad != full
            try:
                validate(bad, 144, 35)
            except AssertionError:
                pass
            else:
                raise AssertionError('corrupt stream accepted')
        # P2 replay rejects stale/wrong-domain streams, duplicate/missing
        # keys, invalid per-key counts, invalid hashes and noncanonical rows.
        reference_parts, reference_certs = oracle(144, 35)
        good = replay(full, 144, 35, reference_parts, reference_certs,
                      '5b8ed68d8512bb11bf4ac57e2f79657e65893427c157c0615b784d86671af482')
        assert good['partition_rows'] == 2574 and good['right_pair_visits'] == 475063
        assert good['certificates'] == 1
        bad_replays = [
            (full, 143, 35, None),
            (full, 144, 34, None),
            (full, 144, 35, '0' * 64),
            (full[:2] + [full[1]] + full[2:], 144, 35, None),
            (full[:1] + full[2:], 144, 35, None),
            ([s.replace('PART 2 0 32', 'PART 2 00 32') for s in full], 144, 35, None),
            ([s.replace('PART 2 0 32 0 0', 'PART 2 0 32 1 0')
              for s in full], 144, 35, None),
            (full[:cert_index] + full[cert_index+1:], 144, 35, None),
        ]
        for stream, b, m, digest in bad_replays:
            try:
                replay(stream, b, m, oracle(b, m)[0], oracle(b, m)[1], digest)
            except AssertionError:
                pass
            else:
                raise AssertionError('stale or corrupted partition accepted by replay')
        print('P2 replay: domain, keys, counts and digests verified; 8 corrupt streams rejected.')
        record = manifest(full)
        if '--write' in sys.argv:
            header = {k: v for k, v in record.items() if k != 'partitions'}
            text = json.dumps(header, indent=2)[:-2] + ',\n  "partitions": [\n'
            text += ',\n'.join('    ' + json.dumps(row) for row in record['partitions'])
            MANIFEST.write_text(text + '\n  ]\n}\n')
        else:
            assert json.loads(MANIFEST.read_text()) == record
        print(f"Manifest: {record['partition_rows']} partitions; {record['right_pair_visits']} visits; "
              f"{record['certificates']} certificate(s); sha256={record['certificate_sha256']}")


if __name__ == '__main__':
    main()
