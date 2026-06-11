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

### Step 0 — Bind the Input

Triage's input is not a parameter sitting where this skill's body can see it. The harness appends it as an `ARGUMENTS` block *after* this skill's body — that trailing block is the operator's articulation described in `## Input` above: the candidate piece of work and the durable-vision pointer Step 2 climbs from. Read that block as the substrate of the whole triage, not as optional flags. If no `ARGUMENTS` block was appended — the skill was invoked bare — do not proceed against an empty input or invent a candidate: elicit the articulation from the operator (the near-term step and the vision it serves) before Step 1.

### Step 1 — Scaffold the Why-Draft

No Q-number is minted yet. The number is a stable identifier pinned for the item's lifetime, and it is assigned only at commit (Step 5) — the first moment the item is certain to become a queue row — so work that may never reach a row never claims a number. Scaffold the why-draft now, under a slug name, with the deterministic script (run from the workspace root):

```bash
node ${CLAUDE_PLUGIN_ROOT}/skills/triage/scripts/next-q.mjs scaffold
```

It writes `Q-draft-{slug}-why.md` at the workspace root from `references/why-template.md` — the operator-authored core, `Intent version: v0`, and a blank `Frozen:`. The script is `now.mjs`-shaped: plain `node`, dependency-free, no bun, no `NODE_PATH`, no credential. The slug-named draft claims no number by construction — a `Q-draft-…` name has a non-digit after `Q`, so the Step-5 `max(Q[0-9]+)+1` computation cannot see it, and an abandoned triage leaves no number-claiming orphan.

### Step 2 — Articulate the Why

Elicit from the operator, climbing from where their sight is strongest. Do not start at the top — near-term sight is the strong instrument.

1. **Near-term step** — the immediate thing they can already see clearly. This becomes the QUEUE.md `Intent` (imperative form).
2. **Climb** — ask "in service of what?" and repeat, rung by rung, until the answer goes fuzzy. The last rung answered confidently is the direction. If the operator stops climbing readily, push one rung past the first hesitation and capture that rung even at low confidence — a wrong high rung is disposable; a missing one is the failure.
3. **Direction** — the vector, the toward-what; NOT a specific destination. Capture the direction even when the endpoint is unknown, plus one line connecting it to the durable vision.
4. **The fuzz** — what they canNOT see yet: the part of the larger shape they are genuinely unsure of and are protecting against committing to prematurely. Naming it is what keeps the near-term step from being read as the whole thing.
5. **The carve** — the conscious narrowing: "scoping the first work to X, against the larger shape; if that read is wrong, this forecloses ___."
6. **Revisit trigger** — the concrete checkpoint where intent gets re-derived once the work surfaces what was not visible now. Not "later."

Write these into the `Q-draft-{slug}-why.md` scaffold from Step 1, following `references/why-template.md`. Do not set the `Frozen:` date — the commit step (Step 5) stamps it at PASS.

### Step 3 — Cold Review

The review must be cold: it cannot see the elicitation above, or it inherits the same context that produced the narrowing. The cold review is performed by a standalone reviewer script whose **only** interface is the artifact path — the parent cannot pass the Step 2 elicitation, or any other context, into the review even if it tries. That mechanical boundary is what makes the review cold; it replaces the prior fresh-context subagent dispatch, which isolated context but left prompt fidelity to the parent's good behavior.

Run the reviewer with a single `Bash` call, passing the absolute path to the `Q-draft-{slug}-why.md` draft as the sole argument:

```bash
NODE_PATH="${CLAUDE_PLUGIN_DATA}/node_modules" bun ${CLAUDE_PLUGIN_ROOT}/skills/triage/scripts/cold-review.ts <abs-path-to-Q-draft-{slug}-why.md>
```

Do not add arguments, environment variables, or stdin intending to inform the review — the script reads only the artifact at the path, and nothing else reaches the review prompt (an extra positional argument is a hard error). The script's system prompt is the version-controlled review contract: the three probes (under-climb; cold smell-test; direction-vs-destination) and the structured verdict shape. See `scripts/cold-review.ts` and `${CLAUDE_PLUGIN_ROOT}/adrs/ADR-002-triage-cold-review-reviewer.md` for the authoritative probe definitions, the default reviewer model and effort, the `--model` cross-model override, and the fail-closed credential contract.

The script prints a single JSON object — `confidence` (1–4; 5 is unreachable), per-probe `probes` findings, `blocking_deficiencies`, `l3_residue`, and a derived `verdict` — and exits non-zero, emitting no verdict, if it cannot run (missing runtime, missing credential, model error). Its dependencies are installed into the plugin's persistent data dir (`${CLAUDE_PLUGIN_DATA}/node_modules`) by the chassis `SessionStart` hook (`${CLAUDE_PLUGIN_ROOT}/hooks/ensure-reviewer-deps.sh`) and resolved via `NODE_PATH`; a Pi-configured credential (`~/.pi/agent`) is also required. See ADR-002.

### Step 4 — Verdict Gate (fail-closed)

If the script exited non-zero, it could not produce a review: **halt**. Do not fabricate a verdict, do not fall back to an in-context review, do not proceed to Step 5 — surface the script's error to the operator. This is the fail-closed boundary.

On a zero exit, take the script's JSON output and apply the verdict rule:

- A missing or placeholder Direction, fuzz, carve, or revisit trigger is a **blocking deficiency** (structural) — the script reports these in `blocking_deficiencies`.
- **PASS** iff `confidence` is `4` (the top of the 1–4 scale; 5 is unreachable) and there are no blocking deficiencies.
- **FAIL** iff `confidence` is `≤3` or any blocking deficiency exists.
- The `l3_residue` note is recorded and surfaced to the operator but never changes the verdict — an agent hard-judging "is the scope right for the actual question" is the wrong inhabitant for that seat; the operator is.

The script computes a `verdict` field applying exactly this rule; you may use it directly, but the rule above is authoritative. Append a `## Cold Review` section to the `Q-draft-{slug}-why.md` draft (reviewed date, confidence, findings, L3 residue, verdict) per the template.

On **FAIL**: report the findings to the operator, let them revise the why-artifact's core, and re-run Step 3. This is fail-closed — do not proceed to Step 5 on an unresolved FAIL or on ambiguity about any condition.

### Step 5 — Commit (on PASS)

The number is assigned now — at PASS, the first moment the item is certain to become a queue row. Run the commit half of the script against the draft (from the workspace root):

```bash
node ${CLAUDE_PLUGIN_ROOT}/skills/triage/scripts/next-q.mjs commit --draft <abs-path-to-Q-draft-{slug}-why.md>
```

It computes `max(Q[0-9]+)+1` over the union of all three durable sources — `QUEUE.md` rows, root `Q{n}-*.md`, and `gates/Q{n}-*.md` — renames the draft to `Q{n}-why.md`, stamps its `Frozen:` line with the UTC instant (the authored core is now the v0 anchor), substitutes the number into the title, and emits a `QUEUE.md` row stub carrying `Q{n}`. The script owns the number and the row; the prose cells are yours.

Numbers are assigned and never reassigned, and the sequence is deliberately allowed to have gaps — a retired or skipped number is simply absent, and non-contiguous Q-numbers are normal, not a defect to close. Because the number is computed at commit over what actually exists on disk (the three sources above), an item that never reaches this step leaves no number behind to collide with; the old `max + 1` collision hazard, and the operator-confirmation backstop it required, are dissolved rather than guarded.

Then:

1. Fill the emitted row's prose cells — `{near-term step, imperative}`, `{project link or domain}`, `{immediate next action or blocker}` — and append the completed row to `QUEUE.md` at the workspace root.
2. Leave `Q{n}-why.md` at the workspace root — it is the durable v0 record and the on-disk trace that keeps its number from being recomputed.
3. Present a one-line summary: the Q-number assigned, the direction, and the carve.

The row is now ready for gate-plan.

## Related Skills

- **gate-plan** — Binds to the QUEUE.md row triage produces; reads its intent, scope, and next, and reads the frozen `Q{n}-why.md` alongside it (gate-plan Step 1) to author against the frozen direction and carve. Triage creates the row and the why-record; gate-plan expands them into a gate.
- **prime** — Loads session context including `QUEUE.md` and `TRIAGE.md`. Triage creates the rows prime later summarizes; prime never creates them.
- **aar** — At close, the frozen `Q{n}-why.md` is the canonical intended-outcome record the after-action diff compares against, rather than operator memory. Wiring aar's "Expectations vs Reality" to read it is a separate one-line delta to the aar skill.

## Reference Files

- **`scripts/next-q.mjs`** — Deterministic, dependency-free (`now.mjs`-shaped) Q-number resolution and why-draft scaffolding for Steps 1 and 5. `scaffold` mints the slug-named draft (no number); `commit` computes `max(Q[0-9]+)+1` over the three durable sources, renames the draft to `Q{n}-why.md`, and stamps `Frozen:` at PASS.
- **`references/why-template.md`** — Structural template for the why-artifact: the operator-authored core and the appended cold-review section.
- **`${CLAUDE_PLUGIN_ROOT}/skills/gate-plan/SKILL.md`** — The next lifecycle step. Triage's output — the QUEUE.md row plus the frozen `Q{n}-why.md` — is gate-plan's input (gate-plan Step 1 reads both).
