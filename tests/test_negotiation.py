"""Negotiation is exact, ordered and decided before any assignment exists."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from estatuto.peg import CompatibilityDemand, Manifest, compatibility_token, negotiate
from tests.test_peg_contracts import manifest_document

NOW = datetime(2026, 9, 10, tzinfo=UTC)


def demand(**overrides: object) -> CompatibilityDemand:
    document: dict[str, object] = {
        "schema": "peg.compatibility-demand/1.0.0",
        "protocol_version": "1.0.0",
        "required_profiles": ["CORE"],
        "capability_id": "cap_archivero_work01",
        "capability_version": "0.1.0",
        "input_contract": "archivero.work-assignment/1.0.0",
        "output_contract": "archivero.work-result/1.0.0",
        "evidence_contract": "archivero.evidence-bundle/1.0.0",
        "mode": "job",
        "checkpoint_required": False,
    }
    document.update(overrides)
    return CompatibilityDemand.model_validate(document)


def test_an_exact_match_is_accepted_with_no_reasons() -> None:
    decision = negotiate(Manifest.model_validate(manifest_document()), demand(), now=NOW)
    assert (
        decision.disposition == "accept" and decision.reasons == [] and decision.decided_at == NOW
    )


def test_every_material_difference_is_a_stable_reason_in_protocol_order() -> None:
    manifest = Manifest.model_validate(manifest_document())
    decision = negotiate(
        manifest,
        demand(
            protocol_version="2.0.0",
            required_profiles=["CORE", "FRAMEWORK"],
            mode="session",
            output_contract="archivero.other/1.0.0",
            evidence_contract="archivero.other-evidence/1.0.0",
            checkpoint_required=True,
        ),
    )
    assert decision.disposition == "reject"
    assert decision.reasons == [
        "PROTOCOL_UNSUPPORTED",
        "PROFILE_UNSUPPORTED",
        "MODE_UNSUPPORTED",
        "OUTPUT_CONTRACT_MISMATCH",
        "EVIDENCE_CONTRACT_MISMATCH",
        "CHECKPOINT_UNSUPPORTED",
    ]


def test_a_shared_capability_id_at_another_version_is_not_substitutable() -> None:
    manifest = Manifest.model_validate(manifest_document())
    assert negotiate(manifest, demand(capability_version="0.2.0")).reasons == [
        "CAPABILITY_UNSUPPORTED"
    ]


def test_a_deprecated_input_contract_is_still_accepted() -> None:
    capability = dict(manifest_document()["capabilities"][0])  # type: ignore[index]
    capability["input_contract"] = "archivero.work-assignment/2.0.0"
    capability["deprecated_input_contracts"] = ["archivero.work-assignment/1.0.0"]
    manifest = Manifest.model_validate(manifest_document(capabilities=[capability]))
    assert negotiate(manifest, demand()).disposition == "accept"
    assert negotiate(
        manifest, demand(input_contract="archivero.work-assignment/3.0.0")
    ).reasons == ["INPUT_CONTRACT_MISMATCH"]


def test_the_compatibility_token_is_deterministic_and_refused_on_reject() -> None:
    manifest = Manifest.model_validate(manifest_document())
    assert compatibility_token(manifest, demand()) == compatibility_token(manifest, demand())
    assert len(compatibility_token(manifest, demand())) == 64
    with pytest.raises(ValueError, match="MODE_UNSUPPORTED"):
        compatibility_token(manifest, demand(mode="session"))
