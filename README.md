# El Estatuto

The framework standard of the house and the owner of the Governed Employee Protocol (PEG/1).

Three frameworks were built independently — La Generala, which governs; El Corresponsal and La
Bibliotecaria, which work — and were about to be joined by many more. Each had grown its own
repository shape, documentation, naming and way of connecting. El Estatuto fixes the shared form so
that a governor connects any employee, an agent continues any repository, and a new employee is
created from zero already conforming.

## What it is

- **A standard** with numbered clauses (`docs/standard/STANDARD.md`; the owner's edition in
  Spanish is `ESTATUTO.md`) covering identity, repository, documentation, language, naming,
  tooling, protocol and the discipline of change.
- **A protocol**, PEG/1, rendered from one source to `schemas/peg/` and vendored verbatim by every
  framework: manifest, negotiation, bindings, assignment, result, refusal, health.
- **A gate**, `estatuto gate`, that measures any repository against the standard and produces a
  typed result document.
- **A factory**, `estatuto new-employee`, that creates a complete employee framework passing the
  gate and its own tests at birth.

## What it is not

It governs form, never substance: what a framework is belongs to that framework's charter. It is
not a runtime dependency of any framework — a tool their CI runs and a source of schemas they
vendor.

## Quickstart

```bash
uv sync --all-groups
uv run estatuto --version
uv run estatuto gate .                                   # the standard measures itself
uv run estatuto new-employee /tmp/el-archivero --name "El Archivero" --slug archivero
uv run estatuto gate /tmp/el-archivero                   # a newborn employee passes
```

From another repository, without installing anything permanently:

```bash
uvx --from git+https://github.com/chiribogasantiago/el-estatuto estatuto gate .
```

## Documentation

- [The standard](docs/standard/STANDARD.md) · [Owner's edition](ESTATUTO.md)
- [PEG/1](docs/protocol/PEG-1.md)
- [Creating an employee](docs/standard/NEW-EMPLOYEE.md) · [Agent directive](docs/standard/AGENT-DIRECTIVE.md)
- [Decisions](docs/decisions/index.md) · [Charter](docs/governance/CHARTER.md)
- `PROJECT_MAP.md` for where everything lives; `AGENTS.md` for the rules in this repository.

## Verifying a change

The chain in `AGENTS.md`: ruff, mypy, pytest with coverage, `estatuto render --check`,
`estatuto gate .`, pip-audit, `uv build`, `mkdocs build --strict`. CI runs the same chain.

## Status

1.0.0, in force since 2026-09-10. Applied to the three existing frameworks; each measures its own
conformance in CI. The protocol keeps the governor's candidate shapes with a neutral owner, two
added documents and three renamed fields; see the decision records.
