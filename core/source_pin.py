"""Source pinning: the provenance helpers every ingest needs, and NOTHING else.

⚠⚠ WHY THIS MODULE EXISTS, RECORDED BECAUSE IT WAS FOUND THE HARD WAY. These four lived in
`core/clinical_ingest.py`, which imports `scripts.kathad_reproduction` for the `D-100` grid
reproduction. The census feature ingest needed only `verify_source` and `IngestRefused` — and
importing them dragged in the whole clinical layer, and with it a `scripts/` module that is
deliberately NOT shipped in the serving image. It built fine and died on the production host at
`ModuleNotFoundError: No module named 'scripts.kathad_reproduction'`.

⚠ Nothing here is reimplemented — the functions are MOVED, verbatim, and `core.clinical_ingest`
re-exports them so every existing caller and test is untouched. *A second copy is a second source
with nothing comparing them.*

⚠ This module imports the standard library and nothing else, and that is its whole point: the
thing an ingest reaches for first must not be able to drag a tier's worth of code behind it.
"""

from __future__ import annotations

import hashlib
import pathlib


class IngestRefused(RuntimeError):
    """⚠⚠ Raised when the ingest may not commit. The caller MUST roll back.

    It is an exception rather than a returned `False` because a boolean invites a caller to log it
    and carry on — and *a failing check nobody is forced to obey is decoration* (Principle 9).
    """



def sha256_of(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def verify_source(path: pathlib.Path, expected_sha256: str) -> str:
    """⚠⚠ HARD ERROR, NEVER A SKIP — KEEL-1 V9 Principle 6's direction clause.

    An absent file and a hash mismatch are **different refusals with different messages**, because
    they are different facts: one is *the input is not here*, the other is *the input is not the one
    that was pinned*. ⚠ **A guard that returns quietly when its input is missing is the shape that
    armed the truncation** — *"you probably do not have a database"* is not a safety property.
    """
    if not path.exists():
        raise IngestRefused(
            f"source file {path} is ABSENT. The ingest refuses rather than proceeding with "
            f"whatever else is on disk — an absent input is not an empty one.")
    got = sha256_of(path)
    if got != expected_sha256:
        raise IngestRefused(
            f"source file {path} does not match its pinned sha256.\n"
            f"  pinned {expected_sha256}\n  actual {got}\n"
            f"⚠ This is a NEW ingest of a DIFFERENT file, not a re-run of the pinned one. "
            f"Re-pin deliberately or supply the pinned file; do not proceed.")
    return got


def is_noop_rerun(recorded_hashes: dict[str, str], current_hashes: dict[str, str]) -> bool:
    """`GC4` idempotency. ⚠ A second run against the SAME hashes is a no-op; against DIFFERENT
    hashes it is a new ingest and must say so rather than silently appending."""
    return bool(recorded_hashes) and recorded_hashes == current_hashes
