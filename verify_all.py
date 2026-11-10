#!/usr/bin/env python3
"""Run all verification stages recorded in the source manifest."""
from scripts.verification import main

if __name__ == '__main__':
    raise SystemExit(main(default_stage='all', cases=(2, 3),
                          allow_stage=True))
