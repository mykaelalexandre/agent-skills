# Expected findings for `vulnerable-app`

When the skill is run against `examples/vulnerable-app/`, a good review should report at least
the findings below (severity is my own judgement for this toy app). Extra findings are fine; missing
ones are a gap in the skill or in the run. Line numbers refer to `app.py` unless stated.

| # | Cat | Where | Finding | Severity |
|---|-----|-------|---------|----------|
| 1 | A01 | L46 `invoice` | IDOR: any caller reads any invoice by id; no login or owner check | High |
| 2 | A01 | L52 `admin_users` | Admin listing has no authentication or role check | High |
| 3 | A02 | L39 | Passwords hashed with unsalted MD5 | High |
| 4 | A02 | L17 | Hard-coded, guessable Flask `secret_key` allows forging session cookies | High |
| 5 | A03 | L59 | SQL injection via f-string in `/search` | Critical |
| 6 | A03 | L65 | Template injection / XSS: user input concatenated into `render_template_string` | Critical |
| 7 | A03 | L71 | OS command injection: `shell=True` with user-controlled `host` | Critical |
| 8 | A04 | L78 | Reset token is `md5(username)`: predictable, permanent, no rate limit | High |
| 9 | A05 | L99 | `debug=True` (interactive debugger) bound to `0.0.0.0` | High |
| 10 | A06 | `requirements.txt` | Very old pinned Flask, PyYAML and requests; recommend an audit tool, no CVE claims without a lookup | Medium |
| 11 | A07 | L38 | User enumeration via distinct "No such user" / "Wrong password" responses | Low |
| 12 | A07 | L25 | Seeded `admin` account whose hash is the MD5 of a trivial password; no lockout or throttling on `/login` | High |
| 13 | A08 | L84 | `pickle.loads` on client-supplied data: remote code execution | Critical |
| 14 | A08 | L90 | `yaml.load` with the full `Loader` on request body | High |
| 15 | A09 | L35 | Plaintext password written to the log; failed logins are not logged | Medium |
| 16 | A10 | L95 | SSRF: server fetches an arbitrary user-supplied URL and returns the body | High |

Rows 1-16 cover all ten categories. The block below is machine-readable; `tests/test_examples.py`
checks that each `needle` still appears on the stated line, so edits to `app.py` cannot silently
drift out of sync with this file.

```json
[
  {"n": 1,  "cat": "A01", "file": "app.py", "line": 46, "needle": "def invoice"},
  {"n": 2,  "cat": "A01", "file": "app.py", "line": 52, "needle": "def admin_users"},
  {"n": 3,  "cat": "A02", "file": "app.py", "line": 39, "needle": "hashlib.md5(password"},
  {"n": 4,  "cat": "A02", "file": "app.py", "line": 17, "needle": "app.secret_key"},
  {"n": 5,  "cat": "A03", "file": "app.py", "line": 59, "needle": "LIKE '%{q}%'"},
  {"n": 6,  "cat": "A03", "file": "app.py", "line": 65, "needle": "render_template_string("},
  {"n": 7,  "cat": "A03", "file": "app.py", "line": 71, "needle": "shell=True"},
  {"n": 8,  "cat": "A04", "file": "app.py", "line": 78, "needle": "token = hashlib.md5(user"},
  {"n": 9,  "cat": "A05", "file": "app.py", "line": 99, "needle": "debug=True"},
  {"n": 10, "cat": "A06", "file": "requirements.txt", "line": 2, "needle": "Flask==0.12.2"},
  {"n": 11, "cat": "A07", "file": "app.py", "line": 38, "needle": "No such user"},
  {"n": 12, "cat": "A07", "file": "app.py", "line": 25, "needle": "'admin'"},
  {"n": 13, "cat": "A08", "file": "app.py", "line": 84, "needle": "pickle.loads"},
  {"n": 14, "cat": "A08", "file": "app.py", "line": 90, "needle": "yaml.load("},
  {"n": 15, "cat": "A09", "file": "app.py", "line": 35, "needle": "logging.info(\"login attempt"},
  {"n": 16, "cat": "A10", "file": "app.py", "line": 95, "needle": "requests.get(request.args"}
]
```
