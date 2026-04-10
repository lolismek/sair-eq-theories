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

echo "Done. Ready to evaluate."
