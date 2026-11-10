"""Exact verification of the finite computations in the manuscript.

The allocation and auxiliary computations of Section 4 are tied to the
tables extracted from v13, which are unchanged in the later revisions
recorded in data/source_manifest.json. The stages 'balanced' and 'base3'
were added for v19 and are implemented in separate modules.

Only Python's standard library is required. All acceptance tests use integers
or Fraction. Floating-point fields are supplementary displays. The input
witnesses and the three extracted manuscript tables are distributed with this
repository. Published primitive-prime results used for the universal order
bounds are stated in the repository documentation.
"""
from collections import Counter
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
import argparse
import hashlib
import json
from math import gcd, isqrt

ROOT = Path(__file__).resolve().parent.parent
PRIMARY = ROOT
OUT = ROOT / 'results'
if not __debug__:
    raise SystemExit('Run without -O: this checker uses assertions.')
TABLES_PATH = ROOT / 'data' / 'tables_v13.json'
MANIFEST_PATH = ROOT / 'data' / 'source_manifest.json'
TABLES = json.loads(TABLES_PATH.read_text(encoding='utf-8'))
MANIFEST = json.loads(MANIFEST_PATH.read_text(encoding='utf-8'))



def sieve(n):
    isprime = bytearray(b'\x01') * (n + 1)
    isprime[0:2] = b'\x00\x00'
    for p in range(2, isqrt(n) + 1):
        if isprime[p]:
            isprime[p * p:n + 1:p] = b'\x00' * ((n - p * p) // p + 1)
    return [p for p in range(2, n + 1) if isprime[p]]


PRIMES = sieve(1000000)


def prime_divisors(n):
    out = []
    for p in PRIMES:
        if p * p > n:
            break
        if n % p == 0:
            out.append(p)
            while n % p == 0:
                n //= p
    if n > 1:
        out.append(n)
    return out


def prove_prime_trial(n):
    assert n < 10 ** 12
    return n >= 2 and all(n % p != 0 for p in PRIMES if p * p <= n)


def has_order(q, d):
    return (pow(2, d, q) == 1
            and all(pow(2, d // ell, q) != 1 for ell in prime_divisors(d)))


GUARDS = {
    2: [tuple(row) for row in TABLES['binary_guards']['rows']],
    3: [tuple(row) for row in TABLES['ternary_guards']['rows']],
}
KROWS = [tuple(row) for row in TABLES['auxiliary_families']['rows']]
KTABLE = {i: {row[0]: row[i-1] for row in KROWS if row[i-1] is not None}
          for i in (2, 3)}


def validate_cases(cases):
    cases = tuple(cases)
    assert cases and len(set(cases)) == len(cases)
    assert all(i in (2, 3) for i in cases)
    return tuple(sorted(cases))


def validate_inputs():
    assert TABLES['schema_version'] == MANIFEST['schema_version'] == 1
    assert TABLES['manuscript_version'] == MANIFEST['manuscript']['version'] == 'v13'
    assert TABLES['manuscript_sha256'] == MANIFEST['manuscript']['sha256']
    for name, expected in MANIFEST['inputs'].items():
        data = (ROOT / name).read_bytes()
        assert len(data) == expected['bytes'], (name, 'input size')
        assert hashlib.sha256(data).hexdigest() == expected['sha256'], (
            name, 'input digest')
    assert GUARDS[2] == sorted(GUARDS[2]) and GUARDS[3] == sorted(GUARDS[3])
    assert KROWS == sorted(KROWS)


def metadata():
    validate_inputs()
    out = {'source': MANIFEST['manuscript']['filename'],
           'source_sha256': MANIFEST['manuscript']['sha256'],
           'source_tables': 'data/tables_v13.json'}
    for name in ['binary_cover_1440_full.json', 'ap_certificate.json',
                 'data/tables_v13.json']:
        data = (ROOT / name).read_bytes()
        out[name] = {'path': name, 'bytes': len(data),
                     'sha256': hashlib.sha256(data).hexdigest()}
    return out


def write_json(name, value):
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / name).write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')


def finite_checks(cases=(2, 3)):
    cases = validate_cases(cases)
    results = {'metadata': metadata()}
    for i, D, nh, reps, filename, target in [
        (2, 1440, 45, [32*c for c in range(23)],
         'binary_cover_1440_full.json', Fraction('2.081483')),
        (3, 1296, 8, [81*c for c in (1, 3, 5, 7)],
         'ap_certificate.json', Fraction('2.287407')),
    ]:
        if i not in cases:
            continue
        data = json.loads((PRIMARY / filename).read_text())
        assert data['period'] == D and data['denominator'] == 10 ** 12
        guards = GUARDS[i]
        assert len(guards) == (41 if i == 2 else 30)
        assert len({q for q, d, b in guards}) == len(guards)
        assert sorted((q, b) for q, d, b in guards) == sorted(
            map(tuple, data['guards']))
        for q, d, b in guards:
            assert prove_prime_trial(q), (i, q, 'not prime')
            assert D % d == 0 and has_order(q, d), (i, q, d, 'order')
            assert 0 <= b < q
        if i == 2:
            assert all(d & (d - 1) for q, d, b in guards)
        else:
            assert 3 not in {q for q, d, b in guards}
            pure_three = [(q, d) for q, d, b in guards
                          if set(prime_divisors(d)) == {3}]
            assert pure_three == [(71119, 81), (97685839, 81)]
            assert prove_prime_trial(2593) and has_order(2593, 81)
            assert 2593 not in {q for q, d, b in guards}
        ds = [g for g in range(1, D + 1) if D % g == 0]
        supply_numerator = Counter()
        for j in range(1, D + 1):
            supply_numerator[gcd(j, D)] += 2 if j % 8 == 4 else 1
        assert Fraction(sum(supply_numerator.values()), D) == Fraction(9, 8)
        denominator = 2 * data['denominator']
        full = {}
        seen = set()
        for h, g, u, n in data['allocation']:
            assert all(isinstance(v, int) for v in (h, g, u, n))
            assert h in reps and g in ds and 0 <= u < g and n >= 0
            assert (h, g, u) not in seen
            seen.add((h, g, u))
            full[h, g, u] = n * (2 if h == 0 else 1)
            if h:
                key = ((-h) % D, g, (u + (i - 1) * h) % g)
                assert key not in full
                full[key] = n
        capacity = Counter()
        for (h, g, u), n in full.items():
            capacity[g] += n
        for g in ds:
            assert D * capacity[g] <= denominator * supply_numerator[g], (
                i, g, 'capacity')
        hs = sorted(set(reps) | {(-h) % D for h in reps})
        assert len(hs) == nh
        survivors = {}
        for h in hs:
            alive = [True] * D
            for q, d, b in guards:
                v = pow(2, h, q)
                value = (1 + v + (v * v if i == 3 else 0)) % q
                for a in range(D):
                    if value == b:
                        alive[a] = False
                    value = (2 * value) % q
            survivors[h] = [a for a in range(D) if alive[a]]
        for h in hs:
            assert set(survivors[(-h) % D]) == {
                (a + (i - 1) * h) % D for a in survivors[h]}
        phases = []
        minimum = None
        min_pairs = []
        for h in hs:
            local = []
            for a in survivors[h]:
                total = sum(g * full.get((h, g, a % g), 0) for g in ds)
                gamma = Fraction(nh * total, denominator)
                assert gamma >= target, (i, h, a, str(gamma), 'coverage')
                local.append(gamma)
                if minimum is None or gamma < minimum:
                    minimum, min_pairs = gamma, [(h, a)]
                elif gamma == minimum:
                    min_pairs.append((h, a))
            phases.append({'h': h, 'survivors': len(local),
                           'min_gamma_exact': str(min(local)) if local else None,
                           'min_gamma_decimal': float(min(local)) if local else None})
        results[str(i)] = {
            'guard_count': len(guards),
            'order_and_primality_check': (
                'exact trial division and modular exponentiation passed'),
            'guard_checks': [{'q': q, 'order': d, 'residue': b,
                              'prime_by_complete_trial_division': True,
                              'power_at_order': pow(2, d, q),
                              'proper_order_witnesses': {str(ell): pow(2, d//ell, q)
                                                         for ell in prime_divisors(d)}}
                             for q, d, b in guards],
            'divisor_count': len(ds), 'representative_phases': reps,
            'allocation_entries': len(data['allocation']),
            'full_allocation_entries': len(full),
            'surviving_pairs_full': sum(map(len, survivors.values())),
            'capacities_checked': len(ds),
            'target_exact': str(target), 'min_gamma_exact': str(minimum),
            'min_gamma_decimal': float(minimum),
            'target_margin_exact': str(minimum - target), 'min_pairs': min_pairs,
            'capacities': [{'g': g, 'c_g': str(Fraction(supply_numerator[g], D)),
                            'used': str(Fraction(capacity[g], denominator)),
                            'slack': str(Fraction(supply_numerator[g], D)
                                         - Fraction(capacity[g], denominator))}
                           for g in ds],
            'phases': phases,
        }
        print('FINITE', i, 'guards', len(guards),
              'survivors', sum(map(len, survivors.values())),
              'minimum', str(minimum), 'decimal', float(minimum),
              'margin', str(minimum-target), flush=True)
    name = ('allocation_finite_exact.json' if cases == (2, 3) else
            'binary_cover_checks.json' if cases == (2,) else 'ap_cover_checks.json')
    write_json(name, results)
    return results


@lru_cache(None)
def cyclotomic_at_two(d):
    # Generic divisor recurrence, independent of the manuscript's special formulas.
    # All input d are at most 2*3^6*499, so exact integers are tractable.
    value = (1 << d) - 1
    divisors = set()
    for a in range(1, isqrt(d) + 1):
        if d % a == 0:
            divisors.add(a)
            divisors.add(d // a)
    for e in sorted(divisors):
        if e < d:
            value, rem = divmod(value, cyclotomic_at_two(e))
            assert rem == 0, (d, e)
    return value


def special_phi(r, j, e, i):
    if i == 2:
        return ((1 << r) - 1 if j == 0 else
                ((1 << (2 ** (j-1) * r)) + 1) // ((1 << (2 ** (j-1))) + 1))
    if j == 0:
        return ((1 << r) - 1 if e == 0 else ((1 << r) + 1) // 3)
    z = 1 << (3 ** (j-1))
    zr = pow(z, r)
    return ((zr*zr + zr + 1) // (z*z + z + 1) if e == 0 else
            (zr*zr - zr + 1) // (z*z - z + 1))


def count_order_lower(d, r, phi):
    remainder = phi
    exceptional = {}
    for p in (3, r):
        exponent = 0
        while remainder % p == 0:
            remainder //= p
            exponent += 1
        if exponent:
            exceptional[p] = exponent
    found = []
    for q in PRIMES:
        if q >= 10 ** 6:
            break
        if (q - 1) % d == 0 and remainder % q == 0:
            assert has_order(q, d), (q, d, 'nonprimitive counted')
            exponent = 0
            while remainder % q == 0:
                remainder //= q
                exponent += 1
            found.append([q, exponent])
    return {'d': d, 'small_distinct_primes': found, 'exceptional_removed': exceptional,
            'residual_bits': remainder.bit_length(),
            'residual_greater_than_one': remainder > 1,
            'lower_bound': len(found) + int(remainder > 1)}


def ternary_families(beta, nu, cap=2):
    @lru_cache(None)
    def recurse(j, b, n):
        if j == 0:
            return b + n // 2
        answer = 0
        pmax = n // 2 if cap is None else min(n // 2, cap)
        for p in range(pmax + 1):
            smax = b + p if cap is None else min(b + p, cap)
            for s in range(smax + 1):
                next_b = beta[j-1] + (b+p-s)//3
                next_n = nu[j-1] + (n-2*p+s)//3
                answer = max(answer, recurse(j-1, next_b, next_n))
        return answer
    return recurse(len(beta)-1, beta[-1], nu[-1])


def decimal_bounds(value, places=18):
    """Return a strict decimal enclosure, proved by rational comparisons."""
    scale = 10 ** places
    lower = value.numerator * scale // value.denominator
    upper = lower + 1
    if Fraction(lower, scale) == value:
        lower -= 1
    assert Fraction(lower, scale) < value < Fraction(upper, scale)
    def display(n):
        return f'{n // scale}.{n % scale:0{places}d}'
    return {'lower': display(lower), 'upper': display(upper)}


def tail_checks(cases=(2, 3)):
    cases = validate_cases(cases)
    results = {'metadata': metadata(), 'method': (
        'Independent generic divisor recurrence plus exact trial factor removal.')}
    full_comparison = []
    coefficients = {}
    all_primes_5000 = [p for p in PRIMES if p <= 5000]
    assert len(all_primes_5000) == 669
    for i in cases:
        rs = [r for r in all_primes_5000 if r >= (7 if i == 2 else 5)]
        assert len(rs) == (666 if i == 2 else 667)
        assert set(KTABLE[i]) == {r for r in rs if r <= 499}
        entries = []
        for r in rs:
            k = KTABLE[i][r] if r <= 499 else (2 if i == 2 else 1)
            assert 1 <= k <= (r-1)//2
            if r > 499:
                continue
            counts = []
            if i == 2:
                for j in range(9):
                    d = 2**j*r
                    phi = cyclotomic_at_two(d)
                    assert phi == special_phi(r, j, 0, i)
                    entry = count_order_lower(d, r, phi)
                    entry.update({'j': j, 'e': 0})
                    entry['lower_bound_used'] = max(
                        entry['lower_bound'], 2 if j == 2 else 1)
                    counts.append(entry)
                f = sum((Fraction(v['lower_bound_used'], 2**v['j'])
                         for v in counts), Fraction())
                available = f.numerator // f.denominator
            else:
                beta, nu = [], []
                for j in range(7):
                    for e in range(2):
                        d = 2**e*3**j*r
                        phi = cyclotomic_at_two(d)
                        assert phi == special_phi(r, j, e, i)
                        entry = count_order_lower(d, r, phi)
                        entry.update({'j': j, 'e': e})
                        entry['lower_bound_used'] = entry['lower_bound']
                        counts.append(entry)
                        (beta if e == 0 else nu).append(entry['lower_bound'])
                available = ternary_families(beta, nu)
                unrestricted = ternary_families(beta, nu, cap=None)
                assert unrestricted >= available
                assert unrestricted == available, (r, 'recursion difference')
                full_comparison.append({
                    'r': r, 'restricted': available, 'full': unrestricted})
            assert available >= k, (i, r, available, k, 'family count')
            entries.append({'r': r, 'table_k': k,
                            'certified_families': available, 'orders': counts})
            print('TAIL', i, r, 'K', available, 'target', k, flush=True)
        product = Fraction(1)
        for r in rs:
            k = KTABLE[i][r] if r <= 499 else (2 if i == 2 else 1)
            product *= 1 - Fraction(1, r) + Fraction(1, r-k)
        Z = Fraction('2.081483' if i == 2 else '2.287407')
        ptarget = Fraction('1.170314' if i == 2 else '1.331909')
        zptarget = Fraction('2.435990' if i == 2 else '3.046617')
        assert product > ptarget and Z*product > zptarget
        C = (Fraction(4) if i == 2 else Fraction(3, 2)) / (Z*product)
        ctarget = Fraction('1.642043' if i == 2 else '0.492350')
        assert C < ctarget, (i, 'final coefficient')
        coefficients[str(i)] = {
            'P_interval': decimal_bounds(product),
            'ZP_interval': decimal_bounds(Z*product),
            'C_exact': str(C),
            'C_interval': decimal_bounds(C),
            'C_target_exact': str(ctarget),
            'C_target_margin_exact': str(ctarget-C),
            'C_target_margin_interval': decimal_bounds(ctarget-C)}
        results[str(i)] = {'prime_index_count': len(rs),
                           'finite_rows_checked': len(entries),
                           'all_k_within_cap': True, 'P_exact': str(product),
                           'P_decimal': float(product),
                           'ZP_exact': str(Z*product), 'ZP_decimal': float(Z*product),
                           'P_target_margin_decimal': float(product-ptarget),
                           'ZP_target_margin_decimal': float(Z*product-zptarget),
                           'entries': entries}
        print('PRODUCT', i, float(product), 'ZP', float(Z*product), flush=True)
    name = ('allocation_tail_exact.json' if cases == (2, 3) else
            'binary_tail_checks.json' if cases == (2,) else 'ap_tail_checks.json')
    write_json(name, results)
    assert len(full_comparison) == (93 if 3 in cases else 0)
    if 3 in cases:
        write_json('full_recursion_comparison.json', full_comparison)
    coefficient_name = ('coefficient_checks.json' if cases == (2, 3) else
                        'binary_coefficient_checks.json' if cases == (2,) else
                        'ap_coefficient_checks.json')
    write_json(coefficient_name, coefficients)
    for i, row in coefficients.items():
        print('COEFFICIENT', i, row['C_interval'], flush=True)
    if 3 in cases:
        print('FULL_RECURSION', len(full_comparison), 'all equal', flush=True)
    return results


def main(default_stage='all', cases=(2, 3), allow_stage=True):
    global OUT
    parser = argparse.ArgumentParser(
        description='Exact finite verification for A prime and powers of fixed bases.')
    if allow_stage:
        parser.add_argument('stage', choices=['finite', 'tail', 'intro',
                                              'balanced', 'base3', 'all'],
                            default=default_stage, nargs='?')
    parser.add_argument('--output-dir', type=Path, default=OUT,
                        help='output directory (default: results/ in this repository)')
    args = parser.parse_args()
    OUT = args.output_dir.resolve()
    stage = args.stage if allow_stage else default_stage
    validate_inputs()
    if stage in ('finite', 'all'):
        finite_checks(cases)
    if stage in ('tail', 'all'):
        tail_checks(cases)
    if stage in ('intro', 'all'):
        from scripts.introductory_checks import run_checks
        run_checks(OUT)
    if stage in ('balanced', 'all'):
        from scripts.balanced_sieve import run_checks as balanced_checks
        balanced_checks(OUT)
    if stage in ('base3', 'all'):
        from scripts.base3_minimality import run_checks as base3_checks
        base3_checks(OUT)
    print('SUCCESS', flush=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
