# Day 2 Question — Kemeriya

## Topic: Agent and Tool-Use Internals

---

## Final Sharpened Question

In `agent/email/reply_handler.py` in my Week 10 Conversion Engine, I prompt Claude Sonnet 4.6 to return a JSON object that includes a `suggested_next_action` field — values like `"book_call"` or `"route_to_human"`. But `policy.py` completely ignores this field. The deterministic policy engine overrides whatever the model suggests and applies its own rules.

I built this as **free-text JSON generation** — the model is instructed via a system prompt to output valid JSON, which I then parse. I never used Anthropic's actual `tool_use` API, where function definitions are injected into the model's context and the output is constrained to valid function invocations.

**My gap**: I cannot explain what is happening at the token level in each approach — specifically: when a model uses the `tool_use` API, is it generating JSON constrained by a schema that was injected as part of the prompt context? And would using `tool_use` with a schema that only defines `intent` (no `suggested_next_action`) have prevented the dual-control stalling failure mode — where in τ²-Bench, the model hallucinated asking for human permission on actions the policy already allowed? My hypothesis is that asking the model to generate `suggested_next_action` in the JSON schema primed it toward conservative escalation answers, but I cannot defend this at the mechanism level.

---

## Connection to Existing Artifact

**Week 10 — two files in direct tension:**

- `agent/email/reply_handler.py` lines 14–40 (`SYSTEM_PROMPT_QUALIFIER`): defines the JSON schema the model is asked to return, including the `suggested_next_action` field
- `agent/policy.py` `_AUTONOMOUS_ACTIONS` dict: the deterministic engine that ignores `suggested_next_action` entirely and maps intent → action via its own rules

The `suggested_next_action` field the model generates is defined in the prompt schema but never consumed by the policy engine. This is the specific design choice I cannot defend: I asked the model to suggest an action, it generated a conservative answer (often `route_to_human`), and that conservatism is what I believe drove the dual-control stalling — but I do not know whether this is a function of the JSON-prompting approach or whether switching to constrained `tool_use` would have changed the model's behavior.

**τ²-Bench result this connects to**: dual-control stalling was 40% of Week 10 failures. The fix (deterministic policy layer) addressed the symptom but not the mechanism.

---

## Why This Is Generalizable

Every FDE building an agentic system faces this design choice: JSON-prompting vs tool_use API for structured output. The answer has direct implications for reliability, failure mode prediction, and how much the model's training on tool-use patterns affects output quality. Anyone building a classifier or router on top of an LLM needs to know what the model is actually doing at the token level in each mode.

---

## What a Satisfying Answer Looks Like

A 600–900 word explainer that:
1. Names what the model is doing at the token level in JSON-prompting vs `tool_use` — are these mechanically different or just syntactically different?
2. Explains whether the presence of `suggested_next_action` in the JSON schema would prime the model toward escalation answers
3. Tells me whether constrained function calling would reduce dual-control stalling or is orthogonal to it
4. Points to where in the Anthropic docs or a canonical paper the token-level mechanism is described
