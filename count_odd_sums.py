#!/usr/bin/env python3
"""Count the odd integers p + q1^j + q2^k of Table 5."""
from scripts.verification import main

if __name__ == '__main__':
    raise SystemExit(main(default_stage='counts', cases=(2, 3),
                          allow_stage=False))
