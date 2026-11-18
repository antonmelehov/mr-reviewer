import json
import os

from github import Github

from src.trigger import fetch_pr_diff


def main() -> None:
    token = os.environ["GITHUB_TOKEN"]
    repo_full_name = os.environ["GITHUB_REPOSITORY"]

    with open(os.environ["GITHUB_EVENT_PATH"], encoding="utf-8") as event_file:
        event = json.load(event_file)
    pr_number = event["pull_request"]["number"]

    github = Github(token)
    result = fetch_pr_diff(github, repo_full_name, pr_number)

    print(f"Touched files ({len(result.touched_files)}):")
    for filename in result.touched_files:
        print(f"  - {filename}")

    print("\nDiff:")
    print(result.diff_text)


if __name__ == "__main__":
    main()
