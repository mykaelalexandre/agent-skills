"""Keep the vulnerable demo app and its answer key in sync."""
import json
import re

from conftest import ROOT

SKILL = ROOT / "skills" / "owasp-security-review"
APP_DIR = SKILL / "examples" / "vulnerable-app"
KEY = (SKILL / "examples" / "expected-findings.md").read_text(encoding="utf-8")


def load_key():
    block = re.search(r"```json\n(.*?)\n```", KEY, re.S).group(1)
    return json.loads(block)


def test_every_finding_needle_is_on_the_stated_line():
    for f in load_key():
        lines = (APP_DIR / f["file"]).read_text(encoding="utf-8").splitlines()
        assert f["needle"] in lines[f["line"] - 1], f"finding {f['n']} drifted: {f}"


def test_all_ten_categories_covered():
    assert {f["cat"] for f in load_key()} == {f"A{n:02d}" for n in range(1, 11)}


def test_reference_file_per_category():
    names = sorted(p.name[:3] for p in (SKILL / "references").glob("A*.md"))
    assert names == [f"A{n:02d}" for n in range(1, 11)]


def test_each_reference_has_required_sections():
    for p in (SKILL / "references").glob("A*.md"):
        text = p.read_text(encoding="utf-8")
        for heading in ("## What to look for", "## Vulnerable vs safe", "## Remediation"):
            assert heading in text, f"{p.name} lacks {heading}"
        assert "https://owasp.org/" in text, f"{p.name} lacks a source link"


def test_demo_app_is_labelled_and_compiles():
    src = (APP_DIR / "app.py").read_text(encoding="utf-8")
    assert "DO NOT DEPLOY" in src
    compile(src, "app.py", "exec")
    assert "DO NOT DEPLOY" in (APP_DIR / "README.md").read_text(encoding="utf-8")
