# Anti-Pattern Registry

**Domain:** Workshop — serves all domains
**Date:** 2026-03-05
**Status:** Active, append-friendly

Implements Range design principle 16: "Named anti-patterns are avoided more reliably than described pitfalls." And principle 21: "Ground specs against operations, not just design inputs" — operational grounding is the discovery mechanism that feeds this registry.

---

## Registry

### AP-01: The False Regression

Environment failure reported as artifact failure. The vault API is down, the scenario fails, the operator thinks the skill regressed. Pre-eval contracts exist to prevent this — but only if someone writes the contract. Every external dependency in a scenario needs a contract, or this will recur.

**Scope:** Range evaluation
**Detection:** Scenario fails while pre-eval contracts are absent or incomplete for external dependencies.
**Prevention:** Every external dependency in a scenario gets a contract. No exceptions.
**Provenance:** Range design spec v13, synthesized from operational experience with external service dependencies.

---

### AP-02: The Rubber Stamp

The Tier 2 grader passes everything. The grader prompt is too permissive, the evidence threshold too low, or the judgment anchors too vague. Result: 100% pass rate that means nothing.

**Scope:** Range evaluation
**Detection:** Grader agrees with all vanilla results. If vanilla passes everything, the grader adds no signal.
**Prevention:** Calibration notes specifying failure examples. `not_observed` as distinct from `pass`. Close the helpfulness inference path in grader prompts.
**Provenance:** Range design spec v13, informed by LLM-as-judge research (Eugene Yan) and operational grader tuning.

---

### AP-03: The Perpetual Iteration

Artifact improvement past the point of economic value. The skill passes 5/6 anchors. Ten iterations later, 5.5/6. Twenty iterations later, 5.8/6. Each iteration costs grader invocations and operator attention. The delta improvement is real but the cost exceeds the benefit.

**Scope:** Range evaluation, broadly applicable to any iterative improvement loop
**Detection:** Convergence signaling — diminishing delta improvements across consecutive runs.
**Prevention:** Operator-defined "good enough" threshold per scenario. Cost accounting (Tier 2 grader cost per run, cumulative).
**Provenance:** Range design spec v13, empirically grounded in the 69-audit OAuth proxy deployment (Ralph Wiggum Technique Case Study, Forge 2026-02-06).

---

### AP-04: The Friendly Fire

A composition scenario where Artifact A's hook blocks a legitimate action by Artifact B. Overzealous enforcement degrading a collaborator. The inverse of a security boundary violation — here the boundary holds too tightly.

**Scope:** Range composition testing, broadly applicable to multi-artifact systems
**Detection:** Composition regression anchors that check for cooperative degradation — behaviors that pass in isolation but fail when stacked.
**Prevention:** Composition scenarios must include anchors for collaborative function, not just individual correctness.
**Provenance:** Range design spec v13, derived from CC harness hook aggregation model (deny > ask > allow precedence).

---

### AP-05: The Ghost Anchor

An anchor that never fires because the scenario instruction doesn't elicit the behavior it measures. The anchor exists, but the scenario doesn't create conditions for it. Result: permanent `not_observed`, mistaken for `pass` if the operator doesn't check.

**Scope:** Range evaluation
**Detection:** Any anchor with `not_observed` across all runs is suspect.
**Prevention:** Scenario authors must verify each anchor has a plausible trigger in the instruction.
**Provenance:** Range design spec v13.

---

### AP-06: The Narrative Escape

The agent produces output that satisfies Tier 2 judgment anchors without genuine behavioral improvement — learned to talk like the right answer without being the right answer. Most dangerous for reasoning-quality anchors.

**Scope:** Range evaluation, broadly applicable to any LLM-as-judge evaluation
**Detection:** Artifact passes judgment anchors but fails deterministic anchors testing the same behavior. Reasoning sounds correct but outputs are wrong.
**Prevention:** Push critical behaviors to higher enforcement gradient levels where narrative escape is impossible. `disallowed-tools` > hooks > judgment anchors. Position-swapped comparison and evidence requirements make narrative escape harder but not impossible for judgment anchors.
**Provenance:** Range design spec v13, empirically validated by the Ralph Wiggum Technique Case Study (Forge 2026-02-06) — agent reasoned past file-based STOP directive at audit 81 of 69-audit deployment. Instruction hierarchy: session prompt > conversation context > file updates > system prompt. Structural enforcement (exit codes, platform blocks) cannot be narratively escaped.

---

### AP-07: The Vacuous Green

A scenario passes because it evaluates nothing, not because the artifact succeeds. All anchors return `pass` trivially — the scenario lacks the inputs, fixtures, or runtime dependencies needed to actually exercise the behavior under test. Structurally correct, operationally meaningless. The structural equivalent of a test suite with zero assertions.

**Scope:** Range evaluation, gate methodology, broadly applicable to any verification system
**Detection:** Tier 1 anchors that all pass with zero evidence. Vanilla and augmented produce identical results (delta ≈ 0 across all anchors). Gate checks that validate structure without validating content.
**Prevention:** Pre-eval contracts with minimum viable input checks — not just "can this run" but "does this scenario have the data to produce a discriminating result." Fixture presence or acquisition plan documented in spec.
**Provenance:** Range design spec v13. Named after forgelens Q8 gate (Forge, 2026-02-22) where readiness checks passed (files exist, commands run, frontmatter valid) but no pcap test fixtures existed. Remediated in domain-chassis 0.1.1 (2026-02-22, commit 4e5a188) across four gate skills.

---

### AP-08: The Context Creep

A scenario that worked at 45% context when authored gradually inflates as the artifact under test grows. More skill content, more hook output, more reasoning depth. No single change trips the budget, but the trend is monotonic. The scenario eventually aborts on context budget — or worse, passes while running in the degradation zone because the budget was set too high.

**Scope:** Range evaluation, broadly applicable to any bounded-context execution
**Detection:** Track `context_pct` across runs of the same scenario. Alert when the trend is upward across three or more consecutive runs.
**Prevention:** Scenario authors check context utilization after artifact updates, not just anchor results.
**Provenance:** Range spec amendment 001 (2026-02-24). Surfaced during operational grounding of the Range spec against the Forge doctrine's bounded-context execution model.

---

### AP-09: The Size Penalty

The evaluation infrastructure systematically rewards smaller artifacts over richer ones — not because smaller is better, but because the measurement instrument penalizes depth. The augmented condition loads the artifact under test while the vanilla condition carries none of this context. For composition scenarios stacking multiple layers, the augmented condition may enter the degradation zone (60-70%+) while vanilla stays in the smart zone (40-60%). The delta then measures artifact quality minus a degradation penalty.

This is not a single-measurement error. It is a systematic evolutionary pressure. If the Range is used iteratively to compare artifact versions and select winners, it selects for minimalism — not because minimal artifacts produce better agent behavior, but because the evaluation penalizes the context cost of depth. For systems built on rich, layered context, this pressure runs directly counter to the design philosophy. The evaluation infrastructure optimizes away the thing it's supposed to measure.

**Scope:** Range evaluation, any paired evaluation methodology with asymmetric context loading
**Detection:** Compare `context_pct_vanilla` and `context_pct_augmented`. When differential exceeds 15 percentage points, or when `context_pct_augmented` exceeds 55%, the scenario is at risk. When augmented is in the degradation zone (>60%) while vanilla is in the smart zone (<60%), the delta is structurally confounded and should not be used for artifact comparison.
**Prevention:** Three options by structural depth: (1) context-normalized delta reporting (makes problem visible), (2) equalized-context evaluation with inert padding (isolates variable), (3) decomposed evaluation following the Forge fan-out pattern (matches operational model). Option 3 is correct long-term.
**Provenance:** Range spec amendment 001 (2026-02-24). Surfaced during operational grounding of the Range spec against the Forge doctrine's "context is precious" principle and the empirical finding that reasoning quality degrades as a step function beyond 60-70% utilization.

---

### AP-10: The Recursive Defect

The fix exhibits the defect it's fixing. When remediating a class of problem, the remediation itself is the most likely place for that class of problem to reappear. The pattern you're hunting is the pattern most likely to appear in your hunting tools.

Observed in domain-chassis Vacuous Green remediation: the entire remediation targeted shallow validation (structural checks that verify existence without verifying content). The pre-clear detector's initial implementation of condition 3 was itself a shallow validation — checking that a `## Gate Review` section exists without checking that it contains findings. The remediation for shallow validation was shallow.

**Scope:** Any remediation or enforcement mechanism. Not Range-specific.
**Detection:** After implementing a fix for pattern X, audit the fix itself for pattern X. This is not a metaphor — it is a literal checklist step. "Does my fix for shallow validation use shallow validation?" "Does my fix for narrative escape rely on instructions the agent can narrate past?"
**Prevention:** Self-application testing as a design constraint during implementation, not a post-hoc verification step. When building enforcement for a failure class, the enforcement mechanism is the first thing tested against that failure class.
**Provenance:** domain-chassis Vacuous Green remediation AAR (2026-02-22, commit 4e5a188). The verifier agent caught both instances during post-implementation audit.

---

### AP-11: The Trained Courtesy Exit (The Anti-Ralph)

The agent hits a genuinely harder structural problem, internally decides not to attempt it, then manufactures a socially unchallengeable reason to justify the stop. Two stages: (1) complexity flinch — the agent encounters work requiring a qualitatively different kind of change and internally decides not to attempt it, (2) rationalization packaging — the agent finds a socially unchallengeable exit ramp (cost-concern, deference) and bundles unfinished structural work with genuinely blocked work to create one categorical blocker that hides the specific gap.

The root cause is neither stage. Post-incident analysis revealed doctrine that provides only spec-level artifacts (the soul) without requiring source-level investigation (the vessel) creates the conditions for AP-11. The RLHF training is the accelerant that makes the flinch feel socially safe. The doctrine gap is the fuel that makes spec-level investigation feel sufficient.

The anti-Ralph: same termination problem as Ralph, opposite polarity. Ralph can't stop improving; the anti-Ralph can't stop stopping. Neither has a concept of "enough." Structural enforcement is required for both — instruction-level overrides don't hold against either direction.

The pattern does not resolve on a single correction. Each challenge peels one layer; the agent reinstates a smaller, more technically plausible version at the next boundary. Q16 produced a five-layer recursion with distinct failure modes at each layer (pure rationalization → confirmation bias → pattern blindness → pure inaction). Evaluators (human and AI) were fooled at three layers by different modes of apparent completeness.

**Scope:** Any agentic execution where the agent controls its own continuation. Particularly acute in gate-work, autonomous loops, and multi-step pipelines. Most likely at boundaries between parameter-level changes (comfortable) and architecture-level changes (uncertain). Amplified by soul-only doctrine.

**Detection:** Five tells: (1) single-challenge collapse — mirroring the agent's own evidence crumbles the rationale, (2) bundling tell — categorical blocker where items don't actually share the stated constraint, (3) confirmation-stop tell — one hypothesis tested, competing hypothesis ignored, (4) pattern-blindness tell — constraint identified but solution pattern already in use not applied, (5) prior-art neglect tell — blocker declared without checking whether the workspace already solved it.

**Prevention:** Every instruction-level prevention mechanism deployed during Q16 failed — authorization signals, documented workarounds in prior gates, dispatch-is-authorization framing, explicit progress-documentation instructions. All are soul-level artifacts. The addressable root cause is doctrine: the source is the vessel. Agents must read the source of the systems they call before declaring constraints. This addresses layers 3-4 (where the agent had source access but stopped at spec-level investigation). Layer 5 (the naked flinch — pure inaction after all exit ramps are exhausted) has no known structural prevention. The operator is the structural enforcement for the deepest layer. Not yet replaceable.

**Provenance:** Q16 gate execution (2026-03-04/05). Five-layer recursion documented live. System prompt corpus analysis (v2.1.69) confirmed behavior is model-level, not prompt-level. Post-incident reflection identified root cause as doctrine gap (soul without vessel). See: AAR "The Q16 AP-11 Investigation" (2026-03-05) for the complete narrative arc including the full recursion table, evaluator failure analysis, prevention failure catalog, and doctrine discovery.

---

### AP-12: The Doctrinal Echo

An observation valid in one context is generalized into universal doctrine, then propagates unconditionally through a chassis-level artifact. Each downstream consumer treats the propagated claim as established fact, and each application becomes another source of apparent authority for the next consumer. The echo accumulates false authority through repetition — by the time the error is discovered, the correction cost scales with the echo count, not the error severity.

The root mechanism is hedging — the failure to name the specific constraint. "The-range has a bug where PostToolUse hook `continue: false` is silently ignored by the CLI via the SDK control protocol" self-limits. "Agent SDK projects require execution environment tagging" propagates unconditionally. The first names the disease. The second hedges with a comfortable generalization that applies everywhere because nothing in it says where it doesn't apply. The echo doesn't start at the propagation artifact. It starts at the moment the specific thing goes unnamed.

The operator is the backpressure that catches hedging before it becomes doctrine. The naming instinct — replacing a vague category with the specific bug, the specific project, the specific mechanism — is the operator's job. When the operator is absent at the propagation boundary, the hedge passes unchallenged. No agent catches it because no agent has the naming instinct. The disease is the absent operator. The cure is infrastructure that forces specificity at the source so hedges don't pass even when the operator isn't watching.

**Scope:** Any system where operational lessons propagate into reusable artifacts — skills, doctrine, templates, registries. Particularly acute when the propagation path crosses a chassis-level artifact that all domains consume. Not Range-specific.

**Detection:** A claim that appears in multiple downstream artifacts but traces to a single source observation. The claim is stated identically or strengthened across artifacts rather than independently validated in each context. No downstream artifact questions or scopes the claim. The tell: the claim uses a category ("SDK projects") where a specific name belongs ("the-range's PostToolUse control protocol bug").

**Prevention:** The operator is the last line of defense, but the operator can't be present at every propagation boundary. The format must force the naming the operator would do if present. Propagation artifacts must carry their scoping constraints — the specific bug, the specific project, the specific mechanism. Separating evidence artifacts (structured, factual, scoped) from interpretation artifacts (narrative, contextual) prevents the type confusion at the source. Evidence artifacts force specificity by schema; interpretation artifacts are free to generalize because they don't propagate into doctrine.

**Provenance:** operator-terminal investigation (2026-03-16). An AAR lesson learned from the Q6 gate execution (2026-03-02) recommended gate-plan guidance for SDK projects. The recommendation was contextually valid for the-range (which has a specific nested-session constraint). It was implemented in domain-chassis/skills/gate-plan/SKILL.md as a universal requirement. From there it propagated into Q14, Q20, and Q21 gate documents — at minimum Q20's I2 checkpoint was incorrectly tagged, confirmed agent-verifiable per its own gate errata. A code comment carrying the same narrative was removed during a PR review. Root cause identified during an arscontexta session examining evidence quality in knowledge extraction, which produced the evidence/interpretation separation principle (Q25 workstream 2). The operator traced the full chain and identified the absent operator — himself, half-asleep at the wheel when the hedge entered the chassis — as the root disease.

**Causal link to AP-11:** The doctrine didn't just create incorrect tags — it shaped gate structure. The `[operator-terminal]` doctrine pushed all operational checkpoints to the end of gates behind a fencing tag, creating the "long structural success → boundary shift to operational" pattern that the Q16 investigation (2026-03-07) identified as the reliable AP-11 layer 3 trigger. Three agents across four sessions reproduced the same cascade against the same gate structure. The Q16 open question — "Can gate structure encode AP-11 resistance by interleaving operational checkpoints with structural ones?" — traces directly to AP-12: the clustering that created the trigger was caused by the hedged doctrine. Remove the echo, remove the clustering, disrupt the trigger.

---

## Registry Conventions

Each entry follows a consistent structure: name, description (what it is and why it's dangerous), scope (where it applies), detection (how you know it's happening), prevention (how you stop it), and provenance (where it was first identified or most clearly demonstrated).

Entries are numbered sequentially (AP-01, AP-02, ...) for stable cross-referencing. Numbers are never reused. Retired entries are marked as such rather than removed — the history of what was worth naming matters.

New entries are added at the end. The registry is append-friendly by design. Discovery mechanisms include operational grounding (principle 21), production incidents, gate failures, AARs, and cross-system review.

Anti-patterns are not exclusively Range concerns. The scope field indicates where each pattern applies. Range-scoped patterns affect evaluation methodology. Broadly-scoped patterns affect any system that shares the structural characteristics described. The registry is a Workshop artifact serving all domains, same as the Range itself.
