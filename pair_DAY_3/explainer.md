# When Your Eval Loss Lies: Variant-Level Data Leakage in Augmented SFT Datasets

**By Kemeriya — Day 3 Explainer, answering Mikias Dagem's question**

---

Mikias's training script reports a best eval loss of **0.0213** at checkpoint-441. For a language model fine-tuned on a structured classification task, that number is suspicious. Typical SFT eval loss after convergence sits between 0.5 and 1.5. Near-zero usually means one of two things: the model has collapsed to degenerate outputs, or the eval set is contaminated. In his case it is contamination — and the specific contamination is a variant-level train/eval split on an augmented dataset.

Here is what that means, why it breaks checkpoint selection, and what to use instead.

---

## What a Variant-Level Split Actually Does

Mikias's dataset starts with probes — structured ICP evaluation scenarios, each grounded in specific Crunchbase signals, a correct segment label, and a required funding reference. Each probe has 10 Magpie paraphrase variants: same underlying facts, different surface phrasing. The full dataset is 1,440 examples (1,172 train + 268 eval).

The current split works like this:

```
all_examples = [probe_1_v1, probe_1_v2, ..., probe_1_v10,
                probe_2_v1, ..., probe_N_v10]
random.shuffle(all_examples)
train = all_examples[:1172]   # 80%
eval  = all_examples[1172:]   # 20%
```

After shuffling, the eval set contains roughly 2 variants of each probe and training contains roughly 8. **The eval set is a paraphrase set of the training data, not a held-out set.** Every eval example shares its probe's underlying signals with training examples: same company size, same funding stage, same correct segment label, same required phrasing constraints.

A probe-level split looks different:

```
probe_ids = list(unique probe identifiers)
random.shuffle(probe_ids)
train_probes = probe_ids[:split]
eval_probes  = probe_ids[split:]

train = [e for e in all_examples if e['probe_id'] in train_probes]
eval  = [e for e in all_examples if e['probe_id'] in eval_probes]
```

Now every probe is entirely on one side of the split. The eval set contains probes the model has never seen in any form. That is a generalization signal. The variant-level eval set is not.

---

## Why Eval Loss Becomes a Memorization Metric

At training step T, the model has processed 8 variants of probe_42. Each variant describes the same scenario: a company with Series B funding, 45 employees, 3 open engineering roles — the correct segment is `mid_market_saas`. The model learns to map `(funding_stage, headcount, open_roles)` to the correct label across 8 surface phrasings.

When the eval loop runs on eval_variant_2 of probe_42, the model sees: "Company X raised a $15M Series B... currently has 45 team members... recruiting for 3 engineering positions." The surface phrasing is new but the features are identical to what the model memorized from 8 training variants. The model produces the correct output with high confidence. The eval loss is near zero.

**The eval loss at 0.0213 is measuring probe recall, not generalization.** The model has been shown the underlying facts 8 times. The eval set tests whether it can retrieve them in a new phrasing. That is a harder version of training-set memorization — not a held-out test.

`load_best_model_at_end=True` in HuggingFace `Trainer` selects the checkpoint with minimum eval loss. Applied to a variant-level eval set, it selects the checkpoint where probe memorization is most complete. That is the deepest memorizer, not the best generalizer. Checkpoint-441 at 0.0213 was published to HuggingFace on that basis. Whether it generalizes to unseen ICP profiles — probes not in the training set — the current training setup cannot answer.

---

## The Correct Checkpoint Selection Criterion

Mikias's question already contains the answer: a true held-out set exists, producing the 78.8% rubric score. That score evaluates the model on examples it has never seen in any form. It is the generalization signal the eval loss was supposed to provide but does not.

The fix in `train.py` is to decouple the monitoring metric from the selection metric:

- **Keep** the variant-level eval split for training stability monitoring — it will catch NaN loss, catastrophic forgetting, or gradient explosion before the held-out evaluation runs.
- **Add** a custom callback that runs `scoring_evaluator.py` on the held-out set every N steps and logs a `eval_rubric_score` metric using `trainer.log({"eval_rubric_score": score})` inside an `on_evaluate` method.
- **Change two kwargs in `TrainingArguments`**:

```python
metric_for_best_model = "eval_rubric_score"
greater_is_better = True
```

The checkpoint selected will then be the one with the highest rubric score on examples the model never trained on — an actual generalization signal.

---

## The Three Concrete Fixes

**Fix 1 — `generate_full_training_data.py`**: Replace the example-level shuffle with a probe-level split. Group examples by `probe_id`, shuffle the probe list, assign probes to train/eval, then reconstruct the example lists. This ensures no probe leaks across the split boundary.

**Fix 2 — `train.py` line 207**: Replace the `EarlyStoppingCallback` (which monitors `eval_loss`) with a callback that runs rubric scoring on the held-out set and passes the result as a Trainer metric. Set `metric_for_best_model` to the rubric metric name.

**Fix 3 — `model_card.md`**: Add a single clarifying sentence: "The reported eval loss of 0.0213 is computed on a variant-level split and reflects paraphrase recall, not generalization. The held-out rubric score (78.8%) on a probe-disjoint set is the appropriate generalization estimate."

---

## What 0.0213 Actually Tells You

The 0.0213 eval loss is not meaningless. It confirms the model has fully internalized the training distribution — it can reproduce correct outputs across paraphrase variations of seen probes. That is a useful property for a rejection-sampling critic, where the model will encounter probes similar to ones it was trained on.

What it does not tell you is how the model behaves on a new client's ICP profile, a new funding stage combination, or a new phrasing pattern outside the Magpie vocabulary. For that, the 78.8% held-out rubric score is the number to watch — and maximizing it, not minimizing variant-level eval loss, is what checkpoint selection should optimize for.

---

**Sources**: Hong et al., "ORPO" (EMNLP 2024); HuggingFace `Trainer` documentation on `metric_for_best_model`; Mikias's `model_card.md` and `training/train.py`.
