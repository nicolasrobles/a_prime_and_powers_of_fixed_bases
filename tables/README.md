# Generated tables

Run python3 scripts/make_tables.py after python3 verify_all.py. No optional Python packages are required.

The binary_guards, ternary_guards, auxiliary_families, allocation_summary, and constants tables are supplied in CSV and LaTeX. The LaTeX fragments require the amsmath, booktabs, and longtable packages and can be included in another document.

The guard tables reproduce the prescribed prime, exact multiplicative order, and residue. The auxiliary table reproduces the certified covering counts. The allocation summary records the complete finite-system counts and exact rational coverage margins.

The constants CSV contains the complete exact rational values, certified decimal intervals, the manuscript bounds, and positive exact margins. Its LaTeX version prints the decimal intervals so that the table remains readable. Both versions are derived from the same exact results.

The partial_products CSV contains all 666 binary and 667 ternary auxiliary factors through 5000 and decimal enclosures for each cumulative product and corresponding coefficient. A blank binary count in auxiliary_families.csv means that $r=5$ is not a binary auxiliary index. It does not mean that its count is zero.

The source tables and verified results are read from repository-relative paths. A mismatch in the input rows, certified counts, product endpoints, or claimed strict inequalities stops table generation.
