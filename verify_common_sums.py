#!/usr/bin/env python3
"""Run the common-sums verification (Proposition 7.1)."""
from scripts.verification import main

if __name__ == '__main__':
    raise SystemExit(main(default_stage='common', cases=(2, 3),
                          allow_stage=False))
