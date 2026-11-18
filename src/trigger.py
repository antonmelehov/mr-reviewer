from dataclasses import dataclass

from github import Github


@dataclass
class TriggerResult:
    touched_files: list[str]
    diff_text: str


def fetch_pr_diff(github: Github, repo_full_name: str, pr_number: int) -> TriggerResult:
    repo = github.get_repo(repo_full_name)
    pr = repo.get_pull(pr_number)

    touched_files: list[str] = []
    patches: list[str] = []

    for file in pr.get_files():
        touched_files.append(file.filename)
        if file.patch:
            patches.append(f"--- a/{file.filename}\n+++ b/{file.filename}\n{file.patch}")

    return TriggerResult(touched_files=touched_files, diff_text="\n".join(patches))
