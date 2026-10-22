# A09 Security Logging and Monitoring Failures

Source: https://owasp.org/Top10/A09_2021-Security_Logging_and_Monitoring_Failures/ · ASVS 4.0 chapter V7 (Error Handling and Logging)

Attacks go unnoticed or cannot be investigated because the right events are not recorded, are
unusable, or are never reviewed. The opposite failure also counts: logs that leak secrets.

## What to look for

- No log entries for failed logins, access-control denials, input-validation failures, privilege changes.
- Log lines containing passwords, tokens, session ids, card numbers or full request bodies.
- User input written to logs unsanitised (log forging via newlines).
- Logs only on local disk of an ephemeral host; no retention, no tamper protection.
- No alerting path or owner; no way to correlate events (request id, user id, source IP).
- Exceptions swallowed silently (`except: pass`).
- Admin actions with no audit trail.

## Vulnerable vs safe

```python
# Vulnerable: leaks the secret, records nothing about failures
logging.info("login attempt %s / %s", username, password)
try:
    do_work()
except Exception:
    pass

# Safe
logging.warning("login_failed user=%s ip=%s", sanitize(username), request.remote_addr)
try:
    do_work()
except Exception:
    logging.exception("do_work failed request_id=%s", g.request_id)
    raise
```

```js
// Vulnerable
console.log("body", req.body);          // may contain credentials
// Safe: structured, redacted
log.info({ event: "login_failed", user: redact(req.body.email), ip: req.ip, requestId: req.id });
```

## Remediation

Define security events and log them in a structured way with who/what/when/where. Redact secrets
and sanitise inputs. Ship logs to central, append-only storage, set alerts on the signals that
matter (bursts of failures, privilege changes), and test that the alerts fire.
