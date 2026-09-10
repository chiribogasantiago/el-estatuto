"""Render the ``peg.*`` JSON Schemas from the protocol models, or check that they are current.

``schemas/peg/<name>-v<version>.json`` is a projection of ``estatuto.peg.contracts``; it is never
edited by hand. Every conforming framework vendors these files verbatim under ``contracts/peg/``.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from estatuto.peg.contracts import DOCUMENTS, StrictModel, schema_filename, schema_id

JSON_SCHEMA_DIALECT = "https://json-schema.org/draft/2020-12/schema"


def rendered_schema(document: type[StrictModel]) -> str:
    """The published JSON text of one document's schema, with ``$id`` and ``$schema`` first."""
    body: dict[str, Any] = document.model_json_schema(by_alias=True)
    envelope: dict[str, Any] = {"$id": schema_id(document), "$schema": JSON_SCHEMA_DIALECT}
    envelope.update(body)
    return json.dumps(envelope, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def render_all(destination: Path, *, check: bool = False) -> list[str]:
    """Write every schema under ``destination``; return the files changed (or that would change)."""
    destination.mkdir(parents=True, exist_ok=True)
    changed: list[str] = []
    expected = {schema_filename(document): rendered_schema(document) for document in DOCUMENTS}
    for name, text in expected.items():
        target = destination / name
        current = target.read_text(encoding="utf-8") if target.exists() else None
        if current != text:
            changed.append(name)
            if not check:
                target.write_text(text, encoding="utf-8")
    for stray in sorted(path.name for path in destination.glob("*.json")):
        if stray not in expected:
            changed.append(stray)
            if not check:
                (destination / stray).unlink()
    return changed


__all__ = ["JSON_SCHEMA_DIALECT", "render_all", "rendered_schema"]
