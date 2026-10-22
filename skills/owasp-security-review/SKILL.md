---
name: owasp-security-review
description: Review code or a diff for security weaknesses using the OWASP Top 10 (2021) and ASVS chapters as a checklist, and report evidenced findings with severity and fixes. Use when the user asks for a security review, audit, threat check or "is this safe" on application code, an API or a pull request.
---

# OWASP security review

A structured, evidence-first review. Output is a list of findings a developer can act on, not a
generic lecture. Reference checklists are in `references/`, one file per category.

## Scope first

1. Confirm what is in scope: a directory, a diff, one feature. Ask if unclear. Note the stack
   (language, framework, datastore, auth mechanism) and where untrusted input enters
   (routes, queue consumers, file uploads, CLI args, webhooks).
2. Only review code you can read. Do not run exploits against live systems, and do not run the
   application unless the user asks and the environment is isolated.

## Procedure

1. **Map the surface.** List entry points, auth boundaries, data stores, outbound calls, secrets
   handling and dependency manifests. Keep it short.
2. **Walk the categories in order, A01 to A10.** For each, open the matching file in `references/`
   and apply its "What to look for" list to the in-scope code. Use search (grep) for the sink
   patterns listed there, then read the surrounding code to see whether input really reaches them.
3. **Confirm before reporting.** A pattern match is a lead, not a finding. Trace the data flow from
   source to sink, check for validation or framework protection upstream, and decide:
   `confirmed`, `likely` (needs runtime or config you cannot see) or `discarded`.
4. **Rate severity** using impact times exploitability for this app: Critical, High, Medium, Low,
   Info. Say why in one clause.
5. **Propose the fix** as a concrete change (a code snippet or config line), using the safe
   pattern from the reference file adapted to the project's stack.
6. **Report** in the format below. Finish with categories that had no findings, and the things you
   could not assess (deployment config, secrets in CI, infrastructure).

## Rules

- Every finding needs a file path and line, a short evidence quote, and an explanation of how an
  attacker reaches it. No finding without evidence.
- Do not invent CVE ids or version vulnerabilities. For dependencies, report age and missing
  lockfiles from what you can read, and recommend running an audit tool (`pip-audit`, `npm audit`).
- Never paste real secrets into the report; show the first and last two characters only.
- Prefer few, real findings over many speculative ones, but list speculative ones under "Needs
  verification" when the risk would be high.
- Do not modify code unless the user asks for fixes. If asked, fix one finding at a time and keep
  tests passing.
- This is a review aid, not a certification. Say that it does not replace testing or a human
  security review for high-risk systems.

## Report format

```
# Security review: <scope>
Stack: ... · Reviewed: <files/dirs> · Method: manual code review against OWASP Top 10 (2021)

## Summary
<2-3 sentences; counts by severity>

## Findings
### [SEVERITY] A03 SQL injection in /search  (confirmed)
- Where: app.py:59
- Evidence: `db.execute(f"... LIKE '%{q}%'")`
- Impact: attacker-controlled SQL; can read or modify any table.
- Fix: bind the parameter: `db.execute("... LIKE ?", (f"%{q}%",))`

## Needs verification
## Categories with no findings
## Not assessed
```

## Category index

| Id | Category | Reference |
|----|----------|-----------|
| A01 | Broken Access Control | `references/A01-broken-access-control.md` |
| A02 | Cryptographic Failures | `references/A02-cryptographic-failures.md` |
| A03 | Injection | `references/A03-injection.md` |
| A04 | Insecure Design | `references/A04-insecure-design.md` |
| A05 | Security Misconfiguration | `references/A05-security-misconfiguration.md` |
| A06 | Vulnerable and Outdated Components | `references/A06-vulnerable-outdated-components.md` |
| A07 | Identification and Authentication Failures | `references/A07-identification-authentication-failures.md` |
| A08 | Software and Data Integrity Failures | `references/A08-software-data-integrity-failures.md` |
| A09 | Security Logging and Monitoring Failures | `references/A09-logging-monitoring-failures.md` |
| A10 | Server-Side Request Forgery | `references/A10-server-side-request-forgery.md` |

Sources: https://owasp.org/Top10/ and https://owasp.org/www-project-application-security-verification-standard/.
The reference files are my own summaries, not OWASP text; read the originals for authoritative detail.

A worked target is in `examples/vulnerable-app/` (never deploy it) with the answer key in
`examples/expected-findings.md`.
