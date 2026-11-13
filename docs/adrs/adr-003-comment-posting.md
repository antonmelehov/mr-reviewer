# ADR-003: Comment posting and deduplication

## Status
Accepted

## Context
The agent must post review feedback on the MR without re-posting or spamming on every push to the same branch.

## Options considered
- **Single summary comment** — one comment per MR, located by a hidden marker and PATCHed (not recreated) on every push. Simplest possible dedup, but no line-anchored feedback — reads as a report, not a code review.
- **Inline per-line comments only** — uses GitHub's Review API to anchor comments to exact diff lines, feels like a real reviewer. Dedup is harder: needs to track which lines/commits were already reviewed so re-pushing the same unchanged lines doesn't re-comment.
- **Hybrid: summary + inline (chosen)** — one summary comment (overview, severity counts) plus inline comments for high-confidence findings only. Both are replaced on each push via a marker. Best UX of the three, more to build than either option alone.

## Decision
Use the **hybrid** approach: a single, update-in-place summary comment plus inline comments for high-confidence findings.

## Consequences
- The summary comment carries a hidden marker (e.g. an HTML comment with the MR's latest reviewed commit SHA) so the bot can find and PATCH it instead of creating a new one each push.
- Inline comments are posted as a GitHub PR review; previously-posted bot reviews/comments need to be tracked (by ID) so re-pushing doesn't duplicate comments on unchanged lines.
- This is more initial build effort than either option alone — the exact dedup mechanics (which GitHub Review API calls, what counts as "unchanged") are pinned down in [docs/specs/comment-posting.md](../specs/comment-posting.md), not here.
