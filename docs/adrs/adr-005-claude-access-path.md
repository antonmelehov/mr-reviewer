# ADR-005: Model access path and fallback policy

## Status
Accepted

## Context
Depends on [ADR-004](adr-004-agent-hosting.md): the agent's primary model is Claude from the Foundry catalog. That catalog's availability varies by region/subscription, and the catalog also natively includes OpenAI models (Azure OpenAI is part of Foundry). We need a policy for what happens if the primary model isn't available, without over-building resilience the MVP doesn't need.

## Options considered
- **Manual runbook only (chosen)** — the Foundry agent is configured with one catalog model (Claude) at a time. If it's ever unavailable, a human redeploys the agent against a different catalog model (e.g. GPT-4o — also natively in the Foundry catalog, so this is a config change, not a new integration). No fallback code, no extra secrets.
- **Code fallback to direct Anthropic API** — app code tries the Foundry Claude deployment first, and on failure calls `api.anthropic.com` directly using a Key Vault secret. Keeps the model specifically Claude, but this is a second integration path (separate auth, separate billing, data leaves Azure's network) to build, maintain and test for a case that may never trigger.
- **Automatic multi-provider chain** (Claude via Foundry → GPT-4o via Foundry → Claude via direct Anthropic API, all automatic) — most resilient, but the most complexity: different models can produce inconsistent review tone/quality, and it's meaningfully more to test. Not justified for an MVP/hackathon timeline.

## Decision
**Manual runbook only.** No automatic runtime fallback code in the MVP. If Claude becomes unavailable via the Foundry catalog, redeploy the agent against a different catalog model (e.g. GPT-4o) — a short operational note in AGENTS.md, not application logic.

## Consequences
- If Claude ever becomes unavailable, there's a manual step and a gap in reviews until someone redeploys — accepted for the MVP.
- No direct Anthropic API integration, no second secret, no second auth path to maintain right now.
- Revisit (toward an automatic fallback) only if this actually causes friction in practice — avoids building speculative robustness the brief explicitly scopes out.
