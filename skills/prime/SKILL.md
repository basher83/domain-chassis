---
name: prime
description: This skill should be used when the user asks to "prime the session", "load context", "session context", "orient me", "what's in flight", "prime", "start the session", "load domain context", "what's the current state", or mentions loading initial context for a working session, getting oriented on the current state of things, or wanting a summary of active work and queue state. Provides session context loading by reading the doctrine, project index, queue, and triage state.
---

# Prime — Session Context Loading

Read the domain's core files and summarize the current state for the operator.

## Process

### Step 1 — Load Doctrine

Discover the domain's doctrine file at the workspace root. Look for files matching known domain doctrine names: `FORGE.md`, `WORKSHOP.md`, `LAB.md`, `RESEARCH.md`. Read whichever one exists.

If multiple doctrine files are found, warn the operator — a workspace should belong to exactly one domain. If no doctrine file is found, note its absence and continue with the remaining steps.

### Step 2 — Load Project Index

Read `PIN.md` at the workspace root — the project index tracking what's here and what state it's in. If PIN.md does not exist, note its absence and skip.

List the subdirectories in the workspace root to cross-reference against PIN.md entries. Exclude `gates/` — that's the gate archive, not a project. Validate PIN.md against the workspace standard (`references/workspace-standard.md`). Flag stale status values, PIN.md entries without a directory on disk, or directories on disk without PIN.md entries. Don't block on these — report them as part of the summary.

### Step 3 — Load Queue

Read `QUEUE.md` at the workspace root — the operational intent tracker. If QUEUE.md does not exist, note its absence and skip.

### Step 4 — Check Triage

Check `TRIAGE.md` — raw intake. Only check whether content exists below the `---` separator. If content exists, output exactly this line and nothing more: "TRIAGE.md has pending intake — triage when ready?" Do not read the file contents. Do not list, describe, or summarize what is in TRIAGE.md. The operator knows what they put there.

### Step 5 — Summarize

Summarize current state: active projects, what state they're in, what needs attention, and what the operator is currently working on (from the queue).

Keep the summary concise. Focus on current state: what's in flight, what's converged, what needs attention, and what intent is queued. If workspace hygiene issues are found, note them briefly at the end.

## Reference Files

- **`references/workspace-standard.md`** — Workspace organization: domain workspace principles, PIN.md structure, QUEUE.md schema, TRIAGE.md lifecycle, workspace hygiene rules
