---
Project: Workshop
Type: Lifecycle Automation Architecture
Date: 2026-06-01
Status: Active
Revision: v2 — Phase 0 (Q66) cleared; Layer-2 judge calibrated to reasoning effort=off; Phases 1–4 authorized per Q69 revisit trigger
---

# B3 — Gate Loop as a Pi Extension

## What It Is

The gate loop is the chassis's validation lifecycle (plan → plan-review → work → work-review → CLEARED) made into an enforced, deterministic automation rather than a manual sequence of separately-launched Claude Code sessions. This blueprint commits to building it as a **Pi extension** — code that *is* the harness behavior — rather than as a Claude Code supervisor agent dispatching sub-agents.

The empirical basis is a single throughline. Three workshop projects — `the-range` (measure whether enforcement held), `skill-creator` (enforce a build workflow via hooks), `latent-space` (get determinism via the Agent SDK) — and the retired Q33 gate-orchestrator design are not independent efforts. They are successive attempts at one problem: **deterministic, enforceable agentic execution at the operator's hardening threshold.** Each got closer; each hit the same ceiling — Claude Code's leverage model, where you script *around* a harness that may or may not honor your directive (`context: fork` broken in plugins, AP-06 narrative escape, checkers that run "if the agent remembers"). Q33 was retired (2026-05-30) because hardening it on those leverage points could not reach the threshold, and its pieces were decomposed into standalone deterministic primitives (Q61 verdict determinism, Q63 citation-scope, Q65 checkers-as-hooks, Q66 cold-reviewer-as-script).

Pi changes the category. In Pi you build *on* the harness: an extension registers a synchronous pre-execution tool veto, holds state across turns, swaps models per call, and gates completion behind a check the model cannot route around. This is enforcement-by-construction, not enforcement-by-instruction. The blueprint's claim is that the gate loop is the **recomposition** of the decomposed Q33 primitives onto a platform that can finally enforce them.

The thesis is verified, not asserted. `forge/nanny-rs-via-pi-until-done/` is a Pi-`until-done`-driven port of a TypeScript CLI to Rust, confirmed on disk (HEAD `eb9ba58`) by running the gates independently: `mise run check` green (fmt + clippy `-D warnings` + 67 tests + release build), `mise run parity` 9/9 against an external black-box cross-binary oracle, structural constraints met (max source file 171 LOC, zero debug/TODO/clippy-disable residue), semantically-decomposed code. Zero AP-06 narrative-escape residue — the exact failure class CC could not suppress. Confidence in the Pi-leverage thesis is ~85%; the residual is additive design on a proven base, not platform risk (see Open Questions).

## What It Replaces

Today the gate lifecycle is manual and human-orchestrated. The operator launches a session, runs prime for domain context, then drives each stage as a separate session: triage assigns a Q-number; a plan session (prime + short context conversation) authors the gate; a fresh review session runs gate-review against the gate artifact and appends results; the operator reads the review and relays it to the planner, who addresses feedback (a second review follows on a severe failure); on PASS the operator launches a fresh build session; build clears the gate. Work-review (auditing whether the build's evidence proves its claims) is a stage the operator has intended to add but never has — because in the CC model it meant standing up yet another review session.

There is no enforcement of ordering, no automatic state detection, no structural guarantee that review runs in isolated context, no deterministic backpressure rejecting bad output before the lifecycle advances, and no enforced verdict-correctness — only verdict-existence.

| Before (CC, manual) | After (Pi extension) |
|---------------------|----------------------|
| Operator manually sequences plan → review → build across sessions | Extension enforces stage ordering; refuses to start a stage on a non-passing gate |
| Cold review achieved by launching a fresh session (the only CC isolation mechanism) | Cold judge is a `complete()` call handed only the artifact + criteria — isolated by construction |
| Verdict parsed as prose (`Verdict: PASS`), fragile (dual-verdict detector halt) | Verdict is a machine-readable field (Q61); `currentPhase()` is a deterministic fold |
| Backpressure verifies a verdict *exists and is shaped right*, never that it is *correct* | Two-layer gate: deterministic checkers (shape) + cold cross-model judge (correctness) |
| Work-review intended but never built (a whole extra session to stand up) | Work-review is the same judge mechanism fired at a second transition — nearly free |
| Operator reads every review and relays to planner | Operator is escalated on every FAIL; PASS flows to build-ready |
| Build context grows unbounded across a long execution | Build runs the until-done loop with boomerang context summarization |
| No structural guarantee the build agent can't write its own clearance | Status/verdict fields are phase-gated; only the judge-passed transition writes them |

## Design Inputs

| Source | Key Contribution |
|--------|-----------------|
| `gate-orchestrator-dev-working/` (Q33 corpus: plan, operator/planner/reviewer/worker/backpressure designs, 2026-02-27 review) | The pre-decomposition whole. Supplies the **state machine** (NO_GATE → plan → review → work → work-review → CLEARED) and the **BP-1..BP-6 enforcement-point taxonomy** — both carry over. Its *mechanisms* (double-loop supervisor agent, sub-agent dispatch, agent-scoped Stop hooks) are CC-shaped and superseded by this blueprint. |
| `upstream/pi-until-done` (read 2026-06-01) | The loop+judge engine. `tools/complete.ts:executeComplete` is the verdict gate: `decideJudge()` → `continue` verdict → `refuseCompletion` (model cannot mark done). `tools/judge.ts` builds the judge prompt from ONLY goal+doneCriteria+verifyCommand+evidence (cold by construction) and resolves a different model via `modelRegistry.find` (cross-model real). `store.ts` is event-sourced (`persist` appends, `reconstructFromSession` folds). `hooks/agent.ts:handleEndTransitions` is the outer loop with a zero-progress spin-guard (escalation cap). This is Q66's cold-reviewer mechanism already in production. |
| `upstream/pi-grill-me` (read 2026-06-01) | The phase-gated tool block. `index.ts:1003` — one `pi.on("tool_call", …)` returning `{block:true, reason}` is a synchronous pre-execution veto. `currentPhase()` is a pure function of state; transitions are tools that self-guard preconditions (`grill_enter_output_phase` refuses unless output-selection ran). Read-only classifier is allow-list/deny-by-default (fail-closed). Demonstrates the stage-skip hard-block the Q33 design only *asked for* in a prompt. |
| `forge/nanny-rs-via-pi-until-done/` (verified 2026-06-01) | Empirical proof: a Pi-until-done loop drove a non-trivial port to a clean, externally-verified, production-shaped result with zero narrative-escape residue. The evidence that Pi enforces by construction where CC could not. |
| `upstream/pi-boomerang` (read 2026-06-01) | Intra-stage context management: compactor (raw turns → structured handoff summary of changed files / reads / commands / failures), chainer, rethrow loop (N passes, summarize between, files persist on disk). Summary format ≈ the evidence record the work-review judge consumes. Session-tree-scoped — does NOT cross sessions, so it is intra-stage only. |
| Operator workflow (stated 2026-06-01) | Each stage is a separate session with its own prime → the gate file is the sole cross-session baton → file-as-truth is forced, not chosen. Forward edges human-stepped (operator launches build; wants that boundary stricter). HITL leverage is the FAIL. |
| FAIL-convergence invariant (operator, 2026-06-01; memory `project_gate-loop-fail-convergence`) | On a reviewer FAIL the operator checks exactly two spots: the reviewer's narrative and the planner's exclusions. The exclusions ARE the carve. Preserving this two-spot convergence is a hard design constraint; it gives the judge its FAIL-output spec and is the concrete reason Q67 (wire `Q{n}-why.md` into review) exists. |
| Q61 (gate-review header determinism) | Machine-readable `Verdict`/`Confidence` fields + the verdict↔confidence↔blocking-deficiency invariant. Makes `currentPhase()` a deterministic fold rather than prose-parsing, and supplies the "append-only review log vs single current-state verdict" separation that lets counters be derived from the file. |
| Q66 (cold-review as a bun Pi-SDK reviewer script) | The pilot. The smallest "gate primitive on Pi"; the empirical test of whether Pi clears the threshold against *fuzzy* criteria (vs nanny's deterministic byte-diff oracle). This blueprint is the parent; Q66 is its first proof-step. |
| B1 — Domain Chassis Architecture | The chassis artifact lifecycle and gate-file contract this loop reads/writes. B1 line 70 anticipates the orchestrator as a CC double-loop "downstream consumer … blocked on a stable B1"; this blueprint supersedes that mechanism while preserving the shared gate-file artifact contract. The dependency softens (a Pi extension reads the gate file rather than dispatching chassis skills as sub-agents) but does not vanish. |
| Memory `project_enforcement-determinism-throughline` | The full throughline, two-axis design vocabulary, and the gate-orchestrator-corpus dissolve/add/carry analysis this blueprint synthesizes. |

## Architecture

### Primitive 1 — `currentPhase()` as a deterministic fold over gate-file state

The extension is stateless across sessions. On load it reconstructs lifecycle position by folding the gate file — `reconstructFromGateFile`, the Pi analog of until-done's `reconstructFromSession`, except the source is the durable artifact, not session entries (see Primitive 4). The fold reads Q61's machine-readable fields, not prose:

```text
currentPhase(gate) →
  gate absent                                    → NO_GATE     (→ plan)
  gate in gates/  OR  status == CLEARED          → CLEARED     (terminal)
  review_verdict unset                           → UNREVIEWED  (→ plan-review)
  review_verdict == FAIL                         → PLAN_FAIL   (halt → operator)
  review_verdict == PASS && checkpoints_open > 0 → WORK        (→ build)
  checkpoints_open == 0 && work_verdict unset    → WORK_DONE   (→ work-review)
  work_verdict == FAIL                           → WORK_FAIL   (halt → operator)
  work_verdict == PASS && status != CLEARED      → WORK_PASS   (→ final clear)
```

Five inputs: file location, a status field, two verdict fields, a count of open checkpoints. No `## Gate Review`-section sniffing, no prose `Verdict: PASS` parsing — the fragility Q61 removes. This is the Q33 Decision-4 state detector, re-expressed over machine-readable fields.

### Primitive 2 — Two-layer gate at every transition

Each `→` edge is not one check. It is two layers in fail-fast order, the conscious synthesis of the Q33 deterministic-only stance and until-done's judge-centric stance — chosen because each catches what the other cannot:

```text
TRANSITION (e.g. WORK_DONE → WORK_PASS):
  Layer 1 — deterministic checkers (cheap, fail-closed, no model)
     Q59 citation checker, Q61 verdict↔confidence invariant,
     structural validations (every [x] has evidence; sections well-formed).
     ANY non-zero exit → BLOCK; no judge call.       ← this is the BP-1..BP-6 taxonomy,
                                                        relocated from Stop-hooks to a transition predicate
  Layer 2 — cold cross-model judge (only if Layer 1 passed)
     consultJudge(goal = checkpoint claims,
                  criteria = gate completion,
                  evidence = documented results + carve/exclusions).
     Sees ONLY the artifact. Verdict is STRUCTURED (not until-done's binary):
     PASS/FAIL + confidence + findings.
     FAIL → write verdict field = FAIL, halt to operator.
```

Layer 1 catches *malformed* (Q61's job, fast, free). Layer 2 catches *well-formed-but-wrong* — the gap the Q33 backpressure design explicitly conceded it could not close ("hooks verified format, not correctness"). Layer 1 cheap-fails before spending a judge call.

**Layer-2 judge operating point — reasoning effort=off (empirically calibrated, Q66 Phase 0).** The cold judge runs at reasoning effort **off**, not higher. This is counterintuitive (a "judge" intuitively wants deep reasoning) and was falsified by the Phase-0 pilot: across an effort sweep on a known-PASS well-carved artifact (`anthropic-proxy/claude-sonnet-4-6`, temp 0), effort=off returned PASS@4 deterministically (5/5), while low/medium/high each returned FAIL@3 — the smell-test probe **over-fires** under reasoning (the model reasons itself into "the near-term step could be the whole thing," ignoring the carve) and **flickers** run-to-run at the PASS/FAIL boundary even at temperature 0 (thinking models are not deterministic). Discrimination on genuinely-flawed artifacts held at *every* effort level (degraded artifact FAIL@1 throughout), so effort=off does not cost sensitivity — it removes false-FAIL noise on good artifacts. **Effort is therefore a calibrated floor, not a maximized knob.** Two coupled constraints follow: (1) the judge model defaults to the one faithful to the labels that defined the threshold (`anthropic-proxy/claude-sonnet-4-6`; Gemini over-fires and is off-target); (2) `temperature: 0` is set only when `!registry.isUsingOAuth(model)` — OAuth paths (Codex) HTTP-400 on a temperature parameter. This operating point is the load-bearing calibration the pilot produced; any future model swap re-opens it. Full recipe and gotchas: memory `project_q66-pi-reviewer-calibration`, `domain-chassis/adrs/ADR-002`.

This calibration also surfaced a probe-wording defect that bears on Primitive 3: the triage smell-test probe ("read the near-term step *alone* … is the narrowing silent?") is literally carve-blind — the carve is exactly what makes a narrowing non-silent. At effort=off the model applies it holistically and gets it right; under reasoning it applies the literal text and over-fires. The probe wording wants a carve-aware revision (deferred triage-skill refinement, ADR-002) — and it is the same carve-axis as Primitive 3 and Q67.

### Primitive 3 — The FAIL-convergence constraint binds the judge to the carve

The judge's FAIL output is not free-form. The operator's attention surface on a FAIL is exactly two spots: the reviewer's narrative and the planner's exclusions (the carve). This is a load-bearing invariant — scattering failure information across more places degrades operator leverage. Therefore:

- Layer 2's judge reads the gate's **exclusions** and the triage **`Q{n}-why.md` carve** as a first-class input (this is the consumer side of Q67).
- Every FAIL is structured as (a) narrative rationale + (b) a specific exclusion/carve assessment — landing in exactly the two spots the operator checks.

Triage-carve → gate-exclusions → reviewer-FAIL are one axis seen at three lifecycle points. This is why Q67 exists; the judge checking the carve is the mechanism that keeps the human attention surface bounded.

### Primitive 4 — File-as-truth; durability split

Because every stage is a separate session, the gate file is the only baton that crosses the boundary. Session-scoped stores (until-done entries, boomerang's session tree, grill-me state) evaporate at session end and cannot carry lifecycle state. Therefore state is split by durability requirement:

- **Gate file (authoritative, event-sourced *within the file*):** phase inputs, verdicts, checkpoint marks, the append-only review log, derived counters. The append-only verdict history lives as stacked review sections (Q61's review-log-vs-current-verdict separation); `currentPhase()` folds the latest current-state field; `review_attempts`/`work_review_attempts` are derived as `len(FAIL sections)`, never a mutable field that can drift. Human edits on FAIL *are* state changes with no desync — decisive, because FAIL is human-gated by design.
- **Pi session entries (ephemeral, within-run):** turns-this-run, the spin-guard zero-progress counter, dispatch attempts this session. Session-scoped by nature; correct that they evaporate on resume.

The cost accepted: the extension owns gate-file parse/write/concurrency logic instead of getting it free from `pi.appendEntry`. Mitigated because the gate file must be parsed anyway (it is the deliverable) and Q61 builds the machine-readable-field half of that parser. Concurrency surface is small and single-writer-per-phase, enforced by the phase gate itself.

### Primitive 5 — Per-stage execution model

The lifecycle stages are two kinds of thing:

- **Productive agentic stages (plan, build):** full agent sessions with tools and prime context, launched by the operator. **Build is until-done almost exactly** — checkpoints are the `goal`, "all checkpoints have evidence + work-review passes" is `doneCriteria`, the spin-guard + escape-hatch-to-operator are until-done's escalation, "I think I'm done" → work-review judge → PASS-clears/FAIL-continues is `until_done_complete`. Build runs the until-done loop **with boomerang** keeping its context lean across iterations; boomerang's handoff summary is the evidence the work-review judge reads.
- **Judgmental stages (plan-review, work-review):** NOT separate sessions. A cold judge `complete()` call fired at the transition, isolated by construction. This is why work-review becomes nearly free — the same judge mechanism at a second boundary, the thing the operator has long intended but the CC model made expensive.

### Primitive 6 — Forward human-stepped, backward auto-halts

Across stages the loop is **not** until-done's continuous auto-advance. PASS marks the gate ready and stops; the operator launches the next stage. The extension's forward-edge job is enforcement, not automation: refuse to start build on a non-passing gate, refuse to skip review, and enforce the stricter fresh-agent build boundary by refusing to enter build phase in the same session that authored the plan (detect via session identity). FAIL always auto-halts and escalates to the operator with findings (the existing "advise the planner" / "escape hatch when spiraling" moment, now surfaced by the extension). The continuous until-done loop lives *within* the build stage, not across stages.

### Primitive 7 — Phase-gated write protection (narrow grill-me application)

With review as a judge *call*, grill-me's BP-3 "constrain the reviewer's Edit to the gate file" apparatus dissolves (a judge call has no tools to gate). What survives is narrower: a grill-me-style `tool_call` block scoped tightly to the **machine-readable status/verdict fields**. The build agent legitimately mutates everything else, but must not be able to write `work_verdict: PASS` or `CLEARED` itself — only the extension writes those, after the judge passes.

## Phasing

Phase 0 cleared 2026-06-01 — the pilot's PASS authorizes Phases 1–4 (Q69 revisit trigger fired; operator authorized). The thesis held *with* a calibration: the Layer-2 judge runs at effort=off (Primitive 2). Phases 1–4 carry that constraint into the judge design.

| Phase | Gate | Scope | Depends On |
|-------|------|-------|------------|
| 0 (pilot) | Q66 ✅ CLEARED | Cold-review as a standalone bun Pi-SDK reviewer script (artifact-path-as-only-interface). Proved: mechanical argv-only boundary (byte-identical prompt under env/stdin injection); cross-model routing (3 providers); cold judge reaches the operator's fuzzy-criteria threshold **at effort=off** (load-bearing calibration). `gates/Q66-gate.md`, chassis 0.4.1, ADR-002. | — |
| 1 | Q__ | `currentPhase()` fold over gate-file state (Primitive 1) + file-as-truth read/write contract (Primitive 4). Reads Q61 fields. | Q61, Q66 |
| 2 | Q__ | Two-layer gate at the plan-review transition (Primitives 2, 3): Layer 1 wraps Q59/Q61 checkers; Layer 2 carve-aware judge consuming `Q{n}-why.md` (Q67). | Phase 1, Q67, Q63 |
| 3 | Q__ | Build stage as until-done + boomerang (Primitive 5); forward/backward edge enforcement (Primitive 6); phase-gated write protection (Primitive 7). | Phase 2 |
| 4 | Q__ | Work-review transition (the long-intended stage) — same judge at the second boundary; structured-verdict schema finalized. | Phase 3 |

## Scope Boundaries

### Excluded

- **CC-era mechanisms from the Q33 corpus.** The double-loop supervisor agent, sub-agent dispatch, agent-scoped Stop hooks, and the `.claude/gate-state.local.md` coordination file are superseded, not ported. Their *logic* (state machine, BP taxonomy) carries; their *mechanism* does not.
- **Cross-stage boomerang chaining.** Boomerang's `/scout -> /planner -> /impl` chaining auto-advances stages; this conflicts with human-stepped forward edges. Chaining is permitted *inside* a stage (e.g. build's scout→impl), never across the gate lifecycle.
- **Session-entries-as-authoritative-state.** Impossible given separate-session stages; the gate file is truth. Session entries hold only ephemeral within-run telemetry.
- **Layer-1-only or Layer-2-only enforcement.** The Q33 deterministic-only stance and a judge-only stance are both rejected in favor of the two-layer synthesis.

### Deferred

- **The Pi-everywhere-vs-fork decision (cross-domain blast radius).** The chassis serves all four domains, which run on Claude Code. A Pi-native gate loop forces a choice: other domains adopt Pi to get gates, or the chassis forks its "runs in any harness" property, or 3I commits to Pi-everywhere. This is a domain-level direction, adjacent to Q53 (which it pulls from "port chassis to Pi" toward "rebuild as native Pi"). Deferred to a named decision before Phase 3.
- **Structured-verdict schema.** until-done's judge is binary (`done`/`continue` + one sentence); gate-review needs a structured multi-finding report + confidence + PASS/FAIL. The schema (replacing until-done's `interpretJudge` parse) is deferred to Phase 2 design.
- **Gap 1 (post-CLEARED exit ordering)** and **Gap 2 (work-review as a real gate-review skill change)** from the 2026-02-27 Q33 review. Both are platform-independent carried-either-way work; deferred but not dropped. Gap 1: CLEARED must mean delivery is proven (order delivery → CLEARED → archive). Gap 2: `## Work Review` is a methodology change (mode parameter or separate skill), mis-scoped as out-of-scope in the Q33 plan.

## Open Questions

- [x] **Does Pi's enforcement reach the operator's threshold against fuzzy criteria? — RESOLVED YES (Q66, 2026-06-01), with a calibration.** The pilot proved the cold judge reaches the operator's fuzzy-criteria threshold — but only at reasoning **effort=off** (5/5 PASS@4 deterministic at off; FAIL@3 at low/medium/high, smell-test over-fire + run-to-run flicker). Discrimination on flawed artifacts held at every effort. The counter-hypothesis (threshold is a moving target, not the platform) is retired: the threshold was reachable, the lever was reasoning-effort, and the platform delivered. The ~15% residual collapses to the operating-point constraint now in Primitive 2. This is the authorization basis for Phases 1–4.
- [ ] **State-home final form.** Leaning file-as-truth with event-sourcing *within* the gate file (Primitive 4). Confirm against an actual multi-session build resume before locking — does folding the gate file reconstruct phase as cleanly as until-done's session-entry fold?
- [ ] **Structured-verdict schema.** What exact object does Layer 2 return, and how does it serialize into the gate file's review section such that `currentPhase()` reads it and a human reads the narrative? (Deferred to Phase 2.) **Now carries a fixed constraint from Q66:** the judge runs at effort=off, defaults to `anthropic-proxy/claude-sonnet-4-6`, and gates `temperature: 0` on `!isUsingOAuth` (Primitive 2). The schema design inherits this operating point; the open part is the verdict *object shape* and its gate-file serialization, not the model/effort/temp settings.
- [ ] **Carve-aware probe wording (new, from Q66).** The triage smell-test probe is literally carve-blind ("read the near-term step *alone* … is the narrowing silent?" — the carve is what makes it non-silent). Effort=off masks this (holistic reading); under reasoning it over-fires. A carve-aware rewrite is a deferred triage-skill refinement (ADR-002) and the same carve-axis as Primitive 3 / Q67. Does the Layer-2 judge prompt inherit the current (ambiguous) probe text or a carve-aware revision? Resolve at Phase 2 judge design.
- [ ] **Pi-everywhere-vs-fork.** The cross-domain blast-radius decision (deferred above). Until resolved, is the gate loop a Workshop-only tool or a chassis-distributed one? This determines whether B3 stays a chassis blueprint or becomes a Workshop-domain artifact.
- [ ] **B1 dependency status.** B1 is `Draft` with open TODOs (reference graph, skill-interaction map, findings-separation, artifact-lifecycle). The Pi recomposition softens the coupling (reads the gate-file contract, does not dispatch chassis skills as sub-agents) but the shared gate-file artifact contract still depends on B1's artifact-lifecycle section stabilizing. Confirm the specific B1 sections this blueprint depends on, and whether they are stable enough to proceed to Phase 1.
- [ ] **Strict build-boundary detection.** Primitive 6 enforces "build cannot run in the plan-authoring session" via session identity. Confirm Pi exposes a stable session identifier an extension can read to make this mechanical rather than conventional.
- [ ] **Forward-edge on PASS — auto-ready vs pause-for-ack.** Resolved for now: PASS flows to build-ready (HITL leverage is the FAIL, per the convergence invariant). Recorded as a question because it is the operator-interaction trade and may revisit if PASS-without-eyeball proves uncomfortable in practice.
- [ ] **Candidate primitive — star-wise orientation distribution (prime-once, inherit down).** Every phase already begins with the prime skill today (operator's manual workflow), re-executed per session — so this is NOT new lifecycle surface; the extension *absorbs* an existing per-phase step and removes its redundancy (prime once, distribute, instead of N re-primes). **Hard constraint — star, not chain:** there are two context layers. *Orientation* (doctrine/PIN/QUEUE/project state/quality bar — what prime loads) is shared, stable, non-contaminating, and every phase wants it. *Authoring* (plan rationale, triage elicitation, the conversation that produced the artifact) is the contaminating layer the cold reviewer must never see and the fresh-build boundary must exclude. The fork must distribute ONLY orientation: every phase forks from the *clean-primed parent snapshot* (star), never from a prior phase's accumulated context (chain) — a chain re-contaminates review and build. This is VCI (workshop-polish ADR-001) formalized through the extension, with prime as the existing safe-landing-zone for CWD-dependent content. **Does NOT replace the gate file:** orientation flows by fork (clean-parent → all phases); work product flows by gate file (each phase reads/writes the artifact) — two channels, and review staying blind to authoring is exactly what keeps it cold. **Open sub-decision — freshness vs dedup:** today's manual per-phase re-prime silently gets *current* state every time; a frozen snapshot maximizes dedup but risks staleness across a long/multi-session lifecycle (a re-review days later). Likely hybrid: fork within a single continuous run, re-prime at session-resume boundaries — preserves today's freshness while deduping within a session. Fold into the Architecture section as a primitive when the pilot lands; the star-topology constraint and the freshness decision are the load-bearing parts.

## Revision History

- **v1 (2026-06-01):** Initial capture. Pi-native recomposition of the retired Q33 gate-orchestrator, synthesized from a session that verified the Pi-leverage thesis (nanny port), read all three Pi primitive extensions (until-done, grill-me, boomerang) in code, and analyzed the Q33 corpus for dissolve/add/carry. Status Draft — pilot (Q66) not yet run, six open questions, structured-verdict schema and Pi-everywhere decision deferred.
- **v2 (2026-06-01):** Phase 0 (Q66) cleared and independently spot-verified (mechanical argv-only boundary re-run: byte-identical prompt under env/stdin injection). Status Draft → **Active**. Load-bearing unknown resolved YES with a calibration: Layer-2 judge runs at reasoning **effort=off** (Primitive 2 amended with the effort sweep + determinism data, model default, and the OAuth/temperature gate). Phases 1–4 **authorized** per Q69's revisit trigger (operator, 2026-06-01), carrying the effort=off constraint into the judge design. New open question added (carve-aware probe wording, from the Q66 smell-test over-fire). Sources: AAR `workshop-polish/aar/2026-06-01-domain-chassis-q66-triage-cold-reviewer.{md,evidence.md}`, ADR-002, memory `project_q66-pi-reviewer-calibration`.
