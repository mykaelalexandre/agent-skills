# Roadmap

Small, independent increments, each sized for roughly an hour. Pick the first unchecked item,
keep `python scripts/validate_skills.py` and `python -m pytest` green, and tick the box in the same change.

- [ ] **Third skill: `test-driven-bugfix`.** `SKILL.md` for reproducing a bug with a failing test
  first, then the minimal fix; reuse `run_validation.py` by reference. Must pass the linter.
- [ ] **Markdown report renderer.** Add `skills/spec-implementation/scripts/render_report.py`
  that turns the checklist JSON plus the last validation report into the final-report table, with tests.
- [ ] **Checklist status updater.** `spec_checklist.py --set AC-2=met --evidence "..."` (or a small
  sibling script) to update a checklist file in place, with tests for bad ids.
- [ ] **Frontmatter checks.** Extend `validate_skills.py`: warn when the description lacks a
  "Use when" clause, reject duplicate names across skills, report `SKILL.md` line count over 500. Add tests.
- [ ] **Coverage for criteria shapes.** More `spec_checklist.py` parser tests and handling for
  Given/When/Then blocks and tables of criteria; document the supported shapes in the reference file.
- [ ] **JS/Express vulnerable example.** Add `examples/vulnerable-express/` (labelled, never deploy)
  covering A01, A03, A07 and A10, with its own section in `expected-findings.md` and a drift test.
- [ ] **OWASP references: ASVS map.** Add `references/asvs-map.md` listing ASVS 4.0 chapters with
  the A-categories they support and which checklist file to open; link it from `SKILL.md`.
- [ ] **Safe-version example.** Add `examples/fixed-app/app.py`, a remediated counterpart for five
  of the findings, plus a test that the vulnerable needles are absent from it.
- [ ] **Docs: worked session.** Run the spec skill by hand on `examples/sample-spec.md` in a scratch
  directory and record the real commands and outputs in `docs/walkthrough.md` (only observed output).
- [ ] **Repo hygiene.** Add `CONTRIBUTING.md` (how to add a skill, naming rules, what the linter enforces)
  and a pull request template with the two commands that must pass.
