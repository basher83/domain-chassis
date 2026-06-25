# ADR-004: Machine-Readable Gate Review Header in Frontmatter

**Status:** Accepted
**Date:** 2026-06-01T19:22:07Z
**Authors:** Brent, Claude
**Reviewers:** Brent

## Context

A gate document carries two different things in one `## Gate Review` section: an *append-only review log* — the FAIL → fix → re-review → PASS arc that is worth preserving in-file — and a *single current-state verdict* — the one signal gate-work's fail-closed detector reads to decide whether the gate may be entered for work and whether it may clear. Today both render as undifferentiated prose lines (`Reviewed:` / `Verdict:` / `Confidence:`) inside that one section, and the detector keys on the substring `## Gate Review` plus `Verdict: PASS`.

That conflation has a live failure mode. When a gate is re-reviewed, the section carries both a `Verdict: FAIL` block (the superseded first review) and a `Verdict: PASS` block (the operative re-review); a substring detector sees both and the fail-closed surface halts. `gates/Q59-gate.md` had to be hand-relabelled (`Verdict [first review — SUPERSEDED …]: FAIL`) to clear at all. The substring approach is also fragile in the other direction: `Verdict:` appears in gate *bodies* as comparison results (`Verdict: version_a` in Q14/Q15), quoted research findings (`Verdict: *"Supported (n=1)…"*` in Q58), and parentheticals (`Verdict: PASS (review waived…)` in Q46). A body-wide grep is structurally wrong; it keys clearance on text the author never meant as the review verdict.

### Research Foundation (provenance)

Surfaced at the Q59 re-review (2026-05-29): a FAIL→PASS dual-verdict gate trips the fail-closed detector. Recorded as QUEUE item Q61 and ruled at gate-plan/gate-work (2026-06-01). Same exit-code-as-verdict / AP-06 ethos as Q59's citation checker (`check-citations.py`), and the same "machine-readable field, not narratable prose" move as ADR-001's UTC-canonical timestamp primitive.

## Decision

Lift the gate's current-state review signal out of the `## Gate Review` prose and into a **YAML frontmatter block at the top of the gate file**. The frontmatter carries `verdict:` (and, per Phase 2, `reviewed:` and `confidence:`); it is the single machine-readable current-state the detector reads with a position-anchored read. The `## Gate Review` section is redefined as the pure append-only human narrative — the review log, where the FAIL→PASS arc lives unedited and may carry any number of prose `Verdict:` lines, none of which the detector reads. gate-plan authors a new gate with `verdict: pending`; gate-review overwrites the frontmatter to the current-state `pass`/`fail` while appending the narrative block; gate-work reads only the frontmatter field. A gate with no frontmatter `verdict:` key predates this contract and fails closed loud (instructing migration) — there is no body-grep fallback.

### Key Decision Factors

- Separation of signal from log: the current-state verdict (overwritten each review) and the append-only arc (appended each review) are different artifacts and now live in different places. This is the evidence/interpretation separation applied to the review signal.
- Position-anchored, not content-matched: the detector reads one key at one fixed position. It cannot be confused by a superseded verdict in the log, by a body comparison result, or by a quoted finding.
- Fail-closed and fix-forward: an absent field halts loud and routes to migration; no compatibility grep-shim is retained (consistent with the workspace's no-backward-compat stance).
- Structural separation by format: frontmatter is not prose, so a `verdict:` key can never be mistaken for narrative and narrative `Verdict:` lines can never be mistaken for the signal.

## Architecture Decisions Matrix

| Decision Point | Options Considered | Selected | Rationale |
|---|---|---|---|
| **Fixed-position carrier** | YAML frontmatter, a canonical top-of-file status line after the title | YAML frontmatter | A structurally distinct block (not prose) that cannot collide with body `Verdict:` tokens; standard, parseable, and unambiguous in position. A bare status line re-introduces a `Verdict:`-shaped line into the prose soup the contract is escaping. |
| **Detector read** | position-anchored frontmatter read, body-wide `Verdict:` grep, parse/sort of timestamped review blocks | position-anchored read | The fail-closed safety surface must stay dumb: one key, one position. Parsing/sorting review blocks puts log-interpretation logic on the clearance surface (the exact fragility being removed). |
| **Absent-field behavior** | loud fail-closed halt → migrate, silent grep-fallback to old format | loud halt → migrate | Fix-forward, no shim. A silent fallback would keep the broken substring path alive and mask unmigrated gates. |
| **`verdict` value set** | `pending`/`pass`/`fail`, `pass`/`fail` only | `pending`/`pass`/`fail` | `pending` distinguishes a planned-but-unreviewed gate (present field) from an old unmigrated gate (absent field); both correctly block entry/clearance, but only the latter routes to migration. |

## Technical Approach

The gate template's structure block leads with a frontmatter fence carrying `verdict: pending`; gate-plan reproduces it by following the template. gate-review's persisted-header step writes the frontmatter as the canonical current-state and appends the `## Gate Review` narrative. gate-work's entry gate and pre-clear detector perform a position-anchored read of `verdict:` from the frontmatter: `pass` → proceed/may-clear; `fail`/`pending` → halt (needs a passing review); key or block absent → loud halt instructing migration. The frontmatter sits before the `# Q{n} Gate:` title and before any `## ` heading, so the existing chassis parsers (`check-citations.py`, `check-inheritance.py`) — which key on the H1 title, the pre-`##` preamble, and `## ` sections — are unaffected. A deterministic checker (`check-review-header.py`) enforces that the frontmatter verdict matches the narrative's current verdict.

## Risk Assessment

### Migration boundary

1. **Pre-contract gates carry no frontmatter**
   - Description: Every gate authored before this contract lacks the frontmatter field; the new detector would halt loud on them.
   - Mitigation: A one-time migration backfills `verdict:` (from each gate's current narrative verdict) across the workshop `gates/` archive and any active root gate. Archived gates are already CLEARED, so the detector never re-reads them, but the field is backfilled so a future state-detection consumer reads uniformly.
   - Fallback: The loud halt itself is the prompt — any consuming domain that adopts the new chassis migrates its own active gates when the halt fires.

### Cross-domain adoption

2. **Other domains' active gates halt until migrated**
   - Description: A domain that refreshes its plugin cache to this chassis version, but has unmigrated active gates, will see the loud halt.
   - Mitigation: Intended behavior — fail-closed and loud, not silent. The halt names the fix (backfill the frontmatter from the narrative current verdict).
   - Fallback: None needed; the halt is the designed signal.

## Success Metrics

- A re-reviewed gate carrying a superseded `Verdict: FAIL` and an operative `Verdict: PASS` in its narrative clears without a hand-applied relabel, because the detector reads only the frontmatter.
- A gate whose body carries comparison/quoted/parenthetical `Verdict:` tokens does not clear on those tokens — only the frontmatter governs.
- An unmigrated (field-absent) gate halts loud and is not silently passed.

## Consequences

### Positive

- The fail-closed clearance surface is a single-position read, immune to the review log and to body `Verdict:` tokens.
- The review arc is preserved verbatim in `## Gate Review` without endangering clearance.
- The frontmatter is machine-parseable for a future lifecycle/hook state-detection consumer.

### Negative

- A one-time migration boundary exists; gates split into pre-frontmatter and frontmatter eras.
- Every new gate carries a frontmatter block it did not before (a small, standard addition).

### Neutral

- The existing citation/inheritance checkers are unaffected (frontmatter is before the title and any `## ` section).

## Alternatives Considered

A canonical top-of-file status line (a `Verdict:`-shaped line right after the title) — rejected: it re-introduces a prose `Verdict:` line into the very soup the contract escapes, trading one ambiguous-position read for another. A smarter detector that parses and sorts the timestamped review blocks to find the latest verdict — rejected: it puts log-interpretation logic on the fail-closed safety surface, which must stay dumb; that smartness belongs in the (non-blocking) consistency checker, not the clearance gate.

## Dependencies

- `skills/gate-plan/references/gate-template.md` — structure block + machine-readable-header convention.
- `skills/gate-review/SKILL.md` — writes the frontmatter as current-state; `## Gate Review` becomes append-only narrative.
- `skills/gate-work/SKILL.md` — entry gate and pre-clear detector read the frontmatter field.
- `skills/gate-review/scripts/check-review-header.py` — enforces frontmatter-matches-narrative (and, per ADR-005, the confidence/format invariants).

## Related Documents

- `adrs/ADR-001-utc-canonical-timestamps.md` — the UTC-canonical `_shared/now.mjs` primitive the `reviewed:` field uses (Phase 2).
- `adrs/ADR-005-confidence-enum-and-invariant.md` — the `confidence:` enum and the verdict↔confidence↔blocking-deficiency invariant (Phase 2).
- `references/anti-pattern-registry.md` — AP-06 (Narrative Escape), the failure mode the position-anchored read structurally forecloses.
