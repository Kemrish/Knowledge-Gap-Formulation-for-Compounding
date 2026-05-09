# Week 12 Synthesis — 8 Gaps Closed

**Author**: Kemeriya  
**Date**: 2026-05-09  
**Programme**: 10 Academy AI FDE — Week 12

---

## Overview

Over four days of paired research, I identified and closed 8 genuine gaps in my understanding of the AI systems I built in Weeks 10 and 11. Each gap was anchored in a specific artifact from prior work, sharpened with a partner, researched and written up as a public explainer, and closed with a concrete edit to the original portfolio artifact. This document summarises each gap, what closed it, and what changed.

---

## Gap 1 — Inference Bottleneck Misdiagnosis (I Named)

**Topic**: Inference-time mechanics  
**Artifact**: `Week-11/submission_report.md` — Section 3 latency analysis  
**Gap**: I recommended an A100 upgrade to address the 19.7s inference latency on Tenacious-Bench evaluation. I did not know whether the bottleneck was model compute or execution overhead.

**What closed it**: Applying the roofline model to the 0.8B adapter. Prefill (1,024 tokens): 1.64 TFLOPs → ~84ms on T4. Decode (~50 tokens): ~265ms. Theoretical total: ~350ms. The actual 19.7s is 56× the theoretical ceiling — the bottleneck is per-call overhead from sequential task execution with no batching, not model compute. An A100 would reduce the ~350ms inference portion; it leaves the ~19,350ms overhead untouched.

**What changed**: `submission_report.md` — added prefill/decode diagnosis section, corrected A100 recommendation, named batch inference as the correct fix.

---

## Gap 2 — 7B Judge Inference Cost (I Researched for Yosef)

**Topic**: Inference-time mechanics  
**Artifact**: Yosef's Qwen2.5-7B judge — claim of "near-zero marginal cost, one forward pass"  
**Gap**: Yosef claimed his 7B judge had near-zero marginal inference cost. The claim needed a mechanism-level check.

**What closed it**: For Qwen2.5-7B in BF16: prefill (1,024 tokens) = 2 × 7.62B × 1,024 ≈ 15.6 TFLOPs; decode (2 output tokens) = 30.5 GFLOPs. Prefill is 89% of wall time on every tested hardware tier. The "one forward pass" framing is correct in token count but misleading in cost — the prefill dominates, and 1,024 input tokens at 7B scale is not cheap.

**What changed**: Published explainer — [One Forward Pass: What a Qwen2.5-7B Judge Actually Costs at Inference](https://open.substack.com/pub/kemeriyamajor/p/one-forward-pass-what-a-qwen25-7b).

---

## Gap 3 — Schema Design Caused Dual-Control Stalling (I Named)

**Topic**: Agent and tool-use internals  
**Artifact**: `Week-10/The Conversion Engine/agent/email/reply_handler.py`  
**Gap**: The reply classifier stalled on dual-control decisions 40% of the time in τ²-Bench. I attributed this to using JSON prompting instead of the tool_use API and could not explain the mechanism.

**What closed it**: The `suggested_next_action` field in `SYSTEM_PROMPT_QUALIFIER` made the model a policy engine. A well-calibrated model defaults to `route_to_human` because it is always safe — that is rational behaviour, not a bug. The field generated tokens that `policy.py` immediately discarded, and those tokens were priming conservative intent classifications upstream. tool_use vs JSON-prompting was not the issue; schema design was.

**What changed**: `reply_handler.py` — removed `suggested_next_action` from the JSON schema, added explicit instruction "Your job is classification only."

---

## Gap 4 — tool_use API Token-Level Mechanism (I Researched for Tsegay)

**Topic**: Agent and tool-use internals  
**Artifact**: Tsegay's orchestrator — repeated tool calls after 3–4 turns  
**Gap**: Tsegay's agent re-called tools it had already used, as if it had forgotten the results.

**What closed it**: tool_use is trained behaviour + XML format injection, not logit masking. The model reads the full messages array fresh each turn — it has no internal state. Missing `tool_result` blocks means the model literally cannot see its own previous outputs. Tsegay's scaffolding was appending `tool_use` blocks but not the corresponding `tool_result` blocks, so the model saw its own calls but never saw the answers.

**What changed**: Published explainer covering the Anthropic messages format for multi-turn tool use and the required `tool_use` → `tool_result` pairing.

---

## Gap 5 — ORPO Per-Token Gradient Dilution Explains Dual-Control Regression (I Named)

**Topic**: Training and post-training mechanics  
**Artifact**: `Week-11/synthesis_memos/memo_07_orpo.md` + `Week-11/submission_report.md` Section 7  
**Gap**: Signal grounding improved +11.8 pts post-training; dual control regressed −4.5 pts. I attributed this to β=0.2 overshoot or data sparsity (33 pairs). I did not know what β actually controls at the gradient level in TRL's implementation.

**What closed it**: TRL's `ORPOTrainer` computes the odds ratio using per-token averaged log probabilities: `log_p = (1/T) × Σ log p(tᵢ)`. Signal-grounding pairs have forbidden phrases distributed across many tokens — the gradient averages strong signal throughout. Dual-control pairs have identical reasoning traces; only the final routing token differs — the gradient from that one token is divided by the full sequence length (~100×). The +11.8 / −4.5 split is explained by this dilution, not by β or data volume.

**What changed**: `memo_07_orpo.md` — added per-token averaging caveat to β=0.2 reasoning. `submission_report.md` Section 7 — added dilution as third hypothesis with three-way diagnostic (per-dimension loss logging to distinguish dilution, sparsity, and early-stop in the 750-step run).

---

## Gap 6 — Variant-Level Data Leakage in Augmented SFT (I Researched for Mikias)

**Topic**: Training and post-training mechanics  
**Artifact**: Mikias's `training/train.py` — `load_best_model_at_end=True` on a variant-level eval split  
**Gap**: Mikias reported eval loss of 0.0213 at checkpoint-441 and published it to HuggingFace as the best checkpoint.

**What closed it**: Variant-level splitting (random shuffle over all examples) puts 8 variants of each probe in training and 2 in eval. The model memorizes each probe's underlying facts from 8 training variants, then sees the same probe in new phrasing at eval — near-zero loss is probe recall, not generalization. `load_best_model_at_end=True` selected the deepest memorizer, not the best-generalizing checkpoint. Fix: probe-level split (all variants of a probe stay on one side) and `metric_for_best_model='eval_rubric_score'` using a probe-disjoint held-out set.

**What changed**: Published explainer — [When Your Eval Loss Lies: Variant-Level Data Leakage in Augmented SFT Datasets](https://open.substack.com/pub/kemeriyamajor/p/when-your-eval-loss-lies-variant).

---

## Gap 7 — 216-Task Benchmark Underpowered (I Named)

**Topic**: Evaluation and statistics  
**Artifact**: `Week-11/submission_report.md` — Delta A reporting  
**Gap**: I reported Delta A = −2.34 pts (p = 0.71) as "not significant" without checking whether 216 tasks was enough to detect the improvements I care about. I also reported p = 0.0 for Delta B, which is mathematically impossible with finite bootstrap samples.

**What closed it**: MDE for 216 binary tasks at 74.6% baseline = (1.96 + 0.842) × √(2 × 0.734 × 0.266 / 216) ≈ **12 percentage points**. The observed −2.34 point Delta A is 20% of the MDE. p = 0.71 cannot distinguish "no improvement" from "real improvement below detection threshold." For 5-point sensitivity, v0.2 needs ~1,100 tasks. For p = 0.0 with B = 2,000: correct statement is p < 1/(B+1) = p < 0.0005.

**What changed**: `submission_report.md` — three additions: MDE + power analysis note in Section 1, p < 0.0005 correction in Section 2, 1,100–1,500 task design constraint in Section 5.

---

## Gap 8 — Bootstrap P-Value Bounds and Two-Proportion Power Analysis (I Researched for Beamlak)

**Topic**: Evaluation and statistics  
**Artifact**: Beamlak's research question, anchored in `submission_report.md`  
**Gap**: Beamlak asked for the MDE formula applied to the 216-task benchmark, sample size targets for v0.2, and the correct finite-bootstrap p-value statement — the same gap from the other direction.

**What closed it**: Worked through the full derivation: SE(Delta) = √(p₁(1−p₁)/n + p₂(1−p₂)/n) ≈ 0.0425, CI half-width = 1.96 × 0.0425 ≈ 8.3 pp (matching the reported CI). Sample size targets: +3 pts → ~3,100 tasks, +5 pts → ~1,100, +8 pts → ~410. The bootstrap lower bound: p_min = 1/(B+1) per Efron & Hastie.

**What changed**: Published explainer (pending). Reinforced the three `submission_report.md` edits made in Gap 7.

---

## Cross-Cutting Patterns

Three patterns appeared across all four topic areas:

**1. Correct mechanism, wrong target**: Both the A100 recommendation (Gap 1) and the β=0.2 reasoning (Gap 5) had correct intuitions applied to the wrong bottleneck. Knowing the mechanism would have redirected both decisions before the cost was paid.

**2. Schema encodes assumptions**: The `suggested_next_action` field (Gap 3) and the variant-level eval split (Gap 6) both encoded an assumption about what the model should do — one asked it to be a policy engine, the other treated paraphrase recall as generalization. In both cases the model did exactly what the schema asked; the schema was wrong.

**3. Non-significant ≠ no effect**: p = 0.71 (Gap 7) and the variant-level eval loss (Gap 6) were both interpreted as "nothing to see here" when the correct reading was "the measurement instrument is too coarse." Resolution problems look like null results.
