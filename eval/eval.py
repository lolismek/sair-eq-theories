#!/usr/bin/env python3
"""
Evaluate a prompt template against equational theory problems.

This evaluator supports two practical tracks:

1. `fast` — 100 fixed public problems for inner-loop prompt iteration
2. `sair-public` — all 1,869 public problems under SAIR-like Gemma settings

It also supports `sair-smoke`, which mirrors the official public 20-problem
hard3 smoke-test semantics.

Env vars:
    SAIR_MODEL_URL    — base URL of the vLLM server (required)
    SAIR_API_KEY      — bearer token for the vLLM server (required)
    SAIR_BATCH        — optional: 1/true to prefer the Modal batch endpoint
    SAIR_BATCH_CONCURRENCY — optional: internal concurrency for batch mode
    SAIR_STREAM       — optional: 1/true to force streaming, 0/false to disable
    SAIR_CONCURRENCY  — optional: override direct-request concurrency
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
# SAIR's official local Gemma config uses a 16384 output-token cap as of
# 2026-04-13. Self-hosted vLLM rejects that exact value when the prompt is
# non-empty because prompt tokens and output tokens must share the same
# 16384-token context window, so we clamp slightly for compatibility.
OFFICIAL_MAX_TOKENS_CAP = 16384
REQUEST_MAX_TOKENS = 16000
TEMPERATURE = 0.0
SEED = 0
CALL_TIMEOUT = 600  # seconds per direct LLM call
BATCH_ENDPOINT = "/sair/batch_chat_completions"
BATCH_JOB_CREATE_ENDPOINT = "/sair/batch_jobs"
MODAL_DEFAULT_BATCH_CONCURRENCY = 8
DEFAULT_BATCH_CONCURRENCY = 4
MODAL_DEFAULT_CONCURRENCY = 1
DEFAULT_CONCURRENCY = 3
READY_TIMEOUT = 60 * 15
READY_POLL_SECONDS = 5
BATCH_CONNECT_RETRIES = 3
BATCH_POLL_SECONDS = 5

PRESETS = {
    "fast": {
        "path": REPO_ROOT / "data" / "iter_100.jsonl",
        "description": "100 fixed iteration problems (50 normal + 50 hard3)",
    },
    "sair-public": {
        "path": REPO_ROOT / "data" / "all_problems.jsonl",
        "description": "1,869 public problems under Gemma-only SAIR-like settings",
    },
    "sair-smoke": {
        "path": REPO_ROOT / "data" / "sair_smoke_20.jsonl",
        "description": "20 hard3 public smoke problems using official SAIR semantics",
    },
}


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


def should_batch(url: str) -> bool:
    forced = _env_truthy("SAIR_BATCH")
    if forced is not None:
        return forced
    return _looks_like_modal_url(url)


def resolve_concurrency(url: str, use_stream: bool) -> int:
    override = os.environ.get("SAIR_CONCURRENCY")
    if override:
        return max(1, int(override))
    if _looks_like_modal_url(url):
        # Concurrent public requests to the Modal web endpoint were unstable in
        # practice, so keep direct-call mode conservative and prefer batch mode.
        return MODAL_DEFAULT_CONCURRENCY
    return DEFAULT_CONCURRENCY


def resolve_batch_concurrency(url: str) -> int:
    override = os.environ.get("SAIR_BATCH_CONCURRENCY")
    if override:
        return max(1, int(override))
    if _looks_like_modal_url(url):
        return MODAL_DEFAULT_BATCH_CONCURRENCY
    return DEFAULT_BATCH_CONCURRENCY


def load_problems(path: Path) -> list[dict]:
    with path.open() as f:
        return [json.loads(line) for line in f if line.strip()]


def derive_sair_smoke_problems(all_problems: list[dict]) -> list[dict]:
    """Derive the official public smoke split from the full public dataset.

    SAIR's smoke set is the first 10 TRUE and first 10 FALSE problems from the
    hard3 subset, preserving original order.
    """
    selected = []
    true_count = 0
    false_count = 0

    for problem in all_problems:
        if not str(problem.get("id", "")).startswith("hard3_"):
            continue

        answer = bool(problem["answer"])
        if answer and true_count < 10:
            selected.append(problem)
            true_count += 1
        elif not answer and false_count < 10:
            selected.append(problem)
            false_count += 1

        if true_count >= 10 and false_count >= 10:
            break

    if true_count < 10 or false_count < 10:
        raise RuntimeError(
            "Unable to derive SAIR smoke problems from data/all_problems.jsonl"
        )

    return selected


def resolve_problem_set(
    preset: str,
    problems_override: str | None,
) -> tuple[list[dict], str, str]:
    if problems_override:
        path = Path(problems_override)
        return load_problems(path), "custom", str(path)

    preset_info = PRESETS[preset]
    path = preset_info["path"]
    if path.exists():
        return load_problems(path), preset, str(path)

    if preset == "sair-smoke":
        fallback_path = PRESETS["sair-public"]["path"]
        if not fallback_path.exists():
            raise FileNotFoundError(
                "Missing data/sair_smoke_20.jsonl and data/all_problems.jsonl"
            )
        return (
            derive_sair_smoke_problems(load_problems(fallback_path)),
            preset,
            f"{path} (derived from {fallback_path})",
        )

    raise FileNotFoundError(f"Missing problems file: {path}")


async def wait_until_ready(url: str, headers: dict[str, str]) -> None:
    if not _looks_like_modal_url(url):
        return

    deadline = asyncio.get_running_loop().time() + READY_TIMEOUT
    health_errors = []

    async with httpx.AsyncClient(
        timeout=httpx.Timeout(connect=10.0, read=10.0, write=10.0, pool=10.0),
        headers=headers,
        trust_env=False,
    ) as client:
        while True:
            try:
                resp = await client.get(f"{url}/healthz")
                if resp.is_success:
                    return
            except Exception as exc:
                health_errors.append(str(exc))
                health_errors = health_errors[-3:]

            if asyncio.get_running_loop().time() >= deadline:
                detail = "; ".join(health_errors) if health_errors else "timed out"
                raise RuntimeError(
                    f"Modal endpoint did not become ready within {READY_TIMEOUT}s: {detail}"
                )
            await asyncio.sleep(READY_POLL_SECONDS)


async def call_model(
    client: httpx.AsyncClient, url: str, prompt_text: str, use_stream: bool
) -> tuple[str, str | None]:
    """Call the vLLM endpoint, optionally via streaming SSE."""
    body = {
        "model": MODEL_ID,
        "messages": [{"role": "user", "content": prompt_text}],
        "temperature": TEMPERATURE,
        "max_tokens": REQUEST_MAX_TOKENS,
        "seed": SEED,
    }

    if use_stream:
        body["stream"] = True
        chunks = []
        finish_reason = None

        async with client.stream("POST", f"{url}/v1/chat/completions", json=body) as resp:
            if not resp.is_success:
                detail = await resp.aread()
                raise httpx.HTTPStatusError(
                    f"{resp.status_code} {resp.reason_phrase}: {detail.decode(errors='replace')}",
                    request=resp.request,
                    response=resp,
                )
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
    if not resp.is_success:
        raise httpx.HTTPStatusError(
            f"{resp.status_code} {resp.reason_phrase}: {resp.text}",
            request=resp.request,
            response=resp,
        )
    data = resp.json()
    choice = data["choices"][0]
    return choice["message"]["content"], choice.get("finish_reason")


async def iter_batch_results(
    client: httpx.AsyncClient,
    url: str,
    prompts: list[str],
    batch_concurrency: int,
):
    request_body = {
        "prompts": prompts,
        "model": MODEL_ID,
        "temperature": TEMPERATURE,
        "max_tokens": REQUEST_MAX_TOKENS,
        "seed": SEED,
        "concurrency": batch_concurrency,
    }

    job_id = None
    yielded_any = False
    for attempt in range(1, BATCH_CONNECT_RETRIES + 1):
        try:
            if job_id is None:
                create_resp = await client.post(
                    f"{url}{BATCH_JOB_CREATE_ENDPOINT}",
                    json=request_body,
                )
                create_resp.raise_for_status()
                payload = create_resp.json()
                job_id = payload["job_id"]
            next_seq = 0

            while True:
                try:
                    status_resp = await client.get(
                        f"{url}{BATCH_JOB_CREATE_ENDPOINT}/{job_id}",
                        params={"after_seq": next_seq},
                    )
                    status_resp.raise_for_status()
                    status = status_resp.json()
                except httpx.HTTPStatusError:
                    raise
                except (
                    httpx.ConnectError,
                    httpx.RemoteProtocolError,
                    httpx.ReadError,
                    httpx.ReadTimeout,
                ):
                    await asyncio.sleep(BATCH_POLL_SECONDS)
                    continue

                for row in status.get("results", []):
                    next_seq = max(next_seq, row["seq"])
                    clean_row = dict(row)
                    clean_row.pop("seq", None)
                    yielded_any = True
                    yield clean_row

                if status.get("done"):
                    if status.get("error"):
                        raise RuntimeError(status["error"])
                    return
                await asyncio.sleep(BATCH_POLL_SECONDS)
        except (
            httpx.ConnectError,
            httpx.RemoteProtocolError,
            httpx.ReadError,
            httpx.ReadTimeout,
        ):
            if attempt == BATCH_CONNECT_RETRIES:
                raise
            await asyncio.sleep(min(5 * attempt, 15))
        except httpx.HTTPStatusError:
            if yielded_any or job_id is not None:
                raise
            raise


async def run(args: argparse.Namespace) -> int:
    url = os.environ.get("SAIR_MODEL_URL", "").rstrip("/")
    api_key = os.environ.get("SAIR_API_KEY", "")

    if not url:
        print("Error: SAIR_MODEL_URL env var must be set", file=sys.stderr)
        return 1
    if not api_key:
        print("Error: SAIR_API_KEY env var must be set", file=sys.stderr)
        return 1

    use_batch = should_batch(url)
    use_stream = should_stream(url)
    headers = {"Authorization": f"Bearer {api_key}"}
    await wait_until_ready(url, headers)
    prompt_path = Path(args.prompt_file)
    prompt_template = prompt_path.read_text()
    problems, preset_name, problems_label = resolve_problem_set(
        preset=args.preset,
        problems_override=args.problems,
    )
    rendered_prompts = [
        render_prompt(prompt_template, problem["equation1"], problem["equation2"])
        for problem in problems
    ]

    total = len(problems)
    correct = 0
    no_verdict = 0
    errors = 0
    seen_indices: set[int] = set()

    print(
        json.dumps(
            {
                "preset": preset_name,
                "problems": problems_label,
                "prompt_file": str(prompt_path),
                "model": MODEL_ID,
                "temperature": TEMPERATURE,
                "official_max_tokens_cap": OFFICIAL_MAX_TOKENS_CAP,
                "request_max_tokens": REQUEST_MAX_TOKENS,
                "seed": SEED,
            }
        ),
        flush=True,
    )

    def record_result(i: int, text: str | None, error_text: str | None) -> None:
        nonlocal correct, no_verdict, errors
        if i in seen_indices:
            return
        seen_indices.add(i)
        problem = problems[i - 1]
        pid = problem.get("id", f"#{i}")

        if error_text is not None:
            status = f"ERROR: {error_text}"
        else:
            result, _ = judge_response(text or "", expected_answer=problem["answer"])
            if result is True:
                status = "CORRECT"
                correct += 1
            elif result is False:
                status = "WRONG"
            else:
                status = "NO_VERDICT"
                no_verdict += 1

        if status.startswith("ERROR"):
            errors += 1

        print(
            json.dumps(
                {
                    "i": i,
                    "id": pid,
                    "status": status,
                    "expected": problem["answer"],
                },
                ensure_ascii=False,
            ),
            flush=True,
        )

    if use_batch:
        batch_concurrency = resolve_batch_concurrency(url)
        print(
            json.dumps(
                {
                    "mode": "batch",
                    "batch_concurrency": batch_concurrency,
                    "url": url,
                }
            ),
            flush=True,
        )
        batch_timeout = httpx.Timeout(connect=30.0, write=60.0, read=None, pool=60.0)
        try:
            async with httpx.AsyncClient(
                timeout=batch_timeout,
                headers=headers,
                trust_env=False,
            ) as client:
                async for row in iter_batch_results(
                    client=client,
                    url=url,
                    prompts=rendered_prompts,
                    batch_concurrency=batch_concurrency,
                ):
                    record_result(
                        i=row["i"],
                        text=row.get("content"),
                        error_text=row.get("error"),
                    )
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code not in {404, 405}:
                raise
            print(
                json.dumps(
                    {
                        "warning": "batch endpoint unavailable, falling back to direct mode",
                        "status_code": exc.response.status_code,
                    }
                ),
                flush=True,
            )
            use_batch = False

    if not use_batch:
        concurrency = resolve_concurrency(url, use_stream)
        sem = asyncio.Semaphore(concurrency)

        async def process(i: int, prompt_text: str) -> tuple[int, str | None, str | None]:
            async with sem:
                try:
                    text, _ = await call_model(client, url, prompt_text, use_stream)
                    return i, text, None
                except Exception as exc:
                    return i, None, str(exc)

        print(
            json.dumps(
                {
                    "mode": "direct",
                    "streaming": use_stream,
                    "concurrency": concurrency,
                    "url": url,
                }
            ),
            flush=True,
        )

        async with httpx.AsyncClient(
            timeout=CALL_TIMEOUT,
            headers=headers,
            trust_env=False,
        ) as client:
            tasks = [
                process(i, prompt_text)
                for i, prompt_text in enumerate(rendered_prompts, 1)
            ]
            for coro in asyncio.as_completed(tasks):
                i, text, error_text = await coro
                record_result(i=i, text=text, error_text=error_text)

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
        "--preset",
        choices=sorted(PRESETS),
        default="fast",
        help="Named evaluation preset",
    )
    parser.add_argument(
        "--problems",
        type=str,
        default=None,
        help="Optional path to a JSONL problems file; overrides --preset",
    )
    parser.add_argument(
        "--prompt-file",
        type=str,
        default=str(REPO_ROOT / "prompt.txt"),
        help="Prompt template file to render for each problem",
    )
    args = parser.parse_args()
    return asyncio.run(run(args))


if __name__ == "__main__":
    raise SystemExit(main())
