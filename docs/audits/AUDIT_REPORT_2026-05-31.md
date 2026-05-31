# Documentation Audit Report

Generated: 2026-05-31 | Commit: 82ac1fe

## Executive Summary

| Metric | Count |
|--------|-------|
| Documents scanned (user-facing) | 2 (README.md, AGENTS.md) |
| Supporting docs cross-checked | 12 (manifests, BLUEPRINT.md, foundation, references, skills, command) |
| Claims verified | ~55 |
| Verified TRUE | ~48 (87%) |
| **Verified FALSE** | **2** |
| Index/disk mismatches | 1 |
| Coverage gaps (undocumented dirs) | 3 |
| Ambiguous / namespace collisions | 2 |

The chassis docs are largely accurate. The skill/command/foundation/reference/template
inventories in `README.md` all check out against disk, and `AGENTS.md`'s constitutional,
anti-pattern, and convention claims hold. Two concrete false claims, one index mismatch,
and several coverage gaps are below.

## Verified FALSE Claims Requiring Fixes

### AGENTS.md

| Line | Claim | Reality | Fix |
|------|-------|---------|-----|
| 51 | "`specs/` directory is empty. The chassis ... has not yet authored specs for its own skill changes." | `specs/queue-lifecycle.md` exists and is git-tracked (commit `1366727` "docs(specs): add queue lifecycle specification"). | Update the Known Gaps entry: specs/ now contains `queue-lifecycle.md`. Remove or rescope the "empty" claim. |
| 36 | "B2 (gate orchestrator) is blocked on B1 stabilizing. B2-qmd-architecture covers QMD..." — implies a B2 gate-orchestrator blueprint exists alongside B2-qmd-architecture. | Only one B2 file exists on disk: `B2-qmd-architecture.md`. There is no `B2-gate-orchestrator` file. Two different things are both numbered B2. | Resolve the B2 collision: either renumber QMD to B3, or move gate-orchestrator to a different number. The doc narrates two B2s as if both are filed, but only one file exists. |

### blueprints/BLUEPRINT.md (index vs disk)

| Line region | Claim | Reality | Fix |
|------|-------|---------|-----|
| Index table | Lists "B2-gate-orchestrator — Planned — Gate lifecycle automation... Blocked on B1" as the only B2 row. | The B2 file actually on disk is `B2-qmd-architecture.md` (QMD search infrastructure, dated 2026-04-05). The index has no row for the file that exists, and lists a B2 row for a file that does not exist. | Add a row for `B2-qmd-architecture.md`; resolve the duplicate B2 numbering (see AGENTS.md line 36 above). The index is the source of truth for blueprint state and currently omits a tracked blueprint. |

## Coverage Gaps (documented structure omits tracked directories)

`README.md` enumerates Skills, Commands, Foundation, References, Templates, and Blueprints,
but three git-tracked top-level directories are absent from every table:

| Undocumented directory | Contents | Note |
|------------------------|----------|------|
| `agents/` | `gate-operator.md` — a subagent that preloads prime and drives the gate lifecycle ("gate Q{n}", "review Q{n}", "work Q{n}", "prime"). | Not mentioned in README or AGENTS.md. This is a shipped plugin component (an agent) with no documentation surface. |
| `adrs/` | `ADR-001-utc-canonical-timestamps.md` (Status: Proposed). | Not referenced anywhere in README/AGENTS. Note: AGENTS.md line 52 references a *different* "commons ADR-001" — see namespace collision below. |
| `skills/_shared/` | `now.mjs`, `git-changes.mjs`, `git-context.mjs`, `list-recent.mjs`, `changelog-bootstrap.mjs` (+ `.test.ts` siblings). | Shared runtime scripts. No `SKILL.md` references them by name, and README's File Operation Model does not mention a `_shared` location. The README's claim that skills only "read their own references and cross-reference sibling skills" does not account for a shared script directory. |

Also: `README.md`'s Blueprints table lists only `BLUEPRINT.md` and `B1-chassis-architecture.md`.
It omits `B2-qmd-architecture.md`, which is tracked on disk. (Same root cause as the BLUEPRINT.md
index mismatch.)

## Ambiguous / Namespace Collisions (human judgment needed)

| Location | Issue |
|----------|-------|
| AGENTS.md line 30 ("use the `chassis-release` skill"); also stated in project CLAUDE.md Manifests section. | No `skills/chassis-release/` directory exists in this repo. `chassis-release` is available as a harness slash command (globally installed), not as a plugin-shipped skill. The doc phrasing ("`.claude-plugin/` holds two manifests... use the `chassis-release` skill") reads as if the skill ships with the manifests. Either confirm chassis-release lives elsewhere (global skill) and note that, or ship it in this plugin. |
| AGENTS.md line 52 "commons ADR-001" vs `adrs/ADR-001-utc-canonical-timestamps.md`. | Two distinct "ADR-001" identifiers: one external (commons) and one local (UTC timestamps). Not strictly false — the AGENTS reference is explicitly to the external commons registry — but the bare "ADR-001" collides with the repo's own `adrs/ADR-001`. Consider qualifying both consistently (e.g., "commons ADR-001" vs "chassis ADR-001"). |

## Verified TRUE (spot-check confirmations)

- README Skills table: all 8 listed skills (`aar`, `component-writeup`, `gate-plan`, `gate-review`, `gate-work`, `prime`, `spec-review`, `triage`) exist as `skills/{name}/SKILL.md`. No extras, no missing.
- README Commands table: `init-domain` exists at `commands/init-domain.md`.
- README "init-domain ... scaffold ... the four chassis files and gates directory": command creates exactly 4 files (`{DOMAIN}.md`, `PIN.md`, `QUEUE.md`, `TRIAGE.md`) + `gates/`. Matches.
- README Foundation table: `SOUL.md`, `VESSEL.md`, `EVIDENCE.md`, `WELCOME.md` all exist; one-line descriptions match each file's actual thesis.
- README References table: `anti-pattern-registry.md`, `blueprint-standard.md` exist and match descriptions.
- README Templates table: all 5 (`adr-template`, `blueprint-template`, `component-writeup-template`, `proposal-template`, `triage-format`) exist.
- README File Operation Model: gate-plan owns `references/gate-template.md` (exists); gate-review and gate-work reference it via `${CLAUDE_PLUGIN_ROOT}`. Path asymmetry described accurately.
- AGENTS.md Skills convention: all 8 SKILL.md files include the `when_to_use` frontmatter field. Convention holds.
- AGENTS.md anti-pattern claims: AP-10 "The Recursive Defect" (line 114) and AP-12 "The Doctrinal Echo" (line 147) both exist in `references/anti-pattern-registry.md` with the stated names.
- AGENTS.md "B1 (chassis architecture) is Draft": B1 file Status field reads "Draft". Matches.
- plugin.json version `0.3.0` and marketplace.json plugin entry version `0.3.0` agree. (marketplace.json top-level `metadata.version` is `0.1.0` — this is the marketplace registry version, distinct from the plugin version, and is not contradicted by any doc claim.)

## Pattern Summary

| Pattern | Count | Root Cause |
|---------|-------|------------|
| Stale "known gap" claim | 1 | `specs/` documented as empty after a spec was authored; Known Gaps not updated. |
| B2 numbering collision | 1 (spans 3 docs) | A second blueprint was filed as B2-qmd-architecture while B2 was already conceptually reserved for gate-orchestrator; index, AGENTS, and README never reconciled. |
| Undocumented shipped component | 3 dirs | `agents/`, `adrs/`, `_shared/` added without extending README's structure tables. |
| Cross-registry ID collision | 2 | "ADR-001" and "B2" each name two different artifacts in different registries. |

## Human Review Queue

- [ ] Confirm whether `chassis-release` is intentionally a global/harness skill rather than plugin-shipped, and reword AGENTS.md line 30 accordingly (or ship the skill here).
- [ ] Decide the B2 renumbering (renumber QMD vs renumber gate-orchestrator) and propagate to BLUEPRINT.md, AGENTS.md, and README.
- [ ] Decide whether `agents/gate-operator.md`, `adrs/`, and `skills/_shared/` should appear in README's structure tables, or are intentionally internal.
