#!/usr/bin/env python3
"""Build a gitignored repo snapshot: tracked files + the census artifacts.

    python scripts/make_snapshot.py

⚠⚠ **IT REFUSES TO WRITE A ZIP CONTAINING `.env`.** That file holds the production database
password. The check is an **assertion over the assembled name list**, made *before* the archive is
written — not a filter that is assumed to have worked. **A secret excluded by a pattern nobody
verified is a secret one typo from being shipped.**

**What goes in:** every file `git ls-files` reports at HEAD, plus `data/census/*.csv` and
`*.provenance.json` — the **measured outputs**.

⚠ **What stays out, and why each is deliberate:**
  · `.env` — ⚠ the production password
  · `data/census/spancache/` — 5,009 cached UniProt entries, regenerable from the network
  · `.venv`, `node_modules`, `ui/dist`, `__pycache__` — rebuildable
  · the ESMFold weights — 8.4 GB, and pinned by revision in `worker/runner.py` anyway

⚠ **The manifest of what was included is written INTO the zip**, so a later reader can tell what a
snapshot is missing without diffing it against a repo they may not have.
"""

from __future__ import annotations

import hashlib
import subprocess
import sys
import zipfile
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

#: ⚠ Checked by ASSERTION over the final list, never by trusting a glob.
FORBIDDEN = (".env",)

EXCLUDE_DIRS = ("data/census/spancache/", ".venv/", "node_modules/", "ui/dist/", "__pycache__/")


def tracked_files() -> list[str]:
    out = subprocess.run(["git", "ls-files"], cwd=REPO, capture_output=True, text=True, check=True)
    return [l for l in out.stdout.splitlines() if l.strip()]


def census_artifacts() -> list[str]:
    """The measured outputs — CSVs and provenance, NOT the raw cache."""
    base = REPO / "data" / "census"
    found = []
    for p in sorted(list(base.glob("*.csv")) + list(base.glob("*.provenance.json"))
                    + list(base.glob("*.jsonl")) + list(base.glob("*.json"))):
        found.append(p.relative_to(REPO).as_posix())
    return found


def force_utf8_output() -> None:
    """⚠ The console is cp1252 on Windows, and every line this script prints carries a ⚠.

    Without this, the *reporting* dies on the character while the archive it is reporting on is
    already written — the script exits 1 with a UnicodeEncodeError and a caller that checks the
    status code concludes the snapshot failed when it did not.

    ⚠⚠ **The sharper case is the refusal path.** `main` prints the `.env` refusal to stderr, and
    that message also carries ⚠. On a real leak the operator would get a traceback about a character
    instead of the sentence naming the production database password. It still fails closed — nothing
    is written and the status is nonzero — but **a safety message that cannot be printed is not a
    safety message.** Both streams are reconfigured, not just stdout.
    """
    for stream in (sys.stdout, sys.stderr):
        # Guard: a redirected stream need not be a TextIOWrapper.
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")


def main() -> int:
    force_utf8_output()
    names = sorted(set(tracked_files()) | set(census_artifacts()))
    names = [n for n in names if not any(n.startswith(d) for d in EXCLUDE_DIRS)]

    # ⚠⚠ THE ASSERTION, BEFORE ANYTHING IS WRITTEN.
    leaked = [n for n in names if Path(n).name in FORBIDDEN or n in FORBIDDEN]
    if leaked:
        print(f"⚠⚠ REFUSING TO WRITE: the file list contains {leaked} — that is the production "
              f"database password. Nothing was written.", file=sys.stderr)
        return 1

    existing = [n for n in names if (REPO / n).is_file()]
    missing = [n for n in names if not (REPO / n).is_file()]

    out = REPO / f"PharmFoldMDK-snapshot-{date.today().isoformat()}.zip"
    head = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=REPO,
                          capture_output=True, text=True, check=True).stdout.strip()
    dirty = subprocess.run(["git", "status", "--porcelain"], cwd=REPO,
                           capture_output=True, text=True, check=True).stdout.strip()

    manifest = [
        f"PharmFoldMDK snapshot — {date.today().isoformat()}",
        f"HEAD: {head}",
        f"working tree: {'DIRTY — this snapshot is NOT a commit' if dirty else 'clean'}",
        f"files: {len(existing)}",
        "",
        "⚠ DELIBERATELY EXCLUDED, and none of it is recoverable from this zip:",
        "  .env                       the production database password",
        "  data/census/spancache/     5,009 cached UniProt entries (re-fetchable)",
        "  .venv, node_modules, ui/dist, __pycache__   rebuildable",
        "  ESMFold weights            8.4 GB; pinned by revision in worker/runner.py",
        "",
        "⚠ A snapshot is not a backup of the database. protein_analyses, jobs and every fold",
        "  artifact live in production and on the Fly volume, not here.",
        "",
    ]
    if missing:
        manifest += ["⚠ listed but absent from disk at build time:"] + [f"  {m}" for m in missing]

    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("SNAPSHOT_MANIFEST.txt", "\n".join(manifest))
        for n in existing:
            z.write(REPO / n, n)

    # ⚠ Verify by READING THE ARCHIVE BACK, not by trusting the loop that wrote it.
    with zipfile.ZipFile(out) as z:
        inside = z.namelist()
    back_leaked = [n for n in inside if Path(n).name in FORBIDDEN]
    if back_leaked:
        out.unlink()
        print(f"⚠⚠ {back_leaked} FOUND INSIDE THE ARCHIVE — deleted. Report and stop.", file=sys.stderr)
        return 1

    sha = hashlib.sha256(out.read_bytes()).hexdigest()
    print(f"wrote {out.name}")
    print(f"  files    | {len(inside)} (incl. SNAPSHOT_MANIFEST.txt)")
    print(f"  size     | {out.stat().st_size / 2**20:.1f} MiB")
    print(f"  sha256   | {sha}")
    print(f"  HEAD     | {head} | working tree {'DIRTY' if dirty else 'clean'}")
    print(f"  ⚠ .env inside | {any(Path(n).name == '.env' for n in inside)}  (verified by reading "
          f"the archive back)")
    print(f"  ⚠ spancache inside | {any('spancache' in n for n in inside)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
