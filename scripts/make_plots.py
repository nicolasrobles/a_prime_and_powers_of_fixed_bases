#!/usr/bin/env python3
"""Regenerate scientific plots from the verified v13 data.

The plotted numbers are computed with exact rational arithmetic, then
converted to floating point only for rendering. The figures illustrate the
verified data; the exact checks are in verify_all.py and results/.
"""
from fractions import Fraction
from pathlib import Path
import json

try:
    import matplotlib
except ModuleNotFoundError as exc:
    raise SystemExit(
        "Plotting requires Matplotlib. Install requirements-figures.txt."
    ) from exc

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FixedLocator, MaxNLocator, ScalarFormatter

if __package__:
    from .make_tables import ROOT, load_inputs, partial_products
else:
    from make_tables import ROOT, load_inputs, partial_products

PLOTS = ROOT / "plots"
COLORS = {2: "#245C86", 3: "#A64B16"}


def style():
    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "font.size": 10,
        "axes.titlesize": 12,
        "axes.labelsize": 10,
        "legend.fontsize": 9,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "grid.alpha": 0.22,
        "grid.linewidth": 0.6,
        "axes.axisbelow": True,
        "savefig.facecolor": "white",
        "svg.hashsalt": "prime-and-fixed-base-powers-v13",
    })


def save(fig, name):
    fig.savefig(
        PLOTS / (name + ".svg"),
        metadata={"Date": None, "Creator": "scripts/make_plots.py"},
    )
    fig.savefig(
        PLOTS / (name + ".png"),
        dpi=180,
        metadata={"Software": "scripts/make_plots.py"},
    )
    plt.close(fig)


def auxiliary_figure(data):
    fig, axes = plt.subplots(
        2, 1, figsize=(8.2, 6.4), sharex=True, layout="constrained"
    )
    for case, axis in zip((2, 3), axes):
        rows = [
            (row[0], row[case - 1])
            for row in data["auxiliary_families"]["rows"]
            if row[case - 1] is not None
        ]
        r_values, k_values = zip(*rows)
        axis.vlines(
            r_values, 0, k_values, color=COLORS[case], alpha=0.40, lw=0.7
        )
        axis.scatter(r_values, k_values, color=COLORS[case], s=17, zorder=3)
        axis.set_title(
            "Binary covering counts" if case == 2
            else "Ternary covering counts",
            loc="left",
        )
        axis.set_ylabel(r"$k_{%d,r}$" % case)
        axis.yaxis.set_major_locator(MaxNLocator(integer=True))
        axis.set_ylim(0, max(k_values) + 1)
        axis.set_xlim(0, 510)
        axis.text(
            0.99, 0.93, str(len(rows)) + " prime indices",
            transform=axis.transAxes, ha="right", va="top", fontsize=9,
        )
    axes[-1].set_xlabel(r"Auxiliary prime $r$")
    save(fig, "auxiliary_families")


def product_figure(data, tail, coefficients):
    products = partial_products(data, tail)
    fig, axes = plt.subplots(
        2, 1, figsize=(8.2, 6.4), sharex=True, layout="constrained"
    )
    for case, axis in zip((2, 3), axes):
        rows = [row for row in products if row["case"] == case]
        parameter = data["parameters"][str(case)]
        # The midpoint of an exact interval of width at most 10^-18 is
        # sufficient for plotting. It is not used in any acceptance test.
        values = [
            float((Fraction(row["P_lower"]) + Fraction(row["P_upper"])) / 2)
            for row in rows
        ]
        axis.step(
            [row["r"] for row in rows], values, where="post",
            color=COLORS[case], lw=1.65,
        )
        axis.axvline(
            parameter["finite_max_prime"], color="#777777", ls="--", lw=0.8,
            label=r"$r=499$: end of the finite table",
        )
        axis.set_xscale("log")
        axis.set_xlim(4, parameter["auxiliary_max_prime"] * 1.05)
        axis.set_ylim(1, max(values) + 0.012)
        axis.set_ylabel(r"$P_%d(R)$" % case)
        axis.set_title(
            "Binary auxiliary product" if case == 2
            else "Ternary auxiliary product",
            loc="left",
        )
        lower = coefficients[str(case)]["P_interval"]["lower"]
        axis.text(
            0.98, 0.13,
            r"$P_%d(5000) > %s$" % (case, lower[:10]),
            transform=axis.transAxes, ha="right", va="bottom", fontsize=10,
        )
        axis.legend(loc="lower left", frameon=False, fontsize=8.5)
    axes[-1].set_xlabel(r"Largest auxiliary prime included, $R$ (log scale)")
    axes[-1].xaxis.set_major_locator(
        FixedLocator([5, 10, 50, 100, 500, 1000, 5000])
    )
    axes[-1].xaxis.set_major_formatter(ScalarFormatter())
    save(fig, "partial_products")


def main():
    data, finite, tail, coefficients = load_inputs()
    style()
    PLOTS.mkdir(exist_ok=True)
    auxiliary_figure(data)
    product_figure(data, tail, coefficients)
    manifest = {
        "manuscript_version": data["manuscript_version"],
        "manuscript_sha256": data["manuscript_sha256"],
        "generator": "scripts/make_plots.py",
        "figures": {
            "auxiliary_families": {
                "formats": ["svg", "png"],
                "data": "data/tables_v13.json",
                "meaning": "Certified counts for the finite prime indices.",
            },
            "partial_products": {
                "formats": ["svg", "png"],
                "data": "tables/partial_products.csv",
                "meaning": "Exact rational partial products converted for display.",
            },
        },
    }
    (PLOTS / "plot_manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    print("Generated auxiliary_families and partial_products in SVG and PNG.")


if __name__ == "__main__":
    main()
