#!/usr/bin/env python3
"""Regenerate the v13 tables using only repository data and exact results.

Run from any directory with Python 3.9 or later. No optional packages are
required. The verification results must first be made by verify_all.py.
"""
from fractions import Fraction
from math import isqrt
from pathlib import Path
import csv
import hashlib
import json

ROOT = Path(__file__).resolve().parent.parent
TABLES = ROOT / "tables"


def read_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SystemExit(
            "Required repository data is missing. Run python3 verify_all.py "
            "from the repository first."
        ) from exc


def load_inputs():
    data = read_json(ROOT / "data" / "tables_v13.json")
    finite = read_json(ROOT / "results" / "allocation_finite_exact.json")
    tail = read_json(ROOT / "results" / "allocation_tail_exact.json")
    coefficients = read_json(ROOT / "results" / "coefficient_checks.json")
    for result in (finite, tail):
        for name in [
            "binary_cover_1440_full.json", "ap_certificate.json",
            "data/tables_v13.json",
        ]:
            digest = hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
            if digest != result["metadata"][name]["sha256"]:
                raise ValueError(
                    "Input bytes differ from the verified results. "
                    "Run python3 verify_all.py before regenerating tables."
                )
    for case, key in [(2, "binary_guards"), (3, "ternary_guards")]:
        parameter = data["parameters"][str(case)]
        target = Fraction(str(parameter["Z"]))
        product = Fraction(tail[str(case)]["P_exact"])
        multiplier = Fraction(4) if case == 2 else Fraction(3, 2)
        if target != Fraction(finite[str(case)]["target_exact"]):
            raise ValueError("Coverage target differs from the verified result.")
        if target * product != Fraction(tail[str(case)]["ZP_exact"]):
            raise ValueError("Coverage/product identity failed.")
        if multiplier / (target * product) != Fraction(
            coefficients[str(case)]["C_exact"]
        ):
            raise ValueError("Final coefficient identity failed.")
        expected = sorted(tuple(row) for row in data[key]["rows"])
        actual = sorted(
            (row["q"], row["order"], row["residue"])
            for row in finite[str(case)]["guard_checks"]
        )
        if actual != expected:
            raise ValueError("Guard tables and verification results differ.")
        if len(actual) != finite[str(case)]["guard_count"]:
            raise ValueError("Guard count differs from its result.")
        for row in tail[str(case)]["entries"]:
            supplied = next(
                entry[case - 1] for entry in data["auxiliary_families"]["rows"]
                if entry[0] == row["r"]
            )
            if supplied != row["table_k"] or supplied != row["certified_families"]:
                raise ValueError("Auxiliary counts and results differ.")
    return data, finite, tail, coefficients


def decimal_text(numerator, places):
    """Format an integer divided by 10**places, without a float conversion."""
    scale = 10 ** places
    integer, remainder = divmod(numerator, scale)
    return str(integer) + "." + str(remainder).zfill(places)


def enclosing_decimals(value, places=18):
    """Return a closed rational enclosure with exact decimal endpoints."""
    value = Fraction(value)
    scale = 10 ** places
    scaled, remainder = divmod(value.numerator * scale, value.denominator)
    lower = decimal_text(scaled, places)
    upper = decimal_text(scaled + bool(remainder), places)
    if not Fraction(lower) <= value <= Fraction(upper):
        raise ArithmeticError("Decimal enclosure failed.")
    return lower, upper


def primes_up_to(limit):
    sieve = bytearray(b"\x01") * (limit + 1)
    sieve[0:2] = b"\x00\x00"
    for p in range(2, isqrt(limit) + 1):
        if sieve[p]:
            sieve[p * p:limit + 1:p] = b"\x00" * (
                (limit - p * p) // p + 1
            )
    return [p for p in range(2, limit + 1) if sieve[p]]


def partial_products(data, tail):
    """Compute every plotted product as a Fraction before decimal conversion."""
    rows = []
    for case in (2, 3):
        parameter = data["parameters"][str(case)]
        k_values = {
            row[0]: row[case - 1]
            for row in data["auxiliary_families"]["rows"]
            if row[case - 1] is not None
        }
        product = Fraction(1)
        count = 0
        target = Fraction(str(parameter["Z"]))
        multiplier = Fraction(4) if case == 2 else Fraction(3, 2)
        for r in primes_up_to(parameter["auxiliary_max_prime"]):
            if r < parameter["auxiliary_min_prime"]:
                continue
            k = (k_values[r] if r <= parameter["finite_max_prime"]
                 else parameter["tail_k"])
            if not 1 <= k <= (r - 1) // 2:
                raise ValueError("Auxiliary count is outside the allowed range.")
            factor = 1 - Fraction(1, r) + Fraction(1, r - k)
            if factor <= 1:
                raise ValueError("An auxiliary factor failed to exceed one.")
            product *= factor
            coefficient = multiplier / (target * product)
            count += 1
            p_lower, p_upper = enclosing_decimals(product)
            c_lower, c_upper = enclosing_decimals(coefficient)
            rows.append({
                "case": case,
                "r": r,
                "k": k,
                "factor_exact": str(factor),
                "P_lower": p_lower,
                "P_upper": p_upper,
                "C_lower": c_lower,
                "C_upper": c_upper,
            })
        if product != Fraction(tail[str(case)]["P_exact"]):
            raise ArithmeticError("Partial product endpoint differs from proof.")
        if count != tail[str(case)]["prime_index_count"]:
            raise ArithmeticError("Auxiliary index count differs from proof.")
    return rows


def write_csv(name, fieldnames, rows):
    path = TABLES / name
    with path.open("w", encoding="utf-8", newline="") as output:
        writer = csv.DictWriter(
            output, fieldnames=fieldnames, lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)


def tex_escape(value):
    text = str(value)
    for old, new in [
        ("&", r"\&"), ("%", r"\%"), ("_", r"\_"), ("#", r"\#")
    ]:
        text = text.replace(old, new)
    return text


def write_longtable(name, caption, headers, rows, alignment):
    """Write an includable longtable with standard math and table packages."""
    columns = len(headers)
    ending = " " + "\\" * 2
    header = " & ".join(headers) + ending
    lines = [
        "% Generated by scripts/make_tables.py. Do not edit by hand.",
        "% Required packages: amsmath, booktabs, longtable.",
        r"\begingroup",
        r"\small",
        r"\setlength{\tabcolsep}{5pt}",
        r"\begin{longtable}{" + alignment + "}",
        r"\caption{" + caption + "}" + ending,
        r"\toprule",
        header,
        r"\midrule",
        r"\endfirsthead",
        r"\toprule",
        header,
        r"\midrule",
        r"\endhead",
        r"\midrule",
        r"\multicolumn{" + str(columns)
        + r"}{r}{Continued on the next page}" + ending,
        r"\endfoot",
        r"\bottomrule",
        r"\endlastfoot",
    ]
    lines.extend(" & ".join(row) + ending for row in rows)
    lines.extend([r"\end{longtable}", r"\endgroup", ""])
    (TABLES / name).write_text("\n".join(lines), encoding="utf-8")


def guard_tables(data):
    for case, name, key in [
        (2, "binary_guards", "binary_guards"),
        (3, "ternary_guards", "ternary_guards"),
    ]:
        values = sorted(data[key]["rows"])
        rows = [
            {"q": q, "order": order, "residue": residue}
            for q, order, residue in values
        ]
        write_csv(name + ".csv", ["q", "order", "residue"], rows)
        write_longtable(
            name + ".tex",
            "Prescribed primes and residues for "
            + ("two powers" if case == 2 else "three powers in progression")
            + r". The order is $\operatorname{ord}_q(2)$.",
            [r"$q$", r"$\operatorname{ord}_q(2)$", r"$b_q$"],
            [[str(q), str(order), str(residue)]
             for q, order, residue in values],
            "rrr",
        )


def auxiliary_table(data):
    rows = [
        {"r": r, "k_2": "" if binary is None else binary, "k_3": ternary}
        for r, binary, ternary in data["auxiliary_families"]["rows"]
    ]
    write_csv("auxiliary_families.csv", ["r", "k_2", "k_3"], rows)
    write_longtable(
        "auxiliary_families.tex",
        "Certified auxiliary covering counts in v13 for primes "
        + r"$r\le499$. The binary indices start at $r=7$.",
        [r"$r$", r"$k_{2,r}$", r"$k_{3,r}$"],
        [[str(row["r"]), "--" if row["k_2"] == "" else str(row["k_2"]),
          str(row["k_3"])] for row in rows],
        "rrr",
    )


def allocation_table(finite, tail):
    fields = [
        ("Prescribed prime entries", "guard_count"),
        ("Capacity inequalities", "capacities_checked"),
        ("Representative allocation entries", "allocation_entries"),
        ("Reflected allocation entries", "full_allocation_entries"),
        ("Surviving exponent-phase pairs", "surviving_pairs_full"),
        ("Claimed coverage constant", "target_exact"),
        ("Minimum normalized coverage", "min_gamma_exact"),
        ("Coverage margin", "target_margin_exact"),
    ]
    rows = [
        {"quantity": label, "binary": finite["2"][field],
         "ternary": finite["3"][field]}
        for label, field in fields
    ]
    rows.extend([
        {"quantity": "Finite auxiliary order calculations",
         "binary": sum(len(entry["orders"]) for entry in tail["2"]["entries"]),
         "ternary": sum(len(entry["orders"]) for entry in tail["3"]["entries"])},
        {"quantity": "Finite auxiliary indices",
         "binary": tail["2"]["finite_rows_checked"],
         "ternary": tail["3"]["finite_rows_checked"]},
        {"quantity": "All auxiliary indices through 5000",
         "binary": tail["2"]["prime_index_count"],
         "ternary": tail["3"]["prime_index_count"]},
    ])
    write_csv(
        "allocation_summary.csv", ["quantity", "binary", "ternary"], rows
    )
    formatted = []
    for row in rows:
        numeric = []
        for column in ("binary", "ternary"):
            value = str(row[column])
            if "/" in value:
                fraction = Fraction(value)
                numeric.append(
                    r"$\dfrac{" + str(fraction.numerator)
                    + "}{" + str(fraction.denominator) + "}$"
                )
            else:
                numeric.append(value)
        formatted.append([tex_escape(row["quantity"])] + numeric)
    write_longtable(
        "allocation_summary.tex",
        "Exact finite verification totals and coverage margins.",
        ["Quantity", "Binary", "Ternary"],
        formatted,
        r"p{0.47\linewidth}rr",
    )


def constants_table(data, tail, coefficients):
    rows = []
    formatted = []
    for case in (2, 3):
        parameter = data["parameters"][str(case)]
        case_tail = tail[str(case)]
        case_coeff = coefficients[str(case)]
        values = [
            ("P", Fraction(case_tail["P_exact"]),
             case_coeff["P_interval"], ">", parameter["P_lower"]),
            ("ZP", Fraction(case_tail["ZP_exact"]),
             case_coeff["ZP_interval"], ">", parameter["ZP_lower"]),
            ("C", Fraction(case_coeff["C_exact"]),
             case_coeff["C_interval"], "<", parameter["C_upper"]),
        ]
        for symbol, value, enclosure, relation, bound in values:
            bound = str(bound)
            margin = (value - Fraction(bound) if relation == ">"
                      else Fraction(bound) - value)
            lower, upper = enclosure["lower"], enclosure["upper"]
            if not Fraction(lower) < value < Fraction(upper) or margin <= 0:
                raise ArithmeticError("A claimed strict constant bound failed.")
            margin_lower, margin_upper = enclosing_decimals(margin)
            rows.append({
                "case": case, "quantity": symbol, "exact_value": str(value),
                "lower_endpoint": lower, "upper_endpoint": upper,
                "manuscript_comparison": relation, "manuscript_bound": bound,
                "margin_exact": str(margin),
                "margin_lower": margin_lower, "margin_upper": margin_upper,
            })
            label = (r"$Z_" + str(case) + r"P_" + str(case) + "$"
                     if symbol == "ZP" else "$" + symbol + "_" + str(case) + "$")
            formatted.append(
                [label, lower, upper, "$" + relation + bound + "$"]
            )
    write_csv("constants.csv", list(rows[0]), rows)
    write_longtable(
        "constants.tex",
        "Open rational enclosures for the exact products and coefficients. "
        "The last column gives the strict bound printed in v13.",
        ["Quantity", "Lower endpoint", "Upper endpoint", "v13 bound"],
        formatted,
        "lrrr",
    )


def main():
    data, finite, tail, coefficients = load_inputs()
    TABLES.mkdir(exist_ok=True)
    guard_tables(data)
    auxiliary_table(data)
    allocation_table(finite, tail)
    constants_table(data, tail, coefficients)
    partial = partial_products(data, tail)
    write_csv("partial_products.csv", list(partial[0]), partial)
    print("Generated five CSV/TeX table pairs and partial_products.csv.")
    print("Every comparison and product endpoint was checked exactly.")


if __name__ == "__main__":
    main()
