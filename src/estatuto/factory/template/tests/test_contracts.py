"""The published contracts: honest results, current renderings, identified files."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from __PACKAGE__.capabilities import CONTRACTS, render_publication
from __PACKAGE__.contracts import EvidenceBundle, Receipt, WorkResult

ROOT = Path(__file__).resolve().parents[1]


def _result(**overrides: object) -> WorkResult:
    base: dict[str, object] = {
        "schema": "__SLUG__.work-result/1.0.0",
        "state": "completed",
        "employee_id": "__EMPLOYEE_ID__",
        "employee_version": "0.1.0",
        "tenant_id": "ten_a",
        "request_id": "req_1",
        "objective": "x",
        "summary": "done",
        "evidence": EvidenceBundle(schema="__SLUG__.evidence-bundle/1.0.0"),
        "receipts": [Receipt(receipt_id="r", unit="work-unit", quantity=1, cost_micros=5)],
        "observed_cost_micros": 5,
    }
    base.update(overrides)
    return WorkResult.model_validate(base)


def test_a_non_completed_result_names_its_cause_and_a_next_step() -> None:
    with pytest.raises(ValidationError):
        _result(state="blocked")
    blocked = _result(
        state="blocked",
        error_code="PROVIDER_UNAVAILABLE",
        limitations=["no provider"],
        next_steps=["retry later"],
    )
    assert blocked.proposed is True


def test_cost_equals_the_sum_of_receipts() -> None:
    with pytest.raises(ValidationError):
        _result(observed_cost_micros=6)


def test_publication_is_current() -> None:
    assert render_publication(ROOT, check=True) == []


def test_every_contract_file_publishes_its_id() -> None:
    for contract in CONTRACTS:
        document = json.loads((ROOT / "contracts" / contract.filename).read_text())
        assert document["$id"] == contract.contract_id
        assert document["additionalProperties"] is False
