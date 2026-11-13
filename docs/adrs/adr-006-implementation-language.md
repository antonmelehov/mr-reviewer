# ADR-006: Implementation language

## Status
Accepted

## Context
The GitHub Actions workflow step ([ADR-002](adr-002-trigger-mechanism.md)) needs to fetch the diff, call the Foundry agent ([ADR-004](adr-004-agent-hosting.md)), and post comments back on the PR ([ADR-003](adr-003-comment-posting.md)). That's a short, frequently-iterated script, not a long-lived service — the choice of language is scoped to that.

## Options considered
- **Python** — `actions/setup-python` + `pip install` is near-zero CI overhead, no compile step. `azure-ai-projects`/`azure-identity` cover the Foundry/auth side, `PyGithub` covers diff fetch + comment posting. Fast edit-run-test loop, which matters for iterating on review logic/prompts during a hackathon timeline. Dynamic typing offers less compile-time safety, but the logic here is a straight-line "fetch diff → call agent → post comment," not a large system where that matters much.
- **.NET** — Azure's own SDKs (`Azure.AI.Projects`, `Azure.Identity`, `Azure.Security.KeyVault.Secrets`) and `Octokit.net` are mature and well-documented, with strong typing. But GitHub Actions' custom-logic ecosystem is overwhelmingly JS/shell/Python; a .NET step needs `actions/setup-dotnet` plus `restore`/`build` on every run, adding CI time and ceremony for what's fundamentally two REST API calls.
- **Node/TypeScript** — `@azure/ai-projects` + `octokit`, arguably the most "native" fit since Actions' own toolkit and most custom actions are JS-first. Viable, but no stronger a fit than Python for this specific task, and Python was already the team's more comfortable default.

## Decision
Use **Python** for the `src/` implementation.

## Consequences
- `requirements.txt` (or `pyproject.toml`), `pytest` for tests, and `ruff` for lint/format are the expected conventions once code lands (see [AGENTS.md](../../AGENTS.md)).
- If this ever grows into a long-lived service (e.g. the webhook + Azure Function alternative from ADR-002), revisit — Python's CI-speed advantage matters less for a persistent service than for a short CI step.
