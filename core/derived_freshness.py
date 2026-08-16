"""Is a derived artifact still derived from the manifest that is on disk?

⚠⚠ **THE PROBLEM THIS SOLVES IS SILENCE.** `span_segments.csv` and `census_labels.csv` are derived
from `census_manifest.v7.csv`. If the manifest is revised, they do not fail, do not warn, and do not
change — **they keep serving answers about a manifest that no longer exists.** A wrong topology is
worse than a missing one, because a missing one is visible.

## ⚠ Detect and REFUSE, never auto-regenerate

Regenerating on read would hide the change: a surface that silently re-derived would give a reader
different numbers on two loads with nothing saying why, and derivation would happen inside a request
nobody asked to do work. **So the mismatch becomes a stated category** and a human runs the script.

## ⚠ Hashed on CONTENT, not on mtime

A file copied, checked out, or restored from a zip has a new mtime and identical content. `mtime`
would cry stale on a `git checkout` and stay quiet on an in-place edit that preserved it — **wrong
in both directions.** The sha256 of the bytes is the only claim worth storing.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Optional

#: The key every derived provenance file carries. ⚠ Named once, here, so a producer and a consumer
#: cannot disagree about the spelling — the drift F-027 is about.
SOURCE_HASH_KEY = "source_manifest_sha256"

#: ⚠ Distinct verdicts, because they need different actions. `FRESH` proceed; `STALE` re-run the
#: derivation; `UNSTAMPED` the artifact predates this check — **not the same as stale, and not the
#: same as fresh**; `ABSENT` nothing was derived at all.
FRESH = "fresh"
STALE = "derivation_stale"
UNSTAMPED = "derivation_unstamped"
ABSENT = "derivation_absent"


def file_sha256(path: Path) -> Optional[str]:
    """sha256 of a file's bytes, or `None` if it is not there. ⚠ Never raises on absence."""
    if not path.is_file():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stamp(manifest: Path, extra: Optional[dict] = None) -> dict:
    """The provenance block a derivation writes. ⚠ Records the NAME and the HASH.

    The name alone is not identity — *a filename is not an identity* — and the hash alone cannot
    tell a reader which file to look at.
    """
    return {"source_manifest": manifest.name,
            SOURCE_HASH_KEY: file_sha256(manifest),
            **(extra or {})}


def check(provenance_path: Path, manifest: Path) -> tuple[str, str]:
    """`(verdict, human sentence)` for one derived artifact. ⚠ Never raises, never guesses."""
    if not provenance_path.is_file():
        return ABSENT, (f"{provenance_path.name} is absent — nothing was derived, which is not the "
                        f"same as derived-and-empty")
    try:
        prov = json.loads(provenance_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        # ⚠ Unreadable is its own outcome. Treating it as fresh would trust a file we cannot read.
        return STALE, f"{provenance_path.name} is unreadable ({e.msg}) — treated as stale"

    recorded = prov.get(SOURCE_HASH_KEY)
    if not recorded:
        return UNSTAMPED, (f"{provenance_path.name} carries no {SOURCE_HASH_KEY} — it predates this "
                           f"check. ⚠ UNKNOWN freshness, which is not a pass and not a failure; "
                           f"re-run the derivation to stamp it")
    current = file_sha256(manifest)
    if current is None:
        return STALE, f"{manifest.name} is absent — a derivation cannot be checked against nothing"
    if recorded != current:
        return STALE, (f"derived from {manifest.name} @ {recorded[:12]}…, but the file on disk is "
                       f"@ {current[:12]}… — ⚠ RE-RUN THE DERIVATION. The numbers below describe a "
                       f"manifest that is no longer there.")
    return FRESH, f"derived from {manifest.name} @ {current[:12]}…"
