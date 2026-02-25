# domain-chassis

Shared operational methodology for all domains. Gate validation lifecycle, session context loading, structured document review, and operational retrospectives.

## Skills

| Skill | Purpose | Lifecycle Role |
|-------|---------|----------------|
| aar | After-action review of a completed work session | Writes AAR to domain knowledge repo |
| gate-plan | Author a gate document from a QUEUE.md item | Creates Q{n}-gate.md |
| gate-review | Audit a gate document against the quality bar | Produces findings, appends Gate Review verdict to gate document |
| gate-work | Execute a gate document checkpoint by checkpoint | Edits Q{n}-gate.md in place, moves to gates/ on clear |
| prime | Load doctrine, PIN, queue, and triage state | Read-only summary |
| skill-creator | Create, improve, and evaluate skills | Creates/edits SKILL.md files |
| spec-review | Multi-round structured document review via subagent | Produces findings, no file writes |

## Commands

| Command | Purpose |
|---------|---------|
| init-domain | Scaffold a new domain workspace with the four chassis files and gates directory |

## References

| File | Purpose |
|------|---------|
| anti-pattern-registry.md | Catalog of identified anti-patterns across the gate and operational methodology |
| triage-format.md | Triage intake formatting conventions |
| WELCOME.md | System orientation for agents entering a domain workspace |

## Templates

| File | Purpose |
|------|---------|
| ADR-template.md | Architecture Decision Record format |
| Proposal-template.md | Options evaluation and decision proposal format |

## File Operation Model

These skills operate across two distinct locations. Understanding the boundary prevents path bugs and unintended writes.

### Workspace root (current working directory)

All domain-facing file operations target the workspace root. This is the operator's domain directory (e.g., `~/dev/workshop/`, `~/dev/forge/`).

Files read from workspace root:

- `QUEUE.md` — gate-plan (resolve Q-item), gate-work (queue context), prime (load intent)
- `PIN.md` — prime (project index)
- `TRIAGE.md` — prime (check for pending intake)
- `{DOMAIN}.md` — prime (doctrine discovery: FORGE.md, WORKSHOP.md, LAB.md, RESEARCH.md)
- `*-gate.md` — gate-plan (study prior gates), gate-review (evaluate), gate-work (execute)
- `gates/*-gate.md` — gate-plan (study cleared prior gates)

Files written to workspace root:

- `Q{n}-gate.md` — gate-plan creates, gate-work edits in place, gate-review appends Gate Review verdict
- `gates/Q{n}-gate.md` — gate-work moves cleared gates here (creates directory if needed)

No skill writes to the plugin directory. The plugin is read-only at runtime.

### Plugin directory (`${CLAUDE_PLUGIN_ROOT}`)

Skills read their own references and cross-reference sibling skills. Nothing is written here.

Same-skill references use relative paths:

- gate-plan reads `references/gate-template.md` (its own reference)
- prime reads `references/workspace-standard.md` (its own reference)

Cross-skill references use the plugin root variable:

- gate-review reads `${CLAUDE_PLUGIN_ROOT}/skills/gate-plan/SKILL.md` (quality bar)
- gate-review reads `${CLAUDE_PLUGIN_ROOT}/skills/gate-plan/references/gate-template.md` (structural conventions)
- gate-work reads `${CLAUDE_PLUGIN_ROOT}/skills/gate-plan/references/gate-template.md` (gate conventions)

### Why the asymmetry

gate-plan references `references/gate-template.md` with a relative path because it owns that file. gate-review and gate-work reference the same file via `${CLAUDE_PLUGIN_ROOT}/skills/gate-plan/references/gate-template.md` because they are reaching into a sibling skill's directory. The relative path resolves within the owning skill's context; the absolute path resolves from any skill's context. Both point to the same file. The gate-template lives in one place (gate-plan owns it) and is referenced from two others.

### Constraint: no plugin-side state

If a future skill needs persistent state (e.g., storing gate history, caching review results), that state belongs in the workspace, not the plugin. The plugin ships methodology; the workspace holds operational data. This separation means the plugin can be updated, reinstalled, or shared across machines without losing domain state, and domain workspaces can be condensed or archived without affecting the plugin.
