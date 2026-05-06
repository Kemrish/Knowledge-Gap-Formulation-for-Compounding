# Asker Sign-Off — Day 2

**Asker**: Kemeriya
**Explainer author**: Tsegay Assefa
**Question**: What is the model doing at the token level in JSON-prompting vs tool_use, and would using tool_use with a tighter schema have prevented dual-control stalling?

**Gap closure judgment**: ✅ Closed

---

## What I Understand Now That I Did Not Before

Before this explainer I thought the dual-control stalling was a JSON-parsing reliability problem — that if I had used the tool_use API instead of JSON prompting, the structured output would have forced better behavior. I was wrong about the cause.

Tsegay's explainer made two things clear. First: tool_use is not logit masking at the decision level. The model's choice of which action to suggest is trained behavior, not a hard constraint — switching to tool_use would not have stopped the model from generating conservative outputs. Second: the stalling was caused by the schema itself. By including `suggested_next_action` in the JSON I asked the model to act as a policy engine. A well-calibrated model is correctly cautious about autonomous actions, so it defaulted to `route_to_human`. That wasn't a failure — it was the model doing exactly what I asked.

The fix is removing `suggested_next_action` from the system prompt schema entirely, which I have done in `reply_handler.py`. The model is now a classifier only. `policy.py` decides the action, which is what it was already doing — the field was generating tokens that were immediately discarded, and those tokens were probably nudging the model's internal state toward conservatism in the intent classification itself.

I also now understand where tool_use does add real value: parse failures go to zero (API handles JSON validation), `enum` constraints make hallucinated intent categories harder, and `tool_choice: "any"` removes the plain-text fallback. These are reliability improvements worth having, separate from the stalling question.
