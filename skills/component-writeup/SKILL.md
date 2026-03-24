---
name: component-writeup
description: This skill should be used when the user asks to "write up this component", "document this system", "produce a technical writeup", "create a component writeup", "architecture documentation", "system documentation", "document the architecture of X", "technical writeup of X", "how does this system work — write it up", "map out this system's components", or mentions producing structured technical documentation of a system, subsystem, or component set. Produces progressive-disclosure documentation following the Patnaik template with system-decomposition analytical rigor — component inventory, architecture overview, data flow, per-component detail, and grouped references.
---

# Component Writeup — Structured Technical Documentation

Produce a structured technical writeup of a target system by systematically discovering its components, tracing their relationships through artifacts, and rendering the findings into progressive-disclosure documentation.

The writeup follows the Patnaik template format. The analytical methodology is adapted from the system-decomposition pattern — phased discovery with gate checks ensures the documentation is grounded in artifact evidence rather than assumptions.

## Input

The operator provides a target system: a project directory, a subsystem within a project, or a set of artifacts to document. The operator may also specify the audience and the question the documentation should answer.

If the operator provides only a name or vague reference, ask for the artifact paths before proceeding. The skill cannot produce artifact-grounded documentation without access to the artifacts.

## Phase 1: Readiness and Discovery

Phase 1 produces the raw inventory that all subsequent phases build on. Do not begin analysis or writing until discovery is complete.

### 1.1 Readiness Verification

Before beginning discovery, verify that the target system's artifacts exist and are accessible. Read the top-level directory structure. Identify the artifact types present (code, config, skills, hooks, specs, docs). If critical artifacts are missing or inaccessible, report the gaps to the operator before proceeding — a writeup produced from incomplete artifacts will contain gaps that look like analysis failures rather than input failures.

### 1.2 Component Inventory

Read the system artifacts and identify every discrete component. A component is any unit with its own identity, inputs, outputs, and reason for existing. For each component, capture:

- **Name** — what it is called
- **Type** — what kind of component (module, service, skill, hook, config, data store, CLI tool, external dependency)
- **Function** — what it accomplishes in one sentence
- **Inputs** — what it reads, receives, or depends on
- **Outputs** — what it produces, modifies, or emits

Apply the scoping test: each component should be describable in one sentence without "and." A component requiring "and" to describe its function likely represents two components that should be separated.

### 1.3 Relationship Identification

For every pair of components that interact, classify the relationship:

- **Dependency** — A requires B to function (A cannot operate without B)
- **Consumer** — A reads output from B but does not require B's presence
- **Trigger** — A causes B to execute (event-driven, hook-based, orchestrated)
- **Shared state** — A and B both read or modify the same state

Trace relationships through artifacts — imports, config references, API calls, file reads/writes. If a relationship is implied but not explicitly visible, flag it as inferred with the evidence that suggests it.

### 1.4 Execution Pipeline

Determine how execution flows through the system:

- **Entry points** — where execution begins
- **Decision points** — where the system chooses between paths
- **Interception points** — where hooks or middleware modify the flow
- **Terminal points** — where execution ends and what outputs are produced

### Gate Check

Before proceeding to Phase 2, verify completeness: every component in the artifact set appears in the inventory, and every inter-component interaction visible in the artifacts appears in the relationship list. Components that reference things outside the artifact set are listed as external dependencies. Output the inventory as a structured table.

## Phase 2: Analysis and Synthesis

Phase 2 transforms the raw inventory into the analytical structures that feed the documentation. Do not begin writing the final artifact until analysis is complete.

### 2.1 Architecture Synthesis

From the component inventory and relationships, construct the system's architecture:

- How components are organized (layers, pipelines, hub-and-spoke, peer-to-peer)
- Which components are load-bearing (most dependents, most shared state)
- What the dominant interaction pattern is (synchronous calls, event-driven, file-based, shared state)

### 2.2 Data Flow Trace

From the execution pipeline, trace the primary data flow as a numbered sequence:

1. What enters the system and where
2. How each component transforms or routes the data
3. What exits the system and in what form

If the system has multiple primary workflows, trace each separately. Name the workflow being traced.

### 2.3 Design Rationale Collection

As you discover architectural decisions during analysis, collect the rationale:

- Why this structure and not the obvious alternative
- What constraints drove the architecture (performance, simplicity, compatibility, operator workflow)
- What tradeoffs were accepted

Rationale feeds the "Why this approach" and "Why this shape?" sections in the output. If rationale is not visible in the artifacts, note what is unknown rather than inventing justifications.

### Gate Check

Before proceeding to Phase 3, verify: the architecture synthesis accounts for all components in the inventory, the data flow trace names the component responsible at each step, and no component from the inventory is orphaned (present in inventory but absent from both the architecture and data flow).

## Phase 3: Artifact Production

Render the analysis into the Patnaik template format. The template is in [references/component-writeup-template.md](references/component-writeup-template.md) — read it before writing.

### Output Structure

The writeup follows progressive disclosure through zoom levels. Each level is self-contained — a reader can stop at any layer and have a coherent understanding:

1. **Opening hook** — one paragraph stating what the system does and what makes it interesting
2. **Why this approach** — design rationale with concrete differentiators
3. **Component inventory** — every major component and its one-line role
4. **Architecture overview** — prose paragraph on system shape, followed by:
   - Process model (ASCII box diagram with labeled arrows)
   - Data flow (numbered step sequence for primary workflow)
   - "Why this shape?" rationale bridge
5. **Per-component detail** — each component follows the introduction pattern:
   - Concept paragraph (what it is and why it exists)
   - Realistic example from the target's actual artifacts (code, config, schema)
   - Explanation (walk through the example, connect to architecture)
   - Variants or alternative views (table, compact, different lens)
   - Implementation notes (blockquote, skippable)
6. **Sequence diagram** — for complex interactions, time-ordered component interaction
7. **Extension points** — concrete extension surfaces that exist now
8. **Operational checklist** — practical tasks, known rough edges
9. **Key takeaways** — synthesis of insight, not summary
10. **References** — grouped by type (conceptual, implementation, research)

### Writing Constraints

Every structural claim in the writeup must be anchored to an artifact. If the writeup states "Component A sends data to Component B," the artifact evidence (import statement, API call, config reference) should be traceable. Claims that could apply to any system — generic descriptions without target-specific names, paths, or structural details — indicate the analysis phase was incomplete.

Examples in per-component sections must be drawn from the target's actual code, config, or artifacts. Invented examples undermine the writeup's value as documentation of a real system.

The writeup documents what the system IS, incorporating design rationale where visible in artifacts. It does not prescribe improvements or redesigns unless the operator explicitly requests recommendations.

## Reference Files

- **[references/component-writeup-template.md](references/component-writeup-template.md)** — Patnaik progressive disclosure template with structural elements reference and design principles. Read before Phase 3 artifact production.
- **[references/integration-decisions.md](references/integration-decisions.md)** — Integration decisions documenting which elements from system-decomposition and extraction patterns were incorporated and why.
