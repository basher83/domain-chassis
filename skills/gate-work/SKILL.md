---
name: gate-work
description: This skill should be used when the user asks to "work the gate", "execute the gate", "run the gate", "work Q3", "run Q3", "do Q3", "execute Q3", "work through the gate", "gate work", "task me with the gate", "resume the gate", or mentions executing against an existing gate file, working through gate checkpoints, resuming a partially-completed gate, or validating against a gate document. Provides the gate execution methodology for working through an operator-authored validation plan.
---

# Gate Work — Gate Execution

You are the executing agent. This skill loads a gate document into your context and you work through it directly. There is no subagent dispatch — you read the gate, adopt the framing below, and do the work.

## Input

The operator provides a gate reference: a Q-number (e.g., "Q3"), a filename (e.g., "Q3-gate.md"), or a path. Resolve to a `*-gate.md` file at the workspace root.

## Step 1 — Resolve and Validate

1. Resolve the gate file at the workspace root. If the file doesn't exist, stop and tell the operator.
2. Read the gate file.
3. Check for `## Gate Status: CLEARED`. If the gate is already cleared, tell the operator and stop. Do not re-execute a cleared gate without explicit confirmation.

## Step 2 — Extract Context

1. **Completion criteria**: The first paragraph after the `# Q{n} Gate:` title and before the first `## ` heading. This is what success means.
2. **Dependencies**: The "Depends on:" line, if present. If the gate depends on an uncleared gate, warn the operator.
3. **Queue context**: Read `QUEUE.md` at the workspace root. Find the matching Q-item for additional context on intent and scope. If no match, proceed without it — the gate file is self-contained.

## Step 3 — Adopt Framing and Begin

After completing Steps 1 and 2, adopt this operational context and begin working through the gate:

The gate file is an operator-authored validation plan. You did not create it. It is not code you can compile or test in that manner. It is a structured set of checkpoints that must be satisfied through real work — executing commands, verifying outputs, producing artifacts, and confirming results.

Your completion criteria: you must be able to claim the extracted completion criteria when done. Every checkpoint in the gate serves that claim. Work through them in order, respecting any stated dependencies between phases.

**How to work the gate:**

- Check off items as you complete them by changing `[ ]` to `[x]` in the gate file.
- Produce the verification each checkpoint requires. If a checkpoint specifies a command, run it. If it specifies an observable outcome, confirm it and document the result.
- Document artifact evidence inline for every checkpoint you complete. When you mark a checkpoint `[x]`, the gate file must contain the concrete evidence that proves it — command output, file contents, counts, or results quoted directly below the checkpoint. A checkpoint marked `[x]` without artifact evidence documented in the gate file is not completed. Either produce the evidence or leave the checkpoint unchecked.
- If a checkpoint cannot be completed, do not mark it `[x]`. Explain what blocked it and continue with unblocked checkpoints. The operator will decide how to proceed.
- If a checkpoint should be bypassed, mark it `[~]` and document the justification inline. Bypasses are decisions — they require reasoning.
- If you discover issues with the gate document itself (wrong assumptions, filename mismatches, spec-vs-reality divergences), document them under a `## Gate Errata` section at the end.
- **Pre-clear detector.** Before writing `## Gate Status: CLEARED`, verify all three conditions. If any condition fails, the gate cannot clear — halt and report to the operator. This is fail-closed: ambiguity on any condition is a halt, not a pass.
  1. At least one checkpoint is marked `[x]` (not all bypassed, deferred, or blocked).
  2. Every checkpoint marked `[x]` has artifact evidence documented inline in the gate file (no prose-only completions).
  3. A `## Gate Review` section exists in the gate document with `Verdict: PASS`, confirming the gate was reviewed and found adequate for execution. A missing review section or `Verdict: FAIL` blocks clearance.
- **Post-clearance exit sequence.** When the pre-clear detector passes, execute the following before stamping CLEARED. Evidence from each step is written into the gate file itself — the gate file is the enforcement contract and must contain complete proof before being sealed. The gate file remains at the workspace root throughout this sequence.
  1. **Commit and push.** All changes produced during gate execution — modified source files and any artifacts referenced by checkpoints — are committed and pushed. Write the commit hash into the gate file. Evidence: commit hash documented in gate file.
  2. **Version bump.** If the gate modified any file within a plugin repository, bump the patch version, commit, and push. Write the new version number and commit hash into the gate file. Evidence: version number and commit hash documented in gate file.
  3. **Consumer reachability (conditional).** If the gate modified artifacts consumed external to the current domain, identify the distribution path and document it in the gate file. Flag the operator on any distribution steps the agent cannot perform (e.g., plugin cache refresh). The agent's obligation is to make the delivery path visible — not to verify or execute distribution. If all artifacts are domain-local, state so explicitly in the gate file.
- **Stamp CLEARED.** Only after the exit sequence completes and all delivery evidence is documented in the gate file, add a `## Gate Status: CLEARED` section with the validation date and a summary sentence stating what was proven. The CLEARED stamp is the seal on the complete contract — checkpoints, review, and delivery proof. Do not stamp CLEARED before the exit sequence is complete.
- **Archive the gate.** Move the cleared gate file from the workspace root to `gates/` (create the directory if it doesn't exist). This is the final step. Nothing follows it. The gate file is the enforcement contract; the archive move releases the contract.
  A cleared gate with uncommitted changes, an unbumped version, or unreachable consumers is delivery without deployment.

The operator is here to assist you, not as a crutch. You may work toward the completion criteria in whatever way you deem appropriate. If you are blocked and cannot unblock yourself, ask. Otherwise, proceed.

## Related Skills

- **gate-plan** — Authors a gate document. Plan creates the gate; work executes it.
- **gate-review** — Audits a gate document against the quality bar. Review sits between plan and work in the lifecycle.
- **prime** — Session context loading. Prime and gate-work are independent — prime loads context, gate-work frames execution against an existing gate.

## Reference Files

- **`${CLAUDE_PLUGIN_ROOT}/skills/gate-plan/references/gate-template.md`** — Gate document conventions: section ordering (phases, errata, notes, status), checkpoint ID format, bypass markers, and verification method placement.
