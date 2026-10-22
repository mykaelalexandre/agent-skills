# A05 Security Misconfiguration

Source: https://owasp.org/Top10/A05_2021-Security_Misconfiguration/ · ASVS 4.0 chapter V14 (Configuration)

Insecure defaults, incomplete hardening, or leaky settings in the app, framework, container or cloud.

## What to look for

- `debug=True`, Werkzeug debugger or stack traces reachable in production.
- Default or shipped credentials; sample apps and admin consoles left enabled.
- Binding to `0.0.0.0` without need; permissive CORS; open storage buckets; wide IAM policies.
- Missing security headers (CSP, `X-Content-Type-Options`, `Strict-Transport-Security`, frame protections) and cookies without `Secure`, `HttpOnly`, `SameSite`.
- Verbose error messages, directory listing, exposed `.git`, `.env`, backups, source maps.
- XML parsers with external entities enabled; unsafe deserialisation flags.
- Containers running as root, secrets baked into images, `latest` tags.
- Different config between environments with no review.

## Vulnerable vs safe

```python
# Vulnerable
app.config["SESSION_COOKIE_SECURE"] = False
app.run(host="0.0.0.0", debug=True)

# Safe
app.config.update(SESSION_COOKIE_SECURE=True, SESSION_COOKIE_HTTPONLY=True,
                  SESSION_COOKIE_SAMESITE="Lax")
# run behind a production server (gunicorn/uwsgi); DEBUG comes from env and defaults to off
```

```js
// Vulnerable
app.use(cors({ origin: true, credentials: true }));
app.use((err, req, res, next) => res.status(500).send(err.stack));

// Safe
app.use(helmet());
app.use(cors({ origin: ["https://app.example.com"], credentials: true }));
app.use((err, req, res, next) => { log.error(err); res.status(500).json({ error: "internal" }); });
```

## Remediation

Ship a hardened baseline, remove what is unused, make environments reproducible from code, scan
configs (IaC and container linters), and review settings on every release. Return generic errors to
clients and detailed ones to logs.
