# Asker Sign-Off — Day 3

**Asker**: Kemeriya
**Question**: Does TRL's per-token log-probability averaging in ORPO explain why signal_grounding improved +11.8 pts but dual_control regressed −4.5 pts — because dual-control pairs share identical reasoning traces and differ only in the final routing token, diluting the gradient signal by ~100×?

**Gap closure judgment**: ✅ Closed

---

## What Closed It

Mikias's explainer worked through the per-token averaging formula (`log_p = (1/T) * Σ log p(t_i)`) with a concrete example: a 100-token dual-control completion where tokens 1–99 are identical between chosen and rejected, and only token 100 differs. The odds-ratio gradient contribution from that one token gets divided by 100 in the average. For a signal-grounding completion where 30 of 100 tokens contain forbidden phrases, the average aggregates strong signal from all 30 wrong tokens. The gradient magnitude ratio between the two pair types at the same β is approximately 30:1 — which is consistent with a +11.8 / −4.5 split at the same training step count.

The explainer also confirmed that raising β from 0.1 to 0.2 does not fix the dilution: β scales the odds-ratio term uniformly, so it multiplies a diluted signal by 2, not a strong signal by 2. The structural cause is the normalization, not the weight.

**Concrete edit made**: `memo_07_orpo.md` updated to add per-token averaging caveat and corrected β reasoning. `submission_report.md` Section 7 updated to name per-token dilution as the primary hypothesis with specific diagnostic for the 750-step follow-up run.
