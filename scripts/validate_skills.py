#!/usr/bin/env python3
"""Lint every skill under skills/: frontmatter, naming and local file references.

Stdlib only. Usage: python scripts/validate_skills.py [SKILLS_DIR]
Exit code 0 if all skills are valid, 1 otherwise.

Checks per skills/<folder>/SKILL.md:
  * file exists and starts with a '---' YAML frontmatter block
  * `name` present, lowercase-hyphen, <= 64 chars, equals the folder name
  * `description` present, 20..1024 chars, single line of plain text
  * backticked paths like `references/x.md`, `scripts/y.py`, `examples/z` exist
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
REF_RE = re.compile(r"`((?:references|scripts|examples)/[^`\s]*)`")
NAME_MAX = 64
DESC_MIN, DESC_MAX = 20, 1024


def parse_frontmatter(text: str) -> tuple[dict[str, str] | None, str]:
    """Parse a flat `key: value` frontmatter block. Returns (fields | None, error)."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, "missing frontmatter: file must start with '---'"
    fields: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            return fields, ""
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        key, sep, value = line.partition(":")
        if not sep or line[0] in " \t":
            return None, f"unsupported frontmatter line (flat 'key: value' only): {line!r}"
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        fields[key.strip()] = value
    return None, "unterminated frontmatter: no closing '---'"


def lint_skill(skill_dir: Path) -> list[str]:
    errors: list[str] = []
    md = skill_dir / "SKILL.md"
    if not md.is_file():
        return [f"{skill_dir.name}: SKILL.md not found"]
    text = md.read_text(encoding="utf-8")
    fm, err = parse_frontmatter(text)
    if fm is None:
        return [f"{skill_dir.name}: {err}"]

    name = fm.get("name", "")
    if not name:
        errors.append(f"{skill_dir.name}: frontmatter 'name' is missing")
    else:
        if not NAME_RE.match(name):
            errors.append(f"{skill_dir.name}: name {name!r} must be lowercase letters, digits and single hyphens")
        if len(name) > NAME_MAX:
            errors.append(f"{skill_dir.name}: name longer than {NAME_MAX} chars")
        if name != skill_dir.name:
            errors.append(f"{skill_dir.name}: name {name!r} does not match folder name")

    desc = fm.get("description", "")
    if not desc:
        errors.append(f"{skill_dir.name}: frontmatter 'description' is missing")
    elif len(desc) < DESC_MIN:
        errors.append(f"{skill_dir.name}: description too short ({len(desc)} < {DESC_MIN})")
    elif len(desc) > DESC_MAX:
        errors.append(f"{skill_dir.name}: description too long ({len(desc)} > {DESC_MAX})")
    if "<" in desc or ">" in desc:
        errors.append(f"{skill_dir.name}: description must not contain angle brackets")

    for ref in sorted(set(REF_RE.findall(text))):
        if not (skill_dir / ref.rstrip("/")).exists():
            errors.append(f"{skill_dir.name}: referenced path does not exist: {ref}")
    return errors


def lint_all(skills_dir: Path) -> list[str]:
    if not skills_dir.is_dir():
        return [f"skills directory not found: {skills_dir}"]
    dirs = sorted(p for p in skills_dir.iterdir() if p.is_dir() and not p.name.startswith("."))
    if not dirs:
        return [f"no skills found in {skills_dir}"]
    errors: list[str] = []
    for d in dirs:
        errors.extend(lint_skill(d))
    return errors


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    root = Path(argv[0]) if argv else Path(__file__).resolve().parent.parent / "skills"
    errors = lint_all(root)
    for e in errors:
        print(f"ERROR {e}")
    if errors:
        print(f"{len(errors)} problem(s) found")
        return 1
    count = sum(1 for p in root.iterdir() if p.is_dir() and not p.name.startswith("."))
    print(f"OK: {count} skill(s) valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
