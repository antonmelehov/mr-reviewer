# AGENTS.md

Instructions for any AI coding agent (Claude Code or otherwise) working in this repo. If you're a human, this applies to you too.

## What this repo is
An AI agent that reviews GitHub pull requests automatically and posts comments on them. See [architecture.md](architecture.md) for the flow and [docs/adrs/](docs/adrs/) for why things are built the way they are.

**Claude Code (this tool) is not the production reviewer.** It's the personal dev tool used to build this repo. Don't conflate the two in code, comments, or docs — e.g. don't name things so it looks like Claude Code itself is what reviews PRs in production.

## The one rule that matters
No code gets written for a capability without a spec in `docs/specs/` describing it first. No architectural choice (new service, new trigger, new data flow) gets made without an ADR in `docs/adrs/` recording it. If you're about to write code and can't point to the spec or ADR that justifies it, stop and write that first.

## Tech stack
- **Language:** Python ([ADR-006](docs/adrs/adr-006-implementation-language.md)).
- **Dependencies:** `azure-ai-projects` (Foundry agent calls), `azure-identity` (auth), `PyGithub` (diff fetch + comment posting).
- **Tests:** `pytest`, mirroring `src/` structure under `tests/`.
- **Lint/format:** `ruff`.
- **Packaging:** this repo is distributed as a composite GitHub Action — `action.yml` at the repo root wraps `src/` ([ADR-007](docs/adrs/adr-007-distribution-model.md)). This repo's own `.github/workflows/` covers two different things: this repo's CI (lint/test), and a self-referential workflow (`uses: ./`) that exercises the action against its own PRs.

Nothing above is scaffolded yet — `src/` is empty until the first capability has a spec. When the first spec lands, create `requirements.txt` (or `pyproject.toml`) and `tests/` alongside the code that implements it, not before.

## Running and testing locally
Once code exists:
```
python -m venv .venv
.venv\Scripts\activate       # or: source .venv/bin/activate on macOS/Linux
pip install -r requirements.txt
pytest
ruff check .
```
There's no local emulator for Azure AI Foundry Agent Service — you can't fully run the review step offline. For unit tests, mock the Foundry agent's response (see the relevant spec's Given/When/Then scenarios for expected inputs/outputs). For a manual smoke test against the real agent, authenticate locally with `az login` and let `DefaultAzureCredential` pick that up — don't create or use a service principal/API key for local dev.

## Secrets
- **In CI (GitHub Actions):** no stored secrets at all. Auth to Azure is via OIDC federated credentials, exchanged for an Azure AD access token with RBAC permissions on the Foundry project ([ADR-002](docs/adrs/adr-002-trigger-mechanism.md)). No Key Vault is provisioned for the current scope — see [ADR-005](docs/adrs/adr-005-claude-access-path.md)'s consequences for why. Posting comments uses the Actions-provided `GITHUB_TOKEN`, not a personal token.
- **Locally:** auth via `az login` (see above). If you ever need a GitHub token for local testing of comment-posting, put it in a `.env` file — it's gitignored, never commit it, and use a token scoped only to the test repo.
- Nothing that counts as a secret goes in the repo, a workflow file, or an ADR/spec. If a doc needs to reference where a credential comes from, name the OIDC trust relationship or RBAC role, not a value.
- If the direct-Anthropic-API fallback in ADR-005 is ever actually adopted, that's the point to introduce Key Vault — not before.

## Where to look first
- [architecture.md](architecture.md) — the three-step flow and diagram.
- [docs/adrs/](docs/adrs/) — why each architectural choice was made.
- [docs/specs/](docs/specs/) — requirements + scenarios per capability, written before that capability's code.
