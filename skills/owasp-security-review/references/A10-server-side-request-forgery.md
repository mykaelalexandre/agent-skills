# A10 Server-Side Request Forgery (SSRF)

Source: https://owasp.org/Top10/A10_2021-Server-Side_Request_Forgery_%28SSRF%29/ · ASVS 4.0 chapters V5.2 (Sanitization), V12.6 (SSRF protection), V13 (API)

The server fetches a URL influenced by the user, letting an attacker reach internal services,
cloud metadata endpoints or other hosts the attacker cannot reach directly.

## What to look for

- Features that fetch a URL: link previews, webhooks, image/avatar import, PDF/HTML renderers, import-from-URL, OAuth/OIDC discovery.
- `requests.get(user_url)`, `fetch(req.query.url)`, `urllib.request.urlopen(...)` with no destination checks.
- Validation by string prefix or regex on the URL text only; redirects followed automatically.
- Access to `127.0.0.1`, private ranges (`10/8`, `172.16/12`, `192.168/16`), link-local `169.254.169.254`, `file://`, `gopher://`.
- DNS names that resolve to internal addresses, or change between check and use (rebinding).
- Responses returned verbatim to the user, which turns blind SSRF into data exfiltration.

## Vulnerable vs safe

```python
# Vulnerable
@app.get("/fetch")
def fetch():
    return requests.get(request.args["url"], timeout=5).text

# Safer: allow-list hosts, then also verify the resolved IP is public
ALLOWED = {"api.partner.example"}
u = urlparse(url)
if u.scheme != "https" or u.hostname not in ALLOWED:
    abort(400)
ip = ipaddress.ip_address(socket.gethostbyname(u.hostname))
if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
    abort(400)
requests.get(url, timeout=5, allow_redirects=False)
```

```js
// Vulnerable
const r = await fetch(req.query.url);
// Safer: parse, allow-list hostname, block redirects
const u = new URL(req.query.url);
if (u.protocol !== "https:" || !ALLOWED.has(u.hostname)) return res.sendStatus(400);
const r = await fetch(u, { redirect: "error" });
```

## Remediation

Prefer allow-lists of destinations over deny-lists. Resolve and validate the IP you will actually
connect to (and pin it for the request), disable redirects or re-validate each hop, restrict
schemes, put outbound requests through an egress proxy or network policy, require IMDSv2 on cloud
hosts, and do not return raw upstream responses.
