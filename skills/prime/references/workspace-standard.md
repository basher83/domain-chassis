# Workspace Standard

How domain workspaces are organized. Each domain (forge, workshop, lab, research) has a workspace directory that serves as the operational surface for that domain's work. Projects come and go; the workspace tracks what's currently here and what's being done with it.

## Workspace Principles

The workspace directory is not git-tracked at the root level. It has no `.git`, no commit history, no branches. This is by design.

The workspace is an ephemeral container for operational work. The repos inside it are git-tracked individually. The flat files at the root (PIN.md, QUEUE.md, TRIAGE.md, and the doctrine file) are workspace state that describes the present, not the past.

Agents operating in the workspace must not assume git tracking at the workspace root. Do not run `git status`, `git add`, or any git operations against the workspace directory itself. Each project inside the workspace manages its own git state independently.

## Workspace Files

Every domain workspace has four files at its root:

| File | Purpose |
|------|---------|
| `{DOMAIN}.md` | Operating doctrine for this domain (FORGE.md, WORKSHOP.md, LAB.md, RESEARCH.md) |
| `PIN.md` | Project index — what's here and what state it's in |
| `QUEUE.md` | Operational intent — what's being worked on and what's next |
| `TRIAGE.md` | Raw intake — unprocessed items awaiting triage |

## PIN.md — Project Index

PIN.md is the workspace routing table. It answers "what's here and what state is it in" for both the operator and the prime skill.

Each domain defines its own categories and table schemas based on the types of work it contains. Categories are markdown sections with tables. Section ordering should progress from most active to most speculative.

### Format

```markdown
# {Domain Name}

{One-sentence workspace description.}

## {Category 1}

| Column1 | Column2 | ... |
|---------|---------|-----|

## {Category 2}

| Column1 | Column2 | ... |
|---------|---------|-----|
```

### Requirements

- Every repo in the workspace has a PIN.md row. If it doesn't have a row, it shouldn't be in the workspace.
- Status values (when used) should be a closed set defined by the domain. Document what each status means so agents can validate them.
- Section ordering is fixed per domain. Empty sections can be omitted but the order must be preserved when present.

## QUEUE.md — Operational Intent

PIN.md tracks what's in the workspace. QUEUE.md tracks what the operator intends to do with it. Goals, evaluation criteria, cross-cutting work — operational intent that would otherwise live only in the operator's head between sessions.

### Schema

| Column | Required | Content |
|--------|----------|---------|
| Q | Yes | Stable identifier. `Q1`, `Q2`, etc. Pinned to the intent for its lifetime. When an item is removed, its number retires — never reassigned. New items get the next unused number. Used for cross-referencing between items, across sessions, and in operator commands. |
| Intent | Yes | What to accomplish. Imperative form. |
| Scope | Yes | Project link (relative to workspace root) or domain name for cross-cutting work. |
| Next | Yes | Immediate next action or current blocker. Use Q-references for dependencies (e.g. "Blocked by Q2"). |

### Format

```markdown
# Queue

{One-sentence description of what the queue tracks for this domain.}

| Q | Intent | Scope | Next |
|---|--------|-------|------|
```

### Lifecycle

Items are added when work begins, updated as next actions change, removed when done. The queue itself is ephemeral — it tracks live operational state, not history. No status column. If it's in the queue, it's active. If it's done, remove it.

## TRIAGE.md — Raw Intake

A dump zone for links, repos, ideas, and work items. No schema, no structure required. The operator drops things here while working or while other sessions are running. The prime skill checks for content at session start and offers to triage if present.

Content below the `---` separator is intake. Everything above is the template header.

### Lifecycle

Items accumulate until a triage session processes them. Triage means: evaluate each item, decide what to act on and what to discard, wire keepers into PIN.md and QUEUE.md, discard the rest. After triage, clear the processed items from TRIAGE.md.

TRIAGE.md is never flagged by hygiene rules — having pending intake is normal, not a hygiene issue.

## Gate Files — Validation Records

Gate documents (`Q{n}-gate.md`) are validation specs tied to QUEUE.md items. They define what must be proven before a body of work is considered done.

Active gates live at the workspace root while being worked. When a gate clears (gate-work adds `## Gate Status: CLEARED`), move the file to `gates/` at the workspace root. The `gates/` directory is the archive of completed validation records.

Gate files are operational records, not knowledge artifacts. They live and die with the workspace. When a workspace is condensed, gate files are disposable — the knowledge they validated persists in the work itself (committed code, deployed infrastructure, published tools).

## Workspace Hygiene

- **No scattered repos.** If a repo is in the workspace, it has a PIN.md row. If it doesn't have a PIN.md row, it shouldn't be in the workspace.
- **No stale status values.** When a project's state changes, update PIN.md. The prime skill reads PIN.md every session — stale data wastes operator orientation time.
- **No cross-domain references.** PIN.md links are relative to the workspace root. Don't reference other domain workspaces. If something from another domain is needed, note the cross-domain dependency in QUEUE.md.
- **Archive, don't accumulate.** When a workspace gets cramped, condense it. Extract what's worth keeping, archive or delete spent repos, and clean up. The workspace is disposable; the knowledge it produced is not.
