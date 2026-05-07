# Day 3 Question — Kemeriya

## Topic: Training and Post-Training Mechanics

---

## Final Sharpened Question

TRL's `ORPOTrainer` computes the odds-ratio using per-token averaged log probabilities: `log_p = (1/T) * Σ log p(t_i)`. My signal_grounding preference pairs have errors distributed across many tokens (forbidden phrases throughout the completion). My dual-control preference pairs share an identical reasoning trace between chosen and rejected — only the final routing token differs.

**Does per-token averaging explain why signal_grounding improved +11.8 pts but dual_control regressed −4.5 pts at the same β and training step count — because the gradient signal on dual-control pairs was diluted across ~100 tokens when only 1 token was actually wrong?**

---

## Connection to Existing Artifact

- `Week-11/synthesis_memos/memo_07_orpo.md` lines 12–18: documents `L_ORPO = L_SFT + λ · L_OR` but says nothing about per-token averaging in the implementation
- `Week-11/synthesis_memos/memo_07_orpo.md` lines 38–46: justifies β=0.2 as applying "more preference pressure" — treats all 158 pairs as equivalent without accounting for where the error sits in the sequence
- `Week-11/submission_report.md` Section 7: records the +11.8 / −4.5 split as unresolved; per-token dilution is not named as a hypothesis

---

## What a Satisfying Answer Looks Like

A 600–900 word explainer that:
1. States how TRL computes `log_p` for ORPO's odds-ratio term and why
2. Shows the gradient magnitude difference between a distributed-error pair and a terminal-error pair at the same β
3. Says whether β=0.2 helps or just scales an already-diluted signal
4. Names the concrete fix before the 750-step follow-up run
