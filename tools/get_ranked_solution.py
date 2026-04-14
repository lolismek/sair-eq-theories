#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def load_index(repo_root: Path) -> dict:
    index_path = repo_root / "data" / "top_50_solutions" / "index.json"
    if not index_path.exists():
        raise FileNotFoundError(
            "Missing data/top_50_solutions/index.json. Run tools/build_top_50_solutions.py first."
        )
    return json.loads(index_path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Show the nth-ranked SAIR cheatsheet.")
    parser.add_argument("rank", type=int, help="1-based rank")
    parser.add_argument(
        "--show-content",
        action="store_true",
        help="Print the cheatsheet content after the summary.",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    index = load_index(repo_root)
    entries = index["entries"]

    if args.rank < 1 or args.rank > len(entries):
        raise SystemExit(f"Rank must be between 1 and {len(entries)}")

    entry = entries[args.rank - 1]
    rank_path = repo_root / "data" / "top_50_solutions" / entry["rank_file"]
    payload = json.loads(rank_path.read_text(encoding="utf-8"))

    print(f"rank: {payload['rank']}")
    print(f"author: {payload['author']}")
    print(f"title: {payload['title']}")
    print(f"leaderboard_public_id: {payload['leaderboard_public_id']}")
    print(f"contributor_network_public_code: {payload['contributor_network_public_code']}")
    print(f"file: {rank_path}")

    if args.show_content:
        print()
        print(payload["contributor_network_item"]["cheatsheetContent"])

    return 0


if __name__ == "__main__":
    sys.exit(main())
