# Tool_use Is Not Logit Masking — And That Changes How You Build Safe Agent Loops

*Explainer for: "Does tool_use work by logit masking (invalid tokens set to zero probability), or is it just a well-crafted prompt? And would using tool_use with a tighter schema have prevented dual-control stalling in my Week 10 reply classifier?"*

---

The question assumes two options: either tool_use is a hard constraint (logit masking) or it's a soft prompt. The actual answer is a third thing — and understanding it explains exactly why the dual-control stalling happened and what actually fixes it.

## What tool_use Is at the Token Level

When you pass `tools=[...]` to the Anthropic Messages API, three things happen internally:

**1. Tool definitions are serialized into the context.** Claude uses XML-formatted blocks internally. The tools array is converted to something like:

```xml
<tools>
  <tool_description>
    <tool_name>classify_reply</tool_name>
    <description>Classify the intent of a prospect reply</description>
    <parameters>
      <parameter><name>intent</name><type>string</type>...</parameter>
    </parameters>
  </tool_description>
</tools>
```

This block is prepended to the system prompt. The model sees it as plain context — tokens like any other.

**2. The model outputs a `tool_use` content block.** This is *trained behavior*, not a hard constraint. Claude has been trained on millions of examples where tool definitions in context are followed by structured tool-call outputs. When the model sees the XML blocks, it has learned to respond with a `tool_use` block rather than plain text.

**3. The API validates the JSON arguments.** The `input` field of a `tool_use` block is validated against the JSON schema you provided. If the model generates invalid JSON (which is rare because of training), the API either rejects it or uses constrained decoding to repair it.

**What this means**: tool_use is NOT logit masking at the decision level. The model can still output plain text instead of a tool call — it chooses not to because of training. Only `tool_choice: "any"` forces tool use, and that works by the API rejecting responses that don't include a tool call, not by masking tokens during generation.

True logit masking — setting invalid token probabilities to exactly zero at each decode step — is what libraries like `outlines` and `lm-format-enforcer` do for open-source models. Anthropic's tool_use is softer than that at the tool-selection level, harder than plain JSON prompting in practice.

## What the Difference Looks Like in Code

```python
# ── Approach A: JSON prompting (current Week 10 reply_handler.py) ──
response = client.messages.create(
    model="claude-sonnet-4-6",
    system="""Return JSON with these fields:
    intent: one of POSITIVE|SCHEDULING|OBJECTION_TIMING|...
    confidence: high|medium|low
    suggested_next_action: book_call|send_followup|route_to_human
    """,
    messages=[{"role": "user", "content": reply_text}],
    max_tokens=512
)
result = json.loads(response.content[0].text)  # can fail; model decides action

# ── Approach B: tool_use with intent-only schema ──
tools = [{
    "name": "classify_reply",
    "description": "Classify the intent of a prospect reply. Do not decide what action to take.",
    "input_schema": {
        "type": "object",
        "properties": {
            "intent": {
                "type": "string",
                "enum": ["POSITIVE","SCHEDULING","OBJECTION_TIMING",
                         "OBJECTION_OFFSHORE","OBJECTION_FIT",
                         "OBJECTION_BUDGET","UNSUBSCRIBE","UNCLEAR"]
            },
            "confidence": {"type": "string", "enum": ["high","medium","low"]}
        },
        "required": ["intent", "confidence"]
    }
}]
response = client.messages.create(
    model="claude-sonnet-4-6",
    tools=tools,
    tool_choice={"type": "any"},   # forces tool use
    messages=[{"role": "user", "content": reply_text}],
)
tool_input = response.content[0].input  # dict, always valid, no action field
# policy.py decides the action — model was never asked
```

The practical differences: parsing failures are rarer with tool_use because the API handles JSON validation. The `enum` in the schema makes hallucinated intent categories harder. `tool_choice: "any"` eliminates plain-text fallback.

But notice what didn't change: if you kept `suggested_next_action` in Approach B's schema, stalling would still happen.

## The Real Cause of Dual-Control Stalling

The stalling was not caused by using JSON prompting instead of tool_use. It was caused by asking the model to make a policy decision inside the classification step.

`SYSTEM_PROMPT_QUALIFIER` in `reply_handler.py` asks Claude to output `suggested_next_action`. That field puts Claude in the role of a policy engine. A well-calibrated model is correctly cautious about autonomous actions — it doesn't know what's safe. So it outputs `route_to_human` because that's always defensible. This is rational model behavior, not a bug.

The deterministic `policy.py` fixed the stalling by removing the model from the policy decision entirely — but it left `suggested_next_action` in the JSON schema. The model still generates the field; `policy.py` ignores it. That field is dead weight that costs tokens and may still prime conservative classification.

The correct fix, now that you understand the mechanism: **remove `suggested_next_action` from the schema regardless of whether you use JSON or tool_use.** The model's job is classification. `policy.py`'s job is action selection. Merging them in the schema is what caused the problem.

## How to Test Whether Schema Design Is the Culprit

Run the same τ²-Bench stalling tasks with three conditions:

```python
# Condition 1: current (JSON with suggested_next_action)
# Condition 2: JSON without suggested_next_action
# Condition 3: tool_use without suggested_next_action

# Compare stall rate (intent=UNCLEAR or confidence=low on tasks
# where the right answer is autonomous action)
```

If Condition 2 stalls less than Condition 1, the field is the problem — tool_use is optional. If Condition 2 and Condition 3 are similar, tool_use adds reliability (less JSON parse failures) but doesn't change the fundamental behavior. The demo script in `sources/tool_use_comparison.py` runs this comparison against a small probe set.

## Adjacent Concepts Worth Connecting

**Constrained decoding for open-source models**: If you're running a self-hosted model (like the Qwen3.5-0.8B adapter from Week 11), Anthropic's trained tool_use isn't available. Libraries like `outlines` (Willard & Louf, 2023) implement true logit masking against a JSON schema FSM — this IS the hard constraint that tool_use approximates through training. At 0.8B scale, this is more reliable than hoping the model learned good tool-use patterns.

**`tool_choice` modes**: `"auto"` lets the model decide whether to call a tool. `"any"` forces a tool call. `{"type": "tool", "name": "X"}` forces a specific tool. For a classifier that must always return an intent, `"any"` is the right choice — it removes the model's ability to respond with plain text.

## Pointers

**Anthropic tool use documentation**: https://docs.anthropic.com/en/docs/build-with-claude/tool-use — the primary source for API format, `tool_choice` modes, and JSON schema support. The `input_schema` spec and `tool_choice` options are documented here.

**Willard, B. & Louf, R. (2023). *Efficient Guided Generation for Large Language Models*.** https://arxiv.org/abs/2307.09702 — the paper behind the `outlines` library. Describes how FSM-based logit masking works and why it guarantees schema conformance. Useful for understanding what Anthropic's tool_use is approximating through training — and what you'd need for a self-hosted model like the Week 11 adapter.

---

*The gap this closes: tool_use is trained behavior + format injection, not logit masking. The stalling came from schema design — asking the model to be a policy engine. The fix is removing `suggested_next_action` from the schema, which works in either JSON or tool_use mode. tool_use adds reliability through consistent format and API validation, but it does not prevent a model from being conservative when asked to make policy decisions.*
