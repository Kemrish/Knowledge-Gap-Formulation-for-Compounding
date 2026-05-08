# p = 0.71 Doesn't Mean No Improvement — It Means You Can't See One Yet

**By Kemeriya — Day 4 Explainer, answering Beamlak's question**

---

Tenacious-Bench v0.1 has 216 binary pass/fail tasks. The adapter scored 72.25%; the baseline scored 74.59%. The difference is −2.34 points. p = 0.71. The report says "not significant."

That interpretation is incomplete. p = 0.71 does not mean there is no improvement. It means the benchmark is too small to see one — unless the improvement is very large. Here is the exact threshold, the correct sample size for v0.2, and what to write instead of "p = 0.0."

---

## What the Minimum Detectable Effect Actually Is

For two independent proportions compared at significance α = 0.05 (two-sided) with 80% power, the minimum detectable effect is:

```
MDE = (z₀.₀₂₅ + z₀.₂₀) × √(2 × p̄ × (1−p̄) / n)
    = (1.96 + 0.842) × √(2 × 0.7342 × 0.2658 / 216)
    = 2.802 × √(0.001805)
    = 2.802 × 0.0425
    ≈ 11.9 percentage points
```

Where p̄ = (0.7459 + 0.7225) / 2 = 0.7342 is the pooled baseline rate and n = 216.

**The MDE for Tenacious-Bench v0.1 is approximately 12 percentage points.**

This means the benchmark has 80% power to detect an improvement only if the true improvement is 12 points or larger. The observed Delta A of −2.34 points is one-fifth of the MDE. The benchmark is structurally unable to distinguish that signal from noise — not because there is no signal, but because 216 tasks are not enough to see it.

p = 0.71 says: "given 216 tasks, a −2.34 point observed difference is exactly what you would expect from random variation even if the true effect is zero." It does not say the true effect is zero. The adapter could be genuinely +5 points better at full convergence, and a 216-task benchmark would still return p ≈ 0.71 roughly half the time.

---

## What the CI Is Actually Telling You

The 95% CI for Delta A is [−11.09, +6.20] — a 17.3-point span. This is not a formatting artifact. It is the direct consequence of 216 binary tasks:

```
SE(Delta) = √(p₁(1−p₁)/n + p₂(1−p₂)/n)
          = √(0.7225×0.2775/216 + 0.7459×0.2541/216)
          = √(0.000927 + 0.000877)
          ≈ 0.0425

95% CI half-width = 1.96 × 0.0425 ≈ 8.3 pp
```

A 17-point-wide CI means you cannot distinguish "the adapter is 6 points better" from "the adapter is 11 points worse." Both are inside the interval. This is not a statistical curiosity — it is a measurement instrument with insufficient resolution for the effect sizes you care about.

---

## How Many Tasks v0.2 Needs

The sample size formula for detecting a δ-point improvement at 80% power (α = 0.05, two-sided):

```
n = (z₀.₀₂₅ + z₀.₂₀)² × [p₁(1−p₁) + p₂(1−p₂)] / δ²
  = 7.85 × [p₁(1−p₁) + p₂(1−p₂)] / δ²
```

Using p₁ = 0.7459 (baseline) and p₂ = p₁ + δ (expected adapter score):

| Target improvement (δ) | p₂ | n required |
|---|---|---|
| +3 points | 0.7759 | ~3,100 tasks |
| +5 points | 0.7959 | ~1,100 tasks |
| +8 points | 0.8259 | ~410 tasks |

The +5 point target is probably the most realistic for a full 750-step run that resolves the dual-control regression. **Tenacious-Bench v0.2 needs approximately 1,100 tasks** to have an 80% chance of detecting a 5-point improvement. The current 216 tasks would need to detect an 8-point improvement just to have 80% power — and even then only barely.

A practical v0.2 target: 1,200–1,500 tasks across six dimensions (200–250 per dimension), which keeps per-dimension power reasonable while making the overall Delta A a meaningful signal.

---

## The p = 0.0 Problem

The report states "p = 0.0 across 2,000 bootstrap samples." This is technically wrong.

A bootstrap p-value is computed by counting how many of B replicates exceed the observed test statistic. If 0 of 2,000 replicates exceed it:

```
p̂ = 0 / 2000 = 0.0
```

But with a finite number of replicates, p = 0.0 is impossible — it would require infinite bootstrap samples to rule out any non-zero probability. The correct lower bound on a bootstrap p-value is:

```
p_min = 1 / (B + 1) = 1 / 2001 ≈ 0.0005
```

The correct statement is: **"p < 0.0005 (0 of 2,000 bootstrap replicates exceeded the observed delta)"** — or equivalently, "p ≤ 1/(B+1) = 0.0005."

This is not pedantic. Reporting p = 0.0 in a paper or benchmark card implies exact zero probability, which misleads readers into thinking the result is more certain than the bootstrap resolution permits.

For Delta B this does not change the interpretation — the result is still highly significant — but the reporting should be corrected in any public-facing version of the report.

---

## What to Change in the Report

**In Section 1 (Delta A)**: Add one sentence after the CI paragraph: "The 17-point CI width reflects the benchmark's resolution limit: at 216 binary tasks and an 80% power threshold, the minimum detectable effect is ~12 percentage points. p = 0.71 is consistent with both 'no improvement' and 'real improvement below the detection threshold.'"

**In Section 2 (Delta B)**: Replace "p = 0.0 across 2,000 bootstrap samples" with "p < 0.0005 (0 of 2,000 bootstrap replicates exceeded the observed delta)."

**In Section 5 (v0.2 design)**: Add a sample size target: "To detect a 5-point improvement at 80% power, v0.2 requires approximately 1,100 tasks — roughly 5× the v0.1 task count."

---

*This explainer uses the standard two-proportion z-test power formula. Sources: Cohen (1988) Statistical Power Analysis for the Behavioral Sciences; Efron & Hastie (2016) on bootstrap p-value bounds; HuggingFace `evaluate` library documentation on bootstrap confidence intervals.*
