# Working rules for __NAME__

1. The normative source is `docs/governance/CHARTER.md`; the frozen design baseline lives under
   `docs/governance/baseline/` and its hashes in `BASELINE.sha256`. Neither is edited in place: a
   change is a new version, recorded in a decision.
2. This repository conforms to El Estatuto (`estatuto.toml`). Read `CONTRIBUTING.md` for the
   definition of done, `PROJECT_MAP.md` for where things live, and the standard's agent directive
   before changing structure.
3. `manifest.json` and `contracts/*.json` are rendered from `src/__PACKAGE__/capabilities.py`
   (`uv run __SLUG__ render`); never edit them by hand. `contracts/peg/` is vendored from the
   standard (`estatuto sync-peg .`); never edit it at all.
4. A published contract's rules never change in place. A breaking change is a new version and a
   deprecation entry with a removal version.
5. Authority is explicit, never inferred; a result never conveys authority and is never accepted
   here. Refusals are typed and honest: the `error_code` names the cause that occurred.
6. Everything in the live surface is English (see the standard's language clause). Fixture
   payloads may use any language when language neutrality is under test.
7. Before declaring work done, run:

```text
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

8. A change to `src/`, `contracts/`, `gates/`, `scripts/`, `manifest.json`, `pyproject.toml`,
   `conformance.py` or `estatuto.toml` records itself under `## Unreleased` in `CHANGELOG.md`;
   CI fails otherwise.
