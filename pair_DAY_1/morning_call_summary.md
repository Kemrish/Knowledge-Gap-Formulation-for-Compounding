# Morning Call Summary — Day 1

**Pair**: Kemeriya ↔ Yosef
**Date**: 2026-05-04
**Duration**: ~25 minutes

---

## What Was Ambiguous in the Original Drafts

**Kemeriya's original question** was too broad: "Why does my ORPO adapter take 19.7 seconds on T4 and would an A100 fix it?" The partner challenged: "Are you asking about the mechanism or the recommendation? Those are different questions." The first version didn't name which specific artifact contained the undefended claim, and "would A100 fix it" is a yes/no question — not a gap-closing one.

**Yosef's original question** about the 7B judge initially framed as: "Is one forward pass really cheap?" The challenge from Kemeriya: "What do you mean by cheap — relative to what?" The partner was conflating two separate claims: (1) it's one forward pass architecturally, and (2) it's cheap. These needed splitting. The more diagnostic question is about the *split* between prefill and decode, because that's where the "near-zero" framing either holds or collapses.

---

## How Each Question Was Sharpened

**Kemeriya's question** was sharpened by: (a) naming the specific artifact section ("latency section of memo.md with the A100 recommendation"), (b) replacing the yes/no hardware question with a mechanism question ("is this compute-bound or bandwidth-bound?"), (c) making the resolution criterion explicit ("tell me which optimization lever to pull first at 0.8B scale"). The connection to Week 11 work was named precisely.

**Yosef's question** was sharpened by: (a) anchoring to the specific claim ("near-zero marginal cost — one forward pass"), (b) adding the concrete parameters (7B model, 1,024-token input, 1–3 token output), (c) asking for the split explicitly rather than just a yes/no on cost. The question now asks for something you can calculate and verify, not just an opinion.

---

## Final Status

Both questions committed as final by end of call. Partner confirmed Kemeriya's question is unambiguous to them. Kemeriya confirmed partner's question is unambiguous.
