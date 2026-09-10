"""The protocol documents: identifiers, coherence rules and the rendered schemas."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from estatuto.peg import DOCUMENTS, Manifest, integrity_digest, schema_filename, schema_id
from estatuto.render import render_all, rendered_schema

ROOT = Path(__file__).resolve().parents[1]


def manifest_document(**overrides: object) -> dict[str, object]:
    document: dict[str, object] = {
        "schema": "peg.manifest/1.0.0",
        "employee_id": "emp_archivero01",
        "employee_version": "0.1.0",
        "protocol_versions": ["1.0.0"],
        "profiles": ["CORE"],
        "capabilities": [
            {
                "capability_id": "cap_archivero_work01",
                "version": "0.1.0",
                "input_contract": "archivero.work-assignment/1.0.0",
                "output_contract": "archivero.work-result/1.0.0",
                "evidence_contract": "archivero.evidence-bundle/1.0.0",
                "cost_unit": "work-unit",
                "supports_checkpoint": False,
                "deprecated_input_contracts": [],
            }
        ],
        "modes": ["job"],
        "error_codes": ["CONTRACT_INVALID"],
        "packs": [],
    }
    document.update(overrides)
    document["integrity_digest"] = integrity_digest(document)
    return document


def test_every_document_publishes_a_peg_schema_id_and_filename() -> None:
    for document in DOCUMENTS:
        identifier = schema_id(document)
        assert identifier.startswith("peg.") and identifier.endswith("/1.0.0")
        assert schema_filename(document).endswith("-v1.0.0.json")


def test_rendered_schemas_are_current_and_carry_their_id() -> None:
    assert render_all(ROOT / "schemas" / "peg", check=True) == []
    for document in DOCUMENTS:
        published = json.loads((ROOT / "schemas" / "peg" / schema_filename(document)).read_text())
        assert published["$id"] == schema_id(document)
        assert published["additionalProperties"] is False
        assert published["properties"]["schema"]["const"] == schema_id(document)


def test_rendered_schema_text_is_deterministic() -> None:
    assert rendered_schema(Manifest) == rendered_schema(Manifest)


def test_manifest_requires_the_core_profile() -> None:
    with pytest.raises(ValidationError, match="CORE"):
        Manifest.model_validate(manifest_document(profiles=["FRAMEWORK"]))


def test_manifest_rejects_duplicate_capabilities_and_undeclared_pack_members() -> None:
    capability = manifest_document()["capabilities"][0]  # type: ignore[index]
    with pytest.raises(ValidationError, match="unique"):
        Manifest.model_validate(manifest_document(capabilities=[capability, capability]))
    pack = {"pack_id": "pack_archive", "version": "0.1.0", "capabilities": ["cap_other_thing01"]}
    with pytest.raises(ValidationError, match="undeclared"):
        Manifest.model_validate(manifest_document(packs=[pack]))


def test_manifest_rejects_unknown_fields_and_malformed_identifiers() -> None:
    with pytest.raises(ValidationError):
        Manifest.model_validate(manifest_document(extra_field=True))
    with pytest.raises(ValidationError):
        Manifest.model_validate(manifest_document(employee_id="archivero"))
    with pytest.raises(ValidationError):
        Manifest.model_validate(manifest_document(error_codes=["contract-invalid"]))


def test_a_valid_manifest_round_trips_by_alias() -> None:
    manifest = Manifest.model_validate(manifest_document())
    dumped = manifest.model_dump(by_alias=True, mode="json")
    assert dumped["schema"] == "peg.manifest/1.0.0"
    assert dumped["integrity_digest"] == integrity_digest(dumped)


def test_render_all_writes_missing_schemas_and_removes_strays(tmp_path: Path) -> None:
    stray = tmp_path / "stray-v0.0.1.json"
    stray.write_text("{}")
    changed = render_all(tmp_path, check=True)
    assert "manifest-v1.0.0.json" in changed and "stray-v0.0.1.json" in changed and stray.exists()
    render_all(tmp_path)
    assert not stray.exists() and len(list(tmp_path.glob("*.json"))) == len(DOCUMENTS)
    assert render_all(tmp_path, check=True) == []
