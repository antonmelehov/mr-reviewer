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
- The summary comment carries a hidden marker — a fixed HTML comment (`<!-- mr-reviewer:summary -->`), not the MR's commit SHA as originally sketched here. A static marker is simpler to search for than a SHA-based one, which would change on every push and require matching "any old-SHA marker" instead of one exact string.
- Inline comments carry their own hidden marker encoding the finding's category (`<!-- mr-reviewer:inline:{category} -->`). Combined with GitHub's own `path`/`line` fields on each comment, this gives a `(path, line, category)` key the bot re-derives fresh on every run via `pr.get_review_comments()` — prior comments aren't tracked by persisted ID across runs, since nothing is persisted between runs at all.
- This is more initial build effort than either option alone — the exact dedup mechanics (which GitHub Review API calls, what counts as "unchanged") are pinned down in [docs/specs/comment-posting.md](../specs/comment-posting.md), not here.
