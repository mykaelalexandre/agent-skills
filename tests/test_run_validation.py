import json
import sys

from conftest import load_module

rv = load_module("skills/spec-implementation/scripts/run_validation.py", "run_validation")
PY = f'"{sys.executable}"'


def test_all_pass(tmp_path, capsys):
    code = rv.main(["--cwd", str(tmp_path), "--cmd", f"ok={PY} -c \"print('hi')\""])
    rep = json.loads(capsys.readouterr().out)
    assert code == 0 and rep["passed"] is True
    assert rep["results"][0]["output_tail"].strip() == "hi"
    assert rep["summary"] == "1/1 checks passed"


def test_failure_is_reported_with_lines(tmp_path, capsys):
    cmd = f"bad={PY} -c \"raise AssertionError('boom')\""
    code = rv.main(["--cwd", str(tmp_path), "--cmd", cmd, "--iteration", "3"])
    rep = json.loads(capsys.readouterr().out)
    assert code == 1 and rep["failed"] == ["bad"] and rep["iteration"] == 3
    r = rep["results"][0]
    assert r["exit_code"] == 1
    assert any("AssertionError" in ln for ln in r["failure_lines"])


def test_json_config_and_fail_fast(tmp_path, capsys):
    cfg = {"commands": [
        {"name": "first", "cmd": f"{PY} -c \"import sys; sys.exit(3)\""},
        {"name": "second", "cmd": f"{PY} -c \"print(1)\""},
    ]}
    (tmp_path / "validate.json").write_text(json.dumps(cfg))
    code = rv.main(["--cwd", str(tmp_path), "--fail-fast"])
    rep = json.loads(capsys.readouterr().out)
    assert code == 1
    assert [r["name"] for r in rep["results"]] == ["first"]
    assert rep["results"][0]["exit_code"] == 3


def test_runs_in_cwd_and_runs_all_without_fail_fast(tmp_path, capsys):
    (tmp_path / "marker.txt").write_text("x")
    cfg = {"commands": [
        {"name": "a", "cmd": f"{PY} -c \"import os; assert os.path.exists('marker.txt')\""},
        {"name": "b", "cmd": f"{PY} -c \"import sys; sys.exit(1)\""},
    ]}
    (tmp_path / "validate.json").write_text(json.dumps(cfg))
    rv.main(["--cwd", str(tmp_path)])
    rep = json.loads(capsys.readouterr().out)
    assert [r["passed"] for r in rep["results"]] == [True, False]


def test_timeout(tmp_path, capsys):
    cfg = {"commands": [{"name": "slow", "timeout": 1,
                         "cmd": f"{PY} -c \"import time; time.sleep(30)\""}]}
    (tmp_path / "validate.json").write_text(json.dumps(cfg))
    code = rv.main(["--cwd", str(tmp_path)])
    rep = json.loads(capsys.readouterr().out)
    assert code == 1 and rep["results"][0]["timed_out"] is True


def test_validate_sh_fallback(tmp_path, capsys):
    (tmp_path / "validate.sh").write_text("echo from-script\n")
    assert rv.main(["--cwd", str(tmp_path)]) == 0
    rep = json.loads(capsys.readouterr().out)
    assert rep["results"][0]["name"] == "validate.sh"


def test_no_config_and_bad_cmd(tmp_path):
    assert rv.main(["--cwd", str(tmp_path)]) == 2
    assert rv.main(["--cwd", str(tmp_path), "--cmd", "nonsense"]) == 2


def test_out_file_and_tail_truncation(tmp_path, capsys):
    cfg = {"tail_chars": 10, "commands": [{"name": "big", "cmd": f"{PY} -c \"print('a'*500)\""}]}
    (tmp_path / "validate.json").write_text(json.dumps(cfg))
    out = tmp_path / "r.json"
    rv.main(["--cwd", str(tmp_path), "--out", str(out)])
    data = json.loads(out.read_text())
    assert len(data["results"][0]["output_tail"]) <= 10
