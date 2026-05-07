# Morning Call Summary — Day 3

**Pair**: Kemeriya ↔ Mikias Dagem
**Date**: 2026-05-07
**Duration**: ~25 minutes

---

## What Was Ambiguous in the Original Drafts

**Kemeriya's original question** started as "why did dual-control regress after ORPO training?" — a consequence question, not a mechanism question. Her partner pushed: "You have a memo that says you changed β from 0.1 to 0.2. Did the regression happen because of that change or despite it?" Kemeriya hadn't connected those two things. The memo says β=0.2 applies more preference pressure on categorically wrong outputs. The dual-control dimension has 33 preference pairs. She couldn't say whether more pressure on 33 pairs causes overshoot or helps. That uncertainty became the question. The partner also pointed out that the question needs to name what β actually does at the gradient level — "too much pressure" is vague without knowing what the gradient update looks like numerically.

**Mikias's original question** started as "why is my eval loss so low?" — a symptom question. Kemeriya pushed: "Is the eval set actually held-out, or does it contain paraphrases of training data?" Mikias hadn't framed it that way. He knew the split was random at the example level, but hadn't connected that to probe-level leakage. Once the leakage mechanism was named — 8 variants of each probe in train, 2 in eval — the question became precise: does variant-level splitting make eval loss a memorization metric rather than a generalization metric, and what should replace it for checkpoint selection?

---

## How Each Question Was Sharpened

**Kemeriya's question** was sharpened by: (a) anchoring to two specific artifacts in tension — the β=0.2 justification in `memo_07_orpo.md` and the −4.5 pts dual-control regression in `submission_report.md` Section 7, (b) replacing "why did it regress" with three specific hypotheses (overshoot / data sparsity / early-stop artefact) and asking which is consistent with ORPO's gradient mechanics, (c) naming the concrete diagnostic that would distinguish them — what the loss curves would look like under each hypothesis.

**Mikias's question** was sharpened by: (a) naming the mechanism — variant-level vs probe-level splitting — instead of just noting the suspicious eval loss number, (b) anchoring to three specific files in his repo (`generate_full_training_data.py`, `train.py:207`, `model_card.md`), (c) adding the key condition that a true held-out set already exists, which changes the question from "how do I get a clean eval signal" to "why am I not using the clean signal I already have."

---

## Final Status

Both questions committed as final by end of call. Partner confirmed Kemeriya's question is unambiguous. Kemeriya confirmed partner's question is unambiguous.
