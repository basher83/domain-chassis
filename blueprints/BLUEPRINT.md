# Blueprints

Architecture design artifacts for domain-chassis. Each blueprint captures the strategic
thinking behind a body of changes: problem framing, architectural commitments, phasing,
and scope boundaries. Specs decompose from blueprints. Gates validate the phases
blueprints define.

## Index

| Blueprint | Status | Scope |
|-----------|--------|-------|
| [B1-chassis-architecture](B1-chassis-architecture.md) | Draft | Chassis as a whole: current state, component interactions, artifact lifecycle, governance, accumulated changes |
| [B2-qmd-architecture](B2-qmd-architecture.md) | Validated | QMD as 3I search infrastructure: system as deployed (v2.1.0), collection scoping, contamination controls |

Planned, not yet filed: gate-orchestrator (gate lifecycle automation — supervisor agent,
sub-agent dispatch, hook-enforced backpressure; blocked on B1). It takes the next
sequential number when authored, not a slot reserved here.

## Convention

Blueprints follow the `B{n}-{descriptor}.md` naming pattern, paralleling the gate
convention (`Q{n}-gate.md`). Numbering is sequential within the chassis project. The
blueprint standard and template live in `references/blueprint-standard.md` and
`templates/blueprint-template.md`.

Blueprint lifecycle: plan (author) and review (audit). No work phase — a blueprint's
execution is its decomposition into specs and gates through the existing gate lifecycle.
