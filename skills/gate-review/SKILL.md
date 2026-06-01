---
name: gate-review
description: Audits an existing gate document against the gate-plan quality bar — the quality assurance step between plan and work. Produces findings (structural compliance, quality findings, self-assessment gaps, strengths) and a PASS/FAIL verdict with confidence rating.
when_to_use: Use when the user asks to review/audit/check a gate, evaluate a gate (e.g. "review Q3-gate"), ask whether a gate passes or is ready for execution, or wants a quality check before running a gate.
---

# Gate Review — Gate Quality Audit

Evaluate an existing gate document against the quality bar defined in gate-plan. This is the quality assurance step between creation and execution — plan creates, review audits, work executes.

The review produces findings. It does not rewrite the gate. The operator decides what to fix.

## Input

The operator provides a gate reference: a Q-number (e.g., "Q4"), a filename (e.g., "Q4-gate.md"), or a path. Resolve to a `*-gate.md` file at the workspace root. If no matching gate file exists, stop and tell the operator — there is nothing to review.

## Step 1 — Load Criteria

Read the quality bar from two sources:

1. `${CLAUDE_PLUGIN_ROOT}/skills/gate-plan/SKILL.md` — Step 3 (quality requirements) and Step 4 (self-assessment questions). These define what a well-formed gate looks like.
2. `${CLAUDE_PLUGIN_ROOT}/skills/gate-plan/references/gate-template.md` — Structural conventions: title format, checkpoint ID patterns, verification method placement, bypass markers, anti-pattern tags, section ordering.
3. `${CLAUDE_PLUGIN_ROOT}/references/anti-pattern-registry.md` — Named failure modes catalog. Required for validating anti-pattern tag references and assessing semantic accuracy of guarding relationships.

These are the criteria. Do not invent additional requirements or import standards from other frameworks. The gate is evaluated against the gate standard.

## Step 2 — Structural Compliance

Check the gate document against the template conventions:

- Title follows `# Q{n} Gate: {descriptive title}` format
- First paragraph after the title states completion criteria (concrete, claimable, specific)
- `Depends on:` line present
- Phases numbered sequentially with descriptive names
- Checkpoint IDs are bold, use letter prefix + number, unique within the gate
- Every checkpoint has a verification method (command, observable outcome, or artifact)
- Bypass markers (`[~]`) include inline justification
- Cleanup section present if the gate produces temporary artifacts
- Excluded section present if the gate deliberately omits scope

Report each as compliant or non-compliant. Non-compliance is a finding, not a blocker — some gates may intentionally deviate.

## Step 3 — Quality Requirements

Evaluate the gate against each quality requirement from gate-plan Step 3. For each requirement, assess the gate and report pass, fail, or partial with specific evidence.

**Completion criteria must be claimable.** Can a practitioner read the first paragraph and know exactly what was proven? Does it name the scope, method, and deliverable? Or is it vague enough to mean different things to different readers?

**Every verification method must produce a positive artifact.** Walk each verification method within each checkpoint. Does it leave evidence when it passes — output to quote, a file that exists, a count that matches? Flag any verification method that could pass silently or proves a negative (absence of errors, no failures, clean exit without observable output). When a checkpoint contains multiple verification methods, assess each method independently — a positive sibling method does not mask a negative-proof method within the same checkpoint. A checkpoint where some methods produce positive evidence while others prove negatives has a per-method granularity defect even if the checkpoint as a whole appears to have positive evidence. Watch for search-and-validate patterns: "search for X, and for each X found, confirm Y" passes vacuously when zero X are found. The verification must name the items or minimum count it expects the search to return — an empty result set is a verification failure, not a clean pass. A verification method without a defined positive artifact is a blocking deficiency, not a minor finding.

**Checkpoint categories must be declared.** Check whether every checkpoint uses the `[structural]` or `[operational]` tag after the checkpoint ID. Flag any checkpoint without a category tag. For preflight gates, verify at least one `[operational]` checkpoint exists — a preflight gate with only structural checkpoints is a finding at the highest priority, as it has direct Vacuous Green exposure (can clear without proving the deliverable works).

**Pre-clear conditions must pass prospectively.** Evaluate whether the pre-clear detector conditions from gate-work would pass if this gate were executed and all checkpoints cleared as written: (1) would at least one checkpoint be genuinely completed, not all bypassed? (2) would every completed checkpoint have artifact evidence defined? (3) is there a provision for gate review? This catches gates that would fail the pre-clear detector before they reach execution.

**Verification must exercise what it claims to validate.** For each checkpoint with a verification method, check: does the verification actually prove the checkpoint's claim? A header count doesn't prove the right headers exist. A file existence check doesn't prove the file has the right content. Flag verifications that could pass without the validated thing being true.

**Ordering dependencies must be explicit.** Check whether later phases depend on earlier phases producing artifacts. Are these dependencies stated? Could an agent encounter a checkpoint that fails because a prerequisite wasn't documented?

**Specify outcomes, not tool sequences.** A checkpoint that prescribes specific tool invocations, command sequences, or step-by-step procedures instead of defining what the result looks like is a blocking deficiency, not a minor finding. The gate defines "done," not "how."

**Bypasses are decisions, not shortcuts.** Check any `[~]` markers for inline justification. A bypass without reasoning is a finding.

**Document cleanup expectations.** If the gate produces temporary state (scratch repos, test artifacts, temp files), is the Cleanup section specific about what to remove?

**Scope out explicitly.** Is there an Excluded section? Does it name what the gate deliberately does not cover and why? Missing exclusions leave the executing agent guessing about boundaries.

**Coverage matrix completeness (conditional).** If the gate targets remediations across multiple vectors and multiple lifecycle stages, it must include a coverage matrix. Evaluate three aspects: (1) matrix completeness — every vector-stage cell contains a named enforcement mechanism or an explicit scope-out justification, with no empty cells; (2) mechanism-to-vector alignment — each named mechanism actually closes the vector it claims to at the lifecycle stage where it appears; (3) conditional applicability — the matrix is present when the gate crosses multiple vectors and lifecycle stages, and absent when the gate is single-vector or single-stage (presence in a single-scope gate is not a finding, but absence in a multi-vector gate is). A missing matrix in a multi-vector gate is a blocking deficiency.

**Cross-domain delivery verification (conditional).** If the gate modifies artifacts consumed external to the current domain, it must include at least one checkpoint that verifies consumer reachability through the actual distribution path, or scope out delivery verification in the Excluded section with reasoning. Evaluate three aspects: (1) delivery coverage — every cross-domain artifact modified by the gate has a corresponding reachability checkpoint, not just the source-level change; (2) conditional applicability — the delivery checkpoint is present when the gate modifies cross-domain artifacts, and absent when all artifacts are domain-local (presence in a domain-local gate is not a finding, but absence in a cross-domain gate is); (3) operator-dependent distribution — when the distribution path requires operator action or platform mechanics outside the gate agent's control (e.g., plugin cache refresh, manual deployment), an explicit scope-out in Excluded with reasoning that names what the agent cannot control and why in-scope checkpoints cover correctness is a valid resolution. A missing delivery checkpoint in a cross-domain gate is a blocking deficiency only when the distribution path is within the agent's control and no scope-out justification is provided.

**Anti-pattern tag validation (conditional).** If the gate contains checkpoints with anti-pattern tags (`` `{AP-nn}` ``), validate three aspects: (1) every anti-pattern tag references a valid AP-nn entry present in the anti-pattern registry — tags referencing nonexistent entries are a finding; (2) the guarding relationship between the tagged checkpoint and the referenced anti-pattern is semantically correct — the checkpoint genuinely prevents or detects the named failure mode, not a superficially related one; (3) checkpoints with clear anti-pattern relevance that lack tags are flagged as potential omissions — this is a finding, not a blocker, since not every anti-pattern mapping is obvious to the authoring agent. If the gate contains no anti-pattern tags, note the absence and assess whether any checkpoints have obvious anti-pattern relevance that the authoring agent missed.

**Decision-token legend validation (conditional).** When a gate cites decision-record tokens — `d-NNNN`, `ADR-NNNN`, or an equivalent external decision ID — run the deterministic citation checker (`${CLAUDE_PLUGIN_ROOT}/skills/gate-review/scripts/check-citations.py <gate-file>`, from the workspace root so pointers resolve) and record its exit code and output. The checker's exit code is the verdict input, not an agent's spot-check (AP-06, The Narrative Escape): a RED exit is a blocking deficiency — a missing legend entry for a worked-example token, a malformed pointer, a dangling pointer, or a gross title mismatch; an UNRESOLVABLE exit is surfaced to the operator as "N pointers unverifiable in this environment" — not a silent pass and not a citation defect; only a GREEN or N/A exit clears the requirement. This requirement replaces any instruction to "spot-resolve" or "grep and confirm" a citation by hand — the checker is the resolution, and the review quotes its verdict. Conditional applicability: a gate that cites no decision-record tokens draws the checker's N/A and is not a finding. Anti-pattern tags (`{AP-nn}`) are not decision-record tokens and do not trigger this requirement.

**Predecessor-gate inheritance validation (conditional).** When a gate declares a `Builds on:` field naming a predecessor gate, run the deterministic inheritance checker (`${CLAUDE_PLUGIN_ROOT}/skills/gate-review/scripts/check-inheritance.py <gate-file>`, from the workspace root) and treat its exit code as a verdict input, exactly as the citation checker above (AP-06, The Narrative Escape): a RED exit — a declared `Builds on:` with no matching `## Inherited from {predecessor}` section — is a blocking deficiency. A GREEN exit (section present and predecessor-name-matched) or an N/A exit (no `Builds on:` field, or `Builds on: None`) clears the requirement. The checker enforces section presence and predecessor-name match only; whether the `Inherited from` section transcribes the right load-bearing fraction is the reviewer's judgment, not the checker's (`${CLAUDE_PLUGIN_ROOT}/adrs/ADR-003-gate-to-gate-inheritance.md`). Conditional applicability: a gate with no `Builds on:` relation draws the checker's N/A and is not a finding.

## Step 4 — Self-Assessment Questions

Apply the thirteen questions from gate-plan Step 4 to the gate as if you were the authoring agent reviewing your own work:

1. If every checkpoint were cleared, does that fully justify the completion criteria? Are there gaps — things the first paragraph claims that no checkpoint validates?
2. Does every verification method within every checkpoint produce a positive, observable verification? Any that prove negatives, could pass silently, or use search-and-validate patterns that pass vacuously on zero results — including negative-proof methods masked by positive siblings within the same checkpoint?
3. Are all ordering dependencies documented?
4. Could an agent execute this gate top-to-bottom without the operator clarifying sequencing, prerequisites, or intent?
5. Is checkpoint granularity appropriate — unambiguous but not micromanaged?
6. Does the gate include operational checkpoints that verify first-iteration readiness, not just structural completeness?
7. If the gate targets multiple vectors across lifecycle stages, does it include a coverage matrix with zero empty cells?
8. If the gate modifies artifacts consumed external to the current domain, does it include a checkpoint verifying consumer reachability — or, if the distribution path is outside the agent's control, does it scope out delivery verification with reasoning in the Excluded section?
9. Does every `[operator-terminal]` tag carry a stated project-specific execution constraint — naming the project, the mechanism, and why the agent cannot verify that checkpoint within a Claude Code session? Would a tag justified only by the project's technology category (without naming the specific constraint) fail this check?
10. Do the gate's checkpoints cover relevant anti-patterns from the registry? Where a guarding relationship exists between a checkpoint and a registry entry, has the `{AP-nn}` tag been applied? Are there relevant anti-patterns with no guarding checkpoint that should be addressed?
11. Does any checkpoint prescribe a specific tool invocation, command sequence, or procedure instead of defining what the result looks like?
12. If the gate cites decision-record tokens, does the Decision-Token Legend carry one decision title and one `<corpus-path>#<record-id>` source pointer per token, and does the citation checker exit GREEN/N-A? A RED exit, or a missing legend on a token-citing gate, is a blocking deficiency.
13. If the gate builds on a predecessor gate's load-bearing semantics, does it set `Builds on:` and carry a matching `## Inherited from {predecessor}` section, and does `check-inheritance.py` exit GREEN/N-A? A RED exit (declared `Builds on:` with no matching section) is a blocking deficiency.

Report each question's answer with specific evidence from the gate.

## Step 5 — Findings Report

The Findings Report goes to two surfaces: the terminal (for the operator in real time) and the `## Gate Review` section appended to the gate document (for future readers — gate-work's pre-clear detector, later re-reviewers, and the operator months from now). Both surfaces receive the same report. The terminal may additionally include the per-requirement and per-question audit walk produced during Steps 2–4 so the operator can audit the review live; the persisted artifact must not include that walk. Future readers need conclusions, not a replay of the audit.

Report structure:

**Classification binding.** When a quality requirement in Step 3 explicitly classifies a violation as a "blocking deficiency," the review must classify findings against that requirement at the same severity. The review agent does not have discretion to downgrade a finding that the quality bar already classified. If the review agent believes the classification is wrong for this gate type or context, it must state that disagreement as a named finding — "this review believes requirement X is over-specified for infrastructure gates because Y" — not silently reclassify the violation to a lower priority. A review that contains blocking deficiency findings produces a FAIL verdict regardless of the gate's overall quality. The operator decides whether the blocking classification is warranted and either fixes the gate or revises the quality bar — the review does not make that call on the operator's behalf.

**Confidence rating:** Rate your confidence in the gate on a 1-5 scale with reasoning.

- **1-2:** Blocking deficiencies. The gate cannot be executed as written — missing verification artifacts, structural non-compliance, or checkpoints that don't validate what they claim.
- **3:** Significant findings that may require revision before execution. The gate is structurally sound but has gaps that could cause execution friction or ambiguous outcomes.
- **4:** Minor findings only. The gate is ready for execution. This is the expected rating for a well-formed gate — reviews always surface something.
- **5:** Unreachable. A 5/5 would mean zero findings, zero observations, nothing to improve. Reviews always produce findings; a reviewer reporting 5/5 hasn't looked hard enough. Never assign this rating.

**Structural compliance:** List of compliant/non-compliant template conventions.

**Quality findings:** Only quality requirements that scored fail or partial, with the specific checkpoint(s) affected and what's wrong. Prioritize by impact — a verification that can pass without validating anything is higher priority than a missing Excluded section. Do not include requirements that passed — those belong in the Step 3 terminal walk, not in the report.

**Self-assessment gaps:** Only questions 1–10 or 12 that answered "no," or question 11 that answered "yes," with evidence. Do not include clean answers — those belong in the Step 4 terminal walk, not in the report.

**Strengths:** What the gate does well. A review that only reports problems misses the chance to reinforce good patterns.

The operator reads the findings and decides what to fix. The review does not propose rewrites, suggest alternative checkpoints, or offer to regenerate the gate. That's the operator's work or a subsequent gate-plan invocation.

After presenting the Findings Report in the terminal, record the outcome in the gate document in **two** places. (1) Set the gate's frontmatter machine-readable review header — the fixed-position current-state that gate-work's detector and the `check-review-header.py` checker read (see the *Machine-readable review header* convention in `${CLAUDE_PLUGIN_ROOT}/skills/gate-plan/references/gate-template.md`): overwrite `verdict:` to `pass`/`fail` to match this review; set `reviewed:` to a UTC-canonical `Z` stamp from `${CLAUDE_PLUGIN_ROOT}/skills/_shared/now.mjs` (ADR-001); and set `confidence:` to the bare 1–4 enum matching the rating below (5 is unreachable). The verdict↔confidence invariant (`pass` iff `confidence` is 4; `fail` iff 1–3) and the `Z` `reviewed` format are enforced by `check-review-header.py` (ADR-004 / ADR-005). (2) **Append** a `## Gate Review` block containing the same report. The `## Gate Review` section is the append-only review log: on a re-review, append a new block below the prior one and leave earlier blocks unedited (the FAIL → fix → PASS arc is preserved); never overwrite or delete a prior block. Because the detector reads the frontmatter field and not the log, a superseded `Verdict: FAIL` in an earlier block no longer endangers clearance — no hand-relabel is needed.

The section opens with three human-readable header lines that echo the authoritative frontmatter — `Reviewed: {UTC-canonical Z stamp}`, `Verdict: PASS` or `Verdict: FAIL`, and `Confidence: {n}/5` (the same `n` as the frontmatter `confidence:` enum) — then the report body: structural compliance, quality findings, self-assessment gaps, and strengths. Each persisted finding must carry full reasoning — affected checkpoints, why it matters, and fix shape. Do not downgrade findings to one-sentence summaries. The fidelity floor applies to the findings themselves, not to the Step 2–4 audit walk, which remains terminal-only.

Verdict is PASS when confidence is 4/5 and no blocking deficiencies were found. Verdict is FAIL when confidence is 3/5 or below, or when blocking deficiencies were found — state the primary blocking finding on the Verdict line. Gate-work's pre-clear detector requires the frontmatter `verdict: pass` to clear the gate; a `fail` verdict (frontmatter set to `fail`) blocks clearance until the gate is revised and re-reviewed. Keep the frontmatter `verdict:` field and the latest `## Gate Review` block's `Verdict:` line in agreement — the deterministic checker `${CLAUDE_PLUGIN_ROOT}/skills/gate-review/scripts/check-review-header.py` enforces that agreement (exit-code = verdict).

## Related Skills

- **gate-plan** — Authors gate documents. The review skill audits against plan's quality bar.
- **gate-work** — Executes gate documents. Review sits between plan and work in the lifecycle.

## Reference Files

- **`${CLAUDE_PLUGIN_ROOT}/skills/gate-plan/SKILL.md`** — Quality requirements (Step 3) and self-assessment questions (Step 4) that define the evaluation criteria.
- **`${CLAUDE_PLUGIN_ROOT}/skills/gate-plan/references/gate-template.md`** — Structural conventions for gate documents.
- **`${CLAUDE_PLUGIN_ROOT}/references/anti-pattern-registry.md`** — Named failure modes catalog. Required for validating anti-pattern tag references during quality audit.
