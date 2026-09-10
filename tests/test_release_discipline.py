"""One version everywhere, recorded in the changelog; the gate corpus names real tests."""

from __future__ import annotations

import ast
import json
import re
import tomllib
from pathlib import Path

from estatuto.version import STANDARD_VERSION

ROOT = Path(__file__).resolve().parents[1]


def test_one_version_everywhere_and_recorded_in_the_changelog() -> None:
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text())
    changelog = (ROOT / "CHANGELOG.md").read_text()
    assert pyproject["project"]["version"] == STANDARD_VERSION
    assert "\n## Unreleased\n" in changelog
    assert re.search(
        rf"^## {re.escape(STANDARD_VERSION)} — \d{{4}}-\d{{2}}-\d{{2}}$", changelog, re.M
    )
    assert f'standard = "{STANDARD_VERSION}"' in (ROOT / "estatuto.toml").read_text()


def test_the_gate_corpus_names_tests_that_exist_and_covers_every_control() -> None:
    from estatuto.gate.runner import CONTROL_IDS

    document = json.loads((ROOT / "gates" / "framework-standard-gate-v1.0.0.json").read_text())
    assert document["required_score"] == len(document["cases"])
    covered: set[str] = set()
    for case in document["cases"]:
        covered.update(case["controls"])
        for nodeid in case["test_nodeids"]:
            path, _, name = nodeid.partition("::")
            source = ROOT / path
            assert source.is_file(), nodeid
            if name:
                defined = {
                    node.name
                    for node in ast.parse(source.read_text()).body
                    if isinstance(node, ast.FunctionDef)
                }
                assert name.split("[")[0] in defined, nodeid
    assert covered == CONTROL_IDS
