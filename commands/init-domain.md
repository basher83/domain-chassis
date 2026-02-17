---
name: init-domain
description: Scaffold a new domain workspace with the common chassis files
arguments:
  - name: domain
    description: "Domain name (e.g., workshop, lab, research, forge)"
    required: true
---

# Init Domain

Scaffold the common chassis for a new domain workspace. Creates the four required files and the gates directory at the current working directory.

**Before creating anything**, check what already exists. If any of the target files are already present, list them and stop. Do not overwrite existing chassis files without explicit confirmation.

## Files to Create

### 1. Doctrine file: `{DOMAIN}.md`

The domain name argument determines the filename. Uppercase the first letter for the heading.

```markdown
# The {Domain} Doctrine

Operating principles for {description of domain scope}. Core principle: {to be defined by the operator}.

---

*Draft — define operating principles as the domain matures.*
```

Leave the doctrine as a stub. The operator writes their own principles.

### 2. `PIN.md`

```markdown
# {Domain}

{One-sentence workspace description.}

## Projects

| Project | Description |
|---------|-------------|
```

Use a single generic category. The operator refines categories as the domain's work takes shape.

### 3. `QUEUE.md`

```markdown
# Queue

Operational intent tracker for the {domain} domain. Read at session start alongside PIN.md.

| Q | Intent | Scope | Next |
|---|--------|-------|------|
```

### 4. `TRIAGE.md`

```markdown
# Triage

Raw intake. Drop ideas, tasks, and items from other domains here. Triaged at session start when content is present.

---
```

### 5. `gates/` directory

Create an empty `gates/` directory for cleared gate file archival.

## After Scaffolding

Report what was created. Remind the operator that the doctrine file is a stub — defining operating principles is the first real work for the new domain.
