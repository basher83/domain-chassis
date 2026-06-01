# ADR-005: Gate-Review Confidence Enum and the Verdict↔Confidence Invariant

**Status:** Proposed
**Date:** 2026-06-01T19:40:11Z
**Authors:** Brent, Claude
**Reviewers:** Brent

## Context

ADR-004 lifted a gate's current-state review signal into frontmatter. This ADR fixes the format and the cross-field rule of the two remaining header fields, `reviewed` and `confidence`, so the whole reviewer header is machine-checkable rather than soft prose an agent narrates.

`confidence` today is free prose — `Confidence: 4/5`, but also legacy `high` (Q15/Q46 comparison gates) and even `5/5` despite gate-review's own scale declaring 5 unreachable. gate-review already encodes a binding in prose: a verdict is PASS only at confidence 4 with no blocking deficiency, and FAIL at confidence ≤3 or when a blocking deficiency exists. Nothing enforces it, so a `Verdict: PASS` next to `Confidence: 3/5` — a self-contradicting header — passes review unremarked. `reviewed` is likewise free-form, ranging from bare local dates (`2026-03-10`) to UTC-canonical `Z` stamps.

### Research Foundation (provenance)

QUEUE item Q61, Phase 2; ruled at gate-plan/gate-work 2026-06-01. Same exit-code-as-verdict ethos as Q59's `check-citations.py` and ADR-004's verdict field. The `reviewed` basis is the prior decision ADR-001 (UTC-canonical `_shared/now.mjs`).

## Decision

Make `confidence` a frontmatter enum — a bare integer 1–4 (5 is unreachable per gate-review's scale; `high`/`n/5`/`5` are rejected). Enforce the binding deterministically as `verdict ⟺ confidence`: `verdict: pass` iff `confidence == 4`; `verdict: fail` iff `confidence ∈ {1,2,3}`. The blocking-deficiency clause of gate-review's rule is carried by the confidence semantics, not by a separate text scan: gate-review's scale defines confidence 4 as "minor findings only" (no blocking deficiency) and 1–2 as the blocking-deficiency band, so binding the verdict to the confidence value *transitively* enforces "PASS iff no blocking deficiency" and "FAIL iff a blocking deficiency exists." `reviewed` is a UTC-canonical `Z` timestamp per ADR-001, sourced from `_shared/now.mjs`; a bare date, a numeric `+0000`/`+00:00` offset, or a local-basis value is rejected. The deterministic checker `check-review-header.py` enforces all three (enum, invariant, `Z` format).

### Key Decision Factors

- The named contradiction is caught structurally: `verdict: pass` + `confidence: 3` is RED by the invariant, with no agent judgment.
- The blocking-deficiency rule is enforced without a fragile narrative scan. A regex hunting the words "blocking deficiency" would false-positive on "No blocking deficiencies" and, worse, would put narrative interpretation back on the enforcement surface — the very AP-06 (Narrative Escape) risk this header design removes. Confidence is the machine-readable carrier gate-review already populates from that judgment.
- One basis for timestamps: `reviewed` reuses ADR-001's UTC-canonical `Z` rather than inventing a second time convention.

## Architecture Decisions Matrix

| Decision Point | Options Considered | Selected | Rationale |
|---|---|---|---|
| **Confidence range** | enum 1–4, enum 1–5, free `n/5` prose | enum 1–4 | 5 is unreachable per gate-review's scale; a bare 1–4 integer is machine-checkable and drops the legacy `/5` and `high` forms. |
| **Invariant enforcement** | `verdict ⟺ confidence` binding, a separate narrative scan for "blocking deficiency", a `blocking:` frontmatter field | `verdict ⟺ confidence` | Confidence already encodes the blocking-deficiency state (4 = none, 1–2 = blocking) per gate-review's scale, so the binding captures the whole invariant deterministically. A narrative scan re-introduces the AP-06 risk; a 4th field adds surface the three-field header was scoped to avoid. |
| **Reviewed basis** | UTC-canonical `Z` (ADR-001), bare date, numeric offset | UTC-canonical `Z` | Host-independent and unambiguous; reuses the existing `now.mjs` primitive rather than a second convention (ADR-001). |

## Technical Approach

gate-review's persisted-header step writes frontmatter `confidence:` as a bare 1–4 integer and `reviewed:` as a `now.mjs` `Z` stamp, alongside the `verdict:` field of ADR-004. `check-review-header.py` validates: `confidence` matches `^[1-4]$`; the `verdict ⟺ confidence` invariant; and `reviewed` matches `^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$`. Each check is conditional on its field being present, so a Phase-1-migrated gate carrying only `verdict` is not retroactively required to gain the Phase-2 fields. The checks are run at gate-review authoring and as a verdict input; promotion to an enforcement hook is Q65's scope.

## Risk Assessment

### Confidence mis-rating

1. **A confidence 4 asserted over a real blocking deficiency**
   - Description: The transitive design enforces the invariant *given* an honest confidence rating. An author who rates confidence 4 while a blocking deficiency genuinely exists defeats it.
   - Mitigation: That is a confidence-rating error, not a header-consistency error; detecting it requires judging whether a finding is a blocking deficiency, which is not deterministic. gate-review's classification-binding rule and the human review own that judgment.
   - Fallback: None at the checker layer by design — the alternative (a narrative scan) is the AP-06 risk the header design removes.

### Legacy headers

2. **Sealed archived gates carry `high` / `n/5` confidence and bare-date reviewed**
   - Description: Pre-contract gates do not satisfy the enum/`Z` forms.
   - Mitigation: The Phase-2 fields are conditional; sealed historical `reviewed`/`confidence` values are not re-stamped (re-deriving a UTC instant from a sealed local date would fabricate provenance). Only the load-bearing `verdict` field was backfilled (ADR-004 migration).
   - Fallback: New reviews emit the enum and `Z` forms going forward.

## Success Metrics

- `Verdict: PASS` + `Confidence: 3` is RED without agent judgment.
- `Confidence: 5/5` and `Confidence: high` are RED (non-enum).
- `Reviewed: 2026-03-10` and `…+0000` are RED; `…Z` is GREEN.

## Consequences

### Positive

- The whole reviewer header is machine-checkable; a self-contradicting header cannot pass review silently.
- No second time convention and no narrative-scan enforcement surface.

### Negative

- The transitive design does not catch a confidence value mis-rated against a real blocking deficiency (a judgment the human review retains).

### Neutral

- Phase-2 field checks are conditional, so Phase-1-only gates are unaffected.

## Alternatives Considered

A `blocking:` boolean frontmatter field to make the blocking clause explicit — rejected: it adds a fourth header field beyond the scoped three, and the value is still author-asserted, so it buys determinism the confidence enum already provides. A narrative scan for "blocking deficiency" wording — rejected: false-positives on "No blocking deficiencies" and re-introduces narrative interpretation on the enforcement surface (AP-06).

## Dependencies

- `adrs/ADR-001-utc-canonical-timestamps.md` — the `reviewed` field's UTC-canonical `Z` basis and the `_shared/now.mjs` primitive.
- `adrs/ADR-004-machine-readable-review-header.md` — the frontmatter container and the `verdict` field this invariant binds to.
- `skills/gate-plan/references/gate-template.md` — documents the `reviewed`/`confidence` conventions.
- `skills/gate-review/SKILL.md` — emits the enum and `Z` forms.
- `skills/gate-review/scripts/check-review-header.py` — enforces enum, invariant, and `Z` format.

## Related Documents

- `references/anti-pattern-registry.md` — AP-06 (Narrative Escape), the reason the blocking clause rides the confidence enum rather than a text scan.
