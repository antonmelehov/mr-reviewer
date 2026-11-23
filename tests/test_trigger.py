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


def test_fetch_pr_diff_returns_touched_files_and_combined_diff():
    files = [
        FakeFile("src/example.py", "@@ -1,2 +1,2 @@\n-return a / b\n+return a / b  # fixed"),
        FakeFile("src/other.py", "@@ -1 +1 @@\n-old\n+new"),
    ]
    pr = FakePullRequest(files)

    result = fetch_pr_diff(pr)

    assert result.touched_files == ["src/example.py", "src/other.py"]
    assert "--- a/src/example.py" in result.diff_text
    assert "+++ b/src/example.py" in result.diff_text
    assert "--- a/src/other.py" in result.diff_text


def test_fetch_pr_diff_skips_diff_text_for_files_without_a_patch():
    files = [FakeFile("assets/logo.png", None)]
    pr = FakePullRequest(files)

    result = fetch_pr_diff(pr)

    assert result.touched_files == ["assets/logo.png"]
    assert result.diff_text == ""
