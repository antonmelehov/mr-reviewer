import json

import src.main as main_module
from src.trigger import TriggerResult


class FakeHead:
    sha = "abc123"


class FakePullRequest:
    number = 42
    head = FakeHead()


class FakeRepo:
    def __init__(self, pr):
        self._pr = pr
        self.get_pull_calls = []

    def get_pull(self, number):
        self.get_pull_calls.append(number)
        return self._pr


class FakeGithubClient:
    def __init__(self, repo):
        self._repo = repo

    def get_repo(self, full_name):
        return self._repo


class FakeProjectClient:
    def __init__(self, endpoint, credential, allow_preview):
        pass

    def get_openai_client(self, agent_name):
        return object()


def test_main_fetches_the_pr_exactly_once_and_passes_it_through(tmp_path, monkeypatch):
    event_path = tmp_path / "event.json"
    event_path.write_text(json.dumps({"pull_request": {"number": 42}}))

    monkeypatch.setenv("GITHUB_TOKEN", "tok")
    monkeypatch.setenv("GITHUB_REPOSITORY", "owner/repo")
    monkeypatch.setenv("FOUNDRY_PROJECT_ENDPOINT", "https://example")
    monkeypatch.setenv("FOUNDRY_AGENT_NAME", "agent")
    monkeypatch.setenv("GITHUB_EVENT_PATH", str(event_path))

    pr = FakePullRequest()
    repo = FakeRepo(pr)
    monkeypatch.setattr(main_module, "Github", lambda token: FakeGithubClient(repo))
    monkeypatch.setattr(main_module, "DefaultAzureCredential", lambda: object())
    monkeypatch.setattr(main_module, "AIProjectClient", FakeProjectClient)

    received = {}

    def fake_fetch_pr_diff(fetched_pr):
        received["fetch_pr_diff_pr"] = fetched_pr
        return TriggerResult(touched_files=["a.py"], diff_text="diff")

    def fake_run_review(run_pr, openai_client, touched_files, diff_text):
        received["run_review_pr"] = run_pr
        received["touched_files"] = touched_files
        received["diff_text"] = diff_text

    monkeypatch.setattr(main_module, "fetch_pr_diff", fake_fetch_pr_diff)
    monkeypatch.setattr(main_module, "run_review", fake_run_review)

    main_module.main()

    assert repo.get_pull_calls == [42]
    assert received["fetch_pr_diff_pr"] is pr
    assert received["run_review_pr"] is pr
    assert received["touched_files"] == ["a.py"]
    assert received["diff_text"] == "diff"
