---
name: gate-plan
description: This skill should be used when the user asks to "create a gate", "plan a gate", "write a gate", "draft a gate", "new gate", "gate Q4", "gate for Q4", "gate plan", "create Q-gate", "gate plan for Q", "write a validation plan", or mentions creating a gate document, drafting validation criteria for a queue item, or planning what needs to be proven before work is considered done. Provides the gate document authoring methodology for creating production validation plans from queue items.
---

# Gate Plan — Gate Document Authoring

Produce a gate document for a queue item. The gate defines what must be proven before the work can be considered done. It is a production validation plan, not a checklist.

## Input

The operator provides a Q-number (e.g., "Q4", "4"). This maps to a row in QUEUE.md.

## Process

### Step 1 — Resolve Context

1. Read `QUEUE.md` at the workspace root. Find the row matching the Q-number. Extract the intent, scope, and next action. If the Q-number doesn't exist in the queue, stop and tell the operator.
2. Check for inter-gate dependencies. If the queue item's Next field references other Q-items, or if the intent logically depends on prior work, check whether those items have gates and whether those gates have cleared. This informs the `Depends on:` field in the gate document.
3. Check if a gate file already exists at the workspace root (`Q{n}-gate.md`). If it does, stop and tell the operator — do not overwrite without explicit confirmation.
4. If the scope references a project directory, read that project's README or top-level structure to understand what's being validated.

### Step 2 — Internalize the Pattern

Read existing `*-gate.md` files at the workspace root and in `gates/` (if more than 3 exist total, focus on the 2-3 with the highest Q-numbers). Active gates live at the workspace root; cleared gates are archived in `gates/`. Both are valid pattern references. The gate template (`references/gate-template.md`) defines the structural standard. The existing gates show how that standard is applied in practice.

Pay attention to:

- How completion criteria are stated (first paragraph — concrete, claimable, specific)
- How phases are scoped (each phase is a coherent stage of validation, not an arbitrary grouping)
- How checkpoints are verified (positive artifacts, not absence of errors)
- How dependencies between checkpoints are documented
- How bypasses are justified inline
- How the Excluded and Cleanup sections scope the work

### Step 3 — Draft the Gate

Write the gate document. Apply these quality requirements:

**Completion criteria must be claimable.** The first paragraph states what the operator can claim when the gate clears. "Validate the system" is vague. "Targeted extraction across 5 implementations to understand how different engineers solve X" is claimable — it names the scope, the method, and what understanding is produced. A practitioner should read the completion criteria and know exactly what was proven.

**Every checkpoint must produce a positive artifact.** A passing checkpoint must leave evidence that it passed. Command output to quote, a file that exists, a document with specific content, a count that matches an expectation. If a checkpoint can pass when nothing happens — no output, no artifact, silent success — it's proving a negative. Design checkpoints that succeed visibly, not ones that pass by default. This is a hard requirement: a checkpoint without a defined verification artifact is a blocking deficiency in the self-assessment (Step 4), not a suggestion to improve.

**Every checkpoint must be categorized as structural or operational.** Use the `[structural]` or `[operational]` tag after the checkpoint ID as defined in the gate template. Structural checkpoints verify existence or form — file present, format valid, command succeeds. Operational checkpoints verify that the deliverable produces meaningful results — pipeline generates output, tool processes real input, integration completes a cycle. Preflight gates must include at least one `[operational]` checkpoint. A preflight gate with only structural checkpoints has direct Vacuous Green exposure and must not be presented — it fails the self-assessment in Step 4.

**Verification must exercise what it claims to validate.** If a checkpoint says "study document produced," the verification must confirm the document exists and contains the expected sections — not just that the command exited cleanly. If a checkpoint says "all 5 repos on disk," the verification lists them. Don't write a checkpoint that could pass without the thing it validates actually being true.

**Ordering dependencies must be explicit.** If a verification phase depends on prior phases producing artifacts, say so. If a checkpoint assumes setup from an earlier phase, document the assumption. An agent executing this gate top-to-bottom should never hit a checkpoint that fails because a prerequisite wasn't stated.

**Specify outcomes, not tool sequences.** Don't prescribe the mechanical steps to achieve a checkpoint. Specify what the result looks like, not how to get there. The executing agent chooses its own approach — the gate defines what "done" means for each checkpoint, not the procedure.

**Bypasses are decisions, not shortcuts.** `[~]` requires inline justification explaining why the checkpoint is being skipped and what risk is accepted. A bypass without reasoning is a gap.

**Document cleanup expectations.** If the gate produces temporary artifacts, test repos, or scratch state, the Cleanup section should specify what to remove after the gate clears. An executing agent should know what to tear down when done.

**Scope out explicitly.** If something is deliberately not covered, it belongs in the Excluded section with a reason. This prevents an executing agent from scope-creeping into adjacent validation and prevents the operator from wondering why something was missed.

**Multi-vector gates require a coverage matrix.** When a gate targets remediations across multiple vectors and multiple lifecycle stages, the gate document must include a coverage matrix mapping every identified vector (rows) to every applicable lifecycle stage (columns), with the enforcement mechanism named in each cell. Empty cells are gaps — they represent vector-stage combinations where no enforcement exists. All empty cells must be addressed (filled with a mechanism or explicitly scoped out with justification) before the gate is presented. This requirement applies only to gates that cross both multiple vectors and multiple lifecycle stages; single-vector or single-stage gates are not required to produce a matrix.

**Cross-domain reachability requires a delivery checkpoint.** When a gate modifies artifacts consumed external to the current domain, the gate must include at least one checkpoint verifying the changes are reachable to that domain. "External to the current domain" means the artifact's consumer operates in a different domain than where the gate executes — a chassis skill modified in Workshop but consumed by Forge agents, a vault artifact produced in Research but referenced in Lab. The checkpoint must verify reachability through the actual distribution path (plugin cache version, vault file presence, deployed configuration), not just source-level correctness (repo commit, file content). A gate that validates source changes without verifying consumer reachability has proven correctness but not delivery. This requirement applies only to gates modifying cross-domain artifacts; gates whose artifacts are consumed entirely within the authoring domain are not required to include a delivery checkpoint. When the distribution path requires operator action or depends on platform mechanics outside the gate agent's control (e.g., plugin cache refresh, manual deployment), the gate may scope out delivery verification in the Excluded section with reasoning that names what the agent cannot control and why the in-scope checkpoints already cover correctness. This is a valid resolution, not a blocking deficiency.

### Step 4 — Self-Assess Before Presenting

Before showing the draft to the operator, evaluate it:

1. If every checkpoint were cleared, does that fully justify the completion criteria in the first paragraph? If not, there are missing checkpoints.
2. Does every checkpoint produce a positive, observable verification? Flag any that prove negatives or could pass silently.
3. Are all ordering dependencies between checkpoints and phases documented?
4. Could an agent execute this gate top-to-bottom without the operator having to clarify sequencing, prerequisites, or intent?
5. Is the checkpoint granularity appropriate — detailed enough to be unambiguous, not so granular that it's micromanagement?
6. Does the gate include operational checkpoints that verify first-iteration readiness, not just structural completeness?
7. If the gate targets multiple vectors across lifecycle stages, does it include a coverage matrix with zero empty cells?
8. If the gate modifies artifacts consumed external to the current domain, does it include a checkpoint verifying consumer reachability — or, if the distribution path is outside the agent's control, does it scope out delivery verification with reasoning in the Excluded section?

If the answer to any of these is no, fix the gaps before presenting. Do not present a draft you assess below 4/5 confidence and ask the operator to identify what's wrong. That's the operator's time wasted on work the agent should have caught.

### Step 5 — Output

Write the gate file to the workspace root as `Q{n}-gate.md`. Present a brief summary of what the gate covers and how many phases/checkpoints it contains. The operator will review and may request changes.

## Related Skills

- **gate-review** — Audits a gate document against the quality bar defined here. Review sits between plan and work in the lifecycle.
- **gate-work** — Frames an agent to execute an existing gate. Plan creates the gate; work executes it.
- **prime** — Session context loading. Prime and gate-plan are independent — prime loads context, gate-plan authors a gate document.

## Reference Files

- **`references/gate-template.md`** — Structural template for gate documents. Conventions for titles, phases, checkpoints, verification methods, and operational sections.
