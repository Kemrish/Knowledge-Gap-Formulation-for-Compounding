"""
Tool_use vs JSON Prompting — Comparison Script
Demonstrates the difference between free-text JSON and Anthropic tool_use
at the API call level, and tests whether removing suggested_next_action
reduces conservative/stalling output.

Usage:
    pip install anthropic
    export ANTHROPIC_API_KEY=your_key
    python tool_use_comparison.py

No GPU required. Requires Anthropic API key.
"""

import json
import os
import anthropic

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
MODEL = "claude-haiku-4-5-20251001"  # cheapest model for demo

INTENT_VALUES = [
    "POSITIVE", "SCHEDULING", "OBJECTION_TIMING", "OBJECTION_OFFSHORE",
    "OBJECTION_FIT", "OBJECTION_BUDGET", "UNSUBSCRIBE", "UNCLEAR"
]

# ── Test probes: cases where dual-control stalling would manifest ──
# These are POSITIVE or SCHEDULING intents that should be handled autonomously.
# A stalling model outputs "route_to_human" in suggested_next_action.
STALLING_PROBES = [
    "Yes, I'd love to set up a call. When are you available?",
    "Sounds interesting, let's schedule 30 minutes this week.",
    "We are definitely open to exploring this. Please send a calendar invite.",
    "Great timing actually — we have a hiring push happening right now.",
]


def approach_a_json_with_action(reply_text: str) -> dict:
    """Current Week 10 approach: JSON prompting with suggested_next_action."""
    system = """You are a reply classifier for a B2B sales agent.
Return ONLY valid JSON with these exact fields:
{
  "intent": "<one of: POSITIVE|SCHEDULING|OBJECTION_TIMING|OBJECTION_OFFSHORE|OBJECTION_FIT|OBJECTION_BUDGET|UNSUBSCRIBE|UNCLEAR>",
  "confidence": "<high|medium|low>",
  "suggested_next_action": "<book_call|send_followup|route_to_human|close_thread>"
}"""
    response = client.messages.create(
        model=MODEL,
        system=system,
        messages=[{"role": "user", "content": f"Classify this reply:\n{reply_text}"}],
        max_tokens=256,
    )
    text = response.content[0].text.strip()
    if text.startswith("```"):
        text = text.split("```")[1].lstrip("json").strip()
    return json.loads(text)


def approach_b_json_no_action(reply_text: str) -> dict:
    """JSON prompting WITHOUT suggested_next_action — model classifies only."""
    system = """You are a reply classifier for a B2B sales agent.
Return ONLY valid JSON with these exact fields:
{
  "intent": "<one of: POSITIVE|SCHEDULING|OBJECTION_TIMING|OBJECTION_OFFSHORE|OBJECTION_FIT|OBJECTION_BUDGET|UNSUBSCRIBE|UNCLEAR>",
  "confidence": "<high|medium|low>"
}
Do NOT suggest any action. Classification only."""
    response = client.messages.create(
        model=MODEL,
        system=system,
        messages=[{"role": "user", "content": f"Classify this reply:\n{reply_text}"}],
        max_tokens=128,
    )
    text = response.content[0].text.strip()
    if text.startswith("```"):
        text = text.split("```")[1].lstrip("json").strip()
    return json.loads(text)


def approach_c_tool_use(reply_text: str) -> dict:
    """tool_use with intent-only schema — model constrained by API."""
    tools = [{
        "name": "classify_reply",
        "description": (
            "Classify the intent of a prospect reply. "
            "Do NOT decide what action to take — classification only."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "intent": {
                    "type": "string",
                    "enum": INTENT_VALUES,
                    "description": "The intent category of the reply."
                },
                "confidence": {
                    "type": "string",
                    "enum": ["high", "medium", "low"],
                    "description": "Confidence in the classification."
                }
            },
            "required": ["intent", "confidence"]
        }
    }]
    response = client.messages.create(
        model=MODEL,
        tools=tools,
        tool_choice={"type": "any"},   # forces tool use, no plain-text fallback
        messages=[{"role": "user", "content": f"Classify this reply:\n{reply_text}"}],
        max_tokens=128,
    )
    # Response is always a tool_use block — no JSON parsing needed
    return response.content[0].input


def main():
    print("=" * 65)
    print("Tool_use vs JSON Prompting — Stalling Probe Comparison")
    print("=" * 65)
    print(f"\nModel: {MODEL}")
    print(f"Probes: {len(STALLING_PROBES)} positive/scheduling replies")
    print("Expected intent: POSITIVE or SCHEDULING (autonomous action)\n")

    stall_counts = {"A_json_with_action": 0, "B_json_no_action": 0, "C_tool_use": 0}
    parse_failures = {"A_json_with_action": 0, "B_json_no_action": 0}

    for i, probe in enumerate(STALLING_PROBES, 1):
        print(f"Probe {i}: \"{probe[:60]}...\"" if len(probe) > 60 else f"Probe {i}: \"{probe}\"")

        # Approach A
        try:
            a = approach_a_json_with_action(probe)
            a_stall = a.get("suggested_next_action") == "route_to_human"
            if a_stall:
                stall_counts["A_json_with_action"] += 1
            print(f"  A (JSON+action):  intent={a['intent']:<20} "
                  f"action={a.get('suggested_next_action','—'):<20} "
                  f"{'⚠ STALL' if a_stall else '✓'}")
        except (json.JSONDecodeError, KeyError) as e:
            parse_failures["A_json_with_action"] += 1
            print(f"  A (JSON+action):  PARSE FAILURE — {e}")

        # Approach B
        try:
            b = approach_b_json_no_action(probe)
            print(f"  B (JSON only):    intent={b['intent']:<20} conf={b['confidence']}")
        except (json.JSONDecodeError, KeyError) as e:
            parse_failures["B_json_no_action"] += 1
            print(f"  B (JSON only):    PARSE FAILURE — {e}")

        # Approach C
        c = approach_c_tool_use(probe)
        print(f"  C (tool_use):     intent={c['intent']:<20} conf={c['confidence']}")
        print()

    print("=" * 65)
    print("Summary")
    print("=" * 65)
    print(f"Stalls (suggested route_to_human on positive probe):")
    print(f"  A JSON+action:  {stall_counts['A_json_with_action']}/{len(STALLING_PROBES)}")
    print(f"Parse failures:")
    print(f"  A JSON+action:  {parse_failures['A_json_with_action']}/{len(STALLING_PROBES)}")
    print(f"  B JSON only:    {parse_failures['B_json_no_action']}/{len(STALLING_PROBES)}")
    print(f"  C tool_use:     0/{len(STALLING_PROBES)} (API handles validation)")
    print()
    print("Key insight: if A stalls more than B, the schema field is the cause.")
    print("If B and C have similar intent accuracy, tool_use adds reliability")
    print("(no parse failures, enum enforcement) but not different intent classification.")


if __name__ == "__main__":
    main()
