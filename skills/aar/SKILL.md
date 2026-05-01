---
name: aar
description: Runs a structured retrospective of a completed work session — captures what specs, gates, and plans miss. What actually happened, where friction occurred, and what to change next time. Domain-agnostic methodology.
when_to_use: Use when the user asks to do an AAR, after-action review, retrospective, post-mortem, debrief a session or run, review what happened, capture lessons learned, or analyze outcomes of completed work.
---

# AAR — After Action Review

Structured retrospective analysis of a completed work session. The AAR captures what specs, gates, and plans miss: what actually happened, where friction occurred, and what to change next time.

The AAR produces two artifacts: an evidence record (structured, factual, verifiable) and an interpretation document (narrative analysis, lessons, recommendations). These are separate files. A downstream consumer can read the evidence record without encountering interpretation, and vice versa. This separation is a chassis-level requirement — see `foundation/EVIDENCE.md` for the doctrine and provenance.

You (the main agent) drive the analysis. You sat through the session or have been primed with the project state. The AAR's value is in connecting observations to methodology decisions — identifying which skill, process, or configuration change would have changed the outcome. That's judgment work that requires your context.

Subagents gather mechanical data when you lack session context. When you participated in the work, your conversation history is the evidence base — subagents are skipped.

## Domain Resolution

Before gathering data, identify which domain this AAR belongs to. Check the workspace root for a domain doctrine file:

- `FORGE.md` → Forge (Building)
- `LAB.md` → Lab (Operating)
- `WORKSHOP.md` → Workshop (Tooling)
- `RESEARCH.md` → Research (Investigating)

If no doctrine file is found, ask the operator which domain this work belongs to. Set `DOMAIN` to the resolved domain name (lowercase).

## Domain Knowledge Repo Resolution

The AAR persists to the domain's knowledge repo — the domain-specific plugin that holds doctrine, AARs, and operational knowledge. These repos are not uniformly named. Known mappings:

- Forge → `forge-doctrine`
- Workshop → `workshop-polish`

For other domains, look for a repo or directory matching `{domain}-doctrine` or `{domain}-*` that contains an `aar/` directory.

Resolution order:

1. Check if the current working directory is the domain knowledge repo (look for `aar/` directory and the domain doctrine file).
2. Check for `./{repo-name}/` as a subdirectory of cwd using the known mappings above.
3. If the domain isn't in the known mappings, scan for sibling directories matching `{domain}-*` that contain an `aar/` directory.
4. If no repo can be resolved, write the AAR to the workspace root and flag it for the operator to file. Do not block the review on repo resolution.

Set `DOMAIN_REPO` to the resolved path.

## Phase 1: Data Gathering

Before dispatching subagents, determine your context mode based on observable session signals:

- **Warm context:** Your conversation history contains the work being reviewed — gate execution output, implementation commits, debugging sessions, or other artifacts from participating in the work session. You have first-hand evidence.
- **Cold context:** This session started from a prime, session log, or operator briefing. Your conversation history does not contain the work being reviewed — only summaries or descriptions of it.

If warm context: skip subagent dispatch. Your session context is the primary evidence base for Phase 2. Proceed directly to Phase 2.

If cold context: you must delegate data gathering to subagents using the Agent tool. Do not run git commands or scan artifacts yourself — dispatch subagents and wait for their reports. This keeps the main agent's context clean for the judgment-heavy Phase 2 work.

Dispatch both subagents in a single message (one Agent tool call each) so they run concurrently. Do NOT set `run_in_background: true` — use foreground mode so you block until both return. Do not proceed to Phase 2 until both subagent results are in your conversation. Their reports are your primary evidence base.

**Subagent 1 — Git Evidence** (via Agent tool):

Brief the subagent with the project directory and ask it to run these git commands and report back:

- `git log --oneline -20` — recent commits including the session's output
- `git log --format='%h %s' --since="24 hours ago"` — today's session commits
- `git diff HEAD~N..HEAD --stat` — files changed across the session (adjust N to span it)
- `git tag --sort=-creatordate | head -5` — tags produced

The subagent should return a structured summary of what it finds — commit hashes, file change stats, and any tags.

**Subagent 2 — Artifact State** (via Agent tool):

Brief the subagent with the workspace root and project directory. Ask it to scan for operational artifacts:

- Implementation plans, task files, or work-in-progress documents
- Spec directories and spec status files
- Gate documents (active at workspace root, cleared in `gates/`)
- Queue files (QUEUE.md, TRIAGE.md)
- Agent configuration or activity logs (`.claude/` directory)
- Test results, build outputs, or deployment records

The subagent should report what exists and its current state. Do not assume a fixed set of artifacts — different domains and projects produce different artifacts.

If the user can provide a session log path, have one of the subagents read that too.

## Phase 2: Structured Review

Work through each section using your available evidence — session context in warm mode, subagent reports in cold mode, or both if subagent data supplements your session context. Don't ask the user to repeat what's already been discussed.

Phase 2 gathers both evidence and interpretation. The separation into distinct artifacts happens in Phase 3, not here. Work through the sections naturally — just be aware of which sections produce evidence (factual, verifiable data) and which produce interpretation (analysis, conclusions, recommendations).

### Change Summary — evidence

What was built, modified, or fixed. Commit hashes, file counts, test counts. Quantitative, not narrative. This section's content goes into the evidence record.

### Expectations vs Reality — interpretation

What was the estimate (scope, complexity, timeline)? What actually happened? Where did the estimate diverge and why? This is analysis — it interprets what the evidence means.

### What Went Well — interpretation

3-5 specific successes. "The spec was tight" is vague. "The spec had five requirements with exact field names and code locations, eliminating all ambiguity" is useful.

### What Didn't Go Well — interpretation

Friction, failures, unexpected issues. Categorize:

- **Methodology** — specs, prompts, skills, gates, process configuration
- **Infrastructure** — git auth, sandbox, tooling, environment
- **Agent behavior** — off-track execution, scope creep, convergence failures

### Lessons Learned — interpretation

Distill into reusable, actionable principles. Each lesson should be something a practitioner can apply to their next session. No generic platitudes. Lessons are interpretation — they are the operator's conclusions drawn from the evidence, not the evidence itself.

### Action Items — interpretation

Concrete next steps with clear ownership:

- **Methodology fixes** — changes to skills, prompts, gates, or process
- **Infrastructure fixes** — tooling, auth, environment changes
- **Follow-up work** — validation, testing, or tasks spawned by this session

Each action item should be specific enough to become a task or commit. Action items are interpretation — they are recommendations derived from analysis, not factual records.

## Phase 3: Write the AAR

Write two files to the domain knowledge repo's aar directory. The evidence record captures factual data. The AAR captures interpretation that references the evidence record.

### Evidence record

```text
${DOMAIN_REPO}/aar/{YYYY-MM-DD}-{project}-{brief-description}.evidence.md
```

Template:

```markdown
# Evidence: {Project} — {Brief Description}

**Date:** {YYYY-MM-DD}
**Domain:** {domain name}
**Project:** {project name}
**Scope:** {what was attempted — 1 sentence}

## Commits

| Hash | Message | Files changed |
|------|---------|---------------|
| {hash} | {message} | {count} |

## Artifacts Produced

| Artifact | Path | Type |
|----------|------|------|
| {name} | {path} | {file/tag/config/etc} |

## Timeline

| Event | Timestamp |
|-------|-----------|
| {event} | {ISO 8601} |

## Metrics

{quantitative data — test counts, file counts, version numbers, durations, or other measurable outcomes. Omit this section if no metrics are relevant.}
```

The evidence record contains only verifiable data. No analysis, no conclusions, no recommendations. Every entry is independently checkable against git history, file system state, or other external sources.

### AAR interpretation

```text
${DOMAIN_REPO}/aar/{YYYY-MM-DD}-{project}-{brief-description}.md
```

Template:

```markdown
# AAR: {Project} — {Brief Description}

**Date:** {YYYY-MM-DD}
**Domain:** {domain name}
**Project:** {project name}
**Evidence:** [{evidence filename}]({evidence filename})

## Expectations vs Reality

{estimate vs actual, divergence analysis}

## What Went Well

{specific successes with reasoning}

## What Didn't Go Well

{friction and failures, categorized by type}

## Lessons Learned

{actionable principles}

## Action Items

- [ ] {action item 1}
- [ ] {action item 2}

## Operator Notes

{leave blank for operator input}
```

The AAR is interpretation. It analyzes, concludes, and recommends. It references the evidence record for factual grounding — a reader who wants to verify a claim follows the Evidence link. The AAR does not duplicate the commit table, artifact list, or timeline from the evidence record.

## Phase 4: Cross-Reference

Check if any lessons or action items should propagate to:

- **Skills** — does a chassis or domain skill need updating based on what we learned?
- **Gates** — should a new gate checkpoint be added to prevent this class of issue?
- **Doctrine** — does the domain's operating principles need a refinement?
- **Hooks or tooling** — does a hook need fixing or a new one created?

Note proposed propagations at the end of the AAR under a "Propagation" section. Don't make changes automatically — flag them for the operator to review.

## Phase 5: Commit and Push

Persist both artifacts to the domain knowledge repo in a single commit:

```bash
cd ${DOMAIN_REPO}
git add aar/{filename}.evidence.md aar/{filename}.md
git commit -m "aar: {project} — {brief-description}"
git push
```

Both files are committed together — the evidence record and interpretation are a pair. If the domain knowledge repo could not be resolved in the earlier step and the AAR was written to the workspace root, remind the operator to file it.

## Related Skills

- **gate-work** — gate execution; gates are a common subject of AARs
- **gate-review** — gate quality audit; AAR findings may identify gate gaps
- **prime** — session context loading; prime and AAR are bookends of a work session
