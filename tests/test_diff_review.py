import json

import pytest

from src.diff_review import DiffReviewError, Finding, review_diff


class FakeResponse:
    def __init__(self, output_text):
        self.output_text = output_text


class FakeResponses:
    def __init__(self, output_text=None, error=None):
        self._output_text = output_text
        self._error = error
        self.last_input = None

    def create(self, input):
        self.last_input = input
        if self._error is not None:
            raise self._error
        return FakeResponse(self._output_text)


class FakeOpenAIClient:
    def __init__(self, output_text=None, error=None):
        self.responses = FakeResponses(output_text=output_text, error=error)


def test_review_diff_returns_findings_across_categories():
    payload = {
        "findings": [
            {"category": "bug", "file": "a.py", "line": 2, "severity": "high", "message": "boom"},
            {"category": "missing_test", "file": "a.py", "line": None, "severity": "medium", "message": "no tests"},
            {"category": "style", "file": "a.py", "line": 5, "severity": "low", "message": "naming"},
        ]
    }
    client = FakeOpenAIClient(output_text=json.dumps(payload))

    findings = review_diff(client, ["a.py"], "--- a/a.py\n+++ b/a.py\n@@ ...")

    assert findings == [
        Finding(category="bug", file="a.py", line=2, severity="high", message="boom"),
        Finding(category="missing_test", file="a.py", line=None, severity="medium", message="no tests"),
        Finding(category="style", file="a.py", line=5, severity="low", message="naming"),
    ]


def test_review_diff_clean_diff_returns_empty_list_not_error():
    client = FakeOpenAIClient(output_text=json.dumps({"findings": []}))

    findings = review_diff(client, ["a.py"], "clean diff")

    assert findings == []


def test_review_diff_sends_touched_files_and_diff_in_the_input():
    client = FakeOpenAIClient(output_text=json.dumps({"findings": []}))

    review_diff(client, ["a.py", "b.py"], "the diff text")

    assert '"a.py"' in client.responses.last_input
    assert '"b.py"' in client.responses.last_input
    assert "the diff text" in client.responses.last_input


def test_review_diff_raises_on_malformed_json():
    client = FakeOpenAIClient(output_text="not json")

    with pytest.raises(DiffReviewError):
        review_diff(client, ["a.py"], "diff")


def test_review_diff_raises_when_findings_key_missing():
    client = FakeOpenAIClient(output_text=json.dumps({"oops": []}))

    with pytest.raises(DiffReviewError):
        review_diff(client, ["a.py"], "diff")


def test_review_diff_raises_on_missing_required_field():
    payload = {"findings": [{"category": "bug", "file": "a.py", "severity": "high"}]}
    client = FakeOpenAIClient(output_text=json.dumps(payload))

    with pytest.raises(DiffReviewError):
        review_diff(client, ["a.py"], "diff")


def test_review_diff_raises_on_unrecognized_category():
    payload = {
        "findings": [
            {"category": "performance", "file": "a.py", "line": 1, "severity": "high", "message": "slow"}
        ]
    }
    client = FakeOpenAIClient(output_text=json.dumps(payload))

    with pytest.raises(DiffReviewError):
        review_diff(client, ["a.py"], "diff")


def test_review_diff_raises_when_agent_call_fails():
    client = FakeOpenAIClient(error=TimeoutError("agent timed out"))

    with pytest.raises(DiffReviewError):
        review_diff(client, ["a.py"], "diff")
