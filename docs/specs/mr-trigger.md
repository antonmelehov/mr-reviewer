# Spec: mr-trigger

Capability: get from "a PR was opened or updated" to "the workflow has an authenticated Azure session and the PR's diff + touched files in hand." Does not cover what happens with that diff (see [diff-review](diff-review.md)) or how results get posted (see [comment-posting](comment-posting.md)).

Context: [architecture.md](../../architecture.md) step 2, [ADR-002](../adrs/adr-002-trigger-mechanism.md) (trigger mechanism), [ADR-001](../adrs/adr-001-platform.md) (GitHub).

## Requirements
1. The workflow runs automatically when a PR is opened, reopened, or updated with new commits (synchronize) — and only for PR events. A push with no associated PR does not trigger it.
2. The workflow authenticates to Azure using OIDC federated credentials. No long-lived Azure secret is stored anywhere in the repo or the workflow file.
3. The workflow fetches the full current diff (base branch → latest head commit) and the list of touched files for the PR, not an incremental diff since the last run.
4. If a new commit is pushed to a PR while a run for an earlier commit on the same PR is still in progress, the earlier run is superseded/cancelled rather than letting both run to completion.
5. If the workflow fails before completing (OIDC auth failure, diff fetch failure), it fails visibly — a non-zero/failed run in the Actions UI — rather than silently no-op'ing.

## Scenarios

**New PR opened**
- Given a PR is opened against the repository
- When the PR is created
- Then the workflow starts, authenticates to Azure via OIDC, and fetches the diff and touched files for the PR's head commit

**New commit supersedes an in-progress run**
- Given a workflow run is in progress for a PR's previous commit
- When a new commit is pushed to the same PR before that run finishes
- Then the in-progress run for the stale commit is cancelled, and a new run starts for the latest commit

**Push with no PR is ignored**
- Given a commit is pushed directly to a branch with no associated open PR
- When the push event occurs
- Then the workflow does not run

**OIDC auth failure fails loud**
- Given the workflow attempts to authenticate to Azure via OIDC
- When the token exchange fails (e.g. misconfigured federated credential)
- Then the run fails visibly and does not proceed to fetch the diff or invoke review

## Definition of Done
- [ ] Workflow runs automatically on PR opened/synchronize/reopened events against a real test PR
- [ ] No long-lived Azure secret exists anywhere in the repo or workflow file — auth is OIDC only
- [ ] Workflow successfully fetches the full diff and touched-file list for the PR's current head commit
- [ ] Pushing a new commit while a prior run is in progress cancels the stale run and starts a new one
- [ ] A push with no associated PR does not trigger the workflow
- [ ] A simulated OIDC/auth failure causes the run to fail visibly, not pass silently
- [ ] The diff + touched files are available in a form the diff-review step can consume
