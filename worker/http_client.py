"""D-031 — the concrete HTTP ``QueueClient`` the worker loop drives.

This is the realization of the protocol ``worker/orchestrator.py`` defined by needing
it (D-030). It implements exactly the four methods, over the four routes, and does the
two pieces of transport work the loop deliberately left to it: it **gzips the PAE**
into the multipart body (D-031 PAE ruling — compression is client-side work, not a
route concern) and it maps **every** non-2xx response and connection failure to
``TransportError``, the loop's already-proven retry signal (D-030 §4). The loop's tests
do not change; if they had to, this client would be implementing the protocol wrongly.

Runtime dependency: ``httpx`` (worker/requirements.txt — the GPU tier is outside the
root lock, D-018). Importable on the CI gate too (httpx is in requirements-dev.lock),
which is why the client's tests run there without a GPU.
"""

from __future__ import annotations

import gzip
import json
from dataclasses import asdict
from typing import Any, Optional

import httpx

from worker.orchestrator import FoldSpec, TransportError


class HttpQueueClient:
    """A ``QueueClient`` over HTTP to the Fly transport. One shared bearer token on
    every call (D-031 §4); ``worker_id`` is a label carried in the claim body, not a
    credential."""

    def __init__(self, base_url: str, token: str, *, client: Optional[httpx.Client] = None) -> None:
        self._client = client or httpx.Client(base_url=base_url)
        self._headers = {"Authorization": f"Bearer {token}"}

    # ── the four QueueClient methods ─────────────────────────────────────────

    def claim(self, worker_id: str) -> Optional[FoldSpec]:
        """POST /jobs/claim → the inline FoldSpec, or ``None`` on 204 (empty queue)."""
        r = self._post("/jobs/claim", json={"worker_id": worker_id}, ok=(200, 204))
        if r.status_code == 204:
            return None
        return FoldSpec(**r.json())

    def upload(self, job_id: int, artifacts: Any) -> None:
        """POST /jobs/{id}/artifacts as multipart. Serializes the FoldResult: pdb text,
        plddt json, provenance json, and — when present — the PAE gzipped here."""
        files: dict[str, tuple[str, Any, str]] = {
            "pdb": ("structure.pdb", artifacts.pdb, "text/plain"),
            "plddt": ("plddt.json", json.dumps(artifacts.plddt), "application/json"),
            "provenance": ("provenance.json",
                           json.dumps(asdict(artifacts.provenance) if artifacts.provenance else {}),
                           "application/json"),
        }
        if artifacts.pae is not None:
            files["pae"] = ("pae.json.gz",
                            gzip.compress(json.dumps(artifacts.pae).encode("utf-8")),
                            "application/gzip")
        self._post(f"/jobs/{job_id}/artifacts", files=files, ok=(204,))

    def complete(self, job_id: int) -> None:
        """POST /jobs/{id}/complete — ONLY after ``upload`` landed (the loop guarantees
        the ordering; the endpoint enforces it, D-031 (c))."""
        self._post(f"/jobs/{job_id}/complete", ok=(204,))

    def fail(self, job_id: int, error: str) -> None:
        """POST /jobs/{id}/fail — terminal."""
        self._post(f"/jobs/{job_id}/fail", json={"error": error}, ok=(204,))

    # ── the single transport-error boundary ──────────────────────────────────

    def _post(self, path: str, *, json: Any = None, files: Any = None,
              ok: tuple[int, ...]) -> httpx.Response:
        """POST with the bearer token; any connection failure or unexpected status
        becomes ``TransportError``, so the loop's failure taxonomy (D-030 §4) works
        unchanged across the real transport."""
        try:
            r = self._client.post(path, json=json, files=files, headers=self._headers)
        except httpx.HTTPError as e:                       # connect/read/timeout → retryable
            raise TransportError(f"POST {path} failed: {e}") from e
        if r.status_code not in ok:
            raise TransportError(f"POST {path} -> {r.status_code}")
        return r
