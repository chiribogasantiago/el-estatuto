# Command line

| Command | Effect |
|---|---|
| `__SLUG__ render [--check]` | Render `manifest.json` and `contracts/*.json` from the declarations; `--check` exits 1 when stale. |
| `__SLUG__ serve [--host] [--port]` | Serve PEG/1 over HTTP. |
| `python conformance.py` | Run executable conformance; exit 1 on any finding. |
| `estatuto gate .` | Measure conformance to El Estatuto. |
