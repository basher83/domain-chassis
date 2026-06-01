#!/usr/bin/env -S uv run --script --quiet
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Verify a gate's predecessor-gate inheritance and return a verdict as an exit code.

A gate that declares `Builds on: <predecessor>` must carry a matching
`## Inherited from <predecessor>` section transcribing the load-bearing fraction the
successor reuses, so a cold gate-work executor reaches it from the single file it loads.
The verdict is the exit code, not an agent's claim to have looked (chassis anti-pattern
AP-06, The Narrative Escape). Section *presence and predecessor-name match* is checked here
structurally — at gate-plan authoring (self-check) and again at gate-review (verdict input).

Usage:
    check-inheritance.py <gate-file.md>

    # authoring / review self-check, run from the workspace root:
    check-inheritance.py Q71-gate.md

When to use:
    Run against any gate during gate-plan (pre-submission self-check) and gate-review
    (verdict input). A RED exit is a blocking deficiency. The `Builds on:` field is distinct
    from `Depends on:`: it names a predecessor whose runtime/fixtures/contracts/baselines this
    gate REUSES (Q70 builds on the cleared Q66 while its `Depends on:` reads "None").

When NOT to use:
    Not a general markdown linter, and not a judge of transcription completeness or
    correctness. It decides one thing deterministically: does every predecessor named in
    `Builds on:` have a matching `## Inherited from <predecessor>` section present? Whether
    that section carries the RIGHT load-bearing fraction is human gate-review's judgment
    (ADR-003), surfaced there, not folded into this exit code.

Exit-code contract (tri-state):
    0  GREEN — every predecessor named in `Builds on:` has a matching `## Inherited from
               <predecessor>` section; or N/A when the gate declares no inheritance
               (`Builds on:` field absent, or `Builds on: None`).
    2  RED   — a declared `Builds on: <predecessor>` with no matching `## Inherited from
               <predecessor>` section, or a `Builds on:` field present but unparseable
               (non-None yet naming no Q-numbered predecessor).
    Fail-closed: an unreadable/absent gate file, or a malformed `Builds on:` field, exits
    non-zero and loud — never a silent GREEN.
"""

import argparse
import re
import sys
from pathlib import Path

# A predecessor reference is a Q-number token (Q66, Q58, ...).
PRED_RE = re.compile(r"\bQ\d{1,4}\b")


def split_preamble(text):
    """Return the gate's preamble — the text before the first '## ' heading.

    The `Builds on:` field lives in the header block (alongside `Depends on:`), before any
    `## ` section. Scanning only the preamble for the field avoids matching the many prose
    and code-block mentions of "Builds on:" that a gate about this convention legitimately
    carries lower down.
    """
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if re.match(r"^##\s", line):
            return "\n".join(lines[:i])
    return text


def find_builds_on(preamble):
    """Return the raw value of the `Builds on:` field line in the preamble, or None if absent."""
    for line in preamble.splitlines():
        m = re.match(r"^\s*Builds on\s*:\s*(.*)$", line)
        if m:
            return m.group(1).strip()
    return None


def inherited_section_tokens(text):
    """Set of predecessor Q-tokens named across all '## Inherited from ...' headings."""
    tokens = set()
    for m in re.finditer(r"^##\s+Inherited from\s+(.*)$", text, re.MULTILINE):
        tokens.update(PRED_RE.findall(m.group(1)))
    return tokens


def main():
    ap = argparse.ArgumentParser(
        description="Verify a gate's Builds-on / Inherited-from predecessor inheritance.")
    ap.add_argument("gate", help="path to the gate markdown file")
    args = ap.parse_args()

    gate_path = Path(args.gate)
    if not gate_path.exists():
        print(f"ERROR: gate file not found: {gate_path}", file=sys.stderr)
        return 2
    try:
        text = gate_path.read_text(encoding="utf-8")
    except OSError as e:
        print(f"ERROR: cannot read gate file {gate_path}: {e}", file=sys.stderr)
        return 2

    builds_on = find_builds_on(split_preamble(text))
    print(f"check-inheritance: {gate_path}")

    # N/A: no `Builds on:` field at all.
    if builds_on is None:
        print("RESULT: N/A (exit 0) — no `Builds on:` field; gate declares no predecessor inheritance")
        return 0

    predecessors = list(dict.fromkeys(PRED_RE.findall(builds_on)))  # ordered, deduped
    bo_norm = builds_on.strip().strip("`*_.").strip().lower()

    if not predecessors:
        if bo_norm in ("", "none"):
            print("RESULT: N/A (exit 0) — `Builds on: None`; gate declares no predecessor inheritance")
            return 0
        # present, non-None, but names no Q-numbered predecessor -> fail closed.
        print(f"RESULT: RED (exit 2) — `Builds on: {builds_on}` is non-None but names no "
              "Q-numbered predecessor (unparseable / fail-closed)")
        return 2

    section_tokens = inherited_section_tokens(text)
    print(f"declared `Builds on:` = {predecessors}  |  `## Inherited from` sections name = "
          f"{sorted(section_tokens) if section_tokens else '[]'}")
    print("-" * 72)

    missing = []
    for p in predecessors:
        if p in section_tokens:
            print(f"[GREEN] {p}: matching `## Inherited from … {p} …` section present")
        else:
            missing.append(p)
            print(f"[RED:missing-section] {p} declared in `Builds on:` but no matching "
                  f"`## Inherited from {p}` section")
    print("-" * 72)

    if missing:
        print(f"RESULT: RED (exit 2) — {len(missing)} declared predecessor(s) without an "
              f"`Inherited from` section: {missing}")
        return 2
    print("RESULT: GREEN (exit 0) — every `Builds on:` predecessor has a matching "
          "`Inherited from` section")
    return 0


if __name__ == "__main__":
    sys.exit(main())
