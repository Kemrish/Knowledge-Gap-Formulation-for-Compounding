# Canonical Reading List — Week 12

**Author**: Kemeriya  
**Date**: 2026-05-09

Ten sources that were decisive in closing the eight gaps this week. Each entry states what it is, why it is canonical for this domain, and exactly what it resolved.

---

## 1. Vaswani et al. — "Attention Is All You Need" (NeurIPS 2017)

**Why canonical**: The primary architecture reference for transformer FLOPs estimation. The parameter count formulas and the separation between prefill (compute-bound, matrix–matrix) and decode (memory-bandwidth-bound, matrix–vector) are derivable from this paper's architecture description.

**What it resolved**: Gap 1 and Gap 2 — the prefill/decode split analysis for both the 0.8B adapter (T4 latency) and the 7B judge (Yosef's forward pass cost). Established that prefill is 89% of wall time because it is compute-bound while decode is memory-bandwidth-bound.

---

## 2. Williams, S. et al. — "Roofline: An Insightful Visual Performance Model" (CACM 2009)

**Why canonical**: The roofline model is the standard framework for determining whether a workload is compute-bound or memory-bandwidth-bound. Any hardware bottleneck analysis for neural network inference should start here.

**What it resolved**: Gap 1 — used to show that the 0.8B adapter's theoretical inference time is ~350ms (well below the 19.7s actual latency), proving the bottleneck is not model compute. The roofline calculation is implemented in `pair_DAY_1/sources/flops_calculator.py`.

---

## 3. Anthropic — Tool Use Documentation

**URL**: https://docs.anthropic.com/en/docs/build-with-claude/tool-use  
**Why canonical**: Primary source for how the tool_use API works — XML injection format, `tool_choice` modes, `input_schema` JSON Schema validation, and the `tool_use` / `tool_result` message pairing requirement for multi-turn loops.

**What it resolved**: Gap 3 and Gap 4 — confirmed that tool_use is trained behaviour + format injection, not logit masking, and that `tool_result` blocks are required for the model to see its own prior outputs.

---

## 4. Willard, B. & Louf, R. — "Efficient Guided Generation for Large Language Models" (2023)

**URL**: https://arxiv.org/abs/2307.09702  
**Why canonical**: The paper behind the `outlines` library. Describes FSM-based logit masking — the hard constraint that Anthropic's tool_use approximates through training. Essential for understanding the distinction between "trained to conform" and "mathematically guaranteed to conform."

**What it resolved**: Gap 3 and Gap 4 — established what true logit masking looks like and why tool_use is softer than it, which explained why schema design (not API choice) was the cause of dual-control stalling.

---

## 5. Hong, Lee & Thorne — "ORPO: Monolithic Preference Optimization without Reference Model" (EMNLP 2024)

**URL**: https://arxiv.org/abs/2403.07691  
**Why canonical**: The paper introducing ORPO. Defines the combined loss `L_ORPO = L_SFT + λ · L_OR` and motivates the per-token log-probability averaging in TRL's implementation for numerical stability across variable-length sequences.

**What it resolved**: Gap 5 — the per-token averaging property is what causes gradient dilution on terminal-error preference pairs (dual-control) versus distributed-error pairs (signal grounding), explaining the +11.8 / −4.5 split.

---

## 6. HuggingFace — Trainer Documentation (`metric_for_best_model`, `load_best_model_at_end`)

**URL**: https://huggingface.co/docs/transformers/main_classes/trainer  
**Why canonical**: Documents the exact mechanism by which `load_best_model_at_end=True` selects checkpoints — uses `metric_for_best_model` (default: `eval_loss`) and `greater_is_better` (default: `False`). The two kwargs that need to change to use a rubric score instead.

**What it resolved**: Gap 6 — confirmed that the published checkpoint-441 was selected by minimising variant-level eval loss, not by maximising held-out rubric score.

---

## 7. Pedregosa et al. — scikit-learn: Machine Learning in Python (JMLR 2011) / `GroupKFold` documentation

**URL**: https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.GroupKFold.html  
**Why canonical**: Standard reference for group-aware train/eval splitting. `GroupKFold` guarantees that all samples from the same group appear on the same side of the split — the property Mikias's variant-level split violated.

**What it resolved**: Gap 6 — provided the standard implementation and vocabulary for probe-level splitting, and the guarantee that no probe leaks across the split boundary.

---

## 8. Dror et al. — "The Hitchhiker's Guide to Testing Statistical Significance in NLP" (ACL 2018)

**URL**: https://aclanthology.org/P18-1128/  
**Why canonical**: The canonical NLP-specific reference for statistical testing. Recommends bootstrap and permutation tests over parametric tests for NLP metrics, and explicitly warns against reporting p = 0 with finite bootstrap samples.

**What it resolved**: Gap 7 and Gap 8 — the finite-bootstrap p-value bound and the convention for reporting "p < 1/(B+1)" when zero replicates exceed the observed statistic.

---

## 9. Cohen, J. — *Statistical Power Analysis for the Behavioral Sciences*, 2nd ed. (1988)

**Why canonical**: The foundational textbook for power analysis. Defines the MDE formula for two-proportion comparisons, the relationship between α, β, effect size, and sample size, and the standard z-test approximation used throughout Gaps 7 and 8.

**What it resolved**: Gap 7 and Gap 8 — the MDE ≈ 12 pp result for 216 binary tasks, the sample size targets for v0.2 (+3 pts → ~3,100 tasks, +5 pts → ~1,100, +8 pts → ~410), and the interpretive distinction between p = 0.71 as "no effect" versus "below detection threshold."

---

## 10. Efron, B. & Hastie, T. — *Computer Age Statistical Inference* (Cambridge, 2016)

**URL**: https://hastie.su.domains/CASI/  
**Why canonical**: Authoritative reference on modern statistical inference including bootstrap methods. Chapter 11 derives the finite-bootstrap p-value lower bound: with B replicates and k exceedances, the minimum achievable p-value is 1/(B+1).

**What it resolved**: Gap 7 and Gap 8 — the p = 0.0 → p < 0.0005 correction in `submission_report.md` Section 2, and the general principle that bootstrap p-values have resolution limits determined by the number of replicates.
