#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/.."
python eval/eval.py --problems data/iter_100.jsonl
