Overview
This competition explores a core question in AI for mathematics: can strong mathematical reasoning be distilled into a compact, human-readable cheatsheet that improves LLM performance on formal tasks?

This competition is organized by:

Damek Davis (Associate Professor, Department of Statistics and Data Science, University of Pennsylvania)

Terence Tao (Fields Medalist, Professor at UCLA, Co-Founder of SAIR Foundation)

and SAIR Foundation.

The setup is inspired by Honda, Murakami, and Zhang (2025), Distilling Many-Shot In-Context Learning into a Cheat Sheet.

Our difference is that cheatsheets are discovered through an open competition process rather than a single model query.

Background
The pilot task is equational implication over magmas: given Equation 1 and Equation 2, determine whether Equation 1 implies Equation 2.

This challenge is based on the Equational Theories Project:

Example: E_4: x = x * y implies E_3: x = x * x.

Raw implication graph: export_raw_implications
Law list (4694 laws): equations.txt
Core Task
Participants submit a complete prompt for Stage 1. A complete prompt means the full prompt template and cheatsheet text together, as they will actually be sent to the model.

The model then solves implication problems of the form:

Does Equation 1 imply Equation 2?

In Stage 1, the expected behavior is to provide a true/false answer to the question.

Participants are responsible for the formatting of their own prompt, including placeholders such as { equation1 } and { equation2 }, and for ensuring that the model output can be parsed correctly.

Evaluation Format
Stage 1 (Lower Barrier)
Task: determine whether Equation 1 implies Equation 2.
Cheatsheet size cap: 10KB.
Scoring focus: correctness (right/wrong) only.
Stage 2 (Higher Difficulty)
Harder benchmark setting than Stage 1.

Participants may be required to submit one of:
an explicit counterexample,
an explicit Lean proof/disproof,
or a calibrated confidence probability for implication truth.
Detailed rules: TBD.
Key Dates
Stage 1 starts: March 14, 15:09:26 (UTC+14), 2026
Stage 1 submission deadline: April 20, 23:59 AoE (Anywhere on Earth), 2026
Stage 1 leaderboard release: on or before April 30, 2026
Stage 2 starts: May 1, 2026
Stage 1 Training and Evaluation Rules
Public selected problem subsets for Stage 1:
normal: 1000 normal-difficulty problems. Hugging Face: normal
hard1: 69 hard-difficulty problems. Hugging Face: hard1
hard2: 200 hard-difficulty problems. Hugging Face: hard2
hard3: 400 hard-difficulty problems. Hugging Face: hard3
Participants may also use additional problems from the Equational Theories Project for training.
Stage 1 evaluation set is balanced: 50% TRUE implications and 50% FALSE implications.
After submission deadline, organizer runs offline evaluation.
Offline evaluation is conducted in a no-tools setting: the evaluation pipeline does not provide browser access, web search, or external internet retrieval to the models.
Offline evaluation set is different from the 1669 public selected problems.
We recommend an average cost of no more than USD 0.01 per problem and a solve time of no more than 10 minutes per problem; exceeding time or budget limits may negatively affect final ranking.
Top-performing teams in Stage 1 will advance to Stage 2, with no more than 1,000 teams in total.
Evaluation Models
The current planned Stage 1 evaluation models are:

OpenAI GPT-OSS-120B
Meta Llama-3.3-70B-Instruct
Google Gemma-4-31B-IT
These three models are currently planned to serve as the final Stage 1 evaluation models, with equal weight. The setup may still be adjusted based on community feedback.

The official evaluation setup is published here:

Stage 1 evaluation details: Evaluation Setup
GitHub repository: https://github.com/SAIRcompetition/equational-theories-stage1-judge
The GitHub repository includes the current evaluation configuration, local testing scripts, and reference examples for participants who want to test prompts before submission.

Playground and Recommended Workflow
The Playground and the submission interface both support fully customizable complete prompts.
A complete prompt means the prompt template and cheatsheet text together, as submitted to the model.
Participants may use official or community prompt templates as references, but they are not restricted to a fixed template.
Participants are responsible for correct placeholder usage, including fields such as { equation1 } and { equation2 }, and for ensuring that the output format can be parsed correctly.
We strongly recommend testing your complete prompt in the Playground before formal submission, to make sure it is parsed correctly by the model and behaves as intended.
The Playground is designed to be usable even for participants with no AI development experience.
For professional AI researchers, we recommend setting up your own environment and rigorously testing complete prompts before submission.
Publication Policy After Stage 1
Stage 1 submitted complete prompts may be made public to support community learning and strategy exchange.
This is expected to remain fair because Stage 2 is substantially harder and allows larger cheatsheets, so Stage 1 winners are not guaranteed to transfer directly.
Team Participation and Anti-Cheating Policy
Each individual or organization can participate in only one team.
Teams must register members and sponsors in advance.
If coordinated cheating is detected (including sockpuppet teams), all related teams will be disqualified.
Current Scope
This version of the competition implementation focuses on Stage 1.

Experimental Status
This challenge is currently in an experimental phase.
Rules, scoring details, and evaluation procedures may be adjusted based on implementation experience and community feedback.

Community contributions are welcome.
Join the SAIR Foundation Zulip community for discussion and collaboration:

https://zulip.sair.foundation/







Part 1: Full Raw Dataset and Public Stage 1 Problems
Full Raw Dataset
The full raw implication dataset comes from the Equational Theories Project. It contains 4694 laws, which yields 4694 * (4694 - 1) = 22,028,942 ordered implications.

The full raw implications table can be downloaded from the Equational Theories Project implications page by selecting Download raw implications table:

The full list of all 4694 equations is available here:

https://teorth.github.io/equational_theories/implications/
equations.txt
Selected Problems
Because the full raw dataset is very large, the organizers released several public problem subsets drawn directly from the full raw implication dataset above.

Official public selected subsets for Stage 1:

normal: 1000 normal-difficulty problems, selected programmatically, with 500 ground-truth TRUE labels and 500 ground-truth FALSE labels. Hugging Face: normal
hard1: 69 hard-difficulty problems, co-curated by human mathematicians and AI, with 24 ground-truth TRUE labels and 45 ground-truth FALSE labels. Hugging Face: hard1
hard2: 200 hard-difficulty problems, co-curated by human mathematicians and AI, with 100 ground-truth TRUE labels and 100 ground-truth FALSE labels. Hugging Face: hard2
hard3: 400 hard-difficulty problems, with 195 ground-truth TRUE labels and 205 ground-truth FALSE labels. Hugging Face: hard3
Part 2: Complete Prompt Format and Prompt References
For Stage 1, participants will submit a complete prompt rather than only a cheatsheet. A complete prompt means the full prompt template and cheatsheet text together, as actually provided to the model.

The Playground and the submission interface both support fully customizable complete prompts. Participants may use official or community prompt templates as references, but they are not restricted to a fixed template.

Participants are responsible for correct placeholder usage, including variables such as { equation1 } and { equation2 }, and for ensuring that the final model output can be parsed correctly by the evaluation pipeline.

We strongly recommend testing your complete prompt in the Playground before formal submission, to make sure the prompt is formatted correctly and can be parsed successfully by the model.

Below is an example prompt template for reference. Participants may use it as a starting point when constructing a complete prompt, but Stage 1 is not restricted to a fixed prompt template.

 
You are a mathematician specializing in equational theories of magmas. 
Your task is to determine whether Equation 1 ({{ equation1 }}) implies Equation 2 ({{ equation2 }}) over all magmas.
{% if cheatsheet is defined and cheatsheet %}
{{ cheatsheet }}
{% endif %}
Output format (use exact headers without any additional text or formatting):
VERDICT: must be exactly TRUE or FALSE (in the same line).
REASONING: must be non-empty.
PROOF: required if VERDICT is TRUE, empty otherwise.
COUNTEREXAMPLE: required if VERDICT is FALSE, empty otherwise.
 






Stage 1 Evaluation Setup
This page summarizes the current planned Stage 1 evaluation setup for the Mathematics Distillation Challenge: Equational Theories.

Current Planned Evaluation Models
The current planned Stage 1 evaluation models are:

OpenAI GPT-OSS-120B
Meta Llama-3.3-70B-Instruct
Google Gemma-4-31B-IT
These three models are currently planned to serve as the final Stage 1 evaluation models, with equal weight. The setup may still be adjusted based on community feedback.

The current planned setup in the GitHub repository is:

Alias	OpenRouter model	Pinned provider route	Reasoning	Seed
gpt-oss-120b	openai/gpt-oss-120b	deepinfra/bf16	low	0
llama-3-3-70b-instruct	meta-llama/llama-3.3-70b-instruct	deepinfra/fp8	disabled	0
gemma-4-31b-it	google/gemma-4-31b-it	novita/bf16	disabled	0
Current Evaluation Configuration
The current planned configuration uses:

strict provider pinning, with no fallbacks (allow_fallbacks = false)
temperature 0.0
max output tokens 8192
seeded requests where supported
The offline Stage 1 evaluation is also conducted in a no-tools setting: the evaluation pipeline does not provide browser access, web search, or external internet retrieval to the models.

The final offline evaluation set is private and different from the public selected Stage 1 subsets.

Official Repository
The official GitHub repository for the Stage 1 evaluation setup is:

https://github.com/SAIRcompetition/equational-theories-stage1-judge
This repository includes:

the current planned evaluation models and configuration
the local verdict extractor and prompt renderer
a small local smoke-test workflow
reference examples for prompt testing
For participants who want to test prompts locally before submission, this repository is the reference implementation.

Local Testing
The repository supports local prompt testing before submission. A typical workflow is:

Write a complete prompt.
Test it locally against the public example problems.
Fix formatting failures first.
Then iterate on accuracy.
Submit only after the prompt is stable locally.
The current configuration in the GitHub repository reflects the current planned evaluation setup for Stage 1. If the setup changes, the repository and policy pages will be updated accordingly.
