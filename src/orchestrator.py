import logging

from src.comment_posting import post_failure, post_success
from src.diff_review import DiffReviewError, OpenAIClientLike, review_diff
from src.github_types import PullRequestLike

logger = logging.getLogger(__name__)


def run_review(
    pr: PullRequestLike, openai_client: OpenAIClientLike, touched_files: list[str], diff_text: str
) -> None:
    try:
        findings = review_diff(openai_client, touched_files, diff_text)
    except DiffReviewError as exc:
        logger.error("diff review failed: %s", exc)
        post_failure(pr, str(exc))
        return

    post_success(pr, findings)
