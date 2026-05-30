#!/usr/bin/env -S uv run --script --quiet
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Resolve a gate's Decision-Token Legend against source and return a verdict as an exit code.

The verdict is the exit code, not an agent's claim to have looked (chassis anti-pattern
AP-06, The Narrative Escape). A decision-record citation whose stated identity does not
match the source record it points to is caught here structurally — at gate-plan authoring
(self-check) and again at gate-review (verdict input).

Usage:
    check-citations.py <gate-file.md> [--root <workspace-root>]

    # authoring / review self-check, run from the workspace root:
    check-citations.py Q59-gate.md
    # explicit root (e.g. checking a fixture whose pointers are workspace-root-relative):
    check-citations.py Q59-working/fixture-a.md --root /Users/me/3I/workshop

When to use:
    Run against any gate that cites decision-record tokens (`d-NNNN`, `ADR-NNNN`, or an
    equivalent external decision ID) in a `## Decision-Token Legend`. gate-plan runs it as
    a pre-submission self-check; gate-review runs it and treats the exit code as the verdict
    input. A RED exit is a blocking deficiency.

When NOT to use:
    Not a general markdown linter and not a semantic-faithfulness judge. It decides
    resolution, pointer well-formedness, legend completeness for worked examples, and gross
    title mismatch deterministically. It does NOT adjudicate whether a faithful-looking
    paraphrase of a record that does exist and is on-topic is semantically faithful — that
    is not deterministic. Such cases are surfaced as a printed WARN for operator judgment,
    not folded into the exit-code verdict.

Exit-code contract (tri-state):
    0  GREEN   — every cited legend entry resolves to a real record in a present corpus and
                 the stated title covers the source title (see FLOOR); or N/A when the gate
                 cites no decision-record tokens at all. WARNs may be printed but do not
                 change the exit code.
    2  RED     — a citation defect: a worked-example token missing from the legend, a
                 malformed pointer, a dangling pointer (record-id absent from a present
                 corpus), or a gross title mismatch (the QF-1 class).
    3  UNRESOLVABLE — a well-formed pointer into a corpus file that is not on disk. This is
                 an environment condition, distinct from a citation defect (AP-01, The False
                 Regression): a foreign-domain corpus that simply is not checked out is not a
                 misattribution. Reported, never silently passed.
    RED takes precedence over UNRESOLVABLE when both are present (a real defect outranks an
    undeterminable one).

Title matching — the one sub-decision with a tunable boundary, pinned here so the RED/WARN
split is reproducible across runs and workers:
    Significant terms = whitespace tokens, lowercased, surrounding punctuation stripped
    (internal hyphens/dots kept, so `claude-opus-4-7` and `GPT-5.5` stay intact), stopwords
    and <2-char tokens dropped. The score is the recall of the SOURCE title's significant
    terms in the STATED title: |stated ∩ source| / |source|.
        score == 1.0          -> GREEN  (every source term is present; the legend may add
                                          context per the authority rule — context is allowed,
                                          contradiction is not)
        FLOOR < score < 1.0   -> WARN   (a paraphrase that drops source terms; surfaced,
                                          non-blocking — the irreducible residual)
        score <= FLOOR        -> RED    (gross mismatch — wrong record)
    FLOOR is a constant declared on the next line, not chosen per run.
"""

FLOOR = 0.40  # title-match RED/WARN boundary on source-term recall; constant across runs.

import argparse
import json
import os
import re
import sys
from pathlib import Path

# Tokens that stand in for a recorded decision. Anti-pattern tags ({AP-nn}) are deliberately
# NOT in this set — they resolve against the anti-pattern registry separately.
TOKEN_RE = re.compile(r"\b(d-\d{3,5}|ADR-\d{3,5})\b", re.IGNORECASE)

# Sections excluded from the worked-example completeness scan: the legend's own explanation,
# and post-authoring narrative where tokens are discussed as data, not cited as authority.
EXCLUDED_SECTIONS = {
    "decision-token legend",
    "gate review",
    "gate status",
    "gate errata",
    "notes",
}

STOPWORDS = {
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "being", "of", "to", "in",
    "on", "for", "and", "or", "not", "do", "does", "with", "as", "by", "that", "this", "it",
    "its", "at", "from", "into", "via", "per", "vs", "but", "so", "if", "then", "than",
}


def significant_terms(text):
    """Return the set of significant (lowercased, de-punctuated, non-stopword) terms in text."""
    out = set()
    for raw in text.lower().split():
        tok = re.sub(r"^[^\w]+|[^\w]+$", "", raw)  # strip surrounding punctuation only
        if len(tok) >= 2 and tok not in STOPWORDS:
            out.add(tok)
    return out


def title_score(stated, source):
    """Source-term recall of the source title in the stated title. 1.0 iff source ⊆ stated."""
    s = significant_terms(stated)
    src = significant_terms(source)
    if not src:
        return 0.0
    return len(s & src) / len(src)


def find_record_title(node, record_id):
    """Walk a loaded JSON corpus for a record whose id == record_id; return its title or None."""
    if isinstance(node, dict):
        idv = node.get("id") or node.get("decision_id")
        if isinstance(idv, str) and idv == record_id:
            for key in ("title", "decision", "summary", "statement", "name"):
                val = node.get(key)
                if isinstance(val, str) and val.strip():
                    return val
            return ""  # record exists but carries no title-like field
        for v in node.values():
            found = find_record_title(v, record_id)
            if found is not None:
                return found
    elif isinstance(node, list):
        for v in node:
            found = find_record_title(v, record_id)
            if found is not None:
                return found
    return None


def extract_md_title(path):
    """Title of a one-record-per-file markdown corpus: frontmatter title, else first H1."""
    text = path.read_text(encoding="utf-8")
    fm = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if fm:
        m = re.search(r"^title:\s*(.+)$", fm.group(1), re.MULTILINE)
        if m:
            return m.group(1).strip().strip("\"'")
    m = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
    return m.group(1).strip() if m else ""


def resolve_pointer(pointer, root):
    """Resolve a `<corpus-path>#<record-id>` pointer.

    Returns (status, detail, source_title) where status is one of
    'ok' | 'malformed' | 'unresolvable' | 'dangling'.
    """
    p = pointer.strip().strip("`").strip()
    if not p:
        return ("malformed", "empty pointer", None)
    if p.startswith("#"):
        return ("malformed", f"no corpus path before '#': {pointer!r}", None)
    if p.endswith("#"):
        return ("malformed", f"empty record-id after '#': {pointer!r}", None)
    path_part, _, record_id = p.partition("#")
    if not path_part or " " in path_part:
        return ("malformed", f"not a <corpus-path>#<record-id> pointer: {pointer!r}", None)
    fpath = root / path_part
    if not fpath.exists():
        return ("unresolvable", f"corpus not on disk: {path_part}", None)
    if fpath.suffix == ".json":
        try:
            data = json.loads(fpath.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as e:
            return ("dangling", f"corpus unreadable as JSON ({path_part}): {e}", None)
        if not record_id:
            return ("malformed", f"JSON corpus needs a #<record-id>: {pointer!r}", None)
        title = find_record_title(data, record_id)
        if title is None:
            return ("dangling", f"record-id {record_id!r} not found in {path_part}", None)
        return ("ok", "", title)
    # one-record-per-file corpus (e.g. an ADR markdown file): the file is the record.
    return ("ok", "", extract_md_title(fpath))


def parse_legend(text):
    """Parse the `## Decision-Token Legend` markdown table into [(token, stated_title, pointer)]."""
    m = re.search(r"^##\s+Decision-Token Legend\s*$(.*?)(?=^##\s|\Z)", text,
                  re.MULTILINE | re.DOTALL)
    if not m:
        return []
    rows = []
    for line in m.group(1).splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 3:
            continue
        if re.fullmatch(r"[\s:|-]+", line):  # separator row |---|---|
            continue
        token = cells[0].strip().strip("`").strip()
        if not TOKEN_RE.fullmatch(token):  # skips the header row (e.g. "Token")
            continue
        rows.append((token, cells[1], cells[-1]))
    return rows


def fenced_example_tokens(text):
    """Decision-record tokens inside fenced code blocks, excluding non-authoring sections.

    These are the gate's worked examples; a token cited in one must be in the legend. Analytical
    prose is intentionally NOT scanned — a gate may legitimately discuss tokens as data (this one
    does), and flagging that would be over-enforcement.
    """
    # Drop excluded sections wholesale before scanning.
    kept, current = [], None
    for line in text.splitlines():
        h = re.match(r"^##\s+(.*?)\s*$", line)
        if h:
            current = h.group(1).strip().lower()
        if current in EXCLUDED_SECTIONS:
            continue
        kept.append(line)
    body = "\n".join(kept)
    found = {}
    for block in re.findall(r"```.*?\n(.*?)```", body, re.DOTALL):
        for tok in TOKEN_RE.findall(block):
            found.setdefault(tok.lower() if tok.lower().startswith("d-") else tok, tok)
    return list(found.values())


def main():
    ap = argparse.ArgumentParser(description="Verify a gate's Decision-Token Legend against source.")
    ap.add_argument("gate", help="path to the gate markdown file")
    ap.add_argument("--root", default=os.getcwd(),
                    help="workspace root that legend pointers resolve against (default: cwd)")
    args = ap.parse_args()

    gate_path = Path(args.gate)
    root = Path(args.root)
    if not gate_path.exists():
        print(f"ERROR: gate file not found: {gate_path}", file=sys.stderr)
        return 2
    text = gate_path.read_text(encoding="utf-8")

    legend = parse_legend(text)
    legend_tokens = {t for (t, _, _) in legend}
    example_tokens = fenced_example_tokens(text)

    print(f"check-citations: {gate_path}  (root={root})")
    print(f"floor={FLOOR}  legend-entries={len(legend)}  fenced-example-tokens={len(example_tokens)}")
    print("-" * 72)

    red = unresolvable = warn = 0

    # 1) Worked-example completeness: a fenced-example token with no legend entry is RED.
    for tok in example_tokens:
        if tok not in legend_tokens:
            red += 1
            print(f"[RED:missing-entry] {tok} cited in a fenced worked example, no legend row")

    # 2) Resolve every legend entry against source.
    for token, stated, pointer in legend:
        status, detail, source_title = resolve_pointer(pointer, root)
        if status == "malformed":
            red += 1
            print(f"[RED:malformed-pointer] {token} {detail}")
        elif status == "unresolvable":
            unresolvable += 1
            print(f"[UNRESOLVABLE] {token} {detail}")
        elif status == "dangling":
            red += 1
            print(f"[RED:dangling] {token} {detail}")
        else:  # ok — compare titles
            score = title_score(stated, source_title)
            if score <= FLOOR:
                red += 1
                print(f"[RED:title-mismatch] {token} score={score:.2f} (<= floor {FLOOR})")
                print(f'    stated   = "{stated[:120]}"')
                print(f'    resolved = "{source_title[:120]}"')
            elif score < 1.0:
                warn += 1
                print(f"[WARN:paraphrase] {token} score={score:.2f} — surfaced for operator")
                print(f'    stated   = "{stated[:120]}"')
                print(f'    resolved = "{source_title[:120]}"')
            else:
                print(f'[GREEN] {token} -> "{source_title[:90]}"  (score=1.00)')

    print("-" * 72)
    if red:
        print(f"RESULT: RED (exit 2) — {red} citation defect(s)"
              + (f", {unresolvable} unresolvable" if unresolvable else "")
              + (f", {warn} warn" if warn else ""))
        return 2
    if unresolvable:
        print(f"RESULT: UNRESOLVABLE (exit 3) — {unresolvable} pointer(s) unverifiable in this environment")
        return 3
    if not legend and not example_tokens:
        print("RESULT: N/A (exit 0) — gate cites no decision-record tokens")
        return 0
    print(f"RESULT: GREEN (exit 0) — all entries resolve"
          + (f"; {warn} warn surfaced" if warn else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
