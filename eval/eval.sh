#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/.."
python eval/eval.py --preset fast
