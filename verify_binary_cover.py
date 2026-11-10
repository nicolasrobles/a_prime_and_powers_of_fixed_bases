#!/usr/bin/env python3
"""Run the finite verification for manuscript v13."""
from scripts.verification import main

if __name__ == '__main__':
    raise SystemExit(main(default_stage='finite', cases=(2,),
                          allow_stage=False))
