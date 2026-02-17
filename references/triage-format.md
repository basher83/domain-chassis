# Triage Format

Standard format for items in a domain's `TRIAGE.md`. Everything below the `---` separator is pending intake.

## Row Format

Each item is a single markdown table row:

```markdown
| Source | Item | Context | Arrived |
|--------|------|---------|---------|
```

### Fields

| Field | Required | Description |
|-------|----------|-------------|
| **Source** | Yes | Where the item came from. Domain name (`forge`, `research`), person name (`brent`), or agent name (`astrogator`). Lowercase. |
| **Item** | Yes | What the work is. One line, imperative mood. Enough to act on without chasing references. |
| **Context** | No | Why it's here or where to look. Cross-domain reference (`Ref: F-QUEUE Q4`), link, or brief rationale. Leave empty (`—`) if self-evident. |
| **Arrived** | Yes | ISO date (`YYYY-MM-DD`) when the item was deposited. Used for staleness detection. |

### Example

```markdown
# Triage

Raw intake. Drop ideas, tasks, and items from other domains here. Triaged at session start when content is present.

---

| Source | Item | Context | Arrived |
|--------|------|---------|---------|
| research | Evaluate CodeSpeak for prompt compression | Ref: R-QUEUE Q3, output routes to workshop | 2026-02-17 |
| brent | Fix Tailscale cert renewal on mini | Cert expired 2/16 | 2026-02-17 |
| forge | Add health endpoint to shuttle | Needed for lab monitoring rollout | 2026-02-18 |
```

## Processing Rules

Triage is processed at session start (by `prime`) when content exists below `---`.

For each item, exactly one outcome:

- **Promote** — create a QUEUE.md row, remove from triage
- **Discard** — item is out of scope or stale, remove from triage
- **Defer** — not actionable yet, leave in place

The operator (or agent with operator confirmation) decides. Triage doesn't auto-promote.

## Writing Rules (for routers)

When depositing items into another domain's TRIAGE.md:

1. Append rows to the existing table. Do not rewrite the file header or other rows.
2. One item per row. Decompose compound work at the boundary — don't ship a bundle.
3. Include enough context that the receiving domain can act without calling back to the source.
4. If the item has a cross-domain dependency, note it in Context (e.g., `blocked by: L-QUEUE Q2`).

## What Triage Is Not

- Not a backlog. Items that survive more than two triage passes should be promoted or discarded.
- Not a discussion thread. No comments, replies, or status updates. That's the gate's job.
- Not prioritized. Priority is assigned at queue promotion, not intake.
