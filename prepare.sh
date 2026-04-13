#!/usr/bin/env bash
set -e

cd "$(dirname "$0")"

# Clone the official judge repo (for prompt.py and judge.py)
if [ ! -d "judge_repo" ]; then
    echo "Cloning judge repo..."
    git clone https://github.com/SAIRcompetition/equational-theories-stage1-judge.git judge_repo
else
    echo "Judge repo already cloned."
fi

# Install Python dependencies
pip install -q httpx>=0.27 datasets

# Download full dataset from HuggingFace
if [ ! -f "data/all_problems.jsonl" ]; then
    echo "Downloading full dataset..."
    python -c "
from datasets import load_dataset
import json

subsets = ['normal', 'hard', 'hard1', 'hard2', 'hard3']
with open('data/all_problems.jsonl', 'w') as f:
    for subset in subsets:
        ds = load_dataset(
            'SAIRfoundation/equational-theories-selected-problems',
            subset,
            split='train',
        )
        for row in ds:
            f.write(json.dumps(row, ensure_ascii=False) + '\n')
print(f'Downloaded all problems to data/all_problems.jsonl')
"
else
    echo "Full dataset already downloaded."
fi

# Build the SAIR-style public smoke split from the hard3 subset.
if [ ! -f "data/sair_smoke_20.jsonl" ]; then
    echo "Building SAIR smoke split..."
    python -c "
import json

true_count = 0
false_count = 0
rows = []

with open('data/all_problems.jsonl') as src:
    for line in src:
        row = json.loads(line)
        if not row['id'].startswith('hard3_'):
            continue
        if row['answer'] and true_count < 10:
            rows.append(row)
            true_count += 1
        elif (not row['answer']) and false_count < 10:
            rows.append(row)
            false_count += 1
        if true_count >= 10 and false_count >= 10:
            break

if true_count < 10 or false_count < 10:
    raise RuntimeError('Could not derive the SAIR smoke split from hard3')

with open('data/sair_smoke_20.jsonl', 'w') as dst:
    for row in rows:
        dst.write(json.dumps(row, ensure_ascii=False) + '\n')

print('Wrote data/sair_smoke_20.jsonl')
"
else
    echo "SAIR smoke split already built."
fi

echo "Done. Ready to evaluate."
