---
name: spec-review
description: This skill should be used when the user asks to "review a spec", "validate a spec", "is this spec implementable", "critique this spec", "find problems in my spec", "check this design doc", "is this plan sound", "review before implementation", "review this document", "document review", or mentions reviewing specs or structured documents for correctness, implementability, cross-reference consistency, or control-flow soundness before execution begins. Provides a structured multi-round review methodology using targeted subagent prompts that trace state through control flow branches and cross-reference interfaces.
---

# Spec Review — Structured Document Review

The reviewer's director holds the context, writes the subagent prompt, and triages the results.

## Responsibilities

1. Read the target document
2. Construct a targeted subagent prompt (see methodology below)
3. Spawn a fresh general-purpose subagent with that prompt
4. Present findings to the user with severity assessment
5. If the user asks for another round, incorporate prior findings into the next subagent prompt as "already addressed — do not re-flag"

## Subagent prompt methodology

When constructing the subagent prompt, include:

- One-sentence context: what the document is for, what system it targets
- State tracing directive: trace concrete execution through every control flow branch. Track the state of key variables at each step. Look for states where the next operation assumes something that isn't true.
- Cross-reference directive: for every interface/signature, verify return types match callers, error semantics match across sections, and implementation notes match the requirements they describe.
- Concrete scenarios: based on the director's read of the document, identify 3-5 specific scenarios that exercise dangerous intersections. Write them out as "simulate this: [scenario]". These scenarios are the primary value add since the subagent lacks architectural context.
- Do-not list: things already addressed, style/formatting exclusions, performance concerns unless they cause correctness. Grows each round.
- Output format: severity (critical/important/minor), section reference, what goes wrong, why it matters.

## What NOT to do

- Do not send the subagent a generic "review for bugs" prompt
- Do not duplicate the subagent's work by also reviewing the document in the same pass
- Do not combine correctness review and implementability review in one subagent invocation — these are different reviews with different concerns

## Round lifecycle

Round 1 is a broad sweep. Expect 5-15 findings across severity levels.

Subsequent rounds are targeted. Exclude prior findings and focus on areas not yet covered.

Two to three rounds is typically sufficient. After each round, report the severity level of findings and whether another round is likely to surface actionable issues.

Stop after findings drop to minor severity unless the user explicitly requests another round.
