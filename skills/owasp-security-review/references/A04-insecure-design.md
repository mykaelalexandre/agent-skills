# A04 Insecure Design

Source: https://owasp.org/Top10/A04_2021-Insecure_Design/ · ASVS 4.0 chapters V1 (Architecture), V11 (Business Logic)

The flaw is in the design, so perfect code would still be unsafe: missing controls, abusable
workflows, trust placed in the wrong party.

## What to look for

- No rate limit or lockout on login, password reset, OTP, coupon, signup or search endpoints.
- Reset or invite tokens that are guessable, reusable, never expire, or derived from user data.
- Business rules enforced only in the client (price, quantity, discount, step order).
- Race conditions on limits and balances (check then act without a transaction or lock).
- Security questions, "enumerate by response" flows, or recovery that bypasses MFA.
- No threat model for a feature that handles money, PII or privileged actions.
- Missing tenant isolation as an architecture choice rather than per-query patches.

## Vulnerable vs safe

```python
# Vulnerable: predictable, permanent reset token; no attempt limit
token = hashlib.md5(username.encode()).hexdigest()

# Safe: random, single use, short lifetime, stored hashed
raw = secrets.token_urlsafe(32)
store(user.id, sha256(raw), expires=now() + timedelta(minutes=15))
```

```js
// Vulnerable: server trusts the price sent by the browser
order.total = req.body.total;

// Safe: recompute from server-side catalogue inside a transaction
order.total = await priceFromCatalogue(req.body.items);
```

## Remediation

Threat-model features early (who is the attacker, what do they gain). Write abuse cases next to
use cases and turn them into tests. Put limits (rate, size, count) on every expensive or sensitive
operation. Keep authority on the server. Prefer secure-by-default building blocks over per-feature
fixes.
