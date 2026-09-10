"""The method: valid assignments become proposals; invalid ones are rejected without work."""

from __future__ import annotations

from __PACKAGE__.employee import Employee

REQUEST = {
    "schema": "__SLUG__.work-assignment/1.0.0",
    "tenant_id": "ten_aurora0001",
    "request_id": "req_1",
    "objective": "Acknowledge.",
    "budget_micros": 0,
}


def test_a_valid_assignment_becomes_a_completed_proposal() -> None:
    result = Employee().execute(dict(REQUEST))
    assert result["state"] == "completed"
    assert result["proposed"] is True
    assert result["evidence"]["items"]
    assert result["observed_cost_micros"] == sum(item["cost_micros"] for item in result["receipts"])


def test_an_invalid_assignment_is_rejected_as_contract_invalid() -> None:
    result = Employee().execute({"tenant_id": "ten_aurora0001"})
    assert result["state"] == "rejected"
    assert result["error_code"] == "CONTRACT_INVALID"
    assert result["limitations"] and result["next_steps"]


def test_two_tenants_produce_distinct_evidence() -> None:
    aurora = Employee().execute(dict(REQUEST))
    boreal = Employee().execute({**REQUEST, "tenant_id": "ten_boreal00001"})
    assert aurora["evidence"]["items"][0]["digest"] != boreal["evidence"]["items"][0]["digest"]


def test_a_new_version_changes_the_output_and_rollback_restores_it() -> None:
    baseline = Employee(version="0.1.0").execute(dict(REQUEST))
    candidate = Employee(version="0.2.0").execute(dict(REQUEST))
    rollback = Employee(version="0.1.0").execute(dict(REQUEST))
    assert candidate["evidence"] != baseline["evidence"]
    assert rollback == baseline
