# Sources — Day 4 Explainer

*Explainer written by Kemeriya, answering Beamlak's question on benchmark power analysis and bootstrap p-value reporting.*

---

## Canonical Papers / Primary Sources

### 1. Cohen, J. (1988). *Statistical Power Analysis for the Behavioral Sciences* (2nd ed.)
**Why canonical**: The foundational reference for power analysis. Defines the MDE formula for two-proportion comparisons, the relationship between α, β, effect size, and sample size, and the standard z-test approximation used in the explainer calculation.
**What I used**: The two-proportion power formula: `n = (z_{α/2} + z_β)² × [p₁(1−p₁) + p₂(1−p₂)] / δ²`. Applied with z₀.₀₂₅ = 1.96, z₀.₂₀ = 0.842, baseline p₁ = 0.7459.

---

### 2. Efron, B. & Hastie, T. (2016). *Computer Age Statistical Inference*. Cambridge University Press.
**URL**: https://hastie.su.domains/CASI/
**Why canonical**: Authoritative reference on bootstrap methods. Chapter 11 covers bootstrap p-values and the finite-B lower bound. The statement that the minimum achievable bootstrap p-value with B replicates is 1/(B+1) is derived here.
**What I used**: The finite-bootstrap p-value bound: p_min = 1/(B+1). Applied to correct the "p = 0.0" reporting with B = 2,000.

---

### 3. Dror et al. (2018). *The Hitchhiker's Guide to Testing Statistical Significance in Natural Language Processing*. ACL 2018.
**URL**: https://aclanthology.org/P18-1128/
**Why canonical**: The canonical NLP-specific reference for statistical testing. Argues that bootstrap/permutation tests are preferable to parametric tests for NLP metrics, and explicitly warns against reporting p = 0 with finite bootstrap samples. Directly relevant to Tenacious-Bench's evaluation methodology.
**What I used**: The bootstrap p-value reporting convention and the recommendation for reporting "p < 1/(B+1)" when zero replicates exceed the observed statistic.

---

## Tool / Demonstration

### `sources/power_calculator.py` — sample size calculator for binary benchmarks
**What it shows**: Given a baseline pass rate, target effect size (in percentage points), significance level, and power target, computes the required number of tasks. Reproduces the three-row table in the explainer (+3, +5, +8 point targets → ~3,100, ~1,100, ~410 tasks). Run with `python power_calculator.py`.

---

## Follow-On Directions

- **For v0.2 design**: Use the +5 point target (n ≈ 1,100) as the minimum, not the exact number — budget for 1,200–1,500 to account for per-dimension subgroup analyses, which require larger samples than the overall comparison.
- **For reporting**: HuggingFace `evaluate` library documents its bootstrap CI implementation; check whether it reports p = 0 or p < 1/(B+1) by default.
- **For future ablations**: If comparing multiple adapter checkpoints (e.g., 200-step vs 750-step vs 1,000-step), apply a Bonferroni correction — each additional comparison inflates the false positive rate.
