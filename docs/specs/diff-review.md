# Spec: diff-review

Capability: given a diff and touched-files list (from [mr-trigger](mr-trigger.md)), produce structured review findings by calling the Foundry agent. Does not cover how findings get posted on the PR (see [comment-posting](comment-posting.md)).

Context: [architecture.md](../../architecture.md) step 3, [ADR-004](../adrs/adr-004-agent-hosting.md) (agent hosting), [ADR-005](../adrs/adr-005-claude-access-path.md) (model access/fallback).

## Requirements
1. The diff is reviewed against four categories: obvious bugs, security smells, missing tests/null-checks, style.
2. Review is scoped strictly to the diff and touched files — no broader repo context, and no flagging of pre-existing issues outside the diff.
3. Review is performed by calling the Azure AI Foundry agent configured with a catalog model ([ADR-004](../adrs/adr-004-agent-hosting.md); currently `gpt-oss-120b`, not Claude, due to subscription quota constraints — see [ADR-008](../adrs/adr-008-primary-model-quota.md)). No direct Anthropic API call happens here — that's the manual fallback runbook in [ADR-005](../adrs/adr-005-claude-access-path.md), not automatic code in this capability. The agent's instructions are checked into this repo as the authoritative copy — see [diff-review-agent-instructions.md](diff-review-agent-instructions.md) — since they otherwise only live in the Foundry portal and must stay in lockstep with `src/diff_review.py`'s parsing.
4. Each finding includes: category, location (file, and line where applicable — not every finding is line-anchored, e.g. "missing tests for this change" may be file-level), a severity level, and a human-readable message. "Confidence" and "severity" are not two separate fields — the implementation has a single `severity` field (`high`/`medium`/`low`) that doubles as the confidence signal comment-posting uses to decide what goes inline vs. summary-only ([comment-posting.md](comment-posting.md) treats `severity == "high"` as "high-confidence").
5. If the Foundry agent call fails or times out, the step reports a failure for that run — it never returns partial or fabricated findings as if they were a complete review.
6. Every run is logged: what diff was reviewed and what findings (or failure) came back.
7. No auto-fix or auto-merge action is taken, regardless of findings.

## Scenarios

**Clean diff**
- Given a diff and touched-files list with no issues in the four review categories
- When diff-review runs
- Then it returns an explicit "no findings" result, not an error

**Diff with findings across categories**
- Given a diff containing, for example, a missing-null-check bug and a style issue
- When diff-review runs
- Then it returns a finding for each, each tagged with category, location, a severity level, and a message

**Foundry agent failure**
- Given the Foundry agent call fails or times out
- When diff-review runs
- Then the step reports a failure for that run, rather than returning partial or fabricated findings

**Review stays scoped to the diff**
- Given a diff touching file A, while file B elsewhere in the repo has an unrelated pre-existing issue
- When diff-review runs
- Then findings are limited to file A / the diff; the pre-existing issue in file B is not flagged

## Definition of Done
- [x] A sample diff with no issues returns an explicit no-findings result without erroring
- [x] A sample diff with known issues in each of the four categories returns a finding for each, with category, location, severity, and message — observed in the full e2e validation run (PR #5): bug, missing_test, security, and style all returned in one run
- [x] A simulated Foundry agent failure/timeout causes the step to report failure, not partial/fabricated findings
- [x] A known pre-existing issue outside the diff is not flagged — guaranteed structurally (the agent only ever receives touched files + diff text, no repo access) and defended in code (out-of-scope findings are dropped, with a dedicated test)
- [x] Every run's input (diff reference) and output (findings or failure) is logged
- [x] No auto-fix or auto-merge action occurs regardless of findings
