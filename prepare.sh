#!/usr/bin/env bash
set -e

cd "$(dirname "$0")"

mkdir -p data data/public_subsets

# Clone the official judge repo (for prompt.py and judge.py)
if [ ! -d "judge_repo" ]; then
    echo "Cloning judge repo..."
    git clone https://github.com/SAIRcompetition/equational-theories-stage1-judge.git judge_repo
else
    echo "Judge repo already cloned."
fi

# Install Python dependencies if they are missing.
python3 - <<'PY'
import importlib.util
import subprocess
import sys

required = {
    "httpx": "httpx>=0.27",
    "datasets": "datasets",
}
missing = [
    requirement
    for module_name, requirement in required.items()
    if importlib.util.find_spec(module_name) is None
]

if missing:
    subprocess.check_call(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--quiet",
            "--user",
            "--break-system-packages",
            *missing,
        ]
    )
PY

# Download the official public selected Stage 1 problems from Hugging Face.
# This intentionally excludes the older local-only `hard` subset so the merged
# file matches SAIR's published public selected set: normal + hard1 + hard2 +
# hard3 = 1,669 problems.
echo "Ensuring official public selected dataset is present..."
python - <<'PY'
from collections import Counter
from datasets import load_dataset
import json
from pathlib import Path
import random

repo_root = Path(".")
data_dir = repo_root / "data"
subsets_dir = data_dir / "public_subsets"
subsets_dir.mkdir(parents=True, exist_ok=True)

dataset_name = "SAIRfoundation/equational-theories-selected-problems"
subset_order = ["normal", "hard1", "hard2", "hard3"]
expected_counts = {"normal": 1000, "hard1": 69, "hard2": 200, "hard3": 400}

all_problems_path = data_dir / "all_problems.jsonl"
iter_100_path = data_dir / "iter_100.jsonl"

iter_targets = {
    ("normal", True): 30,
    ("normal", False): 30,
    ("hard1", True): 1,
    ("hard1", False): 3,
    ("hard2", True): 6,
    ("hard2", False): 6,
    ("hard3", True): 12,
    ("hard3", False): 12,
}


def infer_subset(problem_id: str) -> str | None:
    for subset in subset_order:
        if problem_id.startswith(f"{subset}_"):
            return subset
    return None


def existing_counts_ok() -> bool:
    if not all_problems_path.exists():
        return False

    counts = Counter()
    unknown = 0
    total = 0
    with all_problems_path.open() as src:
        for line in src:
            if not line.strip():
                continue
            total += 1
            row = json.loads(line)
            subset = infer_subset(str(row.get("id", "")))
            if subset is None:
                unknown += 1
                continue
            counts[subset] += 1

    return (
        dict(counts) == expected_counts
        and unknown == 0
        and total == sum(expected_counts.values())
    )


if existing_counts_ok():
    print("Public selected dataset already matches official Stage 1 counts.")
else:
    print("Downloading / refreshing public selected dataset...")
    merged_rows = []
    for subset in subset_order:
        subset_path = subsets_dir / f"{subset}.jsonl"
        ds = load_dataset(dataset_name, subset, split="train")
        rows = list(ds)
        if len(rows) != expected_counts[subset]:
            raise RuntimeError(
                f"Subset {subset} has {len(rows)} rows, expected {expected_counts[subset]}"
            )
        with subset_path.open("w") as dst:
            for row in rows:
                dst.write(json.dumps(row, ensure_ascii=False) + "\n")
        merged_rows.extend(rows)

    with all_problems_path.open("w") as dst:
        for row in merged_rows:
            dst.write(json.dumps(row, ensure_ascii=False) + "\n")

    print("Wrote data/all_problems.jsonl and data/public_subsets/*.jsonl")


all_rows = []
with all_problems_path.open() as src:
    for index, line in enumerate(src):
        row = json.loads(line)
        row["_source_index"] = index
        all_rows.append(row)

strata = {(subset, answer): [] for subset in subset_order for answer in (True, False)}
for row in all_rows:
    subset = infer_subset(str(row["id"]))
    if subset is None:
        raise RuntimeError(f"Unexpected problem id outside official public set: {row['id']}")
    strata[(subset, bool(row["answer"]))].append(row)

rng = random.Random(0)
selected = []
for key, target in iter_targets.items():
    rows = list(strata[key])
    if len(rows) < target:
        raise RuntimeError(f"Not enough rows in stratum {key}: have {len(rows)}, need {target}")
    picks = rng.sample(rows, target)
    selected.extend(picks)

selected.sort(key=lambda row: row["_source_index"])
with iter_100_path.open("w") as dst:
    for row in selected:
        row = dict(row)
        row.pop("_source_index", None)
        dst.write(json.dumps(row, ensure_ascii=False) + "\n")

print("Wrote data/iter_100.jsonl (deterministic stratified sample)")
PY

# Build a tiny balanced hard3 smoke split for parser / infra sanity checks.
rm -f "data/sair_smoke_20.jsonl"
echo "Building smoke split..."
python -c "
import json

true_count = 0
false_count = 0
rows = []
target_per_label = 3

with open('data/all_problems.jsonl') as src:
    for line in src:
        row = json.loads(line)
        if not row['id'].startswith('hard3_'):
            continue
        if row['answer'] and true_count < target_per_label:
            rows.append(row)
            true_count += 1
        elif (not row['answer']) and false_count < target_per_label:
            rows.append(row)
            false_count += 1
        if true_count >= target_per_label and false_count >= target_per_label:
            break

if true_count < target_per_label or false_count < target_per_label:
    raise RuntimeError('Could not derive the smoke split from hard3')

with open('data/sair_smoke_6.jsonl', 'w') as dst:
    for row in rows:
        dst.write(json.dumps(row, ensure_ascii=False) + '\n')

print('Wrote data/sair_smoke_6.jsonl')
"

echo "Done. Ready to evaluate."
