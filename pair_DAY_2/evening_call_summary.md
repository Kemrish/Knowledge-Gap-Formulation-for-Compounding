# Evening Call Summary — Day 2

**Pair**: Kemeriya ↔ Tsegay Assefa
**Date**: 2026-05-06
**Duration**: ~35 minutes

---

## Feedback Tsegay Gave on Kemeriya's Explainer (tool_result blocks / multi-turn state)

Tsegay said the explainer landed the core mechanism well — he now understood that the model doesn't maintain state internally across turns, it reads the full messages array fresh each time, and missing `tool_result` blocks meant the model literally couldn't see its own previous tool outputs. What didn't land initially was the section on message ordering — the explainer said `tool_result` must immediately follow `tool_use` in the messages array but didn't show what the broken version looked like vs the correct one. He couldn't tell if his bug was ordering or omission. Kemeriya revised that section to include a side-by-side: broken (tool_use block present, tool_result missing) vs correct (tool_use followed by tool_result in the next user turn). After that revision Tsegay confirmed it matched exactly what his orchestrator was doing wrong.

## Feedback Kemeriya Gave on Tsegay's Explainer (JSON-prompting vs tool_use)

Kemeriya's main feedback: the explainer answered the logit masking question clearly but buried the most useful finding — that removing `suggested_next_action` from the schema is the real fix — in the third section. A reader scanning the post would miss it. Tsegay moved that finding to the second section right after explaining what tool_use is, so it sits next to the mechanism that explains why the field causes conservatism. Kemeriya also asked Tsegay to be more direct about whether the fix requires switching to tool_use or not. He revised one line to say explicitly: "You can keep JSON prompting. The fix is the schema, not the API."
