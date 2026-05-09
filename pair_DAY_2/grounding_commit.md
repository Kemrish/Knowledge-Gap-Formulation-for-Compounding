# Grounding Commit — Day 2

**Asker**: Kemeriya
**Artifact edited**: `Week-10/The Conversion Engine/agent/email/reply_handler.py` — `SYSTEM_PROMPT_QUALIFIER`

---

## What Changed

**File**: `agent/email/reply_handler.py`, lines 32–39 (`SYSTEM_PROMPT_QUALIFIER` return spec)

Removed the `suggested_next_action` field from the JSON schema the model is asked to return:

```diff
- - suggested_next_action: "book_call" | "send_followup" | "route_to_human" | "close_thread" | "sms_scheduling"
```

Added two lines at the end of the prompt explicitly telling the model its role is classification only:

```diff
+ Do NOT decide what action to take. Action routing is handled by the policy engine downstream.
+ Your job is classification only.
```

The fields `intent`, `confidence`, `extracted_signals`, `suggested_response`, `urgency`, and `notes_for_crm` are unchanged. `suggested_response` (a draft reply text) is kept because it is actually used — `policy.py` passes it to the email composer. `suggested_next_action` was the only field that was generated and then silently discarded.

## Why It Changed

Tsegay's explainer showed that tool_use is not logit masking — the model's choice of output is trained behavior, not a hard constraint. Asking the model to output `suggested_next_action` made it act as a policy engine, and a well-calibrated model defaults to `route_to_human` because that is always safe. The field was generating tokens that `policy.py` immediately threw away, but those tokens were likely nudging the model's internal probability distribution toward conservative intent classifications upstream of the action suggestion.

Removing the field eliminates the role confusion: the model classifies, the policy engine routes. The explicit instruction "Your job is classification only" reinforces this at the prompt level. This also reduces token output by roughly 5–8 tokens per call — small individually, meaningful across 1,000+ prospect replies in production.

## Blog and Thread URLs

- Blog post: https://open.substack.com/pub/kemeriyamajor/p/tool_use-is-not-logit-masking-and?r=2xdj7z&utm_campaign=post&utm_medium=web&showWelcomeOnShare=true
- Thread: https://www.linkedin.com/feed/update/urn:li:share:7458827952596811776/
