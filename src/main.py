import json
import logging
import os

from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from github import Github

from src.orchestrator import run_review
from src.trigger import fetch_pr_diff

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)


def main() -> None:
    github_token = os.environ["GITHUB_TOKEN"]
    repo_full_name = os.environ["GITHUB_REPOSITORY"]
    foundry_endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
    foundry_agent_name = os.environ["FOUNDRY_AGENT_NAME"]

    with open(os.environ["GITHUB_EVENT_PATH"], encoding="utf-8") as event_file:
        event = json.load(event_file)
    pr_number = event["pull_request"]["number"]

    github = Github(github_token)
    pr = github.get_repo(repo_full_name).get_pull(pr_number)

    trigger_result = fetch_pr_diff(pr)
    logger.info(
        "PR #%d (%s): fetched %d touched file(s), %d chars of diff",
        pr.number,
        pr.head.sha,
        len(trigger_result.touched_files),
        len(trigger_result.diff_text),
    )

    credential = DefaultAzureCredential()
    project_client = AIProjectClient(endpoint=foundry_endpoint, credential=credential, allow_preview=True)
    openai_client = project_client.get_openai_client(agent_name=foundry_agent_name)

    run_review(pr, openai_client, trigger_result.touched_files, trigger_result.diff_text)


if __name__ == "__main__":
    main()
