# Portfolio Update — Week 12

**Author**: Kemeriya  
**Date**: 2026-05-09  
**For**: Hiring managers reviewing the 10 Academy AI FDE portfolio

---

## What Week 12 Demonstrates

Week 12 was not a build week. It was an audit week: I went back through every AI system built in Weeks 10–11 and closed the gaps I couldn't explain at the time. Each gap had to be anchored in a specific artifact, sharpened into a researchable question with a peer, answered with a published explainer, and closed with a concrete edit to the original work.

The result is four AI systems (inference pipeline, agent email classifier, ORPO-trained judge adapter, B2B benchmark) that now have correct documented reasoning where the original had gaps or errors.

---

## What Was Corrected in the Portfolio

### Week 11 — Submission Report (`submission_report.md`)

Five separate corrections made across the week:

| Section | Original | Corrected |
|---|---|---|
| Section 1 — Latency | Recommended A100 upgrade to fix 19.7s inference | Identified bottleneck as per-call overhead (56× theoretical); correct fix is batch inference |
| Section 1 — Delta A | p = 0.71 interpreted as "no improvement" | Added MDE ≈ 12 pp — p = 0.71 cannot distinguish no effect from below-threshold effect |
| Section 2 — Delta B | p = 0.0 (mathematically impossible) | Corrected to p < 0.0005 (finite bootstrap bound 1/(B+1) with B=2,000) |
| Section 5 — v0.2 design | Four qualitative coverage gaps, no sample size target | Added ~1,100–1,500 task minimum for 5-point statistical sensitivity |
| Section 7 — Dual-control regression | Two hypotheses: early-stop, data sparsity | Added third hypothesis: per-token gradient dilution; three-way diagnostic for the 750-step run |

### Week 11 — ORPO Memo (`synthesis_memos/memo_07_orpo.md`)

The β=0.2 justification said "categorical pairs need more preference pressure." Corrected to note that TRL's per-token averaging means raising β scales a diluted gradient on dual-control pairs — not a strong one. The verification plan updated to include per-dimension loss logging that distinguishes the three regression hypotheses.

### Week 10 — Reply Handler (`agent/email/reply_handler.py`)

Removed `suggested_next_action` from the JSON schema. The field made the model a policy engine; `policy.py` was already the policy engine and silently discarded the field. Removing it eliminates role confusion and reduces output tokens by 5–8 per call.

---

## Public Artifacts Produced

| Day | Topic | Blog Post | Thread |
|---|---|---|---|
| 1 | Inference-time mechanics | [One Forward Pass: What a Qwen2.5-7B Judge Actually Costs at Inference](https://open.substack.com/pub/kemeriyamajor/p/one-forward-pass-what-a-qwen25-7b) | [LinkedIn](https://www.linkedin.com/feed/update/urn:li:ugcPost:7457311830399602689/) |
| 2 | Agent and tool-use internals | [tool_use Is Not Logit Masking — And That Changes How You Build Safe Agent Loops](https://open.substack.com/pub/kemeriyamajor/p/tool_use-is-not-logit-masking-and?r=2xdj7z&utm_campaign=post&utm_medium=web&showWelcomeOnShare=true) | [LinkedIn](https://www.linkedin.com/feed/update/urn:li:share:7458827952596811776/) |
| 3 | Training and post-training mechanics | [When Your Eval Loss Lies: Variant-Level Data Leakage in Augmented SFT Datasets](https://open.substack.com/pub/kemeriyamajor/p/when-your-eval-loss-lies-variant) | [LinkedIn](https://www.linkedin.com/feed/update/urn:li:share:7458129929784836097/) |
| 4 | Evaluation and statistics | [p = 0.71 Doesn't Mean No Improvement — It Means You Can't See One Yet](https://open.substack.com/pub/kemeriyamajor/p/p-071-doesnt-mean-no-improvement?r=2xdj7z&utm_campaign=post&utm_medium=web&showWelcomeOnShare=true) | [LinkedIn](https://www.linkedin.com/feed/update/urn:li:share:7458824634835210240/) |

Each post was written to answer a peer's question, not Kemeriya's own — a deliberate constraint that forces the explainer to start from first principles rather than from personal context.

---

## Skills Demonstrated

**Inference cost analysis**: Applied the roofline model to a 0.8B transformer on T4 hardware. Derived prefill vs decode wall-time bounds from parameter counts. Identified per-call overhead as the dominant latency source. This is the skill needed to diagnose and fix inference pipelines before reaching for hardware upgrades.

**Training mechanics**: Traced ORPO's gradient computation through TRL's `ORPOTrainer` implementation. Identified how per-token log-probability averaging creates systematically different gradient magnitudes for different types of preference pairs. This is the skill needed to debug training runs where per-dimension results split in unexpected ways.

**ML data engineering**: Identified variant-level data leakage in an augmented SFT dataset and its effect on checkpoint selection. Specified the probe-level split and `metric_for_best_model` fix. This is a common production pitfall for anyone fine-tuning on augmented data.

**Benchmark statistics**: Applied two-proportion power analysis to a binary pass/fail benchmark. Computed MDE for existing sample size and required sample size for target effect sizes. Corrected a finite-bootstrap p-value reporting error. This is the skill needed to interpret evaluation results and design benchmarks that can detect the effects you actually care about.

**Peer research and technical writing**: Researched and wrote four public explainers answering peers' questions on topics I had to learn from scratch (7B judge inference cost, multi-turn tool-use state, variant-level leakage, bootstrap bounds). Each explainer is 600–900 words, grounded in canonical sources, and includes a runnable code demonstration.

---

## What the Portfolio Shows End-to-End

A candidate who:
- Builds a B2B sales agent (Week 10), benchmarks it (Week 11), and then audits every design decision that turned out to be wrong (Week 12)
- Knows when an inference latency problem is a batching problem, not a hardware problem
- Can read a training loss curve and connect per-dimension regression to a specific implementation detail in the loss function
- Understands the difference between a non-significant result and an underpowered measurement instrument
- Publishes technical explainers for peers, not just internal documentation

The Week 12 portfolio edits are not cleanup. They are the evidence that the learning happened.
