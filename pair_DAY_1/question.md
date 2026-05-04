# Day 1 Question — Kemeriya

## Topic: Inference-Time Mechanics

---

## Final Sharpened Question

In my Week 11 submission I report a **19,712 ms average inference latency** per task for the Qwen3.5-0.8B ORPO adapter running on a Colab T4, and I recommend an A100 or H100 hardware upgrade to bring this to 2–4 seconds. But I cannot defend *why* the upgrade would close that gap at the mechanism level.

**Specifically: how does inference latency for a 0.8B-parameter model on a T4 split between the prefill phase (processing the input prompt tokens in parallel) and the decode phase (generating the output tokens sequentially), and does that breakdown tell me whether the 19.7-second figure is compute-bound (fixed by more FLOPS) or memory-bandwidth-bound (fixed by higher HBM bandwidth) — and therefore whether my A100 recommendation targets the actual bottleneck or whether quantization, smaller batch size during evaluation, or KV cache optimization would be a more targeted fix at this model scale?**

---

## Connection to Existing Artifact

**Week 11 `memo.md` / `submission_report.md` — latency section**, which reads (approximately):

> "Avg latency per task with adapter: 19,712 ms. This is borderline unacceptable for real-time sales workflows. Would require hardware upgrade (A100/H100) to reduce to 2–4 seconds, or batch overnight mode."

The recommendation is stated but the mechanism is not. I do not know whether the 19.7s is:
- Dominated by the prefill pass (compute-limited on T4 at 65 TFLOPS FP16), which an A100's 312 TFLOPS would shrink ~5×
- Dominated by the decode pass (memory-bandwidth-limited, where T4's 300 GB/s vs A100's 2 TB/s matters more)
- Dominated by model loading overhead (cold start on Colab), which neither A100 nor quantization would fix

Without this breakdown, the hardware upgrade recommendation is undefended and could be wrong for a 0.8B model specifically — at this size the weight-to-bandwidth ratio is very different from a 7B or 70B model.

---

## Why This Is Generalizable

Any FDE deploying a fine-tuned adapter for evaluation or real-time scoring faces this same diagnosis question before choosing between: (a) hardware upgrade, (b) quantization, (c) batching, or (d) a smaller backbone. The wrong choice is expensive. The right choice depends entirely on which phase dominates and whether the bottleneck is compute or memory bandwidth.

---

## What a Satisfying Answer Looks Like

A 600–900 word explainer that:
1. Names the prefill/decode split for a model of this parameter count on T4 specifically
2. Shows whether a 0.8B model on T4 is compute-bound or bandwidth-bound (and at what sequence length the regime changes)
3. Tells me concretely whether the A100 upgrade, INT8 quantization, or dynamic batching is the right first lever
4. Points to a way to measure the split in practice (profiler, timing hook, or framework flag)
