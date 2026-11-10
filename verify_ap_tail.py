#!/usr/bin/env python3
"""Run the tail verification for manuscript v13."""
from scripts.verification import main

if __name__ == '__main__':
    raise SystemExit(main(default_stage='tail', cases=(3,),
                          allow_stage=False))
