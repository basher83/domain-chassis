// Print one tab-separated line: <iso>\t<slug>
//   <iso>  — ISO 8601 in UTC, e.g. 2026-05-30T02:21:27Z
//   <slug> — first 19 chars of <iso> with `T`→`_` and `:`→`-`, e.g. 2026-05-30_02-21-27
// No trailing newline so the value can be inlined cleanly.
//
// UTC-canonical (see chassis ADR-001). The timestamp is built from UTC Date
// components, so it is identical on any host — your machine, a Cowork sandbox, or
// any published-plugin consumer — and never depends on the host's locale or zone.
// The slug is a deterministic creation record (sort key / unique id), so UTC also
// keeps it monotonic and collision-free across the DST fall-back hour, which a
// local-time slug is not.
const d = new Date();
const pad = (n) => String(n).padStart(2, "0");
const iso = `${d.getUTCFullYear()}-${pad(d.getUTCMonth() + 1)}-${pad(d.getUTCDate())}T${pad(d.getUTCHours())}:${pad(d.getUTCMinutes())}:${pad(d.getUTCSeconds())}Z`;
const slug = iso.slice(0, 19).replaceAll(":", "-").replace("T", "_");
process.stdout.write(`${iso}\t${slug}`);
