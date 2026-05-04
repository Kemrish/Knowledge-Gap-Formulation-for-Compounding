# Sources — Day 1 Explainer

## Canonical Papers

### 1. Pope, R. et al. (2022). *Efficiently Scaling Transformer Inference*
**URL**: https://arxiv.org/abs/2211.05102  
**Publisher**: Google Research (MLSys 2023 / ICLR workshop)  
**Why canonical**: The definitive paper on prefill/decode cost modeling for large transformers. Introduces the partitioned-compute framing: prefill is compute-bound (matrix-matrix), decode is memory-bandwidth-bound (matrix-vector). Derives the arithmetic intensity threshold that determines which regime a given model/hardware pair falls into. Directly backs the roofline estimates in the explainer.  
**What I used**: Section 2 (cost model), Table 1 (hardware specs), Figure 3 (prefill vs decode latency breakdown). The 2×P×N FLOPs approximation is from their Equation 1.

---

### 2. Qwen Team, Alibaba Cloud (2024). *Qwen2.5 Technical Report*
**URL**: https://arxiv.org/abs/2412.15115  
**Why canonical**: Primary source for Qwen2.5-7B architecture constants used in all calculations. Specifies: hidden_size=3584, num_layers=28, num_attention_heads=28, num_key_value_heads=4, intermediate_size=18944, vocab_size=152,064. Without these, the FLOPs and memory estimates would be approximate guesses.  
**What I used**: Table 1 (model architecture), Section 3.1 (training configuration), Appendix A (model card with parameter counts).

---

## Tool / Demonstration

### `sources/flops_calculator.py` (this repo)
A standalone Python script (no GPU required) that:
- Takes Qwen2.5-7B architecture constants and hardware specs as inputs
- Applies the roofline model to derive prefill and decode wall-time bounds
- Produces the hardware comparison table in the explainer
- Shows KV cache memory scaling across context lengths (1K → 32K tokens)
- Explains why decode is always memory-bandwidth-bound regardless of GPU tier

Run with: `python sources/flops_calculator.py`

---

## Supporting Reference

### Williams, S., Waterman, A., Patterson, D. (2009). *Roofline: An Insightful Visual Performance Model for Multicore Architectures*
**URL**: https://doi.org/10.1145/1498765.1498785  
**Publisher**: Communications of the ACM  
**Why relevant**: The roofline model is the analytical framework behind all wall-time estimates. The bound: `time ≥ max(FLOPs / peak_compute, bytes / peak_bandwidth)` is used throughout the explainer to decompose prefill (compute-bound) from decode (bandwidth-bound).

---

## Follow-On Directions (for deeper reading)

- **FlashAttention** (Dao et al., 2022, https://arxiv.org/abs/2205.14135): Reduces HBM reads/writes during attention by fusing the softmax and matmul. Most relevant for prefill at long sequence lengths where attention computation starts rivaling linear-layer cost.
- **Speculative Decoding** (Leviathan et al., 2023, https://arxiv.org/abs/2211.17192): Addresses the memory-bandwidth bottleneck in decode by using a smaller draft model to generate candidate tokens in parallel. Provides 2–3× decode speedup on A100-class hardware.
- **vLLM profiling tool** (https://github.com/vllm-project/vllm): `python benchmarks/benchmark_throughput.py --model Qwen/Qwen2.5-7B-Instruct --backend vllm` reports prefill and decode latency separately in JSON output. The most practical way to measure the actual split on real hardware.
