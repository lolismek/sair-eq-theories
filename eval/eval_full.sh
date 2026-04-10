#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/.."
python eval/eval.py --problems data/all_problems.jsonl
