# Contributing to El Estatuto

Written for the next person or agent who continues the standard. Where a rule has an executable
gate, the gate wins over this text.

## What changes here, and how

| Change | Path | Records itself as |
|---|---|---|
| A clause | `docs/standard/STANDARD.md` and `ESTATUTO.md`, same identifier | a decision record and a version bump per the rule below |
| A protocol document | `src/estatuto/peg/contracts.py`, then `uv run estatuto render` | a new version of that document, never an edit in place |
| A control | `src/estatuto/gate/controls.py`, its test in `tests/test_gate.py`, its entry in `gates/framework-standard-gate-v1.0.0.json` | the clause it enforces |
| The template | `src/estatuto/factory/template/` | `tests/test_gate.py` must stay green |
| A framework of the house | `registry/frameworks.json` | a changelog entry |

## Versioning and deprecation

The standard's version follows semantic versioning. A clause that becomes stricter, or a protocol
document whose shape changes, is a **major**: every framework must re-measure and the changelog
names the migration. An additive clause or document is a **minor**. Wording and tooling are
**patches**. A deprecated clause or document keeps applying for at least one minor release after
the release that deprecates it, is listed in `CHANGELOG.md` with its replacement and its removal
version, and changes nothing silently in the meantime.

## Language

The live surface is English. The owner's edition (`ESTATUTO.md`, `docs/es/`) is Spanish and is
archived from the language check; it must carry the same clause identifiers as the English
standard, and the gate verifies it.

## Definition of done

1. The clause, the control and the test agree.
2. The template still produces a repository that passes the gate.
3. The whole verification chain in `AGENTS.md` passes.
4. The change is recorded under `## Unreleased`.
5. The documentation describes exactly what exists, again.

## Verification chain

See `AGENTS.md`. CI runs the same chain.

## No clutter

No machine-specific paths in the live surface. No claim that code and a test do not back.
Test files are named after the subject they protect. `work/`, `dist/`, `site/` and caches are
disposable.
