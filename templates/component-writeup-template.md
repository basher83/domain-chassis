# Component Writeup Template

Extracted from Raja Patnaik's blog design patterns (rajapatnaik.com/blog). The format works for project documentation, technical blog posts, system teardowns, and component mapping. Pure markdown — no tooling dependencies.

The template comes first. The design reference follows.

---

* * *

# [Project/System Name]

[One-paragraph hook. State the problem or the thing this system does. End with what makes it interesting or different. This is the TL;DR — a reader who stops here should still walk away with the core idea.]

## Why [This Approach]

[Establish rationale before showing anything. Answer "why this and not the obvious alternative?" Use quantified claims where possible.]

- **[Differentiator 1]:** [What it does differently, with evidence or a citation]
- **[Differentiator 2]:** [Concrete advantage, not marketing language]
- **[Differentiator 3]:** [Qualification — where it falls short or what it doesn't do]

* * *

## What You'll Build / What This Is

[Component inventory. Name every major piece and its role in one sentence each. This is the map before the territory.]

- **[Component A]** — [one-line purpose]
- **[Component B]** — [one-line purpose]
- **[Component C]** — [one-line purpose]
- **[Component D]** — [one-line purpose]

* * *

## Architecture Overview

[Prose paragraph introducing the system shape — how the components relate at the highest level. One paragraph, not a list.]

### Process Model

[ASCII box diagram showing components, their boundaries, and data flow between them. Label every arrow.]

```text
+---------------------------+
|       Component A         |
|  - responsibility 1       |
|  - responsibility 2       |
+-------------+-------------+
              | data/control flow label
              v
+---------------------------+       relationship label
|       Component B         |------>  Component C
|  - responsibility 1       |
+---------------------------+
```

### Data Flow

[Numbered step sequence showing how data moves through the system for the primary use case.]

1. [Actor] does [action]
2. [Component A] receives [input], produces [output]
3. [Component B] transforms [output] into [artifact]
4. [Component C] validates and persists [artifact]

> **Why this shape?** [One paragraph explaining the design rationale. What constraints drove this architecture. What alternatives were considered and rejected.]

* * *

## [Component A]: [Name]

[Conceptual introduction — what this component is and why it exists. Two to four sentences.]

```yaml
# Realistic example with real field names
id: example-2026-03-24-001
title: "Descriptive title of what this represents"
version: 1
config:
  setting_a: value    # inline comment explaining the field
  setting_b: true     # why this default
```

[Explanation paragraph. Walk through the example — what each section means, what the reader should notice. Connect back to the architecture overview.]

### Variants / Alternative Views

[Show the same concept in a different representation — table view, compact view, JSON output, CLI output. Same underlying data, different lens.]

```text
NAME          ROLE        STATUS    NOTES
component-a   ingestion   active    primary entry point
component-b   transform   active    stateless
component-c   storage     active    persistent
```

#### Implementation Notes

> **Notes for implementation:** [Blockquote for practical caveats — performance constraints, known edge cases, UX considerations. Things an implementer needs but a reader skimming for concepts can skip.]

* * *

## [Component B]: [Name]

[Same pattern: concept paragraph → realistic code/config example → explanation → variants → implementation notes. Repeat for each major component.]

```python
class ComponentB:
    """One-line docstring stating purpose."""

    def __init__(self, config):
        self.upstream = config.component_a    # relationship to prior component
        self.output_format = config.format    # configurable behavior

    def process(self, input_data):
        # Step 1: validate against contract
        validated = self.validate(input_data)
        # Step 2: transform
        result = self.transform(validated)
        # Step 3: emit to downstream
        return self.emit(result)
```

[Explanation of how this connects to Component A (upstream) and Component C (downstream). Show the seams between components explicitly.]

* * *

## Sequence: [Primary Workflow Name]

[For complex interactions, show the time-ordered sequence of component interactions.]

```text
Actor          Component A       Component B       Component C
  |                 |                 |                 |
  |--- request ---->|                 |                 |
  |                 |--- transform -->|                 |
  |                 |                 |--- persist ---->|
  |                 |                 |<-- confirm -----|
  |                 |<-- result ------|                 |
  |<--- response ---|                 |                 |
```

* * *

## Extension Points

[Where the system can be extended. Not aspirational features — concrete extension surfaces that exist now.]

- **[Extension 1]:** [What it enables and how to hook into it]
- **[Extension 2]:** [Same]
- **[Extension 3]:** [Same]

## Productionizing / Operational Checklist

[Practical tasks for making this real. Not theory — concrete actions.]

- [ ] [Task 1: specific action with rationale]
- [ ] [Task 2: specific action]
- [ ] [Task 3: monitoring, observability, or guard rail]
- [ ] [Known rough edge: documented limitation with workaround]

* * *

## Key Takeaways

[Three to five sentences synthesizing what matters. Not a summary of the document — a distillation of the insight. What should change about how the reader thinks after reading this.]

## References

**Conceptual**
- [Reference 1](url) — one-line description of what it covers
- [Reference 2](url) — one-line description

**Implementation**
- [Reference 3](url) — one-line description
- [Reference 4](url) — one-line description

**Research**
- [Reference 5](url) — one-line description

---

* * *

# Design Reference: Patnaik Blog Formatting Patterns

Two reference sections follow. The first covers the structural elements and when to use each. The second covers the design principles that make the format work.

* * *

## Formatting Elements Reference

| Element | When to Use | Example |
|---------|-------------|---------|
| `## H2` | Major sections — each represents a chapter | Architecture, Component A, Sequence |
| `### H3` | Subsections within a chapter | Process Model, Variants, Data Flow |
| `#### H4` | Fine-grain details, alternative views | Implementation Notes, Table View |
| Horizontal rules (`* * *`) | Visual chapter breaks between major sections | Between each `## H2` group |
| `**bold:** text` | First introduction of a concept or component | `**Component A:** ingestion pipeline` |
| Inline code (backticks) | Identifiers, paths, CLI commands, config keys | `component_a`, `/path/to/config` |
| Fenced code blocks | Always language-tagged, realistic content | ```yaml, ```python, ```text |
| Blockquote `>` | Implementation notes, callouts, design rationale | `> **Notes for implementation:**` |
| Numbered lists | Sequential steps, data flows, build order | Process sequences, workflow steps |
| Bullet lists | Component inventories, feature sets, differentiators | "What you'll build" sections |
| `**term:** definition` pairs | Inline definitions within bullet lists | Extension points, differentiators |
| Rhetorical bridges | "Why?" paragraphs between architecture and implementation | `> **Why this shape?**` |
| ASCII diagrams | System topology, process models, sequence flows | Box diagrams with labeled arrows |
| Tables | Compact multi-column views of the same data shown elsewhere | Component summary, CLI cheatsheet |
| `- [ ]` checklists | Operational/productionizing tasks | Actionable items, not aspirational |

## Design Principles

These are the structural decisions that make the format effective, independent of any specific content.

### Progressive disclosure through zoom levels

Show the same system at multiple resolutions. The reader picks the depth they need. Each level is self-contained — you can stop reading at any layer and still have a coherent understanding.

- **Layer 1 — Inventory:** Name every component and its role (bullet list)
- **Layer 2 — Topology:** Show how components connect (ASCII box diagram)
- **Layer 3 — Data flow:** Numbered step sequence for the primary workflow
- **Layer 4 — Component detail:** Per-component concept/example/explanation
- **Layer 5 — Interfaces:** Schemas, APIs, configuration contracts
- **Layer 6 — Sequences:** Time-ordered interaction diagrams

### Never explain without an example

Every concept introduction is immediately followed by a realistic example — not a toy, not a placeholder. The example uses real field names, real values, real structure. The explanation paragraph follows the example, not the other way around. The reader sees the thing before they're told what it is.

### Bridge sections with rationale

Transitions between architectural overview and implementation detail use "Why?" paragraphs. These explain the design constraints that drove the structure. They serve double duty: they justify the architecture for reviewers and they orient implementers who need to make judgment calls at the edges.

### Separate concept from implementation caveats

Implementation notes live in blockquotes (`> **Notes for implementation:**`). A reader scanning for conceptual understanding skips them. An implementer finds them. This prevents the main narrative from drowning in edge cases while still capturing them.

### Group references by type

References at the end are categorized: Conceptual (understand the domain), Implementation (build the thing), Research (go deeper). A reader looking for the paper doesn't wade through API docs. A builder looking for the SDK doesn't wade through papers.

### Multiple representations of the same data

Show the same system as a box diagram, a numbered step list, a table, and a sequence diagram. Different readers parse different representations. The redundancy is intentional — it's not repetition, it's the same territory from different vantage points.

### Component introduction pattern

Every component follows the same micro-structure:

1. Name it and state its purpose (paragraph, not a heading)
2. Show a realistic example (code block, config, schema)
3. Explain what the example shows (paragraph after the code)
4. Show variants or alternative views (table, compact, filtered)
5. Implementation notes (blockquote, skippable)
6. Connection to adjacent components (how data flows in and out)

This repetition creates a rhythm. Once the reader recognizes the pattern, they can navigate any component section by structure alone.
