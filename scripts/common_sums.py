"""Common sums for two pairs of bases (Proposition 7.1 of v20).

For odd primes q1 != q2 let A(q1, q2) be the set of the integers
q1^j + q2^k with j, k >= 1. The program proves that

    A(5, 13) and A(7, 11) have the single common element 18,
    A(17, 19) and A(599, 601) are disjoint,

by three congruences. For a modulus m and a power g^v restricted to
v >= v0, the program checks g^(v0+T) = g^v0 (mod m). Then g^(v+T) = g^v
(mod m) for all v >= v0, so the residues of these powers are those with
v0 <= v < v0 + T. It forms the sets of residues of the two sides of each
equation and checks that they are disjoint.

  m = 2978325:  5^j + 13^k (j >= 2)  against  7^a + 11^b
  m = 132665:   5 + 13^k   (k >= 2)  against  7^a + 11^b
  m = 731120:   17^j + 19^k          against  599^a + 601^b

The first two rows leave j = k = 1, that is 5 + 13 = 18, and
7^a + 11^b = 18 only for a = b = 1.

Only the standard library is used. Run without -O.
"""
from pathlib import Path
import json

if not __debug__:
    raise SystemExit('Run without -O: this checker uses assertions.')

# (modulus, period T, (base, least exponent) for the four terms, expected
# sizes of the left set, the right set and their intersection). A least
# exponent None denotes the constant term equal to the base.
ROWS = [
    (2_978_325, 60, ((5, 2), (13, 1), (7, 1), (11, 1)), (1800, 3600, 0)),
    (132_665, 156, ((5, None), (13, 2), (7, 1), (11, 1)), (12, 21561, 0)),
    (731_120, 36, ((17, 1), (19, 1), (599, 1), (601, 1)), (1296, 324, 0)),
]


def residues(base, start, period, modulus):
    """Residues modulo modulus of base^v for all v >= start."""
    assert pow(base, start + period, modulus) == pow(base, start, modulus), (
        base, start, period, modulus, 'the stated period does not hold')
    return {pow(base, v, modulus) for v in range(start, start + period)}


def sumset(first, second, modulus):
    return {(x + y) % modulus for x in first for y in second}


def run_checks(output_dir):
    rows = []
    for modulus, period, terms, expected in ROWS:
        sets = [{base % modulus} if start is None
                else residues(base, start, period, modulus)
                for base, start in terms]
        left = sumset(sets[0], sets[1], modulus)
        right = sumset(sets[2], sets[3], modulus)
        sizes = (len(left), len(right), len(left & right))
        assert sizes == expected, (modulus, sizes)
        rows.append({
            'modulus': modulus, 'period': period,
            'terms': [{'base': base, 'least_exponent': start}
                      for base, start in terms],
            'left_residues': sizes[0], 'right_residues': sizes[1],
            'common_residues': sizes[2]})
    # The remaining case j = k = 1 of the first comparison.
    assert 5 + 13 == 18 == 7 + 11
    assert [(a, b) for a in range(1, 3) for b in range(1, 3)
            if 7 ** a + 11 ** b == 18] == [(1, 1)]
    assert 7 ** 2 > 18 and 11 ** 2 > 18
    result = {
        'manuscript_statement': 'Proposition 7.1',
        'rows': rows,
        'common_elements_5_13_and_7_11': [18],
        'common_elements_17_19_and_599_601': [],
    }
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / 'common_sums.json').write_text(
        json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print('COMMON SUMS', len(rows), 'congruences; residue sets disjoint',
          flush=True)
    return result
