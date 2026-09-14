#!/usr/bin/env python3
"""Mark a database DISPOSABLE so the test suite will run against it (KEEL V8-a / `D-158`).

    python scripts/keel_mark_disposable.py                 # marks $DATABASE_URL
    python scripts/keel_mark_disposable.py --check         # reports, writes nothing
    python scripts/keel_mark_disposable.py --url postgresql://...

⚠⚠ **RUN THIS ONLY AGAINST A DATABASE WHOSE DATA YOU ARE WILLING TO LOSE.** The marker it creates
is the single thing standing between `tests/conftest.py`'s `TRUNCATE … CASCADE` and the target.
Marking production would hand the suite the database it has already destroyed twice —
**2026-08-17** (2,771 rows) and **2026-09-13** (4,535 rows).

⚠ **This is NOT a migration and must never become one.** `tests/test_d158_positive_identity_guard.py`
asserts that no file under `db/migrations/` mentions the marker, because a migration would put it
into production on the next `alembic upgrade head` and **invert the guard silently** — it would then
permit precisely what it exists to refuse. The marker's absence from the schema chain is the
assumption registered as `A-031`.

⚠ The refusal below is deliberately NOT overridable. A bootstrap that argues with you about whether
you meant it is a bootstrap you learn to run with your eyes closed; this one simply refuses a target
that looks populated, and a genuinely fresh test database sails through.
"""
from __future__ import annotations

import argparse
import os
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "tests"))

from _db_safety import MARKER_TABLE, db_host, db_name          # noqa: E402

#: ⚠ A populated target is not a test database. This is a SECOND opinion, not the guard: the guard
#: asks whether the marker is present, and this asks whether creating one would be insane.
POPULATED_AT = 100


def _engine(url: str):
    from sqlalchemy import create_engine                       # noqa: PLC0415

    from db.dburl import normalize_db_url                      # noqa: PLC0415
    return create_engine(normalize_db_url(url), future=True,
                         connect_args={"connect_timeout": 5})


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--url", default=os.environ.get("DATABASE_URL", ""))
    ap.add_argument("--check", action="store_true", help="report only; write nothing")
    args = ap.parse_args(argv)

    if not args.url:
        print("refusing: no DATABASE_URL and no --url. Nothing to mark.", file=sys.stderr)
        return 2

    from sqlalchemy import text                                # noqa: PLC0415

    host, name = db_host(args.url) or "<unparseable>", db_name(args.url) or "<unparseable>"
    print(f"target: {name!r} on host {host!r}")

    engine = _engine(args.url)
    try:
        with engine.connect() as conn:
            present = conn.execute(
                text("SELECT to_regclass(:m)"), {"m": MARKER_TABLE}).scalar() is not None
            print(f"marker {MARKER_TABLE!r}: {'present' if present else 'ABSENT'}")

            # ⚠ The population check reads the tables the suite TRUNCATEs. A target holding real
            # rows is the one case where marking it is the mistake this whole entry is about.
            rows = 0
            for table in ("protein_analyses", "jobs"):
                if conn.execute(text("SELECT to_regclass(:t)"), {"t": table}).scalar() is None:
                    continue
                rows += conn.execute(text(f"SELECT count(*) FROM {table}")).scalar() or 0
            print(f"rows across protein_analyses + jobs: {rows}")

            if args.check:
                print("\n--check: nothing was written.")
                return 0 if present else 1

            if present:
                print("\nalready marked; nothing to do.")
                return 0

            if rows >= POPULATED_AT:
                print(f"\nREFUSING: {rows} rows across the tables this suite TRUNCATEs. That is a "
                      f"populated database, not a throwaway one.\n"
                      f"  Marking it would arm `TRUNCATE jobs, protein_analyses, ranking_runs "
                      f"RESTART IDENTITY CASCADE` against every row above.\n"
                      f"  If this really is a scratch database, empty it first and re-run.",
                      file=sys.stderr)
                return 1

        with engine.begin() as conn:
            conn.execute(text(
                f"CREATE TABLE IF NOT EXISTS {MARKER_TABLE} ("
                f"  token text PRIMARY KEY,"
                f"  marked_at timestamptz NOT NULL DEFAULT now())"))
            conn.execute(text(
                f"INSERT INTO {MARKER_TABLE} (token) VALUES ('disposable') "
                f"ON CONFLICT DO NOTHING"))
        print(f"\nmarked: {name!r} on {host!r} now carries {MARKER_TABLE!r}.")
        print("the suite will run against it. it will also TRUNCATE it, every test.")
        return 0
    finally:
        engine.dispose()


if __name__ == "__main__":
    raise SystemExit(main())
