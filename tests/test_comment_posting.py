from github import GithubException

from src.comment_posting import post_failure, post_success
from src.diff_review import Finding


class FakeUser:
    def __init__(self, login):
        self.login = login


class FakeIssueComment:
    def __init__(self, body, user_login="github-actions[bot]"):
        self.body = body
        self.user = FakeUser(user_login)
        self.edited_with = None
        self.deleted = False

    def edit(self, body):
        self.body = body
        self.edited_with = body

    def delete(self):
        self.deleted = True


class FakeReviewComment:
    def __init__(self, path, line, body, user_login="github-actions[bot]"):
        self.path = path
        self.line = line
        self.body = body
        self.user = FakeUser(user_login)
        self.deleted = False

    def delete(self):
        self.deleted = True


class FakeHead:
    def __init__(self, sha):
        self.sha = sha


class FakePullRequest:
    def __init__(self, issue_comments=None, review_comments=None, head_sha="headsha"):
        self._issue_comments = list(issue_comments or [])
        self._review_comments = list(review_comments or [])
        self.head = FakeHead(head_sha)
        self.created_issue_comments = []
        self.created_review_comments = []

    def get_issue_comments(self):
        return list(self._issue_comments)

    def create_issue_comment(self, body):
        comment = FakeIssueComment(body)
        self._issue_comments.append(comment)
        self.created_issue_comments.append(comment)
        return comment

    def get_review_comments(self):
        return list(self._review_comments)

    def create_review_comment(self, body, commit, path, line=None):
        if path in getattr(self, "failing_paths", ()):
            raise GithubException(422, message=f"line {line} is not part of the diff")
        comment = FakeReviewComment(path, line, body)
        self._review_comments.append(comment)
        self.created_review_comments.append(comment)
        return comment


def test_first_run_creates_summary_and_inline_for_high_severity_only():
    pr = FakePullRequest()
    findings = [
        Finding(category="bug", file="a.py", line=2, severity="high", message="zero div"),
        Finding(category="style", file="a.py", line=5, severity="low", message="naming"),
    ]

    post_success(pr, findings)

    assert len(pr.created_issue_comments) == 1
    assert "<!-- mr-reviewer:summary -->" in pr.created_issue_comments[0].body

    assert len(pr.created_review_comments) == 1
    assert pr.created_review_comments[0].path == "a.py"
    assert pr.created_review_comments[0].line == 2


def test_high_severity_finding_without_line_gets_no_inline_comment():
    pr = FakePullRequest()
    findings = [Finding(category="missing_test", file="a.py", line=None, severity="high", message="no tests")]

    post_success(pr, findings)

    assert pr.created_review_comments == []


def test_repush_unchanged_findings_updates_summary_and_does_not_duplicate_inline():
    existing_summary = FakeIssueComment("old summary\n\n<!-- mr-reviewer:summary -->")
    existing_inline = FakeReviewComment("a.py", 2, "zero div\n\n<!-- mr-reviewer:inline:bug -->")
    pr = FakePullRequest(issue_comments=[existing_summary], review_comments=[existing_inline])

    findings = [Finding(category="bug", file="a.py", line=2, severity="high", message="zero div")]

    post_success(pr, findings)

    assert pr.created_issue_comments == []
    assert existing_summary.edited_with is not None

    assert pr.created_review_comments == []
    assert existing_inline.deleted is False


def test_fixed_finding_deletes_stale_inline_comment():
    stale_inline = FakeReviewComment("a.py", 2, "zero div\n\n<!-- mr-reviewer:inline:bug -->")
    pr = FakePullRequest(review_comments=[stale_inline])

    post_success(pr, [])

    assert stale_inline.deleted is True


def test_clean_diff_produces_no_issues_summary():
    pr = FakePullRequest()

    post_success(pr, [])

    assert len(pr.created_issue_comments) == 1
    assert "No issues found" in pr.created_issue_comments[0].body


def test_failure_produces_failure_summary_and_leaves_inline_untouched():
    existing_inline = FakeReviewComment("a.py", 2, "zero div\n\n<!-- mr-reviewer:inline:bug -->")
    pr = FakePullRequest(review_comments=[existing_inline])

    post_failure(pr, "Foundry agent call failed: timeout")

    assert len(pr.created_issue_comments) == 1
    assert "could not complete" in pr.created_issue_comments[0].body

    assert existing_inline.deleted is False
    assert pr.created_review_comments == []


def test_foreign_comment_without_marker_is_never_edited():
    foreign = FakeIssueComment("just a regular comment from a human")
    pr = FakePullRequest(issue_comments=[foreign])

    post_success(pr, [])

    assert foreign.edited_with is None
    assert len(pr.created_issue_comments) == 1


def test_foreign_comment_containing_the_marker_is_never_edited():
    foreign = FakeIssueComment(
        "look, I can type <!-- mr-reviewer:summary --> too", user_login="some-human"
    )
    pr = FakePullRequest(issue_comments=[foreign])

    post_success(pr, [])

    assert foreign.edited_with is None
    assert len(pr.created_issue_comments) == 1


def test_one_failing_inline_comment_does_not_block_the_rest():
    stale_inline = FakeReviewComment("c.py", 9, "old finding\n\n<!-- mr-reviewer:inline:style -->")
    pr = FakePullRequest(review_comments=[stale_inline])
    pr.failing_paths = {"a.py"}

    findings = [
        Finding(category="bug", file="a.py", line=2, severity="high", message="rejected by GitHub"),
        Finding(category="security", file="b.py", line=5, severity="high", message="created fine"),
    ]

    post_success(pr, findings)

    assert [c.path for c in pr.created_review_comments] == ["b.py"]
    assert stale_inline.deleted is True


def test_foreign_inline_comment_containing_the_marker_is_never_deleted():
    foreign_inline = FakeReviewComment(
        "a.py", 2, "nice try <!-- mr-reviewer:inline:bug -->", user_login="some-human"
    )
    pr = FakePullRequest(review_comments=[foreign_inline])

    post_success(pr, [])

    assert foreign_inline.deleted is False
