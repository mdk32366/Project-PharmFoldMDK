#!/usr/bin/env python3
"""Mark the LIVE campaign cluster, once, so `D-159` can tell it from the forensic one.

    python scripts/keel_mark_live_cluster.py --check                 # reports, writes NOTHING
    python scripts/keel_mark_live_cluster.py --i-am-the-owner        # writes the marker

⚠⚠ **THIS IS A PRODUCTION WRITE AND IT REQUIRES THE OWNER AT THE KEYBOARD.** It is the one write in
the 2026-09-15 wave, it happens once, and it is a single row in a table nothing else reads.

⚠ **Why it has to exist at all.** `D-159` refuses an enqueue unless the target proves it is the live
campaign database. The proof is this marker. **Until it is written, every enqueue is refused** —
which is the correct direction for a guard to fail, and the reason this bootstrap ships with the
entry rather than being discovered later as a missing step.

⚠⚠ **RUN IT AGAINST THE LIVE CLUSTER ONLY.** `kyzl60xz9zyrpj9g` is the live cluster, restored
2026-09-14. `zp2wjrej9lwodn4q` is the **forensic record of the 2026-09-13 truncation** — do not mark
it, do not write to it, do not destroy it. This script refuses to mark any target whose census
population is missing, and prints the cluster it believes it is talking to before it does anything.

⚠ It cannot verify the cluster *id* independently: a tunnel does not tell you which cluster it
reaches, which is the whole problem this marker solves. **The operator's confirmation IS the
evidence**, and that is why the flag is `--i-am-the-owner` and not a default.
"""
from __future__ import annotations

import argparse
import os
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from core.db_identity import (                                   # noqa: E402
    ANCHOR_ACCESSION,
    CENSUS_FLOOR,
    FORENSIC_CLUSTER_ID,
    LIVE_CLUSTER_ID,
    LIVE_MARKER_TABLE,
    read_identity,
)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--url", default=os.environ.get("DATABASE_URL", ""))
    ap.add_argument("--check", action="store_true", help="report only; write nothing")
    ap.add_argument("--i-am-the-owner", dest="owner", action="store_true")
    args = ap.parse_args(argv)

    if not args.url:
        print("refusing: no DATABASE_URL and no --url.", file=sys.stderr)
        return 2

    from sqlalchemy import create_engine, text                   # noqa: PLC0415

    from db.dburl import normalize_db_url                        # noqa: PLC0415

    engine = create_engine(normalize_db_url(args.url), future=True,
                           connect_args={"connect_timeout": 10})
    try:
        with engine.connect() as conn:
            ident = read_identity(conn)
        print(f"marker       : {ident.live_cluster or 'ABSENT'}")
        print(f"census rows  : {ident.census_rows}  (floor {CENSUS_FLOOR})")
        print(f"anchor {ANCHOR_ACCESSION}: {'present' if ident.anchor_present else 'ABSENT'}")

        if ident.live_cluster == LIVE_CLUSTER_ID:
            print("\nalready marked as the live cluster; nothing to do.")
            return 0
        if ident.live_cluster == FORENSIC_CLUSTER_ID:
            print(f"\nREFUSING: this target is marked {FORENSIC_CLUSTER_ID!r} - the FORENSIC "
                  f"cluster. Do not write to it.", file=sys.stderr)
            return 1
        if ident.live_cluster is not None:
            print(f"\nREFUSING: already marked {ident.live_cluster!r}, which is neither the live "
                  f"nor the forensic cluster. Resolve that before writing.", file=sys.stderr)
            return 1

        # ⚠ The population check is a SECOND opinion, not the guard. It cannot tell the live
        # cluster from the forensic one - that is exactly what the marker is for - but it does
        # catch a fresh or truncated database, which is the other way this goes wrong.
        if ident.census_rows < CENSUS_FLOOR or not ident.anchor_present:
            print(f"\nREFUSING: {ident.census_rows} census rows and anchor "
                  f"{'present' if ident.anchor_present else 'ABSENT'}. This does not look like the "
                  f"restored campaign database at all. Reconcile before marking anything.",
                  file=sys.stderr)
            return 1

        if args.check:
            print("\n--check: nothing was written. Re-run with --i-am-the-owner to mark.")
            return 1
        if not args.owner:
            print("\nDRY RUN - nothing written. This is a PRODUCTION WRITE; re-run with "
                  "--i-am-the-owner, and be certain this tunnel reaches "
                  f"{LIVE_CLUSTER_ID!r} and not {FORENSIC_CLUSTER_ID!r}.")
            return 0

        with engine.begin() as conn:
            conn.execute(text(
                f"CREATE TABLE IF NOT EXISTS {LIVE_MARKER_TABLE} ("
                f"  cluster_id text PRIMARY KEY,"
                f"  marked_at timestamptz NOT NULL DEFAULT now())"))
            conn.execute(text(
                f"INSERT INTO {LIVE_MARKER_TABLE} (cluster_id) VALUES (:c) "
                f"ON CONFLICT DO NOTHING"), {"c": LIVE_CLUSTER_ID})
        print(f"\nmarked: this cluster now identifies itself as {LIVE_CLUSTER_ID!r}.")
        print("enqueues are no longer refused on identity.")
        return 0
    finally:
        engine.dispose()


if __name__ == "__main__":
    raise SystemExit(main())
