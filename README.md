# mr-reviewer

An AI agent that automatically reviews GitHub pull requests and posts review comments — built on Azure AI Foundry Agent Service with a Claude model.

## Status
Early/MVP, in active development. This repo documents before it implements: specs exist before the code that implements them, and architectural choices get an ADR before they get built.

## How it works
1. A PR is opened or updated on GitHub.
2. A GitHub Actions workflow triggers, authenticates to Azure via OIDC, and fetches the diff.
3. An Azure AI Foundry agent (Claude) reviews the diff against basic categories (bugs, security smells, missing tests/null-checks, style).
4. The workflow posts the findings back on the PR — a summary comment plus inline comments on specific lines.

Full flow and diagram: [architecture.md](architecture.md).

## Documentation
- [architecture.md](architecture.md) — high-level flow and diagram
- [docs/adrs/](docs/adrs/) — one decision per file: why things are built the way they are
- [docs/specs/](docs/specs/) — capability specs (requirements + Given/When/Then scenarios), written before implementation
- [AGENTS.md](AGENTS.md) — how to work in this repo: local setup, where secrets come from, the spec/ADR-first rule

## MVP scope
In scope: trigger on PR push, fetch the diff, review it against basic categories, post comments, log everything, secrets via Key Vault/managed identity only.

Out of scope for now: auto-merge/approve, full-repo context beyond the diff and touched files, per-user permissions, multi-platform support.
