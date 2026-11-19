import json
import os

from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from github import Github

from src.diff_review import DiffReviewError, review_diff
from src.trigger import fetch_pr_diff

FOUNDRY_ENDPOINT = "https://mr-reviewer-foundry-anton-melehov.services.ai.azure.com/api/projects/mr-reviewer"
AGENT_NAME = "mr-reviewer-diff-review"


def main() -> None:
    token = os.environ["GITHUB_TOKEN"]
    repo_full_name = os.environ["GITHUB_REPOSITORY"]

    with open(os.environ["GITHUB_EVENT_PATH"], encoding="utf-8") as event_file:
        event = json.load(event_file)
    pr_number = event["pull_request"]["number"]

    github = Github(token)
    trigger_result = fetch_pr_diff(github, repo_full_name, pr_number)

    print(f"Touched files ({len(trigger_result.touched_files)}):")
    for filename in trigger_result.touched_files:
        print(f"  - {filename}")

    credential = DefaultAzureCredential()
    project_client = AIProjectClient(endpoint=FOUNDRY_ENDPOINT, credential=credential, allow_preview=True)
    openai_client = project_client.get_openai_client(agent_name=AGENT_NAME)

    try:
        findings = review_diff(openai_client, trigger_result.touched_files, trigger_result.diff_text)
    except DiffReviewError as exc:
        print(f"\nDiff review FAILED: {exc}")
        raise SystemExit(1) from exc

    print(f"\nFindings ({len(findings)}):")
    for finding in findings:
        print(f"  [{finding.category}/{finding.severity}] {finding.file}:{finding.line} - {finding.message}")


if __name__ == "__main__":
    main()
