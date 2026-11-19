import logging
import re
from collections import Counter

from src.diff_review import Finding

logger = logging.getLogger(__name__)

SUMMARY_MARKER = "<!-- mr-reviewer:summary -->"
INLINE_MARKER_RE = re.compile(r"<!-- mr-reviewer:inline:(\w+) -->")
HIGH_CONFIDENCE_SEVERITY = "high"


def post_review(pr, findings: list[Finding] | None = None, error_message: str | None = None) -> None:
    if (findings is None) == (error_message is None):
        raise ValueError("exactly one of findings or error_message must be set")

    summary_body = _build_summary_body(findings, error_message)
    _upsert_summary_comment(pr, summary_body)

    if findings is not None:
        _reconcile_inline_comments(pr, findings)

    logger.info("comment-posting complete")


def _build_summary_body(findings: list[Finding] | None, error_message: str | None) -> str:
    if error_message is not None:
        return f"### mr-reviewer\n\nReview could not complete: {error_message}\n\n{SUMMARY_MARKER}"

    if not findings:
        return f"### mr-reviewer\n\nNo issues found.\n\n{SUMMARY_MARKER}"

    by_category = Counter(finding.category for finding in findings)
    by_severity = Counter(finding.severity for finding in findings)

    lines = ["### mr-reviewer", "", f"Found {len(findings)} issue(s).", "", "By category:"]
    lines += [f"- {category}: {count}" for category, count in sorted(by_category.items())]
    lines += ["", "By severity:"]
    lines += [f"- {severity}: {count}" for severity, count in sorted(by_severity.items())]
    lines += ["", SUMMARY_MARKER]
    return "\n".join(lines)


def _upsert_summary_comment(pr, body: str) -> None:
    for comment in pr.get_issue_comments():
        if SUMMARY_MARKER in comment.body:
            comment.edit(body)
            logger.info("updated existing summary comment")
            return
    pr.create_issue_comment(body)
    logger.info("created new summary comment")


def _reconcile_inline_comments(pr, findings: list[Finding]) -> None:
    high_confidence = [
        finding
        for finding in findings
        if finding.severity == HIGH_CONFIDENCE_SEVERITY and finding.line is not None
    ]

    existing_by_key = {}
    for comment in pr.get_review_comments():
        match = INLINE_MARKER_RE.search(comment.body)
        if match:
            existing_by_key[(comment.path, comment.line, match.group(1))] = comment

    desired_keys = set()
    for finding in high_confidence:
        key = (finding.file, finding.line, finding.category)
        desired_keys.add(key)
        if key not in existing_by_key:
            body = f"{finding.message}\n\n<!-- mr-reviewer:inline:{finding.category} -->"
            pr.create_review_comment(body, pr.head.sha, finding.file, line=finding.line)
            logger.info("created inline comment for %s:%s (%s)", finding.file, finding.line, finding.category)

    for key, comment in existing_by_key.items():
        if key not in desired_keys:
            comment.delete()
            logger.info("deleted stale inline comment for %s", key)
