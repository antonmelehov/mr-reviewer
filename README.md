# mr-reviewer

An AI agent that automatically reviews GitHub pull requests and posts review comments — built on Azure AI Foundry Agent Service with a catalog model (`gpt-oss-120b`; see [ADR-008](docs/adrs/adr-008-primary-model-quota.md) for why it's not Claude).

## Status
Early/MVP, in active development. This repo documents before it implements: specs exist before the code that implements them, and architectural choices get an ADR before they get built.

## How it works
1. A PR is opened or updated on GitHub.
2. A GitHub Actions workflow triggers, authenticates to Azure via OIDC, and fetches the diff.
3. An Azure AI Foundry agent (`gpt-oss-120b`) reviews the diff against basic categories (bugs, security smells, missing tests/null-checks, style).
4. The workflow posts the findings back on the PR — a summary comment plus inline comments on specific lines.

Full flow and diagram: [architecture.md](architecture.md).

## Using this in another repo

This is distributed as a composite GitHub Action ([ADR-007](docs/adrs/adr-007-distribution-model.md)) — the code lives here, but each adopting repo brings its own Azure AI Foundry project, agent, and OIDC trust (see [ADR-002](docs/adrs/adr-002-trigger-mechanism.md)). Nothing is shared between repos: no central service, no shared credentials, no shared Foundry resource.

A consumer's own workflow is responsible for the trigger and concurrency behavior `mr-trigger.md` requires — this action only runs the review once invoked:

```yaml
name: PR review
on:
  pull_request:
    types: [opened, synchronize, reopened]

concurrency:
  group: mr-reviewer-${{ github.event.pull_request.number }}
  cancel-in-progress: true

permissions:
  id-token: write
  contents: read
  pull-requests: write

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: antonmelehov/mr-reviewer@v1
        with:
          azure-client-id: ${{ vars.AZURE_CLIENT_ID }}
          azure-tenant-id: ${{ vars.AZURE_TENANT_ID }}
          azure-subscription-id: ${{ vars.AZURE_SUBSCRIPTION_ID }}
          foundry-project-endpoint: ${{ vars.FOUNDRY_PROJECT_ENDPOINT }}
          foundry-agent-name: ${{ vars.FOUNDRY_AGENT_NAME }}
```

The Azure values come from the adopter's own OIDC app registration, federated credential (scoped to `repo:<org>/<repo>:pull_request`), and RBAC grant on their own Foundry resource — not provided by this repo.

## Documentation
- [architecture.md](architecture.md) — high-level flow and diagram
- [docs/adrs/](docs/adrs/) — one decision per file: why things are built the way they are
- [docs/specs/](docs/specs/) — capability specs (requirements + Given/When/Then scenarios), written before implementation
- [AGENTS.md](AGENTS.md) — how to work in this repo: local setup, where secrets come from, the spec/ADR-first rule

## MVP scope
In scope: trigger on PR push, fetch the diff, review it against basic categories, post comments, log everything, no stored secrets (Azure auth via OIDC, GitHub auth via the Actions-provided token).

Out of scope for now: auto-merge/approve, full-repo context beyond the diff and touched files, per-user permissions, multi-platform support.
