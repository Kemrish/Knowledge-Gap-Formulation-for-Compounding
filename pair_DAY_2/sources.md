# Sources — Day 2 Explainer

## Canonical Papers / Primary Sources

### 1. Anthropic Tool Use Documentation
**URL**: https://docs.anthropic.com/en/docs/build-with-claude/tool-use
**Why canonical**: Primary source for how the tool_use API works — `tools` parameter format, `tool_choice` modes ("auto", "any", specific tool), JSON schema support for `input_schema`, and how `tool_use` content blocks are structured in responses. The format for tool definitions (JSON Schema) and the behavior of `tool_choice: "any"` are documented here.
**What I used**: API reference for `tools` parameter structure, `tool_choice` options, and `input_schema` JSON Schema support. The enum constraint behavior and required fields documentation.

---

### 2. Willard, B. & Louf, R. (2023). *Efficient Guided Generation for Large Language Models*
**URL**: https://arxiv.org/abs/2307.09702
**Why canonical**: The paper behind the `outlines` library — describes FSM-based logit masking for constrained generation. This is the mechanism that Anthropic's tool_use approximates through training rather than implementing as hard constraints. Essential for understanding the distinction between "trained to conform" (tool_use) and "mathematically guaranteed to conform" (outlines-style logit masking). Directly relevant for Week 11's Qwen3.5-0.8B adapter, which would need this library for reliable structured output.
**What I used**: Section 3 (FSM-based guided generation), the distinction between regex/CFG/JSON Schema constraints and how they map to token-level masking. The proof that FSM-constrained generation is lossless (no quality degradation vs unconstrained).

---

## Tool / Demonstration

### `sources/tool_use_comparison.py` (this repo)
A runnable script (requires Anthropic API key, uses claude-haiku for low cost) that:
- Runs 4 stalling probes against all three approaches: JSON+action, JSON-only, tool_use
- Measures whether `suggested_next_action` in the schema causes conservative output on POSITIVE/SCHEDULING replies
- Counts parse failures per approach (tool_use always zero; JSON may fail)
- Produces a summary table showing the stalling rate difference

This directly tests the hypothesis that schema design — not API choice — causes dual-control stalling.

---

## Follow-On Directions

- **`outlines` library** (https://github.com/outlines-dev/outlines): Implements FSM-based constrained generation for open-source models. Relevant for the Week 11 Qwen3.5-0.8B adapter if reliable structured output is needed without Anthropic's trained tool_use.
- **Anthropic structured output guide** (https://docs.anthropic.com/en/docs/test-and-evaluate/strengthen-guardrails/increase-consistency): Documents the relationship between JSON mode, tool_use, and reliability for structured classification tasks.
