# Gate Template

Structure for gate documents. Gates are production validation plans — they define what must be proven before a body of work can be considered done.

## Structure

```markdown
# Q{n} Gate: {title}

{Completion criteria — one paragraph. What can the operator claim when this gate clears? This paragraph is the soul of the gate. Every checkpoint below must serve this claim. If clearing all checkpoints wouldn't justify this paragraph, the gate is incomplete.}

Depends on: {Q-references to prior gates, or "None"}
Builds on: {Q-references to predecessor gates whose load-bearing semantics this gate reuses, or "None"}

## Inherited from {predecessor}

{Present only when `Builds on:` is non-None. Transcribes the load-bearing fraction — the runtime, fixtures, contracts, or baseline values the successor actually reuses — so a cold gate-work executor reaches it from this single file without opening the predecessor.}

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

**Builds on** (a.k.a. **Inherits from**): Cross-references to predecessor gate(s) whose load-bearing semantics — runtime, fixtures, contracts, or baseline values — this gate *reuses*. Distinct from `Depends on:`, which names gates that must *clear first*: a gate may build on a cleared predecessor it does not depend on (Q70 builds on the cleared Q66 while its `Depends on:` reads "None"). Uses Q-numbers; if the gate reuses no predecessor's load-bearing semantics, state "None". When `Builds on:` is non-None, the gate must carry a matching `## Inherited from {predecessor}` section.

**Inherited from {predecessor}** (conditional section): Present when — and only when — `Builds on:` is non-None. It transcribes the *load-bearing fraction* of the predecessor (the runtime, fixtures, contracts, or baseline values the successor actually reuses), not the whole predecessor, so a cold `gate-work` executor reaches that context from the single file it loads without opening the predecessor. The heading names the predecessor (`## Inherited from Q66`). Presence of this section against a non-None `Builds on:` is enforced by the deterministic checker `check-inheritance.py`, run from gate-plan (authoring self-check) and gate-review (verdict input); the checker enforces section presence and predecessor-name match, not transcription completeness or correctness — that remains gate-review's judgment.

**Phases**: Numbered sequentially. Names describe the phase's purpose. The number of phases is gate-specific — use as many as needed, no more.

**Checkpoint IDs**: Bold, letter prefix + number. The letter is phase-relevant (P for prerequisites, D for deployment, V for verification, etc.). IDs are unique within the gate. Examples: **P1**, **D3**, **V2**, **S1**.

**Verification methods**: Appear below the checkpoint they verify. Code blocks for commands. Inline descriptions for observable outcomes. Every checkpoint must have a verification method — if verification can't be described, it's not a checkpoint.

**Bypass marker**: `[~]` instead of `[ ]` or `[x]`. Used when a checkpoint is deliberately skipped. Justification must appear inline — a bypass without reasoning is a gap, not a decision.

**Checkpoint categories**: Every checkpoint is categorized as `[structural]` or `[operational]`. The category tag appears inline after the checkpoint ID, wrapped in backticks.

- `[structural]` — Verifies that something exists or is correctly formed: file present, command succeeds, format valid, dependency installed. Necessary but not sufficient for proving a deliverable works.
- `[operational]` — Verifies that the deliverable produces meaningful results on first use: pipeline generates discriminating output, tool processes real input, integration completes an end-to-end cycle. Proves the thing works, not just that it's assembled.

Preflight gates must include at least one `[operational]` checkpoint. A preflight gate with only structural checkpoints can clear without proving the deliverable works — this is a Vacuous Green vector. For projects with external runtime dependencies (test fixtures, sample data, API access), fixture presence or a documented acquisition plan is itself a gating requirement, not deferred work.

**Anti-pattern tags**: Checkpoints that guard against known anti-patterns from the anti-pattern registry (`references/anti-pattern-registry.md`) carry an inline tag referencing the AP-nn entry. The tag uses curly braces inside backticks — `` `{AP-nn}` `` — and appears after the category tag, before the checkpoint description:

```markdown
- [ ] **V1** `[operational]` `{AP-07}` Pipeline produces discriminating output on first run
```

Tags are optional. Apply them only when the checkpoint genuinely guards against the referenced anti-pattern — the checkpoint must prevent or detect the named failure mode. Not every checkpoint has anti-pattern relevance, and forcing tags where none applies degrades the signal. A checkpoint with no applicable anti-pattern remains untagged.

When a checkpoint guards against multiple anti-patterns, list the AP-nn entries comma-separated within a single tag: `` `{AP-07, AP-10}` ``. Each referenced entry must exist in the registry. Order within the tag does not imply priority.

The anti-pattern tag is a gate-authoring standard with the same normative status as the category tag and bypass marker conventions. Tagged checkpoints inform both review (tag validity and semantic accuracy) and execution (verification rigor calibrated to the failure mode).

**Decision-token legend**: When — and only when — a gate cites decision-record tokens, it carries a **Decision-Token Legend** resolving each cited token to one decision title and one source pointer. A decision-record token is a short identifier standing in for a recorded decision: `d-NNNN`, `ADR-NNNN`, or an equivalent external decision ID. A gate that cites no such tokens does not carry a legend — the convention is conditional, not a blanket requirement on every gate. Anti-pattern tags (`{AP-nn}`) are **not** decision-record tokens: they resolve against the anti-pattern registry separately and never trigger a legend.

The **source pointer** uses the syntax `<corpus-path>#<record-id>`, where `<corpus-path>` is a path resolvable workspace-root-relative to the corpus that holds the decision and `<record-id>` is the record's own identifier (for example, a JSON `id` field). For a one-record-per-file corpus — such as an ADR markdown file — the file path is the record and the `#<record-id>` anchor is optional.

The legend is the **authoritative resolution** of a token's identity. Inline mentions of a token in the gate's prose may add context, but must not restate the decision's identity; where prose and legend disagree, the legend governs. Resolve each token against its own source once, at authoring time, and record the title and pointer — do not key the legend off a secondary citation (another gate, a triage note, a prior review), which can itself be wrong.

The convention is enforced by a deterministic checker shipped in the chassis and run from the gate-plan (authoring self-check) and gate-review (verdict input) skills. The checker resolves every legend pointer against its corpus and returns a non-zero exit when an entry is missing, a pointer is malformed or dangling, or a stated title grossly mismatches the resolved record — so a misattributed citation is caught structurally, not left to a reader's spot-check.

```markdown
## Decision-Token Legend

| Token | Decision title (resolved against source) | Source pointer |
|-------|------------------------------------------|----------------|
| `d-0008` | Audit reviewer is claude-opus-4-7; builder was GPT-5.5 | `latent-space/.questionnaire/2026-05-28:01-53-48/state.json#d-0008` |
```

**Artifact evidence**: Every checkpoint must define what positive artifact proves it passed. A positive artifact is concrete, quotable evidence: command output, file contents, test counts, grep results, or equivalent observable output. Prose-only claims ("verified that X works," "confirmed it runs correctly") are not artifact evidence. A checkpoint without a defined artifact is unverifiable and must be redesigned.

## Sections Added During or After Execution

These are not part of the initial gate template. They emerge during the work.

**Gate Errata**: Issues found in the gate document itself during execution — wrong assumptions, filename mismatches, spec-vs-reality divergences. Captured so the operator can improve future gates.

**Notes**: Edge cases, observations, and context discovered during execution that don't fit into checkpoints.

**Gate Review**: Added by gate-review after auditing the document. Contains a `Reviewed:` date, a `Verdict:` (PASS or FAIL), and a summary. Gate-work's pre-clear detector requires this section with `Verdict: PASS` before the gate can clear.

**Gate Status**: Added when the gate clears. Format: `## Gate Status: CLEARED` followed by validation date and a summary sentence stating what was proven.
