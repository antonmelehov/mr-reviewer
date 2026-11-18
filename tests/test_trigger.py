from src.trigger import fetch_pr_diff


class FakeFile:
    def __init__(self, filename, patch):
        self.filename = filename
        self.patch = patch


class FakePullRequest:
    def __init__(self, files):
        self._files = files

    def get_files(self):
        return self._files


class FakeRepo:
    def __init__(self, pr):
        self._pr = pr
        self.requested_pr_number = None

    def get_pull(self, number):
        self.requested_pr_number = number
        return self._pr


class FakeGithub:
    def __init__(self, repo):
        self._repo = repo
        self.requested_repo_name = None

    def get_repo(self, full_name):
        self.requested_repo_name = full_name
        return self._repo


def test_fetch_pr_diff_returns_touched_files_and_combined_diff():
    files = [
        FakeFile("src/example.py", "@@ -1,2 +1,2 @@\n-return a / b\n+return a / b  # fixed"),
        FakeFile("src/other.py", "@@ -1 +1 @@\n-old\n+new"),
    ]
    github = FakeGithub(FakeRepo(FakePullRequest(files)))

    result = fetch_pr_diff(github, "owner/repo", 42)

    assert result.touched_files == ["src/example.py", "src/other.py"]
    assert "--- a/src/example.py" in result.diff_text
    assert "+++ b/src/example.py" in result.diff_text
    assert "--- a/src/other.py" in result.diff_text


def test_fetch_pr_diff_skips_diff_text_for_files_without_a_patch():
    files = [FakeFile("assets/logo.png", None)]
    github = FakeGithub(FakeRepo(FakePullRequest(files)))

    result = fetch_pr_diff(github, "owner/repo", 7)

    assert result.touched_files == ["assets/logo.png"]
    assert result.diff_text == ""


def test_fetch_pr_diff_requests_the_right_repo_and_pr():
    repo = FakeRepo(FakePullRequest([]))
    github = FakeGithub(repo)

    fetch_pr_diff(github, "owner/repo", 99)

    assert github.requested_repo_name == "owner/repo"
    assert repo.requested_pr_number == 99
