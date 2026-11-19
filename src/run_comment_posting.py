import json
import os

from github import Github

from src.comment_posting import post_review
from src.diff_review import Finding

SCENARIOS = {
    "first_run": {
        "findings": [
            Finding(
                category="bug",
                file="src/run_comment_posting.py",
                line=1,
                severity="high",
                message="validation: high-severity finding",
            ),
            Finding(
                category="style",
                file="src/run_comment_posting.py",
                line=1,
                severity="low",
                message="validation: low-severity finding",
            ),
        ],
        "error_message": None,
    },
    "repush_unchanged": {
        "findings": [
            Finding(
                category="bug",
                file="src/run_comment_posting.py",
                line=1,
                severity="high",
                message="validation: high-severity finding",
            ),
            Finding(
                category="style",
                file="src/run_comment_posting.py",
                line=1,
                severity="low",
                message="validation: low-severity finding",
            ),
        ],
        "error_message": None,
    },
    "failure": {
        "findings": None,
        "error_message": "validation: simulated Foundry failure",
    },
    "fixed_and_clean": {
        "findings": [],
        "error_message": None,
    },
}


def main() -> None:
    token = os.environ["GITHUB_TOKEN"]
    repo_full_name = os.environ["GITHUB_REPOSITORY"]

    with open(os.environ["GITHUB_EVENT_PATH"], encoding="utf-8") as event_file:
        event = json.load(event_file)
    pr_number = event["pull_request"]["number"]

    with open("VALIDATION_SCENARIO_do_not_merge.json", encoding="utf-8") as scenario_file:
        scenario_name = json.load(scenario_file)["scenario"]

    scenario = SCENARIOS[scenario_name]
    print(f"Running scenario: {scenario_name}")

    github = Github(token)
    pr = github.get_repo(repo_full_name).get_pull(pr_number)

    post_review(pr, findings=scenario["findings"], error_message=scenario["error_message"])

    print("post_review completed")


if __name__ == "__main__":
    main()
