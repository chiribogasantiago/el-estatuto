"""The command line: honest exit codes for every command."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from estatuto.cli import main
from estatuto.version import STANDARD_VERSION

ROOT = Path(__file__).resolve().parents[1]


def test_render_check_is_clean_on_a_current_tree(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["render", "--check"]) == 0
    assert '"would change": []' in capsys.readouterr().out


def test_version_flag_reports_the_single_source(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exit_info:
        main(["--version"])
    assert exit_info.value.code == 0 and STANDARD_VERSION in capsys.readouterr().out


def test_gate_passes_on_a_scaffolded_employee_and_writes_the_document(
    employee: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    output = tmp_path / "gate.json"
    assert main(["gate", str(employee), "--output", str(output)]) == 0
    assert "PASS" in capsys.readouterr().out
    assert json.loads(output.read_text())["gate_passed"] is True


def test_gate_fails_on_a_broken_employee(
    mutable_employee: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    (mutable_employee / "README.md").unlink()
    assert main(["gate", str(mutable_employee)]) == 1
    assert "missing README.md" in capsys.readouterr().out


def test_gate_refuses_a_repository_without_a_declaration(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert main(["gate", str(tmp_path)]) == 2
    assert "estatuto.toml" in capsys.readouterr().err


def test_changelog_gate_skips_an_unknown_base(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["changelog-gate", "--base", "0000000", "--root", str(ROOT)]) == 0
    assert "skipped" in capsys.readouterr().out


def test_changelog_gate_refuses_a_root_without_a_declaration(tmp_path: Path) -> None:
    assert main(["changelog-gate", "--base", "HEAD~1", "--root", str(tmp_path)]) == 2


def test_sync_peg_vendors_every_schema(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["sync-peg", str(tmp_path)]) == 0
    vendored = json.loads(capsys.readouterr().out)["vendored"]
    assert "manifest-v1.0.0.json" in vendored and len(vendored) == 11
    assert (tmp_path / "contracts" / "peg" / "result-v1.0.0.json").is_file()


def test_new_employee_creates_and_refuses_twice(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    destination = tmp_path / "cronista"
    assert (
        main(
            [
                "new-employee",
                str(destination),
                "--name",
                "La Cronista",
                "--slug",
                "cronista",
                "--no-lock",
            ]
        )
        == 0
    )
    assert "created La Cronista" in capsys.readouterr().out
    assert (
        main(
            [
                "new-employee",
                str(destination),
                "--name",
                "La Cronista",
                "--slug",
                "cronista",
                "--no-lock",
            ]
        )
        == 2
    )
    assert "empty" in capsys.readouterr().err
