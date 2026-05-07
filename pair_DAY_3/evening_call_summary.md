# Evening Call Summary — Day 3

**Pair**: Kemeriya ↔ Mikias Dagem
**Date**: 2026-05-07

---

## Feedback on Kemeriya's Explainer (variant-level leakage — written for Mikias)

**What Mikias said landed:**

The probe_42 walkthrough was the part that clicked for him. He said he'd read about data leakage in general before but it always felt abstract — "contamination" as a concept. Seeing it written out as 8 train variants + 2 eval variants of the same underlying company profile made it concrete. He said: "I knew my eval loss was weirdly low but I kept thinking maybe the task is just easy. You naming it as memorization versus generalization was the thing that actually diagnosed it."

He also said the sentence "0.0213 is very likely contamination-driven memorization" was useful precisely because it gave him a number to anchor to. He hadn't compared his eval loss against typical SFT ranges before.

**What Mikias said didn't land / wanted changed:**

The fix section told him *what* to change but not *exactly how*. He knew `metric_for_best_model` needed to change but didn't know what the custom callback for rubric scoring looked like in Trainer. He asked: "Can you show me the actual kwargs I need to add to TrainingArguments?"

Kemeriya revised the fix section to include the two specific `TrainingArguments` changes:
```python
metric_for_best_model = "eval_rubric_score"
greater_is_better = True
```
And added a note that the rubric callback needs to log the metric under the exact key `eval_rubric_score` using `trainer.log()` inside an `on_evaluate` method.

---

## Feedback on Mikias's Explainer (per-token ORPO averaging — written for Kemeriya)

**What landed:**

The gradient magnitude calculation was what Kemeriya needed. Mikias worked through the concrete ratio: 30 wrong tokens in a signal-grounding pair versus 1 wrong token in a dual-control pair, both 100 tokens long — the odds-ratio gradient contribution ratio is approximately 30:1 at the same β. Kemeriya said: "That's the number I couldn't derive from reading the memo. I knew the outcomes were different, I just didn't have the mechanism." She also said the confirmation that β=0.2 doesn't help — it scales both sides proportionally — was the part she most needed to hear, because the memo's reasoning implied increasing β would fix the categorical wrongness problem.

**What Kemeriya said didn't land:**

The explainer answered whether dilution explains the split but didn't say what to actually change before the 750-step run. Kemeriya pushed: "Now that I know it's dilution, should I be rewriting the dual-control pairs to be shorter? Or is there a TRL flag I can set?" Mikias added a section naming the fix: either write shorter completions for dual-control pairs (reduce T so the dilution factor is smaller), or use token-level weighting by setting a high loss weight on the action token in the chosen/rejected completion. He noted SimPO's length-normalized reward as an alternative approach but flagged it drops the SFT component, which matters for catastrophic forgetting at 0.8B scale.

**What Kemeriya revised in response:**

Updated `memo_07_orpo.md` lines 38–46 to add the per-token averaging caveat and reframe the β reasoning. Updated `submission_report.md` Section 7 to name per-token dilution as the primary diagnosis and state the 750-step run diagnostic.

---

## Final Status

Both gaps closed. Kemeriya's grounding commit completed. Mikias's fixes to `generate_full_training_data.py`, `train.py:207`, and `model_card.md` noted as his grounding commit.
