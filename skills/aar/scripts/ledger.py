#!/usr/bin/env -S uv run --script --quiet
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Project per-gate AAR attribution tables into a cross-gate ledger, and surface prune candidates.

This is the derived-projection half of the gate-verdict measurement loop (see
`../references/attribution-ledger.md`). The per-gate **attribution table** lives in each
AAR's interpretation artifact (the source of truth); this script *derives* a cross-gate
**snapshot** from those tables and *reviews* the snapshot for requirements whose inert
streak licenses a prune candidacy. The snapshot is never hand-edited — regenerate it and it
is correct by construction, so the ledger cannot drift from its source (chassis anti-pattern
AP-12, The Doctrinal Echo: a hand-maintained accumulator is where single observations harden
into false authority).

Usage:
    # derive a committed, timestamped snapshot from a domain's AARs:
    ledger.py derive workshop-polish/aar/ --scope workshop --out workshop-polish/aar/ledger-2026-06-02.tsv

    # surface prune candidates from the latest snapshot:
    ledger.py prune-review workshop-polish/aar/ledger-2026-06-02.tsv --threshold 5

When to use:
    `derive` after a gate-closure AAR adds an attribution block, to refresh the projection.
    `prune-review` at an operator-run pruning pass, to see which requirements have been inert
    long enough to be prune candidates. The prune *decision* is the operator's — this only
    surfaces candidates; it never edits the bar.

When NOT to use:
    Not a judge of whether an attribution is correct (that is the AAR author's locus-anchored
    judgment) and not an evidence artifact. `derive` only transcribes + sorts; `prune-review`
    only counts streaks. Neither classifies a requirement — they read what the AARs recorded.

Exit-code contract:
    0  OK — derive emitted a snapshot, or prune-review ran (candidates or none is still a
            clean run; the report is on stdout, not the exit code).
    2  a malformed attribution table (bad classification, wrong column count) or an unreadable
       / malformed snapshot. Fail-closed and loud — never a silent empty projection.
"""

import argparse
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

CLASSIFICATIONS = {"load-bearing", "inert", "absent-but-needed", "indeterminate"}
COLUMNS = ["requirement_key", "gate_id", "gate_date", "classification", "locus"]
BEGIN_RE = re.compile(
    r"<!--\s*ledger:begin\s+gate=(?P<gate>Q\d{1,4})\s+date=(?P<date>\d{4}-\d{2}-\d{2})\s*-->"
)
END_MARK = "<!-- ledger:end -->"


def _clean(cell):
    """Collapse tabs/newlines in a field so a row stays one TSV line."""
    return re.sub(r"\s+", " ", cell.strip())


def _parse_table(block, gate, date, src, errors):
    """Yield (requirement_key, gate_id, gate_date, classification, locus) rows from one block."""
    rows = []
    for line in block.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if cells and cells[0] == "requirement_key":
            continue  # header row
        if all(set(c) <= {"-", ":", " "} for c in cells):
            continue  # separator row
        if len(cells) != 5:
            errors.append(f"{src} [{gate}]: expected 5 columns, got {len(cells)}: {line}")
            continue
        key, requirement, source, classification, locus = cells
        if classification not in CLASSIFICATIONS:
            errors.append(f"{src} [{gate}]: unknown classification '{classification}' for {key}")
            continue
        if classification != "indeterminate" and locus in ("", "—", "-"):
            errors.append(f"{src} [{gate}]: '{classification}' for {key} needs a locus anchor")
            continue
        rows.append((key, gate, date, classification, _clean(locus)))
    return rows


def _extract(paths, errors):
    """Walk AAR markdown files and extract every ledger block's rows."""
    files = []
    for p in paths:
        path = Path(p)
        if path.is_dir():
            files.extend(sorted(path.glob("*.md")))
        elif path.is_file():
            files.append(path)
        else:
            errors.append(f"not found: {p}")
    rows, gates = [], set()
    for f in files:
        text = f.read_text(encoding="utf-8")
        pos = 0
        while True:
            m = BEGIN_RE.search(text, pos)
            if not m:
                break
            end = text.find(END_MARK, m.end())
            if end == -1:
                errors.append(f"{f}: ledger:begin for {m.group('gate')} has no ledger:end")
                break
            block = text[m.end():end]
            gate, date = m.group("gate"), m.group("date")
            gates.add(gate)
            rows.extend(_parse_table(block, gate, date, f.name, errors))
            pos = end + len(END_MARK)
    return rows, gates


def cmd_derive(args):
    errors = []
    rows, gates = _extract(args.paths, errors)
    if errors:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        return 2
    rows.sort(key=lambda r: (r[0], r[2], r[1]))  # key, date, gate — deterministic
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    out = []
    out.append(f"# ledger-snapshot\tderived={ts}\tscope={args.scope}\tgates={len(gates)}\trows={len(rows)}")
    out.append("\t".join(COLUMNS))
    out.extend("\t".join(r) for r in rows)
    text = "\n".join(out) + "\n"
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
        print(f"derived {len(rows)} rows across {len(gates)} gates -> {args.out}", file=sys.stderr)
    else:
        sys.stdout.write(text)
    return 0


def _read_snapshot(path, errors):
    """Parse a snapshot TSV into rows of dicts, skipping '# ' header comments."""
    rows = []
    try:
        lines = Path(path).read_text(encoding="utf-8").splitlines()
    except OSError as e:
        errors.append(f"cannot read snapshot: {e}")
        return rows
    header = None
    for line in lines:
        if line.startswith("#") or not line.strip():
            continue
        cells = line.split("\t")
        if header is None:
            header = cells
            if header != COLUMNS:
                errors.append(f"snapshot header {header} != expected {COLUMNS}")
                return []
            continue
        if len(cells) != len(COLUMNS):
            errors.append(f"snapshot row has {len(cells)} cols: {line}")
            continue
        rows.append(dict(zip(COLUMNS, cells)))
    return rows


def cmd_prune_review(args):
    errors = []
    rows = _read_snapshot(args.snapshot, errors)
    if errors:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        return 2
    by_key = {}
    for r in rows:
        by_key.setdefault(r["requirement_key"], []).append(r)
    candidates = []
    for key, krows in by_key.items():
        krows.sort(key=lambda r: (r["gate_date"], r["gate_id"]))
        streak, streak_gates = 0, []
        for r in reversed(krows):  # most-recent first
            if r["classification"] == "inert":
                streak += 1
                streak_gates.append(r["gate_id"])
            else:
                break
        if streak >= args.threshold:
            candidates.append((key, streak, list(reversed(streak_gates))))
    candidates.sort(key=lambda c: (-c[1], c[0]))
    print(f"# prune-review  snapshot={args.snapshot}  threshold={args.threshold}  requirements={len(by_key)}")
    if not candidates:
        print(f"no prune candidates (no requirement inert for {args.threshold}+ consecutive gates)")
    else:
        print(f"{len(candidates)} prune candidate(s) — inert streak >= {args.threshold}:")
        for key, streak, gates in candidates:
            print(f"  {key}\tinert x{streak}\t({', '.join(gates)})")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    d = sub.add_parser("derive", help="project AAR attribution tables into a snapshot")
    d.add_argument("paths", nargs="+", help="AAR files or directories")
    d.add_argument("--scope", required=True, help="projection scope label, e.g. workshop")
    d.add_argument("--out", help="write snapshot here (default: stdout)")
    d.set_defaults(func=cmd_derive)

    p = sub.add_parser("prune-review", help="surface prune candidates from a snapshot")
    p.add_argument("snapshot", help="a snapshot TSV produced by `derive`")
    p.add_argument("--threshold", type=int, required=True, help="inert-streak length that licenses prune candidacy")
    p.set_defaults(func=cmd_prune_review)

    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
