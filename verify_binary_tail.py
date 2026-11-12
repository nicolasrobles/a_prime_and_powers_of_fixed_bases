#!/usr/bin/env python3
"""Run the tail verification for the binary case."""
from scripts.verification import main

if __name__ == '__main__':
    raise SystemExit(main(default_stage='tail', cases=(2,),
                          allow_stage=False))
