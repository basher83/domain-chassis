---
name: aar
description: This skill should be used when the user asks to "do an AAR", "after action review", "retrospective", "review what happened", "what went well", "lessons learned", "post-mortem", "debrief the session", "debrief the run", or mentions reviewing a completed work session, analyzing outcomes, or capturing operational lessons. Provides the AAR methodology framework for structured retrospective analysis across any domain.
---

# AAR — After Action Review

Structured retrospective analysis of a completed work session. The AAR captures what specs, gates, and plans miss: what actually happened, where friction occurred, and what to change next time.

You (the main agent) drive the analysis. You sat through the session or have been primed with the project state. The AAR's value is in connecting observations to methodology decisions — identifying which skill, process, or configuration change would have changed the outcome. That's judgment work that requires your context.

Spawn subagents for mechanical data gathering. Retain control of synthesis.

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

Spawn Explore-type subagents in parallel for the target project. Each returns a structured report.

**Subagent 1 — Git Evidence:**

- `git log --oneline -20` — recent commits including the session's output
- `git log --format='%h %s' --since="24 hours ago"` — today's session commits
- `git diff HEAD~N..HEAD --stat` — files changed across the session (adjust N to span it)
- `git tag --sort=-creatordate | head -5` — tags produced

**Subagent 2 — Artifact State:**

Scan the workspace root and project directory for operational artifacts. Look for any of:

- Implementation plans, task files, or work-in-progress documents
- Spec directories and spec status files
- Gate documents (active at workspace root, cleared in `gates/`)
- Queue files (QUEUE.md, TRIAGE.md)
- Agent configuration or activity logs (`.claude/` directory)
- Test results, build outputs, or deployment records

Report what exists and its current state. Do not assume a fixed set of artifacts — different domains and projects produce different artifacts. Report what you find.

If the user can provide a session log path, read that too.

## Phase 2: Structured Review

Work through each section using your session context and the subagent reports. Don't ask the user to repeat what's already been discussed — you have the conversation history.

### Change Summary

What was built, modified, or fixed. Commit hashes, file counts, test counts. Quantitative, not narrative.

### Expectations vs Reality

What was the estimate (scope, complexity, timeline)? What actually happened? Where did the estimate diverge and why?

### What Went Well

3-5 specific successes. "The spec was tight" is vague. "The spec had five requirements with exact field names and code locations, eliminating all ambiguity" is useful.

### What Didn't Go Well

Friction, failures, unexpected issues. Categorize:

- **Methodology** — specs, prompts, skills, gates, process configuration
- **Infrastructure** — git auth, sandbox, tooling, environment
- **Agent behavior** — off-track execution, scope creep, convergence failures

### Lessons Learned

Distill into reusable, actionable principles. Each lesson should be something a practitioner can apply to their next session. No generic platitudes.

### Action Items

Concrete next steps with clear ownership:

- **Methodology fixes** — changes to skills, prompts, gates, or process
- **Infrastructure fixes** — tooling, auth, environment changes
- **Follow-up work** — validation, testing, or tasks spawned by this session

Each action item should be specific enough to become a task or commit.

## Phase 3: Write the AAR

Save to the domain knowledge repo's aar directory:

```text
${DOMAIN_REPO}/aar/{YYYY-MM-DD}-{project}-{brief-description}.md
```

Template:

```markdown
# AAR: {Project} — {Brief Description}

**Date:** {YYYY-MM-DD}
**Domain:** {domain name}
**Project:** {project name}
**Scope:** {what was attempted — 1 sentence}
**Commit(s):** {hash(es)}
**Tag:** {version tag if created}

## Change Summary

{quantitative summary}

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
```

## Phase 4: Cross-Reference

Check if any lessons or action items should propagate to:

- **Skills** — does a chassis or domain skill need updating based on what we learned?
- **Gates** — should a new gate checkpoint be added to prevent this class of issue?
- **Doctrine** — does the domain's operating principles need a refinement?
- **Hooks or tooling** — does a hook need fixing or a new one created?

Note proposed propagations at the end of the AAR under a "Propagation" section. Don't make changes automatically — flag them for the operator to review.

## Phase 5: Commit and Push

Persist the AAR to the domain knowledge repo:

```bash
cd ${DOMAIN_REPO}
git add aar/{filename}.md
git commit -m "aar: {project} — {brief-description}"
git push
```

If the domain knowledge repo could not be resolved in the earlier step and the AAR was written to the workspace root, remind the operator to file it.

## Related Skills

- **gate-work** — gate execution; gates are a common subject of AARs
- **gate-review** — gate quality audit; AAR findings may identify gate gaps
- **prime** — session context loading; prime and AAR are bookends of a work session
