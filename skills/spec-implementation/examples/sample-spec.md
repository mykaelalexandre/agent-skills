# Slugify helper

Add a `slugify(text)` function to `textutils.py` that turns titles into URL slugs.

## Acceptance criteria

- `slugify("Hello, World!")` returns `"hello-world"`.
- Runs of whitespace and punctuation collapse into a single hyphen.
- Leading and trailing hyphens are stripped.
- Accented Latin letters are transliterated (`"Ação"` becomes `"acao"`).
- An input with no alphanumeric characters returns an empty string.
- Unit tests cover each criterion above and `pytest` passes.

## Out of scope

- Non-Latin scripts.
