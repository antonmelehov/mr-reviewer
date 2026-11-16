# ADR-007: Distribution model

## Status
Accepted

## Context
The goal isn't just "this repo reviews its own PRs" — other repos should be able to adopt this reviewer without copy-pasting and maintaining their own fork of the logic.

## Options considered
- **Composite GitHub Action (chosen)** — an `action.yml` at the repo root wraps the Python implementation in `src/`. A consumer repo's workflow becomes a few lines: trigger + `uses: org/mr-reviewer@v1` with inputs (Azure client/tenant IDs, etc.). Versioned via git tags/releases, so `main` can keep moving without breaking pinned consumers.
- **Reusable workflow (`workflow_call`)** — consumers call the whole job via `uses: org/mr-reviewer/.github/workflows/review.yml@main`. We'd own the entire trigger/job shape, which is less flexible for a consumer who wants to add their own steps around it.
- **Copy-paste template, no real packaging** — document "copy this workflow + `src/` into your repo." Simplest, but no real reuse story: updates don't propagate, and every consumer forks the logic by hand.

## Decision
Package this as a **composite GitHub Action**: `action.yml` at the repo root, implementation in `src/`.

## Consequences
- `action.yml` becomes a versioned input/output contract — changes to it need to consider existing consumers, not just this repo's own use.
- This repo's own `.github/workflows/` serves two distinct purposes that must stay separate: this repo's own CI (lint/test on PRs to mr-reviewer itself), and a self-referential workflow (`uses: ./`) that exercises the action against this repo's own PRs — which doubles as the integration test before anything is tagged for external consumers.
- Fork-PR support (a consumer accepting PRs from forks) is explicitly out of scope for now — GitHub restricts OIDC/secrets on `pull_request` runs from forks by design, and supporting that safely needs a different trigger pattern. Revisit if/when that's actually requested.
