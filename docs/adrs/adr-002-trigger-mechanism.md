# ADR-002: Trigger mechanism

## Status
Accepted

## Context
An MR event needs to reach the Foundry review agent. Depends on [ADR-001](adr-001-platform.md) (GitHub).

## Options considered
- **Webhook + Azure Function dispatcher** — GitHub webhook → Azure Function (HTTP trigger) → Foundry agent. Decoupled from CI, room to add retry/queue logic later, but it's a whole new resource to build, host and secure (public endpoint, webhook secret validation, its own deployment).
- **CI pipeline step (chosen)** — a GitHub Actions workflow on `pull_request` events calls the Foundry Agent Service REST API directly, authenticating to Azure via OIDC federated credentials (no long-lived secret). No new infra to run; GitHub handles event delivery/retries; logs land in the Actions UI for free. The "boring, simple" option.
- **GitHub App + Function** — same shape as webhook+Function but via an installable GitHub App. Only pays off if we need multi-repo/multi-org support later, which is explicitly out of scope for the MVP.

## Decision
Use a **GitHub Actions workflow** triggered on `pull_request` (opened/synchronize) that calls the Foundry agent's REST API directly via OIDC.

## Consequences
- Review latency is tied to GitHub Actions runner availability/queue time.
- The trigger logic lives in a workflow YAML file in the reviewed repo itself — the workflow must be careful not to trigger review of its own changes in confusing ways.
- No extra Azure resource (Function App) to provision, deploy, or secure for the MVP.
- If multi-repo/org support is ever needed, revisit in favor of webhook + Function.
