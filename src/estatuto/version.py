"""Single source of the standard's version.

``pyproject.toml``, ``CHANGELOG.md`` and every rendered document must agree with
``STANDARD_VERSION``; the release-discipline test fails when they drift.
"""

from __future__ import annotations

STANDARD_VERSION = "1.0.0"
