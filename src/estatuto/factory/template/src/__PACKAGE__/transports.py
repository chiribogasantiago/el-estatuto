"""Transports carry a protocol document across a boundary without touching the method.

``DirectTransport`` is the baseline; ``JsonBytesTransport`` proves a JSON round trip changes
nothing; ``HttpServer`` offers the protocol's three routes. All three return identical documents
for identical assignments — a test enforces it.
"""

from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, cast

from __PACKAGE__.peg import PegEmployee

ASSIGNMENTS = "/peg/v1/assignments"
MANIFEST = "/peg/v1/manifest"
HEALTH = "/peg/v1/health"
MAX_BODY_BYTES = 1_048_576


class DirectTransport:
    """Pass the document straight to the adapter."""

    def __init__(self, peg: PegEmployee) -> None:
        self.peg = peg

    def exchange(self, document: dict[str, Any]) -> tuple[int, dict[str, Any]]:
        """Execute in process and return the status and document unchanged."""
        return self.peg.handle(document)


class JsonBytesTransport:
    """Serialize the document and the answer through JSON bytes before and after execution."""

    def __init__(self, peg: PegEmployee) -> None:
        self.peg = peg

    def exchange(self, document: dict[str, Any]) -> tuple[int, dict[str, Any]]:
        """Round-trip both ways through JSON bytes; the result must equal the direct exchange."""
        wire = json.dumps(document, sort_keys=True).encode()
        status, answer = self.peg.handle(json.loads(wire))
        return status, cast(dict[str, Any], json.loads(json.dumps(answer, sort_keys=True)))


def _handler(peg: PegEmployee) -> type[BaseHTTPRequestHandler]:
    class Handler(BaseHTTPRequestHandler):
        server_version = "__SLUG__/peg1"

        def _send(self, status: int, document: dict[str, Any]) -> None:
            body = json.dumps(document, ensure_ascii=False).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self) -> None:  # noqa: N802 - http.server API
            if self.path == MANIFEST:
                self._send(200, peg.manifest)
            elif self.path == HEALTH:
                self._send(200, peg.health_report())
            else:
                self._send(404, {"error": "not found"})

        def do_POST(self) -> None:  # noqa: N802 - http.server API
            if self.path != ASSIGNMENTS:
                self._send(404, {"error": "not found"})
                return
            length = int(self.headers.get("Content-Length", "0"))
            if length > MAX_BODY_BYTES:
                self._send(413, {"error": "payload too large"})
                return
            try:
                document = json.loads(self.rfile.read(length))
            except json.JSONDecodeError:
                status, refusal = peg.refusal("unknown", "CONTRACT_INVALID", ["body is not JSON"])
                self._send(status, refusal)
                return
            if not isinstance(document, dict):
                status, refusal = peg.refusal(
                    "unknown", "CONTRACT_INVALID", ["body is not an object"]
                )
                self._send(status, refusal)
                return
            status, answer = peg.handle(document)
            self._send(status, answer)

        def log_message(self, format: str, *args: Any) -> None:  # noqa: A002 - http.server API
            return

    return Handler


class HttpServer:
    """The protocol over HTTP: ``POST /peg/v1/assignments``, ``GET /peg/v1/manifest``, ``GET /peg/v1/health``."""

    def __init__(self, peg: PegEmployee, host: str = "127.0.0.1", port: int = 0) -> None:
        self._server = ThreadingHTTPServer((host, port), _handler(peg))
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._serving = False

    def _run(self) -> None:
        self._serving = True
        try:
            self._server.serve_forever()
        finally:
            self._serving = False

    @property
    def port(self) -> int:
        """The bound port (useful when started on 0)."""
        return int(self._server.server_address[1])

    @property
    def base_url(self) -> str:
        """``http://host:port``."""
        host = str(self._server.server_address[0])
        return f"http://{host}:{self.port}"

    def start(self) -> HttpServer:
        """Serve in a daemon thread and return self."""
        self._thread.start()
        return self

    def stop(self) -> None:
        """Stop serving and release the port.

        ``shutdown`` waits for the serving loop to acknowledge; when the loop never started —
        a failed start, an interrupt before the first request — waiting would block forever, so
        it is only called while the loop is running.
        """
        if self._serving:
            self._server.shutdown()
        self._server.server_close()

    def serve_forever(self) -> None:
        """Block serving requests (the CLI's ``serve``)."""
        self._run()


__all__ = [
    "ASSIGNMENTS",
    "HEALTH",
    "MANIFEST",
    "DirectTransport",
    "HttpServer",
    "JsonBytesTransport",
]
