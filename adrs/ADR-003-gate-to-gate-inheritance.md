# ADR-003: Gate-to-Gate Inheritance — a `Builds on:` field, gate-plan inlining, and a presence checker

**Status:** Accepted
**Date:** 2026-06-01T06:10:43Z
**Authors:** Brent, Claude
**Reviewers:** Brent

## Context

The chassis gate lifecycle is `plan → review → work`. `gate-work` loads exactly one file — the current gate — and its framing states the gate file is a self-contained contract (Step 2.3: "the gate file is self-contained"). Nothing makes `gate-work` load a *predecessor* gate that the current gate builds on. So when a gate reuses a prior gate's load-bearing semantics — its runtime, fixtures, contracts, or baseline numbers — those semantics must be hand-carried into the current gate, or a cold executor (a fresh session, or a resume that never saw the authoring conversation) is blind to them.

This surfaced concretely on Q70. Q70 reused Q66's Pi-SDK runtime, its cold-strip fixture technique, its degraded-fixture shape, and its over-fire baseline numbers. Q70's author had to hand-carry those into Q70's Operating Model (a "Inherited from Q66 — required reading" constraint) and a new Phase 0 preflight — caught by author diligence, not by any lifecycle mechanism. Tellingly, Q70's own `Depends on:` line reads "None": Q70 does not *block* on Q66 (Q66 is cleared), it *inherits* from it. The blocking relation and the inheritance relation are different relations, and the existing `Depends on:` field encodes only the first.

This ADR records the decision (queue item Q71) on how a predecessor gate's load-bearing semantics reach a cold `gate-work` executor.

## Decision

Close the gap with a **(b) + (c) hybrid keyed off a distinct field**, not by changing `gate-work`:

- **A distinct `Builds on:` field** (a.k.a. `Inherits from:`) in the gate template, separate from the blocking `Depends on:`. It names the predecessor gate(s) whose load-bearing semantics the current gate reuses, and defaults to "None". The signal is this new field, **not** `Depends on:` — because the motivating fact is that Q70's `Depends on:` reads "None" while it reuses Q66, so a mechanism keyed off `Depends on:` would miss the very case that motivates this work.
- **(b) gate-plan inlining.** When a queue item reuses a predecessor gate's load-bearing semantics, the author sets `Builds on:` and transcribes the load-bearing *fraction* — not the whole predecessor — into an `## Inherited from {predecessor}` section. This keeps `gate-work`'s one-file self-contained contract intact: the inherited context travels inside the single file `gate-work` already loads.
- **(c) a presence checker.** A deterministic `check-inheritance.py`, co-located with `check-citations.py` and following its exit-code-as-verdict contract, flags a gate that declares `Builds on: <predecessor>` but lacks a matching `## Inherited from <predecessor>` section. It is wired into gate-plan (authoring self-check) and gate-review (verdict input), in parity with the citation checker.

`gate-work` is **not** changed. The single-file premise it is built on is preserved and that non-change is verified, not assumed.

### Rejected alternative — (a) auto-load predecessors

`gate-work` reads and loads predecessor gates named in a `Depends-on`/`Builds-on` line. Rejected for three grounded reasons:

1. **It contradicts `gate-work`'s single-file premise.** The executor is built to load exactly one self-contained contract; auto-loading other files changes that contract surface and the blast radius reaches the executor itself.
2. **It incurs transitive-loading, archive-boundary-crossing, and context cost when only a fraction is load-bearing.** A predecessor may have its own predecessors (where does transitive loading stop?), cleared predecessors live in `gates/` (resolution must cross the archive boundary), and only a fraction of a predecessor is ever relevant — Q70 needed Q66's runtime/fixtures/baselines, not all of Q66.
3. **It does not even recover the motivating case.** Q66's degraded fixture (`analytics-dashboard`) had been cleaned up per Q66's own Cleanup and no longer exists on disk; Q70 had to *transcribe* its shape, not load it. An auto-loader pointed at Q66 would not surface a fact that Q66 no longer carries. Transcription at authoring time is what actually carries the load-bearing fraction forward.

### Q67 boundary — Q71 stays a separate point fix

Q67 wires the frozen *why-record* (intent) into gate-plan/gate-review; this work wires predecessor-*gate* context into the gate document gate-work loads. Per `Q71-why.md`'s revisit trigger, the chosen shape was checked against Q67 and the ruling is that **Q71 ships as a separate point fix, not merged with Q67.** The two share a meta-pattern — *a lifecycle stage consumes a named durable upstream artifact* (Q67: a why-record; Q71: a predecessor gate) — and that shared pattern is recorded here so that a **third** instance can decide whether to generalize into one mechanism. Two instances is a coincidence to note, not yet a generalization to build.

### The checker's honest limit

`check-inheritance.py` enforces `Inherited from {predecessor}` section **presence and predecessor-name match** against the declared `Builds on:` field. It does **not** judge transcription *completeness* or *correctness* — whether the section actually carries the right load-bearing fraction remains human gate-review's job. This is the same presence-not-faithfulness limit the citation checker carries (it resolves pointers and catches gross title mismatch, but does not adjudicate semantic faithfulness of a paraphrase), and the checker is layered behind human review the same way.

## Scope

This ADR and the mechanism it records cover **gate-to-gate inheritance only** — a successor gate reaching a predecessor gate's load-bearing semantics. It is not a general "every lifecycle stage reads every named durable upstream artifact" mechanism (why-records, predecessor gates, source ADRs, commons); that generalization is explicitly deferred to a possible future third instance (see the Q67 boundary above). It does not change `gate-work`, and it does not retroactively migrate the cleared `gates/` archive to the new convention. Scope is named explicitly so the convention is not read as universal chassis doctrine that echoes unconditionally through every domain's lifecycle (AP-12).

## Consequences

- **Gates that build on a predecessor become self-contained for a cold executor** without changing `gate-work`: the load-bearing fraction is transcribed into the one file the executor already loads, enforced by a checker rather than left to author diligence (the AP-06 durable-artifact-over-ambient-context move).
- **A new authoring obligation.** gate-plan authors must recognize an inheritance relation, set `Builds on:`, and transcribe the fraction. The presence checker catches a declared-but-missing section; it cannot catch a *missing declaration* (a gate that should set `Builds on:` but does not) — that remains a human-judgment gap, the same residual the citation checker leaves for prose-only citations.
- **Transcription can drift.** An inlined copy of a predecessor's semantics can go stale if the predecessor changes. For cleared predecessors (the common case — a gate builds on something already done) the predecessor is frozen in `gates/`, so drift risk is low; the alternative (a) auto-load would avoid drift but was rejected for the reasons above.
- **The checker runs at instruction level** — invoked by gate-plan (self-check) and gate-review (verdict input), exactly as `check-citations.py` does today. Promotion to an enforcement hook at the user-message gradient (so nothing relies on an agent remembering to run it) is **Q65's** scope, not this work's.
- **`Depends on:` and `Builds on:` are now distinct relations** in the template. A gate may carry both, either, or neither; they are not redundant (Q70 → Q66 is `Builds on` with `Depends on: None`).
