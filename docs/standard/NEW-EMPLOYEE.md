# Creating an employee from zero

An employee is a framework with a craft. It is created conforming: the factory produces a whole
repository that passes the standard's gate and its own tests at birth, and the work that follows is
the craft, the charter and the design — never the scaffolding.

## 1. Before the first command

Answer in one paragraph each, in English, and keep the answers; they become the charter:

- What does the employee convert into what, for whom, and where does it stop?
- Which capabilities does it offer, each with one input, one output and one evidence contract?
- What does it refuse to do, and which error codes name its refusals?
- What costs does it incur, in which unit, and how does a receipt prove them?

Choose the persona (`El` or `La` and a capitalised name), the slug (lowercase, the persona's name
without its article) and, if different, the package.

## 2. Create it

```bash
uvx --from git+https://github.com/chiribogasantiago/el-estatuto estatuto new-employee ../el-archivero --name "El Archivero" --slug archivero
cd ../el-archivero
git init && git add -A && git commit -m "feat: scaffold El Archivero under El Estatuto"
uv sync --all-groups
uv run pytest
uv run python conformance.py
uvx --from git+https://github.com/chiribogasantiago/el-estatuto estatuto gate .
```

The gate passes. What you have is a complete, honest, empty employee: one placeholder capability,
the PEG/1 adapter with its three routes, two in-process transports proven equivalent, executable
conformance, a gate corpus, the documentation skeleton, CI. Read `PROJECT_MAP.md` — it was written
for you.

## 3. Write the charter

`docs/governance/CHARTER.md` is the normative source of what the employee is and is not. Complete
every section with the answers from step 1. Then write the design description under
`docs/governance/baseline/` as a new file, and freeze it:

```bash
cd docs/governance/baseline && shasum -a 256 SDD-*.md > BASELINE.sha256 && cd -
```

A frozen file is never edited again; a new version is a new file and a new hash line.

## 4. Declare the capabilities

In `src/<package>/contracts.py`, define each input, output and evidence contract as a closed
Pydantic model with a `schema` literal `<slug>.<name>/1.0.0`. In `capabilities.py`, register the
contracts and the capabilities (`cap_<slug>_<name>01`), the modes and the error codes. Render:

```bash
uv run <slug> render
```

`manifest.json` and `contracts/*.json` are now projections of your declarations. Never edit them.

## 5. Write the craft

`src/<package>/employee.py` owns the invariants: strict contracts, honest states, cost equal to the
sum of receipts, `proposed: true`. Everything a deployment might want differently — providers,
models, limits, vocabularies, templates — is an injected policy with a named default, reached
through ports. A new capability arrives through declarations, ports and policies, never by branching
the core on a use case.

Every evidence item carries a digest and a reference. Every receipt carries a unit, a quantity and
a cost. A result that is not `completed` names its error code, at least one limitation and one next
step. A refusal is a typed document, never a disguised result.

## 6. Prove it

Tests are named after the subject they protect. For each capability: the method on valid input, the
rejection on invalid input, the wire (assignment in, result out, refusals on tampering and on
undeclared capabilities), and the transport equivalence. Add the tests to `gates/<slug>-gate-…json`
so a promise cannot silently lose its proof. Keep branch coverage at or above the floor; raise the
floor when coverage rises; never lower it.

## 7. Document it

Diátaxis: a tutorial that takes a reader to a served, answered assignment; how-to pages for the
tasks an integrator performs; topics for the concepts; reference for contracts, routes, error codes
and the command line. Record every decision the code depends on under `docs/decisions/`. Record
every normative change under `## Unreleased`.

## 8. Connect it to the governor

The governor discovers the employee from its manifest, negotiates a compatibility demand against
each capability, admits the version per tenant through its administration plane, and only then
assigns. The employee never depends on the governor's code. Ask the governor's maintainers to add
the employee to their composition; give them the manifest, the contracts and the base URL.

## 9. Release

`src/<package>/version.py` is the single source. Bump it, move `## Unreleased` under
`## <version> — <date>`, re-render (`<slug> render`), run the chain in `AGENTS.md`, tag. An updated
employee is a new version admitted next to the previous one until rollback is proven.

## What never happens

- Editing `contracts/peg/`, `manifest.json`, `contracts/*.json`, a frozen baseline or a recorded
  evidence file by hand.
- Depending on the governor or on another employee at runtime.
- Accepting, closing or governing anything. The employee proposes.
- Claiming in a document what code and a test do not prove.
- Writing Spanish, or a machine path, into the live surface.
