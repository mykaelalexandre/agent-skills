#!/usr/bin/env python3
"""Parse a markdown spec into a checklist of acceptance criteria (JSON).

Stdlib only. Usage:
    python spec_checklist.py SPEC.md [--out checklist.json]

A criterion is a list item (bullet, numbered, or task-list checkbox) found:
  * under a heading containing "acceptance" or "criteria" (any level), or
  * anywhere in the file if it is a task-list checkbox ("- [ ]" / "- [x]").
Fenced code blocks are ignored. Exit code 2 if no criteria were found.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
ITEM = re.compile(r"^(\s*)(?:[-*+]|\d+[.)])\s+(?:\[(?P<box>[ xX])\]\s+)?(?P<text>\S.*)$")
FENCE = re.compile(r"^\s*(```|~~~)")
SECTION_HINT = re.compile(r"accept|criteri", re.IGNORECASE)


def parse_spec(text: str) -> dict:
    """Return {"title": str, "criteria": [...]} for the given markdown text."""
    title = ""
    section = ""
    in_criteria_section = False
    section_level = 0
    in_fence = False
    criteria: list[dict] = []
    current: dict | None = None

    for lineno, raw in enumerate(text.splitlines(), start=1):
        if FENCE.match(raw):
            in_fence = not in_fence
            continue
        if in_fence:
            continue

        h = HEADING.match(raw)
        if h:
            level, name = len(h.group(1)), h.group(2).strip()
            if level == 1 and not title:
                title = name
            if in_criteria_section and level <= section_level:
                in_criteria_section = False
            if SECTION_HINT.search(name):
                in_criteria_section, section_level = True, level
            if not in_criteria_section or level <= section_level:
                section = name
            current = None
            continue

        m = ITEM.match(raw)
        if m:
            indent = len(m.group(1).replace("\t", "    "))
            has_box = m.group("box") is not None
            # Nested plain bullets under a criterion are notes, not new criteria.
            if current is not None and indent >= 2 and not has_box:
                current["notes"].append(m.group("text").strip())
                continue
            if in_criteria_section or has_box:
                current = {
                    "id": f"AC-{len(criteria) + 1}",
                    "text": m.group("text").strip(),
                    "section": section,
                    "line": lineno,
                    "declared_done": (m.group("box") or "").lower() == "x",
                    "status": "pending",
                    "evidence": None,
                    "notes": [],
                }
                criteria.append(current)
            else:
                current = None
        elif current is not None and raw.strip() and raw.startswith((" ", "\t")):
            # Continuation line of a wrapped list item.
            current["text"] += " " + raw.strip()
        elif not raw.strip():
            continue
        else:
            current = None

    return {"title": title, "criteria": criteria}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("spec", help="path to the markdown spec")
    ap.add_argument("--out", help="write JSON here instead of stdout")
    args = ap.parse_args(argv)

    path = Path(args.spec)
    if not path.is_file():
        print(f"error: spec not found: {path}", file=sys.stderr)
        return 1
    result = parse_spec(path.read_text(encoding="utf-8"))
    result = {"spec": str(path), **result, "total": len(result["criteria"])}
    payload = json.dumps(result, indent=2, ensure_ascii=False)
    if args.out:
        Path(args.out).write_text(payload + "\n", encoding="utf-8")
    else:
        print(payload)
    if not result["criteria"]:
        print("warning: no acceptance criteria found", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
