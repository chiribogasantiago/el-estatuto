"""The changelog gate: normative changes record themselves; tooling may change alone."""

from __future__ import annotations

from estatuto.changelog import is_normative, verdict
from estatuto.gate.config import FrameworkConfig

CONFIG = FrameworkConfig(
    name="El Archivero", slug="archivero", role="employee", package="archivero", standard="1.0.0"
)


def test_normative_paths_are_the_declared_prefixes_and_files() -> None:
    assert is_normative("src/archivero/peg.py", CONFIG)
    assert is_normative("manifest.json", CONFIG)
    assert not is_normative(".github/workflows/ci.yml", CONFIG)
    assert not is_normative("uv.lock", CONFIG)


def test_a_normative_change_without_a_changelog_entry_fails() -> None:
    passed, message = verdict(["src/archivero/peg.py"], CONFIG)
    assert not passed and "Unreleased" in message


def test_a_recorded_normative_change_and_a_tooling_change_pass() -> None:
    assert verdict(["src/archivero/peg.py", "CHANGELOG.md"], CONFIG)[0]
    assert verdict([".github/workflows/ci.yml", "uv.lock"], CONFIG)[0]
