# Gate Template

Structure for gate documents. Gates are production validation plans — they define what must be proven before a body of work can be considered done.

## Structure

```markdown
# Q{n} Gate: {title}

{Completion criteria — one paragraph. What can the operator claim when this gate clears? This paragraph is the soul of the gate. Every checkpoint below must serve this claim. If clearing all checkpoints wouldn't justify this paragraph, the gate is incomplete.}

Depends on: {Q-references to prior gates, or "None"}

## Phase 1: {name}

- [ ] **{ID}** `[structural]` {checkpoint description}

{Verification method — code block, command, or specific observable outcome}
{Artifact evidence — concrete output, file, or result that proves this checkpoint passed}

- [ ] **{ID}** `[operational]` {checkpoint description}

## Phase 2: {name}

...

## Excluded

{What this gate deliberately does not cover and why. Scoping out is a decision, not an omission. Document it.}

## Cleanup

{Artifacts, repos, or temp state to remove after the gate clears.}
```

## Conventions

**Title**: `Q{n} Gate: {descriptive title}`. The Q-number matches QUEUE.md.

**Completion criteria**: First paragraph after the title. Always present. States what success means in concrete terms — not "validate the system works" but "E2E validation of X as a production Y." A practitioner should be able to read this paragraph and know exactly what the gate proves.

**Depends on**: Cross-references to gates that must clear first. Uses Q-numbers. If no dependencies, state "None".

**Phases**: Numbered sequentially. Names describe the phase's purpose. The number of phases is gate-specific — use as many as needed, no more.

**Checkpoint IDs**: Bold, letter prefix + number. The letter is phase-relevant (P for prerequisites, D for deployment, V for verification, etc.). IDs are unique within the gate. Examples: **P1**, **D3**, **V2**, **S1**.

**Verification methods**: Appear below the checkpoint they verify. Code blocks for commands. Inline descriptions for observable outcomes. Every checkpoint must have a verification method — if verification can't be described, it's not a checkpoint.

**Bypass marker**: `[~]` instead of `[ ]` or `[x]`. Used when a checkpoint is deliberately skipped. Justification must appear inline — a bypass without reasoning is a gap, not a decision.

**Checkpoint categories**: Every checkpoint is categorized as `[structural]` or `[operational]`. The category tag appears inline after the checkpoint ID, wrapped in backticks.

- `[structural]` — Verifies that something exists or is correctly formed: file present, command succeeds, format valid, dependency installed. Necessary but not sufficient for proving a deliverable works.
- `[operational]` — Verifies that the deliverable produces meaningful results on first use: pipeline generates discriminating output, tool processes real input, integration completes an end-to-end cycle. Proves the thing works, not just that it's assembled.

Preflight gates must include at least one `[operational]` checkpoint. A preflight gate with only structural checkpoints can clear without proving the deliverable works — this is a Vacuous Green vector. For projects with external runtime dependencies (test fixtures, sample data, API access), fixture presence or a documented acquisition plan is itself a gating requirement, not deferred work.

**Artifact evidence**: Every checkpoint must define what positive artifact proves it passed. A positive artifact is concrete, quotable evidence: command output, file contents, test counts, grep results, or equivalent observable output. Prose-only claims ("verified that X works," "confirmed it runs correctly") are not artifact evidence. A checkpoint without a defined artifact is unverifiable and must be redesigned.

## Sections Added During or After Execution

These are not part of the initial gate template. They emerge during the work.

**Gate Errata**: Issues found in the gate document itself during execution — wrong assumptions, filename mismatches, spec-vs-reality divergences. Captured so the operator can improve future gates.

**Notes**: Edge cases, observations, and context discovered during execution that don't fit into checkpoints.

**Gate Review**: Added by gate-review after auditing the document. Contains a `Reviewed:` date, a `Verdict:` (PASS or FAIL), and a summary. Gate-work's pre-clear detector requires this section with `Verdict: PASS` before the gate can clear.

**Gate Status**: Added when the gate clears. Format: `## Gate Status: CLEARED` followed by validation date and a summary sentence stating what was proven.
