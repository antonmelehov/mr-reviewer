# ADR-008: Primary model selection under subscription quota constraints

## Status
Accepted

## Context
[ADR-004](adr-004-agent-hosting.md) chose Azure AI Foundry Agent Service with a Claude catalog model as the primary model. [ADR-005](adr-005-claude-access-path.md) named GPT-4o as the manual-fallback example if Claude ever became unavailable.

Setting up the actual Azure resources surfaced a gap neither ADR anticipated: on the subscription this project deploys to (`Visual Studio Professional Subscription`), **every Claude model variant has 0/0 quota**, confirmed via `az cognitiveservices usage list` in both eastus2 and swedencentral. This isn't a catalog-availability problem — Claude is listed in the eastus2 catalog — it's a quota entitlement that was never granted on this subscription. The named fallback, **GPT-4o, also has 0 quota** on this subscription. A second subscription exists on the account (`EPAM Production`) but isn't accessible yet.

Of the catalog's Foundry-Agent-Service-compatible (`agentsV2`) chat models, only two currently have nonzero, unused quota on this subscription: `o4-mini` (100k TPM available) and `gpt-oss-120b` (5000k TPM available). Everything else is either ungranted (0 quota, same as Claude/GPT-4o) or already fully consumed by an unrelated pre-existing deployment (`rg-foundry-week4`: `gpt-4.1-mini`, `gpt-5-mini`, `Llama-3.3-70B-Instruct`).

`o4-mini` turned out to be a dead end too: its only catalog version (`2025-04-16`) is in `Deprecating` lifecycle status with an inference cutoff of 2026-11-19 — three days out at the time of writing — and Azure rejects new deployments of it outright (`ServiceModelDeprecating`). `gpt-oss-120b`'s only version is `GenerallyAvailable` with an inference cutoff of 2027-09-15.

## Options considered
- **Request Claude quota and wait** — keeps ADR-004's original intent, but is a manual approval process with no guaranteed timeline, and benefit/VS subscriptions aren't guaranteed eligible for partner-model quota at all.
- **Switch to the EPAM Production subscription** — not available yet (no access).
- **`o4-mini` as primary** — ruled out: deprecating, cannot take new deployments regardless of quota.
- **`gpt-oss-120b` as primary (chosen)** — an open-weight 120B model, `agentsV2`-compatible, `GenerallyAvailable` with over a year of runway left, and by far the most quota headroom (5000k TPM) of any viable option on this subscription. Not as purpose-built for structured reasoning as a dedicated reasoning model, but the only `agentsV2`-compatible chat model on this subscription that is both quota-available and not actively deprecating.

## Decision
Deploy **`gpt-oss-120b`** as the Foundry agent's primary model for the MVP. There is currently no second `agentsV2`-compatible model on this subscription with available quota to serve as a documented fallback (per [ADR-005](adr-005-claude-access-path.md)'s runbook) — re-run the same quota/lifecycle check (`az cognitiveservices usage list` + catalog lifecycle status) at the time a fallback is actually needed, since quota allocation and model deprecation both change over time.

## Consequences
- Deviates from ADR-004's "Claude as primary" decision and ADR-005's GPT-4o fallback example — not because either is a worse fit, but because neither is obtainable on this subscription right now. Revisit ADR-004 if Claude quota is ever granted, or if work moves to a subscription where Claude has quota (e.g. EPAM Production, once accessible).
- No fallback model is pre-selected for the MVP — ADR-005's manual-runbook policy still applies, but the "redeploy against a different catalog model" step now starts with a fresh quota/lifecycle check rather than a pre-named model.
- Review tone/quality is an open-weight OpenAI model's, not Anthropic's, for the MVP. ADR-004's core reasoning (managed orchestration via Foundry, swappable catalog model) still holds regardless of which specific model is plugged in — only the specific model name changes.
- Catalog model availability and quota both shift over time (as `o4-mini`'s sudden deprecation here shows) — this ADR documents the model in use as of 2026-11-16, not a permanent guarantee.
