#!/usr/bin/env python3
"""Run configured validation commands and emit a structured pass/fail report.

Stdlib only. Usage:
    python run_validation.py [--config validate.json] [--cwd DIR] [--out report.json]
    python run_validation.py --cmd "tests=pytest -q" --cmd "lint=ruff check ."

Config sources, in priority order:
  1. --cmd NAME=COMMAND (repeatable)
  2. --config FILE (JSON: {"commands": [{"name", "cmd", "timeout"?}], "tail_chars"?})
  3. ./validate.json
  4. ./validate.sh (run as a single command named "validate.sh")

Exit codes: 0 all passed, 1 at least one failed, 2 no configuration found.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from pathlib import Path

DEFAULT_TIMEOUT = 600
DEFAULT_TAIL = 4000
FAILURE_LINE = re.compile(
    r"(FAILED|ERROR|Error\b|error:|Traceback|AssertionError|assert |✗|npm ERR!)"
)


def load_commands(args: argparse.Namespace, cwd: Path) -> tuple[list[dict], int]:
    tail = DEFAULT_TAIL
    if args.cmd:
        cmds = []
        for item in args.cmd:
            name, sep, command = item.partition("=")
            if not sep or not name or not command:
                raise ValueError(f"--cmd must look like NAME=COMMAND, got: {item!r}")
            cmds.append({"name": name.strip(), "cmd": command.strip()})
        return cmds, tail
    config = Path(args.config) if args.config else cwd / "validate.json"
    if config.is_file():
        data = json.loads(config.read_text(encoding="utf-8"))
        cmds = data.get("commands", [])
        for c in cmds:
            if "name" not in c or "cmd" not in c:
                raise ValueError("each command needs 'name' and 'cmd'")
        return cmds, int(data.get("tail_chars", tail))
    if args.config:
        raise FileNotFoundError(f"config not found: {config}")
    script = cwd / "validate.sh"
    if script.is_file():
        return [{"name": "validate.sh", "cmd": "bash validate.sh"}], tail
    return [], tail


def run_one(spec: dict, cwd: Path, tail: int) -> dict:
    timeout = spec.get("timeout", DEFAULT_TIMEOUT)
    start = time.monotonic()
    timed_out = False
    try:
        proc = subprocess.run(
            spec["cmd"], shell=True, cwd=cwd, capture_output=True, text=True,
            timeout=timeout, errors="replace",
        )
        code, out = proc.returncode, (proc.stdout or "") + (proc.stderr or "")
    except subprocess.TimeoutExpired as exc:
        timed_out, code = True, 124
        def _s(v):
            return v.decode("utf-8", "replace") if isinstance(v, bytes) else (v or "")
        out = _s(exc.stdout) + _s(exc.stderr)
    failures = [ln.strip() for ln in out.splitlines() if FAILURE_LINE.search(ln)][:20]
    return {
        "name": spec["name"],
        "cmd": spec["cmd"],
        "exit_code": code,
        "passed": code == 0,
        "timed_out": timed_out,
        "duration_s": round(time.monotonic() - start, 3),
        "failure_lines": [] if code == 0 else failures,
        "output_tail": out[-tail:],
    }


def build_report(results: list[dict], iteration: int | None) -> dict:
    failed = [r["name"] for r in results if not r["passed"]]
    return {
        "iteration": iteration,
        "passed": not failed,
        "summary": f"{len(results) - len(failed)}/{len(results)} checks passed",
        "failed": failed,
        "results": results,
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--config")
    ap.add_argument("--cmd", action="append", help="NAME=COMMAND (repeatable)")
    ap.add_argument("--cwd", default=".")
    ap.add_argument("--out", help="write the JSON report to this file as well")
    ap.add_argument("--iteration", type=int, help="loop iteration number, echoed in the report")
    ap.add_argument("--fail-fast", action="store_true", help="stop after the first failing command")
    args = ap.parse_args(argv)

    cwd = Path(args.cwd).resolve()
    try:
        cmds, tail = load_commands(args, cwd)
    except (ValueError, FileNotFoundError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    if not cmds:
        print("error: no validation commands configured (validate.json, validate.sh or --cmd)",
              file=sys.stderr)
        return 2

    results = []
    for spec in cmds:
        res = run_one(spec, cwd, tail)
        results.append(res)
        if args.fail_fast and not res["passed"]:
            break
    report = build_report(results, args.iteration)
    payload = json.dumps(report, indent=2, ensure_ascii=False)
    if args.out:
        Path(args.out).write_text(payload + "\n", encoding="utf-8")
    print(payload)
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
