---
Project: <domain>
Type: <category>
Date: YYYY-MM-DD
Status: Draft
Revision: v1
---

# [Project Name]: [One-Line Description]

## What It Is

What this thing does, why it exists, and what evidence supports building it. Not a feature list — the conceptual foundation. Ground in operational experience, research findings, or cross-project data when available.

## What It Replaces

Current state versus desired state. What's manual today, what's missing, what stays broken without this. If greenfield, describe the absence and its cost.

| Before | After |
|--------|-------|
| ... | ... |

## Design Inputs

| Source | Key Contribution |
|--------|-----------------|
| ... | What specific insight this source contributed to the architecture |

## Architecture

Core primitives and load-bearing decisions that constrain everything downstream. Structure this section to match the shape of the architecture — named primitives, layers, phases, whatever fits. Every decision that specs will inherit should be present with its reasoning.

## Phasing

How the work decomposes into gates. Remove this section for single-gate projects.

| Phase | Gate | Scope | Depends On |
|-------|------|-------|------------|
| 1 | Q__ | ... | — |
| 2 | Q__ | ... | Phase 1 |

## Scope Boundaries

### Excluded

What doesn't belong to this project and why.

### Deferred

What belongs to a future phase. Name the target phase when known.

## Open Questions

Unresolved design decisions. Each should be specific enough that an answer resolves it. Drain to zero before moving status to Pre-gate.

- [ ] ...
