# ADR-001: Repo/MR hosting platform

## Status
Accepted

## Context
The MVP needs one real platform to host the repo and its merge/pull requests. Per the brief: pick whichever is fastest to get a real test repo running on — multi-platform support is explicitly out of scope.

## Options considered
- **GitHub** — already have an account; Actions CI is built in; REST/webhook/Review APIs are well documented and widely supported by SDKs and examples. Fastest path to a working test repo.
- **GitLab** — "merge request" is its native vocabulary, and CI/CD is solid, but setting up an org/runner from scratch adds setup time we don't need to spend.
- **Azure DevOps** — same tenant as the rest of the infra (Foundry), but its REST API and PR comment/thread model are more awkward to work with, with a steeper learning curve for this specific use case.

## Decision
Use **GitHub**.

## Consequences
- All subsequent ADRs and specs are scoped to GitHub's API surface (Actions, REST API, Review API) — no multi-platform abstraction layer.
- The project keeps using "MR" informally in docs (matching the brief's vocabulary), even though GitHub calls them "pull requests" — same concept, no need to churn existing wording.
