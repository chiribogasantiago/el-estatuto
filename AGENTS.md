# Working rules for El Estatuto

1. This repository is the standard. Its normative text is `docs/standard/STANDARD.md`; the owner's
   edition is `ESTATUTO.md`; the two carry the same clause identifiers and the gate fails when
   they drift (E-9.1). The charter of the standard itself is `docs/governance/CHARTER.md`.
2. The protocol's source is `src/estatuto/peg/contracts.py`. `schemas/peg/` is rendered from it
   (`uv run estatuto render`) and never edited by hand. A protocol document's rules never change
   in place: a breaking change is a new version and a decision record.
3. The controls in `src/estatuto/gate/controls.py` enforce clauses. A control without a clause,
   or a clause that claims enforcement without a control, is a defect. `tests/test_self_conformance.py`
   and `tests/test_release_discipline.py` check both directions.
4. The factory template under `src/estatuto/factory/template/` is a whole repository. A change
   there must keep `tests/test_gate.py::test_a_scaffolded_employee_passes_every_applicable_control`
   green: the standard never ships a template that fails its own gate.
5. Everything in the live surface is English except the Spanish edition, which is archived from
   the language check and kept in parity by clause identifiers.
6. Read `docs/standard/AGENT-DIRECTIVE.md` before changing structure anywhere in the house; it
   binds this repository too.
7. Before declaring work done, run:

```text
uv run ruff check src tests
uv run ruff format --check src tests
uv run mypy
uv run pytest --cov --cov-branch --cov-report=term-missing --cov-fail-under=80
uv run estatuto render --check
uv run estatuto gate . --output work/framework-standard-gate.json
uv run pip-audit --skip-editable
uv build
uv run mkdocs build --strict
```

8. A change to `src/`, `schemas/`, `gates/`, `registry/`, `docs/standard/`, `docs/protocol/`,
   `pyproject.toml`, `estatuto.toml` or `ESTATUTO.md` records itself under `## Unreleased` in
   `CHANGELOG.md`; CI fails otherwise.
