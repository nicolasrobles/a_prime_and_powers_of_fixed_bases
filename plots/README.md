# Figures

These figures illustrate the certified finite data for *A prime and powers of fixed bases*. The exact comparisons are performed by the verification scripts. Floating point is used only to draw the figures.

## Auxiliary covering counts

The two panels of auxiliary_families.png and auxiliary_families.svg show the certified integers $k_{2,r}$ and $k_{3,r}$ at the finite auxiliary prime indices $r\le499$. The binary indices start at $r=7$, and the ternary indices start at $r=5$. There are 92 binary points and 93 ternary points. These are the counts in the manuscript's auxiliary-prime table, independently reproduced by the verification program.

## Partial auxiliary products

The two panels of partial_products.png and partial_products.svg show

$$
P_i(R)=\prod_{\substack{r\in\mathcal R_i\\r\le R}}
\left(1-\frac1r+\frac1{r-k_{i,r}}\right).
$$

The horizontal axis is logarithmic and extends through $R=5000$. The dashed line at 499 marks the end of the finite table. For larger auxiliary primes through 5000, the construction uses $k_{2,r}=2$ and $k_{3,r}=1$. Every factor is greater than one, so each partial product increases. The endpoint is compared exactly with the value in results/allocation_tail_exact.json before a figure is written.

The plotted values are obtained from rational products, enclosed between exact decimal endpoints, and only then converted to floats. The small final margins cannot be resolved visually. Consult tables/constants.csv and the exact result files for those comparisons.

## Regeneration

From the repository root, run the verifier and the table generator, install requirements-figures.txt, and then run scripts/make_plots.py. Each script also works when invoked by its full path from another directory.

The SVG files are vector graphics. The PNG files are rendered at 180 dpi. The scripts fix the style and omit timestamps from image metadata.
