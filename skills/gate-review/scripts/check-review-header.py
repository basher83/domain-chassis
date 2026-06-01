#!/usr/bin/env -S uv run --script --quiet
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Validate a gate's machine-readable review header against its append-only review log.

The verdict is the exit code, not an agent's claim to have looked (chassis anti-pattern
AP-06, The Narrative Escape). A gate's current-state review signal lives in YAML frontmatter
(`verdict`, and the Phase-2 fields `reviewed` / `confidence` — chassis ADR-004 / ADR-005);
the `## Gate Review` section is the append-only human log. This checker enforces that the
frontmatter is internally consistent and agrees with the log's *latest* review — at
gate-review authoring (self-check) and again as a verdict input. It is the consistency guard,
distinct from gate-work's fail-closed *detector* (which reads only the frontmatter field and
does not parse the log): this checker MAY read the log, because it runs at authoring/review
time, not on the clearance safety surface.

Usage:
    check-review-header.py <gate-file.md>

    # from the workspace root:
    check-review-header.py Q61-gate.md

What it checks (all deterministic):
  1. verdict-matches-narrative (F4): the frontmatter `verdict:` agrees with the LATEST
     `Verdict:` line in the `## Gate Review` log. The append-only log may carry a superseded
     `Verdict: FAIL` above the operative `Verdict: PASS`; only the latest is the current state
     the frontmatter must match. The detector reads the frontmatter; this guard keeps the
     frontmatter honest against the log.
  2. confidence enum (H2): `confidence:` is a bare integer in 1..4. 5 is unreachable per
     gate-review's scale; a legacy `high`, an `n/5` form, or `5` is RED.
  3. verdict <-> confidence invariant (H2): `verdict: pass` iff `confidence == 4`;
     `verdict: fail` iff `confidence in {1,2,3}`. Per gate-review's confidence scale,
     confidence 4 == "minor findings only" (no blocking deficiency) and 1-2 == blocking
     deficiencies, so this binding transitively enforces gate-review's blocking-deficiency
     -> FAIL rule WITHOUT a fragile narrative scan for the words "blocking deficiency" (which
     would be the very AP-06 narrative-escape risk this header design removes). See ADR-005
     for why the blocking-deficiency clause is carried by the confidence semantics, not a
     separate text match.
  4. reviewed format (H2): `reviewed:` is a UTC-canonical Z timestamp (ADR-001) —
     `YYYY-MM-DDThh:mm:ssZ`. A bare date, a numeric `+0000`/`+00:00` offset, or any
     local-basis value is RED.

Conditional fields: `reviewed` / `confidence` are Phase-2 additions. A Phase-1-migrated gate
may carry only `verdict` in frontmatter; the enum / invariant / format checks are N/A when
their field is absent. The verdict-matches-narrative check applies whenever a frontmatter
verdict and a log verdict both exist.

Exit-code contract (tri-state):
    0  GREEN — the header is present, internally consistent, and matches the log; or N/A
               when the gate has neither a frontmatter review header nor a `## Gate Review`
               log (a not-yet-reviewed or pre-contract edge the other checks own).
    2  RED   — a drift (frontmatter verdict != latest log verdict), an unmigrated reviewed
               gate (a `## Gate Review` log exists but the frontmatter carries no verdict), a
               frontmatter pass/fail with no log to back it, a bad confidence enum, a broken
               verdict<->confidence invariant, or a non-Z reviewed value.
    Fail-closed: an unreadable or absent gate file exits non-zero and loud.
"""

import argparse
import re
import sys
from pathlib import Path

VERDICT_VALUES = {"pass", "fail", "pending"}
Z_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")


def parse_frontmatter(text):
    """Return a dict of the leading YAML frontmatter's simple `key: value` lines, or {}.

    No YAML dependency: the review header is flat `key: value` scalars. Absence of a leading
    `---\\n...\\n---` block returns {} (no frontmatter), distinct from a present-but-empty one.
    """
    m = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not m:
        return None  # no frontmatter block at all
    fields = {}
    for line in m.group(1).splitlines():
        km = re.match(r"^([A-Za-z_][\w-]*)\s*:\s*(.*)$", line)
        if km:
            fields[km.group(1).strip().lower()] = km.group(2).strip().strip("\"'")
    return fields


def gate_review_section(text):
    """Return the text of the `## Gate Review` section, or None if absent.

    Also matches the one legacy heading variant `## Gate Review History` (Q16-findings.md),
    which is a review log under a non-standard heading; the standard heading is `## Gate Review`.
    """
    m = re.search(r"^##\s+Gate Review(?:\s+History)?\s*$(.*?)(?=^##\s|\Z)", text,
                  re.MULTILINE | re.DOTALL)
    return m.group(1) if m else None


def latest_log_verdict(section_text):
    """Return the last `Verdict ...: PASS|FAIL` value in the log (lowercased), or None.

    'Latest' = last in document order, because review blocks are appended. A superseded
    first-review verdict (possibly hand-relabelled, e.g. `Verdict [first review ...]: FAIL`)
    sits above the operative one and is therefore not the value returned.
    """
    matches = re.findall(r"^Verdict\b[^:\n]*:\s*\**\s*(PASS|FAIL)\b", section_text,
                         re.MULTILINE | re.IGNORECASE)
    return matches[-1].lower() if matches else None


def main():
    ap = argparse.ArgumentParser(
        description="Validate a gate's machine-readable review header against its review log.")
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

    fm = parse_frontmatter(text)
    fm = fm if fm is not None else {}
    fm_verdict = fm.get("verdict", "").lower() or None
    fm_reviewed = fm.get("reviewed")
    fm_confidence = fm.get("confidence")

    section = gate_review_section(text)
    log_verdict = latest_log_verdict(section) if section is not None else None

    print(f"check-review-header: {gate_path}")
    print(f"frontmatter: verdict={fm_verdict!r} reviewed={fm_reviewed!r} confidence={fm_confidence!r}"
          f"  |  log latest Verdict={log_verdict!r}  review-section={'present' if section is not None else 'absent'}")
    print("-" * 72)

    red = 0

    # N/A: neither a frontmatter review header nor a review log.
    if fm_verdict is None and section is None:
        print("RESULT: N/A (exit 0) — no frontmatter review header and no `## Gate Review` log")
        return 0

    # 1) verdict-matches-narrative (F4).
    if fm_verdict is None and log_verdict is not None:
        red += 1
        print(f"[RED:unmigrated] `## Gate Review` log carries Verdict={log_verdict!r} but the "
              "frontmatter has no `verdict:` field — pre-contract gate, migrate (backfill frontmatter)")
    elif fm_verdict is not None and fm_verdict not in VERDICT_VALUES:
        red += 1
        print(f"[RED:bad-verdict] frontmatter verdict={fm_verdict!r} is not one of pass/fail/pending")
    elif fm_verdict in ("pass", "fail"):
        if log_verdict is None:
            red += 1
            print(f"[RED:no-log] frontmatter verdict={fm_verdict!r} but no `Verdict:` line in any "
                  "`## Gate Review` block backs it")
        elif fm_verdict != log_verdict:
            red += 1
            print(f"[RED:drift] frontmatter verdict={fm_verdict!r} != latest log verdict={log_verdict!r}")
        else:
            print(f"[GREEN] verdict-matches-narrative: frontmatter {fm_verdict!r} == latest log {log_verdict!r}")
    elif fm_verdict == "pending":
        if log_verdict is not None:
            red += 1
            print(f"[RED:drift] frontmatter verdict='pending' but the log already carries a "
                  f"Verdict={log_verdict!r} — stale frontmatter, set it to the review outcome")
        else:
            print("[GREEN] verdict='pending' with no log verdict — planned/unreviewed, consistent")

    # 2) confidence enum (H2) — conditional on the field being present.
    conf_int = None
    if fm_confidence is not None:
        if re.fullmatch(r"[1-4]", fm_confidence):
            conf_int = int(fm_confidence)
            print(f"[GREEN] confidence enum: {conf_int} in 1..4")
        else:
            red += 1
            print(f"[RED:bad-enum] confidence={fm_confidence!r} is not a bare integer 1..4 "
                  "(5 is unreachable; `n/5` and `high` are legacy forms)")

    # 3) verdict <-> confidence invariant (H2) — conditional on both present and valid.
    if conf_int is not None and fm_verdict in ("pass", "fail", "pending"):
        if fm_verdict == "pass" and conf_int != 4:
            red += 1
            print(f"[RED:invariant] verdict='pass' requires confidence==4, got {conf_int} "
                  "(PASS iff confidence 4 and no blocking deficiency — ADR-005)")
        elif fm_verdict == "fail" and conf_int not in (1, 2, 3):
            red += 1
            print(f"[RED:invariant] verdict='fail' requires confidence in 1..3, got {conf_int}")
        elif fm_verdict == "pending":
            red += 1
            print("[RED:invariant] verdict='pending' should carry no confidence (not yet reviewed)")
        else:
            print(f"[GREEN] invariant: verdict={fm_verdict!r} <-> confidence={conf_int} holds")

    # 4) reviewed format (H2) — conditional on the field being present.
    if fm_reviewed is not None:
        if Z_RE.fullmatch(fm_reviewed):
            print(f"[GREEN] reviewed is UTC-canonical Z: {fm_reviewed}")
        else:
            red += 1
            print(f"[RED:bad-reviewed] reviewed={fm_reviewed!r} is not UTC-canonical "
                  "`YYYY-MM-DDThh:mm:ssZ` (a bare date, a +0000 offset, or a local value)")

    print("-" * 72)
    if red:
        print(f"RESULT: RED (exit 2) — {red} header defect(s)")
        return 2
    print("RESULT: GREEN (exit 0) — review header consistent and matches the log")
    return 0


if __name__ == "__main__":
    sys.exit(main())
