# LinkedIn Thread — Day 4

https://www.linkedin.com/feed/update/urn:li:share:7458824634835210240/

*Topic: p = 0.71 doesn't mean no improvement — it means your benchmark is too small to see one*

---

**Post 1**

Your model evaluation returned p = 0.71. You conclude: no improvement.

Wrong conclusion. You may have a real improvement that your benchmark is too small to detect. Here's the calculation that tells the difference. 🧵

---

**Post 2**

With 216 binary pass/fail tasks and a ~75% baseline pass rate, the minimum detectable effect at 80% power is:

MDE = (1.96 + 0.842) × √(2 × 0.734 × 0.266 / 216) ≈ **12 percentage points**

Any true improvement smaller than 12 points has less than 80% chance of showing up as significant. p = 0.71 on a −2.34 point delta is exactly what you'd expect — even if the model is genuinely 5 points better.

---

**Post 3**

This matters for how you respond to the result.

"No improvement" → rethink the training approach.
"Below detection threshold" → run more training steps, then test again on a larger benchmark.

These are completely different decisions. p = 0.71 alone cannot tell you which one is right.

---

**Post 4**

How many tasks does your v0.2 benchmark need?

| Target improvement | Tasks required (80% power) |
|---|---|
| +3 percentage points | ~3,100 |
| +5 percentage points | ~1,100 |
| +8 percentage points | ~410 |

The formula: n = 7.85 × [p₁(1−p₁) + p₂(1−p₂)] / δ²

For a 5-point sensitivity target, you need roughly 5× your current task count.

---

**Post 5**

One more fix: if your bootstrap p-value is "0.0" with B=2,000 replicates, that's technically wrong.

The minimum achievable bootstrap p-value is 1/(B+1) = 1/2001 ≈ 0.0005.

Write: "p < 0.0005 (0 of 2,000 replicates exceeded the observed delta)" — not "p = 0.0."

---

**Post 6**

Full explainer — MDE derivation, the sample size table, CI width explained from first principles, and the exact edits to make in your evaluation report:

https://open.substack.com/pub/kemeriyamajor/p/p-071-doesnt-mean-no-improvement?r=2xdj7z&utm_campaign=post&utm_medium=web&showWelcomeOnShare=true

Runnable calculator: `sources/power_calculator.py` in the repo.
