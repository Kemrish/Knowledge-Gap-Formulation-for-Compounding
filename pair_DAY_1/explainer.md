# One Forward Pass: What a Qwen2.5-7B Judge Actually Costs at Inference

*Explainer for: "How much compute does one forward pass through a LoRA-adapted Qwen2.5-7B actually cost in wall-time and tokens/second, and how does that cost split between the prefill phase (1,024 input tokens) and the decode phase (1–3 token score label)?"*

---

Your rationale says the deployed LoRA judge adds "near-zero marginal cost — one forward pass." That framing is defensible in one context and misleading in another. To know which, you need to know what one forward pass through a 7B model actually costs — and how that cost splits between two phases that hit the GPU completely differently.

## The Two Phases Are Not the Same Operation

Transformer inference has two compute regimes: **prefill** and **decode**. They use the same weights but impose completely different demands on the hardware.

**Prefill** processes all 1,024 input tokens simultaneously. Every layer performs matrix–matrix multiplications: QKV projections across all token positions at once, FFN gates applied in parallel. The arithmetic intensity — FLOPs performed per byte loaded from HBM — is high. The GPU's compute units stay busy. This phase is *compute-bound*: throw more FLOPS at it and it gets faster proportionally.

**Decode** generates one token at a time, even with KV cache. Each step requires loading the full set of model weights from HBM to multiply against a single query vector. You're doing a matrix–vector multiply, not matrix–matrix. Arithmetic intensity collapses. The GPU is mostly waiting for data to arrive from memory, not computing. This phase is *memory-bandwidth-bound*: the bottleneck is how fast you can stream bytes from HBM, not how many FLOPS you have.

Same model, same weights, completely different physics.

## The Numbers for Qwen2.5-7B

Using the standard approximation — forward pass FLOPs ≈ 2 × P × N, which is accurate when the attention term (N² × D per layer) is small relative to the linear-layer term, which holds at N = 1,024 for a 7B model — the split is stark:

| Phase | Tokens | FLOPs |
|---|---|---|
| Prefill | 1,024 input tokens | 2 × 7.62B × 1,024 ≈ **15.6 TFLOPs** |
| Decode (per token) | 1 output token | 2 × 7.62B × 1 ≈ **15.3 GFLOPs** |
| Decode (2 tokens, avg label) | 2 output tokens | 30.5 GFLOPs |

Raw FLOPs ratio: 512:1. The 1–3 token score label adds less than 0.2% of the prefill's arithmetic work.

But wall-time does not follow FLOPs linearly, because the two phases are bottlenecked by different hardware resources. Using the roofline model — wall time = max(FLOPs / peak_FLOPS, bytes / peak_bandwidth) — and architecture constants from the Qwen2.5 technical report (7.62B params, BF16 = 15.24 GB weights):

| Hardware | Prefill (1,024 tok) | Decode (2 tok) | Prefill % of wall time | Decode tok/s |
|---|---|---|---|---|
| A100 SXM4 (312 TFLOPS / 2 TB/s) | ~125 ms | ~15 ms | **89%** | ~131 |
| T4 (65 TFLOPS / 300 GB/s) | ~800 ms | ~102 ms | **89%** | ~20 |
| RTX 3090 (142 TFLOPS / 936 GB/s) | ~313 ms | ~33 ms | **90%** | ~61 |

Prefill dominates at ~89–90% of wall time on every GPU tested. Your 1,024-token prompt is the bottleneck — not your 1–3 token output label.

The calculation script that produced these estimates is in `sources/flops_calculator.py`. You can run it without a GPU; it derives theoretical bounds from architecture constants and hardware specs.

**Note on the LoRA adapter**: LoRA adds rank-16 matrices to selected weight layers. At inference these are either merged (`W' = W + αBA/r`, no overhead) or applied separately (adds ≈0.17% per adapted layer). Either way, inference cost is effectively identical to the base Qwen2.5-7B. DPO training changes weights but not architecture; inference cost is unchanged.

## So Is "Near-Zero" Accurate?

It depends on what you're comparing to.

*Relative to human annotation*: A human rater costs $0.10–$1.00 per label. A self-hosted 7B judge call costs roughly $0.0002–$0.002 at cloud GPU rates. In this comparison, near-zero is accurate and the framing is fair.

*Absolute and operational*: 125–800 ms per call, 15.2 GB VRAM required, ~$0.0002/call. At 216 tasks × 5 trials = 1,080 judge calls per benchmark run, that's 135–864 GPU-minutes on T4. Nightly benchmark iterations add up. "Near-zero" stops being useful language at that scale.

*Relative to the production system it evaluates*: A Qwen2.5-7B judge call costs the same as any other 7B inference call. "Near-zero marginal cost" implies the judge is cheaper than the system under evaluation. That's only true if the production model is substantially larger.

The honest claim: *The judge adds approximately one prefill pass (15.6 TFLOPs on 1,024 tokens) plus 1–3 memory-bandwidth-limited decode steps. Total wall time: 125–800 ms depending on hardware. Cost is near-zero relative to human annotation; comparable to any other 7B inference call in the system.*

## The "One Forward Pass" Nuance

This framing is incomplete. Calling `model.generate(max_new_tokens=3)` runs:
1. One prefill pass (processes all 1,024 tokens, builds KV cache)
2. One decode step → first score token
3. One decode step → second score token
4. Possibly one more → third token

That is **3–4 forward passes**, not one. The phrase "one forward pass" likely comes from the intuition that prefill dominates, which is arithmetically correct — decode adds <0.2% of FLOPs — but it elides the actual execution model.

**True single-forward-pass scoring does exist.** Instead of generating, you extract the logit probabilities at the final input position (1,024) for the specific score tokens ("1", "2", "3", "4", "5") and argmax or softmax directly. No autoregressive decode at all. This is how `lm-evaluation-harness` operates in `loglikelihood` mode, and it is genuinely one forward pass — slightly faster (no decode steps), fully deterministic, and correct when the scoring vocabulary is fixed. Most LLM judge implementations call `model.generate()` and are therefore not running one forward pass. Worth checking which mode your judge uses.

## The KV Cache and Memory Pressure

Prefill also builds the KV cache, which occupies VRAM alongside model weights:

- Model weights (BF16): 7.62B × 2 bytes = **15.24 GB**  
- KV cache for 1,024 tokens: 2 × 28 layers × 4 KV heads × 128 head-dim × 1,024 tokens × 2 bytes ≈ **58 MB**

On a T4 (16 GB total VRAM), the model barely fits. The KV cache at 1,024 tokens is small (58 MB vs 15.24 GB of weights). But if your system ever runs longer contexts, KV cache grows linearly: at 4,096 tokens it reaches 232 MB; at 32K tokens, 1.8 GB — now meaningfully competing with the model itself on a 16 GB card. This is where KV cache eviction strategies and quantized KV caches (storing in INT8 instead of BF16) become load-bearing.

## Pointers

**Prefill/decode analysis**: Pope, R. et al. (2022). *Efficiently Scaling Transformer Inference*. Google Research. The foundational paper on the prefill/decode cost model, roofline analysis for transformers, and how model parallelism interacts with both phases. https://arxiv.org/abs/2211.05102

**Architecture constants**: Qwen Team (2024). *Qwen2.5 Technical Report*. Alibaba Cloud. Architecture spec, parameter counts, GQA configuration. https://arxiv.org/abs/2412.15115

**Roofline model**: Williams, S. et al. (2009). *Roofline: An Insightful Visual Performance Model for Multicore Architectures*. Communications of the ACM. The original bound: wall time ≥ max(FLOPs/peak_compute, bytes/peak_bandwidth).

**Practical profiling**: `torch.profiler` with `profile_memory=True` and `with_stack=True` will decompose a real inference call into prefill and decode phases. `vllm.benchmark_throughput` reports prefill and decode latency separately in its JSON output.

---

*The gap this closes: treating "one forward pass" as a cost axiom rather than a claim that needs decomposition. The cost is real, the bottleneck is the 1,024-token input, and the optimization lever (shorter prompts, not faster decode) follows directly from understanding which phase dominates.*
