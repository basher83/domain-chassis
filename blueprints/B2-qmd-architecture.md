---
date: 2026-04-05
tags:
  - memo
  - knowledge-management
  - search-infrastructure
  - qmd
  - architecture
confidence: high
related:
  - "[[ADR-002-QMD-Collection-Scoping]]"
  - "[[Memo-Vault-Tagging-Standards]]"
  - "[[Eval-QMD-Q1a-Contamination-Bench]]"
  - "[[Eval-QMD-Collection-Information-Class-Audit]]"
---

# QMD Specification

> [!tip] Validated
> Governing document for qmd as 3I search infrastructure. Describes the system as deployed (v2.1.0, upgraded from 1.0.7 on 2026-04-08). ADR-002 covers the collection scoping rationale; this spec covers everything else. Four adversarial reviews conducted 2026-04-06 against upstream codebase (R1-R4). Q1a contamination bench completed 2026-04-08: origin carve-out confirmed effective, historical contamination identified as remaining vector. See [[Eval-QMD-Q1a-Contamination-Bench]].

## What QMD Is

QMD (Quick Markdown Search) is a fully local, on-device hybrid search engine for markdown files. It serves as the prior art search infrastructure for the entire 3I system — any agent in any domain with MCP access can query qmd to find ADRs, patterns, runbooks, research, memos, and project documentation before making decisions.

Built by Tobi Lutke. 100% local — zero cloud dependencies. All models run on-device via Apple Silicon Metal.

## Role in 3I

qmd is vault-owned infrastructure that serves all five domains. The vault curates the content; qmd makes it searchable. The return path: domain work produces knowledge → vault triages and places it → qmd indexes it → any domain can find it.

This is the mechanism behind VAULT.md principle 7: "What one domain learns, the vault makes available to all."

## Config

Location: `~/.config/qmd/index.yml`

```yaml
collections:
  vault-projects:
    path: /Users/basher8383/3I/Vault/TheMothership/Projects
    pattern: "**/*.md"
    context: >-
      Active and historical project work. Contains current specs, plans, and
      project notes alongside stalled/abandoned projects (~21% historical).
      Check project README status fields — Paused or Planning projects may
      contain superseded specs and never-built designs. Treat dated project
      artifacts as point-in-time documents.
  vault-areas:
    path: /Users/basher8383/3I/Vault/TheMothership/Areas
    pattern: "**/*.md"
    ignore: ["origin/**"]
    context: >-
      Ongoing domain knowledge. Current methodology, field journals,
      evaluations, and configuration docs. Areas/recon/ contains landscape
      scouting and external teardowns — third-party analysis, not operator
      decisions.
  vault-origin:
    path: /Users/basher8383/3I/Vault/TheMothership/Areas/origin
    pattern: "**/*.md"
    includeByDefault: false
    context: >-
      Methodology lineage and cleaned transcripts. Historical context
      describing how ideas and systems evolved — not current truth.
      Opt-in only. Query explicitly when tracing provenance or
      understanding why a decision was made.
  vault-resources:
    path: /Users/basher8383/3I/Vault/TheMothership/Resources
    pattern: "**/*.md"
    context: >-
      Reference material: reusable patterns, operational memos, research
      findings, prompt templates, runbooks, and ADRs. Includes
      Resources/research/forge-archaeology/ (teardowns of historical systems
      that may no longer exist). Check confidence frontmatter — low confidence
      material is explicitly unvalidated. Research- prefix is evidence;
      Memo- prefix is operator interpretation.
  notes:
    path: /Users/basher8383/3I/workshop/arscontexta
    pattern: notes/**/*.md
    context: >-
      Atomic knowledge claims from arscontexta (workshop-owned). Prose-as-claim
      format, semantically connected. Structured extractions, not operator
      narrative. Trust level depends on the source chain documented in each
      note. Evidence/interpretation separation not enforced — treat with caution.
```

Five collections. Three vault-owned (scoped by [[ADR-002-QMD-Collection-Scoping]]), one origin carve-out (`includeByDefault: false`), one workshop-owned (arscontexta atomic notes). Context annotations configured 2026-04-08. Origin carve-out implemented 2026-04-08 with `ignore: ["origin/**"]` on vault-areas to prevent double-indexing. See ADR-002 for the rationale behind what's indexed and what's deliberately excluded (00_Inbox, Archives, docs, templates, obsidian-plugin).

**Operational note:** Adding `ignore` patterns to an existing collection requires a subsequent `qmd update` to remove already-indexed files that match the new pattern. The ignore is applied during indexing, not retroactively on the stored index.

## Collections

| Collection | Owner | Docs | Default | Content | Typical Query |
|-----------|-------|------|---------|---------|---------------|
| `vault-projects` | Vault | 100 | Yes | Active work: specs, plans, architecture, project notes | "What's the current state of X?" |
| `vault-areas` | Vault | 83 | Yes | Domain knowledge: methodology, deep dives, field journals (origin excluded) | "What do we know about X?" |
| `vault-origin` | Vault | 8 | **No** | Methodology lineage, cleaned transcripts, convergence records | "How did X originate?" (opt-in) |
| `vault-resources` | Vault | 166 | Yes | Reference: patterns, memos, ADRs, runbooks, research, prompts | "Has this been decided?" "What's the pattern for X?" |
| `notes` | Workshop (arscontexta) | 285 | Yes | Atomic claims: prose-as-claim knowledge atoms, semantically connected | "What verified claims exist about X?" |

Total: 642 documents, 2627 chunks as of 2026-04-08. vault-origin is opt-in only (`includeByDefault: false`) — agents must explicitly include it when investigating provenance.

## Embedding Strategy

QMD uses a three-model local pipeline. All models run on Apple Silicon via Metal acceleration.

| Model | Role | Size |
|-------|------|------|
| EmbeddingGemma 300M | Vector embeddings (GGUF format) | ~600MB |
| Fine-tuned 1.7B LLM | Query expansion (generates alternative phrasings) | ~1.4GB |
| Qwen3-Reranker 0.6B | Result reranking (scores candidate relevance) | ~500MB |

**Chunking:** Two strategies as of v2.1.0:

- **Markdown/unknown files:** 900-token chunks with 15% overlap. Respects code fences and heading boundaries — chunks never split mid-code-block or mid-section.
- **Code files (v2.1.0):** AST-aware chunking via web-tree-sitter. Chunks at function, class, and import boundaries instead of arbitrary text positions. Supported languages: TypeScript/JavaScript, Python, Go, Rust. Controlled via `--chunk-strategy <auto|regex>` (default `regex`).

**Global model config:** `models:` section in `index.yml` configures `embed`, `rerank`, and `generate` model URIs. Resolution order: config > env var (`QMD_EMBED_MODEL`, `QMD_RERANK_MODEL`, `QMD_GENERATE_MODEL`) > built-in default. Despite CHANGELOG claims about "per-collection" model config, the implementation is global — all collections in a single `index.yml` share the same models. A `models:` key nested under an individual collection entry is silently ignored. To use different models for different collections, you'd need separate config files and separate qmd instances.

**Storage:** SQLite database at `~/.cache/qmd/index.sqlite`. BM25 index via SQLite FTS5. Vector index stored alongside.

**Resource management:** Models loaded into VRAM on demand, idle-unloaded after 5 minutes. Total VRAM footprint when active: ~2.5GB on Apple Silicon.

## Search Modes

Three retrieval strategies, selectable via sub-query type in the unified `query` tool (MCP/SDK) or via CLI subcommands. Different speed/quality tradeoffs:

### Lexical / BM25 (~30ms)

Sub-query type: `lex`. CLI: `qmd search`. BM25 keyword search via SQLite FTS5. Finds documents containing exact words and phrases. Fast, deterministic, no model inference required. Supports quoted phrases (`"exact match"`) and negation (`-term`, `-"phrase"`).

Best for: known terms, exact phrases, filenames, specific identifiers.

### Vector / Semantic (~2s)

Sub-query type: `vec`. CLI: `qmd vsearch` (alias: `qmd vector-search`). Meaning-based search using EmbeddingGemma embeddings. Finds conceptually related documents even when vocabulary differs — handles synonyms, paraphrases, and adjacent concepts.

Best for: conceptual queries, finding related work, exploring adjacent topics.

### Hybrid Pipeline (~10s)

Triggered when multiple sub-query types are combined in a single `query` call (e.g., `lex` + `vec`), or when using `qmd query` on the CLI. Eight stages:

1. **BM25 strong-signal probe** — runs BM25 first. If the top result scores above 0.85 and the gap to the second result exceeds 0.15, the query has a clear answer — skip expansion entirely and return early. This avoids expensive LLM inference for unambiguous lookups.
2. **Query expansion** — fine-tuned 1.7B LLM generates typed query variants (`lex`, `vec`, `hyde` sub-queries).
3. **Type-routed retrieval** — each sub-query routes to a single backend based on its type: `lex` → FTS5, `vec`/`hyde` → vector search. This is not parallel BM25+vector; each expanded query goes to one backend.
4. **Reciprocal Rank Fusion** — RRF (k=60) merges all result lists. The first two lists (original query + first expansion) get 2x weight. Positional bonuses: +0.05 for rank 1, +0.02 for ranks 2-3.
5. **Candidate selection** — slice fused results to `candidateLimit` (default 40).
6. **Chunk selection** — for each candidate document, select the best chunk using keyword overlap. The reranker sees chunks, not full documents.
7. **LLM reranking** — Qwen3-Reranker 0.6B scores the selected chunks. Position-aware blending: the final score combines RRF rank with reranker score, so early RRF position continues to influence the result.
8. **Dedup and filter** — deduplicate by file, filter by `minScore`, slice to `limit`.

Best for: complex questions, cross-domain queries, when initial searches return incomplete results. On the CLI, `qmd query` invokes this pipeline automatically (all 8 stages). Via MCP, combine multiple sub-query types in the `searches` array — but note that the MCP path (`structuredSearch`) skips stages 1-2 (strong-signal probe and auto-expansion) because the caller provides pre-expanded queries. The MCP path also applies 2x weight only to the first result list, not the first two. These differences are correct behavior (the skipped stages are irrelevant when queries are pre-expanded) but affect `--explain` trace interpretation.

### Intent Disambiguation

All search modes accept an optional `intent` parameter that steers query expansion, reranking, and snippet extraction without searching on its own. Intent disambiguates queries where the same term has different meanings across collections.

Example: `query: "performance"` is ambiguous (web-perf? team health? infrastructure throughput?). Adding `intent: "web page load times and Core Web Vitals"` steers the entire pipeline toward web-performance content.

Available via:
- MCP: `intent` parameter on the `query` tool
- CLI: `--intent` flag on `qmd query`
- Inline: `intent:` typed line in query documents

The MCP server instructions now say "Always provide `intent` on every search call." This is directly relevant to the propagation risk: agents searching across mixed-class collections should declare what they're looking for to avoid retrieving results from the wrong information class.

### Benchmarking

`qmd bench <fixture.json>` measures search quality: precision@k, recall, MRR, and F1 across BM25, vector, hybrid, and full pipeline backends. Ships with an example fixture. This enables empirical measurement of whether collection rescoping or model changes improve retrieval quality.

### Score Transparency

`qmd query --json --explain` shows score traces (RRF + rerank blend). Enables debugging of why a result ranked where it did — critical for understanding whether collection scoping changes improve or degrade retrieval.

## CLI Surface

Primary CLI commands documented below. The CLI exposes the full management surface — everything the MCP server can't do.

### Search and Retrieval

| Command | Description |
|---------|-------------|
| `qmd query <text>` | Full hybrid pipeline. Accepts `--intent`, `--explain`, `--json`, `--no-rerank`, `--limit`, `--candidate-limit` |
| `qmd search <text>` | BM25/FTS only |
| `qmd vsearch <text>` | Vector search only (alias: `qmd vector-search`) |
| `qmd deep-search <text>` | Alias for `qmd query` |
| `qmd get <path>` | Single document retrieval |

### Index Management

| Command | Description |
|---------|-------------|
| `qmd update` | Scan collections for new/modified files |
| `qmd embed` | Generate embeddings for unembedded documents. Accepts `--chunk-strategy <auto\|regex>` |
| `qmd cleanup` | Database maintenance — remove orphaned content, inactive docs, vacuum |
| `qmd status` | Index health: collection counts, embedding state, staleness |
| `qmd bench <fixture>` | Search quality benchmarks (precision@k, recall, MRR, F1) |

### Model and Skill Management

| Command | Description |
|---------|-------------|
| `qmd pull` | Download/refresh model files |
| `qmd skill show` | Display the packaged Claude Code skill |
| `qmd skill install` | One-command Claude Code skill setup |
| `qmd skill help` | Skill usage information |

### Collection Management

| Command | Description |
|---------|-------------|
| `qmd collection list` | List configured collections |
| `qmd collection update-cmd <name> <cmd>` | Set the `update` pre-command for a collection |

### Server

| Command | Description |
|---------|-------------|
| `qmd mcp` | Start MCP server (stdio transport) |
| `qmd mcp --http` | Start MCP server with HTTP transport + REST endpoints (`/mcp`, `/health`, `/query`, `/search`) |

## Integration Surfaces

qmd exposes three integration surfaces, each serving a different agent mode. Full analysis in [[Research-QMD-Integration-Surfaces]].

| Surface | Agent Mode | Capability | Use When |
|---------|-----------|------------|----------|
| MCP Server | Using a tool | ~20% — search and retrieval only | Normal search during work, concurrent multi-agent access |
| CLI (via Bash) | Following operator instructions | 100% — full management surface | Collection management, re-indexing, diagnostics, debugging search quality |
| SDK (library import) | Building a tool | ~95% — full typed async API | Building hooks, plugins, pipelines, custom MCP tools |

The MCP server exposes the search-and-retrieval core. The CLI exposes the full surface through shell commands. The SDK exposes nearly the full surface through a typed TypeScript API designed for programmatic use. The shipped skill teaches search comprehensively but has zero coverage of operations — access is granted via `allowed-tools: Bash(qmd:*), mcp__qmd__*` but no operational guidance is provided. This is deliberate (CLAUDE.md: "Never run automatically") but creates a gap for autonomous knowledge management workflows.

MCP uses the unified `query` tool with typed sub-queries (`lex:`, `vec:`, `hyde:`). Auto query expansion is CLI/SDK-only — MCP requires the agent to construct sub-queries explicitly.

## MCP Tool Surface

qmd exposes 4 tools via MCP. Supports both stdio transport (primary, used by Claude Code) and HTTP transport with `/mcp`, `/health`, and REST `/query` (alias `/search`) endpoints for daemon/multi-client use.

### `query` — Search

The primary search tool. Accepts structured sub-queries that are type-routed to the appropriate backend.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `searches` | `Array<{type, query}>` | yes | — | Typed sub-queries. `type` is `lex` (BM25/FTS), `vec` (vector similarity), or `hyde` (hypothetical document embedding). |
| `collections` | `string[]` | no | all included | Filter to named collections (OR match). Omit to search all `includeByDefault: true` collections. |
| `limit` | `number` | no | 10 | Max results returned |
| `minScore` | `number` | no | 0 | Minimum relevance score (0-1) |
| `intent` | `string` | no | — | Disambiguation context. Steers expansion, reranking, and snippet extraction. |
| `candidateLimit` | `number` | no | 40 | Max candidates sent to the reranker. Lower = faster, higher = more thorough. **Note:** accepted by the MCP schema but not passed through to `store.search()` in v2.1.0 — this is a dead parameter via MCP. Works correctly via CLI (`--candidate-limit`) and SDK (`hybridQuery`). Upstream bug. |
| `rerank` | `boolean` | no | true | Set `false` to skip LLM reranking entirely (faster, lower quality). |

**Example MCP call:**

```json
{
  "searches": [
    {"type": "lex", "query": "collection scoping"},
    {"type": "vec", "query": "how are qmd collections organized"}
  ],
  "collections": ["vault-resources"],
  "intent": "understanding current collection architecture decisions"
}
```

**Sub-query types:**

- `lex` — BM25 keyword search via FTS5. Fast (~30ms). Supports quoted phrases (`"exact match"`) and negation (`-term`).
- `vec` — vector similarity via EmbeddingGemma. Slower (~2s). Finds conceptual matches even when vocabulary differs.
- `hyde` — hypothetical document embedding. The query is treated as if it were the answer, then embedded and matched. Best for natural-language questions.

Combining multiple sub-query types in one call triggers the full hybrid pipeline (RRF fusion + reranking). A single `lex` sub-query runs BM25 only.

### `get` — Single Document Retrieval

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `file` | `string` | yes | — | File path or docid (`#abc123`). Supports line offset (`file.md:100`). |
| `fromLine` | `number` | no | — | Start from a specific line number |
| `maxLines` | `number` | no | — | Limit returned lines |
| `lineNumbers` | `boolean` | no | false | Add line numbers to output |

### `multi_get` — Batch Document Retrieval

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `pattern` | `string` | yes | — | Glob pattern (`journals/2025-05*.md`) or comma-separated list |
| `maxLines` | `number` | no | — | Limit lines per file |
| `maxBytes` | `number` | no | 10240 | Skip files larger than this (bytes). Files exceeding this limit are silently omitted from results. |
| `lineNumbers` | `boolean` | no | false | Add line numbers to output |

### `status` — Index Health

No parameters. Returns collection counts, embedding state, and staleness info.

## Re-index Triggers

qmd does not auto-index. Re-indexing is operator-initiated:

```bash
qmd update    # scan collections for new/modified files
qmd embed     # generate embeddings for unembedded documents
```

Run after: vault triage sessions, bulk file moves, new content creation, any session that changes indexed directories.

**Staleness detection:** `qmd status` reports `lastUpdated` per collection and `needsEmbedding` count. A `needsEmbedding > 0` means new content exists but isn't searchable yet.

**Current gap:** No automated trigger for re-indexing. The OpenClaw integration (see [[Research-OpenClaw-QMD-Integration]]) runs boot sync + 5-minute periodic updates for its own index, but the standalone qmd config used by Claude Code sessions has no equivalent. This means vault sessions operate on stale indexes unless the operator manually re-indexes.

**Possible solutions (not yet implemented):**
- Git post-commit hook in TheMothership that triggers `qmd update && qmd embed`
- launchd plist watching the vault directory for changes
- Claude Code PostToolUse hook on Write that triggers re-index for vault paths

## Cross-Domain Query Patterns

Agents across 3I use qmd for different query patterns:

| Domain | Typical Pattern | Collection Scope |
|--------|----------------|-----------------|
| Forge | "Has this architecture been attempted before?" | All (prior art) |
| Workshop | "What verified claims exist about hook behavior?" | `notes` (arscontexta) |
| Lab | "What's the runbook for X?" | `vault-resources` |
| Research | "What findings exist about X?" | `notes` + `vault-resources` |
| Vault | "Is this content already captured?" | All (dedup check) |

Omitting the `collection` parameter searches all collections. This is the default for prior art queries where the agent doesn't know which collection holds the answer.

## Relationship to Other Systems

| System | Relationship |
|--------|-------------|
| **Vault** | Owner. Vault content is the primary indexed corpus. Vault triage determines what enters the index. |
| **arscontexta** | Contributor. The `notes` collection is workshop-owned atomic claims indexed by qmd for cross-domain access. |
| **OpenClaw/Astrogator** | Separate consumer. OpenClaw runs its own qmd instance with a superset config (adds workspace memory, session transcripts, OpenClaw docs). Shares the same binary but different index. See [[Research-OpenClaw-QMD-Integration]]. |
| **ensue** | Not indexed. Ensue state is ephemeral coordination, not curated knowledge. If ensue findings need to persist, they route through the vault first. |
| **ADR-002** | Governance. Collection scoping rationale lives in the ADR. This spec describes the operational system the ADR governs. |

## Version History

**Installed:** v2.1.0 (Apr 5, 2026)

The installed version includes all capabilities documented in this spec. Key capabilities by release:

| Version | Date | Key Capabilities |
|---------|------|-----------------|
| v1.1.0 | Feb 20 | `includeByDefault`, `update` pre-command, unified `query` tool (replaces search/vector_search/deep_search), `collections` array filter, lex syntax (quoted phrases, negation) |
| v1.1.2 | Mar 7 | Collection `ignore` patterns, `--explain` score traces, `candidateLimit` tuning |
| v1.1.5 | Mar 7 | `intent` parameter across all surfaces |
| v2.0.0 | Mar 10 | Stable SDK API (`QMDStore`), MCP server rewritten as SDK consumer |
| v2.1.0 | Apr 5 | Global model config, AST-aware chunking (tree-sitter), `qmd bench`, `--no-rerank` |

### Capabilities Available for Collection Scoping

The following are installed and available but not yet configured:

- **`includeByDefault: false`** — hides a collection from all queries unless explicitly named via `collections` parameter. The propagation firewall: origin/provenance collections become opt-in, not default.
- **Collection `ignore` patterns** — `ignore: ["Sessions/**", "*.tmp"]` excludes files within a collection without needing separate collections. Could exclude specific subdirectories (e.g., origin/) from an area-level collection.
- **Collection `update` pre-command** — shell command that runs before every `qmd update` (config field: `update`, CLI: `qmd collection update-cmd`). Solves the re-index trigger gap.
- **`intent` parameter** — steers all five pipeline stages. Available on MCP, CLI, and SDK.
- **Collection `context` annotations** — semantic metadata describing what a collection contains.
- **`qmd bench`** — search quality benchmarks for measuring whether config changes improve retrieval.
- **`--explain`** — score traces for debugging retrieval quality.

These capabilities directly address the collection scoping and propagation concerns documented below. Collections could be restructured by trust level rather than PARA category:

- Origin/provenance material: `includeByDefault: false` — only searched when agent explicitly requests provenance
- Unvalidated theory: `includeByDefault: false` or tagged with `ignore` until confidence reaches `high`
- Current methodology, patterns, reference material: `includeByDefault: true` — default search corpus

This is a config redesign, not a code change. But it requires an ADR-level decision about whether to rescope collections from PARA boundaries to information-class boundaries. ADR-002 deferred subcategory collections on volume grounds; the question now is whether information-class scoping serves a different (more important) purpose than volume management.

## Collection Scoping Concerns

The current PARA-level collections treat all content within each bucket as equivalent. They're not. The vault contains distinct information classes with different trust levels, temporal properties, and appropriate consumption patterns:

| Information Class | Examples | Risk if Consumed as Current Truth |
|-------------------|----------|----------------------------------|
| Current methodology | Design principles, active architecture vision | Low — this IS current truth |
| Origin/provenance | Cleaned transcripts, methodology lineage, convergence records | High — describes how we got here, not where we are now |
| Unvalidated theory | Context engineering theory (confidence: low) | High — explicitly labeled as unproven |
| Evidence artifacts | Research findings, eval results, system audits | Medium — factual but context-dependent |
| Interpretation artifacts | Memos, insights, operator analysis | Medium — operator's read on the evidence, may have evolved |
| Historical | Superseded specs, old architecture docs | High — was true then, may not be true now |

An agent querying `vault-areas` gets origin documents and current methodology with no structural way to distinguish which is which. The `date` field doesn't help (see TRIAGE item on date semantics). The `confidence` tag helps but only if the consuming agent checks it.

**Propagation risk:** This is the mechanism behind investigation 003 (operator-terminal propagation). A contextually valid interpretation gets retrieved by an agent in a different domain, treated as universal truth, and applied without scope checking. The damage compounds silently across gates.

**Mitigations available but not yet used:**

1. **Collection `context` annotations** — qmd supports semantic metadata on collections that describe the content type. Not configured. Would let the consuming agent know "this collection contains origin/provenance material" before interpreting results.

2. **Global model config** — different embedding models could theoretically be optimized for different information classes, but model config is global (not per-collection as CHANGELOG claims). Would require separate qmd instances.

3. **Subcategory-level collections** — splitting `vault-areas` into finer-grained collections (e.g., separate `vault-origin` from `vault-methodology`) would let agents scope queries to the right information class. ADR-002 deferred this but the rationale was volume-based, not information-class-based.

4. **Intent parameter** — agents declaring intent on every query steers results toward the right domain. Available now, not systematically used.

5. **Frontmatter-based filtering** — qmd chunks include frontmatter. An agent could filter on `confidence: high` or exclude `tags: origin`. Requires the consuming agent to know to do this.

**The fundamental question:** Should collection scoping be rescoped to separate information classes rather than PARA categories? This would mean the collections map to trust/temporality boundaries rather than organizational boundaries. The answer affects every downstream consumer. This is an ADR-level decision, not a config tweak.

## Known Gaps

1. **No automated re-index trigger** for the standalone config. Operator must run `qmd update && qmd embed` manually after vault changes. The `update` pre-command solves this for remote-synced collections but not for local changes.
2. **No subcategory-level collections.** ADR-002 deferred this — current volume doesn't create retrieval noise at PARA level. Revisit when ADR centralization from other domains increases volume.
3. **Index staleness in Claude Code sessions.** The qmd MCP server loads on session start with whatever index state exists. Changes made during the session aren't reflected in search results until re-indexed.
4. **No collection for 00_Inbox during triage.** Agents triaging inbox files can't use qmd to check for duplicates in the inbox itself — only in indexed destinations. This is by design (ADR-002 principle: nothing lives in inbox permanently) but creates a workflow gap during triage.
5. ~~**Collection `context` annotations not configured.**~~ RESOLVED 2026-04-08. All 5 collections have context annotations describing content type, trust caveats, and consumption guidance.
6. ~~**Intent not systematically used.**~~ PARTIALLY RESOLVED 2026-04-08. Intent convention added to vault CLAUDE.md. Structural enforcement (pre-filled intent in skill/gate templates) is the next step — done per-skill as skills are created/updated.
7. ~~**Information-class conflation in PARA-level collections.**~~ RESOLVED 2026-04-08. Origin material carved out as `vault-origin` (`includeByDefault: false`). PARA boundaries retained with layered mitigations (annotations, intent, confidence filtering). Q1a bench confirmed origin carve-out effective. Historical contamination remains as a known residual — mitigated by annotations, not collection scoping. See [[Eval-QMD-Q1a-Contamination-Bench]].
8. **Global model config advertised as per-collection.** The CHANGELOG claims per-collection model config but the implementation is global. All collections share the same embed/rerank/generate models. Different models per collection would require separate qmd instances with separate configs.

## Open Questions

Consolidated from Collection Scoping Concerns, Version History, and Known Gaps above. These are the unresolved decisions that block qmd from serving its full role as 3I search infrastructure. Ordered by dependency — later questions depend on earlier ones.

All capabilities referenced below are installed and available (v2.1.0). These are decision and configuration questions, not upgrade questions.

### 1. PARA boundaries or information-class boundaries?

Should collections map to where content lives (Projects/Areas/Resources) or to what class of information it is (current methodology, origin/provenance, unvalidated theory, evidence, interpretation, historical)?

PARA scoping (current) optimizes for organizational navigation — agents can target `vault-resources` for reference lookups. Information-class scoping would optimize for trust — agents wouldn't accidentally consume origin material as current truth.

**Preliminary analysis (2026-04-06):** An in-session audit of `vault-areas` suggested the mixing problem was concentrated in origin material (7 files in Areas/origin/).

**Independent audit (2026-04-06):** A separate agent session audited all 348 files across all three collections with file-level classification. Key corrections to the preliminary analysis:

- **Origin-provenance is broader than Areas/origin/.** 17 files across all collections, not 7. Only 41% live in the carve-out target directory. 10 are scattered across Areas/3I/ (3), Resources/forge-archaeology/ (2), Resources/collections/ (1), and Projects/ (3).
- **Unvalidated theory is 4x larger than estimated.** 11 files, not 2-3. `confidence: low` catches 6/11 but misses 5 that have medium, no tag, or are identifiable only by content.
- **Projects is the biggest historical graveyard.** 26 of 38 historical files (68%) live in Projects — the collection we didn't discuss in the preliminary analysis. 21.5% of Projects content is stale.
- **The Memo- prefix is broken as an information-class signal.** Spans 6 of 9 classes; 43% of Memo- files are actually reference material. Cannot be relied upon for agent-level filtering.
- **Vault grew 21% since spec was written.** 348 files vs 288 documented. Index is stale.
- **The `confidence` tag is the strongest cross-class signal.** `confidence: low` reliably identifies high-risk content. `confidence: high` reliably indicates safe-for-default-search.

Full audit: [[Eval-QMD-Collection-Information-Class-Audit]].

The origin carve-out is still worth doing — it captures the most concentrated pocket of risk. But it's necessary, not sufficient. The mitigation strategy needs to be multi-layered:

1. **Origin carve-out** (Q4) — captures the 7 most obviously-labeled origin files
2. **Confidence-based filtering convention** — agents filter `confidence: low` out of default results; catches high-risk content across all collections regardless of directory
3. **Context annotations** (Q3) — warns agents about what's in each collection, including temporal context for forge-archaeology and historical project content
4. **Intent mandate** (Q5) — agents declare information-class context on every query

**Leaning: PARA + layered mitigations.** ADR-002 amendment would say: PARA remains primary; origin is carved out as opt-in; high-risk content across all collections is mitigated by confidence filtering, context annotations, and intent conventions. No full information-class restructuring.

**Requires: ADR-002 amendment.** Q1a bench testing validates whether the layered approach produces acceptable retrieval quality.

#### 1a. Does `qmd bench` show retrieval contamination?

Before committing to the PARA + origin carve-out, build a test fixture and measure empirically. Test queries that exercise the information-class problem:

- Query "current methodology" or "design principles" — do origin docs or point-in-time assessments appear in results?
- Query "infrastructure architecture" — does the 2026-02-17 system assessment rank alongside current docs?
- Query "how does the Ralph loop work" — does origin/provenance material outrank current methodology docs?

Use `--explain` to understand why contaminating results rank where they do. If contamination is limited to origin material, the carve-out is sufficient. If point-in-time docs or unvalidated theory also contaminate, the mitigation needs to be broader (additional `ignore` patterns, confidence-based filtering conventions, or additional collection splits).

Also test the inverse: query something that should return origin material (e.g., "how did the forge doctrine originate") against the current config where origin IS in default search. Measure baseline retrieval quality. After the carve-out, run the same query with explicit `collections: ["vault-origin"]` opt-in and compare. If the opt-in path produces worse results than the default path, the carve-out degrades the provenance use case.

**No blockers — run this now.** The test fixture can be built against the current PARA config on the installed v2.1.0. This test should be run by an external agent, not the session that designed the carve-out.

### 2. What information classes exist in this vault?

**Independent audit completed (2026-04-06).** A separate agent session classified all 348 files across all three collections using a 9-class taxonomy. Full results: [[Eval-QMD-Collection-Information-Class-Audit]].

Aggregate distribution:

| Class | Count | % | Risk Level |
|-------|------:|--:|------------|
| reference | 133 | 38.2% | Low |
| evidence | 88 | 25.3% | Medium (context-dependent) |
| historical | 38 | 10.9% | High (stale, may mislead) |
| current-methodology | 20 | 5.7% | Low (this IS current truth) |
| interpretation | 19 | 5.5% | Medium (may have evolved) |
| origin-provenance | 17 | 4.9% | High (lineage, not current) |
| active-project | 16 | 4.6% | Low (current work) |
| unvalidated-theory | 11 | 3.2% | High (explicitly unproven) |
| uncategorizable | 1 | 0.3% | — |

High-risk classes total 66 files (19%) across all collections. These are not concentrated in one directory or one collection — they're distributed. The mitigation strategy must work across boundaries, not just at directory level.

The practical distinction is not binary (origin vs everything else). It's tiered: `confidence: low` reliably identifies the highest-risk subset (6/7 low-confidence files are unvalidated-theory). `confidence: high` reliably marks safe-for-default-search content. The gap is the 35+ files at `confidence: medium` that span 6 classes.

Connects to the retroactive evidence/interpretation scrub in TRIAGE.md.

#### 2a. Does the Research-/Memo- prefix convention need enforcement?

**Audit quantified the leakage (2026-04-06):**

- **Research-** prefix: ~94% reliable for evidence (3 of ~47 Research- files are non-evidence). Strong directional signal. But the reverse is weak: many evidence files lack the Research- prefix (Notes, Sessions, Evals, tool captures). Research- → evidence is reliable; evidence → Research- is not.
- **Memo-** prefix: broken as an information-class signal. Spans 6 of 9 classes. 43% of Memo- files in Resources are actually reference material, not interpretation. Any agent-level logic treating Memo- as "interpretation" would be wrong 71% of the time.
- **Eval-** prefix: 100% reliable for evidence (6/6).
- **Pattern-** prefix: 70% reference, 20% current-methodology, 7% unvalidated-theory. Reliable for "reusable technique" but not for a single information class.

The Q1 layered mitigation should not rely on prefix-based filtering at the agent level. The `confidence` frontmatter tag is the stronger signal. The TRIAGE item on evidence/interpretation scrub remains relevant but is now maintenance work rather than a mitigation dependency.

#### 2b. Should forge-archaeology get the same treatment as origin?

**Audit found the picture is more nuanced than initially presented.** Of 16 files in forge-archaeology/:

- 12 are evidence with reusable architectural patterns (confirmed by content inspection — YouTube teardowns have 22-85+ extracted patterns each)
- 2 are pure origin-provenance (00-the-rift, ralph-provenance-chain)
- 1 is current-methodology (Architecture-Autonomous-Forge-Pipeline)
- 1 is reference (README)

6 of the 12 evidence files carry origin-provenance as a secondary class. They're hybrids: the patterns are referenceable, but the framing is historical. An agent consuming a teardown as pure reference material could misread historical framing as current state.

Leaning holds: keep forge-archaeology in `vault-resources`. The patterns are genuinely reusable and agents doing prior art searches need them. The collection `context` annotation (Q3) must mention the temporal context. The 2 pure origin-provenance files (00-the-rift, ralph-provenance-chain) are edge cases — they're in the wrong directory for their class but moving them would break cross-references within the archaeology corpus.

### 3. Should collection `context` annotations be configured?

Yes. Zero config effort, immediately useful, cheap to revise. Each collection gets a prose description that the MCP server injects into dynamic instructions. No blockers — can be done today.

The annotations need to thread a needle: descriptive enough to be accurate regardless of future restructuring, but specific enough to help agents distinguish information classes within a PARA bucket. This is a context engineering concern — the annotation text is agent-facing prose that shapes how results are interpreted.

**Draft annotations:**

```yaml
collections:
  vault-projects:
    context: "Active and historical project work. Contains current specs, plans, and project notes alongside stalled/abandoned projects (21% historical content). Check project README status fields — projects marked Paused, Planning, or with no recent activity may contain superseded specs and never-built designs. Treat dated project artifacts with the same caution as point-in-time documents."
  vault-areas:
    context: "Ongoing domain knowledge. Includes current methodology, field journals, evaluations, and configuration docs. Also contains Areas/origin/ (methodology lineage, cleaned transcripts) which describes how we got here, not where we are now — treat origin material as historical context, not current truth."
  vault-resources:
    context: "Reference material: reusable patterns, operational memos, research findings, prompt templates, runbooks, and ADRs. Includes Resources/research/forge-archaeology/ (teardowns of historical systems that may no longer exist). Check confidence frontmatter — low confidence material is explicitly unvalidated."
  notes:
    context: "Atomic knowledge claims from arscontexta (workshop-owned). Prose-as-claim format, semantically connected. These are structured extractions, not operator narrative. Trust level depends on the source chain documented in each note."
```

#### 3a. Should annotations encode behavioral directives or just descriptions?

The vault-areas draft includes "treat origin material as historical context, not current truth" — that's a directive, not a description. Descriptive alternative: "includes methodology lineage in Areas/origin/." The directive approach is more protective (explicitly warns the agent) but more brittle (encodes assumptions about risk that may change). Leaning directive — an annotation that names origin material without explaining the risk isn't doing the protective work that motivated Q3 in the first place.

#### 3b. Do annotations survive restructuring?

If Q1 resolves with the origin carve-out (new `vault-origin` collection), the vault-areas annotation would need updating to remove the origin caveat, and `vault-origin` would get its own annotation. Low cost — a config edit. Annotations written now against PARA may need revision, but this is routine maintenance, not rework.

#### 3c. Should we re-index before configuring annotations?

Annotations are config-level, not index-level — they take effect immediately regardless of index state. But the index is 10-12 days stale (vault-areas last updated 2026-03-25, vault-projects 2026-03-14). If Q1a bench testing follows annotation work, re-indexing first ensures bench results reflect current vault content. The annotation config and the re-index are independent tasks but both are prerequisites for Q1a.

**Action sequence:** Re-index (`qmd update && qmd embed`), configure annotations in `~/.config/qmd/index.yml`, then annotations are live for all subsequent MCP sessions and ready for Q1a bench testing.

### 4. Should `includeByDefault: false` be used for any current collections?

Yes, for origin material specifically. Create a new `vault-origin` collection pointing at `Areas/origin/` with `includeByDefault: false`, and add `ignore: ["origin/**"]` to the `vault-areas` collection. Origin material becomes opt-in; current areas remain default.

This is the implementation of Q1's PARA + origin carve-out. The mechanism is clean: default searches hit vault-projects, vault-areas (minus origin), vault-resources, and notes. An agent that explicitly needs provenance passes `collections: ["vault-origin"]`.

**Edge case tested (2026-04-06):** Would prior art searches lose signal by missing origin? No. Origin content is lineage and narrative ("collaborative archaeology," "breadcrumbs → validated → receipted"), not architectural reference. The actionable patterns extracted from origin moments already live in Resources/patterns/ and Areas/forge/ as promoted, current-truth documents. A Forge agent doing prior art search wouldn't miss anything actionable.

**Draft config change:**

```yaml
collections:
  vault-origin:
    path: /Users/basher8383/3I/Vault/TheMothership/Areas/origin
    pattern: "**/*.md"
    includeByDefault: false
    context: "Methodology lineage and provenance. Cleaned transcripts, archaeology sessions, convergence records. Describes how we got here, not where we are now. Treat as historical context, not current truth. Opt in explicitly when investigating the origin of a methodology, pattern, or decision."
  vault-areas:
    path: /Users/basher8383/3I/Vault/TheMothership/Areas
    pattern: "**/*.md"
    ignore: ["origin/**"]
    context: "Ongoing domain knowledge. Current methodology, field journals, evaluations, and configuration docs. Check confidence frontmatter — low confidence material is explicitly unvalidated."
```

Depends on: Q1 confirmation (contingent on Q1a bench results and Q2 clean audit).

#### 4a. What's the re-embedding cost?

Creating `vault-origin` (7 files) and excluding origin from `vault-areas` requires re-embedding for both collections. The origin collection is trivial (7 files). Need to confirm whether adding `ignore` patterns to an existing collection triggers selective re-embedding or requires a full collection re-embed. If full re-embed: vault-areas is 71 docs minus 7, still small. Total cost is low either way.

#### 4b. Should any other subdirectories get `ignore` treatment?

While editing the config, is there anything else worth excluding from default search? Candidates considered:

- `Areas/troubleshooting-sessions/` — 2 files, point-in-time diagnostic work. Low default search value but also noise-level volume. Not worth a carve-out.
- `Resources/research/forge-archaeology/` — 14 historical teardowns. Considered in Q2b; leaning keep in default because teardowns contain reusable architectural patterns even though source systems may be dead.

Answer: no additional exclusions for now. Revisit if Q1a bench testing shows contamination from these directories.

#### 4c. How do consuming agents learn to opt in?

Setting `includeByDefault: false` hides origin from default searches, but nothing teaches an agent when to explicitly request it. The `context` annotation on `vault-origin` describes what's there, but only agents that already know to look would see it.

Mitigation: domain-specific agent instructions (CLAUDE.md files, skills, gate plans) should include a convention like "when investigating methodology lineage, provenance, or the origin of a pattern or decision, include the vault-origin collection." This connects to Q5 (intent mandates) — the opt-in convention and the intent convention are complementary. Intent steers result interpretation; collection opt-in controls what enters results in the first place.

### 5. Should intent be mandated in agent instructions?

Yes, at the structural level. The MCP server instructions already say "Always provide `intent` on every search call" — but that's advice in the tool description, and it's not changing behavior. Three enforcement levels:

1. **Convention** — CLAUDE.md files say "provide intent." Compliance depends on the model following the instruction. Weakest.
2. **Structural** — Skills and gate plans include intent as a pre-filled field in their qmd query patterns. The path of least resistance is compliance because the template already has it. Recommended.
3. **Enforced** — PreToolUse hook rejects qmd calls without intent. Too rigid — blocks legitimate quick lookups where intent is unnecessary.

Level 2 (structural) is the sweet spot. Convention alone doesn't work (the existing MCP instruction proves this). Enforcement is brittle and needs exception logic. Structural means the patterns agents follow already include intent.

**Where the convention lives:** Not in domain-specific CLAUDE.md files (5 repos, maintenance burden, easy to drift). The MCP server's dynamic instructions (fed by Q3's `context` annotations) are the one surface every consuming agent sees regardless of domain. The convention should be reinforced there. CLAUDE.md files can reference it but shouldn't be the primary home.

**Interaction with Q4:** If origin is `includeByDefault: false`, intent becomes less critical for the origin contamination problem — origin simply isn't in default results. But intent still matters for disambiguation within default collections (unvalidated theory, point-in-time docs, evidence vs interpretation). Q4 handles the binary in/out decision; Q5 handles disambiguation within what's included. They're complementary.

No blockers — can be done today.

#### 5a. What does good intent look like?

Intent for vault queries should signal the information-class context, not just the topic. Examples:

- `intent: "current infrastructure architecture decisions"` — signals current truth, not historical
- `intent: "reusable patterns for autonomous agent loops"` — signals reference material
- `intent: "how the Ralph loop methodology originated"` — signals provenance (would also trigger vault-origin opt-in per Q4c)
- `intent: "unvalidated hypotheses about context engineering"` — explicitly asks for low-confidence material

Freeform is the right approach — prescribing intent vocabulary creates taxonomy maintenance burden. But the convention should include examples demonstrating the information-class dimension so agents learn to signal temporality and trust level, not just topic.

#### 5b. Which surfaces need updating?

The convention needs to reach every agent that queries qmd:

| Surface | Mechanism | Effort |
|---------|-----------|--------|
| MCP dynamic instructions | Q3 context annotations (agents see these every session) | Config change, done with Q3 |
| Vault CLAUDE.md | Add qmd query convention with intent examples | One file edit |
| Other domain CLAUDE.md files | Reference the convention, don't duplicate it | Lightweight, can defer |
| Skills and gate plans | Pre-fill intent in query templates | Per-skill, done as skills are created/updated |

The MCP dynamic instructions + vault CLAUDE.md cover the primary use case. Cross-domain CLAUDE.md updates can follow as those repos are touched.

### 6. How does the `date`/`originated` frontmatter convention affect retrieval?

The TRIAGE item on frontmatter date semantics proposes `date` (document created/last substantive revision) vs `originated` (when underlying events occurred, only when different). This affects retrieval when agents do temporal reasoning about results — inferring currency, staleness, or causal sequence from dates in chunks.

**Scope of the problem (2026-04-06):** 243 vault files have `date` frontmatter. Roughly 20 have a meaningful divergence between document creation and information origin: 6 origin files, some ai-methodology files (e.g., `homelab-ai-partner` — methodology started Dec 2025, document written Jan 17), and cross-system ingestion. Under 10% of the corpus.

**Interaction with Q4:** If origin material is in `vault-origin` with `includeByDefault: false`, agents won't encounter origin dates in default searches. The date ambiguity is most acute in origin material, so the carve-out reduces the urgency of this convention. But it doesn't eliminate it — ai-methodology files with date divergence remain in default search.

**Leaning:** Implement `originated` as an optional frontmatter field. Not urgent — the Q4 carve-out handles the highest-risk case. The `originated` field is a refinement for temporal reasoning within default collections, not a load-bearing scoping mechanism. Apply retroactively to the ~20 files where it matters.

#### 6a. Is `originated` needed if collection scoping already handles the risk?

If origin material is opt-in (Q4) and the context annotation warns about temporality (Q3), agents in default search already have two layers of protection. Adding `originated` is belt-and-suspenders. The belt (scoping) handles the binary case (is this origin?). The suspenders (frontmatter) handle the gradient case (how old is the thinking in this non-origin doc?).

The gradient case is real but low-frequency. `homelab-ai-partner` is the clearest example: an agent querying "current AI partnership methodology" gets a doc whose `date` says January but whose thinking started in December. The one-month gap probably doesn't change how an agent interprets the doc. For longer gaps, `originated` would matter more.

Leaning: implement for completeness and future-proofing, but don't block Q1-Q5 on it.

#### 6b. Where does the convention live?

Two documents need to reference `originated`:

- **Memo-Vault-Tagging-Standards** — owns frontmatter conventions. Add `originated` as an optional field with semantics: "date when underlying information originated, only when different from `date`."
- **This spec (Memo-QMD-Spec)** — owns retrieval semantics. Document that qmd chunks include both fields when present, and agents can use lex queries to filter by date range.

The tagging standard is the authoritative definition. This spec documents the retrieval implications.

### Decision Sequence — Resolution Status (2026-04-08)

```text
Q3 (context annotations) ── DONE 2026-04-08
Q5 (mandate intent) ── DONE 2026-04-08 (convention in CLAUDE.md; structural enforcement per-skill ongoing)
         │
         └──→ Q1a (bench test) ── DONE 2026-04-08 ──→ Q1 (confirm layered approach) ── CONFIRMED
                                                                    │
                                                                    ├──→ Q4 (origin carve-out) ── DONE 2026-04-08
                                                                    └──→ confidence filtering convention ── DONE 2026-04-08

Q2 (full taxonomy) ── ANSWERED by audit (348 files, 9 classes)
Q6 (date semantics) ── independent, low urgency, deferred
```

**Completed:** Q3 (annotations), Q4 (origin carve-out with `includeByDefault: false`), Q5 (intent convention in CLAUDE.md), Q1a (bench test — 14 queries, origin carve-out confirmed effective), Q1 (layered approach confirmed), Q2 (audit provides authoritative classification). qmd upgraded 1.0.7 → 2.1.0. Full re-embed with 2.1.0 chunking.

**Remaining:** Q6 (date semantics) deferred — low urgency, origin carve-out handles the highest-risk case. Bench fixture paths need refinement for regression testing. Structural intent enforcement (pre-filled intent in skill/gate templates) ongoing per-skill.
