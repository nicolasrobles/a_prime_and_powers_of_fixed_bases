"""The density bound for the balanced-triple sieve (Lemma 5.1).

For a prime q >= 5 write ord_q(2) = 3^alpha * e with 3 not dividing e. The
set K consists of the primes 5 <= q <= 50000 such that

  (a) e / gcd(e, 80) is 1 or a prime v with 7 <= v <= 317, and
  (b) q divides 1 + 2^h1 + 2^h2 for some h1, h2 >= 0 divisible by 3^alpha.

Let N0 = 80 * (product of the primes 7 <= v <= 317). For h1, h2 divisible by
81 the classes of h1, h2 modulo N0 determine whether 1 + 2^h1 + 2^h2 is
divisible by 3 or by a prime of K. The density of the pairs of classes for
which it is not is denoted by rho. The program determines K and proves

    rho <= 1623190827888387 / 6400000000000000 < 0.253624.

By the Chinese remainder theorem,

    rho = 80^(-2) * sum over (a0, b0) of prod over v of N_v(a0, b0) / v^2,

where (a0, b0) runs over the pairs of classes modulo 80 that are not both
even, v runs over 1 and the primes 7 <= v <= 317, and N_v(a0, b0) is the
number of pairs of classes modulo v not excluded by a prime q of K with
e_q / gcd(e_q, 80) = v. The upper bound is obtained with integers scaled by
10^12, rounding upwards after each factor. The exact value of the right side
is also computed with Fraction and compared with the bound.

Only the standard library is used. Run without -O.
"""
from collections import defaultdict
from fractions import Fraction
from math import gcd, isqrt
from pathlib import Path
import json

if not __debug__:
    raise SystemExit('Run without -O: this checker uses assertions.')

BASE = 80
LIMIT = 50000
MAX_EXTRA_PRIME = 317
SCALE = 10 ** 12
EXPECTED_BOUND = Fraction(1623190827888387, 6400000000000000)
STATED_BOUND = Fraction(253624, 10 ** 6)


def popcount(mask):
    """Number of bits equal to 1 (int.bit_count needs Python 3.10)."""
    if hasattr(int, 'bit_count'):
        return mask.bit_count()
    return bin(mask).count('1')


def eratosthenes(limit):
    table = bytearray([1]) * (limit + 1)
    table[:2] = b'\0\0'
    for i in range(2, isqrt(limit) + 1):
        if table[i]:
            table[i * i::i] = bytes(len(table[i * i::i]))
    return table


def order_of_two(q):
    """Multiplicative order of 2 modulo the odd prime q.

    The order divides q - 1. Starting from q - 1, each prime factor p of
    q - 1 is removed as long as 2^(order / p) is still 1 modulo q.
    """
    order = remaining = q - 1
    p = 2
    while p * p <= remaining:
        if remaining % p == 0:
            while remaining % p == 0:
                remaining //= p
            while order % p == 0 and pow(2, order // p, q) == 1:
                order //= p
        p += 1
    if remaining > 1:
        while order % remaining == 0 and pow(2, order // remaining, q) == 1:
            order //= remaining
    assert pow(2, order, q) == 1
    return order


def local_data(q, primes):
    """Return (alpha, e, g, v, solutions) if q satisfies (a), else None.

    solutions lists the pairs (i, k) of classes modulo e with
    1 + zeta^i + zeta^k = 0 (mod q), where zeta = 2^h has order e and
    h is divisible by 3^alpha and congruent to 1 modulo e.
    """
    order = order_of_two(q)
    e, alpha = order, 0
    while e % 3 == 0:
        e //= 3
        alpha += 1
    g = gcd(e, BASE)
    v = e // g
    if v != 1 and (v > MAX_EXTRA_PRIME or not primes[v] or gcd(v, BASE) != 1):
        return None
    three_part = 3 ** alpha
    h = 0 if e == 1 else three_part * pow(three_part, -1, e)
    assert h % three_part == 0 and h % e == 1 % e
    zeta = pow(2, h, q)
    index = {}
    value = 1
    for i in range(e):
        index[value] = i
        value = value * zeta % q
    assert value == 1 and len(index) == e, 'zeta has order e'
    solutions = [(i, index[(-1 - x) % q]) for x, i in index.items()
                 if (-1 - x) % q in index]
    for i, k in solutions:
        assert (1 + pow(zeta, i, q) + pow(zeta, k, q)) % q == 0
    return alpha, e, g, v, solutions


def compute():
    primes = eratosthenes(LIMIT)
    groups = defaultdict(list)
    selected, condition_a, max_alpha = [], 0, 0
    for q in range(5, LIMIT + 1, 2):
        if not primes[q]:
            continue
        data = local_data(q, primes)
        if data is None:
            continue
        condition_a += 1
        alpha, e, g, v, solutions = data
        if solutions:
            selected.append(q)
            max_alpha = max(max_alpha, alpha)
            groups[v].append((g, solutions))

    # Bit k = b0 * BASE + a0 of the arrays below refers to the pair (a0, b0)
    # of classes modulo BASE. Pairs with a0 and b0 both even are excluded by
    # the prime 3.
    upper = [SCALE * int(bool((a0 | b0) & 1))
             for b0 in range(BASE) for a0 in range(BASE)]
    # Exact numerators over the common denominator prod v^2.
    exact = [int(bool((a0 | b0) & 1))
             for b0 in range(BASE) for a0 in range(BASE)]
    common_denominator = 1
    for v, group in sorted(groups.items()):
        masks = [0] * (BASE * BASE)
        for g, solutions in group:
            for i, k in solutions:
                bit = 1 << ((k % v) * v + (i % v))
                for b0 in range(k % g, BASE, g):
                    for a0 in range(i % g, BASE, g):
                        masks[b0 * BASE + a0] |= bit
        choices = v * v
        common_denominator *= choices
        for cell, mask in enumerate(masks):
            if not mask:
                exact[cell] *= choices
                continue
            allowed = choices - popcount(mask)
            exact[cell] *= allowed
            # Upward rounding after every factor.
            upper[cell] = (upper[cell] * allowed + choices - 1) // choices
    bound = Fraction(sum(upper), BASE ** 2 * SCALE)
    rho = Fraction(sum(exact), BASE ** 2 * common_denominator)
    surviving_base_cells = sum(1 for x in exact if x)
    return {
        'selected': selected,
        'condition_a': condition_a,
        'max_alpha': max_alpha,
        'groups': sorted(groups),
        'surviving_base_cells': surviving_base_cells,
        'bound': bound,
        'rho': rho,
    }


def decimal_floor(x, digits):
    """The decimal expansion of x >= 0 truncated to the given digits."""
    scaled = x.numerator * 10 ** digits // x.denominator
    text = str(scaled).rjust(digits + 1, '0')
    return text[:-digits] + '.' + text[-digits:]


def run_checks(output_dir):
    data = compute()
    bound, rho = data['bound'], data['rho']
    assert len(data['selected']) == 626
    assert data['max_alpha'] == 4, 'exponents divisible by 81 suffice'
    assert data['groups'][0] == 1 and len(data['groups']) == 64
    assert all(7 <= v <= MAX_EXTRA_PRIME for v in data['groups'][1:])
    assert bound == EXPECTED_BOUND
    assert 0 < rho <= bound < STATED_BOUND
    # sqrt(2 rho) < 0.712214 < 5/7
    assert 2 * STATED_BOUND < Fraction(712214, 10 ** 6) ** 2
    assert Fraction(712214, 10 ** 6) < Fraction(5, 7)
    result = {
        'manuscript_statement': 'Lemma 5.1',
        'prime_limit': LIMIT,
        'primes_with_condition_a': data['condition_a'],
        'primes_selected': len(data['selected']),
        'selected_primes': data['selected'],
        'max_alpha': data['max_alpha'],
        'groups_including_v_equal_1': len(data['groups']),
        'group_primes_v': data['groups'][1:],
        'base_cells_surviving_3_and_v_equal_1': data['surviving_base_cells'],
        'base_cells_total': BASE * BASE,
        'upper_bound': {'numerator': str(bound.numerator),
                        'denominator': str(bound.denominator)},
        'upper_bound_rounding': 'upwards to a multiple of 10^-12 after each factor',
        'exact_density_decimal_floor': decimal_floor(rho, 30),
        'upper_bound_decimal_floor': decimal_floor(bound, 30),
        'stated_bound': '0.253624',
        'stated_square_root_bound': '0.712214',
    }
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / 'balanced_sieve.json').write_text(
        json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print('BALANCED', len(data['selected']), 'primes; density at most',
          f'{bound.numerator}/{bound.denominator}', flush=True)
    return result
