---
name: triage
description: Articulates the why behind a candidate queue item — its direction, its named uncertainty, and the conscious scope-carve — and gates it through a cold-context review before writing the QUEUE.md row that the gate lifecycle binds to.
when_to_use: Use when the user asks to triage an item, add something to the queue, create a queue item or Q-row, intake new work, or articulate intent before scoping.
---

# Triage — Why-Articulation and Queue Entry

Turn a candidate piece of work into a QUEUE.md row, but only after its *why* is articulated and a cold review confirms the scope has not silently collapsed to the nearest visible step. Triage is the lifecycle step before gate-plan: nothing else creates the queue row that gate-plan binds to.

The failure this guards against: scoping a work item to the nearest clearly-visible step while the larger shape is still fuzzy, committing silently to the smallest possible scope, and letting that narrow scope harden into architecture downstream. A narrow scope is not a neutral starting point — it is a commitment to the smallest shape, usually made without noticing. Triage forces the narrowing to happen out loud and gates on it.

## Input

The operator brings a candidate piece of work — a near-term step they can already see clearly — and references the durable vision (Part 0). No Q-number is supplied; triage assigns it. There is no upstream artifact; the operator's articulation is the input.

## Process

### Step 1 — Resolve the Next Q-number

The Q-number is a stable identifier pinned to the item for its lifetime; retired numbers are never reassigned. No ledger exists, so compute the next number from the durable record on disk:

1. Read `QUEUE.md` at the workspace root (live rows).
2. List `Q{n}-*.md` at the workspace root (active gates and any prior why-artifacts) and in `gates/` (the cleared archive).
3. The next number is `max(all Q-numbers in that union) + 1`. State the proposed number to the operator before using it.

Known hazard: `max + 1` is collision-proof only for numbers that left a durable artifact. A number retired *without* ever producing a `Q{n}-*.md` file leaves no trace, so if the current-highest item were retired that way, `max + 1` could recompute it and violate "never reassigned." The `Q{n}-why.md` this skill writes (Step 2) closes that gap going forward — every triaged number now leaves a record — but for numbers retired before triage existed, the operator's confirmation of the proposed number is the backstop. If the operator flags the proposed number as a known retiree, increment past it.

### Step 2 — Articulate the Why

Elicit from the operator, climbing from where their sight is strongest. Do not start at the top — near-term sight is the strong instrument.

1. **Near-term step** — the immediate thing they can already see clearly. This becomes the QUEUE.md `Intent` (imperative form).
2. **Climb** — ask "in service of what?" and repeat, rung by rung, until the answer goes fuzzy. The last rung answered confidently is the direction. If the operator stops climbing readily, push one rung past the first hesitation and capture that rung even at low confidence — a wrong high rung is disposable; a missing one is the failure.
3. **Direction** — the vector, the toward-what; NOT a specific destination. Capture the direction even when the endpoint is unknown, plus one line connecting it to the durable vision.
4. **The fuzz** — what they canNOT see yet: the part of the larger shape they are genuinely unsure of and are protecting against committing to prematurely. Naming it is what keeps the near-term step from being read as the whole thing.
5. **The carve** — the conscious narrowing: "scoping the first work to X, against the larger shape; if that read is wrong, this forecloses ___."
6. **Revisit trigger** — the concrete checkpoint where intent gets re-derived once the work surfaces what was not visible now. Not "later."

Write these into `Q{n}-why.md` at the workspace root, following `references/why-template.md`. Do not set the `Frozen:` date yet — that is set at PASS in Step 4.

### Step 3 — Cold Review

The review must be cold: it cannot see the elicitation above, or it inherits the same context that produced the narrowing. Delegate it to a subagent with a fresh context window.

Dispatch one subagent using the Agent tool, in a single foreground call (do not set `run_in_background`), and block until it returns. Brief it with **only** the absolute path to `Q{n}-why.md` and the instruction to read that file and nothing else — not `QUEUE.md`, not other gates, not this conversation. Do not restate any of the Step 2 elicitation in the briefing. Its entire evidence base is the artifact; that is what makes the review cold.

Instruct the subagent to run three probes against the artifact and return a structured verdict:

1. **Under-climb probe** — take the stated Direction and try to answer "in service of what?" one rung above it. If a confident answer exists, the operator stopped climbing too low → finding.
2. **Smell test, read cold** — read the Near-term step alone. Could it reasonably be read as the entire endstate? If yes, the narrowing is silent → finding.
3. **Direction-vs-destination** — does the Direction name a specific fixed endpoint rather than a vector? If it reads as a destination → finding.

The subagent returns: a confidence score `N/5` (5 is declared unreachable), the findings from the three probes, and an `L3 residue` note answering "is the scope even right for the actual question?" — recorded as judgment, never as a block.

### Step 4 — Verdict Gate (fail-closed)

Take the subagent's return and apply the verdict rule:

- A missing or placeholder Direction, fuzz, carve, or revisit trigger is a **blocking deficiency** (structural).
- **PASS** iff confidence is `4/5` and there are no blocking deficiencies.
- **FAIL** iff confidence is `≤3/5` or any blocking deficiency exists.
- The `L3 residue` note is recorded and surfaced to the operator but never changes the verdict — an agent hard-judging "is the scope right for the actual question" is the wrong inhabitant for that seat; the operator is.

Append a `## Cold Review` section to `Q{n}-why.md` (reviewed date, confidence, findings, L3 residue, verdict) per the template.

On **FAIL**: report the findings to the operator, let them revise the why-artifact's core, and re-run Step 3. This is fail-closed — do not proceed to Step 5 on an unresolved FAIL or on ambiguity about any condition.

### Step 5 — Output (on PASS)

1. Set the `Frozen:` date in `Q{n}-why.md`. The authored core is now the v0 anchor.
2. Append the row to `QUEUE.md` at the workspace root:

   ```markdown
   | Q{n} | {near-term step, imperative} | {project link or domain} | {immediate next action or blocker} |
   ```

3. Leave `Q{n}-why.md` at the workspace root — it is the durable v0 record (and the retired-number trace from Step 1).
4. Present a one-line summary: the Q-number assigned, the direction, and the carve.

The row is now ready for gate-plan.

## Related Skills

- **gate-plan** — Binds to the QUEUE.md row triage produces; reads its intent, scope, and next. Triage creates the row; gate-plan expands it into a gate.
- **prime** — Loads session context including `QUEUE.md` and `TRIAGE.md`. Triage creates the rows prime later summarizes; prime never creates them.
- **aar** — At close, the frozen `Q{n}-why.md` is the canonical intended-outcome record the after-action diff compares against, rather than operator memory. Wiring aar's "Expectations vs Reality" to read it is a separate one-line delta to the aar skill.

## Reference Files

- **`references/why-template.md`** — Structural template for the why-artifact: the operator-authored core and the appended cold-review section.
- **`${CLAUDE_PLUGIN_ROOT}/skills/gate-plan/SKILL.md`** — The next lifecycle step. Triage's output (the QUEUE.md row) is gate-plan's input.
