"""The command line reports honest exit codes and renders the publication."""

from __future__ import annotations

import pytest

from __PACKAGE__.cli import main
from __PACKAGE__.version import EMPLOYEE_VERSION


def test_render_check_passes_when_the_publication_is_current(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert main(["render", "--check"]) == 0
    assert '"would change": []' in capsys.readouterr().out


def test_version_flag_reports_the_single_source(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exit_info:
        main(["--version"])
    assert exit_info.value.code == 0
    assert EMPLOYEE_VERSION in capsys.readouterr().out


def test_a_missing_command_is_a_usage_error() -> None:
    with pytest.raises(SystemExit) as exit_info:
        main([])
    assert exit_info.value.code == 2
