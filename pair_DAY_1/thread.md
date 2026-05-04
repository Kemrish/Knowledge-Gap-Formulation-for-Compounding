# Tweet Thread — Day 1

*Topic: What does "one forward pass" through Qwen2.5-7B actually cost?*

---

**Tweet 1**

Your LLM judge rationale says "near-zero marginal cost — one forward pass."

Here's what one forward pass through a 7B model at 1,024 tokens actually costs — and why your *input*, not your *output*, is the entire story. 🧵

---

**Tweet 2**

Transformer inference has two phases with completely different hardware bottlenecks:

PREFILL — all 1,024 input tokens processed in parallel → matrix×matrix → compute-bound
DECODE — 1 output token at a time → matrix×vector → memory-bandwidth-bound

Same model. Different physics.

---

**Tweet 3**

FLOPs for Qwen2.5-7B (7.62B params):

Prefill (1,024 tok): 2 × 7.62B × 1,024 = **15.6 TFLOPs**
Decode (2 tok avg):  2 × 7.62B × 2    = **30.5 GFLOPs**

That's a 512:1 ratio. The 1–3 token score label adds <0.2% of the arithmetic work.

But prefill still takes **89% of wall time** on every GPU tested.

---

**Tweet 4**

Wall-time estimates (batch=1, BF16, roofline model):

| GPU          | Prefill  | Decode (2 tok) | Decode tok/s |
|--------------|----------|----------------|--------------|
| A100 SXM4    | ~125 ms  | ~15 ms         | ~131         |
| T4           | ~800 ms  | ~102 ms        | ~20          |
| RTX 3090     | ~313 ms  | ~33 ms         | ~61          |

Shorten the prompt → directly cuts cost. Faster decode → barely helps.

---

**Tweet 5**

"One forward pass" is imprecise.

`model.generate(max_new_tokens=3)` runs 3–4 forward passes: 1 prefill + 2–3 decode steps.

True one-pass mode exists: extract logit probabilities at position 1,024 for your score tokens and argmax directly. No decode. This is how `lm-eval-harness` loglikelihood mode works. Most judge implementations quietly run multiple passes.

---

**Tweet 6**

Full breakdown with calculation script, hardware comparison table, and KV cache memory analysis:

https://open.substack.com/pub/kemeriyamajor/p/one-forward-pass-what-a-qwen25-7b?r=2xdj7z&utm_campaign=post&utm_medium=web&showWelcomeOnShare=true

Sources: Pope et al. 2022 (Efficiently Scaling Transformer Inference) + Qwen2.5 Technical Report 2024.
