---
name: spec-implementation
description: Implement a written spec that has acceptance criteria by looping implement, validate, fix until checks pass, then report evidence per criterion. Use when the user hands over a spec, ticket or requirements doc and wants it built and verified, not just drafted.
---

# Spec implementation with a validation loop

Turn a written spec into working code, and prove each acceptance criterion
is met. The loop is the point: never declare success from reading your own
diff; declare it from command output.

## Inputs

- A spec file (markdown). Acceptance criteria are list items, ideally under an
  "Acceptance criteria" heading. If the spec has none, stop and propose criteria
  to the user before coding.
- A way to validate: `validate.json` / `validate.sh` in the repo root, or commands
  you discover (test runner, linter, type checker). If none exist, ask which to use
  or create a minimal `validate.json` and say so.

Scripts live in this skill's `scripts/` directory (Python 3, stdlib only).

## Procedure

1. **Parse.** `python scripts/spec_checklist.py SPEC.md --out .spec-checklist.json`.
   Read the result. Fix ambiguity by asking the user, not by guessing. Stop on exit code 2
   (no criteria found).
2. **Baseline.** Run `python scripts/run_validation.py --out .validation-0.json --iteration 0`
   before changing anything, so pre-existing failures are not blamed on you.
3. **Plan slices.** Order criteria into the smallest independently verifiable slices.
   Write the list of slices to the user in a few lines; do not start a large rewrite.
4. **Implement one slice.** Add or update a test for the criterion first when feasible,
   then the minimal code.
5. **Validate.** `python scripts/run_validation.py --iteration N --out .validation-N.json`.
6. **Read failures.** Use `failure_lines` and `output_tail` in the report. Identify the
   root cause before editing. If two iterations in a row fail the same way, change approach
   (re-read the spec, inspect assumptions) rather than repeating the same patch.
7. **Fix and repeat** from step 5. Stop when all checks are green for the current slice, then
   go to the next slice (step 4).
8. **Bound the loop.** Default maximum is 5 validation iterations per slice and 15 overall.
   On hitting the cap, stop and report what is failing, what you tried, and your hypothesis.
   Do not weaken tests, delete assertions or skip checks to get green.
9. **Final report** (format below).

## Rules

- Do not edit the spec's criteria. If a criterion is wrong or impossible, say so in the report.
- Never mark a criterion `met` without evidence: a test name, command output line, or file
  and line reference you actually observed.
- Green validation proves only what the checks cover. A criterion with no covering test is
  `unverified`, not `met`; say what manual check would settle it.
- Keep changes scoped to the spec. Note unrelated problems separately.
- Do not commit or push unless the user asked.

## Final report format

```
## Result: <all criteria met | partially met | blocked>
Validation: <summary from last run_validation.py report> (iterations used: N)

| ID | Criterion | Status | Evidence |
|----|-----------|--------|----------|
| AC-1 | ... | met / unverified / failing | tests/test_x.py::test_y passed |

### Not done / risks
- ...
```

See `references/validation-loop.md` for the report schema, stop conditions and tips for
projects without a test suite, and `examples/` for a sample spec and `validate.json`.
