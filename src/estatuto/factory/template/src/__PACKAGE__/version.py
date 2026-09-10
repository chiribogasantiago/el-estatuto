"""Single source of the published employee version.

``pyproject.toml``, ``manifest.json`` and ``CHANGELOG.md`` must agree with ``EMPLOYEE_VERSION``;
conformance and the release-discipline test fail when they drift.
"""

from __future__ import annotations

EMPLOYEE_VERSION = "0.1.0"
