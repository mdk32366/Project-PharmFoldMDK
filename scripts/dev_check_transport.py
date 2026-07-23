"""dev-up.ps1 helper: verify the worker's token against the LIVE transport before starting it.

A wrong WORKER_AUTH_TOKEN only surfaced as 401s in the Fly logs the first-fold night (the DB
password had been pasted as the token). This catches it before the worker starts: it POSTs
`/complete` for a job id that cannot exist. A wrong token returns 401 (fail); a good token
reaches the handler and returns 409 (no artifacts) — non-401, and with NO side effect, since the
job does not exist and `/complete` only flips a job that has persisted artifacts (D-031 §(c)).

Exit 0 if auth passes and the transport is reachable, 1 on 401 or unreachable — so the worker
never starts against an unverified transport. Uses stdlib urllib only (no runtime dep).
"""

from __future__ import annotations

import os
import sys
import urllib.error
import urllib.request

NONEXISTENT_JOB = 2_000_000_000  # far above any real job id — /complete on it is a no-op


def main() -> int:
    base = os.environ.get("TRANSPORT_URL", "https://pharmfoldmdk.fly.dev").rstrip("/")
    token = os.environ.get("WORKER_AUTH_TOKEN")
    if not token:
        print("[transport] no WORKER_AUTH_TOKEN in the environment")
        return 1

    req = urllib.request.Request(
        f"{base}/jobs/{NONEXISTENT_JOB}/complete",
        method="POST",
        headers={"Authorization": f"Bearer {token}"},
    )
    try:
        urllib.request.urlopen(req, timeout=15)
        print("[transport] auth OK")
        return 0
    except urllib.error.HTTPError as e:
        if e.code == 401:
            print("[transport] AUTH FAILED (401) - WORKER_AUTH_TOKEN does not match the Fly secret")
            return 1
        print(f"[transport] auth OK (HTTP {e.code}, non-401)")
        return 0
    except Exception as e:  # noqa: BLE001 — connection/timeout = unreachable
        print(f"[transport] UNREACHABLE: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
