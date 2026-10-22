# A06 Vulnerable and Outdated Components

Source: https://owasp.org/Top10/A06_2021-Vulnerable_and_Outdated_Components/ · ASVS 4.0 chapters V1 (Architecture, dependency items), V14.2 (Dependency)

Dependencies, runtimes or base images with known vulnerabilities, or that are no longer maintained.

## What to look for

- Manifests and lockfiles: `requirements.txt`, `poetry.lock`, `package-lock.json`, `pom.xml`, `go.sum`, Dockerfile base images.
- Very old pinned versions, abandoned packages, or no lockfile at all.
- Unpinned `latest`/`*` ranges that make builds non-reproducible.
- Dependencies loaded from CDNs without integrity hashes (`<script src>` with no SRI).
- Vendored copies of libraries nobody updates; unmaintained frameworks.
- No automated update or audit step in CI.

You can usually spot age and risk by reading manifests. Do not state a specific CVE unless you
checked it with an advisory source or an audit tool run in this session.

## Vulnerable vs safe

```text
# Vulnerable: ancient pins, no hashes
Flask==0.12.2
PyYAML==3.12

# Safer: current, locked and audited
Flask>=3.0,<4        # plus a lockfile (pip-tools / uv / poetry)
# CI: pip-audit -r requirements.txt   ·   npm audit --omit=dev
```

```html
<!-- Vulnerable -->
<script src="https://cdn.example.com/lib.js"></script>
<!-- Safer -->
<script src="https://cdn.example.com/lib-1.2.3.min.js" integrity="sha384-..." crossorigin="anonymous"></script>
```

## Remediation

Inventory dependencies (an SBOM helps), pin and lock them, run an audit tool in CI, enable automated
update PRs, remove unused packages, and prefer maintained libraries. Have a path to patch quickly.
