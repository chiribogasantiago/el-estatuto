"""The standard gate: a conforming employee passes; each broken clause is named; exceptions are dated."""

from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path

import pytest

from estatuto.gate.config import ConfigError, load_config
from estatuto.gate.controls import CONTROLS
from estatuto.gate.runner import CONTROL_IDS, RESULT_SCHEMA, render_text, run_gate, write_result


def failures(root: Path) -> dict[str, list[str]]:
    result = run_gate(root)
    return {item.control_id: item.findings for item in result.controls if item.status == "failed"}


def test_a_scaffolded_employee_passes_every_applicable_control(employee: Path) -> None:
    result = run_gate(employee)
    assert result.passed, render_text(result)
    assert result.role == "employee" and result.maximum_score == 32


def test_the_result_document_is_published_and_typed(employee: Path, tmp_path: Path) -> None:
    result = run_gate(employee)
    output = tmp_path / "gate.json"
    write_result(result, output)
    document = json.loads(output.read_text())
    assert document["schema"] == RESULT_SCHEMA and document["gate_passed"] is True
    assert {item["control_id"] for item in document["controls"]} == CONTROL_IDS
    assert "PASS 32/32" in render_text(result)


def test_every_control_has_a_unique_clause_id() -> None:
    identifiers = [control.control_id for control in CONTROLS]
    assert len(identifiers) == len(set(identifiers))
    assert all(identifier.startswith("E-") for identifier in identifiers)


def test_a_missing_declaration_is_an_error_not_a_guess(tmp_path: Path) -> None:
    with pytest.raises(ConfigError, match="estatuto.toml"):
        run_gate(tmp_path)


def test_a_missing_root_file_names_the_file(mutable_employee: Path) -> None:
    (mutable_employee / "AGENTS.md").unlink()
    assert failures(mutable_employee)["E-2.1"] == ["missing AGENTS.md"]


def test_a_tampered_baseline_fails_the_hash_check(mutable_employee: Path) -> None:
    sdd = next((mutable_employee / "docs" / "governance" / "baseline").glob("SDD-*.md"))
    sdd.write_text(sdd.read_text() + "\nedited in place\n")
    assert any(
        "does not match its recorded hash" in finding
        for finding in failures(mutable_employee)["E-3.3"]
    )


def test_spanish_prose_in_the_live_surface_is_found(mutable_employee: Path) -> None:
    (mutable_employee / "docs" / "topics" / "concepts.md").write_text(
        "# Conceptos\n\nEsta es una página para el equipo.\n"
    )
    assert failures(mutable_employee)["E-4.1"][0].startswith(
        "docs/topics/concepts.md has Spanish prose"
    )


def test_spanish_in_the_archive_is_tolerated(mutable_employee: Path) -> None:
    baseline = mutable_employee / "docs" / "governance" / "baseline"
    (baseline / "SDD-archivero-v0.0.1.md").write_text(
        "# SDD\n\nUna versión histórica para el archivo.\n"
    )
    assert "E-4.1" not in failures(mutable_employee)


def test_a_vendored_schema_that_drifts_is_found(mutable_employee: Path) -> None:
    (mutable_employee / "contracts" / "peg" / "result-v1.0.0.json").write_text("{}\n")
    assert failures(mutable_employee)["E-7.1"] == [
        "contracts/peg/result-v1.0.0.json differs from the standard's schema"
    ]


def test_a_manifest_digest_that_does_not_verify_is_found(mutable_employee: Path) -> None:
    path = mutable_employee / "manifest.json"
    document = json.loads(path.read_text())
    document["integrity_digest"] = "0" * 64
    path.write_text(json.dumps(document))
    assert failures(mutable_employee)["E-7.2"] == [
        "manifest.json integrity_digest is not the digest of the manifest itself"
    ]


def test_a_dated_exception_waives_a_failing_control_until_its_sunset(
    mutable_employee: Path,
) -> None:
    (mutable_employee / "docs" / "reference" / "cli.md").unlink()
    (mutable_employee / "docs" / "reference" / "contracts.md").unlink()
    (mutable_employee / "mkdocs.yml").write_text(
        (mutable_employee / "mkdocs.yml")
        .read_text()
        .replace(
            "      - Contracts and protocol surface: reference/contracts.md\n      - Command line: reference/cli.md\n",
            "",
        )
    )
    decision = mutable_employee / "docs" / "decisions" / "0002-reference-pages-later.md"
    decision.write_text("# 0002 — Reference pages arrive with the first real capability\n")
    index = mutable_employee / "docs" / "decisions" / "index.md"
    index.write_text(
        index.read_text() + "| [0002](0002-reference-pages-later.md) | Reference pages later |\n"
    )
    future = (date.today() + timedelta(days=90)).isoformat()
    with (mutable_employee / "estatuto.toml").open("a") as handle:
        handle.write(
            f'\n[[exception]]\ncontrol = "E-3.1"\ndecision = "docs/decisions/0002-reference-pages-later.md"\nsunset = {future}\nreason = "Reference pages arrive with the first real capability."\n'
        )
        handle.write(
            f'\n[[exception]]\ncontrol = "E-7.4"\ndecision = "docs/decisions/0002-reference-pages-later.md"\nsunset = {future}\nreason = "Same."\n'
        )
    result = run_gate(mutable_employee)
    waived = {item.control_id for item in result.controls if item.status == "waived"}
    assert waived == {"E-3.1", "E-7.4"} and result.passed


def test_an_expired_exception_does_not_waive_and_is_itself_a_finding(
    mutable_employee: Path,
) -> None:
    (mutable_employee / "docs" / "reference" / "cli.md").unlink()
    (mutable_employee / "docs" / "reference" / "contracts.md").unlink()
    with (mutable_employee / "estatuto.toml").open("a") as handle:
        handle.write(
            '\n[[exception]]\ncontrol = "E-3.1"\ndecision = "docs/decisions/0001-adopt-the-estatuto.md"\nsunset = 2020-01-01\nreason = "Expired."\n'
        )
    broken = failures(mutable_employee)
    assert "E-3.1" in broken and any("expired" in finding for finding in broken["E-8.1"])


def test_the_declaration_rejects_a_malformed_persona(mutable_employee: Path) -> None:
    path = mutable_employee / "estatuto.toml"
    path.write_text(path.read_text().replace('name = "El Archivero"', 'name = "archivero"'))
    with pytest.raises(ConfigError, match="name"):
        load_config(mutable_employee)
