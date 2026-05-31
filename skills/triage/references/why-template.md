# Why-Artifact Template

Structure for a why-artifact. The why-artifact captures the intent behind a queue item *before* the item is scoped — the direction, the named uncertainty, and the conscious scope-carve. It is the frozen v0 record that triage gates on and that aar later diffs the actual outcome against.

It answers WHY, not WHAT. The QUEUE.md `Intent` column and the gate's completion criteria both state WHAT will be done; this artifact states the toward-what the work serves and what the chosen scope deliberately leaves out. One why-artifact per queue item, keyed to the same Q-number, written to the workspace root as `Q{n}-why.md`.

## Structure

```markdown
# Q{n} Why: {short title}

Intent version: v0
Frozen: {date — set only when the cold review returns PASS and the row is written}

## Near-term step

{The immediate thing you can already see clearly. This becomes the QUEUE.md Intent — imperative form. Your sight is strongest here; start here and climb.}

## Direction

{The last clear rung when you climb "in service of what?" from the near-term step — the vector, the toward-what, NOT a specific destination. State the direction you are confident about even though the endpoint is unknown.}

Connects to the vision: {one line tying this direction to the durable vision (Part 0)}

## The fuzz

{What you canNOT see yet — the part of the larger shape you are genuinely unsure of and are protecting against committing to prematurely. Naming it here is what keeps the near-term step from being read as the whole thing.}

## The carve

{"I am scoping the first work to {X}, against the larger shape in Direction / The fuzz. If my read of that larger shape is wrong, this carve forecloses: {what}."}

## Revisit trigger

{The concrete checkpoint where intent gets re-derived once the work surfaces what was not visible at triage — e.g. "after the inventory checkpoints, before recommending." Not "later."}
```

## Sections appended after authoring

Not part of the operator-authored core. Added by triage's cold-review pass.

**Cold Review**: Written by the triage parent skill from the review subagent's returned verdict. Contains a `Reviewed:` date, a `Confidence: N/5`, the findings from the three probes (under-climb, smell-test-cold, direction-vs-destination), an `L3 residue:` note (recorded, non-blocking), and a `Verdict:` (PASS or FAIL). The row is not written until `Verdict: PASS`. On `Verdict: FAIL`, the operator revises the core above and the review re-runs.

```markdown
## Cold Review

Reviewed: {date}
Confidence: {N}/5

- Under-climb: {finding, or "none — direction holds at the top of the confident climb"}
- Smell test (cold): {finding, or "none — near-term step does not read as the endstate"}
- Direction-vs-destination: {finding, or "none — direction reads as a vector"}

L3 residue: {the subagent's read on whether the scope fits the actual question — recorded, not blocking}

Verdict: {PASS | FAIL}
```

## Conventions

**Title**: `Q{n} Why: {short title}`. The Q-number matches the QUEUE.md row and the eventual `Q{n}-gate.md`.

**Frozen marker**: `Intent version: v0` and a `Frozen:` date set at PASS. The authored core is the v0 anchor — once frozen, it is the record aar diffs against. Re-derivation at the revisit trigger happens downstream, during work, and does not overwrite v0.

**Direction is not destination**: the Direction section states a vector, not an endpoint. A Direction line that names a specific fixed endstate is a destination — the cold review flags it.

**WHY, not WHAT**: if a section restates the near-term action instead of the motivation or the foreclosed larger shape, it is in the wrong artifact. The WHAT lives in the QUEUE.md row and the gate; this artifact carries only the WHY.

**Disposability**: intent is a pointer, not a specification. Getting the direction wrong is cheap and reversible; staying silent and letting a narrow scope harden is the expensive, one-way mistake. The artifact is meant to be revisable at its revisit trigger — the freeze captures v0 for the record, not to lock the direction.
