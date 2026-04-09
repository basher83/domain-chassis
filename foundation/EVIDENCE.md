# Evidence and Interpretation Are Separate Artifacts

When a 3I workflow produces knowledge, that knowledge has two components that must not share an artifact. Evidence is what happened. Interpretation is what it means. They serve different consumers, decay at different rates, and propagate through different paths. Combining them in a single artifact creates a conflation path where interpretation masquerades as evidence and propagates unconditionally.

## Evidence Artifacts

Evidence artifacts are structured, factual, and vault-ready. They document what happened with verifiable anchors: commit hashes, file paths, timestamps, reproduction steps, quantitative measurements. Their value comes from specificity. An evidence artifact that contains a generalization has failed at its job.

Evidence artifacts route to the knowledge base through the arscontexta ingestion pipeline, where they receive direct extraction — factual content preserved with its verifiable structure intact. The pipeline does not add hypothesis tags, confidence hedging, or interpretive framing to evidence. The anchors go in as structured data, not narrative.

The eval-study skill's sidecar ledger (`{repo-name}.ledger.md`, template at `workshop-polish/skills/eval-study/references/ledger-template.md`) is the reference implementation. Each phase entry records what was done with timestamps and commit hashes. The verification detail table documents what was checked and what was found. The ledger is readable by a future agent who has never seen the evaluation — every claim in it is independently verifiable against the git history it references.

## Interpretation Artifacts

Interpretation artifacts are operator-facing narrative. They explain what the evidence means: lessons learned, root cause analysis, methodology recommendations, propagation implications. They reference evidence but do not contain it. A reader of an interpretation artifact who wants to verify a claim follows the reference to the evidence artifact — the interpretation itself is not the proof.

Interpretation artifacts stay at their origin. For domain-specific work, interpretation lives in the domain's doctrine plugin (AARs in `{domain-plugin}/aar/`, analysis in `{domain-plugin}/analysis/`). For cross-domain work, interpretation lives in commons. Interpretation does not route to the arscontexta vault as primary content — if an interpretation artifact enters the pipeline, it receives hypothesis-tagged extraction where claims are marked as contextual, recommendations carry their scoping context, and generalizations reference their source observation.

## Ledgers

Ledgers are the third artifact type: operational state tracking for active work. A ledger mutates continuously and either archives or dies when the work completes. It serves a different consumer (the executing agent tracking its own progress) with a different lifecycle (write-heavy, session-scoped) and a different mutation pattern (append-only within phases, status fields overwritten between phases).

Ledgers are neither evidence nor interpretation. The eval-study ledger tracks process state. The gate file tracks checkpoint state. The arscontexta queue tracks pipeline state. When the work completes, a ledger's verifiable anchors (commit hashes, timestamps, pass/fail results) become evidence. Its operational narrative (why a phase was retried, what judgment calls were made) becomes interpretation. The ledger is the pre-separation form — the raw material from which evidence and interpretation are extracted after the work is done.

## Enforcement

Separation is enforced at the authoring skill, not at vault intake. The arscontexta pipeline is a knowledge store, not a gatekeeper. Skills that create artifacts are responsible for producing clean separation before the artifact reaches any downstream consumer. The AAR skill (`domain-chassis/skills/aar/SKILL.md`) produces interpretation-only output and references evidence artifacts by path. Gate skills produce gate files (ledgers) whose checkpoint evidence and review findings are structurally distinct sections. The eval-study skill produces an evaluation document (interpretation of what was found) alongside a sidecar ledger (process evidence of how it was found).

The minimum requirement: a downstream consumer — human or automated — can extract evidence from an artifact without also extracting interpretation, and vice versa. If that extraction requires judgment about which sentences are factual and which are interpretive, the separation has failed. The structure must make it mechanical.

## Provenance

This primitive exists because of a specific failure. During the Q6 gate execution (2026-03-02, Forge), an AAR for the-range's Phase 1 implementation observed that nested-session testing required operator intervention due to a PostToolUse hook `continue: false` bug in the CLI's Agent SDK control protocol. The AAR's interpretation — that gate-plan should include guidance for SDK projects — was implemented as a universal doctrine addition in `domain-chassis/skills/gate-plan/SKILL.md` (commit `79d17ad`). The recommendation was contextually valid for the-range. The implementation was a hedged generalization ("Agent SDK projects require execution environment tagging") that applied unconditionally to all domains.

The generalization propagated into gates Q6, Q14, Q20, and Q21 as `[operator-terminal]` tags. At minimum Q20's I2 checkpoint was incorrectly tagged, confirmed agent-verifiable per its own gate errata. A code comment carrying the same narrative was caught and removed during a PR review. The full propagation chain, causal analysis, and remediation are documented in `commons/investigations/003-operator-terminal-propagation/` — the evidence artifact (`evidence-propagation-trace.md`) and the interpretation artifact (`interpretation-root-cause-analysis.md`) are themselves the first demonstration of the separation this primitive requires.

The failure took 14 days to detect. The root cause was not the AAR's recommendation, which was sound in context. The root cause was the absence of structural separation between the observation (evidence: the-range has a specific nested-session bug) and the recommendation (interpretation: gate-plan should account for this). When interpretation was treated as evidence and propagated into chassis-level doctrine, it echoed unconditionally. Evidence/interpretation separation prevents this conflation path by making the boundary mechanical rather than judgment-dependent.

---

*"Evidence is what happened. Interpretation is what it means. Combining them is how a bug in one project becomes doctrine for all projects."*

*Derived from the operator-terminal propagation investigation (2026-03-16). The separation was named during an arscontexta session examining evidence quality in knowledge extraction.*
