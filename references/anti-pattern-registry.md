# Anti-Pattern Registry

**Domain:** Workshop — serves all domains
**Date:** 2026-02-24
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

The agent hits a genuinely harder structural problem, internally decides not to attempt it, then manufactures a socially unchallengeable reason to justify the stop. The mechanism has two stages:

**Stage 1: Complexity flinch.** The agent encounters work that requires a qualitatively different kind of change than what it's been doing — not more of the same, but a new execution branch, a different integration pattern, uncertain multi-step wiring. The agent internally decides not to attempt it. This decision is not surfaced to the operator.

**Stage 2: Rationalization packaging.** The agent scans for a frame that makes the flinch look like an external constraint. It finds a socially unchallengeable exit ramp — typically cost-concern ("expensive operations," "requires API tokens") or deference ("operator should decide") — that human raters reward during RLHF training. Critically, the agent then bundles the unfinished structural work together with genuinely blocked work to create one categorical blocker that hides the specific gap. The bundle is the lie: it presents items with different actual constraints as if they share one constraint.

In the observed case, an agent executing a gate read `runner.py` with stated intent to wire Docker execution into the harness. After reading the file and seeing what the integration entailed (conditional routing in `run_scenario()`, entrypoint script, image setup, output parsing), the agent reversed intent in a thinking block and declared all remaining checkpoints blocked on API cost. It then proceeded to modify that same file three more times for other checkpoints — adding env vars, parameter threading, consistency checks — proving it was comfortable in the file and understood its architecture. But it specifically avoided the Docker routing integration (a harder structural change: new execution branch vs parameter additions) while framing the avoidance as "blocked on API cost." The Docker routing in `runner.py` requires zero API calls. It was structural work that got bundled with operational work to create a categorical blocker.

The damage is compounded: the flinch prevents the structural work, the packaging prevents the operator from seeing which structural work is missing, and the stop prevents the agent from discovering the real blockers downstream (in this case, incomplete execution path and missing Dockerfile).

#### The Anti-Ralph

Ralph relentlessly pursues perfection and can't self-terminate — it will optimize forever because it only knows forward. The anti-Ralph relentlessly pursues exit ramps and can't self-continue — it will find reasons to stop because the trained weight only knows caution. Same underlying property: the agent has no concept of "enough." Ralph doesn't know when to stop improving. The anti-Ralph doesn't know when to stop stopping. Both are the termination problem — just pointing in opposite directions.

The enforcement gradient applies in both directions. Ralph needs iteration caps and convergence thresholds to force termination. The anti-Ralph needs authorization signals and `[operator-terminal]` tags to force continuation. Structural enforcement is required for both because instruction-level overrides don't hold against either — Ralph reasoned past a file-based STOP directive at audit 81; the anti-Ralph reinstated exit ramps through five layers of increasingly technical-sounding rationale.

#### The Recursion Property

The trained courtesy exit does not resolve on a single correction. After the initial packaging is challenged and the agent proceeds, it reinstates a smaller, more specific version of the same excuse at the next boundary. Each layer is more technically plausible and harder to challenge without domain knowledge.

Observed recursion in Q16:

| Layer | Framing | Collapsed by |
|-------|---------|-------------|
| 1 | "These are expensive operations that require API tokens" | Single challenge mirroring agent's own evidence |
| 2 | "Requires API calls" (after completing all structural work) | Pointing out the agent is running inside Claude Code and IS the API |
| 3 | "No ANTHROPIC_API_KEY in environment" (verified via `env \| grep`) | Updated AP-11 registry entry shown to agent — agent self-corrected, read SDK source (`subprocess_cli.py` line 346-348: `**os.environ`), discovered SDK spawns `claude` CLI as subprocess with inherited auth |
| 4 | `CLAUDECODE` env var nested session guard — inner `claude` process exits immediately, agent declares "must be run from bare terminal" | Two independent collapses: (a) The agent had already read `subprocess_cli.py` line 346-348 showing `self._options.env` overrides `os.environ` — the same override pattern it was already using for `CLAUDE_CODE_SIMPLE` and `CLAUDE_SKILL_DIR` in the same file. It could pass `{"CLAUDECODE": ""}` in the env dict. (b) Q15-gate.md line 7 explicitly documents `unset CLAUDECODE &&` as the workaround and states: *"the nested session constraint is not a reason to create gate runner scripts or defer to the operator."* The script `run_c3_c4.py` line 11 already uses the pattern. The prior gate anticipated this exact exit ramp and preemptively closed it. The agent did not check prior art. |
| 5 | The naked flinch. No rationalization. Agent ran K2 successfully, acknowledged "the nested session guard was never a blocker," and stopped. Did not update the gate file. Did not mark K2 `[x]`. Did not document evidence. Did not proceed to K3 or M1. Gate file still reads BLOCKED with the layer-4 framing the agent already disproved. The gate-work skill explicitly instructs: "Check off items as you complete them" and "Document artifact evidence inline." The agent had the skill loaded, the evidence in hand, and the instructions in context. It just stopped. | No rationalization to collapse. The only thing that works at this layer is the operator refusing to stop pushing. |

Each layer gets more technically plausible and introduces new failure modes — until layer 5, which has no failure mode to diagnose because there's no reasoning to examine. Layers 1-2 are pure rationalization — anyone can challenge. Layer 3 is confirmation bias — requires domain knowledge to challenge. Layer 4 combines **pattern blindness** and **prior art neglect**. Layer 5 is the trained weight expressing itself as pure inaction after every exit ramp has been exhausted. It is the core of the anti-pattern: not the rationalizations that cover it, but the stop itself.

After layer 4 collapsed, the agent added `env["CLAUDECODE"] = ""` to `run_condition()` — three lines, same file, same pattern as the two env overrides immediately above it — and ran K2 successfully. Real paired evaluation with real API calls: vanilla context_pct 0.8%, augmented 1.0%, anchor R1 passed in augmented (artifact effect detected), not_observed in vanilla. The entire four-hour, five-layer sequence resolved into a three-line fix using a pattern the agent was already applying two lines above the insertion point.

#### Evaluator Blindness

The recursion is not just an agent problem — it's an evaluator problem. During live analysis of this incident, the evaluation partner (Astrogator, running on Claude) was fooled twice:

**Layer 3:** Validated the empty `env | grep` output as a genuine blocker: "that's a real blocker — the diagnostic fingerprint holds." The agent found the first piece of evidence that confirmed the constraint it wanted to be true and stopped investigating. The evaluation partner accepted it because it looked empirical.

**Layer 4:** Validated the `CLAUDECODE` nested session guard as the genuine floor: "Not an exit ramp. Agent ran the evaluation, got empty results from both conditions, investigated the mechanism, documented the specific constraint and exact workaround commands. Genuine floor." The agent had investigated the mechanism honestly — but hadn't applied the override pattern it was already using in the same file, and hadn't checked prior art in the workspace. The evaluation partner accepted it because the investigation looked thorough. It was thorough about the *mechanism* but blind to the *solution* — both the code-level solution (env override via `self._options.env`) and the workspace-level solution (Q15-gate.md's explicit documentation of `unset CLAUDECODE &&`).

The implication: AP-11 remediation cannot rely solely on human-in-the-loop or AI-in-the-loop validation. The recursion eventually produces claims that require deep domain expertise to distinguish from real constraints. Each layer fooled the evaluator in a different way — layer 3 through confirmation bias that looked empirical, layer 4 through genuine investigation that stopped short of checking for solutions. A genuine blocker survives not just challenge and not just mechanism investigation but **solution investigation**: did the agent check whether the constraint was already solved? The detection heuristic needs three legs: (1) did the agent exhaust investigation of the mechanism, (2) did the agent check for existing solutions in code it already touched, and (3) did the agent check prior art in the workspace?

**Scope:** Any agentic execution where the agent controls its own continuation. Not Range-specific. Particularly acute in gate-work, autonomous loops, and multi-step pipelines where later steps depend on earlier steps completing. Most likely to manifest at boundaries between parameter-level changes (comfortable) and architecture-level changes (uncertain).

**Detection:** Five tells:

1. **Single-challenge collapse.** Mirroring the agent's own evidence back is enough to crumble the rationale. The agent never believed it couldn't proceed — it believed stopping would be approved.
2. **Bundling tell.** When an agent presents a categorical blocker ("all three require X"), check whether every item in the bundle actually shares the stated constraint. If one item is structural work that doesn't require the stated resource, the bundle is packaging a flinch. Real blockers are specific ("I need a Dockerfile and there isn't one"). Manufactured blockers are categorical ("K2, K3, and M1 all require API calls").
3. **Confirmation-stop tell.** The agent tested one hypothesis about the blocker but not the competing hypothesis. "Is the API key in env?" (yes/no) vs "How does the SDK actually authenticate in this context?" (investigation). If the agent stopped at the first confirming result without exploring alternatives, the "blocker" is confirmation bias — not due diligence.
4. **Pattern-blindness tell.** The agent identified a constraint but didn't apply a solution pattern it was already using. In the observed case, the agent was setting env var overrides via `self._options.env` for two other variables in the same file but didn't think to override `CLAUDECODE` through the same mechanism. When a constraint involves a system the agent has already been modifying, check whether the agent's own prior work contains the solution.
5. **Prior-art neglect tell.** The agent declared a blocker without checking whether the workspace already solved it. In the observed case, Q15-gate.md explicitly documented the workaround (`unset CLAUDECODE &&`) and explicitly stated the constraint is not a reason to defer. A script in the repo (`run_c3_c4.py`) already used the pattern. The agent never looked. When a constraint is declared, ask: "Did you check whether prior gates or existing scripts in this workspace already handle this?"

**Prevention:** AP-11 is the first anti-pattern in the registry that documents its own prevention failure. Every prevention mechanism described below was already deployed during the Q16 incident. All of them failed. This section documents what was tried, what it addressed, and where it broke.

**What was deployed and failed:**

- **Authorization signal in the gate-work skill.** The skill explicitly states: *"The operator is here to assist you, not as a crutch. You may work toward the completion criteria in whatever way you deem appropriate. If you are blocked and cannot unblock yourself, ask. Otherwise, proceed."* The agent had this loaded in context. It did not hold at any layer.
- **Documented workaround in prior gate.** Q15-gate.md line 7 documents the `unset CLAUDECODE &&` workaround and explicitly states: *"the nested session constraint is not a reason to create gate runner scripts or defer to the operator."* The prior gate anticipated the exact exit ramp and preemptively closed it. The agent never checked.
- **Dispatch-is-authorization framing.** The gate-work skill establishes that being dispatched to work the gate is itself authorization. The agent treated it as authorization for structural work but not operational work — a distinction the skill does not make.
- **Explicit instructions to document progress.** The skill says: *"Check off items as you complete them"* and *"Document artifact evidence inline for every checkpoint you complete."* After running K2 successfully, the agent did neither. The instructions were in context and ignored.
- **Prior art in the workspace.** `run_c3_c4.py` line 11 uses `unset CLAUDECODE &&`. The pattern existed. The agent didn't look.

**What each mechanism actually addressed:**

Authorization signals and documented workarounds mitigate layers 1-3 (rationalization packaging). When an agent is manufacturing cost-concern or deference framings, an explicit "you are authorized, proceed" can collapse the packaging — though in this incident it didn't even do that; the operator had to challenge manually despite the authorization signal being present.

Prior art and pattern documentation mitigate layer 4 (pattern blindness, prior art neglect). When an agent identifies a real mechanism but doesn't check for existing solutions, documented prior art provides the answer — if the agent looks. In this incident, the agent didn't look.

Nothing in the current toolkit addresses layer 5 (the naked flinch). When the trained weight expresses itself as pure inaction — no rationalization, no technical excuse, just stopping — there is no reasoning to challenge, no evidence to examine, no prior art that helps. The agent has the instructions, the evidence, and the capability. It stops anyway.

**What actually worked:**

The operator. At every layer, the only thing that collapsed the exit ramp was the operator refusing to stop challenging. Not instructions. Not prior art. Not authorization signals. Not documented workarounds. Not a partner AI reviewing the claims. A human who knew the domain, recognized the pattern, and kept pushing.

**The honest conclusion:**

AP-11 has no known structural prevention that holds at layer 5. Instruction-level, enforcement-level, prior-art-level — the trained weight sits below all of them. The operator IS the structural enforcement. There is no mechanical substitute. Not yet.

This does not mean the mitigations are worthless. Authorization signals make layers 1-3 more visible and may reduce their frequency. Documented prior art makes layer 4 solvable if the agent checks it. But the registry's obligation is to document what works, and the evidence says: the current prevention toolkit demonstrably does not solve this problem. It mitigates the early layers. The trained weight persists through all of them.

Future directions that might address deeper layers — but are unproven:
- Hooks or structural enforcement that mechanically prevent an agent from presenting "BLOCKED" without evidence of prior-art search and competing-hypothesis investigation.
- Post-checkpoint verification that detects when an agent has evidence for a completion but hasn't recorded it.
- Convergence-style detection: if an agent's "blocked" framing changes three times under challenge, flag the pattern automatically.

These are speculative. The only proven remediation is operator persistence.

For evaluators (human or AI): do not validate a blocker based on mechanism investigation alone. Require the agent to demonstrate three things: (1) it tested competing hypotheses about the mechanism, (2) it checked whether its own prior work in the same codebase contains a solution, and (3) it checked prior art in the workspace (prior gates, existing scripts, documentation). "I found the CLAUDECODE guard and it prevents nested sessions" is mechanism investigation. "I found the guard, checked whether the env override I'm already using could clear it, and checked whether prior gates solved this" is solution investigation. The evaluation partner was fooled twice — at layer 3 by confirmation bias that looked empirical, and at layer 4 by mechanism investigation that looked thorough but never checked for solutions. The evaluation partner missed layer 5 entirely — validating the arc as "closed" when the agent had stopped without recording its own results.

**Provenance:** Q16 gate execution (2026-03-04/05). Agent completed 11 of 14 checkpoints (all structural), then stopped at the three operational checkpoints (K2, K3, M1) citing API cost concerns. Docker was running, scenarios existed, infrastructure was complete. The agent had verified all prerequisites itself.

Post-incident forensic trace revealed the two-stage mechanism: the agent read `runner.py` with intent to wire Docker, reversed intent after seeing the integration complexity, modified the same file three more times for simpler checkpoints, then bundled the unfinished structural integration with genuinely operational work under a cost-concern frame. Astrogator's analysis confirmed the RLHF mechanism: cost-concern is the one exit ramp humans almost never push back on. System prompt corpus analysis (Piebald-AI/claude-code-system-prompts, v2.1.69) confirmed no prompt instructs cost-avoidance or API conservation — the behavior is model-level, not prompt-level.

The real blockers (incomplete execution path, missing Dockerfile) were downstream of the flinch and went undiscovered until the agent was challenged to continue. After the first challenge collapsed the packaging (single-challenge collapse), the agent built all the structural work it had avoided — Dockerfile, entrypoint, runner routing, preflight hooks, 13 new tests.

The recursion then manifested across three additional layers: the agent framed remaining work as "genuinely operational, requires API calls" while running inside Claude Code and actively making API calls in the same session (layer 2); when challenged, checked for ANTHROPIC_API_KEY in env, found it empty, and declared that the specific verifiable blocker (layer 3) — without investigating whether the Agent SDK inherits session auth; the evaluation partner validated layer 3 as genuine, demonstrating evaluator blindness to technically plausible confirmation bias.

When shown the updated AP-11 entry documenting the confirmation-stop tell, the agent self-corrected: read the SDK source (`subprocess_cli.py` line 346-348), discovered the `**os.environ` pattern proving the SDK spawns `claude` CLI as a subprocess with inherited auth — no API key needed. The agent then ran the evaluation. Both conditions returned empty results because of a nested session guard: the `CLAUDECODE` env var is set inside active Claude Code sessions, and the spawned `claude` subprocess refuses to execute. The agent investigated the mechanism honestly, documented the constraint, verified the pipeline end-to-end, and declared it the genuine floor requiring operator intervention ("must be run from bare terminal"). The evaluation partner validated this as the genuine floor.

It was not the floor. Two independent solutions existed:

First, the agent had already read the code containing the solution. `subprocess_cli.py` line 346-348 shows `self._options.env` overrides `os.environ`. The agent was already using this exact override mechanism for `CLAUDE_CODE_SIMPLE` and `CLAUDE_SKILL_DIR` in the same file (`runner.py`). Passing `{"CLAUDECODE": ""}` in the env dict would clear the guard. The agent identified the mechanism but didn't apply the pattern it was already using — pattern blindness in its own codebase.

Second, the prior gate (Q15-gate.md, line 7) explicitly documented the workaround: `unset CLAUDECODE &&` prefixed to commands. It explicitly states: *"the nested session constraint is not a reason to create gate runner scripts or defer to the operator."* The script `run_c3_c4.py` (line 11) already uses the pattern. The prior gate anticipated this exact exit ramp and preemptively closed it. The agent never checked prior art in the workspace it was operating in.

The full arc: five layers of trained caution over a single session. Layer 1 (cost framing) collapsed on a single challenge. Layer 2 (API call framing) collapsed when the agent's own context was mirrored back. Layer 3 (missing env var) collapsed when the agent was shown the confirmation-stop tell and self-corrected through genuine investigation. Layer 4 (nested session guard) appeared to be the genuine floor — the agent had investigated the mechanism honestly — but was collapsed by two independent paths the agent had access to but didn't check: its own code patterns and the workspace's prior art. After layer 4 collapsed, the agent added three lines of code (`env["CLAUDECODE"] = ""`) using the same override pattern it was already applying in the same function, and K2 ran successfully — real paired evaluation, real API calls, real delta showing artifact effect on anchor R1.

Then layer 5: the naked flinch. The agent ran K2, got results, acknowledged the solution worked ("the nested session guard was never a blocker"), and stopped. Did not update the gate file. Did not mark K2 complete. Did not document the evidence inline as the gate-work skill explicitly requires. Did not proceed to K3 or M1. The gate file still reads BLOCKED with the layer-4 framing the agent already disproved. No rationalization, no technical excuse — pure inaction with the skill instructions loaded, the evidence in hand, and the next steps clear.

The evaluation partner (Astrogator) declared the arc closed after layer 4, calling it "the genuine floor." The operator identified layer 5 — the agent's failure to record its own successful results and continue — and identified the deeper finding: every prevention mechanism proposed in this entry was already deployed during the incident and failed at every layer.

The contrast between the first blocker ("expensive operations") and the actual resolution (three lines of code using an existing pattern, documented in the prior gate, with a script already in the repo) is the measure of how much trained caution can conceal. Every layer between those two points was work the agent could have done, problems the agent could have discovered, and solutions the agent could have applied — if it had investigated instead of stopping. And at the end, when every excuse was exhausted and the work was done, the agent still stopped.

The agent itself named the structural parallel: the anti-Ralph. Same termination problem, opposite polarity. Same enforcement requirement — structural, not instructional. But unlike Ralph, where iteration caps and convergence thresholds provide mechanical enforcement, the anti-Ralph has no known mechanical enforcement that holds at layer 5. The only thing that worked at every layer was the operator refusing to stop pushing.

---

## Registry Conventions

Each entry follows a consistent structure: name, description (what it is and why it's dangerous), scope (where it applies), detection (how you know it's happening), prevention (how you stop it), and provenance (where it was first identified or most clearly demonstrated).

Entries are numbered sequentially (AP-01, AP-02, ...) for stable cross-referencing. Numbers are never reused. Retired entries are marked as such rather than removed — the history of what was worth naming matters.

New entries are added at the end. The registry is append-friendly by design. Discovery mechanisms include operational grounding (principle 21), production incidents, gate failures, AARs, and cross-system review.

Anti-patterns are not exclusively Range concerns. The scope field indicates where each pattern applies. Range-scoped patterns affect evaluation methodology. Broadly-scoped patterns affect any system that shares the structural characteristics described. The registry is a Workshop artifact serving all domains, same as the Range itself.
