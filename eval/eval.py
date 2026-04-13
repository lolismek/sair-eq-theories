#!/usr/bin/env python3
"""
Evaluate a prompt template against equational theory problems.

Sends each problem to the vLLM endpoint, extracts TRUE/FALSE verdicts
using the official judge, and reports accuracy.

Env vars:
    SAIR_MODEL_URL    — base URL of the vLLM server (required)
    SAIR_API_KEY      — bearer token for the vLLM server (required)
    SAIR_STREAM       — optional: 1/true to force streaming, 0/false to disable
    SAIR_CONCURRENCY  — optional: override request concurrency
"""

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path

import httpx

REPO_ROOT = Path(__file__).resolve().parents[1]
JUDGE_ROOT = REPO_ROOT / "judge_repo"

sys.path.insert(0, str(JUDGE_ROOT))

from prompt import render_prompt  # noqa: E402
from judge import judge_response  # noqa: E402

MODEL_ID = "google/gemma-4-31b-it"
MAX_TOKENS = 8192
TEMPERATURE = 0.0
SEED = 0
CALL_TIMEOUT = 600  # seconds per LLM call


def _looks_like_modal_url(url: str) -> bool:
    return ".modal.run" in url or ".modal.site" in url


def _env_truthy(name: str) -> bool | None:
    value = os.environ.get(name)
    if value is None:
        return None
    value = value.strip().lower()
    if value in {"1", "true", "yes", "on"}:
        return True
    if value in {"0", "false", "no", "off"}:
        return False
    raise ValueError(f"{name} must be one of 1/0/true/false/yes/no/on/off")


def should_stream(url: str) -> bool:
    forced = _env_truthy("SAIR_STREAM")
    if forced is not None:
        return forced
    # Modal benefits from streaming because long non-streaming responses can idle out.
    return _looks_like_modal_url(url)


def resolve_concurrency(url: str, use_stream: bool) -> int:
    override = os.environ.get("SAIR_CONCURRENCY")
    if override:
        return max(1, int(override))
    return 1 if use_stream and _looks_like_modal_url(url) else 3


def load_problems(path: Path) -> list[dict]:
    with path.open() as f:
        return [json.loads(line) for line in f if line.strip()]


async def call_model(
    client: httpx.AsyncClient, url: str, prompt_text: str, use_stream: bool
) -> tuple[str, str | None]:
    """Call the vLLM endpoint, optionally via streaming SSE."""
    body = {
        "model": MODEL_ID,
        "messages": [{"role": "user", "content": prompt_text}],
        "temperature": TEMPERATURE,
        "max_tokens": MAX_TOKENS,
        "seed": SEED,
    }

    if use_stream:
        body["stream"] = True
        chunks = []
        finish_reason = None

        async with client.stream("POST", f"{url}/v1/chat/completions", json=body) as resp:
            resp.raise_for_status()
            async for line in resp.aiter_lines():
                if not line.startswith("data: "):
                    continue
                payload = line[len("data: ") :]
                if payload.strip() == "[DONE]":
                    break
                data = json.loads(payload)
                choice = data["choices"][0]
                delta = choice.get("delta", {})
                if delta.get("content"):
                    chunks.append(delta["content"])
                if choice.get("finish_reason"):
                    finish_reason = choice["finish_reason"]
        return "".join(chunks), finish_reason

    resp = await client.post(f"{url}/v1/chat/completions", json=body)
    resp.raise_for_status()
    data = resp.json()
    choice = data["choices"][0]
    return choice["message"]["content"], choice.get("finish_reason")


async def run(args: argparse.Namespace) -> int:
    url = os.environ.get("SAIR_MODEL_URL", "").rstrip("/")
    api_key = os.environ.get("SAIR_API_KEY", "")

    if not url:
        print("Error: SAIR_MODEL_URL env var must be set", file=sys.stderr)
        return 1
    if not api_key:
        print("Error: SAIR_API_KEY env var must be set", file=sys.stderr)
        return 1

    use_stream = should_stream(url)
    concurrency = resolve_concurrency(url, use_stream)
    headers = {"Authorization": f"Bearer {api_key}"}
    prompt_template = (REPO_ROOT / "prompt.txt").read_text()
    problems = load_problems(Path(args.problems))

    total = len(problems)
    correct = 0
    no_verdict = 0
    errors = 0
    sem = asyncio.Semaphore(concurrency)

    async def process(i: int, problem: dict) -> dict:
        pid = problem.get("id", f"#{i}")
        rendered = render_prompt(
            prompt_template, problem["equation1"], problem["equation2"]
        )
        async with sem:
            try:
                text, finish = await call_model(client, url, rendered, use_stream)
                result, reason = judge_response(
                    text, expected_answer=problem["answer"]
                )
                if result is True:
                    st = "CORRECT"
                elif result is False:
                    st = "WRONG"
                else:
                    st = "NO_VERDICT"
            except Exception as e:
                st = f"ERROR: {e}"
                result = None
        return {"i": i, "id": pid, "status": st, "expected": problem["answer"], "result": result}

    print(
        json.dumps(
            {
                "streaming": use_stream,
                "concurrency": concurrency,
                "url": url,
            }
        ),
        flush=True,
    )

    async with httpx.AsyncClient(timeout=CALL_TIMEOUT, headers=headers) as client:
        tasks = [process(i, p) for i, p in enumerate(problems, 1)]
        for coro in asyncio.as_completed(tasks):
            row = await coro
            if row["status"] == "CORRECT":
                correct += 1
            elif row["status"] == "NO_VERDICT":
                no_verdict += 1
            elif row["status"].startswith("ERROR"):
                errors += 1
            print(
                json.dumps(
                    {"i": row["i"], "id": row["id"], "status": row["status"], "expected": row["expected"]},
                    ensure_ascii=False,
                ),
                flush=True,
            )

    accuracy = correct / total if total > 0 else 0.0
    print("---")
    print(f"total:      {total}")
    print(f"correct:    {correct}")
    print(f"no_verdict: {no_verdict}")
    print(f"errors:     {errors}")
    print(f"accuracy:   {accuracy:.4f}")
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--problems",
        type=str,
        default=str(REPO_ROOT / "data" / "iter_100.jsonl"),
        help="Path to JSONL problems file",
    )
    args = parser.parse_args()
    return asyncio.run(run(args))


if __name__ == "__main__":
    raise SystemExit(main())
