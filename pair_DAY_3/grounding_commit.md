# Grounding Commit — Day 3

**Asker**: Kemeriya
**Artifacts edited**: `Week-11/synthesis_memos/memo_07_orpo.md` and `Week-11/submission_report.md`

---

## Edit 1 — `Week-11/synthesis_memos/memo_07_orpo.md`

**What changed**: Added a caveat to the "Where I Disagree" section (lines 38–46). The original text justified β=0.2 purely on the basis of categorical wrongness in rejected outputs, treating all 158 preference pairs as equivalent under ORPO's odds-ratio term. The revised text adds that TRL's `ORPOTrainer` computes the odds ratio using per-token averaged log probabilities, and that this normalization makes the gradient contribution of a preference pair proportional to how many tokens differ between chosen and rejected — not just to how categorically wrong the rejection is. Dual-control pairs (wrong only in the final routing token) are systematically diluted relative to signal-grounding pairs (wrong patterns distributed across many tokens). The β=0.2 reasoning was correct in intent but incomplete: it raised the weight of the preference signal without accounting for the fact that the preference signal on dual-control pairs was already near-zero due to normalization.

**Why**: The memo's β justification is the only design decision connected to the dual-control regression. Leaving it uncorrected means any future reader — including a follow-up training run — would repeat the same mistake: increasing β to apply more pressure on pairs where the gradient is structurally diluted.

---

## Edit 2 — `Week-11/submission_report.md` Section 7

**What changed**: Added one paragraph to the "Most likely cause" subsection naming per-token gradient dilution as a third hypothesis alongside early-stop and data sparsity. The new paragraph states: dual-control preference pairs in this dataset share an identical reasoning trace between chosen and rejected, differing only in the final routing action. Under ORPO's per-token averaged log-probability computation, the odds-ratio gradient contribution from a 100-token completion where 99 tokens are identical is approximately 1/100th of the gradient from a completion where errors are distributed throughout. This is consistent with the observed split: signal_grounding pairs (errors throughout) gained +11.8 pts; dual-control pairs (error only in final token) regressed −4.5 pts at the same β and step count.

The paragraph also states the diagnostic for the 750-step follow-up run: enable per-dimension loss logging, and check whether dual-control train loss decreases at all. If it does not decrease, the cause is dilution. If it decreases but eval regresses, the cause is overfitting on 33 pairs. If both decrease together, the early-stop hypothesis was correct.

**Why**: The Section 7 "unresolved failure" listed only two hypotheses (early-stop and data sparsity) and stated the root cause was unknown. Per-token dilution is a third hypothesis that is mechanistically distinct from the other two and makes different predictions about the fix — rewrite shorter completions or use token-level weighting rather than more training steps or more pairs.
