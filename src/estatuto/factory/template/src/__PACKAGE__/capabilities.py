"""Capabilities, error codes and published contracts, declared in code.

``manifest.json`` and every file under ``contracts/`` are projections of this module, rendered by
``__SLUG__ render``; conformance fails when a published file disagrees with its rendering.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from __PACKAGE__.contracts import EvidenceBundle, WorkAssignment, WorkResult
from __PACKAGE__.version import EMPLOYEE_VERSION

EMPLOYEE_ID = "__EMPLOYEE_ID__"
MANIFEST_SCHEMA = "peg.manifest/1.0.0"
JSON_SCHEMA_DIALECT = "https://json-schema.org/draft/2020-12/schema"
PROTOCOL_VERSIONS: tuple[str, ...] = ("1.0.0",)
PROFILES: tuple[str, ...] = ("CORE",)
MODES: tuple[str, ...] = ("job", "request")

#: Every error code a result or a refusal may carry. Reserved codes keep the protocol's meaning.
ERROR_CODES: tuple[str, ...] = (
    "CONTRACT_INVALID",
    "CAPABILITY_UNSUPPORTED",
    "POLICY_BLOCKED",
    "BUDGET_EXCEEDED",
    "PROVIDER_UNAVAILABLE",
    "EVIDENCE_INSUFFICIENT",
)


@dataclass(frozen=True, slots=True)
class ContractVersion:
    """One published, model-backed contract document."""

    model: type[BaseModel]
    contract_id: str

    @property
    def filename(self) -> str:
        """``__SLUG__.work-result/1.0.0`` is published as ``work-result-v1.0.0.json``."""
        owner_name, _, version = self.contract_id.partition("/")
        return f"{owner_name.partition('.')[2]}-v{version}.json"


@dataclass(frozen=True, slots=True)
class CapabilityDeclaration:
    """What one capability publishes."""

    capability_id: str
    input_contract: ContractVersion
    output_contract: ContractVersion
    evidence_contract: ContractVersion
    cost_unit: str
    supports_checkpoint: bool = False
    deprecated_input_contracts: tuple[ContractVersion, ...] = ()


WORK_ASSIGNMENT = ContractVersion(WorkAssignment, "__SLUG__.work-assignment/1.0.0")
WORK_RESULT = ContractVersion(WorkResult, "__SLUG__.work-result/1.0.0")
EVIDENCE_BUNDLE = ContractVersion(EvidenceBundle, "__SLUG__.evidence-bundle/1.0.0")

CONTRACTS: tuple[ContractVersion, ...] = (WORK_ASSIGNMENT, WORK_RESULT, EVIDENCE_BUNDLE)

CAPABILITIES: tuple[CapabilityDeclaration, ...] = (
    CapabilityDeclaration(
        capability_id="cap___SLUG___work01",
        input_contract=WORK_ASSIGNMENT,
        output_contract=WORK_RESULT,
        evidence_contract=EVIDENCE_BUNDLE,
        cost_unit="work-unit",
    ),
)


def canonical_digest(value: Any) -> str:
    """SHA-256 of the canonical JSON form: sorted keys, compact separators, UTF-8."""
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def manifest_document() -> dict[str, Any]:
    """The ``peg.manifest/1.0.0`` document, with a digest any consumer can verify."""
    document: dict[str, Any] = {
        "schema": MANIFEST_SCHEMA,
        "employee_id": EMPLOYEE_ID,
        "employee_version": EMPLOYEE_VERSION,
        "protocol_versions": list(PROTOCOL_VERSIONS),
        "profiles": list(PROFILES),
        "capabilities": [
            {
                "capability_id": item.capability_id,
                "version": EMPLOYEE_VERSION,
                "input_contract": item.input_contract.contract_id,
                "output_contract": item.output_contract.contract_id,
                "evidence_contract": item.evidence_contract.contract_id,
                "cost_unit": item.cost_unit,
                "supports_checkpoint": item.supports_checkpoint,
                "deprecated_input_contracts": [
                    old.contract_id for old in item.deprecated_input_contracts
                ],
            }
            for item in CAPABILITIES
        ],
        "modes": list(MODES),
        "error_codes": list(ERROR_CODES),
        "packs": [],
    }
    document["integrity_digest"] = canonical_digest(document)
    return document


def rendered_contract(contract: ContractVersion) -> str:
    """The published JSON Schema text of one contract."""
    envelope: dict[str, Any] = {"$id": contract.contract_id, "$schema": JSON_SCHEMA_DIALECT}
    envelope.update(contract.model.model_json_schema(by_alias=True))
    return json.dumps(envelope, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def render_publication(root: Path, *, check: bool = False) -> list[str]:
    """Write ``manifest.json`` and ``contracts/*.json``; return what changed (or would change)."""
    expected: dict[Path, str] = {
        root / "manifest.json": json.dumps(manifest_document(), indent=2, ensure_ascii=False) + "\n"
    }
    for contract in CONTRACTS:
        expected[root / "contracts" / contract.filename] = rendered_contract(contract)
    changed: list[str] = []
    for path, text in expected.items():
        current = path.read_text(encoding="utf-8") if path.exists() else None
        if current != text:
            changed.append(path.relative_to(root).as_posix())
            if not check:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(text, encoding="utf-8")
    return changed


def find_capability(capability_id: str, version: str) -> CapabilityDeclaration | None:
    """The declared capability with this exact id and version, if any."""
    if version != EMPLOYEE_VERSION:
        return None
    return next((item for item in CAPABILITIES if item.capability_id == capability_id), None)


__all__ = [
    "CAPABILITIES",
    "CONTRACTS",
    "EMPLOYEE_ID",
    "ERROR_CODES",
    "MANIFEST_SCHEMA",
    "MODES",
    "PROFILES",
    "PROTOCOL_VERSIONS",
    "CapabilityDeclaration",
    "ContractVersion",
    "canonical_digest",
    "find_capability",
    "manifest_document",
    "render_publication",
    "rendered_contract",
]
