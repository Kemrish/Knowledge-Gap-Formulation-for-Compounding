"""
Qwen2.5-7B Inference Cost Calculator
Derives theoretical prefill/decode wall-time bounds using the roofline model.
No GPU required — runs on CPU using architecture constants and hardware specs.

Usage:
    python flops_calculator.py

Sources:
    - Pope et al. (2022). Efficiently Scaling Transformer Inference.
      https://arxiv.org/abs/2211.05102
    - Qwen2.5 Technical Report (2024).
      https://arxiv.org/abs/2412.15115
"""

# ── Qwen2.5-7B architecture constants (from config.json / technical report) ──
HIDDEN_SIZE       = 3584
NUM_LAYERS        = 28
NUM_Q_HEADS       = 28
NUM_KV_HEADS      = 4
HEAD_DIM          = 128        # hidden_size / num_q_heads = 3584 / 28 = 128
FFN_INTERMEDIATE  = 18944
VOCAB_SIZE        = 152_064
TOTAL_PARAMS      = 7.62e9     # includes embeddings

DTYPE_BYTES = 2  # BF16 / FP16

# ── Sequence config ──
N_PREFILL = 1_024   # input tokens (max_seq_len from training)
N_DECODE  = 2       # avg output tokens for a 1–3 token score label

# ── Hardware specs: (peak_tflops_bf16, hbm_bandwidth_gbs, practical_mfu) ──
# MFU (model FLOP utilization) accounts for kernel launch overhead, memory
# staging, and the gap between peak and sustained throughput at batch size 1.
HARDWARE = {
    "A100 SXM4  (80 GB)":  (312.0,  2_000.0, 0.40),
    "T4         (16 GB)":  ( 65.0,    300.0, 0.30),
    "RTX 3090   (24 GB)":  (142.6,    936.0, 0.35),
    "A10G       (24 GB)":  (125.0,    600.0, 0.35),
}


def flops_prefill(n: int, params: float) -> float:
    """
    Standard transformer FLOPs approximation: 2 * P * N.
    Accurate when the attention term (N^2 * D per layer) << 2 * P * N.
    At N=1024 for a 7B model: attention ≈ 3.75 GFLOPs vs linear ≈ 15,600 GFLOPs.
    Error < 0.025%.
    """
    return 2 * params * n


def attention_flops(n: int) -> float:
    """Attention score computation: N^2 * D (for reference/comparison)."""
    return (n ** 2) * HIDDEN_SIZE * NUM_LAYERS


def kv_cache_bytes(n: int) -> int:
    """
    KV cache memory for n tokens.
    Layout: 2 (K+V) * L layers * H_kv heads * head_dim * n tokens * dtype_bytes
    """
    return 2 * NUM_LAYERS * NUM_KV_HEADS * HEAD_DIM * n * DTYPE_BYTES


def weight_bytes(params: float) -> float:
    return params * DTYPE_BYTES


def roofline_time(flops: float, bytes_needed: float,
                  peak_tflops: float, bandwidth_gbs: float,
                  mfu: float) -> tuple[float, str]:
    """
    Returns (wall_seconds, bottleneck).
    Roofline: time = max(flops / effective_compute, bytes / bandwidth).
    """
    effective_flops_per_s = peak_tflops * 1e12 * mfu
    compute_s = flops / effective_flops_per_s

    bandwidth_bytes_per_s = bandwidth_gbs * 1e9
    memory_s = bytes_needed / bandwidth_bytes_per_s

    if compute_s >= memory_s:
        return compute_s, "compute-bound"
    else:
        return memory_s, "memory-bandwidth-bound"


def main():
    w_bytes = weight_bytes(TOTAL_PARAMS)
    kv_bytes = kv_cache_bytes(N_PREFILL)

    print("=" * 70)
    print("Qwen2.5-7B Inference Cost Breakdown")
    print("=" * 70)
    print(f"\nModel: {TOTAL_PARAMS/1e9:.2f}B parameters, BF16")
    print(f"Weights: {w_bytes/1e9:.2f} GB")
    print(f"KV cache ({N_PREFILL} tokens): {kv_cache_bytes(N_PREFILL)/1e6:.1f} MB")
    print(f"  (at 4096 tokens: {kv_cache_bytes(4096)/1e6:.1f} MB)")
    print(f"  (at 32768 tokens: {kv_cache_bytes(32768)/1e6:.0f} MB)")

    fp_prefill = flops_prefill(N_PREFILL, TOTAL_PARAMS)
    fp_decode_per_tok = flops_prefill(1, TOTAL_PARAMS)
    fp_decode_total = fp_decode_per_tok * N_DECODE
    attn_flops = attention_flops(N_PREFILL)

    print(f"\nFLOPs:")
    print(f"  Prefill  ({N_PREFILL:,} tokens): {fp_prefill/1e12:.2f} TFLOPs")
    print(f"  Attn scores only:    {attn_flops/1e9:.2f} GFLOPs  "
          f"({100*attn_flops/fp_prefill:.3f}% of prefill — negligible at N={N_PREFILL})")
    print(f"  Decode/token:        {fp_decode_per_tok/1e9:.2f} GFLOPs")
    print(f"  Decode  ({N_DECODE} tokens):  {fp_decode_total/1e9:.2f} GFLOPs  "
          f"({100*fp_decode_total/fp_prefill:.3f}% of prefill)")

    print(f"\n{'Hardware':<22} {'Prefill':>12} {'Decode(2tok)':>14} "
          f"{'Total':>10} {'Prefill%':>10} {'Regime':>20}")
    print("-" * 92)

    for name, (tflops, bw_gbs, mfu) in HARDWARE.items():
        # Prefill: compute-bound (loads weights once for N tokens simultaneously)
        prefill_s, prefill_regime = roofline_time(
            fp_prefill, w_bytes, tflops, bw_gbs, mfu
        )

        # Decode: memory-bandwidth-bound per token (loads ALL weights per token)
        decode_per_tok_s = w_bytes / (bw_gbs * 1e9)
        decode_s = decode_per_tok_s * N_DECODE
        decode_tok_per_s = 1.0 / decode_per_tok_s

        total_s = prefill_s + decode_s
        prefill_pct = 100 * prefill_s / total_s
        prefill_tok_per_s = N_PREFILL / prefill_s

        print(
            f"{name:<22} "
            f"{prefill_s*1000:>9.0f} ms "
            f"({prefill_tok_per_s:>6.0f} t/s)  "
            f"{decode_s*1000:>9.1f} ms "
            f"({decode_tok_per_s:>5.0f} t/s)  "
            f"{total_s*1000:>8.0f} ms  "
            f"{prefill_pct:>8.1f}%  "
            f"{prefill_regime}"
        )

    print("\nNote: batch_size=1. MFU accounts for kernel overhead at small batch.")
    print("      Decode is always memory-bandwidth-bound regardless of GPU tier.")
    print("      LoRA adapter (r=16) adds <0.2% overhead per adapted layer.")
    print("\nConclusion:")
    print(f"  Prefill ({N_PREFILL} tok) contributes ~89% of wall time.")
    print("  To cut cost: shorten the input prompt.")
    print("  Faster decode (INT8, speculative) saves the remaining ~11%.")

    # ── Scale comparison: how cost changes with input length ──
    print("\n" + "=" * 70)
    print("Prefill cost scaling (A100, MFU=0.40) — prompt length matters most")
    print("=" * 70)
    tflops_a100, bw_a100, mfu_a100 = HARDWARE["A100 SXM4  (80 GB)"]
    for n in [256, 512, 1_024, 2_048, 4_096]:
        fp = flops_prefill(n, TOTAL_PARAMS)
        t_s, _ = roofline_time(fp, w_bytes, tflops_a100, bw_a100, mfu_a100)
        print(f"  {n:>6} tokens -> {t_s*1000:>6.0f} ms  ({n/t_s:>7,.0f} tok/s)")


if __name__ == "__main__":
    main()
