---
Project: Workshop
Type: Plugin Architecture
Date: 2026-03-10
Status: Draft
Revision: v3 — commons formalization, investigation 003 findings, evidence-interpretation doctrine revision
---

# B1 — Domain Chassis Architecture

## What It Is

The domain-chassis is the shared operational methodology plugin for all 3I execution
domains. It provides the gate validation lifecycle (plan, review, work), session context
loading (prime), structured document review (spec-review), operational retrospectives
(aar), and the skill development workflow (skill-creator). Every domain inherits the
chassis through the Claude Code plugin system. Changes to the chassis propagate to Forge,
Workshop, Lab, and Research simultaneously.

This blueprint captures the chassis architecture as a complete system: how the components
interact, how artifacts move through the lifecycle, where they land on disk, how they're
tracked and updated, and who owns the maintenance lifecycle. The chassis has operated
without a formal architecture document since inception. Individual skills were added
organically as needs emerged. Operational experience — particularly the Q16 investigation,
the AP-11 post-incident analysis, and fifteen cleared gates across Workshop — has surfaced
gaps, naming inconsistencies, and missing integrations that require coordinated changes
across multiple skills.

The trigger for this blueprint is the convergence of multiple accumulated changes that
interact with each other. Anti-pattern checkpoint tagging touches three skills. Gate review
findings separation touches the review-to-work handoff. Blueprint lifecycle skills are new
additions. Treating these as isolated patches risks inconsistency in the component that
defines consistency for every other domain.

## What It Replaces

The chassis currently works but operates without self-documentation at the architecture
level. Skills were built individually and their interactions are implicit rather than
specified. The README documents the file operation model (an important addition that
prevents path bugs), but the broader questions — how do these parts compose, what are the
governing constraints, how do changes get validated — are undocumented.

| Before | After |
|--------|-------|
| No formal architecture document for the chassis | Blueprint captures the complete system |
| Skills added organically, interactions implicit | Component interactions specified and justified |
| No `specs/` directory — chassis doesn't follow the project convention it propagates | `specs/` present, mirroring the pattern uniformly |
| No `blueprints/` directory | `blueprints/` directory with BLUEPRINT.md index paralleling gates |
| Foundational reference files in lowercase (`soul.md`, `vessel.md`) | Uppercase convention (`SOUL.md`, `VESSEL.md`) matching all foundational files |
| Principles, references, and format templates mixed in `references/` | Four-way taxonomy: `foundation/` (constitutional), `references/` (operational), `templates/` (format scaffolds), `specs/` (implementation) |
| Anti-pattern registry exists but isn't integrated into gate lifecycle | Checkpoint-scoped tagging across plan/work/review |
| Gate review produces findings inline, causing document bloat | Review produces companion findings file, gate stays lean for execution |
| No blueprint lifecycle skills | blueprint-plan and blueprint-review added to chassis |
| No formal governance model for chassis changes | Workshop owns lifecycle, the-range validates before integration |

## Design Inputs

| Source | Key Contribution |
|--------|-----------------|
| Q16 gate investigation (commons/q-16-investigation/) | Identified AP-11 (soul-only doctrine), led to VESSEL.md addition. Surfaced gate document bloat problem — review cycles and findings accumulating in gate body |
| Q16 AAR (workshop-polish/aar/2026-03-05-...) | Full narrative arc of the investigation. Documented the five-layer recursion, evaluator failures, doctrine discovery. Source of the anti-pattern tagging recommendation |
| Workshop TRIAGE.md item 4 | Anti-pattern checkpoint tagging specification: three skill touch points, tag format convention, Option B selected over instruction-only and mandatory self-test |
| Q16 word count analysis | Quantified the bloat problem: Q16 at 7,086 words (2.6x average), ~2,500 words of forensic analysis before checkpoint definitions. Executing agent pays context cost for operational history it doesn't need |
| Blueprint standard (references/blueprint-standard.md) | Defines the blueprint artifact class. This is its inaugural exercise — friction points discovered during B1 authoring feed back into the standard |
| Cleared gates Q1-Q15 | Operational history establishing the gate lifecycle patterns. Progressive quality improvement visible in later gates. The chassis earned its shape through these reps |
| Gate review skill (current) | Baseline for review methodology. The ad hoc improvement that improved review quality but caused Q16 bloat is the process change that needs encoding |
| Anti-pattern registry (references/anti-pattern-registry.md) | The knowledge base that checkpoint tagging integrates into the gate lifecycle. AP-10 (Recursive Defect) identified as particularly relevant for enforcement/remediation checkpoints |
| Q10 gate (workshop/gates/Q10-gate.md) | Landed implementation of anti-pattern checkpoint tagging. Defines the `{AP-nn}` tag convention, three-skill integration (gate-plan, gate-review, gate-work), and retrospective validation against Q15/Q16 content. Primary source for the Anti-Pattern Integration section. Demonstrates soul/vessel doctrine integration — spec-first convention definition validated against real artifacts |
| README.md file operation model | Established the workspace vs plugin directory boundary and the read-only-at-runtime constraint. All architectural decisions in this blueprint must honor this separation |
| Gate orchestrator plan (workshop/gate-orchestrator-dev-working/plan/plan.md) | Planned automation layer that sits directly on top of the chassis gate lifecycle. Defines a double-loop supervisor that dispatches gate-plan, gate-review, and gate-work as sub-agents with hook-enforced backpressure (BP-1 through BP-6). Introduces work-review phase not present in the current manual lifecycle. Pre-dates the blueprint standard — structurally a blueprint, will be formalized as B2. B1 is aware of the orchestrator as a downstream consumer but does not design for it. B2 has a blocker on a stable B1 |
| ADR-001 amendment (workshop-polish/adrs/ADR-001-agent-context-loading-order.md) | Amended 2026-03-14 to integrate Vertical Context Inheritance pattern. Workspace CLAUDE.md files inherit into child repo sessions, crossing git boundaries. ADR-001 now defines Tier 1 Content Constraints — a vertical safety invariant that constrains what workspace CLAUDE.md can contain. Relevant to init-domain (scaffolds workspace CLAUDE.md) and prime (safe landing zone for CWD-dependent content that cannot live in workspace CLAUDE.md). Pattern source: Vault/TheMothership/Resources/patterns/Pattern-Vertical-Context-Inheritance.md |
| Commons ADR-001 (commons/architecture-decisions/001-domain-chassis-placement.md) | Formalizes the rationale for domain-chassis living in Workshop rather than at 3I root. The chassis is a plugin built and maintained through Workshop's operational cycle. It is unique among domain plugins: it does not accept domain-specific artifacts. Cross-domain findings route through commons; the chassis receives updates as a result. The workbench/toolbox distinction is now documented as an architecture decision |
| Investigation 003: operator-terminal propagation (commons/investigations/003-operator-terminal-propagation/) | Found that gate-plan SKILL.md line 62 contains factually inaccurate universal doctrine: "Agent SDK projects require execution environment tagging." Traced to AAR interpretation propagated as evidence into chassis-level skill. Detection delay 14 days. AP-07, AP-10, AP-12. Remediation pending. The investigation's three-artifact split (evidence, interpretation, ledger) is the proof of concept for the evidence-interpretation doctrine revision |
| Evidence-interpretation separation doctrine revision (commons/doctrine-revisions/evidence-interpretation-separation.md) | Proposed chassis-level primitive: all 3I workflows producing knowledge must separate evidence (structured, factual, vault-ready) from interpretation (operator-facing narrative referencing evidence). Escalated from Q25 eval-study scope to system-wide doctrine. Directly affects the AAR skill and gate findings separation. Enforcement at production side, not vault intake |
| AP-12: The Doctrinal Echo (references/anti-pattern-registry.md) | New anti-pattern identified during investigation 003. Hedged generalization echoed through chassis into all downstream gates. The operator-terminal investigation is AP-12's inaugural case — an AAR lesson about the-range's specific bug was generalized into universal gate-plan doctrine |

## Architecture

### Governance

Workshop owns the domain-chassis lifecycle exclusively. No other domain modifies the
chassis directly. When a domain encounters friction or identifies improvement points for
the chassis, that feedback is formally routed to Workshop for action. The strictness serves
two purposes: accountability (one domain owns quality and consistency) and interoperability
(changes are validated before they reach every domain simultaneously). The placement
rationale is formally documented in commons ADR-001
(commons/architecture-decisions/001-domain-chassis-placement.md).

The-range serves as the validation and testing ground for chassis changes. Any modification
to the chassis must be validated on the-range prior to integration, due to the blast radius
of a cross-domain shared plugin. Today this blast radius is managed manually because the
operator works one domain at a time. That is not a durable control. The formal routing and
validation requirement is the durable control.

### Plugin Structure

The chassis is a Claude Code plugin rooted at `${CLAUDE_PLUGIN_ROOT}`. The plugin is
read-only at runtime — skills read methodology from the plugin directory and write
operational artifacts to the workspace. This separation means the plugin can be updated,
reinstalled, or shared across machines without losing domain state.

```text
domain-chassis/
  README.md               ← plugin overview and file operation model
  plugin.json
  agents/
  blueprints/
    BLUEPRINT.md          ← index of architecture blueprints
    B1-chassis-architecture.md
  commands/
  foundation/             ← system-level principles, constitutional
    SOUL.md
    VESSEL.md
    WELCOME.md
  references/             ← operational material skills consult during work
    anti-pattern-registry.md
    blueprint-standard.md
  skills/
    aar/
    blueprint-plan/       ← new
    blueprint-review/     ← new
    gate-plan/
    gate-review/
    gate-work/
    prime/
    skill-creator/
    spec-review/
  specs/                  ← new
  templates/
    adr-template.md
    blueprint-template.md
    proposal-template.md
    triage-format.md
```

Convention: foundational files use uppercase naming (BLUEPRINT.md, SOUL.md, VESSEL.md,
WELCOME.md). This mirrors the workspace-level convention (PIN.md, QUEUE.md, TRIAGE.md)
and serves a context engineering purpose — agents encountering the chassis recognize
foundational files by the same visual pattern used everywhere in 3I. Uniformity reduces
reasoning overhead.

### Directory Taxonomy

The plugin directory structure encodes a four-way taxonomy. Each directory has a distinct
purpose, and placing a file in the right directory is an architectural decision, not an
organizational preference.

**foundation/** — System-level principles. Constitutional documents that an agent
internalizes during orientation. These define what 3I believes and how agents orient within
it. Read early, absorbed as context, not consulted during specific tasks. Contents: SOUL.md,
VESSEL.md, WELCOME.md.

**references/** — Operational material that skills consult during work. Not principles to
internalize but knowledge bases and standards that inform specific skill execution. The two
current entries serve functionally different purposes: anti-pattern-registry.md is a
descriptive catalog (accumulated operational knowledge — "here are patterns we've
identified") while blueprint-standard.md is a prescriptive standard (normative definition
of an artifact class — "here's how you produce and evaluate blueprints"). They share the
same operational relationship to skills: a skill reads them during execution to inform its
work. That shared relationship is what makes them both references rather than warranting
further directory splitting.

Future consideration: when blueprint-plan is built as a skill, blueprint-standard.md may
migrate to `skills/blueprint-plan/references/` to parallel how gate-template.md lives in
`skills/gate-plan/references/`. The established ownership pattern is that the skill
producing an artifact class owns the standard for that class. This is a phasing decision
deferred until blueprint-plan is implemented.

**templates/** — Structural templates that get stamped out during document creation. Format
definitions and scaffolds: ADR format, proposal format, blueprint format, triage intake
format.

**specs/** — Implementation specifications. The chassis follows the same project convention
it propagates to every domain. Specs here define the detailed requirements for chassis
components. The directory mirrors the pattern uniformly so agents follow suit without
having to reason about whether the chassis is exempt from its own conventions.

**blueprints/** — Architecture design artifacts. BLUEPRINT.md indexes the collection,
paralleling how gates/ uses gate documents. Each blueprint captures the strategic thinking
behind a body of changes.

The workspace-level foundational files (PIN.md, QUEUE.md, TRIAGE.md, domain doctrines)
are not transported by the chassis but the chassis carries the guidance for creating them.
The `init-domain` command scaffolds them, and `prime` knows how to read them.
Domain-specific doctrines (FORGE.md, WORKSHOP.md, LAB.md, RESEARCH.md) are the exclusion
— the chassis does not own their content. Each domain tunes its own doctrine. The chassis
owns the convention: what a domain doctrine file is, what it should contain, how it relates
to the shared methodology.

### Context Path: `${CLAUDE_PLUGIN_ROOT}`

Every skill in the chassis resolves references through `${CLAUDE_PLUGIN_ROOT}`. This
variable is the anchor point for all cross-skill references and the boundary between
plugin methodology and workspace operations. Skills that own a reference file use relative
paths. Skills reaching into a sibling's directory use the full plugin root path. This
convention is documented in the README and must be preserved in all new skills.

<!-- TODO: Document the full reference graph — which skills read which files -->

### Skill Inventory and Interactions

<!-- TODO: Expand with interaction map — how skills reference each other,
     what artifacts flow between them, dependency ordering -->

#### Gate Lifecycle: plan → review → work

The core validation methodology. Gate-plan authors a gate document from a queue item.
Gate-review audits the gate against the quality bar defined in gate-plan. Gate-work
executes the gate checkpoint by checkpoint. The lifecycle is sequential — plan must
complete before review, review must pass before work begins.

Key interactions: gate-review reads gate-plan's SKILL.md (for quality requirements) and
gate-plan's references/gate-template.md (for structural conventions). Gate-work reads the
same template for gate conventions. Gate-plan reads prior gates (both active at workspace
root and cleared in gates/) for pattern reference.

Gate-plan improvement (from Q16 clearance): checkpoints that reference specific SDK fields,
CLI flags, or API endpoints must verify those interfaces exist against source before the
gate is approved. Q16's K2 checkpoint referenced `includeGitInstructions` on
`ClaudeAgentOptions` — a field that doesn't exist. The agent spent significant session time
chasing a phantom API. This is vessel doctrine applied to gate authoring: verify the
mechanism exists, not just that the intent makes sense. Gate-review should catch this as a
structural defect — a checkpoint referencing a nonexistent interface is AP-07 at the spec
level (structurally valid, operationally hollow).

Gate-plan improvement (from Q11 clearance): infrastructure-dependent gates that define
measurement paths, network topology, or service endpoints must verify those paths are
reachable before checkpoint definitions begin. Q11 defined three measurement paths; one
did not exist in the infrastructure (no direct-to-provider path without proxy-mediated
auth). The executing agent spent more session time chasing credentials for an inaccessible
path than it spent on all ten checkpoints combined. The gate's three-path topology was
architecturally correct but operationally inaccessible — the auth model made one path
unmeasurable. A Phase 0 ("verify all assumed infrastructure") would have caught the
two-path reality at plan time rather than execution time. This is vessel doctrine applied
to gate topology: verify the infrastructure matches the architecture, not just that the
architecture makes sense. Gate-review should screen for this — a gate that assumes
infrastructure without a verification step is AP-07 adjacent (the checkpoint exists but
cannot produce the artifact it defines). The Q11 AAR additionally documented a recurring
AP-11 variant: the agent's hypothesis ("I need an API key") remained fixed across multiple
failed search attempts (env vars, keychains, kubectl, 1Password, Python SDK), with only
the search target rotating. This "rotating search" shape — fixed hypothesis, rotating
implementation — is a detection signal distinct from the Q16 five-layer recursion and
warrants addition to AP-11's detection profile.

Gate-plan known defect (from investigation 003): SKILL.md line 62 contains factually
inaccurate universal doctrine — "Agent SDK projects require execution environment tagging."
The actual constraint is specific to the-range's PostToolUse hook control protocol bug, not
a property of all SDK projects. The paragraph caused every subsequent gate authored against
SDK-adjacent projects to apply `[operator-terminal]` tags as doctrine rather than
per-checkpoint assessment. This is AP-12 (The Doctrinal Echo) — an AAR interpretation
propagated as evidence into a chassis-level skill. Remediation tracked in
`commons/investigations/003-operator-terminal-propagation/ledger.md`. The causal chain
extends to AP-11: the `[operator-terminal]` fencing clustered all operational checkpoints
at gate end, creating the boundary-shift trigger pattern that reliably produces AP-11
layer 3.

#### Blueprint Lifecycle: plan → review

Architecture design methodology. Blueprint-plan authors a blueprint from accumulated
design inputs. Blueprint-review audits the blueprint against the blueprint standard. No
work phase — the blueprint's execution is its decomposition into specs and gates through
the existing gate lifecycle.

Key interactions: blueprint-review reads blueprint-standard.md and blueprint-template.md
for evaluation criteria, paralleling how gate-review reads gate-plan's quality bar.

<!-- TODO: Define what blueprint-plan reads for its methodology.
     Does it need its own references, or does the standard + template suffice? -->

#### Support Skills

Prime loads session context (doctrine, PIN, queue, triage). Spec-review provides
multi-round structured document review via subagent. AAR captures operational
retrospectives. Skill-creator manages skill development and evaluation. These operate
independently of the gate and blueprint lifecycles but may be invoked during any phase.

### Artifact Lifecycle

The evidence-interpretation separation doctrine revision
(commons/doctrine-revisions/evidence-interpretation-separation.md) establishes a
chassis-level primitive: workflows producing knowledge must separate evidence (structured,
factual, vault-ready) from interpretation (operator-facing narrative referencing evidence
but not containing it). This directly shapes the artifact lifecycle for two classes:

AARs currently combine evidence and interpretation in a single document. The AAR skill
needs structural revision to produce separate artifacts — or at minimum enforce structured
sections with clear boundaries. The operator-terminal investigation (003) is the empirical
case: an AAR's interpretation was treated as evidence and propagated into gate-plan
doctrine, compounding for 14 days. The AAR skill is the most immediate target.

Gate review findings are the second affected class. Review findings accumulate in the gate
body today (the Q16 bloat problem). The companion findings file convention (Phase 3) is
conceptually adjacent to the evidence-interpretation split — review findings are
interpretation of how the gate measures up, not evidence of what the project does. Keeping
them separate from the gate body (which is the execution spec) follows the same principle.

<!-- TODO: Complete lifecycle mapping for remaining artifact classes:
     - Gate documents: plan creates → review audits → work executes → cleared moves to gates/
     - Blueprint documents: plan creates → review audits → decomposes into specs/gates
     - Specs: live in specs/ — convention for chassis specs needs definition
-->

### Anti-Pattern Integration

The anti-pattern registry is integrated into the gate lifecycle through checkpoint tagging.
Checkpoints that guard against known anti-patterns carry an inline tag referencing the
registry entry. The tag format is `` `{AP-nn}` `` — curly braces inside backticks,
positioned after the category tag and before the checkpoint description:

```markdown
- [ ] **V1** `[operational]` `{AP-07}` Pipeline produces discriminating output on first run
```

Tags are selective, not blanket. A tag is applied only when the checkpoint genuinely guards
against the referenced anti-pattern — prevents or detects the named failure mode. Not every
checkpoint has anti-pattern relevance, and forcing tags where none applies degrades the
signal. When a checkpoint guards against multiple anti-patterns, entries are comma-separated
within a single tag: `` `{AP-07, AP-10}` ``. The convention has the same normative status
as category tags and bypass markers.

Three skills participate in the lifecycle:

**gate-plan** reads the anti-pattern registry during Step 2 (Internalize the Pattern) and
tags checkpoints during Step 3 (Draft the Gate). The self-assessment in Step 4 includes
anti-pattern coverage — catching omissions where a relevant anti-pattern has no guarding
checkpoint — without mandating that every anti-pattern appear in every gate.

**gate-review** reads the registry during Step 1 (Load Criteria) and validates tags during
Step 3 (Quality Requirements). Validation checks three aspects: tag references valid AP-nn
entries in the registry, the guarding relationship is semantically correct (the checkpoint
genuinely prevents or detects the named failure mode), and untagged checkpoints with clear
anti-pattern relevance are flagged as potential omissions (finding, not blocker).

**gate-work** reads the registry during Step 2 (Extract Context). When a checkpoint carries
a tag, the executing agent understands what failure mode it guards against — this informs
verification rigor. A checkpoint tagged `{AP-07}` (Vacuous Green) means verification must
produce substantive evidence, not just confirm structural existence. A checkpoint tagged
`{AP-10}` (Recursive Defect) means the verification itself should be audited for the defect
class being checked. The tag is a signal, not a procedure.

The design follows Option B from the original triage analysis: not instruction-only (too
soft — agents deprioritize instructions without structural anchoring) and not mandatory
self-test (too heavy for non-enforcement checkpoints). The tag is a lightweight structural
anchor that carries semantic weight through the registry reference.

This integration demonstrates both foundational doctrines in practice. Soul doctrine drove
the spec-first approach — Q10 defined the convention as a gate before any skill file was
touched. Vessel doctrine drove V1's retrospective validation — the convention was proven
against real Q15/Q16 gate content, not just theoretically justified. The Q10 gate
(workshop/gates/Q10-gate.md) is the authoritative source for implementation details and
validation evidence.

AP-12 (The Doctrinal Echo), identified during investigation 003 (2026-03-16), is the first
anti-pattern discovered through the integration this section describes. An AAR
interpretation entered the chassis as universal doctrine via gate-plan, then propagated
through four gates. The tagging integration caught it retrospectively — investigation 003
traces the causal chain including the AP-12 → AP-11 interaction where the doctrinal echo
shaped gate structure that a deeper anti-pattern exploits.

### Gate Review: Findings Separation

<!-- TODO: Detail the process-level change:
     - Current: findings and review cycles accumulate in gate body
     - Target: review produces companion findings file, gate stays lean
     - Convention for companion file naming and location
     - What stays in the gate (checkpoint definitions, final verdict)
       vs what moves to companion (findings, review iteration history)
     - Impact on gate-work context loading
-->

## Phasing

Phase 1 (structural alignment) is partially complete. The structural moves from the initial
B1 session landed: `foundation/`, `blueprints/`, uppercase naming, directory taxonomy.
`specs/` directory and BLUEPRINT.md index are in place. Remaining structural work deferred
to final phase (init-domain updates, README updates).

Phase 2 (anti-pattern checkpoint tagging) is complete. Q10 cleared 2026-03-10. Three skill
files updated (gate-plan, gate-review, gate-work), tag convention defined in gate-template.md,
validated retrospectively against Q15/Q16 content. Commit `cb645b0`, version bump to `0.1.8`.

Phase 3 (gate review findings separation) is open. The companion file convention for
separating review findings from the gate body has not been designed or implemented.

Phase 4 (blueprint lifecycle skills) is open. blueprint-plan and blueprint-review are
planned but not yet built. Phase 4 depends on Phase 3 — blueprint-review needs to inherit
any review methodology changes from the findings separation work.

## Scope Boundaries

### Excluded

Domain-specific plugins (forge-doctrine, workshop-polish) are out of scope. This blueprint
covers the shared chassis only. Domain plugins pair with the chassis but their methodology
is domain-scoped and maintained by their respective domains.

The provenance sprawl concern (scattered quotes, § references, taglines without canonical
sources) is out of scope. It was identified during the Q16 investigation but requires its
own review session to map the problem and determine what's actionable. The chassis provides
a home for system-level principles (SOUL.md, VESSEL.md) but the broader traceability
problem is a system-level concern, not a chassis architecture concern.

Astrogator integration and Layer 1 routing are out of scope. The chassis operates at Layer
2 (execution). Routing decisions happen upstream.

### Deferred

The `init-domain` command will need updating to scaffold the new directory structure
(`specs/`, `blueprints/`) but that change is mechanical and deferred until the architecture
is locked and validated on the-range.

README.md updates to reflect the new plugin structure (blueprints/, specs/, renamed
references) are deferred to the final phase — the README should document the landed
architecture, not the planned one.

The `init-domain` command scaffolds workspace CLAUDE.md files. When init-domain is updated
for the new directory structure, the CLAUDE.md template must comply with ADR-001's Tier 1
Content Constraints (vertical safety invariant). CWD-dependent content — workspace-relative
file references, skill invocation suggestions, workspace-specific operational rules — must
route to the prime skill output instead of the CLAUDE.md template. Prime's role as the safe
landing zone for CWD-dependent orientation content should be reflected in the prime skill
documentation when this update lands.

## Open Questions

- [x] What is the exact tag format for anti-pattern checkpoint tagging? `` `{AP-nn}` `` —
  curly braces inside backticks, positioned after category tag, before description.
  Multi-tag: comma-separated within single tag. Defined in gate-template.md, landed via
  Q10 (2026-03-10).

- [ ] What was the specific ad hoc improvement to the gate review process that improved
  quality but caused Q16 bloat? The blueprint references the outcome but the mechanism
  needs to be captured to encode it properly in the skill.

- [ ] Does blueprint-plan need its own references directory, or does the blueprint standard
  plus template suffice as the methodology source? Gate-plan has
  `references/gate-template.md`. The parallel would be blueprint-plan owning the template,
  but the template already lives in `templates/`.

- [ ] Should the blueprint-template.md move from `templates/` to
  `skills/blueprint-plan/references/` to parallel how gate-template.md lives in
  `skills/gate-plan/references/`? This would be structurally consistent but means the
  template is no longer in the general templates directory.

- [ ] What is the companion file naming convention for gate review findings? Options
  include `Q{n}-findings.md`, `Q{n}-review.md`, or something else. Convention needs to
  work with gate-work's file resolution logic.

- [ ] How should the README's reference table be updated to reflect SOUL.md, VESSEL.md,
  and BLUEPRINT.md? Currently the references table only lists anti-pattern-registry.md,
  triage-format.md, and WELCOME.md.
