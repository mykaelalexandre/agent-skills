# A01 Broken Access Control

Source: https://owasp.org/Top10/A01_2021-Broken_Access_Control/ · ASVS 4.0 chapters V4 (Access Control), V13 (API)

Users can act outside their intended permissions: reading other people's records, calling admin
functions, or changing objects they do not own.

## What to look for

- Handlers that load an object by a client-supplied id with no owner/tenant check (IDOR).
- Admin or internal routes with no role check, or checks only in the UI.
- Authorization done by hiding links, or by trusting a client field (`role`, `isAdmin`, `user_id`).
- Missing checks on non-GET verbs, bulk endpoints, exports, file download paths and GraphQL resolvers.
- Mass assignment: request body copied straight onto a model (`User(**data)`).
- CORS with `*` plus credentials, or reflected origins. CSRF on cookie-authenticated state changes.
- Path traversal on user-supplied file names (`../`).
- Authorization implemented per-route by copy-paste instead of one enforced layer.

## Vulnerable vs safe

```python
# Vulnerable: any logged-in user can read any invoice by changing the id
@app.get("/invoice/<int:invoice_id>")
@login_required
def invoice(invoice_id):
    return jsonify(db.get_invoice(invoice_id))

# Safe: scope the query to the caller; unknown and forbidden look the same
@app.get("/invoice/<int:invoice_id>")
@login_required
def invoice(invoice_id):
    inv = db.get_invoice(invoice_id, owner_id=current_user.id)
    if inv is None:
        abort(404)
    return jsonify(inv)
```

```js
// Vulnerable: mass assignment lets the caller set isAdmin
app.post("/signup", async (req, res) => res.json(await User.create(req.body)));

// Safe: allow-list the fields
const { email, name, password } = req.body;
res.json(await User.create({ email, name, password: await hash(password) }));
```

## Remediation

Deny by default; enforce authorization server-side in one central place (middleware, policy
objects). Check ownership on every object access, derive identity from the session, never from
the request. Allow-list writable fields. Normalise and confine file paths. Add tests that call
each endpoint as another user and as anonymous.
