"""
Demonstrates variant-level vs probe-level train/eval splitting on an augmented dataset.

Variant-level split (the bug): random shuffle over all examples distributes paraphrases
of the same probe across train and eval. Eval loss measures memorization, not generalization.

Probe-level split (the fix): all variants of a probe stay on the same side of the split.
Eval set contains only probes the model has never seen in any form.

Run: python split_comparison.py
"""

import random
from collections import defaultdict

random.seed(42)

# ── Synthetic dataset ────────────────────────────────────────────────────────
# 10 probes, each with 10 Magpie paraphrase variants (matches Mikias's structure)

def make_dataset(n_probes=10, variants_per_probe=10):
    examples = []
    for probe_id in range(n_probes):
        for variant_id in range(variants_per_probe):
            examples.append({
                "probe_id": probe_id,
                "variant_id": variant_id,
                "text": f"probe_{probe_id}_variant_{variant_id}",
            })
    return examples


def variant_level_split(examples, train_ratio=0.8):
    """Current approach in generate_full_training_data.py — shuffles at the example level."""
    data = examples[:]
    random.shuffle(data)
    split = int(train_ratio * len(data))
    return data[:split], data[split:]


def probe_level_split(examples, train_ratio=0.8):
    """Correct approach — keeps all variants of a probe on one side."""
    groups = defaultdict(list)
    for ex in examples:
        groups[ex["probe_id"]].append(ex)

    probe_ids = list(groups.keys())
    random.shuffle(probe_ids)
    split = int(train_ratio * len(probe_ids))
    train_probes = set(probe_ids[:split])

    train = [ex for ex in examples if ex["probe_id"] in train_probes]
    eval_ = [ex for ex in examples if ex["probe_id"] not in train_probes]
    return train, eval_


def probe_overlap(train, eval_):
    """Returns set of probe_ids that appear in both train and eval."""
    train_probes = {ex["probe_id"] for ex in train}
    eval_probes  = {ex["probe_id"] for ex in eval_}
    return train_probes & eval_probes


# ── Run comparison ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    examples = make_dataset()
    print(f"Total examples: {len(examples)}  ({len(set(e['probe_id'] for e in examples))} probes × 10 variants)\n")

    # Variant-level split
    v_train, v_eval = variant_level_split(examples)
    v_overlap = probe_overlap(v_train, v_eval)
    print("── Variant-level split (current) ──────────────────")
    print(f"  Train: {len(v_train)} examples | Eval: {len(v_eval)} examples")
    print(f"  Probes appearing in BOTH train and eval: {sorted(v_overlap)}")
    print(f"  Leakage rate: {len(v_overlap)}/{len(set(e['probe_id'] for e in examples))} probes contaminated")
    print()

    # Probe-level split
    p_train, p_eval = probe_level_split(examples)
    p_overlap = probe_overlap(p_train, p_eval)
    print("── Probe-level split (fix) ─────────────────────────")
    print(f"  Train: {len(p_train)} examples | Eval: {len(p_eval)} examples")
    print(f"  Probes appearing in BOTH train and eval: {sorted(p_overlap)}")
    print(f"  Leakage rate: {len(p_overlap)}/{len(set(e['probe_id'] for e in examples))} probes contaminated")
    print()

    print("── What this means for checkpoint selection ─────────")
    print("  Variant-level: eval loss measures whether model recalls probe content")
    print("                 it already saw in 8 training variants → picks deepest memorizer")
    print("  Probe-level:   eval loss measures whether model generalizes to unseen probes")
    print("                 → picks best-generalizing checkpoint")
    print()
    print("  Fix in train.py: set metric_for_best_model='eval_rubric_score', greater_is_better=True")
    print("  Fix in generate_full_training_data.py: replace example-level shuffle with probe_level_split()")
