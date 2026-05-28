# QUEUE.md lifecycle

QUEUE.md is live operational intent. If a row is in the queue, the operator still intends to do that work. It is not a backlog archive, not history, and not a completed-work log.

## Schema
Rows have four required columns, plus one optional column:

|Column|	Meaning|
|---|---|
|Q|	Stable ID like Q1, Q2. Never reused after removal.|
|Intent|	What to accomplish, imperative form.|
|Scope|	Project link relative to workspace root, or domain name for cross-cutting work.|
|Next|	Immediate next action or current blocker. Use Blocked by Q2-style references here.|

## When to add items

The normative rule is:

> "Items are added when work begins"

So a row should appear when the operator has moved from intake/idea to actual intended work.

There is no dedicated skill that automatically adds arbitrary QUEUE rows.

There are two documented add paths:

1. Direct creation when work begins: the operator, or an agent acting with operator direction, adds a row.
2. Promotion from TRIAGE.md: templates/triage-format.md says a promoted triage item creates a QUEUE.md row and removes the triage row. It also says triage does not auto-promote; the operator or agent with operator confirmation decides.

## What stays on the queue

Anything still actively intended stays.

That includes:

- Blocked work. Put the blocker in Next, e.g. Blocked by Q45.
- Work that has not been gate-planned yet.
- Work with an active gate in progress.
- Work whose next action changed; update Next, do not create a new Q.

The queue is not "started vs not started." It is "operator still means to do this."

## When to update

Update the row whenever the immediate next action or blocker changes.

The Q stays stable for the life of the intent. The mutable field is mainly Next.

## When to remove

The normative rule is:

> “removed when done.”

And:

> “If it's done, remove it.”

No completed status. No archive row. No “Done” column.

## Practical rule

Use QUEUE.md like this:

- Add a row when the operator commits to doing the work.
- Keep it while the intent is active, even if blocked or not yet gated.
- Update Next as the immediate action changes.
- Remove it when done or abandoned.
- Do not reuse Q numbers.
- Do not mark completed rows; completed work leaves the queue.
