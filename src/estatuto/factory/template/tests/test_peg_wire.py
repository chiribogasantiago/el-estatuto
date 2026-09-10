"""The protocol wire: assignments are attested back, defects are typed refusals, HTTP equals in-process."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from collections.abc import Iterator
from typing import Any

import pytest
from jsonschema import Draft202012Validator

from __PACKAGE__.capabilities import EMPLOYEE_ID, canonical_digest
from __PACKAGE__.peg import PegEmployee, load_schema
from __PACKAGE__.transports import ASSIGNMENTS, HEALTH, MANIFEST, HttpServer
from __PACKAGE__.version import EMPLOYEE_VERSION


def assignment(**overrides: Any) -> dict[str, Any]:
    request = {
        "schema": "__SLUG__.work-assignment/1.0.0",
        "tenant_id": "ten_aurora0001",
        "request_id": "req_1",
        "objective": "Acknowledge.",
        "budget_micros": 0,
        "inputs": {},
    }
    context = {"request": request}
    document: dict[str, Any] = {
        "schema": "peg.assignment/1.0.0",
        "tenant_id": "ten_aurora0001",
        "mission_id": "mis_aurora0001",
        "run_id": "run_1",
        "obligation_id": "obl_1",
        "assignment_id": "asg_1",
        "employee_id": EMPLOYEE_ID,
        "employee_version": EMPLOYEE_VERSION,
        "capability_id": "cap___SLUG___work01",
        "capability_version": EMPLOYEE_VERSION,
        "compatibility_token": "b" * 64,
        "generation": 1,
        "purpose": "test",
        "acceptance_criteria": ["a proposal comes back"],
        "context_digest": canonical_digest(context),
        "context": context,
    }
    document.update(overrides)
    return document


def valid(document: dict[str, Any], name: str) -> None:
    Draft202012Validator(load_schema(name)).validate(document)


def test_a_valid_assignment_is_attested_back_as_a_result() -> None:
    status, result = PegEmployee().handle(assignment())
    assert status == 200
    valid(result, "result")
    assert result["assignment_id"] == "asg_1"
    assert result["context_digest"] == assignment()["context_digest"]
    assert result["conveys_authority"] is False
    assert result["handoff_payload"]["proposed"] is True


def test_a_malformed_assignment_is_refused_as_contract_invalid() -> None:
    status, refusal = PegEmployee().handle(
        {"schema": "peg.assignment/1.0.0", "assignment_id": "asg_x"}
    )
    assert status == 400
    valid(refusal, "refusal")
    assert refusal["error_code"] == "CONTRACT_INVALID" and refusal["assignment_id"] == "asg_x"


def test_a_tampered_context_is_refused() -> None:
    status, refusal = PegEmployee().handle(assignment(context_digest="c" * 64))
    assert status == 400 and refusal["reasons"] == ["context_digest does not match context"]


def test_an_undeclared_capability_is_refused_before_any_work() -> None:
    status, refusal = PegEmployee().handle(assignment(capability_version="9.9.9"))
    assert status == 422 and refusal["error_code"] == "CAPABILITY_UNSUPPORTED"


@pytest.fixture
def server() -> Iterator[HttpServer]:
    running = HttpServer(PegEmployee()).start()
    yield running
    running.stop()


def _get(url: str) -> tuple[int, dict[str, Any]]:
    with urllib.request.urlopen(url, timeout=5) as response:
        return response.status, json.loads(response.read())


def _post(url: str, document: dict[str, Any]) -> tuple[int, dict[str, Any]]:
    body = json.dumps(document).encode()
    request = urllib.request.Request(
        url, data=body, headers={"Content-Type": "application/json"}, method="POST"
    )
    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            return response.status, json.loads(response.read())
    except urllib.error.HTTPError as error:
        return error.code, json.loads(error.read())


def test_http_exchange_equals_the_in_process_exchange(server: HttpServer) -> None:
    status, over_http = _post(server.base_url + ASSIGNMENTS, assignment())
    direct_status, direct = PegEmployee().handle(assignment())
    assert (status, over_http) == (direct_status, direct)


def test_http_publishes_manifest_and_health(server: HttpServer) -> None:
    status, manifest = _get(server.base_url + MANIFEST)
    assert status == 200
    valid(manifest, "manifest")
    status, health = _get(server.base_url + HEALTH)
    assert status == 200
    valid(health, "health-report")


def test_http_refusal_carries_the_protocol_status(server: HttpServer) -> None:
    status, refusal = _post(
        server.base_url + ASSIGNMENTS, assignment(capability_id="cap_unknown_thing01")
    )
    assert status == 422 and refusal["schema"] == "peg.refusal/1.0.0"
