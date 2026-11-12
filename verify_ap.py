#!/usr/bin/env python3
"""Run the finite verification for the ternary case."""
from scripts.verification import main

if __name__ == '__main__':
    raise SystemExit(main(default_stage='finite', cases=(3,),
                          allow_stage=False))
