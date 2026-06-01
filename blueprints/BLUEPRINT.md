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
| [B3-gate-loop-pi-extension](B3-gate-loop-pi-extension.md) | Draft | Gate lifecycle as a Pi extension: `currentPhase()` fold over gate-file state, two-layer transition gate (deterministic checkers + cold judge), file-as-truth, FAIL-convergence constraint. Pi-native recomposition of the retired Q33 gate-orchestrator; softened dependency on B1's gate-file artifact contract |

## Convention

Blueprints follow the `B{n}-{descriptor}.md` naming pattern, paralleling the gate
convention (`Q{n}-gate.md`). Numbering is sequential within the chassis project. The
blueprint standard and template live in `references/blueprint-standard.md` and
`templates/blueprint-template.md`.

Blueprint lifecycle: plan (author) and review (audit). No work phase — a blueprint's
execution is its decomposition into specs and gates through the existing gate lifecycle.
