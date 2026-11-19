import json

import src.orchestrator as orchestrator_module
from src.diff_review import Finding
from src.orchestrator import run_review


class FakeResponse:
    def __init__(self, output_text):
        self.output_text = output_text


class FakeResponses:
    def __init__(self, output_text=None, error=None):
        self._output_text = output_text
        self._error = error

    def create(self, input):
        if self._error is not None:
            raise self._error
        return FakeResponse(self._output_text)


class FakeOpenAIClient:
    def __init__(self, output_text=None, error=None):
        self.responses = FakeResponses(output_text=output_text, error=error)


def _patch_post_review(monkeypatch):
    posted = {}

    def fake_post_review(pr, findings=None, error_message=None):
        posted["findings"] = findings
        posted["error_message"] = error_message

    monkeypatch.setattr(orchestrator_module, "post_review", fake_post_review)
    return posted


def test_run_review_posts_findings_on_success(monkeypatch):
    posted = _patch_post_review(monkeypatch)
    payload = {"findings": [{"category": "bug", "file": "a.py", "line": 1, "severity": "high", "message": "x"}]}
    client = FakeOpenAIClient(output_text=json.dumps(payload))

    run_review(pr=object(), openai_client=client, touched_files=["a.py"], diff_text="diff")

    assert posted["error_message"] is None
    assert posted["findings"] == [Finding(category="bug", file="a.py", line=1, severity="high", message="x")]


def test_run_review_posts_error_message_on_diff_review_failure(monkeypatch):
    posted = _patch_post_review(monkeypatch)
    client = FakeOpenAIClient(output_text="not valid json")

    run_review(pr=object(), openai_client=client, touched_files=["a.py"], diff_text="diff")

    assert posted["findings"] is None
    assert posted["error_message"] is not None
