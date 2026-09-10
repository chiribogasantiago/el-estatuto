"""A JSON round trip changes nothing: direct and wire exchanges are identical."""

from __future__ import annotations

from __PACKAGE__.peg import PegEmployee
from __PACKAGE__.transports import DirectTransport, JsonBytesTransport
from tests.test_peg_wire import assignment


def test_direct_and_json_bytes_transports_agree() -> None:
    peg = PegEmployee()
    assert DirectTransport(peg).exchange(assignment()) == JsonBytesTransport(peg).exchange(
        assignment()
    )
