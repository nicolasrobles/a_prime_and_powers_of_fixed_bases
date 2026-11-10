"""The least base-three exception (Theorem 1.5 and Section 6.2 of v19).

Let N = 118514161. The program checks, in integer arithmetic:

 1. N is odd and coprime to 3, and for all 0 <= a <= b <= 16 the integer
    N - 3^a - 3^b is positive and has at least two distinct prime factors
    (complete trial division). Since 3^16 < N < 3^17, the integer N is not
    of the form p^k + 3^a + 3^b with p prime, k >= 1 and a, b >= 0.

 2. Every odd integer n coprime to 3 with 10 < n < N is of the form
    p + 3^a + 3^b with p an odd prime and 1 <= a <= b <= 16.

For the second check the odd primes up to N are found by the sieve of
Eratosthenes and stored as the bits of one integer, bit j standing for the
odd integer 2j + 1. Adding the even integer 3^a + 3^b is a shift by
(3^a + 3^b) / 2 bits. The union of the 136 shifted copies is compared with
the set of the odd integers coprime to 3 in (10, N].

Only the standard library is used. Memory use depends on the Python version
and the machine; about 150 MB were measured. Run without -O.
"""
from math import isqrt
from pathlib import Path
import json

if not __debug__:
    raise SystemExit('Run without -O: this checker uses assertions.')

N = 118_514_161


def distinct_prime_factors(n):
    """Distinct prime factors of n >= 2, by complete trial division."""
    out, d = [], 2
    while d * d <= n:
        if n % d == 0:
            out.append(d)
            while n % d == 0:
                n //= d
        d = 3 if d == 2 else d + 2
    if n > 1:
        out.append(n)
    return out


def check_candidate():
    assert N % 2 == 1 and N % 3 != 0
    assert 3 ** 16 < N < 3 ** 17
    pairs, least = 0, N
    for a in range(17):
        for b in range(a, 17):
            difference = N - 3 ** a - 3 ** b
            assert difference >= 2
            assert len(distinct_prime_factors(difference)) >= 2, (a, b)
            least = min(least, difference)
            pairs += 1
    assert pairs == 153 and least == N - 2 * 3 ** 16 == 32_420_719
    return pairs


def odd_prime_mask(limit):
    """Integer whose bit j is 1 exactly when 2j + 1 <= limit is an odd prime."""
    length = (limit + 1) // 2
    flags = bytearray([1]) * length
    flags[0] = 0                      # the integer 1 is not a prime
    for p in range(3, isqrt(limit) + 1, 2):
        if flags[p // 2]:
            first = p * p // 2
            flags[first::p] = bytes((length - 1 - first) // p + 1)
    return sum(int.from_bytes(flags[j::8], 'little') << j for j in range(8))


def check_minimality():
    length = (N + 1) // 2             # bits 0 .. (N-1)/2
    primes = odd_prime_mask(N)
    powers = [3 ** a for a in range(1, 17)]        # positive exponents only
    assert powers[-1] < N < 3 * powers[-1]
    represented, translates = 0, 0
    for i, larger in enumerate(powers):
        for smaller in powers[:i + 1]:
            shift = (smaller + larger) // 2        # 3^a + 3^b is even
            assert shift < length
            represented |= primes << shift
            translates += 1
    block = sum(1 << j for j in range(24) if (2 * j + 1) % 3 != 0)
    coprime_to_three = int.from_bytes(
        block.to_bytes(3, 'little') * ((length + 23) // 24), 'little')
    # Bits 0..4 stand for 1, 3, 5, 7, 9; the condition is n > 10.
    eligible = coprime_to_three & ((1 << length) - 1) & ~31
    missing = eligible & ~represented
    assert missing == 1 << (N // 2), 'N is the only integer not represented'
    eligible_below = bin(eligible).count('1') - 1
    assert eligible_below == 39_504_717
    return translates, eligible_below


def run_checks(output_dir):
    pairs = check_candidate()
    translates, eligible_below = check_minimality()
    assert translates == 136
    result = {
        'manuscript_statement': 'Theorem 1.5',
        'candidate': N,
        'candidate_differences_checked': pairs,
        'candidate_exponents': 'nonnegative',
        'candidate_excludes': 'prime powers p^k with k >= 1',
        'smaller_integers': 'odd, coprime to 3, 10 < n < candidate',
        'smaller_integers_count': eligible_below,
        'smaller_integers_summand': 'prime',
        'smaller_integers_exponents': 'positive',
        'translates': translates,
        'smaller_integers_not_represented': 0,
        'candidate_represented': False,
        'minimality_checked': True,
    }
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / 'base3_minimality.json').write_text(
        json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print('BASE3 minimality', N, eligible_below,
          'smaller integers represented', flush=True)
    return result
