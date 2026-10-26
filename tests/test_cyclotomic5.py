"""Independent polynomial-division/determinant oracle for exact native algebra.

The finite transcript checks arithmetic, not discovery territory. --verify
replays an existing receipt without executing Mojo or replacing measurements.
"""
import argparse
from hashlib import sha256
from itertools import permutations, product
import json
import os
from pathlib import Path
import subprocess
import time

ROOT = Path(__file__).resolve().parents[1]
ZERO = (0, 0, 0, 0)
ONE = (1, 0, 0, 0)
PIN = 'c5b2d3d7879bcf2354d4d9784bd20a6b3dc610fd'
SOURCES = ('algebra/cyclotomic5.mojo', 'algebra/cyclotomic5_probe.mojo',
           'tests/test_cyclotomic5.py', 'scripts/run_mojo.sh', 'pixi.toml', 'pixi.lock')


def canonical(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'))+'\n').encode()


def digest(data):
    return sha256(data).hexdigest()


def reduce_polynomial(coefficients):
    """Monic long division by X^4+X^3+X^2+X+1 (not cyclic folding)."""
    out = list(coefficients)+[0]*max(0, 4-len(coefficients))
    for degree in range(len(out)-1, 3, -1):
        leading = out[degree]
        for j in range(5):
            out[degree-4+j] -= leading
    assert all(v == 0 for v in out[4:])
    return tuple(out[:4])


def mul(x, y):
    out = [0]*7
    for i, a in enumerate(x):
        for j, b in enumerate(y):
            out[i+j] += a*b
    return reduce_polynomial(out)


def automorphism(x, k):
    out = [0]*(3*k+1)
    for i, a in enumerate(x):
        out[i*k] += a
    return reduce_polynomial(out)


def determinant(matrix):
    """Leibniz determinant: 24 signed products, no numeric linear algebra."""
    total = 0
    for p in permutations(range(4)):
        inversions = sum(p[i] > p[j] for i in range(4) for j in range(i+1, 4))
        term = (-1)**inversions
        for i in range(4):
            term *= matrix[i][p[i]]
        total += term
    return total


def norm(x):
    columns = [mul(x, tuple(int(i == j) for i in range(4))) for j in range(4)]
    return determinant([[columns[j][i] for j in range(4)] for i in range(4)])


def phi5(x, y):
    return sum(x**(4-i)*y**i for i in range(5))


def vector(i):
    return tuple((i//3**k) % 3-1 for k in range(4))


def reference_transcript():
    rows = ['DOMAIN E5-CYCLOTOMIC5-v1 81 81 4 16']
    def emit(label, i, j, x):
        rows.append(' '.join(map(str, (label, i, j, *x))))
    for i in range(81):
        x = vector(i)
        for j in range(81):
            y = vector(j)
            emit('ADD', i, j, tuple(a+b for a, b in zip(x, y)))
            emit('SUB', i, j, tuple(a-b for a, b in zip(x, y)))
            emit('MUL', i, j, mul(x, y))
        for k in range(1, 5):
            emit('AUTO', i, k, automorphism(x, k))
        rows.append(f'NORM {i} {norm(x)}')
    big = (1, -1, 1, -1)
    for i in range(16):
        big = mul(big, (10**9, 1, -1, 2))
        emit('BIG', i, 0, big)
        rows.append(f'BIGNORM {i} {norm(big)}')
    for i, (x, y) in enumerate(zip(
            (0, 1, -1, 144, 14132, 85359, 1956878, 2760001),
            (0, 1, 2, 133, 14068, 85282, 1956213, 2759745))):
        rows.append(f'DIFFNORM {i} {x} {y} {phi5(x, y)}')
        rows.append(f'SUMNORM {i} {x} {y} {phi5(x, -y)}')
    rows += ['REJECTED 4', 'END E5-CYCLOTOMIC5-v1']
    return ('\n'.join(rows)+'\n').encode()


def algebra_checks():
    basis = [tuple(int(i == j) for i in range(4)) for j in range(4)]
    # Bilinearity plus these basis triples establishes the structure constants'
    # associativity over all integers; this does not prove Mojo's lowering.
    for x, y, z in product(basis, repeat=3):
        assert mul(mul(x, y), z) == mul(x, mul(y, z))
    z = basis[1]
    powers = [ONE]
    for _ in range(5):
        powers.append(mul(powers[-1], z))
    assert powers[5] == ONE
    assert tuple(map(sum, zip(*powers[:5]))) == ZERO
    assert norm(tuple(a-b for a, b in zip(ONE, z))) == 5
    assert norm(ONE) == 1 and norm(ZERO) == 0
    for i in range(81):
        x = vector(i)
        conjugate_product = ONE
        for k in range(1, 5):
            conjugate_product = mul(conjugate_product, automorphism(x, k))
            for l in range(1, 5):
                assert automorphism(automorphism(x, k), l) == automorphism(x, k*l % 5)
        assert conjugate_product == (norm(x), 0, 0, 0)
    for k in range(1, 5):
        for x, y in product(basis, repeat=2):
            assert automorphism(mul(x, y), k) == mul(automorphism(x, k), automorphism(y, k))
    for x, y in product(range(-75, 76), repeat=2):
        q = phi5(x, y)
        assert x**5-y**5 == (x-y)*q
        assert x**5+y**5 == (x+y)*phi5(x, -y)
        assert q == (x-y)*(x**3+2*x*x*y+3*x*y*y+4*y**3)+5*y**4
        if (x-y) % 5 == 0:
            assert q % 25 == (5*y**4) % 25
            if y % 5:
                assert q % 25 == 5
    # A norm condition on fixed (e,d) cannot by itself select a candidate (a,c).
    # No filter from this module is wired into a discovery controller.


def source_hashes():
    return {name: digest((ROOT/name).read_bytes()) for name in SOURCES}


def validate_receipt(folder, expected):
    receipt = json.loads((folder/'accepted.json').read_text())
    assert receipt['schema'] == 'E5-CYCLOTOMIC5-CONFORMANCE-v1'
    assert receipt['classification'] == 'algebra_conformance_only'
    assert receipt['finite_math_kernels_sha'] == PIN
    assert receipt['source_sha256'] == source_hashes()
    assert receipt['scope'] == scope()
    raw = (folder/'native.txt').read_bytes()
    assert raw == expected
    assert receipt['transcript_sha256'] == digest(raw)
    resource = (folder/'native-resource.json').read_bytes()
    assert receipt['resource_sha256'] == digest(resource)
    assert receipt['native_resources'] == json.loads(resource)
    assert receipt['transcript_rows'] == len(raw.splitlines())
    assert set(p.name for p in folder.iterdir()) == {'accepted.json', 'native.txt', 'native-resource.json'}
    return receipt


def scope():
    return dict(coefficient_box=[-1, 1], elements=81, ordered_pairs=6561,
                pair_operations=['add', 'sub', 'mul'], automorphisms=[1, 2, 3, 4],
                large_multiplications=16, scalar_norm_pairs=8,
                invalid_input_controls=4, discovery_trials=0)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--python-only', action='store_true')
    parser.add_argument('--output', type=Path)
    parser.add_argument('--verify', action='store_true')
    args = parser.parse_args()
    started = time.perf_counter_ns()
    algebra_checks()
    expected = reference_transcript()
    replay_ns = time.perf_counter_ns()-started
    if args.python_only:
        assert not args.verify and args.output is None
        print(f'Python exact algebra checks passed; {len(expected.splitlines())} expected rows; no native acceptance.')
        return
    if args.output is None:
        parser.error('--output is required for native acceptance or replay')
    folder = args.output.resolve()
    if args.verify:
        validate_receipt(folder, expected)
        print(f'Independent polynomial-division/determinant replay accepted; {replay_ns} ns; no discovery territory.')
        return
    folder.mkdir(parents=True, exist_ok=False)
    resource = folder/'native-resource.json'
    command = ['/usr/bin/time', '-f',
               '{"wall_seconds":%e,"user_seconds":%U,"system_seconds":%S,"max_rss_kib":%M}',
               '-o', str(resource), 'bash', 'scripts/run_mojo.sh', '-I', 'algebra', 'algebra/cyclotomic5_probe.mojo']
    started = time.perf_counter_ns()
    result = subprocess.run(command, cwd=ROOT, capture_output=True, timeout=300)
    native_ns = time.perf_counter_ns()-started
    (folder/'native.txt').write_bytes(result.stdout)
    assert result.returncode == 0, result.stderr.decode()
    assert result.stdout == expected, 'Native arithmetic differs from the independent oracle'
    # A second regeneration is independent of native arithmetic and catches
    # mismatched raw byte order, missing/extra rows, and scalar norm failures.
    replay_started = time.perf_counter_ns()
    assert (folder/'native.txt').read_bytes() == reference_transcript()
    second_replay_ns = time.perf_counter_ns()-replay_started
    receipt = dict(schema='E5-CYCLOTOMIC5-CONFORMANCE-v1', classification='algebra_conformance_only',
                   source_sha256=source_hashes(), finite_math_kernels_sha=PIN,
                   source_commit=os.environ.get('GITHUB_SHA'), github_run_id=os.environ.get('GITHUB_RUN_ID'),
                   scope=scope(), transcript_sha256=digest(result.stdout),
                   transcript_rows=len(result.stdout.splitlines()),
                   resource_sha256=digest(resource.read_bytes()), native_resources=json.loads(resource.read_bytes()),
                   native_invocation_ns=native_ns, initial_python_ns=replay_ns,
                   second_python_replay_ns=second_replay_ns)
    (folder/'accepted.json').write_bytes(canonical(receipt))
    validate_receipt(folder, expected)
    print(json.dumps(receipt, sort_keys=True))


if __name__ == '__main__':
    main()
