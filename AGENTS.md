# AGENTS.md

Repo-specific guidance for agents working in `domain-chassis`. `foundation/WELCOME.md` covers full 3I architecture. This file covers what is unique to this repo.

## What this repo ships

A Claude Code plugin (`.claude-plugin/plugin.json`) — shared operational methodology consumed by every 3I domain (Forge, Lab, Workshop, Research). Skills, commands, foundation doctrine, templates, references, blueprints. The plugin is read-only at runtime; the workspace where it executes holds all operational state.

See `README.md` for the skill index, the workspace-vs-plugin file-operation boundary, and the rationale for the `${CLAUDE_PLUGIN_ROOT}` path asymmetry.

## Constitutional layer

`foundation/` holds the principles every skill must respect:

- `SOUL.md` — specs are the soul, implementations are disposable
- `VESSEL.md` — source is the vessel, source is ground truth
- `EVIDENCE.md` — evidence and interpretation are separate artifacts
- `WELCOME.md` — 3I system orientation, read by agents entering any domain

Changes to foundation files are doctrinal. Open them only with explicit operator direction.

## Skills convention

Every `skills/{name}/SKILL.md` frontmatter must include the `when_to_use` field (introduced 0.1.22). Skill descriptions are the routing signal that decides whether the skill loads — they are not summaries.

Cross-skill file references use `${CLAUDE_PLUGIN_ROOT}/skills/{skill-name}/...`. Same-skill references use relative paths. Never write to a sibling skill's directory. The plugin never writes to itself; if a skill needs persistent state, it lives in the operator's workspace.

## Manifests

`.claude-plugin/` holds two manifests: `plugin.json` (the plugin manifest, read at install and load) and `marketplace.json` (the registry, read by marketplace consumers). For semver semantics, the contract between the two, and the release workflow, use the `chassis-release` slash command.

## Blueprints and gates

Blueprints live in `blueprints/B{n}-{descriptor}.md`, numbered sequentially within the chassis (paralleling the `Q{n}-gate.md` convention used in operator workspaces). `blueprints/BLUEPRINT.md` is the index and the source of truth for which blueprints exist and their status — consult it rather than tracking individual blueprints by number here. Gates themselves are never authored in this repo — they live in domain workspaces and reference chassis skills.

## Anti-pattern awareness

`references/anti-pattern-registry.md` catalogs identified anti-patterns. Two with active enforcement relevance:

- **AP-10 Recursive Defect** — particularly relevant for enforcement and remediation checkpoints.
- **AP-12 Doctrinal Echo** — hedged generalizations propagate through the chassis into every domain. Doctrine added here echoes everywhere. Scope claims tightly, cite evidence in-place, and do not generalize from a single domain's observation.

## Checkpoint trailers

`.entire/` is an external snapshot system. Reverts and structural changes carry an `Entire-Checkpoint: {hash}` trailer in the commit message — this is the recovery anchor, not a rationale. Human "why" for non-obvious reverts belongs in the commit body above the trailer.

## Known gaps

- `specs/` contains `queue-lifecycle.md`. The chassis ships the spec convention to other domains but has not yet authored specs for most of its own skill changes. Tracked in B1.
- The chassis does not accept domain-specific artifacts. Cross-domain findings route through `commons/`; the chassis receives updates as a result (commons ADR-001).
