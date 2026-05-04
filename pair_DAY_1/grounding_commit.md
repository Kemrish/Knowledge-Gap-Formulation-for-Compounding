# Grounding Commit — Day 1

**Asker**: Kemeriya
**Artifact edited**: `Week-11/submission_report.md` — Section 3: Cost per Task Delta and Production Implications

---

## What Changed

**File**: `c:\Users\Administrator\Desktop\TRP1\TRP1-coursework\Week-11\submission_report.md`
**Section**: "Production implications" (lines ~51–65, now expanded)

The original text said:

> "Hardware upgrade: A production A100 or H100 would reduce latency to approximately 2–4 seconds for a 0.8B LoRA — within acceptable range."

The edit adds a **Prefill/decode diagnosis** subsection that:

1. Derives the theoretical inference time for 0.8B on T4: ~84ms prefill + ~265ms decode = **~350ms per task**
2. Computes the actual overhead ratio: 19,712ms / 350ms ≈ **56×** — model compute is not the bottleneck
3. Corrects the hardware upgrade recommendation: an A100 addresses the ~350ms inference portion, not the ~19,350ms of sequential execution overhead
4. Names the correct first fix: **batch inference** (load the model once, pass all 216 tasks in a single call) which resolves the dominant overhead without hardware change
5. Revises the production verdict from "hardware-solvable" to "batch inference resolves it without hardware change"

## Why It Changed

Yosef's explainer on the prefill/decode split revealed that 0.8B model weights fit in 1.6 GB — leaving the T4's 16 GB almost entirely unused for weight storage. The theoretical inference is fast. The 56× gap between theory and measurement points to per-call overhead, not model compute. Recommending an A100 without this diagnosis was an undefended engineering claim that named the wrong bottleneck and the wrong fix. The corrected text names the mechanism and the right lever.

## Substack Blog URL (published artifact)

https://open.substack.com/pub/kemeriyamajor/p/one-forward-pass-what-a-qwen25-7b?r=2xdj7z&utm_campaign=post&utm_medium=web&showWelcomeOnShare=true
