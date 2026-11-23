from dataclasses import dataclass


@dataclass
class TriggerResult:
    touched_files: list[str]
    diff_text: str


def fetch_pr_diff(pr) -> TriggerResult:
    touched_files: list[str] = []
    patches: list[str] = []

    for file in pr.get_files():
        touched_files.append(file.filename)
        if file.patch:
            patches.append(f"--- a/{file.filename}\n+++ b/{file.filename}\n{file.patch}")

    return TriggerResult(touched_files=touched_files, diff_text="\n".join(patches))
