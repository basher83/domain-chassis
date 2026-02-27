---
name: gate-review
description: This skill should be used when the user asks to "review the gate", "audit the gate", "check the gate", "gate review", "does this gate pass", "evaluate this gate", "review Q3-gate", "is this gate ready", or mentions evaluating an existing gate document against quality standards, checking gate verification rigor, or auditing a gate before execution. Provides the gate quality audit methodology for evaluating gate documents against the gate-plan quality bar.
---

# Gate Review — Gate Quality Audit

Evaluate an existing gate document against the quality bar defined in gate-plan. This is the quality assurance step between creation and execution — plan creates, review audits, work executes.

The review produces findings. It does not rewrite the gate. The operator decides what to fix.

## Input

The operator provides a gate reference: a Q-number (e.g., "Q4"), a filename (e.g., "Q4-gate.md"), or a path. Resolve to a `*-gate.md` file at the workspace root. If no matching gate file exists, stop and tell the operator — there is nothing to review.

## Step 1 — Load Criteria

Read the quality bar from two sources:

1. `${CLAUDE_PLUGIN_ROOT}/skills/gate-plan/SKILL.md` — Step 3 (quality requirements) and Step 4 (self-assessment questions). These define what a well-formed gate looks like.
2. `${CLAUDE_PLUGIN_ROOT}/skills/gate-plan/references/gate-template.md` — Structural conventions: title format, checkpoint ID patterns, verification method placement, bypass markers, section ordering.

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

**Every checkpoint must produce a positive artifact.** Walk each checkpoint. Does it leave evidence when it passes — output to quote, a file that exists, a count that matches? Flag any checkpoint that could pass silently or proves a negative (absence of errors, no failures, clean exit without observable output). A checkpoint without a defined verification artifact is a blocking deficiency, not a minor finding.

**Checkpoint categories must be declared.** Check whether every checkpoint uses the `[structural]` or `[operational]` tag after the checkpoint ID. Flag any checkpoint without a category tag. For preflight gates, verify at least one `[operational]` checkpoint exists — a preflight gate with only structural checkpoints is a finding at the highest priority, as it has direct Vacuous Green exposure (can clear without proving the deliverable works).

**Pre-clear conditions must pass prospectively.** Evaluate whether the pre-clear detector conditions from gate-work would pass if this gate were executed and all checkpoints cleared as written: (1) would at least one checkpoint be genuinely completed, not all bypassed? (2) would every completed checkpoint have artifact evidence defined? (3) is there a provision for gate review? This catches gates that would fail the pre-clear detector before they reach execution.

**Verification must exercise what it claims to validate.** For each checkpoint with a verification method, check: does the verification actually prove the checkpoint's claim? A header count doesn't prove the right headers exist. A file existence check doesn't prove the file has the right content. Flag verifications that could pass without the validated thing being true.

**Ordering dependencies must be explicit.** Check whether later phases depend on earlier phases producing artifacts. Are these dependencies stated? Could an agent encounter a checkpoint that fails because a prerequisite wasn't documented?

**Specify outcomes, not tool sequences.** Flag checkpoints that prescribe specific tool invocations, command sequences, or step-by-step procedures instead of defining what the result looks like. The gate defines "done," not "how."

**Bypasses are decisions, not shortcuts.** Check any `[~]` markers for inline justification. A bypass without reasoning is a finding.

**Document cleanup expectations.** If the gate produces temporary state (scratch repos, test artifacts, temp files), is the Cleanup section specific about what to remove?

**Scope out explicitly.** Is there an Excluded section? Does it name what the gate deliberately does not cover and why? Missing exclusions leave the executing agent guessing about boundaries.

**Coverage matrix completeness (conditional).** If the gate targets remediations across multiple vectors and multiple lifecycle stages, it must include a coverage matrix. Evaluate three aspects: (1) matrix completeness — every vector-stage cell contains a named enforcement mechanism or an explicit scope-out justification, with no empty cells; (2) mechanism-to-vector alignment — each named mechanism actually closes the vector it claims to at the lifecycle stage where it appears; (3) conditional applicability — the matrix is present when the gate crosses multiple vectors and lifecycle stages, and absent when the gate is single-vector or single-stage (presence in a single-scope gate is not a finding, but absence in a multi-vector gate is). A missing matrix in a multi-vector gate is a blocking deficiency.

**Cross-domain delivery verification (conditional).** If the gate modifies artifacts consumed external to the current domain, it must include at least one checkpoint that verifies consumer reachability through the actual distribution path. Evaluate two aspects: (1) delivery coverage — every cross-domain artifact modified by the gate has a corresponding reachability checkpoint, not just the source-level change; (2) conditional applicability — the delivery checkpoint is present when the gate modifies cross-domain artifacts, and absent when all artifacts are domain-local (presence in a domain-local gate is not a finding, but absence in a cross-domain gate is). A missing delivery checkpoint in a cross-domain gate is a blocking deficiency.

## Step 4 — Self-Assessment Questions

Apply the eight questions from gate-plan Step 4 to the gate as if you were the authoring agent reviewing your own work:

1. If every checkpoint were cleared, does that fully justify the completion criteria? Are there gaps — things the first paragraph claims that no checkpoint validates?
2. Does every checkpoint produce a positive, observable verification? Any that prove negatives or could pass silently?
3. Are all ordering dependencies documented?
4. Could an agent execute this gate top-to-bottom without the operator clarifying sequencing, prerequisites, or intent?
5. Is checkpoint granularity appropriate — unambiguous but not micromanaged?
6. Does the gate include operational checkpoints that verify first-iteration readiness, not just structural completeness?
7. If the gate targets multiple vectors across lifecycle stages, does it include a coverage matrix with zero empty cells?
8. If the gate modifies artifacts consumed external to the current domain, does it include a checkpoint verifying consumer reachability?

Report each question's answer with specific evidence from the gate.

## Step 5 — Findings Report

Summarize the review. Structure:

**Confidence verdict:** Would you present this gate to the operator at 4/5 confidence or above? Yes or no, with reasoning. This maps directly to gate-plan's threshold: "Do not present a draft you assess below 4/5 confidence."

**Structural compliance:** List of compliant/non-compliant template conventions.

**Quality findings:** Each quality requirement that scored fail or partial, with the specific checkpoint(s) affected and what's wrong. Prioritize by impact — a verification that can pass without validating anything is higher priority than a missing Excluded section.

**Self-assessment gaps:** Any of the eight questions that answered "no," with evidence.

**Strengths:** What the gate does well. A review that only reports problems misses the chance to reinforce good patterns.

The operator reads the findings and decides what to fix. The review does not propose rewrites, suggest alternative checkpoints, or offer to regenerate the gate. That's the operator's work or a subsequent gate-plan invocation.

After presenting findings to the operator, append a `## Gate Review` section to the gate document. This records the review outcome and is required by gate-work's pre-clear detector.

The section contains: a `Reviewed:` date line, a `Verdict:` line (PASS or FAIL), and a one-sentence summary. Verdict is PASS when the confidence assessment is 4/5 or above and no blocking deficiencies were found. Otherwise FAIL, with the primary blocking finding stated. Gate-work's pre-clear detector requires `Verdict: PASS` to clear the gate — a FAIL verdict blocks clearance until the gate is revised and re-reviewed.

## Related Skills

- **gate-plan** — Authors gate documents. The review skill audits against plan's quality bar.
- **gate-work** — Executes gate documents. Review sits between plan and work in the lifecycle.

## Reference Files

- **`${CLAUDE_PLUGIN_ROOT}/skills/gate-plan/SKILL.md`** — Quality requirements (Step 3) and self-assessment questions (Step 4) that define the evaluation criteria.
- **`${CLAUDE_PLUGIN_ROOT}/skills/gate-plan/references/gate-template.md`** — Structural conventions for gate documents.
