"""One version everywhere, a changelog that records it, gates that name real tests."""

from __future__ import annotations

import ast
import json
import re
import tomllib
from pathlib import Path

from __PACKAGE__.version import EMPLOYEE_VERSION

ROOT = Path(__file__).resolve().parents[1]


def test_one_version_everywhere_and_recorded_in_the_changelog() -> None:
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text())
    manifest = json.loads((ROOT / "manifest.json").read_text())
    changelog = (ROOT / "CHANGELOG.md").read_text()
    assert pyproject["project"]["version"] == EMPLOYEE_VERSION
    assert manifest["employee_version"] == EMPLOYEE_VERSION
    assert "\n## Unreleased\n" in changelog
    assert re.search(
        rf"^## {re.escape(EMPLOYEE_VERSION)} — \d{{4}}-\d{{2}}-\d{{2}}$", changelog, re.M
    )


def test_every_gate_corpus_names_tests_that_exist() -> None:
    for corpus in sorted((ROOT / "gates").glob("*-gate-v*.json")):
        document = json.loads(corpus.read_text())
        assert document["required_score"] == len(document["cases"])
        for case in document["cases"]:
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
