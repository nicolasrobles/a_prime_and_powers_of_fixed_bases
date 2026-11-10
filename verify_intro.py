#!/usr/bin/env python3
"""Run the intro verification for manuscript v13."""
from scripts.verification import main

if __name__ == '__main__':
    raise SystemExit(main(default_stage='intro', cases=(2, 3),
                          allow_stage=False))
