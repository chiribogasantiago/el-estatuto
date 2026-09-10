# Command line

| Command | Effect |
|---|---|
| `estatuto render [--check]` | Render `schemas/peg/` from the protocol models; `--check` exits 1 when stale. |
| `estatuto gate [repository] [--output PATH]` | Measure a repository; print the summary; write the result document. Exit 0 on pass, 1 on fail, 2 when `estatuto.toml` is missing or invalid. |
| `estatuto changelog-gate --base REF [--root PATH]` | Fail when a normative change (per `[changelog]` in `estatuto.toml`) lacks a `CHANGELOG.md` entry. |
| `estatuto sync-peg [repository]` | Vendor the protocol schemas under `contracts/peg/`. |
| `estatuto new-employee DEST --name "El Nombre" --slug nombre [--package pkg] [--no-lock]` | Create a conforming employee framework. |
