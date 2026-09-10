# Contributing

Written for the next person or agent who continues the work. Where a rule has an executable
gate, the gate wins over this text.

## Language

Everything in the live surface is English: identifiers, docstrings, comments, messages,
documentation, changelog, commits. Test fixture payloads may use any language when language
neutrality is under test. Frozen baselines under `docs/governance/baseline/` keep the language
they were frozen in.

## Definition of done

A task is finished when:

1. its behaviour is implemented through a general abstraction, not a special case;
2. any change that crosses the public boundary is versioned (see below);
3. its failure states are honest — the `error_code` names the cause that occurred;
4. its costs and evidence are traceable through receipts;
5. it has deterministic tests proportional to its risk;
6. the whole verification chain passes, including `estatuto gate .`;
7. the normative documentation describes exactly what exists, again.

## Verification chain

```bash
uv run ruff check src tests conformance.py
uv run ruff format --check src tests conformance.py
uv run mypy
uv run pytest --cov --cov-branch --cov-report=term-missing --cov-fail-under=80
uv run python conformance.py
estatuto gate . --output work/framework-standard-gate.json
uv run pip-audit --skip-editable
uv build
uv run mkdocs build --strict
```

## Generated files

`manifest.json` and every file under `contracts/` except `contracts/peg/` are projections of
`src/__PACKAGE__/capabilities.py`. Change the declaration, then `uv run __SLUG__ render`.
`contracts/peg/` is the standard's protocol, vendored verbatim with `estatuto sync-peg .`.

## Public contracts and deprecation

A published contract's validation rules are never changed in place. If a change makes a payload
invalid that was valid before, publish a new version, freeze the old one, and list the old id in
the capability's `deprecated_input_contracts`. A deprecated element keeps working for at least
one minor release after the release that deprecates it, is listed in `CHANGELOG.md` with its
replacement and its removal version, and changes no behaviour silently in the meantime.

## Changelog gate

A change to normative content — `src/`, `contracts/`, `gates/`, `scripts/`, `manifest.json`,
`pyproject.toml`, `conformance.py`, `estatuto.toml` — records itself under `## Unreleased`.
CI runs `estatuto changelog-gate --base <ref>` and fails when the entry is missing.

## Coverage floors

Branch coverage never drops below 80. When coverage rises, raise the floor; never lower it.

## Policy belongs outside the core

The core keeps only invariants: strict contracts, explicit authority, evidence, honest states,
cost equal to receipts. Anything a deployment might want differently is an injected policy with a
named default. A new capability arrives through declarations, ports and policies, never by
branching the core on a use case.

## No clutter

No machine-specific paths in documentation. No claim in any document that is not backed by code
and a test. Test files are named after the subject they protect, never after the process that
produced them. `work/`, `dist/`, `site/` and caches are disposable; nothing there is a source of
truth.
