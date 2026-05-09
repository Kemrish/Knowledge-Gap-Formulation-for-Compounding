# Week 12 — Knowledge Gap Formulation for Compounding

## What This Week Is

Weeks 0–11 built AI systems. Week 12 audits them. Each day I pair with a colleague, identify one genuine gap in my understanding of the day's topic drawn from my own Week 10/11 artifacts, sharpen it into a research question, research my partner's question, and publish an explainer that closes the gap publicly. Every gap closed must produce a concrete edit to existing portfolio work.

---

## Daily Research Log

| Day | Topic | My Question | Partner | Blog Post | Tweet Thread |
|-----|-------|-------------|---------|-----------|--------------|
| 1 | Inference-time mechanics | [Prefill/decode split for 0.8B ORPO adapter on T4 — does A100 target the right bottleneck?](pair_DAY_1/question.md) | Yosef | [One Forward Pass: What a Qwen2.5-7B Judge Actually Costs at Inference](https://open.substack.com/pub/kemeriyamajor/p/one-forward-pass-what-a-qwen25-7b?r=2xdj7z&utm_campaign=post&utm_medium=web&showWelcomeOnShare=true) | [Thread](pair_DAY_1/thread.md) |
| 2 | Agent and tool-use internals | [JSON-prompting vs tool_use at token level — did my reply classifier's schema prime dual-control stalling?](pair_DAY_2/question.md) | Tsegay Assefa | [tool_use Is Not Logit Masking — And That Changes How You Build Safe Agent Loops](https://open.substack.com/pub/kemeriyamajor/p/tool_use-is-not-logit-masking-and?r=2xdj7z&utm_campaign=post&utm_medium=web&showWelcomeOnShare=true) | [Thread](https://www.linkedin.com/feed/update/urn:li:share:7458827952596811776/) |
| 3 | Training and post-training mechanics | [ORPO per-token log-prob averaging — does TRL's length normalization explain why signal_grounding improved +11.8 pts but dual_control regressed −4.5 pts at the same β?](pair_DAY_3/question.md) | Mikias Dagem | [When Your Eval Loss Lies: Variant-Level Data Leakage in Augmented SFT Datasets](https://open.substack.com/pub/kemeriyamajor/p/when-your-eval-loss-lies-variant?r=2xdj7z&utm_campaign=post&utm_medium=web&showWelcomeOnShare=true) | [Thread](https://www.linkedin.com/feed/update/urn:li:share:7458129929784836097/) |
| 4 | Evaluation and statistics | [Binary benchmark power analysis — MDE for 216 tasks, v0.2 sample size targets, and correcting p=0.0 bootstrap reporting](pair_DAY_4/question.md) | Beamlak | [p = 0.71 Doesn't Mean No Improvement — It Means You Can't See One Yet](https://open.substack.com/pub/kemeriyamajor/p/p-071-doesnt-mean-no-improvement?r=2xdj7z&utm_campaign=post&utm_medium=web&showWelcomeOnShare=true) | [Thread](https://www.linkedin.com/feed/update/urn:li:share:7458824634835210240/) |

---

## Repository Structure

```
Week-12/
├── README.md                        ← this file
├── pair_DAY_1/                      ← Day 1 deliverables (Inference-time mechanics)
│   ├── question.md                  ← my sharpened question + artifact pointer
│   ├── morning_call_summary.md      ← how both questions were sharpened
│   ├── explainer.md                 ← blog post I wrote for Yosef's question
│   ├── thread.md                    ← tweet thread (published)
│   ├── evening_call_summary.md      ← feedback exchanged + what was revised
│   ├── signoff.md                   ← gap closure judgment (Closed)
│   ├── grounding_commit.md          ← edit made to Week-11/submission_report.md
│   ├── sources.md                   ← canonical papers + tool used
│   └── sources/
│       └── flops_calculator.py      ← runnable prefill/decode cost calculator
├── pair_DAY_2/                      ← Day 2 deliverables (Agent and tool-use internals)
├── pair_DAY_3/                      ← Day 3 deliverables (Training and post-training mechanics)
├── pair_DAY_4/                      ← Day 4 deliverables (Evaluation and statistics)
├── synthesis.md                     ← final submission: 8 gaps closed
├── canonical_list.md                ← final submission: 10 annotated sources
└── portfolio_update.md              ← final submission: hiring-manager summary
```

---

## Public Artifacts

### Blog Posts
1. [One Forward Pass: What a Qwen2.5-7B Judge Actually Costs at Inference](https://open.substack.com/pub/kemeriyamajor/p/one-forward-pass-what-a-qwen25-7b?r=2xdj7z&utm_campaign=post&utm_medium=web&showWelcomeOnShare=true) — Day 1, Inference-time mechanics
2. [tool_use Is Not Logit Masking — And That Changes How You Build Safe Agent Loops](https://open.substack.com/pub/kemeriyamajor/p/tool_use-is-not-logit-masking-and?r=2xdj7z&utm_campaign=post&utm_medium=web&showWelcomeOnShare=true) — Day 2, Agent and tool-use internals
3. [When Your Eval Loss Lies: Variant-Level Data Leakage in Augmented SFT Datasets](https://open.substack.com/pub/kemeriyamajor/p/when-your-eval-loss-lies-variant?r=2xdj7z&utm_campaign=post&utm_medium=web&showWelcomeOnShare=true) — Day 3, Training and post-training mechanics
4. [p = 0.71 Doesn't Mean No Improvement — It Means You Can't See One Yet](https://open.substack.com/pub/kemeriyamajor/p/p-071-doesnt-mean-no-improvement?r=2xdj7z&utm_campaign=post&utm_medium=web&showWelcomeOnShare=true) — Day 4, Evaluation and statistics

### Tweet Threads
1. Day 1 — https://www.linkedin.com/feed/update/urn:li:ugcPost:7457311830399602689/
2. Day 2 — https://www.linkedin.com/feed/update/urn:li:share:7458827952596811776/
3. Day 3 — https://www.linkedin.com/feed/update/urn:li:share:7458129929784836097/
4. Day 4 — https://www.linkedin.com/feed/update/urn:li:share:7458824634835210240/
---

## Portfolio Edits Made (Grounding Commits)

| Day | File Edited | What Changed |
|-----|-------------|--------------|
| 1 | [Week-11/submission_report.md](../Week-11/submission_report.md) | Added prefill/decode diagnosis section. Corrected the A100 hardware upgrade recommendation: the 19.7s latency is 56× the theoretical inference time — the bottleneck is per-call overhead (no batching), not model compute. Batch inference is the correct fix; A100 addresses only the ~350ms inference portion. |
| 2 | [Week-10/agent/email/reply_handler.py](../Week-10/The%20Conversion%20Engine/agent/email/reply_handler.py) | Removed `suggested_next_action` from `SYSTEM_PROMPT_QUALIFIER`. The field was generated by the model and silently discarded by `policy.py`. Asking the model to suggest an action made it a policy engine, priming conservative `route_to_human` outputs. Added explicit instruction: "Your job is classification only." |
| 3 | [Week-11/synthesis_memos/memo_07_orpo.md](../Week-11/synthesis_memos/memo_07_orpo.md) + [Week-11/submission_report.md](../Week-11/submission_report.md) | Added per-token averaging caveat to β=0.2 reasoning in memo: raising λ scales a diluted signal on dual-control pairs, not a strong one. Added dilution as third hypothesis in Section 7 with a three-way diagnostic (per-dimension loss logging) to distinguish dilution, data sparsity, and early-stop in the 750-step follow-up run. |
| 4 | [Week-11/submission_report.md](../Week-11/submission_report.md) | Three additions: (1) MDE ≈ 12 pp power analysis note in Section 1 — p = 0.71 cannot distinguish no effect from below-threshold effect. (2) Corrected p = 0.0 → p < 0.0005 in Section 2 (finite bootstrap bound 1/(B+1)). (3) Added 1,100–1,500 task minimum as a design constraint for v0.2 in Section 5. |

---

## Gaps Closed This Week

| # | I Named | I Researched | Topic | Status |
|---|---------|-------------|-------|--------|
| 1 | ✅ Prefill/decode split for 0.8B adapter on T4 | ✅ 7B judge "one forward pass" cost (Yosef's question) | Inference-time mechanics | Day 1 |
| 2 | ✅ JSON-prompting vs tool_use schema design caused dual-control stalling | ✅ tool_use token-level mechanism (Tsegay's question) | Agent and tool-use internals | Day 2 | 
| 3 | ✅ ORPO per-token log-prob averaging — TRL length normalization as cause of dual-control gradient dilution | ✅ Variant-level data leakage in augmented SFT datasets (Mikias's question) | Training and post-training mechanics | Day 3 |
| 4 | ✅ 216-task benchmark underpowered — MDE ~12 pts, need ~1,100+ tasks for 5-pt sensitivity | ✅ Bootstrap p-value bounds + two-proportion power analysis (Beamlak's question) | Evaluation and statistics | Day 4 |

