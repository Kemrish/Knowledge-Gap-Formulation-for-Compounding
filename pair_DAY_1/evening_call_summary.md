# Evening Call Summary — Day 1

**Pair**: Kemeriya ↔ Yosef
**Date**: 2026-05-04
**Duration**: ~30 minutes

---

## Feedback Yosef Gave on Kemeriya's Explainer (7B judge cost)

Yosef's gap was about whether "near-zero marginal cost — one forward pass" held up. Two things did not land in the first draft: (1) The "relative to what?" framing was implicit — Yosef said he could not tell from the explainer alone whether the claim was being made relative to human labeling or relative to other inference calls in his system, and those are completely different comparisons. (2) The "one forward pass" nuance section listed `model.generate()` vs logit extraction but did not say which mode Yosef's actual implementation uses, leaving the most actionable part unresolved.

## What Kemeriya Revised

Added the three-part breakdown of "near-zero" comparisons (vs human annotation, vs absolute cost at scale, vs production system) as a distinct section rather than scattered through the prose. Added the closing paragraph that states the honest version of the claim explicitly, making clear it applies to Yosef's specific rationale document. The "one forward pass" section now names `lm-evaluation-harness loglikelihood mode` as the concrete reference for the true one-pass pattern, so Yosef can check his own code against that.

## Feedback Kemeriya Gave on Yosef's Explainer (0.8B latency)

The explainer correctly identified the prefill/decode split and gave accurate theoretical numbers. The key finding that the 19.7s is ~56× the theoretical inference time landed clearly. The one thing that was initially missing: the explainer named batch inference as the correct fix but did not say *how* to batch in the Colab eval harness specifically — it stayed at the level of "use batching." After Kemeriya pushed, Yosef added the concrete note that passing all 216 tasks as a batched input in a single `model.generate()` call eliminates the per-call overhead, and that this can be done without changing the harness architecture.
