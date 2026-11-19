#!/usr/bin/env python3
"""Compare the published numerical tables with a manuscript source.

Usage: python3 scripts/check_source_tables.py /path/to/manuscript.tex

The source is identified by its SHA-256 digest, which must be the one
recorded under "manuscript" in data/source_manifest.json. For this source
the program checks every entry of the three tables against data/tables.json
and the recorded line range of each table. The tables are found in the
source by their LaTeX labels, which are recorded in the manifest.

With --rows-only the program accepts any source and compares the table
entries only. Use it for a revision that has not been recorded yet. If the
tables of that revision have other labels, give them with --labels, in the
order binary guards, ternary guards, auxiliary families.

The manuscript is not needed by the verification programs.
"""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TABLE_NAMES = ("binary_guards", "ternary_guards", "auxiliary_families")

if not __debug__:
    raise SystemExit("Run without -O: this checker uses assertions.")


def extract_table(tex, label):
    marker = "\\label{" + label + "}"
    assert marker in tex, "no table with the label " + label
    end = tex.index(marker)
    start = tex.rfind("\\begin{table}", 0, end)
    final = tex.index("\\end{table}", end) + len("\\end{table}")
    assert start >= 0
    rows = []
    for line in tex[start:end].splitlines():
        if not line.startswith("$") or not line[1].isdigit():
            continue
        fields = [
            field.strip().strip("$")
            for field in line.rstrip().removesuffix("\\\\").split("&")
        ]
        while fields and not fields[-1]:
            fields.pop()
        # An empty cell is typeset as "-"; early drafts used "--".
        values = [
            None if value in ("-", "--") else int(value.replace("\\,", ""))
            for value in fields
        ]
        assert len(values) % 3 == 0
        rows.extend(values[j:j + 3] for j in range(0, len(values), 3))
    return sorted(rows), [
        tex.count("\n", 0, start) + 1,
        tex.count("\n", 0, final) + 1,
    ]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument(
        "--rows-only", action="store_true",
        help="compare the table entries of a source that is not recorded")
    parser.add_argument(
        "--labels", nargs=3, metavar="LABEL",
        help="labels of the three tables in a source that is not recorded")
    args = parser.parse_args()
    data = args.source.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    tables = json.loads(
        (ROOT / "data/tables.json").read_text(encoding="utf-8"))
    manifest = json.loads(
        (ROOT / "data/source_manifest.json").read_text(encoding="utf-8"))
    recorded = manifest["manuscript"]
    if digest == recorded["sha256"]:
        assert len(data) == recorded["bytes"], "source size differs"
        assert data.count(b"\n") == recorded["lines"], "line count differs"
        assert args.labels is None, "--labels is for unrecorded sources"
        check_lines = True
        print("Source identified as", recorded["version"])
    else:
        assert args.rows_only, (
            "This source is not the recorded " + recorded["version"]
            + ". Use --rows-only to compare the table entries only.")
        check_lines = False
        print("Source not recorded; comparing the table entries only")
    tex = data.decode("utf-8")
    labels = args.labels or [
        recorded["tables"][name]["label"] for name in TABLE_NAMES]
    for name, label in zip(TABLE_NAMES, labels):
        rows, line_range = extract_table(tex, label)
        assert rows == tables[name]["rows"], (name, "table rows differ")
        if check_lines:
            assert line_range == recorded["tables"][name]["lines"], (
                name, "line range differs")
        print(label, len(rows), "rows agree")
    print("SUCCESS")


if __name__ == "__main__":
    main()
