# __NAME__

A governed employee framework built under El Estatuto. It receives typed assignments through the
Governed Employee Protocol (PEG/1), works under explicit authority and budget, and returns
evidence-first proposals that a governing application accepts or rejects. It never accepts its
own work.

## What it does

- Publishes one capability, `cap___SLUG___work01`, with its input, output and evidence contracts.
- Speaks PEG/1 in process and over HTTP: `POST /peg/v1/assignments`, `GET /peg/v1/manifest`,
  `GET /peg/v1/health`.
- Refuses what it cannot execute with a typed `peg.refusal/1.0.0`, never a disguised result.

## What it refuses to do

It does not decide, accept, close or govern. Authority, grants, budgets and acceptance stay with
the governing application. A result is `proposed: true`, always.

## Quickstart

```bash
uv sync --all-groups
uv run pytest
uv run python conformance.py
uv run __SLUG__ serve --port 8765
```

Then ask the running employee for its manifest:

```bash
curl -s http://127.0.0.1:8765/peg/v1/manifest
```

## Documentation

- `docs/governance/CHARTER.md` — what this employee is and is not. The normative source.
- `docs/tutorials/quickstart.md`, `docs/howto/`, `docs/topics/`, `docs/reference/` — Diátaxis.
- `PROJECT_MAP.md` — where everything lives and how to change it without breaking a guarantee.
- `AGENTS.md` — the rules an agent follows in this repository.

## Verifying a change

Run the chain in `CONTRIBUTING.md`. In short: ruff, mypy, pytest with coverage, `conformance.py`,
`estatuto gate .`, pip-audit, `uv build`, `mkdocs build --strict`. CI runs the same chain.

## Status

Scaffolded on __DATE__ under El Estatuto __STANDARD_VERSION__. The method is a deterministic
placeholder until the craft is written; the charter and the design baseline are skeletons that
must be completed before any horizon is claimed.
