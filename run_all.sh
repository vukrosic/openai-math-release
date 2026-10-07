#!/bin/bash
# Usage: bash run_all.sh /path/to/clone-of-openai-math
set -e
python3 catalog.py "${1:-math}"
echo
python3 coloring.py
echo
python3 pi_fractions.py
echo
python3 primes.py
echo
python3 zeros.py
