#!/usr/bin/env python3
"""Run the balanced-triple density verification (Lemma 5.1)."""
from scripts.verification import main

if __name__ == '__main__':
    raise SystemExit(main(default_stage='balanced', cases=(2, 3),
                          allow_stage=False))
