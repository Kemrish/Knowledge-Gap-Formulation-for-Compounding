# Asker Sign-Off — Day 1

**Asker**: Kemeriya
**Explainer author**: Yosef
**Question**: What is the prefill/decode split for the 0.8B ORPO adapter on T4, and does that breakdown tell me whether the A100 upgrade targets the actual bottleneck?

**Gap closure judgment**: ✅ Closed

---

## What I Understand Now That I Did Not Before

Before this explainer I knew my adapter took 19.7 seconds and believed an A100 would fix it. I could not defend that recommendation at the mechanism level.

After reading Yosef's explainer: the theoretical inference time for 0.8B at 1,024 tokens on T4 is approximately 350ms per task — about 56× less than the measured 19.7s. The gap is not model compute. It is per-call overhead from sequential execution with no batching. An A100 reduces the 350ms inference portion by ~5× but leaves the ~19,350ms of surrounding overhead untouched. The correct first fix is batch inference: load the model once, pass all 216 tasks in a single call, and the wall time collapses to near-theoretical.

I also now understand the roofline model well enough to apply it myself: for a 0.8B model with 1.6 GB weights, the decode phase is memory-bandwidth-bound at 5.3ms per token on T4 (1.6 GB / 300 GB/s), while prefill is compute-bound at ~84ms for 1,024 tokens. This distinction — and knowing that 0.8B is small enough that weights fit easily and the bottleneck is not VRAM capacity — changes what I would recommend for any future deployment of a sub-1B adapter.

The grounding commit to `submission_report.md` reflects these corrections directly.
