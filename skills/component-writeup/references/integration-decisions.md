# Integration Decisions: Component-Writeup Skill

Source review for the component-writeup skill. Documents which elements from the system-decomposition pattern and the five agentic-engineering extraction patterns are incorporated into the skill, and which are excluded with reasoning.

## System-Decomposition Pattern

Source: `the-range/scenarios/system-decomposition/context/system-decomposition/system-decomposition.md`

### Incorporated

1. **Phased methodology with gate checks.** The three-phase structure (Discovery, Analysis, Production) maps directly to the component-writeup workflow. Adapted as: Discovery (inventory target components from artifacts), Analysis (trace relationships and data flow through artifacts), Production (render findings into Patnaik template format). Gate checks between phases ensure completeness before proceeding — the component inventory must be complete before relationship analysis begins, and analysis must be complete before artifact production begins. This prevents the common failure mode of producing documentation from incomplete understanding.

2. **Component inventory format.** The structured inventory schema (name, type, function, inputs, outputs) provides systematic discovery rather than ad-hoc enumeration. Maps to the Patnaik template's "What You'll Build" section and feeds per-component detail sections. The boundary field from the original is omitted — component writeup captures what components do, not where their formal boundaries are drawn.

3. **Relationship classification vocabulary.** The four relationship types (dependency, consumer, trigger, shared state) provide analytical rigor when documenting how components interact. These categories feed into the Architecture Overview and Data Flow sections. Without this vocabulary, relationship descriptions tend toward vague prose ("Component A talks to Component B") rather than precise characterization of the interaction type.

4. **Execution pipeline identification.** The systematic trace of entry points, decision points, interception points, and terminal points maps to the Patnaik template's Data Flow section and Sequence diagrams. Ensures the writeup captures the actual execution flow through the system rather than a simplified mental model.

### Excluded

1. **Two-artifact split (structural model + design analysis).** Component-writeup produces a single documentation artifact following the Patnaik template. The system-decomposition's separation of evidence and interpretation serves a different purpose: structured ingestion into knowledge bases vs. operator decision support. The Patnaik template integrates structural facts and design rationale within the same document through progressive disclosure — facts in inventory and architecture sections, rationale in "Why this shape?" bridges and implementation notes. Splitting the output would break the template's coherence model.

2. **Coupling assessment vocabulary (structural / contractual / incidental).** This classification assesses system health — appropriate for cartographic decomposition work but too deep for component documentation. The writeup captures what relationships exist and how data flows, not the coupling type classification. A reader wanting coupling analysis should use the system-decomposition skill directly.

3. **Complexity indicators (fan-out, fan-in, cross-cutting, hidden state).** Same reasoning as coupling assessment. These are analytical tools for assessing structural risk, not documentation primitives. The writeup may surface these indirectly through the relationship and data flow sections, but does not formally classify them.

## Extraction Patterns

Source: `agentic-engineering/extractions/`

### 1. Comparative-Solution-Analysis — EXCLUDED

CSA's core contribution is a structured comparison matrix across competing solutions. Component writeup documents a single system's architecture, not a comparison between alternatives. The Patnaik template's "Why this approach" section handles design rationale without requiring the full six-step CSA pipeline. If a writeup needs to justify design choices against alternatives, the operator can invoke CSA separately.

### 2. Corpus-Convention-Analysis — EXCLUDED

CCA discovers recurring structural patterns across a corpus of artifacts through prevalence metrics and confidence banding. Component writeup examines a single system's artifacts to document its architecture. The skill reads artifacts to understand one system, not to extract conventions across many. Pattern detection at scale is orthogonal to single-system documentation.

### 3. Directed-Iterative-Analysis — EXCLUDED

DIA's core value is director/analyst role separation for independent review — a structural guarantee of fresh perspective that requires multi-agent execution. Component writeup is a single-agent documentation task, not a review task. The progressive narrowing principle (broad sweep to narrow coverage across rounds) is already embodied in Patnaik's zoom levels (inventory, topology, data flow, detail) and the phased methodology adapted from system-decomposition.

### 4. Iterative-Process-Preflight — INCLUDED (partial)

Two elements incorporated:

- **Readiness verification before execution.** The skill verifies that the target system's artifacts exist and are accessible before beginning discovery. This prevents producing documentation from incomplete information — a writeup based on a subset of artifacts will contain gaps that look like analysis failures rather than input failures.
- **Scoping test.** Each component identified during discovery should be describable in one sentence without "and." This practical boundary check prevents scope creep during inventory and ensures clean component boundaries. A component requiring "and" to describe its function likely represents two components that should be separated.

### 5. Validation-Plan-Authoring — EXCLUDED

VPA produces validation plans (gate documents) — a methodology for defining what must be proven before work is complete. This is orthogonal to component documentation. The "verification by positive evidence" principle is relevant to verification contexts, not documentation contexts. The system-decomposition's requirement that every relationship cites evidence from artifacts already ensures documentation claims are artifact-anchored.
