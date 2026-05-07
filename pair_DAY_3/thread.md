# LinkedIn Thread — Day 3

*Topic: Variant-level data leakage in augmented SFT datasets — why your eval loss is lying to you*

---

**Post 1**

Your SFT eval loss is 0.02. Your model seems to be learning perfectly.

It's not. Your eval set is a paraphrase set of your training data, and you selected the wrong checkpoint. Here's what's actually happening. 🧵

---

**Post 2**

If you trained on an augmented dataset — one probe, 10 paraphrase variants — and split at the example level, your eval set contains variants of the same probes as training.

The model sees a probe 8 times in training. Eval shows it the same probe in different phrasing. That's not generalization. That's recall.

Eval loss near zero = probe memorization, not learning.

---

**Post 3**

`load_best_model_at_end=True` selects the checkpoint with minimum eval loss.

On a variant-level split, that's the checkpoint where probe memorization is most complete — not the checkpoint that generalizes to unseen data.

You published the deepest memorizer to HuggingFace.

---

**Post 4**

The fix is two things:

1. Probe-level split in data generation — all variants of one probe stay on the same side.

```python
# Wrong: shuffle all examples
random.shuffle(all_examples)

# Right: shuffle probes, then reconstruct
random.shuffle(probe_ids)
train = [e for e in all if e['probe_id'] in train_probes]
```

2. Replace eval loss as the checkpoint selection metric with your held-out rubric score.

---

**Post 5**

In TrainingArguments, two lines:

```python
metric_for_best_model = "eval_rubric_score"
greater_is_better = True
```

Keep the variant-level eval split for monitoring training stability. Use the probe-disjoint held-out set to select the checkpoint. They measure different things.

---

**Post 6**

Full explainer — what variant-level leakage looks like in code, why 0.0213 is a memorization number, and the exact callback structure to log rubric score as a Trainer metric:

[blog post link]

Runnable comparison script: `sources/split_comparison.py` in the repo.
