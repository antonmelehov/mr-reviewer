# ADR-004: Review agent hosting

## Status
Accepted

## Context
Something has to run the actual review logic — call a model, reason over the diff, decide what to comment. This ADR documents a decision made up front (before this project's documentation discipline started), not one explored fresh.

## Options considered
- **Bespoke container** (own Docker image running an agent loop, on Container Apps/AKS) — full control, but reinvents orchestration, auth, retries, and model-client plumbing that a managed agent service already provides.
- **Raw API calls** (call a model API ad hoc from inside the CI step, no agent framework) — minimal infra, but no persistent thread/tool-call management, no managed-identity-based auth to the model, and no Azure-native observability without hand-building it.
- **Azure AI Foundry Agent Service with a catalog model (chosen)** — managed orchestration and tool-calling, native Key Vault/managed-identity integration, and the underlying model is swappable via the catalog without re-architecting (see [ADR-005](adr-005-claude-access-path.md)).

## Decision
Use **Azure AI Foundry Agent Service**, with the agent configured against a **Claude model from the Foundry model catalog** as the primary model.

## Consequences
- The review agent's API surface is Foundry's agent API shape, not a generic "call any LLM" abstraction — acceptable since the MVP targets one platform and one use case.
- Model availability is tied to Foundry's regional/subscription catalog offering; what happens if Claude isn't available there is covered separately in ADR-005.
- Claude Code (this CLI) is a separate, personal dev tool used to *build* this repo — it is not, and does not become, the production reviewer agent.
