# Spec: comment-posting

Capability: take the findings (or no-findings, or failure) result from [diff-review](diff-review.md) and post/update comments on the PR, without spamming duplicates on re-push.

Context: [architecture.md](../../architecture.md) step 4, [ADR-003](../adrs/adr-003-comment-posting.md) (hybrid summary + inline, dedup via marker).

## Requirements
1. One summary comment is posted per PR, carrying an overview and severity/category counts, plus inline comments for high-confidence findings only (per [ADR-003](../adrs/adr-003-comment-posting.md)'s hybrid approach).
2. The summary comment is located via a hidden marker and updated in place (not recreated) on every subsequent push to the same PR.
3. Inline comments from a prior run are tracked so that re-pushing with the same findings doesn't duplicate comments on lines already flagged, and findings that no longer apply (the issue was fixed) have their inline comment removed or resolved rather than left stale.
4. A "no findings" result from diff-review produces an explicit "no issues found" summary comment — not silence. The developer should always get confirmation the bot ran.
5. A failure result from diff-review (it couldn't complete the review) produces a summary comment stating the review failed to complete — not silence.
6. Comments are posted using the GitHub Actions-provided `GITHUB_TOKEN`, not a personal access token ([AGENTS.md](../../AGENTS.md) secrets rule).
7. All of the bot's comments/reviews use a consistent identity and marker so this capability can reliably find its own prior comment, never mistaking another user's comment for its own.

## Scenarios

**First review on a PR**
- Given a PR has findings from diff-review for the first time
- When comment-posting runs
- Then it creates a new summary comment (with marker) plus inline comments for the high-confidence findings

**Re-push with unchanged findings**
- Given a summary comment and inline comments already exist from an earlier run on this PR
- When comment-posting runs again with the same findings
- Then the summary comment is updated in place and no duplicate inline comments are created

**Fixed finding on re-push**
- Given an inline comment was posted for a finding on a specific line
- When a later push fixes that issue and diff-review no longer reports it
- Then comment-posting removes or resolves that inline comment rather than leaving it stale

**Clean diff**
- Given diff-review returns "no findings"
- When comment-posting runs
- Then it creates or updates the summary comment to explicitly state no issues were found

**diff-review failure**
- Given diff-review reports a failure for this run
- When comment-posting runs
- Then it creates or updates the summary comment to state the review could not complete

## Definition of Done
- [x] First run on a PR creates a summary comment (with marker) and inline comments for high-confidence findings
- [x] A re-push with unchanged findings updates the existing summary comment in place, with no duplicate inline comments — observed directly: same comment IDs across repeated pushes
- [x] A fixed finding has its inline comment removed/resolved on the next run, not left stale — observed directly: inline comment deleted once its finding disappeared
- [x] A "no findings" result produces an explicit "no issues found" comment, not silence
- [x] A diff-review failure produces a comment stating review could not complete, not silence
- [x] All comments are posted using the Actions-provided `GITHUB_TOKEN`, no personal token
- [x] The bot's own prior comment/review is reliably located via its marker/identity, never confused with another user's comment — observed directly (a real human comment was never touched across 4 live runs) and defended with regression tests for a marker-containing foreign comment
