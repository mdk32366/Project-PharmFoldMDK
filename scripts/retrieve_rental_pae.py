"""D-036 — retrieve the rental tier's PAE off the pod to the Fly Volume before termination.

Walks ``WORKER_ARTIFACT_DIR`` for ``{job_id}/pae.json``, gzips each, and POSTs it to
``POST {TRANSPORT_URL}/jobs/{job_id}/pae`` with the shared bearer token. Committed, reproducible
code (D-009 §3's binding condition), **not** a shell one-liner.

⚠ **BLOCKING pre-termination step.** D-011 rules **no network volumes** — *"download weights,
fold, upload artifacts, terminate."* PAE on the pod's container disk is **destroyed on pod
termination**. The batch is **not** done when the last fold completes; it is done when this
reports every file transferred. ``main()`` **exits non-zero if any transfer failed**, so an
operator gating termination on the exit code never terminates on a partial. The failure is silent
and costs a paid re-fold.

Idempotent: the D-036 route converges server-side, so a re-run after a partial transfer simply
re-POSTs and settles. Run it, read the report, re-run until it is clean, *then* terminate.
"""

from __future__ import annotations

import gzip
import os
import sys
from pathlib import Path


def transfer_all(artifact_dir, *, post):
    """POST each ``{artifact_dir}/{job_id}/pae.json`` (gzipped) via ``post(job_id, gz) -> bool``.

    Returns ``{job_id: ok}``. Directories without a ``pae.json`` are skipped (a fold that emitted
    no PAE, or an already-cleaned dir). ``post`` is injected so the walk/gzip/report logic is
    hermetic; ``main`` wires the real HTTP POST."""
    results: dict[int, bool] = {}
    for job_dir in sorted(Path(artifact_dir).iterdir()):
        if not job_dir.is_dir():
            continue
        pae = job_dir / "pae.json"
        if not pae.is_file():
            continue
        job_id = int(job_dir.name)
        gz = gzip.compress(pae.read_bytes())
        results[job_id] = post(job_id, gz)
    return results


def _http_post(transport_url, token):
    """Build the real POST: the D-036 route, bearer token, explicit timeout (D-035 §3a)."""
    import httpx

    client = httpx.Client(
        base_url=transport_url,
        timeout=httpx.Timeout(connect=10.0, read=300.0, write=300.0, pool=10.0),
    )
    headers = {"Authorization": f"Bearer {token}"}

    def post(job_id, gz):
        r = client.post(f"/jobs/{job_id}/pae",
                        files={"pae": ("pae.json.gz", gz, "application/gzip")}, headers=headers)
        return r.status_code == 204

    return post


def main() -> int:
    artifact_dir = os.environ["WORKER_ARTIFACT_DIR"]
    transport_url = os.environ.get("TRANSPORT_URL", "https://pharmfoldmdk.fly.dev").rstrip("/")
    token = os.environ["WORKER_AUTH_TOKEN"]

    results = transfer_all(artifact_dir, post=_http_post(transport_url, token))
    failed = sorted(j for j, ok in results.items() if not ok)
    print(f"[pae] transferred {len(results) - len(failed)}/{len(results)}; failed: {failed}")
    if failed:
        print("[pae] ⚠ INCOMPLETE — do NOT terminate the pod; re-run after investigating.")
        return 1
    print("[pae] all PAE off the box and acknowledged — safe to terminate.")
    return 0


if __name__ == "__main__":  # pragma: no cover — the operator entry, run on the rented box
    sys.exit(main())
