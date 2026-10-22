from conftest import ROOT, load_module

vs = load_module("scripts/validate_skills.py", "validate_skills")

GOOD = "---\nname: demo-skill\ndescription: Does a useful demo thing. Use when demonstrating.\n---\n\n# Demo\n"


def make(tmp_path, folder, content, extra=None):
    d = tmp_path / folder
    d.mkdir()
    (d / "SKILL.md").write_text(content)
    for rel in extra or []:
        p = d / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("x")
    return d


def test_valid_skill(tmp_path):
    d = make(tmp_path, "demo-skill", GOOD)
    assert vs.lint_skill(d) == []


def test_name_must_match_folder(tmp_path):
    d = make(tmp_path, "other-name", GOOD)
    assert any("does not match folder" in e for e in vs.lint_skill(d))


def test_bad_name_format(tmp_path):
    d = make(tmp_path, "Bad_Name", GOOD.replace("demo-skill", "Bad_Name"))
    assert any("lowercase" in e for e in vs.lint_skill(d))


def test_missing_frontmatter(tmp_path):
    d = make(tmp_path, "demo-skill", "# no frontmatter\n")
    assert any("missing frontmatter" in e for e in vs.lint_skill(d))


def test_unterminated_frontmatter(tmp_path):
    d = make(tmp_path, "demo-skill", "---\nname: demo-skill\n")
    assert any("unterminated" in e for e in vs.lint_skill(d))


def test_description_limits(tmp_path):
    long = GOOD.replace("Does a useful demo thing. Use when demonstrating.", "x" * 1025)
    assert any("too long" in e for e in vs.lint_skill(make(tmp_path, "demo-skill", long)))
    short = GOOD.replace("Does a useful demo thing. Use when demonstrating.", "tiny")
    d2 = tmp_path / "b"
    d2.mkdir()
    assert any("too short" in e for e in vs.lint_skill(make(d2, "demo-skill", short)))


def test_missing_fields(tmp_path):
    d = make(tmp_path, "demo-skill", "---\nfoo: bar\n---\n")
    errs = vs.lint_skill(d)
    assert any("'name' is missing" in e for e in errs)
    assert any("'description' is missing" in e for e in errs)


def test_quoted_values(tmp_path):
    content = '---\nname: "demo-skill"\ndescription: \'Quoted description that is long enough.\'\n---\n'
    assert vs.lint_skill(make(tmp_path, "demo-skill", content)) == []


def test_broken_reference(tmp_path):
    content = GOOD + "\nSee `references/missing.md` and `scripts/ok.py`.\n"
    d = make(tmp_path, "demo-skill", content, extra=["scripts/ok.py"])
    errs = vs.lint_skill(d)
    assert errs == ["demo-skill: referenced path does not exist: references/missing.md"]


def test_lint_all_and_main(tmp_path, capsys):
    root = tmp_path / "skills"
    root.mkdir()
    make(root, "demo-skill", GOOD)
    assert vs.main([str(root)]) == 0
    make(root, "broken", "nothing")
    assert vs.main([str(root)]) == 1
    assert vs.main([str(tmp_path / "nope")]) == 1


def test_repository_skills_are_valid():
    assert vs.lint_all(ROOT / "skills") == []
