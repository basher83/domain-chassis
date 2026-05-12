---
name: chassis-release
description: Bumps domain-chassis plugin.json and marketplace.json versions in lockstep.
when_to_use: Use when releasing a change to the domain-chassis plugin after a substantive skill, doctrine, or methodology change — classifies the semver bump and updates both manifests.
---

# Chassis Release — Plugin Version Bump and Marketplace Sync

The chassis plugin has two manifest files this skill keeps in sync.

## Manifest contract

### plugin.json

`.claude-plugin/plugin.json` is the plugin's own manifest, read by Claude Code at install and load time. Owns the canonical `version`. Follows semver; the plugin is currently in the `0.y.z` pre-stable range where minor bumps may carry breaking changes (the boundaries below are the post-1.0 contract the chassis is converging toward).

- **PATCH** (`0.1.22 → 0.1.23`) — doctrine refinement, prose tightening, anti-pattern additions, bug fixes in skill instructions, description rewording. No change to skill contracts, frontmatter shape, or template structure that downstream gates or domains depend on.
- **MINOR** (`0.1.x → 0.2.0`) — new skill, new command, new template, new optional frontmatter field, new foundation file, additive changes to existing skill behavior.
- **MAJOR** (`0.x → 1.0`, then `1.x → 2.0`) — removing or renaming a skill, breaking changes to a SKILL.md contract domains depend on, breaking template restructures that invalidate existing gates, foundation file removal.

### marketplace.json

`.claude-plugin/marketplace.json` is the marketplace registry. Lists every plugin published from this repo (currently `domain-chassis` from `./` and `workshop-polish` from a remote URL). Read by marketplace consumers, not by the plugin at runtime.

**Not load-bearing.** `plugin.json` is the source of truth — it's what Claude Code reads at install and load. `marketplace.json` is advertisement. Drift between the two is a polish issue, not a correctness one. This skill still keeps them in sync because consumers see the advertised version and stale numbers create confusion.

Two version fields, independent of each other:

- `metadata.version` — the registry's own version. Bumps when the registry shape changes (adding or removing a plugin entry, restructuring categories). Does not bump for individual plugin updates.
- `plugins[].version` — each plugin's advertised version. The `domain-chassis` entry should match `plugin.json` after a release. The `workshop-polish` entry tracks its upstream repo and is out of scope for this skill.

`description` and `keywords` are duplicated between `plugin.json` and the `domain-chassis` entry in `marketplace.json`.

## Process

### Step 1 — Classify the change

Read `plugin.json.version` for the current state. Classify the change being released against the semver boundaries above. State the classification explicitly before touching either file. If ambiguous, choose the higher bump — under-bumping risks silent breakage in downstream domains.

### Step 2 — Verify current state

Read both manifests and capture:

- `plugin.json` `version`
- `marketplace.json` `plugins[].version` for the `domain-chassis` entry
- Whether `description` or `keywords` changed in `plugin.json` since the last release

If `plugin.json` and the `marketplace.json` entry are already out of sync, surface the drift to the operator before proceeding. Decide explicitly whether this release closes the gap (set both to the new target) or compounds it (bump each by one). Default is to close the gap.

### Step 3 — Bump plugin.json

Edit `.claude-plugin/plugin.json`:

- `version` to the new value
- `description` to current text (if it changed)
- `keywords` to current set (if changed)

### Step 4 — Sync marketplace.json

Edit `.claude-plugin/marketplace.json`. In the `plugins[]` entry for `domain-chassis`:

- `version` to match `plugin.json` exactly
- `description` to match `plugin.json` exactly
- `keywords` to match `plugin.json` exactly

Do not bump `metadata.version` unless the registry shape changed (a plugin entry was added or removed). Do not modify the `workshop-polish` entry.

### Step 5 — Commit

Stage both manifest files:

```bash
git add .claude-plugin/plugin.json .claude-plugin/marketplace.json
```

Hand off to the `git-commit` skill (`git-workflow` plugin) with the suggested subject:

```text
chore: bump domain-chassis plugin version to {new-version}
```

`git-commit` runs hooks, applies the repo's conventional-commit conventions, and handles re-staging if hooks modify files. If `description` or `keywords` also changed, mention that in the handoff so the body reflects it.

### Step 6 — Verify

After commit:

- `git diff HEAD~1 .claude-plugin/` shows both manifests updated
- `plugin.json.version` equals `marketplace.json.plugins[domain-chassis].version`
- `description` and `keywords` match across the two files

If either equality fails, fix in a follow-up commit before pushing.
