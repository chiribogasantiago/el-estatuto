# Version a protocol document

A published `peg.*` document's validation rules never change in place.

1. Additive change (a new optional field with a default): bump the document's minor version in
   its `schema` literal, keep the previous class frozen, and record the coexistence window in
   `CHANGELOG.md`. Consumers negotiate the exact version they support; nothing is inferred.
2. Breaking change: a new class with a new major in its `schema` literal, a decision record, a
   deprecation entry with a removal version for the old one, and a migration note.
3. Render (`uv run estatuto render`), let every framework re-vendor (`estatuto sync-peg .`) and
   re-measure. The gate's byte comparison (E-7.1) is what makes the whole house move together.
