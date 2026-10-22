import json
import textwrap

import pytest
from conftest import ROOT, load_module

sc = load_module("skills/spec-implementation/scripts/spec_checklist.py", "spec_checklist")

SPEC = textwrap.dedent("""\
    # Rate limiter

    Some intro text.

    - this bullet is not a criterion

    ## Acceptance criteria

    - Returns 429 after 5 requests per minute
      - note: per client IP
    - [ ] Resets the counter after 60 seconds
    - [x] Keeps existing behaviour for health checks
    1. A numbered criterion that wraps
       onto a second line

    ```
    - not a criterion, inside a fence
    ```

    ## Out of scope

    - Distributed limiting
    """)


def test_extracts_only_criteria_section():
    r = sc.parse_spec(SPEC)
    assert r["title"] == "Rate limiter"
    texts = [c["text"] for c in r["criteria"]]
    assert len(texts) == 4
    assert "Distributed limiting" not in " ".join(texts)
    assert "not a criterion" not in " ".join(texts)


def test_ids_notes_and_checkbox_state():
    c = sc.parse_spec(SPEC)["criteria"]
    assert [x["id"] for x in c] == ["AC-1", "AC-2", "AC-3", "AC-4"]
    assert c[0]["notes"] == ["note: per client IP"]
    assert c[2]["declared_done"] is True
    assert c[1]["declared_done"] is False
    assert all(x["status"] == "pending" and x["evidence"] is None for x in c)


def test_wrapped_item_is_joined():
    c = sc.parse_spec(SPEC)["criteria"]
    assert c[3]["text"] == "A numbered criterion that wraps onto a second line"


def test_checkboxes_outside_criteria_section_are_found():
    r = sc.parse_spec("# T\n\n## Tasks\n\n- [ ] do a\n- plain\n")
    assert [c["text"] for c in r["criteria"]] == ["do a"]


def test_no_criteria():
    assert sc.parse_spec("# Empty\n\nJust prose.\n")["criteria"] == []


def test_cli_writes_json(tmp_path, capsys):
    spec = tmp_path / "s.md"
    spec.write_text(SPEC)
    out = tmp_path / "out.json"
    assert sc.main([str(spec), "--out", str(out)]) == 0
    data = json.loads(out.read_text())
    assert data["total"] == 4 and data["spec"] == str(spec)


def test_cli_exit_codes(tmp_path):
    empty = tmp_path / "e.md"
    empty.write_text("# nothing\n")
    assert sc.main([str(empty)]) == 2
    assert sc.main([str(tmp_path / "missing.md")]) == 1


def test_example_spec_parses():
    r = sc.parse_spec((ROOT / "skills/spec-implementation/examples/sample-spec.md").read_text())
    assert len(r["criteria"]) >= 3
