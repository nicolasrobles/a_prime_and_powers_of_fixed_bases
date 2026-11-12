#!/usr/bin/env python3
"""Run the base-three minimality verification (Theorem 1.5)."""
from scripts.verification import main

if __name__ == '__main__':
    raise SystemExit(main(default_stage='base3', cases=(2, 3),
                          allow_stage=False))
