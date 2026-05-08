# Day 4 Question — Kemeriya

## Topic: Evaluation and Statistics

---

## Final Sharpened Question

In `Week-11/submission_report.md`, I reported:

```
Delta A = −2.34 pts   95% CI [−11.09, +6.20]   p = 0.71   Not significant
Delta B = +22.18 pts  95% CI [+14.43, +29.82]   p = 0.0    Significant
```

Both results were computed using 2,000 bootstrap samples over **216 binary pass/fail tasks**.

I interpreted p = 0.71 as "the trained adapter does not clearly surpass the baseline." I never asked whether the benchmark was large enough to detect the improvement I actually care about. The CI width for Delta A is **17.29 percentage points** — that is a very wide uncertainty band for a benchmark that took a week to build.

**My gap**: With 216 binary tasks, what is the minimum detectable effect (MDE) at 80% power for a two-proportion comparison — and if the true adapter improvement after the full 750-step run is somewhere between +3 and +8 percentage points (a plausible real-world gain), how many tasks does Tenacious-Bench v0.2 need to have an 80% chance of detecting it?

The secondary issue: the report states "p = 0.0 across 2,000 bootstrap samples." With a finite number of bootstrap replicates, p = 0.0 is technically impossible — the true lower bound on a bootstrap p-value with B replicates is 1/(B+1). I reported an impossible p-value and do not know what the correct way to state it is.

---

## Connection to Existing Artifact

**Primary artifact**: `Week-11/submission_report.md`
- Line 11: CI [−11.09, +6.20] — 17.29-point span reported without noting whether 216 tasks can distinguish "no effect" from "small positive effect"
- Line 19: p = 0.71 — interpreted as absence of effect; may be absence of power
- Line 32: p = 0.0 — mathematically impossible with finite bootstrap samples; should be p < 1/2001

**Secondary artifact**: `Week-11/submission_report.md` Section 5 (Tenacious-Bench v0.2 coverage gaps)
- Section 5 names four qualitative coverage gaps but gives no sample size target for v0.2
- A power analysis would give a concrete minimum number of tasks v0.2 must contain to make Delta A a meaningful signal

The gap: I computed bootstrap CIs and p-values correctly but never checked whether the benchmark had enough tasks to detect the effect size I care about. p = 0.71 may mean "no improvement" or it may mean "we cannot tell." Those require completely different responses.

---

## Why This Is Generalizable

Anyone building a benchmark or running an A/B test on a model faces this: you get a non-significant result and don't know whether to interpret it as evidence of no effect or as evidence that your sample was too small. Power analysis before collecting data is standard in clinical trials and psychology; it is rarely done in NLP benchmark design. The calculation for a binary pass/fail benchmark is straightforward but most FDEs never run it.

---

## What a Satisfying Answer Looks Like

A 600–900 word explainer that:
1. States the MDE formula for a two-proportion test and computes it for 216 tasks at the Tenacious-Bench baseline rate (~74%)
2. Tells me whether p = 0.71 is more consistent with "no effect" or "underpowered benchmark"
3. Calculates how many tasks v0.2 needs to detect a +3 pt, +5 pt, and +8 pt improvement at 80% power
4. Corrects the p = 0.0 reporting: what to write instead with 2,000 bootstrap samples
