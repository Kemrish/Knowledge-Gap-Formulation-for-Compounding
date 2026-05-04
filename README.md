# Week 12 — Knowledge Gap Formulation for Compounding

**Author**: Kemeriya
**Program**: 10 Academy AI Forward-Deployed Engineer Track
**Week**: 12 of 12
**Topic spine**: Inference-time mechanics, training/post-training mathematics, evaluation statistics, agent internals, production patterns

---

## What This Week Is

Weeks 0–11 built AI systems. Week 12 audits them. Each day I pair with a colleague, identify one genuine gap in my understanding of the day's topic drawn from my own Week 10/11 artifacts, sharpen it into a research question, research my partner's question, and publish an explainer that closes the gap publicly. Every gap closed must produce a concrete edit to existing portfolio work.

---

## Daily Research Log

| Day | Topic | My Question | Partner | Blog Post | Tweet Thread |
|-----|-------|-------------|---------|-----------|--------------|
| 1 | Inference-time mechanics | [Prefill/decode split for 0.8B ORPO adapter on T4 — does A100 target the right bottleneck?](pair_DAY_1/question.md) | Yosef | [One Forward Pass: What a Qwen2.5-7B Judge Actually Costs at Inference](https://open.substack.com/pub/kemeriyamajor/p/one-forward-pass-what-a-qwen25-7b?r=2xdj7z&utm_campaign=post&utm_medium=web&showWelcomeOnShare=true) | [Thread](pair_DAY_1/thread.md) |
| 2 | TBD | — | — | — | — |
| 3 | TBD | — | — | — | — |
| 4 | TBD | — | — | — | — |
| 5 | TBD | — | — | — | — |

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
├── pair_DAY_2/                      ← (to be added)
├── pair_DAY_3/                      ← (to be added)
├── pair_DAY_4/                      ← (to be added)
├── pair_DAY_5/                      ← (to be added)
├── synthesis.md                     ← (final submission: 10 gaps closed)
├── canonical_list.md                ← (final submission: annotated reading list)
└── portfolio_update.md              ← (final submission: hiring-manager summary)
```

---

## Public Artifacts

### Blog Posts
1. [One Forward Pass: What a Qwen2.5-7B Judge Actually Costs at Inference](https://open.substack.com/pub/kemeriyamajor/p/one-forward-pass-what-a-qwen25-7b?r=2xdj7z&utm_campaign=post&utm_medium=web&showWelcomeOnShare=true) — Day 1, Inference-time mechanics

### Tweet Threads
1. Day 1 — [thread.md](pair_DAY_1/thread.md) *(add URL after posting)*

---

## Portfolio Edits Made (Grounding Commits)

| Day | File Edited | What Changed |
|-----|-------------|--------------|
| 1 | [Week-11/submission_report.md](../Week-11/submission_report.md) | Added prefill/decode diagnosis section. Corrected the A100 hardware upgrade recommendation: the 19.7s latency is 56× the theoretical inference time — the bottleneck is per-call overhead (no batching), not model compute. Batch inference is the correct fix; A100 addresses only the ~350ms inference portion. |

---

## Gaps Closed This Week

| # | I Named | I Researched | Topic | Status |
|---|---------|-------------|-------|--------|
| 1 | ✅ Prefill/decode split for 0.8B adapter on T4 | ✅ 7B judge "one forward pass" cost (Yosef's question) | Inference-time mechanics | Day 1 |
| 2–10 | — | — | TBD | Days 2–5 |

---

## Final Submission Deadline

**Saturday, 21:00 UTC** — GitHub repo final state + all public artifact URLs.
