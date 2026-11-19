import logging

from src.comment_posting import post_review
from src.diff_review import DiffReviewError, review_diff

logger = logging.getLogger(__name__)


def run_review(pr, openai_client, touched_files: list[str], diff_text: str) -> None:
    try:
        findings = review_diff(openai_client, touched_files, diff_text)
    except DiffReviewError as exc:
        logger.error("diff review failed: %s", exc)
        post_review(pr, error_message=str(exc))
        return

    post_review(pr, findings=findings)
