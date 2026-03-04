# Blueprint Standard

The blueprint is the architecture design artifact that precedes specs. It captures the strategic thinking that turns a validated idea into a concrete architecture: problem framing, research synthesis, architectural commitments, phasing strategy, and scope boundaries. Specs decompose from the blueprint. Gates validate the phases the blueprint defines. The blueprint is where the "why this shape" reasoning lives so that agents inheriting the specs understand the decisions behind them.

Not every project needs a blueprint. A clone of an existing pattern, a single-gate tool, a quick prototype — these go straight to specs or skip specs entirely. The trigger for a blueprint is strategic complexity: multiple phases, research dependencies, cross-domain implications, many moving parts where due diligence upfront prevents failure modes during implementation. If the architecture fits in your head and decomposes into specs without deliberation, you don't need one.

The proof of concept is the Range architecture design document, which went through 14 revisions over a week of research and deliberation, then cleanly decomposed into three gate phases (Q6, Q14, Q15) that all cleared. The upfront investment in design eliminated the class of mid-build architectural surprises that derail execution.

## Location

`blueprint.md` at the project root, next to `specs/`. Git-tracked, versioned through iteration. One blueprint per project. If a project's scope expands enough to warrant a second blueprint, that's a signal the project should decompose.

## Frontmatter

```yaml
---
Project: <domain>
Type: <category — what kind of work this is>
Date: <created date, ISO 8601>
Status: Draft | Active | Pre-gate | Superseded
Revision: <version + amendment summary when applicable>
---
```

### Status (closed enum)

| Value | Meaning |
|-------|---------|
| `Draft` | Forming. Research in progress, architectural commitments not yet locked. |
| `Active` | Being iterated on. Core architecture is taking shape, design inputs accumulating. |
| `Pre-gate` | Stable enough to decompose into specs and gates. Architectural commitments are locked. Open questions should be at zero or explicitly deferred to a named phase. |
| `Superseded` | Replaced by a new version or the project shipped and the blueprint is now historical record. |

No qualifiers on status values. `Draft (almost done)` is not valid. If the document is almost done, move it to Active or Pre-gate.

### Revision

Free-form but should track meaningful changes. Format: version identifier plus amendment summary when the document has gone through significant iteration.

Examples: `v1`, `v3 + Amendment 001 (bounded-context execution model)`, `v14 — final pre-gate`.

## Sections

### What It Is (required)

Problem framing. What this thing does, why it exists, what empirical basis supports building it. Not a feature list — the conceptual foundation that everything else derives from. Ground it in evidence when evidence exists: operational data, cross-project analysis, production experience, research findings.

An agent reading this section should understand the problem space well enough to evaluate whether a proposed spec belongs to this project or is scope creep.

### What It Replaces (required)

Gap analysis. Current state versus desired state. What's being done manually, what's missing, what breaks or stays broken without this. Forces articulation of the actual delta rather than enthusiasm for the new thing. If nothing is being replaced (greenfield), this section describes the absence — what capability doesn't exist and what that costs.

### Design Inputs (required)

Research catalogue. Every source that informed the architecture, with the specific contribution extracted from each. This is the due diligence receipt and the traceability chain. An agent reading the blueprint can follow any architectural decision back to the research that justified it.

Format: table with source and key contribution columns. Depth scales with the project — a complex system might have 25+ entries, a focused tool might have 3-5. The point is not volume but traceability. Every entry should articulate what specific insight the source contributed to the architecture, not just that it was read.

### Architecture (required)

The core primitives and commitments that constrain everything downstream. These are the load-bearing decisions — the choices that, once made, shape every spec that follows. Individual specs implement these commitments but the blueprint is where they're justified and locked.

This section absorbs what ADRs traditionally capture: decisions and their reasoning, in context rather than as isolated records. The architecture section is the design authority for the project.

Structure varies by project. Some architectures are best described as a set of named primitives with implementation details. Others are best described as layers or phases. The content should match the shape of the architecture, not a prescribed template. What matters is that every load-bearing decision is present with its reasoning.

### Phasing (required when work spans multiple gates)

How the work decomposes into executable chunks. Which gates cover which capabilities, what the dependency chain looks like, what order things ship in. This is a design decision made upfront, not discovered mid-build. Clean phasing enables clean gates.

Not required for single-gate projects. If the work is one gate, the Architecture section already defines the scope and the gate document handles validation planning.

### Scope Boundaries (required)

What's explicitly excluded and why. Prevents scope creep during execution and gives agents clear rails. Two categories:

Excluded — things that don't belong to this project at all, with reasoning. "Network isolation is a monitoring concern, not a proxy concern."

Deferred — things that belong to a future phase rather than things that don't belong. "Network isolation fields are not part of Phase 1 — they belong alongside the checkpoint that validates network restriction enforcement." Deferred items should name the phase or gate they're deferred to when known.

### Open Questions (required when status is Draft or Active)

Unresolved design decisions that need research or operator input before they can become architectural commitments. Each question should be specific enough that an answer resolves it — not "what about security?" but "does sandbox isolation use Seatbelt profiles or Docker containers?"

Open questions should drain to zero before status moves to Pre-gate. Questions that can't be resolved upfront should be explicitly deferred to a named phase with justification for why deferral is acceptable.

### Revision History (optional)

Amendment log when the blueprint goes through significant iteration. Useful for documents that evolve over multiple sessions. Not needed for blueprints that stabilize quickly. When used, amendments should summarize what changed and why — not just "updated section 3."

### Risk / Failure Modes (optional)

Known risks the architecture is designed to mitigate, or failure modes identified during research that the design explicitly addresses. Most useful for projects where the architecture makes deliberate trade-offs against specific failure scenarios. If the Architecture section already covers risk reasoning inline, a separate section adds no value.

## Weight Classes

The skeleton is the same across domains. The depth scales with the complexity of the work. A forge blueprint for a production system gets the full ceremony — deep design inputs, rigorous architecture section, explicit phasing with gate mapping. A workshop tool gets a lighter version — the architecture section might be two paragraphs and phasing might be "one gate, ship it." A lab initiative might lean heavy on gap analysis and phasing with less emphasis on design inputs.

The sections are universal. The depth is proportional to the stakes.

## Relationship to Other Artifacts

The blueprint sits between the chrome repellent (go/no-go decision) and specs (implementation details). It is the missing middle:

```text
Chrome Repellent  →  Blueprint  →  Specs  →  Gate  →  Execution
    (filter)         (design)     (soul)   (validation)  (build)
```

The blueprint does not replace specs. Specs remain the authoritative source for implementation details — what the code must do, acceptance criteria, non-goals at the feature level. The blueprint provides the architectural context that specs inherit: why these features exist, why they have this shape, how they compose into a whole.

The blueprint does not replace gate documents. Gates define what must be proven. The blueprint's Phasing section defines what each gate covers, but the gate document owns the validation plan — checkpoints, evidence requirements, pass criteria.

The blueprint does not replace research artifacts (teardowns, studies, patterns). Research feeds the blueprint through the Design Inputs section. The blueprint synthesizes research into architecture. Research is the raw material; the blueprint is the refined output.
