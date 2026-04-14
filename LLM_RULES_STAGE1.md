# Stage 1 LLM Operating Rules

As of April 14, 2026, these are the relevant operating constraints for the SAIR Mathematics Distillation Challenge, Equational Theories Stage 1.

## Core evaluation rules

- The task is single-turn implication classification over magmas: decide whether Equation 1 implies Equation 2.
- Participants submit a complete prompt: prompt template plus cheatsheet text.
- The evaluator substitutes `{{equation1}}` and `{{equation2}}` into the submitted prompt text.
- Stage 1 cheatsheet size cap is `10KB`.
- Offline evaluation is `no-tools`: no browser, web search, or external internet retrieval.
- The offline evaluation set is private and different from the public selected Stage 1 problems.
- Recommended operational target from the organizers: average cost no more than `USD 0.01` per problem and solve time no more than `10 minutes` per problem.

## Official evaluation models

The current planned Stage 1 evaluation models are:

1. `openai/gpt-oss-120b`
2. `meta-llama/llama-3.3-70b-instruct`
3. `google/gemma-4-31b-it`

These are equally weighted in Stage 1 evaluation.

## Current official judge configuration

From the public judge repository's current `evaluation_models.json`:

- `allow_fallbacks = false`
- `max_output_tokens = 16384` for all three official models
- `temperature = 0.0` for all three official models
- `seed = 0` where supported
- `gpt-oss-120b` uses reasoning mode `low`
- `llama-3.3-70b-instruct` uses reasoning mode `disabled`
- `gemma-4-31b-it` uses reasoning mode `disabled`

Pinned provider routes:

- `gpt-oss-120b` -> `deepinfra/bf16`
- `llama-3-3-70b-instruct` -> `deepinfra/fp8`
- `gemma-4-31b-it` -> `novita/bf16`

## Per-model operating constraints

The table below combines the official judge config with OpenRouter-published context windows.

| Alias | Model | Pinned route | Reasoning | Max output tokens | Published context window | Approx max prompt input |
| --- | --- | --- | --- | ---: | ---: | ---: |
| `gpt-oss-120b` | `openai/gpt-oss-120b` | `deepinfra/bf16` | `low` | `16384` | `131072` | about `114688` |
| `llama-3-3-70b-instruct` | `meta-llama/llama-3.3-70b-instruct` | `deepinfra/fp8` | `disabled` | `16384` | `131072` | about `114688` |
| `gemma-4-31b-it` | `google/gemma-4-31b-it` | `novita/bf16` | `disabled` | `16384` | `262144` | about `245760` |

Notes:

- "Approx max prompt input" is an inference, computed as `context window - 16384`.
- I did not find a separate explicit cap on total rendered prompt size in the public judge repo beyond the `10KB` cheatsheet cap and the model/provider context window.

## Prompt/rendering behavior

- The public prompt renderer performs literal substitution only.
- Supported placeholders are:
  - `{{equation1}}`
  - `{{ equation1 }}`
  - `{{equation2}}`
  - `{{ equation2 }}`
- Equations are inserted verbatim with no escaping.
- There is no full template engine in the public renderer.
- The example prompt in the judge repo is only a reference; participants are not restricted to that template.

## Output parsing behavior

The public verdict extractor is permissive. It recognizes:

- Boxed verdicts such as `\boxed{TRUE}` or `\boxed{FALSE}`
- Labeled verdicts such as:
  - `VERDICT: TRUE`
  - `ANSWER: FALSE`
  - `FINAL ANSWER: TRUE`
  - `RESULT: FALSE`
  - `OUTPUT_RESULT: TRUE`
- A bare `TRUE` or `FALSE` on the first or last non-empty line

Practical recommendation:

- Still force the model to emit a clean line `VERDICT: TRUE` or `VERDICT: FALSE`.
- Keep the answer format rigid even though the parser accepts several variants.

## Environment recommendations

For local testing against the public judge:

- Python `3.9+`
- OpenRouter API access
- Match the official pinned providers and no-fallback setting
- Test under the same `no-tools` assumption as offline evaluation
- Keep responses concise and parseable

## Important discrepancy

The local repo file `SAIR_INSTRUCTIONS.md` mentions `max output tokens 8192` in one section.

The current official public judge repository uses `16384` in `evaluation_models.json`.

Treat the current public judge repository as the more authoritative source unless the organizers publish a newer override.

## Contributor page note

The contributor-network URL was reachable, but in this environment it appeared to be a JavaScript-rendered shell without extractable text, so it did not provide additional technical constraints beyond the published repo and instructions.

URL checked:

- `https://competition.sair.foundation/contributor-network?competition=mathematics-distillation-challenge-equational-theories-stage1`

## Sources

- Local repo instructions: `SAIR_INSTRUCTIONS.md`
- Official judge repo: `https://github.com/SAIRcompetition/equational-theories-stage1-judge`
- Official model config: `https://github.com/SAIRcompetition/equational-theories-stage1-judge/blob/main/evaluation_models.json`
- Prompt renderer: `https://github.com/SAIRcompetition/equational-theories-stage1-judge/blob/main/prompt.py`
- Verdict extractor: `https://github.com/SAIRcompetition/equational-theories-stage1-judge/blob/main/judge.py`
- OpenRouter model pages:
  - `https://openrouter.ai/openai/gpt-oss-120b`
  - `https://openrouter.ai/meta-llama/llama-3.3-70b-instruct`
  - `https://openrouter.ai/google/gemma-4-31b-it`
