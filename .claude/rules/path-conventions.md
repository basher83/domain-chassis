---
paths:
  - "**/domain-chassis/skills/**/*.md"
  - "**/domain-chassis/commands/**/*.md"
---

# Chassis skill path-reference conventions

When writing or editing a chassis `SKILL.md`, command, or skill reference file, every filepath that points the agent to **read** another file must use the right form — or it resolves against the wrong context and silently fails (it has shipped undetected through the full gate lifecycle more than once).

- **Same-skill files → bare relative.** A skill referencing its *own* `references/`, `scripts/`, etc. uses a relative path: `[references/foo.md](references/foo.md)`. Relative resolves within the owning skill's context.
- **Cross-boundary read pointers → `${CLAUDE_PLUGIN_ROOT}/…`.** ANY file the skill does **not** own — a *sibling skill's* file OR a *plugin-root* directory (`foundation/`, `adrs/`, `references/`, `hooks/`, `blueprints/`, `specs/`, `templates/`) — uses `${CLAUDE_PLUGIN_ROOT}/<path>`, **even for plain "see X" / "read X" navigation**. The absolute form resolves from any skill's context (repo and per-domain cache alike); a bare or `../`-relative path resolves against CWD or the wrong skill and fails.
  - Right: `` see `${CLAUDE_PLUGIN_ROOT}/foundation/EVIDENCE.md` ``
  - Wrong: `` see `foundation/EVIDENCE.md` `` · `` see `../../foundation/EVIDENCE.md` ``
- **Shell commands → `${CLAUDE_PLUGIN_ROOT}` for any executable**, since the shell resolves against CWD, not the skill root: `${CLAUDE_PLUGIN_ROOT}/skills/gate-review/scripts/check-citations.py`.
- The variable is **`${CLAUDE_PLUGIN_ROOT}`**. `${CLAUDE_PLUGIN_DIR}` does not exist; `${CLAUDE_SKILL_DIR}` is shell-only and different. Do not substitute.

A bare doctrine-name citation in prose (e.g. "the principle `EVIDENCE.md` describes") is not a read pointer and stays prose. The trigger is a path *served as a read pointer*: a `/`-containing path in a code span, a markdown link target, or a "see/read X" instruction.

Source of record: `README.md` → "File Operation Model" / "Why the asymmetry".
