"""Counts of odd integers p + q1^j + q2^k (Table 5 of v20).

For a pair (q1, q2) of odd primes let R(q1, q2) be the set of the integers
p + q1^j + q2^k with p prime and j, k >= 1. For an odd integer n the prime
p is odd. The program counts the odd n <= x in R(q1, q2), in R(q1', q2')
and in both, for the pairs

    (5, 13) and (7, 11),        (17, 19) and (599, 601),

and for x = 10^7 and x = 10^8.

The odd primes up to x are found by the sieve of Eratosthenes and stored
as the bits of one integer, bit i standing for 2i + 1. Adding the odd
integer q1^j gives the even integer 2(i + (q1^j - 1)/2) + 2, and adding
q2^k gives the odd integer 2(i + (q1^j - 1)/2 + (q2^k + 1)/2) + 1. Thus
both additions are shifts of the bit set.

These counts are numerical data. No proof in the manuscript depends on
them. Only the standard library is used. Run without -O.
"""
from pathlib import Path
import json

from scripts.base3_minimality import odd_prime_mask

if not __debug__:
    raise SystemExit('Run without -O: this checker uses assertions.')

COMPARISONS = (((5, 13), (7, 11)), ((17, 19), (599, 601)))
LIMITS = (10 ** 7, 10 ** 8)
# (first pair, second pair, x): (first, second, both), as printed in Table 5.
TABLE = {
    ((5, 13), (7, 11), 10 ** 7): (4954168, 4952973, 4907845),
    ((5, 13), (7, 11), 10 ** 8): (49707637, 49714155, 49424567),
    ((17, 19), (599, 601), 10 ** 7): (4675126, 2081335, 1964132),
    ((17, 19), (599, 601), 10 ** 8): (47887149, 19044487, 18302829),
}


def popcount(mask):
    """Number of bits equal to 1 (int.bit_count needs Python 3.10)."""
    if hasattr(int, 'bit_count'):
        return mask.bit_count()
    return bin(mask).count('1')


def powers(base, limit):
    value = base
    while value <= limit:
        yield value
        value *= base


def represented(primes, q1, q2, limit):
    """Bit i is 1 exactly when 2i + 1 <= limit is p + q1^j + q2^k."""
    size = (limit + 1) // 2
    mask = (1 << size) - 1
    # Bit i of `even` stands for the even integer 2i + 2 = p + q1^j.
    even = 0
    for power in powers(q1, limit):
        even |= (primes << (power // 2)) & mask
    result = 0
    for power in powers(q2, limit):
        result |= (even << ((power + 1) // 2)) & mask
    return result


def count(limit):
    primes = odd_prime_mask(limit)
    rows = []
    for first, second in COMPARISONS:
        a = represented(primes, *first, limit)
        b = represented(primes, *second, limit)
        rows.append((first, second, limit,
                     (popcount(a), popcount(b), popcount(a & b))))
    return rows


def run_checks(output_dir):
    rows = []
    for limit in LIMITS:
        for first, second, x, counts in count(limit):
            assert counts == TABLE[(first, second, x)], (first, second, x)
            rows.append({
                'first_pair': list(first), 'second_pair': list(second),
                'x': x, 'odd_integers_up_to_x': (x + 1) // 2,
                'in_first': counts[0], 'in_second': counts[1],
                'in_both': counts[2]})
    result = {'manuscript_statement': 'Table 5', 'rows': rows}
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / 'odd_sum_counts.json').write_text(
        json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print('ODD SUMS', len(rows), 'rows of counts agree with the table',
          flush=True)
    return result
