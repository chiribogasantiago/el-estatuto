# Add a capability

1. Declare the input, output and evidence contracts as closed Pydantic models in
   `src/__PACKAGE__/contracts.py`, each with a `schema` literal `__SLUG__.<name>/<version>`.
2. Register them as `ContractVersion` entries and the capability as a `CapabilityDeclaration` in
   `src/__PACKAGE__/capabilities.py`. The capability id follows `cap_<slug>_<name>NN`.
3. Route the capability in `src/__PACKAGE__/peg.py` if its method differs from the default.
4. Render: `uv run __SLUG__ render`. Commit `manifest.json` and the new `contracts/*.json`.
5. Test the method, the wire and the refusals; name the test file after the capability.
6. Document it here and in `docs/reference/contracts.md`; record it under `## Unreleased`.
