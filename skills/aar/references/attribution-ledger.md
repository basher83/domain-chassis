# Gate-Verdict Calibration & Requirement Attribution — Ledger Convention

Reference for the reflective measurement loop the AAR emits when it reviews a closed gate. Two measurements per gate-closure AAR — **verdict-calibration** (was `gate-review`'s predicted verdict borne out by the lived `gate-work` outcome?) and **requirement-attribution** (which quality-bar requirements were load-bearing on this gate?) — accumulate so the quality bar can eventually be pruned with evidence rather than only grown.

The loop has three parts and a strict source-vs-derived split:

- **Source of truth** — a per-gate **attribution table**, written by the AAR into its own interpretation artifact (the `.md`, never the `.evidence.md`). Interpretation-at-origin.
- **Derived projection** — a cross-gate **snapshot** (`ledger-*.tsv`), produced *only* by `scripts/ledger.py derive` reading the AAR tables. Never hand-edited. Regenerable, so it cannot drift from its source.
- **Consumer** — `scripts/ledger.py prune-review` reads the latest snapshot and surfaces a requirement as a prune candidate when its inert streak meets a threshold.

## Why a derived projection (placement against `${CLAUDE_PLUGIN_ROOT}/foundation/EVIDENCE.md`)

The per-gate calibration and attribution are **interpretation** — judgments about what a gate's outcome means for the bar. They live in the AAR interpretation artifact, at origin, exactly where `EVIDENCE.md` says interpretation lives. They are never written to the `.evidence.md` record.

The cross-gate snapshot is a **derived projection** of those interpretation tables — not an evidence artifact, not the session-scoped operational ledger `EVIDENCE.md` describes (which archives or dies when its work completes), and **not a new hand-maintained standing accumulator**. Because it is regenerated mechanically from the tables, it cannot accumulate false authority: there is no second source of truth to drift. This matters because the loop's purpose is to feed a *doctrine change* (pruning the bar) from accumulated single-gate observations — precisely the AP-12 (Doctrinal Echo) conflation shape `EVIDENCE.md` was born from. Two structural guards keep it off that fault line: per-entry **anchoring** travels from the table into the snapshot (every classification points at a checkable locus), and the prune signal requires an **inert streak** (a single gate's observation never licenses a prune on its own).

## When the emission fires (conditional — AP-12)

Only for **gate-closure AARs**: an AAR reviewing a gate that went through `gate-review` (so there is a predicted verdict to score) and reached a lived outcome (CLEARED, with any errata / re-reviews). AARs of non-gate work, or of work with no `gate-review` verdict, emit nothing here and are unchanged. The measurement is not universalized onto every retrospective the chassis serves across the four domains.

## Self-authored vs cold attribution (the A4 decision)

Per-gate attribution is **self-authored by the AAR agent**, made safe by structural falsifiability rather than a heavier cold pass:

1. Every non-`indeterminate` classification is **locus-anchored** to a checkable artifact (a gate checkpoint ID, a `gate-work` event, an errata entry, an AAR finding). A reader can verify the citation; the agent cannot narrate "requirement X helped" without pointing at where.
2. `indeterminate` is a permitted honest classification, so the agent is never pressured to manufacture a verdict (AP-06).

The heavier guard — cold/independent re-scrutiny — is reserved for the **prune decision** at pruning-review time, where the irreversible doctrine change actually happens, not imposed on every routine AAR. Structural guard at the routine measurement, process guard at the irreversible action. (Calibration is artifact-grounded — predicted header vs lived outcome — so it carries low AP-06 exposure and needs no cold treatment.)

## Home and scope (committed, per-domain)

The attribution tables live inside the AARs in the domain knowledge repo (e.g. `workshop-polish/aar/`). The derived snapshots are **committed** to that same repo (a dated series of projections is real provenance, and because they are derived they cannot drift even in git). Nothing is written into the read-only plugin.

Projection scope is **per-domain**: `derive` reads one domain's AAR tables and emits a domain-local snapshot. The chassis quality bar is shared across domains, so a prune decision wants evidence from more than one domain — the operator integrates across domains' snapshots at pruning time, and a prune is never taken on one domain's partial view. Aggregating across domains into a single cross-domain projection is a clean future extension (`derive` over multiple repos) and is deliberately not built here.

## Attribution table schema (source, in the AAR `.md`)

The AAR writes one block per closed gate, fenced by machine-readable markers so `ledger.py derive` can extract it deterministically:

```markdown
## Gate-Verdict Calibration & Requirement Attribution

<!-- ledger:begin gate=Q72 date=2026-05-30 -->

**Calibration.** Predicted: `pass` @ confidence 4 (reviewed 2026-05-29T..Z). Lived: CLEARED, 1 errata, 0 re-reviews. Verdict-calibration: **accurate** — predicted pass and the gate cleared without a review-reversal; the one errata was a doc-nit, not a missed blocking deficiency.

| requirement_key | requirement | source | classification | locus |
|-----------------|-------------|--------|----------------|-------|
| GR-Q02 | every verification method yields a positive artifact | gate-review Q2 | load-bearing | errata: caught a negative-proof method in D3 pre-clear |
| GP-coverage-matrix | multi-vector coverage matrix | gate-plan | absent-but-needed | gate was single-vector; matrix N/A but inert here |

<!-- ledger:end -->
```

Fields per row: `requirement_key` (stable key from the registry below), `requirement` (short description), `source` (`gate-plan` or `gate-review Qn`), `classification` (the taxonomy below), `locus` (the checkable anchor; `—` only when classification is `indeterminate`).

`date` in the begin marker is the gate's clearance date (used to order the inert streak). One block per gate; an AAR spanning multiple gate closures writes one block each.

## Classification taxonomy

- `load-bearing` — the requirement caught or shaped something real on this gate (anchored to where).
- `inert` — the requirement applied but changed nothing; the gate would have been identical without it (anchored to the checkpoint/section that shows it idle).
- `absent-but-needed` — a gap the bar does not cover that bit this gate (anchored to the failure/errata).
- `indeterminate` — the evidence does not support a classification; no manufactured verdict (locus `—`).

**Streak semantics:** only `inert` advances a requirement's prune-streak. Any non-`inert` value, **including `indeterminate`**, breaks the streak. Ambiguous evidence is conservative: it never advances a prune.

## Snapshot schema (derived projection, TSV)

`ledger.py derive` emits tab-separated long-format — one row per (requirement_key, gate), stably sorted, so the same tables always produce a byte-identical body:

```text
# ledger-snapshot	derived=2026-06-02T23:50:00Z	scope=workshop	gates=12	rows=86
requirement_key	gate_id	gate_date	classification	locus
GP-coverage-matrix	Q72	2026-05-30	absent-but-needed	gate was single-vector; matrix N/A
GR-Q02	Q72	2026-05-30	load-bearing	errata: caught a negative-proof method in D3
```

Only the `derived=` field in the header comment varies between two runs over identical input — everything below it is deterministic. (This is what `L3` proves and the operator can re-confirm any time by re-deriving.)

## Requirement-key registry (v0)

The attribution target: the current `gate-plan` quality requirements (`GP-*`) and `gate-review` self-assessment questions (`GR-Qnn`). Stable keys let the projection track a requirement across gates as the bar evolves. **This registry is maintained as the bar changes** — a new requirement gets a new key; a requirement the pruning review removes is struck here (with a pointer to the snapshot that justified it). Keys are never reused.

| key | requirement | source |
|-----|-------------|--------|
| GP-claimable | completion criteria are concrete and claimable | gate-plan |
| GP-positive-artifact | every verification method produces a positive artifact | gate-plan |
| GP-category | every checkpoint tagged structural/operational | gate-plan |
| GP-exercises | verification exercises what it claims to validate | gate-plan |
| GP-ordering | ordering dependencies are explicit | gate-plan |
| GP-outcomes-not-tools | specifies outcomes, not tool sequences | gate-plan |
| GP-bypass-justified | bypasses carry inline justification | gate-plan |
| GP-cleanup | cleanup expectations documented | gate-plan |
| GP-excluded | out-of-scope items named in Excluded | gate-plan |
| GP-coverage-matrix | multi-vector coverage matrix (when applicable) | gate-plan |
| GP-operator-terminal | operator-terminal tags carry a named constraint | gate-plan |
| GP-delivery | cross-domain delivery checkpoint (when applicable) | gate-plan |
| GP-decision-legend | decision-token legend (when tokens cited) | gate-plan |
| GP-inheritance | predecessor-gate inheritance (when reused) | gate-plan |
| GP-ap-tags | checkpoints tag the anti-patterns they guard | gate-plan |
| GR-Q01 | clearing all checkpoints justifies the completion criteria | gate-review |
| GR-Q02 | every verification method is a positive, observable proof | gate-review |
| GR-Q03 | ordering dependencies documented | gate-review |
| GR-Q04 | executable top-to-bottom without operator clarification | gate-review |
| GR-Q05 | checkpoint granularity appropriate | gate-review |
| GR-Q06 | operational checkpoints verify first-iteration readiness | gate-review |
| GR-Q07 | coverage matrix with zero empty cells (when applicable) | gate-review |
| GR-Q08 | consumer-reachability checkpoint or scoped-out (when applicable) | gate-review |
| GR-Q09 | operator-terminal tags carry a stated constraint | gate-review |
| GR-Q10 | relevant anti-patterns covered/tagged | gate-review |
| GR-Q11 | no checkpoint prescribes a tool sequence | gate-review |
| GR-Q12 | decision-token legend resolves + checker green (when cited) | gate-review |
| GR-Q13 | predecessor inheritance section + checker green (when reused) | gate-review |
