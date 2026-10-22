# A08 Software and Data Integrity Failures

Source: https://owasp.org/Top10/A08_2021-Software_and_Data_Integrity_Failures/ · ASVS 4.0 chapters V10 (Malicious Code), V1 (Architecture), V5.5 (Deserialization)

Code or data is trusted without verifying where it came from or whether it was altered.

## What to look for

- Deserialising untrusted input with `pickle`, `yaml.load` (full loader), `marshal`, Java `ObjectInputStream`, PHP `unserialize`, `node-serialize`.
- Cookies or hidden fields carrying serialised or signed-by-nobody state.
- CI/CD pulling unpinned actions or scripts (`curl | sh`), unsigned artifacts, build steps with broad secrets.
- Auto-update or plugin loading without signature checks.
- Dependencies pulled from untrusted registries or confusable names (typosquats, dependency confusion).
- Third-party scripts with no integrity attributes.

## Vulnerable vs safe

```python
# Vulnerable
import pickle, base64
prefs = pickle.loads(base64.b64decode(request.cookies["prefs"]))
cfg = yaml.load(request.data)

# Safe
prefs = json.loads(request.cookies["prefs"])           # data-only format, then validate fields
cfg = yaml.safe_load(request.data)
# if state must live client-side, sign it: itsdangerous.URLSafeSerializer(secret).loads(...)
```

```yaml
# Vulnerable CI
- uses: some-org/action@main
# Safer: pin to a full commit SHA and restrict token permissions
- uses: some-org/action@<40-char-sha>
permissions: { contents: read }
```

## Remediation

Never deserialise untrusted data with object-capable formats. Use data-only formats with schema
validation, sign anything that round-trips through a client, pin and verify dependencies and CI
actions, require review for pipeline changes, and keep build credentials least-privilege.
