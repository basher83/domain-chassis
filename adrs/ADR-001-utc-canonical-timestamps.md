# ADR-001: UTC-Canonical Timestamps in `_shared/now.mjs`

**Status:** Proposed
**Date:** 2026-05-30T02:38:45Z
**Authors:** Brent, Claude
**Reviewers:** Brent

## Context

The chassis ships a shared timestamp primitive, `skills/_shared/now.mjs`, that skills use to stamp ISO datetimes and to mint slug-form creation records — for example run directories like `.questionnaire/2026-05-18_17-34-12`. The original implementation built both outputs from the host's local clock and timezone, via `new Date()` and `getTimezoneOffset()`.

That host-derived basis is unreliable wherever the chassis runs off the operator's own machine. In a Cowork sandbox the host is UTC, so the emitted offset — and, within the hour around midnight, the calendar day itself — disagrees with the operator's local frame. The chassis is a published plugin registered in a marketplace; any consumer who installs it, including a different operator running it in their own Cowork, inherits the same host dependence. Their sandbox zone is neither knowable at authoring time nor guaranteed to match their local zone, and the shell layer has no trustworthy local-zone signal in these environments.

A second defect is independent of sandboxes. A local-time slug is non-monotonic across the DST fall-back transition: the 01:00–02:00 local hour repeats once a year, so slug keys minted in that window can collide or sort backwards. Because the slug is a deterministic creation record used as a sort key and unique id — not a human-facing date — monotonicity and uniqueness are precisely the properties it must hold, and local time breaks them.

### Research Foundation (provenance)

Surfaced during a hub-level session on 2026-05-29 while applying `now.mjs` to an ADR Date block: run from the sandbox it returned a `+0000` stamp a day ahead of the operator's local date. The analysis that followed — framed as "what is the stamp for" — established that the slug is a machine record (ordering and identity), which is the canonical case for UTC. Recorded directly rather than promoted from an `analysis/` investigation, the same lifecycle deviation noted in workshop-polish ADR-002.

## Decision

Build both outputs of `now.mjs` from UTC `Date` components and emit the ISO form with a trailing `Z`. The slug remains the first 19 characters of the ISO string with `T`→`_` and `:`→`-`, now on a UTC basis. All chassis-generated timestamps are UTC-canonical. Localization, if ever needed for a human-facing surface, happens at that surface where the target zone is explicitly known — never in the shared primitive.

### Key Decision Factors

- Host independence: UTC getters produce an identical result on the operator's machine, a Cowork sandbox, and any published-plugin consumer, with zero per-consumer configuration.
- Correct basis for the slug's purpose: as an ordering and identity key, UTC is monotonic and collision-free, including across the DST fall-back hour.
- Fewer moving parts: removing the offset computation makes the primitive smaller and deletes its only locale- and host-dependent branch.
- Ambiguity pushed to the edge: the primitive stays deterministic; any need for local rendering is localized where the zone is answerable.

## Architecture Decisions Matrix

| Decision Point | Options Considered | Selected | Rationale |
|---|---|---|---|
| **Timestamp basis** | UTC-canonical, split (UTC slug / local human date), parameterized IANA zone | UTC-canonical everywhere | The only option correct and identical across host, sandbox, and distributed consumers with no config, and it removes the DST slug defect. Split reintroduces the host-zone problem for the human half in Cowork; parameterized adds a config knob every consumer must set. |
| **ISO offset form** | `Z`, `+0000` | `Z` | Unambiguous UTC marker. `+0000` reads as a coincidental offset and invites local reinterpretation. |
| **Slug basis** | UTC, local | UTC | The slug is a machine ordering and identity record; UTC guarantees monotonicity and uniqueness. |
| **Where localization lives** | in the primitive, at the consuming edge | at the edge | Keeps the shared primitive deterministic and host-independent; the target zone is only knowable at the surface that renders for a human. |

## Technical Approach

`now.mjs` builds the ISO string from `getUTCFullYear`/`Month`/`Date`/`Hours`/`Minutes`/`Seconds` and appends `Z`; the timezone-offset block is removed. Slug derivation is unchanged in form — `slice(0, 19)`, `T`→`_`, `:`→`-` — and naturally excludes the trailing `Z`. The tab-separated, no-trailing-newline output contract is preserved, so every existing consumer that inlines the value is unaffected in format.

## Risk Assessment

### Mixed-Basis History

1. **Pre-existing local-basis records**
   - Description: Slugs and ISO stamps minted before this change are local-basis; new ones are UTC. A corpus may contain both, and ordering across the boundary is only approximate.
   - Mitigation: The shift is a one-time basis change. Both forms remain valid ISO and slug shapes, so nothing breaks structurally, and new records are internally consistent and monotonic from here forward.
   - Fallback: If continuous ordering across the boundary is ever required, local-basis stamps can be reinterpreted by their known historical offset; no re-mint is needed.

### Human Readability

2. **UTC stamps read as "tomorrow" in evening local time**
   - Description: A human reading a UTC Date block in the evening in US zones sees the next calendar day.
   - Mitigation: Adopt the standing convention that all chassis and 3I timestamps are UTC, and read them accordingly. Slugs are not human-facing and are unaffected.
   - Fallback: Localize at a specific human-facing surface if one ever warrants it.

## Success Metrics

- `now.mjs` returns an identical-format UTC stamp on the operator's machine, a Cowork sandbox, and a fresh plugin install, with no configuration.
- Slug keys sort monotonically through a DST fall-back window.
- No consumer requires changes to parse the output — the format contract is preserved.

## Consequences

### Positive

- The primitive is correct and identical everywhere the chassis runs, including distributed Cowork installs.
- The slug is a sound ordering and identity key, immune to the DST fall-back collision.
- The primitive is smaller and simpler — the host-dependent branch is gone.

### Negative

- Human-facing UTC stamps can show the next calendar day in evening local time, absorbed by the UTC convention.
- A one-time mixed-basis boundary exists in any historical corpus of stamps and slugs.

### Neutral

- The output format — `iso<TAB>slug`, no trailing newline — is unchanged; consumers remain format-compatible.

## Alternatives Considered

Split basis — UTC for slugs, local for human-facing dates. Produces correct slugs, but the local half still cannot source a zone in a sandbox or a distributed consumer's Cowork, so it reintroduces the original defect for exactly the case that motivated the change, and adds a second code path.

Parameterized zone — accept an IANA zone by argument or `TZ` and compute the offset via `Intl`. Most capable, and yields true local stamps anywhere, but it adds a configuration knob every consumer must set and still needs a sane default when unset. More moving parts than the problem warrants, against a stated preference for fewer moving parts.

## Dependencies

- `skills/_shared/now.mjs` — changed to UTC-canonical.
- `skills/_shared/now.test.ts` — assertions updated to the UTC contract (ISO requires trailing `Z`, no numeric offset).
- Consumers that mint slug directories or stamp ISO via `now.mjs` inherit the new basis automatically; no consumer-side format change is required.

## Related Documents

- `skills/_shared/now.mjs` — the primitive
- `skills/_shared/now.test.ts` — contract tests
- `workshop/workshop-polish/adrs/ADR-002-loop-b-driver-skill-naming.md` — first ADR to stamp its Date via `now.mjs`; surfaced this issue
- `domain-chassis/templates/adr-template.md` — ADR template
