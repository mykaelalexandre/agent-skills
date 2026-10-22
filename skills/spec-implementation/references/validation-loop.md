# Validation loop reference

## `spec_checklist.py` output

```json
{
  "spec": "SPEC.md",
  "title": "Slugify helper",
  "total": 6,
  "criteria": [
    {"id": "AC-1", "text": "...", "section": "Acceptance criteria", "line": 7,
     "declared_done": false, "status": "pending", "evidence": null, "notes": []}
  ]
}
```

Update `status` (`pending`, `met`, `unverified`, `failing`) and `evidence` in your working
copy as you go; the final report is rendered from it.

Parsing rules: list items under any heading containing "accept" or "criteri" count; task-list
checkboxes count anywhere; fenced code is ignored; indented plain bullets become `notes`.

## `run_validation.py` output

```json
{
  "iteration": 2,
  "passed": false,
  "summary": "1/2 checks passed",
  "failed": ["tests"],
  "results": [
    {"name": "tests", "cmd": "python -m pytest -q", "exit_code": 1, "passed": false,
     "timed_out": false, "duration_s": 1.2,
     "failure_lines": ["FAILED tests/test_x.py::test_y - AssertionError"],
     "output_tail": "..."}
  ]
}
```

Exit codes: `0` all passed, `1` something failed, `2` no config or bad arguments.
`failure_lines` is a heuristic grep of the output (capped at 20 lines); always read
`output_tail` before deciding on a fix.

## Config

`validate.json` at the repo root:

```json
{"commands": [{"name": "tests", "cmd": "npm test", "timeout": 300}]}
```

Or a `validate.sh` (run as one command). `--cmd NAME=COMMAND` overrides both.

## Stop conditions

- All checks green and every criterion has evidence: finish.
- Iteration cap reached: stop, report.
- Same failure twice with the same fix attempted: stop and rethink.
- Validation command is missing, hangs or needs credentials you lack: stop and ask.

## No test suite?

Propose the smallest check that can fail: a script that exercises the behaviour, a type
check, or a build. Say clearly in the report that coverage is thin.
