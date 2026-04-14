#!/usr/bin/env python3

from __future__ import annotations

import json
import sys
import urllib.request
from pathlib import Path


LEADERBOARD = [
    {
        "rank": 1,
        "author": "Adam Betka",
        "title": "64_hard400",
        "leaderboard_public_id": "EQT01-000015",
        "lookup_code": "EQT01-000015",
        "metrics": {
            "gpt_oss_120b": {
                "problem_set": "hard3",
                "accuracy": 65.0,
                "f1_score": 49.6,
                "mean_parse_success": 100.0,
                "mean_cost_usd": 0.00038,
                "mean_elapsed_seconds": 8.8,
            },
            "llama_3_3_70b_instruct": {
                "problem_set": "hard3",
                "accuracy": 51.7,
                "f1_score": 25.5,
                "mean_parse_success": 100.0,
                "mean_cost_usd": 0.00064,
                "mean_elapsed_seconds": 33.1,
            },
        },
    },
    {
        "rank": 2,
        "author": "Heath",
        "title": "distilled-rules-1",
        "leaderboard_public_id": "EQT01-000017",
        "lookup_code": "EQT01-000017",
        "metrics": {
            "gpt_oss_120b": {
                "problem_set": "hard3",
                "accuracy": 58.0,
                "f1_score": 44.7,
                "mean_parse_success": 100.0,
                "mean_cost_usd": 0.00013,
                "mean_elapsed_seconds": 7.2,
            },
            "llama_3_3_70b_instruct": {
                "problem_set": "hard3",
                "accuracy": 55.8,
                "f1_score": 43.5,
                "mean_parse_success": 100.0,
                "mean_cost_usd": 0.00034,
                "mean_elapsed_seconds": 24.7,
            },
        },
    },
    {
        "rank": 3,
        "author": "Arjun Garg",
        "title": "bank_lookup_v5",
        "leaderboard_public_id": "EQT010003",
        "lookup_code": "EQT01-000037",
        "metrics": {
            "gpt_oss_120b": {
                "problem_set": "hard3",
                "accuracy": 60.8,
                "f1_score": 69.3,
                "mean_parse_success": 100.0,
                "mean_cost_usd": 0.00031,
                "mean_elapsed_seconds": 20.8,
            },
            "llama_3_3_70b_instruct": {
                "problem_set": "hard3",
                "accuracy": 47.0,
                "f1_score": 57.4,
                "mean_parse_success": 100.0,
                "mean_cost_usd": 0.00058,
                "mean_elapsed_seconds": 19.2,
            },
        },
    },
    {
        "rank": 4,
        "author": "AMEY",
        "title": "Mathematics Distillation Challenge",
        "leaderboard_public_id": "EQT01-000009",
        "lookup_code": "EQT01-000009",
        "metrics": {
            "gpt_oss_120b": {
                "problem_set": "hard3",
                "accuracy": 56.3,
                "f1_score": 62.4,
                "mean_parse_success": 98.3,
                "mean_cost_usd": 0.00031,
                "mean_elapsed_seconds": 16.7,
            },
            "llama_3_3_70b_instruct": {
                "problem_set": "hard3",
                "accuracy": 51.5,
                "f1_score": 1.0,
                "mean_parse_success": 100.0,
                "mean_cost_usd": 0.00031,
                "mean_elapsed_seconds": 209.3,
            },
        },
    },
    {
        "rank": 5,
        "author": "Adam Betka",
        "title": "98_hard200",
        "leaderboard_public_id": "EQT01-000014",
        "lookup_code": "EQT01-000014",
        "metrics": {
            "gpt_oss_120b": {
                "problem_set": "hard3",
                "accuracy": 56.3,
                "f1_score": 55.9,
                "mean_parse_success": 100.0,
                "mean_cost_usd": 0.00051,
                "mean_elapsed_seconds": 16.1,
            },
            "llama_3_3_70b_instruct": {
                "problem_set": "hard3",
                "accuracy": 51.0,
                "f1_score": 39.5,
                "mean_parse_success": 100.0,
                "mean_cost_usd": 0.00067,
                "mean_elapsed_seconds": 38.3,
            },
        },
    },
    {
        "rank": 6,
        "author": "haha8888haha8888",
        "title": "Zeta999oldfffZPY Zer00logy/Zero-ology Zeropythfon",
        "leaderboard_public_id": "EQT01-000020",
        "lookup_code": "EQT01-000020",
        "metrics": {
            "gpt_oss_120b": {
                "problem_set": "hard3",
                "accuracy": 57.3,
                "f1_score": 42.4,
                "mean_parse_success": 100.0,
                "mean_cost_usd": 0.00018,
                "mean_elapsed_seconds": 1.8,
            },
            "llama_3_3_70b_instruct": {
                "problem_set": "hard3",
                "accuracy": 50.0,
                "f1_score": 63.0,
                "mean_parse_success": 100.0,
                "mean_cost_usd": 0.00058,
                "mean_elapsed_seconds": 47.8,
            },
        },
    },
    {
        "rank": 7,
        "author": "dd",
        "title": "liyeen",
        "leaderboard_public_id": "EQT01-000006",
        "lookup_code": "EQT01-000006",
        "metrics": {
            "gpt_oss_120b": {
                "problem_set": "hard3",
                "accuracy": 55.0,
                "f1_score": 65.9,
                "mean_parse_success": 100.0,
                "mean_cost_usd": 0.00029,
                "mean_elapsed_seconds": 13.2,
            },
            "llama_3_3_70b_instruct": {
                "problem_set": "hard3",
                "accuracy": 51.2,
                "f1_score": 0.0,
                "mean_parse_success": 100.0,
                "mean_cost_usd": 0.00025,
                "mean_elapsed_seconds": 36.9,
            },
        },
    },
    {
        "rank": 8,
        "author": "SimonRJ",
        "title": "Stage 1 Prompt - Simon Watts",
        "leaderboard_public_id": "EQT01-000027",
        "lookup_code": "EQT01-000027",
        "metrics": {
            "gpt_oss_120b": {
                "problem_set": "hard3",
                "accuracy": 58.3,
                "f1_score": 67.3,
                "mean_parse_success": 100.0,
                "mean_cost_usd": 0.00037,
                "mean_elapsed_seconds": 10.0,
            },
            "llama_3_3_70b_instruct": {
                "problem_set": "hard3",
                "accuracy": 46.3,
                "f1_score": 0.0,
                "mean_parse_success": 91.5,
                "mean_cost_usd": 0.00039,
                "mean_elapsed_seconds": 154.0,
            },
        },
    },
    {
        "rank": 9,
        "author": "Emily",
        "title": "near-miss-detector",
        "leaderboard_public_id": "EQT01-000007",
        "lookup_code": "EQT01-000007",
        "metrics": {
            "gpt_oss_120b": {
                "problem_set": "hard3",
                "accuracy": 52.3,
                "f1_score": 5.9,
                "mean_parse_success": 100.0,
                "mean_cost_usd": 0.00019,
                "mean_elapsed_seconds": 8.5,
            },
            "llama_3_3_70b_instruct": {
                "problem_set": "hard3",
                "accuracy": 51.0,
                "f1_score": 0.0,
                "mean_parse_success": 100.0,
                "mean_cost_usd": 0.00012,
                "mean_elapsed_seconds": 10.0,
            },
        },
    },
    {
        "rank": 10,
        "author": "Adam Betka",
        "title": "99_hard69",
        "leaderboard_public_id": "EQT01-000013",
        "lookup_code": "EQT01-000013",
        "metrics": {
            "gpt_oss_120b": {
                "problem_set": "hard3",
                "accuracy": 50.2,
                "f1_score": 20.7,
                "mean_parse_success": 98.3,
                "mean_cost_usd": 0.00045,
                "mean_elapsed_seconds": 18.7,
            },
            "llama_3_3_70b_instruct": {
                "problem_set": "hard3",
                "accuracy": 52.5,
                "f1_score": 28.0,
                "mean_parse_success": 100.0,
                "mean_cost_usd": 0.00043,
                "mean_elapsed_seconds": 28.5,
            },
        },
    },
    {
        "rank": 11,
        "author": "Tom Chan",
        "title": "v1.05",
        "leaderboard_public_id": "EQT01-000028",
        "lookup_code": "EQT01-000028",
        "metrics": {
            "gpt_oss_120b": {
                "problem_set": "hard3",
                "accuracy": 53.0,
                "f1_score": 26.6,
                "mean_parse_success": 99.8,
                "mean_cost_usd": 0.00026,
                "mean_elapsed_seconds": 7.4,
            },
            "llama_3_3_70b_instruct": {
                "problem_set": "hard3",
                "accuracy": 49.3,
                "f1_score": 0.0,
                "mean_parse_success": 96.0,
                "mean_cost_usd": 0.00025,
                "mean_elapsed_seconds": 127.5,
            },
        },
    },
    {
        "rank": 12,
        "author": "Shailesh P",
        "title": "TEST3.5 V+",
        "leaderboard_public_id": "EQT01-000008",
        "lookup_code": "EQT01-000008",
        "metrics": {
            "gpt_oss_120b": {
                "problem_set": "hard3",
                "accuracy": 51.5,
                "f1_score": 18.7,
                "mean_parse_success": 98.8,
                "mean_cost_usd": 0.00016,
                "mean_elapsed_seconds": 7.5,
            },
            "llama_3_3_70b_instruct": {
                "problem_set": "hard3",
                "accuracy": 50.2,
                "f1_score": 27.1,
                "mean_parse_success": 100.0,
                "mean_cost_usd": 0.00024,
                "mean_elapsed_seconds": 19.0,
            },
        },
    },
    {
        "rank": 13,
        "author": "owen",
        "title": "one-way-implication-guard",
        "leaderboard_public_id": "EQT01-000003",
        "lookup_code": "EQT01-000003",
        "metrics": {
            "gpt_oss_120b": {
                "problem_set": "hard3",
                "accuracy": 51.2,
                "f1_score": 3.9,
                "mean_parse_success": 100.0,
                "mean_cost_usd": 0.00019,
                "mean_elapsed_seconds": 8.1,
            },
            "llama_3_3_70b_instruct": {
                "problem_set": "hard3",
                "accuracy": 50.0,
                "f1_score": 6.5,
                "mean_parse_success": 100.0,
                "mean_cost_usd": 0.00015,
                "mean_elapsed_seconds": 22.9,
            },
        },
    },
    {
        "rank": 14,
        "author": "Jiaxuan Zou",
        "title": "3.15",
        "leaderboard_public_id": "EQT01-000012",
        "lookup_code": "EQT01-000012",
        "metrics": {
            "gpt_oss_120b": {
                "problem_set": "hard3",
                "accuracy": 49.8,
                "f1_score": 64.5,
                "mean_parse_success": 98.3,
                "mean_cost_usd": 0.00041,
                "mean_elapsed_seconds": 15.4,
            },
            "llama_3_3_70b_instruct": {
                "problem_set": "hard3",
                "accuracy": 50.7,
                "f1_score": 18.9,
                "mean_parse_success": 100.0,
                "mean_cost_usd": 0.0005,
                "mean_elapsed_seconds": 26.4,
            },
        },
    },
    {
        "rank": 15,
        "author": "Jun B",
        "title": "Pre 1_edit4",
        "leaderboard_public_id": "EQT01-000022",
        "lookup_code": "EQT01-000022",
        "metrics": {
            "gpt_oss_120b": {
                "problem_set": "hard3",
                "accuracy": 49.0,
                "f1_score": 21.4,
                "mean_parse_success": 98.3,
                "mean_cost_usd": 0.00005,
                "mean_elapsed_seconds": 6.7,
            },
            "llama_3_3_70b_instruct": {
                "problem_set": "hard3",
                "accuracy": 51.2,
                "f1_score": 24.1,
                "mean_parse_success": 99.5,
                "mean_cost_usd": 0.00022,
                "mean_elapsed_seconds": 25.5,
            },
        },
    },
    {
        "rank": 16,
        "author": "Reza Jamei",
        "title": "three-element-focus",
        "leaderboard_public_id": "EQT01-000021",
        "lookup_code": "EQT01-000021",
        "metrics": {
            "gpt_oss_120b": {
                "problem_set": "hard3",
                "accuracy": 55.8,
                "f1_score": 64.9,
                "mean_parse_success": 99.5,
                "mean_cost_usd": 0.00043,
                "mean_elapsed_seconds": 15.7,
            },
            "llama_3_3_70b_instruct": {
                "problem_set": "hard3",
                "accuracy": 44.3,
                "f1_score": 0.0,
                "mean_parse_success": 87.8,
                "mean_cost_usd": 0.0005,
                "mean_elapsed_seconds": 38.9,
            },
        },
    },
    {
        "rank": 17,
        "author": "owen",
        "title": "normalize-then-derive",
        "leaderboard_public_id": "EQT01-000002",
        "lookup_code": "EQT01-000002",
        "metrics": {
            "gpt_oss_120b": {
                "problem_set": "hard3",
                "accuracy": 52.3,
                "f1_score": 6.8,
                "mean_parse_success": 100.0,
                "mean_cost_usd": 0.00024,
                "mean_elapsed_seconds": 13.7,
            },
            "llama_3_3_70b_instruct": {
                "problem_set": "hard3",
                "accuracy": 47.5,
                "f1_score": 25.5,
                "mean_parse_success": 100.0,
                "mean_cost_usd": 0.00014,
                "mean_elapsed_seconds": 18.2,
            },
        },
    },
    {
        "rank": 18,
        "author": "Emily",
        "title": "syntax-then-semantics",
        "leaderboard_public_id": "EQT01-000004",
        "lookup_code": "EQT01-000004",
        "metrics": {
            "gpt_oss_120b": {
                "problem_set": "hard3",
                "accuracy": 49.8,
                "f1_score": 9.0,
                "mean_parse_success": 100.0,
                "mean_cost_usd": 0.00022,
                "mean_elapsed_seconds": 5.9,
            },
            "llama_3_3_70b_instruct": {
                "problem_set": "hard3",
                "accuracy": 49.8,
                "f1_score": 9.0,
                "mean_parse_success": 100.0,
                "mean_cost_usd": 0.00029,
                "mean_elapsed_seconds": 43.2,
            },
        },
    },
    {
        "rank": 19,
        "author": "Emily",
        "title": "proof-skeleton-enforcer",
        "leaderboard_public_id": "EQT01-000001",
        "lookup_code": "EQT01-000001",
        "metrics": {
            "gpt_oss_120b": {
                "problem_set": "hard3",
                "accuracy": 49.3,
                "f1_score": 6.6,
                "mean_parse_success": 98.0,
                "mean_cost_usd": 0.00026,
                "mean_elapsed_seconds": 14.1,
            },
            "llama_3_3_70b_instruct": {
                "problem_set": "hard3",
                "accuracy": 50.2,
                "f1_score": 17.4,
                "mean_parse_success": 100.0,
                "mean_cost_usd": 0.00013,
                "mean_elapsed_seconds": 58.7,
            },
        },
    },
    {
        "rank": 20,
        "author": "Sven Benson",
        "title": "IR3",
        "leaderboard_public_id": "EQT010001",
        "lookup_code": "EQT01-000035",
        "metrics": {
            "gpt_oss_120b": {
                "problem_set": "hard3",
                "accuracy": 48.8,
                "f1_score": 25.3,
                "mean_parse_success": 96.0,
                "mean_cost_usd": 0.00042,
                "mean_elapsed_seconds": 57.6,
            },
            "llama_3_3_70b_instruct": {
                "problem_set": "hard3",
                "accuracy": 50.2,
                "f1_score": 20.7,
                "mean_parse_success": 99.8,
                "mean_cost_usd": 0.00031,
                "mean_elapsed_seconds": 13.7,
            },
        },
    },
    {
        "rank": 21,
        "author": "Hao Oy",
        "title": "List of collapse equation...",
        "leaderboard_public_id": "EQT01-000029",
        "lookup_code": "EQT01-000029",
        "metrics": {
            "gpt_oss_120b": {
                "problem_set": "hard3",
                "accuracy": 47.3,
                "f1_score": 63.7,
                "mean_parse_success": 97.0,
                "mean_cost_usd": 0.0004,
                "mean_elapsed_seconds": 11.2,
            },
            "llama_3_3_70b_instruct": {
                "problem_set": "hard3",
                "accuracy": 51.5,
                "f1_score": 37.8,
                "mean_parse_success": 100.0,
                "mean_cost_usd": 0.00071,
                "mean_elapsed_seconds": 26.4,
            },
        },
    },
    {
        "rank": 22,
        "author": "haha8888haha8888",
        "title": "ZPY v3.9.4 Zer00logy/Zero-Ology Ternary 6GemLogic",
        "leaderboard_public_id": "EQT01-000032",
        "lookup_code": "EQT01-000032",
        "metrics": {
            "gpt_oss_120b": {
                "problem_set": "hard3",
                "accuracy": 51.2,
                "f1_score": 0.0,
                "mean_parse_success": 100.0,
                "mean_cost_usd": 0.0003,
                "mean_elapsed_seconds": 5.2,
            },
            "llama_3_3_70b_instruct": {
                "problem_set": "hard3",
                "accuracy": 47.3,
                "f1_score": 8.9,
                "mean_parse_success": 98.0,
                "mean_cost_usd": 0.0006,
                "mean_elapsed_seconds": 33.2,
            },
        },
    },
    {
        "rank": 23,
        "author": "omegaestable",
        "title": "v23c",
        "leaderboard_public_id": "EQT01-000033",
        "lookup_code": "EQT01-000033",
        "metrics": {
            "gpt_oss_120b": {
                "problem_set": "hard3",
                "accuracy": 48.3,
                "f1_score": 65.1,
                "mean_parse_success": 99.8,
                "mean_cost_usd": 0.00025,
                "mean_elapsed_seconds": 19.0,
            },
            "llama_3_3_70b_instruct": {
                "problem_set": "hard3",
                "accuracy": 49.5,
                "f1_score": 65.5,
                "mean_parse_success": 99.8,
                "mean_cost_usd": 0.00037,
                "mean_elapsed_seconds": 11.8,
            },
        },
    },
    {
        "rank": 24,
        "author": "Dixing Xu",
        "title": "test2",
        "leaderboard_public_id": "EQT01-000026",
        "lookup_code": "EQT01-000026",
        "metrics": {
            "gpt_oss_120b": {
                "problem_set": "hard3",
                "accuracy": 48.8,
                "f1_score": 65.5,
                "mean_parse_success": 100.0,
                "mean_cost_usd": 0.00012,
                "mean_elapsed_seconds": 3.4,
            },
            "llama_3_3_70b_instruct": {
                "problem_set": "hard3",
                "accuracy": 36.3,
                "f1_score": 54.1,
                "mean_parse_success": 83.3,
                "mean_cost_usd": 0.00025,
                "mean_elapsed_seconds": 717.5,
            },
        },
    },
]


def fetch_by_code(code: str) -> dict:
    url = f"https://server-9527.sair.foundation/api/contributor-network/by-code/{code}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=20) as response:
        payload = json.load(response)
    data = payload.get("data")
    if not payload.get("ok") or not data:
        raise RuntimeError(f"Contributor-network item not found for {code}")
    return data


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    output_root = repo_root / "data" / "top_50_solutions"
    by_rank_root = output_root / "by_rank"
    by_rank_root.mkdir(parents=True, exist_ok=True)

    index_entries = []

    for row in LEADERBOARD:
        contributor_item = fetch_by_code(row["lookup_code"])

        fetched_author = contributor_item.get("entityName")
        fetched_title = contributor_item.get("cheatsheetTitle")
        if fetched_author != row["author"] or fetched_title != row["title"]:
            raise RuntimeError(
                "Contributor-network mismatch for "
                f"{row['lookup_code']}: expected ({row['author']}, {row['title']}) "
                f"but got ({fetched_author}, {fetched_title})"
            )

        rank_filename = f"{row['rank']:03d}__{row['lookup_code']}.json"
        rank_path = by_rank_root / rank_filename
        rank_payload = {
            "rank": row["rank"],
            "author": row["author"],
            "title": row["title"],
            "leaderboard_public_id": row["leaderboard_public_id"],
            "contributor_network_public_code": row["lookup_code"],
            "rank_source": "Exact user-pasted leaderboard order from 2026-04-14 conversation.",
            "metrics": row["metrics"],
            "contributor_network_item": contributor_item,
        }
        write_json(rank_path, rank_payload)

        index_entries.append(
            {
                "rank": row["rank"],
                "author": row["author"],
                "title": row["title"],
                "leaderboard_public_id": row["leaderboard_public_id"],
                "contributor_network_public_code": row["lookup_code"],
                "rank_file": f"by_rank/{rank_filename}",
                "gpt_oss_120b_accuracy": row["metrics"]["gpt_oss_120b"]["accuracy"],
                "llama_3_3_70b_instruct_accuracy": row["metrics"]["llama_3_3_70b_instruct"]["accuracy"],
            }
        )

    index_payload = {
        "requested_top_n": 50,
        "available_ranked_entries": len(LEADERBOARD),
        "ranking_source": "Exact user-pasted leaderboard order from 2026-04-14 conversation. No re-ranking was applied.",
        "notes": [
            "Some leaderboard Public IDs do not match the contributor-network public code.",
            "When they differ, leaderboard_public_id preserves the pasted value and contributor_network_public_code is the fetch key used to retrieve the public cheatsheet.",
            "To get the nth-best solution, open data/top_50_solutions/by_rank/{n:03d}__*.json or use tools/get_ranked_solution.py.",
        ],
        "entries": index_entries,
    }
    write_json(output_root / "index.json", index_payload)

    readme = """# Top 50 Solutions

This folder preserves the exact leaderboard order pasted by the user on 2026-04-14.

- `index.json` is the master rank map.
- `by_rank/001__...json` is the 1st-best solution.
- `by_rank/002__...json` is the 2nd-best solution.
- The repository currently contains 24 ranked entries because only 24 leaderboard rows were provided.

Each rank JSON includes:

- the preserved leaderboard rank
- the pasted leaderboard public ID
- the contributor-network public code used for fetching
- the pasted model metrics
- the full public contributor-network cheatsheet payload
"""
    (output_root / "README.md").write_text(readme, encoding="utf-8")

    print(f"Wrote {len(LEADERBOARD)} ranked solutions to {output_root}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
