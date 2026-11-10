#!/usr/bin/env python3
"""Exact candidate factorizations and finite residue checks for v13.

The base-three candidate is checked; its minimality is not tested.
"""
from math import gcd, isqrt, prod
from pathlib import Path
import json

if not __debug__:
    raise SystemExit('Run without -O: this checker uses assertions.')


def is_prime(n):
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    return all(n % d for d in range(3, isqrt(n) + 1, 2))


def factor(n):
    """Complete trial division, with independent primality checks."""
    assert n >= 2
    remainder, d = n, 2
    factors = []
    while d * d <= remainder:
        exponent = 0
        while remainder % d == 0:
            remainder //= d
            exponent += 1
        if exponent:
            factors.append([d, exponent])
        d = 3 if d == 2 else d + 2
    if remainder > 1:
        factors.append([remainder, 1])
    assert all(is_prime(p) and e >= 1 for p, e in factors)
    assert len({p for p, e in factors}) == len(factors)
    assert prod(p ** e for p, e in factors) == n
    return factors


def order(a, modulus):
    assert gcd(a, modulus) == 1
    residue = 1
    for d in range(1, modulus + 1):
        residue = residue * a % modulus
        if residue == 1:
            return d
    raise AssertionError('A unit must have finite order below the modulus.')


def residue_pairs(q1, q2, modulus, b):
    d1, d2 = order(q1, modulus), order(q2, modulus)
    return [[i, l, (b - pow(q1, i, modulus)
                    - pow(q2, l, modulus)) % modulus]
            for i in range(1, d1 + 1) for l in range(1, d2 + 1)]


def run_checks(output_dir):
    # Base-3 candidate: exponent symmetry reduces the enumeration to a <= b.
    N = 118514161
    assert N % 2 == 1 and gcd(N, 3) == 1
    assert 3 ** 16 < N < 3 ** 17
    factorizations = []
    for a in range(17):
        for b in range(a, 17):
            difference = N - 3 ** a - 3 ** b
            assert difference >= 2
            factors = factor(difference)
            assert len(factors) >= 2, (a, b, 'prime-power difference')
            factorizations.append({
                'a': a, 'b': b, 'difference': difference,
                'factorization': factors})
    assert len(factorizations) == 17 * 18 // 2 == 153

    # Odd residue classes modulo 600 for the two distinct bases.
    assert all(is_prime(q) for q in (17, 19, 599, 601))
    periods_600 = [order(q, 600) for q in (599, 601)]
    assert periods_600 == [2, 1]
    prime_divisors_600 = {p for p, e in factor(600)}
    assert prime_divisors_600 == {2, 3, 5}
    rows = []
    for b in range(1, 600, 2):
        residues = [w for i, l, w in residue_pairs(599, 601, 600, b)]
        assert residues == [b, (b - 2) % 600]
        rows.append({
            'b': b, 'w': residues,
            'coprime': any(gcd(w, 600) == 1 for w in residues),
            'J': sum(w in prime_divisors_600 for w in residues)})
    empty = [row['b'] for row in rows
             if not row['coprime'] and row['J'] == 0]
    sparse = [row['b'] for row in rows
              if not row['coprime'] and row['J'] > 0]
    coprime_count = sum(row['coprime'] for row in rows)
    assert len(empty) == 39 and sparse == [5] and coprime_count == 260
    assert empty == [b for b in range(1, 600, 2)
                     if b % 15 in (5, 12) and b != 5]
    assert next(row['J'] for row in rows if row['b'] == 5) == 2

    # The progression 57 modulo 60 has no possible prime residue.
    periods_60 = [order(q, 60) for q in (599, 601)]
    assert periods_60 == [2, 1]
    residues_60 = [w for i, l, w in residue_pairs(599, 601, 60, 57)]
    assert residues_60 == [57, 55]
    divisors_60 = {p for p, e in factor(60)}
    assert all(gcd(w, 60) > 1 for w in residues_60)
    assert all(w not in divisors_60 for w in residues_60)

    # The other pair has coprime residues in the same progression.
    periods_17_19 = [order(q, 60) for q in (17, 19)]
    assert periods_17_19 == [4, 2]
    witnesses = [row for row in residue_pairs(17, 19, 60, 57)
                 if gcd(row[2], 60) == 1]
    assert witnesses == [[2, 1, 49], [2, 2, 7], [4, 1, 37]]
    assert (57 - 17 ** 2 - 19) % 60 == 49 and gcd(49, 60) == 1

    result = {
        'congruence_classes': rows,
        'classes_empty': len(empty),
        'classes_sparse': len(sparse),
        'classes_positive_density_subject_to_theorem': coprime_count,
        '17_19_periods': periods_17_19,
        '17_19_coprime_witnesses': witnesses,
        'base3_candidate': N,
        'base3_candidate_pairs_checked': len(factorizations),
        'base3_factorizations': factorizations,
        'base3_minimality_checked': False,
        '599_601_periods_mod600': periods_600,
        'empty_classes_mod600': empty,
        'sparse_classes_mod600': sparse,
        '599_601_class57_mod60': {
            'periods': periods_60, 'w': residues_60,
            'gcds': [gcd(w, 60) for w in residues_60],
            'J': 0, 'empty': True}}
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / 'intro_checks.json'
    path.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print('BASE3', N, len(factorizations), 'complete factorizations passed')
    print('MOD600', len(empty), 'empty;', len(sparse),
          'sparse with J_5=2;', coprime_count, 'coprime')
    print('MOD60 class57: 599/601 empty; 17/19 witness 49 is coprime')
    print('MINIMALITY not checked')
    return result
