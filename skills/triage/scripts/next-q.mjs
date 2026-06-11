#!/usr/bin/env node
/**
 * Triage Q-number resolution and why-draft scaffolding — deterministic, dependency-free.
 *
 * Owns the two mechanical halves of triage intake that used to be agent prose:
 *   1. scaffolding the why-draft from the version-controlled template, and
 *   2. computing the next Q-number and committing the draft to its numbered name.
 *
 * `now.mjs`-shaped on purpose (see skills/_shared/now.mjs and chassis ADR-001):
 * plain `node`, only `node:` built-ins, no bun runtime, no NODE_PATH, no Pi
 * credential. Contrast skills/triage/scripts/cold-review.ts, which needs all three —
 * this script must run anywhere `node` does.
 *
 * Number-at-commit by construction: `scaffold` mints NO number (the draft is named
 * `Q-draft-{slug}-why.md`); `commit` computes `max(Q[0-9]+)+1` over the union of
 * three durable sources and renames the draft to `Q{n}-why.md` only then. A draft
 * that never reaches `commit` leaves a `Q-draft-…` file that — because `Q` is
 * followed by a non-digit — matches no `Q[0-9]+` and so claims no number. That is
 * the structural fix for the assigned-but-uncommitted orphan (the Q73 failure mode).
 *
 * Usage:
 *   node next-q.mjs scaffold [--root <dir>]
 *       Write `<root>/Q-draft-{slug}-why.md` from ../references/why-template.md.
 *       No number is computed or assigned. Prints the created path.
 *
 *   node next-q.mjs compute [--root <dir>]
 *       Dry run: scan the three sources and print a JSON report of the per-source
 *       numbers, the cross-source max, and next = max+1. Writes nothing.
 *
 *   node next-q.mjs commit --draft <path> [--root <dir>]
 *       Compute next over the three sources, rename <path> -> `<root>/Q{next}-why.md`,
 *       stamp its `Frozen:` line with the UTC instant, substitute the number into the
 *       `# Q{n} Why:` title, and emit a QUEUE.md row stub carrying the number. The
 *       row's prose cells stay agent-authored — the script owns the number and the
 *       row, not the Intent/Scope/Next content.
 *
 * Options:
 *   --root <dir>    Workspace root the three sources are scanned under, and where the
 *                   draft / why-record is written. Default: process.cwd(). (The
 *                   template is always read relative to THIS script, never --root.)
 *   --draft <path>  (commit only) Path to the Q-draft-…-why.md scaffold to promote.
 *
 * The three number sources (union):
 *   - QUEUE.md table rows         (the leading `| Q{n}` cell of each row)
 *   - root `Q{n}-*.md` artifacts  (active gates and why-records)
 *   - gates/`Q{n}-*.md` artifacts (the cleared archive)
 *
 * Exit codes (fail-closed and loud):
 *   0  success.
 *   2  usage error (unknown subcommand/flag, missing --draft, unreadable template
 *      or draft, malformed template).
 */

import { readFileSync, writeFileSync, readdirSync, existsSync, rmSync, statSync } from "node:fs";
import { join, resolve, basename } from "node:path";
import { fileURLToPath } from "node:url";

const die = (code, message) => {
  process.stderr.write(`next-q: ${message}\n`);
  process.exit(code);
};

// UTC-canonical instant + slug, identical to skills/_shared/now.mjs (chassis ADR-001).
const utcNow = () => {
  const d = new Date();
  const pad = (n) => String(n).padStart(2, "0");
  const iso = `${d.getUTCFullYear()}-${pad(d.getUTCMonth() + 1)}-${pad(d.getUTCDate())}T${pad(d.getUTCHours())}:${pad(d.getUTCMinutes())}:${pad(d.getUTCSeconds())}Z`;
  const slug = iso.slice(0, 19).replaceAll(":", "-").replace("T", "_");
  return { iso, slug };
};

const parseFlags = (argv) => {
  const flags = {};
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === "--root") flags.root = argv[++i];
    else if (a.startsWith("--root=")) flags.root = a.slice("--root=".length);
    else if (a === "--draft") flags.draft = argv[++i];
    else if (a.startsWith("--draft=")) flags.draft = a.slice("--draft=".length);
    else die(2, `unknown argument: ${a}`);
  }
  return flags;
};

// Extract a Q-number from a filename's leading `Q{digits}-` segment. A name whose
// `Q` is not immediately followed by a digit (Q-draft-…, QUEUE.md) returns null —
// this is the by-construction draft/orphan exclusion, not a special case.
const numberFromFilename = (name) => {
  const m = name.match(/^Q(\d+)-/);
  return m ? Number(m[1]) : null;
};

// List the Q-ish .md files in a directory and their extracted number (null if none),
// so a `compute` report makes the Q-draft exclusion visible. QUEUE.md is scanned
// separately (queue rows) and is omitted here.
const qFilesIn = (dir) => {
  const out = {};
  if (!existsSync(dir)) return out;
  for (const name of readdirSync(dir)) {
    if (name === "QUEUE.md" || !name.endsWith(".md")) continue;
    if (!name.startsWith("Q")) continue;
    out[name] = numberFromFilename(name);
  }
  return out;
};

const queueRowNumbers = (root) => {
  const p = join(root, "QUEUE.md");
  const rows = {};
  if (!existsSync(p)) return rows;
  for (const line of readFileSync(p, "utf8").split("\n")) {
    const m = line.match(/^\|\s*Q(\d+)\b/);
    if (m) rows[m[1]] = Number(m[1]);
  }
  return rows;
};

const computeSources = (root) => {
  const queue = queueRowNumbers(root);
  const rootArtifacts = qFilesIn(root);
  const gatesArtifacts = qFilesIn(join(root, "gates"));
  const all = [
    ...Object.values(queue),
    ...Object.values(rootArtifacts),
    ...Object.values(gatesArtifacts),
  ].filter((n) => typeof n === "number");
  const max = all.length ? Math.max(...all) : 0;
  return {
    root: resolve(root),
    sources: {
      queue_rows: Object.values(queue).sort((a, b) => a - b),
      root_artifacts: rootArtifacts,
      gates_artifacts: gatesArtifacts,
    },
    max,
    next: max + 1,
  };
};

const readCoreTemplate = () => {
  const templatePath = fileURLToPath(new URL("../references/why-template.md", import.meta.url));
  let text;
  try {
    text = readFileSync(templatePath, "utf8");
  } catch (e) {
    die(2, `cannot read why-template.md at '${templatePath}': ${e instanceof Error ? e.message : String(e)}`);
  }
  const m = text.match(/```markdown\n([\s\S]*?)\n```/);
  if (!m) die(2, `could not find the core \`\`\`markdown block in why-template.md (${templatePath})`);
  // Blank the Frozen line — scaffold mints no date; commit stamps it at PASS.
  return m[1].replace(/^Frozen:.*$/m, "Frozen:");
};

const cmdScaffold = (flags) => {
  const root = resolve(flags.root ?? process.cwd());
  const { slug } = utcNow();
  const core = readCoreTemplate();
  const dest = join(root, `Q-draft-${slug}-why.md`);
  if (existsSync(dest)) die(2, `draft already exists: ${dest}`);
  writeFileSync(dest, core.endsWith("\n") ? core : core + "\n");
  process.stdout.write(
    [
      `scaffolded ${dest}`,
      `  no Q-number minted (named by slug; numbered at commit)`,
    ].join("\n") + "\n",
  );
};

const cmdCompute = (flags) => {
  const root = resolve(flags.root ?? process.cwd());
  process.stdout.write(JSON.stringify(computeSources(root), null, 2) + "\n");
};

const cmdCommit = (flags) => {
  const root = resolve(flags.root ?? process.cwd());
  if (!flags.draft) die(2, "commit requires --draft <path-to-Q-draft-…-why.md>");
  const draftPath = resolve(flags.draft);
  if (!existsSync(draftPath) || !statSync(draftPath).isFile()) {
    die(2, `draft not found: ${draftPath}`);
  }
  const { next } = computeSources(root);
  const dest = join(root, `Q${next}-why.md`);
  if (existsSync(dest)) die(2, `target already exists, refusing to overwrite: ${dest}`);

  const { iso } = utcNow();
  let content = readFileSync(draftPath, "utf8");
  content = content.replace(/^Frozen:.*$/m, `Frozen: ${iso}`);
  content = content.replace(/^#\s*Q\{n\}\s*Why:/m, `# Q${next} Why:`);
  writeFileSync(dest, content);
  if (resolve(draftPath) !== resolve(dest)) rmSync(draftPath);

  const row = `| Q${next} | {near-term step, imperative} | {project link or domain} | {immediate next action or blocker} |`;
  process.stdout.write(
    [
      `committed Q${next}`,
      `  why-record: ${dest}  (renamed from ${basename(draftPath)})`,
      `  frozen:     ${iso}`,
      `  queue-row (fill the prose cells, then append to QUEUE.md):`,
      row,
    ].join("\n") + "\n",
  );
};

const main = () => {
  const [sub, ...rest] = process.argv.slice(2);
  const flags = parseFlags(rest);
  switch (sub) {
    case "scaffold":
      return cmdScaffold(flags);
    case "compute":
      return cmdCompute(flags);
    case "commit":
      return cmdCommit(flags);
    default:
      return die(2, `unknown or missing subcommand: '${sub ?? ""}'. Use scaffold | compute | commit.`);
  }
};

main();
