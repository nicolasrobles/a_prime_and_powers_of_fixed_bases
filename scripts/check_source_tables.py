#!/usr/bin/env python3
"""Compare the published numerical tables with the exact v13 TeX source.

Usage: python3 scripts/check_source_tables.py /path/to/manuscript_v13.tex
The manuscript is not needed by the verification programs. This optional
check is for readers who also have the source identified in the manifest.
"""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

if not __debug__:
    raise SystemExit("Run without -O: this checker uses assertions.")


def extract_table(tex, label):
    end = tex.index("\\label{" + label + "}")
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
        values = [
            None if value == "--" else int(value.replace("\\,", ""))
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
    args = parser.parse_args()
    data = args.source.read_bytes()
    tables = json.loads((ROOT / "data/tables_v13.json").read_text(encoding="utf-8"))
    assert hashlib.sha256(data).hexdigest() == tables["manuscript_sha256"], (
        "This command checks the exact v13 source recorded in the manifest."
    )
    tex = data.decode("utf-8")
    for name in ("binary_guards", "ternary_guards", "auxiliary_families"):
        expected = tables[name]
        rows, line_range = extract_table(tex, expected["source_label"])
        assert rows == expected["rows"], (name, "table rows differ")
        assert line_range == expected["source_lines"], (name, "line range differs")
        print(expected["source_label"], len(rows), "rows agree")
    print("SUCCESS")


if __name__ == "__main__":
    main()
