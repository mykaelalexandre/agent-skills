# A03 Injection

Source: https://owasp.org/Top10/A03_2021-Injection/ · ASVS 4.0 chapter V5 (Validation, Sanitization and Encoding)

Untrusted input is interpreted as code or commands by an interpreter: SQL, OS shell, LDAP,
template engines, NoSQL operators, XPath, and the browser (cross-site scripting).

## What to look for

- SQL built with f-strings, `%`, `+` or `.format` instead of bound parameters.
- `subprocess(..., shell=True)`, `os.system`, `child_process.exec` with user data.
- `render_template_string`, `eval`, `exec`, `new Function`, `vm.runInNewContext` on user text.
- Output that bypasses auto-escaping: `|safe`, `Markup()`, `innerHTML`, `dangerouslySetInnerHTML`, `v-html`.
- NoSQL filters built from raw request bodies (`{"user": req.body.user}` where the value can be an object).
- Dynamic ORDER BY / column names taken from input.
- Header and log injection (unsanitised CR/LF).

## Vulnerable vs safe

```python
# Vulnerable
cur.execute(f"SELECT * FROM items WHERE name LIKE '%{q}%'")
subprocess.run(f"ping -c 1 {host}", shell=True)
return render_template_string("<h1>Hello " + name + "</h1>")

# Safe
cur.execute("SELECT * FROM items WHERE name LIKE ?", (f"%{q}%",))
subprocess.run(["ping", "-c", "1", host], check=False)       # plus validate host format
return render_template_string("<h1>Hello {{ name }}</h1>", name=name)
```

```js
// Vulnerable
db.query(`SELECT * FROM users WHERE email = '${email}'`);
el.innerHTML = comment;

// Safe
db.query("SELECT * FROM users WHERE email = $1", [email]);
el.textContent = comment;
```

## Remediation

Parameterised queries or an ORM used correctly; argument arrays instead of shell strings;
context-aware output encoding and auto-escaping templates; allow-list validation for anything that
must become an identifier or option; a Content-Security-Policy as defence in depth, not as the fix.
