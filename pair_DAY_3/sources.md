# Sources — Day 3 Explainer

*Explainer written by Kemeriya, answering Mikias Dagem's question on variant-level data leakage in augmented SFT datasets.*

---

## Canonical Papers / Primary Sources

### 1. HuggingFace Trainer — `metric_for_best_model` and `load_best_model_at_end`
**URL**: https://huggingface.co/docs/transformers/main_classes/trainer#transformers.TrainingArguments.metric_for_best_model
**Why canonical**: The official documentation specifying how `load_best_model_at_end=True` selects checkpoints — it uses `metric_for_best_model` (defaults to `eval_loss`) and `greater_is_better` (defaults to `False` for loss, `True` for accuracy metrics). This is the exact mechanism being corrupted by the variant-level split.
**What I used**: Confirmed that the default checkpoint selection criterion is minimum `eval_loss`, and that replacing it requires setting `metric_for_best_model` to a custom metric name logged by a callback.

---

### 2. scikit-learn — `GroupKFold` and group-aware splitting
**URL**: https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.GroupKFold.html
**Why canonical**: The standard reference for group-aware train/eval splitting. GroupKFold guarantees that all samples from the same group (here: all variants of the same probe) appear on the same side of the split. The documentation explicitly states: "The same group will not appear in two different folds" — which is the property Mikias's current split violates.
**What I used**: The concept of group-level splitting versus sample-level splitting, and the specific guarantee that group-aware splitting provides for augmented datasets.

---

### 3. Hong, Lee & Thorne — "ORPO: Monolithic Preference Optimization without Reference Model" (EMNLP 2024)
**URL**: https://arxiv.org/abs/2403.07691
**Why canonical**: Background paper for Kemeriya's own question (ORPO per-token averaging). Not directly about Mikias's question, but informs the broader Day 3 context on how training objectives interact with data structure.
**What I used**: ORPO loss formulation and the per-token log-probability averaging used in TRL's implementation, which is the mechanism behind Kemeriya's question answered by Mikias.

---

## Tool / Demonstration

### `sources/split_comparison.py` — runnable probe-level vs variant-level split comparison
**What it shows**: Generates a synthetic dataset of 10 probes × 10 variants, runs both split strategies, and prints the probe overlap count for each. Variant-level split produces ~10/10 contaminated probes. Probe-level split produces 0/10. Also prints the two `TrainingArguments` kwargs needed to fix checkpoint selection. Run with `python split_comparison.py`.

---

## Follow-On Directions

- **If the held-out rubric score fluctuates too much to use as a checkpoint metric**: compute it over a fixed 50-probe subset (not all 268) to reduce variance while keeping it probe-disjoint from training.
- **If rewriting dual-control pairs to be shorter is not feasible**: explore TRL's `token_weights` parameter (if available in the installed version) to upweight the action token in the loss computation.
- **For v0.2 dataset generation**: implement GroupKFold from scikit-learn directly in `generate_full_training_data.py` to make the probe-level guarantee explicit and testable.
