# Grounding Commit — Day 4

**Asker**: Kemeriya
**Artifact edited**: `Week-11/submission_report.md` — three sections

---

## Edit 1 — Section 1 (Delta A power analysis note)

Added one paragraph after the CI interpretation paragraph. The original text said "the true effect is statistically indistinguishable from zero" and stopped there. The revised text adds the MDE calculation explicitly: at 216 binary tasks and 74.6% baseline rate, MDE ≈ 12 percentage points. The observed −2.34 point Delta A is 20% of the MDE. The paragraph makes explicit that p = 0.71 is consistent with both "no improvement" and "real improvement below the detection threshold" — and that these two interpretations require different responses.

**Why**: The original framing implied the absence of a clear gain means the training approach is wrong. It does not. At v0.1 scale, the benchmark cannot resolve effects smaller than 12 points. The full 750-step run may return p = 0.2 or p = 0.3 and that would still be consistent with a real 5-point gain. Leaving the original framing uncorrected would lead to premature abandonment of the training approach.

---

## Edit 2 — Section 2 (Delta B p-value correction)

Changed `p = 0.0` → `p < 0.0005` in the Delta B table and explanatory text. Added the derivation: with B = 2,000 bootstrap replicates and 0 exceeding the observed delta, the finite-bootstrap lower bound is 1/(B+1) = 1/2001 ≈ 0.0005.

**Why**: p = 0.0 is mathematically impossible with finite bootstrap samples. Reporting it implies certainty the bootstrap resolution does not support. The correct statement is p < 0.0005, which is still unambiguously significant but accurately represents what the bootstrap can and cannot say.

---

## Edit 3 — Section 5 (v0.2 task count design constraint)

Added a fifth gap — "Design constraint: minimum task count for statistical sensitivity" — after the four qualitative gaps. States the required sample sizes: ~1,100 tasks to detect a 5-point improvement at 80% power, with a recommended v0.2 target of 1,200–1,500 tasks across six dimensions (200–250 per dimension). Includes the sample size formula for reproducibility.

**Why**: Section 5 named four coverage gaps but gave no quantitative minimum for v0.2. Without a sample size target, v0.2 could be designed with 400 tasks (only detects 8+ point effects) and reproduce the same underpowering problem. The power analysis makes the task count a first-class design constraint, not an afterthought.
