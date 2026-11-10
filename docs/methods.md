# Methods used by the verifiers

The programs check finite claims in version 13 of *A prime and powers of fixed bases*. This document explains what is computed and why the checks suffice for those claims. The covering and asymptotic arguments are given in the manuscript.

## Inputs and exact arithmetic

The two allocation witnesses retain the original bytes and filenames:

| File | Bytes | SHA-256 |
|---|---:|---|
| `binary_cover_1440_full.json` | 7,341 | `012f73acc4cf7ab110939a2a1afa3a7182dba86238ceafe975aa360647f87a76` |
| `ap_certificate.json` | 2,584 | `77339551fcb7f1e69e5faafa04e105706c09f44baa9e0cdbe8fca49de3b043ed` |

Their guard lists are checked against the prescribed primes and residues in `data/tables_v13.json`. The latter file also supplies the claimed orders and auxiliary covering counts from the three manuscript tables. `data/source_manifest.json` identifies the source version and input hashes. The table file records each source label and raw line range.

Python integers have arbitrary precision. The programs use integer modular exponentiation and `fractions.Fraction` for rational comparisons. Where two rational numbers are compared, the comparison is equivalent to cross-multiplying their positive denominators. Floating-point values are used only for supplementary display and plotting.

The verification programs accept witnesses already supplied in the repository. They do not need a linear-programming solver to check feasibility.

## Primality and multiplicative orders

Every prescribed prime is below $10^{12}$. A sieve through $10^6$ therefore supplies all trial primes up to its square root. If none divides the candidate, the candidate is prime.

For a claimed order $d$ of 2 modulo a prime $q$, the verifier checks

$$
2^d\equiv1\pmod q,
\qquad
2^{d/\ell}\not\equiv1\pmod q
\quad\text{for every prime }\ell\mid d.
$$

The first congruence makes the true order a divisor of $d$. Every proper divisor of $d$ divides $d/\ell$ for at least one prime $\ell\mid d$, so the remaining checks exclude every smaller order. The output records the modular residues used in these tests.

The binary table contains 41 entries and the ternary table 30. Ten primes occur in both tables, leaving 61 distinct primes in total. The verifier also checks the specified order-81 choice $2593$, which avoids the two order-81 primes prescribed in the ternary table.

## The finite allocation

Write

$$
D_2=1440,\qquad D_3=1296,
$$

and

$$
\Lambda_2(h)=1+2^h,\qquad
\Lambda_3(h)=1+2^h+2^{2h}.
$$

The phase sets have 45 binary elements and eight ternary elements:

$$
\mathcal H_2=\{32c:0\le c<45\}\pmod{1440},
$$

$$
\mathcal H_3=\{81c:c\in\{1,3,5,7,9,11,13,15\}\}\pmod{1296}.
$$

For each phase $h$, the surviving exponent classes are

$$
A_h=\{a\bmod D_i:
2^a\Lambda_i(h)\not\equiv b_q\pmod q
\text{ for every prescribed }q\}.
$$

Every relevant order divides $D_i$, so reducing the exponents modulo $D_i$ is valid. The program enumerates each class and checks all prescribed congruences.

Set

$$
m(j)=1+\mathbf1_{j\equiv4\pmod8},
\qquad
c_g=\frac1{D_i}
\sum_{\substack{1\le j\le D_i\\\gcd(j,D_i)=g}}m(j).
$$

There is one capacity $c_g$ for each divisor $g$ of $D_i$, giving 36 binary capacities and 25 ternary capacities. Their sum is $9/8$.

Each sparse witness row is a quadruple $[h,g,u,N]$. An omitted triple has numerator zero. For the representative phases the allocation is

$$
x_{h,g,u}=\frac{N}{\varepsilon_h10^{12}},
\qquad
\varepsilon_h=
\begin{cases}
1,&h=0,\\
2,&h\ne0.
\end{cases}
$$

The other phases are filled by

$$
x_{-h,g,u}=x_{h,g,u-(i-1)h}.
$$

This sign follows from

$$
\Lambda_i(-h)\equiv
2^{-(i-1)h}\Lambda_i(h)\pmod q,
$$

which gives $a\in A_{-h}$ exactly when $a-(i-1)h\in A_h$.

The verifier constructs the full reflected allocation and checks

$$
\sum_{h\in\mathcal H_i}\sum_{u\bmod g}x_{h,g,u}\le c_g
$$

for every $g\mid D_i$, and

$$
|\mathcal H_i|\sum_{g\mid D_i}g\,x_{h,g,a\bmod g}\ge Z_i
$$

for every surviving pair $(h,a)$. The targets are the exact rationals represented by the decimals

$$
Z_2=2.081483,\qquad Z_3=2.287407.
$$

The complete enumeration has 20,548 binary surviving pairs and 2,966 ternary surviving pairs. Its minimum normalized coverages are

$$
\frac{3252320451}{1562500000}=2.081485088640,
$$

$$
\frac{35740740681}{15625000000}=2.287407403584.
$$

The positive margins above the targets are $6527/3125000000$ and $3153/7812500000$, respectively. The result file records every capacity slack, every phase count, and every pair attaining a minimum.

Interpreting these finite capacities as an available asymptotic supply of primes uses the primitive-divisor and harmonic-sum lemmas in the manuscript. In particular, the general assertion that two primitive primes exist for $d\equiv4\pmod8$, $d\ge28$, is the published input recorded in Pomerance, Section 2, from Schinzel's work. The finite feasibility checks do not attempt to reprove that general theorem.

## Cyclotomic values and primitive-prime lower bounds

For the finite auxiliary table, the binary orders are $d=2^jr$, with $0\le j\le8$ and primes $7\le r\le499$. The ternary orders are $d=2^e3^jr$, with $e\in\{0,1\}$, $0\le j\le6$, and primes $5\le r\le499$. These ranges contain 828 and 1,302 orders, respectively.

The program computes each cyclotomic value using the general identity

$$
\Phi_d(2)=\frac{2^d-1}
{\prod_{\substack{e\mid d\\e<d}}\Phi_e(2)}.
$$

Each division is checked to have zero remainder. The resulting integer is compared with the specialized formula used in the manuscript. Thus the specialized expressions are not used as the sole way to obtain the values.

If an odd prime $q$ divides $\Phi_d(2)$ and has order $f<d$, it also divides a factor of $X^d-1$ indexed by a proper divisor of $d$. At $X=2$, at least two factors of the product $X^d-1=\prod_{e\mid d}\Phi_e(X)$ then vanish modulo $q$. Its derivative also vanishes, so

$$
d\,2^{d-1}\equiv0\pmod q.
$$

It follows that $q\mid d$. For the orders used here, the possible nonprimitive odd primes are therefore among 3 and $r$.

The program removes their full powers. It then tests the primes $q<10^6$ with $q\equiv1\pmod d$, checks the exact order whenever a divisor is found, and removes its entire power. Each distinct discovered prime contributes one to the lower bound.

If the remaining cofactor exceeds one, it contributes at least one further distinct primitive prime. Its primality is not assumed. Its prime divisors have order $d$, and none can be a previously counted prime because those powers were fully removed. This gives a rigorous lower bound even when the residual cofactor remains composite.

For binary orders $4r$, the lower bound is at least two. For the prime indices used here, this also follows from an elementary factorization. Put

$$
A_\pm=2^r\pm2^{(r+1)/2}+1.
$$

Then $A_-A_+=2^{2r}+1$ and $\Phi_{4r}(2)=A_-A_+/5$. The two factors are odd, greater than 5, and coprime, because their difference is a power of two. For odd prime $r\ge7$,

$$
4^r+1=(-1+5)^r+1\equiv5r\pmod{25},
$$

so exactly one factor of 5 divides the product. After removing it, both coprime factors remain greater than one. Also, $r\nmid\Phi_{4r}(2)$: otherwise the order of 2 modulo $r$ would divide both $4r$ and $r-1$, hence divide 4, forcing $r\mid15$. Each remaining factor therefore supplies a different primitive prime.

## Covering counts

For the binary case, if $s_j$ is the certified number of primes at order $2^jr$, the constructive grouping of two child classes gives

$$
K_2(r)=\left\lfloor\sum_{j=0}^{8}\frac{s_j}{2^j}\right\rfloor.
$$

The program computes this floor with rational arithmetic.

For the ternary case, let $\beta_j$ count full blocks and $\nu_j$ count parity-refined half blocks at depth $j$. At depth zero, $b$ full blocks and $n$ half blocks give $b+\lfloor n/2\rfloor$ full coverings.

At a higher depth, convert $2p$ half blocks to $p$ full blocks, then regard $s$ full blocks as half blocks. The remaining counts are $b+p-s$ and $n-2p+s$, with

$$
0\le p\le\lfloor n/2\rfloor,\qquad 0\le s\le b+p.
$$

Grouping each kind into triples gives the recurrence

$$
K_j(b,n)=
\max_{p,s}
K_{j-1}\left(
\beta_{j-1}+\left\lfloor\frac{b+p-s}{3}\right\rfloor,\,
\nu_{j-1}+\left\lfloor\frac{n-2p+s}{3}\right\rfloor
\right).
$$

The manuscript uses the restriction $p,s\le2$, which still gives valid constructive lower bounds. The program computes both that restricted recurrence and the full displayed recurrence. They agree at all 93 finite ternary indices. This equality concerns these two recurrences, not optimality over every possible covering construction.

All 92 binary and 93 ternary counts reproduce the printed table. Each claimed $k_{i,r}$ satisfies $1\le k_{i,r}\le(r-1)/2$.

For indices above 499 and at most 5000, the manuscript uses $k_{2,r}=2$ and $k_{3,r}=1$. These follow from the primitive-divisor input and the constructive covering lemma, rather than a factorization of all the corresponding cyclotomic values.

## Rational products and final coefficients

Let $\mathcal R_2$ contain primes $7\le r\le5000$ and $\mathcal R_3$ contain primes $5\le r\le5000$. Their sizes are 666 and 667. The program forms

$$
P_i=\prod_{r\in\mathcal R_i}
\left(1-\frac1r+\frac1{r-k_{i,r}}\right)
$$

as a rational number. It checks all four strict lower bounds

$$
P_2>1.170314,\quad P_3>1.331909,\quad
Z_2P_2>2.435990,\quad Z_3P_3>3.046617,
$$

and then checks

$$
C_2=\frac4{Z_2P_2}<1.642043,\qquad
C_3=\frac3{2Z_3P_3}<0.492350.
$$

The decimal intervals in the result files are certified by rational comparison. They enclose the exact values strictly. The figures display partial products obtained from the same rational factors.

## Introductory arithmetic

For $N=118\,514\,161$, one has $3^{16}<N<3^{17}$. It is enough to consider $0\le a\le b\le16$, giving 153 unordered pairs. The program completely factors every $N-3^a-3^b$, checks that the product of the factors reconstructs the difference, and proves each recorded prime factor prime by trial division. Every difference has at least two distinct prime factors, so none is a prime power. This stage checks the candidate. Minimality is treated in the section on base three below.

Modulo 600, the orders of 599 and 601 are 2 and 1. For odd $b$, the possible prime residues are $b$ and $b-2$. Both fail to be units exactly when $b\equiv5$ or $12\pmod{15}$. There are 40 such odd classes modulo 600. Only $b=5$ allows a prime divisor of 600 as one of the residues, giving the two possibilities 5 and 3. Thus there are 39 empty classes, one sparse class with $J_5=2$, and 260 classes with a coprime residue.

The program also checks the empty progression $57\pmod{60}$ for $(599,601)$, and the coprime residue

$$
57-17^2-19\equiv49\pmod{60}
$$

for the pair $(17,19)$. The density consequences require the analytic statements of the manuscript.

## The balanced-triple sieve

For a prime $q\ge5$ write $\operatorname{ord}_q(2)=3^{\alpha_q}e_q$ with $3\nmid e_q$. The set $\mathcal K$ consists of the primes $5\le q\le50000$ such that

- $e_q/(e_q,80)$ is $1$ or a prime $v$ with $7\le v\le317$, and
- $q$ divides $1+2^{h_1}+2^{h_2}$ for some $h_1,h_2\ge0$ divisible by $3^{\alpha_q}$.

`scripts/balanced_sieve.py` computes each order from the factorization of $q-1$. For each $q$ satisfying the first condition it forms $\zeta=2^h$, where $h$ is divisible by $3^{\alpha_q}$ and congruent to $1$ modulo $e_q$, checks that $\zeta$ has order $e_q$ by listing its $e_q$ powers, and finds all pairs $(i,k)$ modulo $e_q$ with $1+\zeta^i+\zeta^k\equiv0\pmod q$. The second condition holds exactly when there is such a pair. The program finds 870 primes with the first condition and 626 with both, and the largest $\alpha_q$ among the latter is $4$. Hence, for exponents divisible by $81$, divisibility by a prime of $\mathcal K$ depends only on the classes of the exponents modulo $e_q$.

Let $N_0=80\prod_{7\le v\le317}v$ over primes $v$, and let $\varrho$ be the density of the pairs of classes modulo $N_0$ for which $1+2^{h_1}+2^{h_2}$ is divisible neither by $3$ nor by a prime of $\mathcal K$. Group the primes of $\mathcal K$ by $v=e_q/(e_q,80)$. For a pair $(a_0,b_0)$ of classes modulo $80$, let $N_v(a_0,b_0)$ be the number of pairs of classes modulo $v$ not excluded by a prime of the group $v$. Since $80$ and the primes $v$ are pairwise coprime,

$$
\varrho=\frac1{80^2}\sum_{(a_0,b_0)}\prod_v\frac{N_v(a_0,b_0)}{v^2},
$$

where the sum is over the pairs that are not both even (the prime $3$) and the product includes $v=1$. The program evaluates the right side twice. The first evaluation uses integers scaled by $10^{12}$ and rounds upwards after each factor; it gives

$$
\varrho\le\frac{1623190827888387}{6400000000000000}<0.253624.
$$

The second evaluation is exact, with the common denominator $80^2\prod_v v^2$. It gives $\varrho=0.25362356684502987\ldots$, and the program checks that this does not exceed the rounded bound. It also checks $2\cdot0.253624<0.712214^2$ and $0.712214<5/7$ with rational numbers.

## Minimality in base three

`scripts/base3_minimality.py` repeats the 153 factorizations for $N=118\,514\,161$ and then proves that every odd integer $n$ coprime to $3$ with $10<n<N$ is of the form $p+3^a+3^b$ with $p$ prime and $1\le a\le b\le16$. Exponents above $16$ cannot occur since $3^{17}>N$, and $p$ is odd because $n$ is odd and $3^a+3^b$ is even.

The odd primes up to $N$ are found by the sieve of Eratosthenes on the odd integers and stored as the bits of one integer, bit $j$ standing for $2j+1$. Adding $3^a+3^b$ to every prime is a shift by $(3^a+3^b)/2$ bits. The union of the $136$ shifted copies is compared with the set of the odd integers coprime to $3$ in $(10,N]$. The only one of these integers not in the union is $N$, and the number of those below $N$ is $39\,504\,717$.

Since a representation with a prime and positive exponents is also one with a prime power and nonnegative exponents, $N$ is the least exception in each of the four conventions.

## Mathematical references

- Cristian Cobeli, Nicolas Robles, and Alexandru Zaharescu, *A prime and powers of fixed bases*, version 13. The manifest records the source identity, and the table file records the raw table locations.
- Carl Pomerance, *Cyclotomic primes*, Section 2 of the [author's manuscript](https://math.dartmouth.edu/~carlp/cyclotomicprimesfinal.pdf), for primitive and intrinsic prime factors and the Schinzel result used for general orders $d\equiv4\pmod8$.

Every finite result described above is recomputed by the repository programs. The broader number-theoretic deductions remain mathematical arguments in the accompanying manuscript.
