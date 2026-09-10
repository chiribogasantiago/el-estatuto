from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from estatuto.factory.scaffold import scaffold_employee

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="session")
def employee(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """One scaffolded employee shared by the session; tests copy it when they must mutate it."""
    destination = tmp_path_factory.mktemp("kits") / "archivero"
    scaffold_employee(destination, name="El Archivero", slug="archivero", lock=False)
    (destination / "uv.lock").write_text("# hermetic placeholder: tests never resolve packages\n")
    return destination


@pytest.fixture
def mutable_employee(employee: Path, tmp_path: Path) -> Path:
    """A private copy a test may break."""
    copy = tmp_path / "archivero"
    shutil.copytree(employee, copy)
    return copy
