# Asker Sign-Off — Day 4

**Asker**: Kemeriya
**Question**: With 216 binary pass/fail tasks, what is the minimum detectable effect at 80% power — and does p = 0.71 mean no improvement or underpowered benchmark?

**Gap closure judgment**: [x] Closed

---

## What Closed It

Beamlak's explainer resolved both parts of the question. The MDE calculation (≈12 percentage points for 216 tasks at 74.6% baseline) showed that the −2.34 point Delta A sits at 20% of the detection threshold — the benchmark literally cannot see an effect that small as statistically significant regardless of what the true effect is. p = 0.71 is not evidence of no improvement; it is a measurement resolution failure.

The sample size table (+3 pts → ~3,100 tasks, +5 pts → ~1,100 tasks) gave the concrete v0.2 design target I had been missing. Section 5 of submission_report.md listed four qualitative coverage gaps but no quantitative minimum — the power analysis fills that slot.

The p = 0.0 correction (→ p < 0.0005) is a small but important fix. With 2,000 bootstrap samples the lower bound is 1/2001. Reporting p = 0.0 is technically wrong and implies certainty the bootstrap resolution does not support.

**Concrete edits made**: Three additions to `Week-11/submission_report.md` — power analysis note + MDE in Section 1, p-value correction in Section 2, and task-count design constraint in Section 5.
