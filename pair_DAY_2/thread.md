# LinkedIn Thread — Day 2


*Topic: Does tool_use work by logit masking or is it just a prompt?*

---

**Post 1**

Does Anthropic's tool_use API work by logit masking — setting invalid token probabilities to zero? Or is it just a well-crafted prompt?

Neither. The answer is a third thing, and it changes how you build safety-critical agent loops. 🧵

---

**Post 2**

When you pass tools=[...] to the API, the definitions are serialized as XML blocks and prepended to Claude's system prompt. The model sees them as regular tokens.

The model then outputs a tool_use content block — not because invalid tokens are masked, but because it was trained to recognize tool definitions and respond with structured calls.

Tool selection = trained behavior, not hard constraint.

---

**Post 3**

So what IS constrained?

✅ tool_choice: "any" — forces a tool call (API rejects plain text responses)
✅ JSON validity of the input field — API validates against your schema
✅ enum values — harder to hallucinate outside the defined set

❌ Which tool to call — the model decides, training-guided
❌ Whether classification is conservative or not — schema design decides this

---

**Post 4**

Here's the real insight for agent builders:

If your classifier asks the model to output suggested_next_action, you've made the model a policy engine. A well-calibrated model is correctly cautious — it outputs "route_to_human" because that's always defensible.

The fix isn't switching to tool_use. It's removing the action field from the schema entirely.

```python
# Stalling: model decides action
{"intent": "POSITIVE", "suggested_next_action": "route_to_human"}

# Fixed: model classifies only, policy.py decides action  
{"intent": "POSITIVE", "confidence": "high"}
```

---

**Post 5**

Comparison script testing all 3 approaches against stalling probes:
A) JSON prompting with suggested_next_action (current)
B) JSON prompting without it
C) tool_use without it

If A stalls more than B → schema field is the cause, tool_use is optional.
If B and C are similar → tool_use adds reliability but not different behavior.

Code: sources/tool_use_comparison.py in the repo.

---

**Post 6**

Full explainer with code walkthrough, XML injection format, and when to use outlines for true logit masking on self-hosted models:

https://open.substack.com/pub/kemeriyamajor/p/tool_use-is-not-logit-masking-and?r=2xdj7z&utm_campaign=post&utm_medium=web&showWelcomeOnShare=true

Sources: Anthropic tool use docs + Willard & Louf (2023) Efficient Guided Generation.
