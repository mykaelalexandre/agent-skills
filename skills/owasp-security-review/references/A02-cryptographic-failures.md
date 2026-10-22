# A02 Cryptographic Failures

Source: https://owasp.org/Top10/A02_2021-Cryptographic_Failures/ · ASVS 4.0 chapters V6 (Stored Cryptography), V8 (Data Protection), V9 (Communication)

Sensitive data is exposed because it is unprotected, or protected with weak, misused or
hard-coded cryptography.

## What to look for

- Passwords stored plain, or hashed with MD5/SHA-1/unsalted SHA-256 instead of a slow password hash.
- Secrets, API keys, signing keys and `SECRET_KEY` committed in source or defaults.
- HTTP for anything sensitive; missing HSTS; TLS verification disabled (`verify=False`, `rejectUnauthorized: false`).
- ECB mode, static IVs/nonces, home-made encryption, `random` / `Math.random` for tokens.
- Sensitive data in URLs, logs, caches, backups or error messages.
- Old protocol/cipher settings; JWTs with `alg: none`, weak HMAC secrets or no expiry.
- Personal or payment data stored when it is not needed.

## Vulnerable vs safe

```python
# Vulnerable
import hashlib
pw_hash = hashlib.md5(password.encode()).hexdigest()
token = str(random.randint(0, 999999))

# Safe
from werkzeug.security import generate_password_hash, check_password_hash  # or argon2-cffi / bcrypt
pw_hash = generate_password_hash(password)          # salted, slow
import secrets
token = secrets.token_urlsafe(32)
```

```js
// Vulnerable
const token = Math.random().toString(36).slice(2);
https.get(url, { rejectUnauthorized: false });

// Safe
const token = crypto.randomBytes(32).toString("base64url");
https.get(url); // default verification stays on
```

## Remediation

Classify data, drop what you do not need. Use vetted libraries and high-level APIs (AEAD such as
AES-GCM or libsodium), a password hash such as argon2id/bcrypt/scrypt, CSPRNG for tokens. Load
secrets from the environment or a secret manager and rotate any that were committed. Enforce TLS
and verification everywhere.
