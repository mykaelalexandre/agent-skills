# A07 Identification and Authentication Failures

Source: https://owasp.org/Top10/A07_2021-Identification_and_Authentication_Failures/ · ASVS 4.0 chapters V2 (Authentication), V3 (Session Management)

Weaknesses in proving who a user is or in keeping that proof safe afterwards.

## What to look for

- Brute-force or credential stuffing possible: no throttling, lockout or MFA option.
- Weak or no password policy; passwords compared in plaintext or with `==` on hashes.
- Different messages for "unknown user" and "wrong password" (account enumeration).
- Session ids in URLs, not rotated on login (fixation), no expiry, not invalidated on logout or password change.
- Session cookies without `Secure`/`HttpOnly`/`SameSite`; self-built session schemes.
- Predictable remember-me or reset tokens; recovery flows weaker than login.
- JWT checks that skip signature, audience, issuer or expiry.
- Default accounts (`admin/admin`).

## Vulnerable vs safe

```python
# Vulnerable
row = db.execute("SELECT * FROM users WHERE name=?", (name,)).fetchone()
if row is None:
    return "No such user", 404
if row["password"] != password:
    return "Wrong password", 401
session["user"] = name

# Safe
row = get_user(name)
if not (row and check_password_hash(row["pw_hash"], password)):   # run a dummy hash if row is None
    record_failed_login(name, request.remote_addr)
    return "Invalid credentials", 401
session.clear(); session["uid"] = row["id"]                       # new session on login
```

```js
// Vulnerable: verifying nothing
const payload = jwt.decode(token);
// Safe
const payload = jwt.verify(token, key, { algorithms: ["RS256"], audience: "api", issuer: "https://id.example.com" });
```

## Remediation

Use a proven identity provider or framework auth rather than rolling your own. Hash with a slow
algorithm, add throttling and MFA, return uniform errors, rotate session ids on privilege change,
set expiry and server-side invalidation, and secure every cookie flag.
