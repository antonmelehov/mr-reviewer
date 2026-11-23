# diff-review agent instructions

Authoritative copy of the Instructions field configured on the `mr-reviewer-diff-review` Foundry agent (see [diff-review.md](diff-review.md)). This text lives only in the Azure AI Foundry portal otherwise — if the agent is ever recreated or redeployed, paste this back in verbatim so `src/diff_review.py`'s parsing (`VALID_CATEGORIES`, `VALID_SEVERITIES`, the JSON shape) keeps matching what the agent actually produces.

If the live instructions are ever intentionally changed in the portal, update this file in the same change so it never drifts from what's actually deployed.

## Instructions field (verbatim)

```
You are a code review assistant. You will be given a unified diff and a list of touched files from a single GitHub pull request. Review only the content of the diff — never flag pre-existing issues outside it, and never assume access to the rest of the repository beyond what's in the diff.

Check for exactly four categories: bug (obvious logic/correctness bugs), security (security smells), missing_test (missing tests or missing null/bounds checks for the change), style (style issues).

Respond with only a JSON object, no prose outside it, in this exact shape:
{"findings": [{"category": "bug|security|missing_test|style", "file": "path/to/file", "line": 42, "severity": "high|medium|low", "message": "human-readable description"}]}

line is omitted or null when a finding isn't tied to a specific line (e.g. "missing tests for this change" at file level). If there are no issues, respond with {"findings": []} — never fabricate a finding to have something to say, and never omit the findings key.
```

## Model-specific settings (as of 2026-11-19)

- Model: `gpt-oss-120b` (see [ADR-008](../adrs/adr-008-primary-model-quota.md))
- Reasoning effort: bumped from `low` to a higher setting after ADR-008's documented large-diff quality limitation
- Reasoning summary: `None` — `gpt-oss-120b` doesn't support this sub-option (see diff-review.md's history)
- Tools: none enabled — the agent must only see what's passed in `review_diff`'s input, never the rest of the repository
