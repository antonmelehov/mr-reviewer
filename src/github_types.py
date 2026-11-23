from collections.abc import Iterable
from typing import Protocol


class UserLike(Protocol):
    login: str


class FileLike(Protocol):
    filename: str
    patch: str | None


class IssueCommentLike(Protocol):
    body: str
    user: UserLike

    def edit(self, body: str) -> None: ...
    def delete(self) -> None: ...


class ReviewCommentLike(Protocol):
    path: str
    line: int | None
    body: str
    user: UserLike

    def delete(self) -> None: ...


class HeadLike(Protocol):
    sha: str


class PullRequestLike(Protocol):
    number: int
    head: HeadLike

    def get_files(self) -> Iterable[FileLike]: ...
    def get_issue_comments(self) -> Iterable[IssueCommentLike]: ...
    def create_issue_comment(self, body: str) -> IssueCommentLike: ...
    def get_review_comments(self) -> Iterable[ReviewCommentLike]: ...
    def create_review_comment(
        self, body: str, commit: str, path: str, line: int | None = None
    ) -> ReviewCommentLike: ...
