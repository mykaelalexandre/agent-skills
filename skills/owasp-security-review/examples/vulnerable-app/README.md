# Vulnerable demo app (DO NOT DEPLOY)

A tiny Flask app with intentional security flaws, written from scratch as a target for the
`owasp-security-review` skill. It is not meant to be run; reviewing the source is enough. If you do
run it, do so only in a throwaway container with no network exposure, because it ships a debug
console, command injection and unsafe deserialisation.

Expected findings: `../expected-findings.md`.
