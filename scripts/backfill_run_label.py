#!/usr/bin/env python3
"""AMENDMENT 2 §3.1 — stamp ``run: 1`` onto every existing ``jobs.inference_settings``.

    python scripts/backfill_run_label.py --dry-run      # ⚠ ALWAYS FIRST — reports, writes nothing
    python scripts/backfill_run_label.py --i-am-the-owner

⚠⚠ **THIS IS AN EXPRESS EXCEPTION TO TASK §4.2** (*no original row is updated, deleted, or
re-pointed*), granted by the owner **by name, with its scope**, and it authorises nothing else.
§4.2 exists precisely so that nobody has to reason about whether a given write is safe; **an
exception granted once is an exception**, not a precedent.

**Why it cannot move `D-075`'s anchor:** it touches no ``pdb_path``, no ``pae_json_path``, no
score, no ``ranking_run_id``, nothing scientific. It adds one key naming a generation.

**Why at all.** Run 2 needs to declare its generation, and a NEW key would be present on **0 of
3,656** existing rows — so Run 1 would be identified by the **absence** of a key. That is
`F-018`'s class (*the absent-value rule violated in the passing direction*), and it is NOT
`D-095` decision 4's pattern: dec 4 went additive because ``boundary_method`` was **present and
monovalued**, so *every existing row already declared itself*. This backfill restores exactly that
property.

**BOUNDS, AND THEY BIND:**
  * the key ``run`` ONLY; value ``1``; ``jobs.inference_settings`` ONLY
  * no other column, no other table, no other row
  * idempotent — a row that already carries ``run`` is left untouched
  * ⚠ **does NOT ride along with any other change**

⚠ `A-030` is the assumption under this script — *a JSONB column can take an additive key without
changing any consumer* — registered **ASSUMED and untested** in `docs/assumptions.md` before this
ran. **This script's guard is what decides whether it becomes HELD or BROKE.**

⚠⚠ **PRODUCTION WRITE. OWNER AT THE KEYBOARD.** There is no default that writes.
"""

from __future__ import annotations

import argparse
import os
import sys
from typing import Any, Optional

RUN_KEY = "run"
RUN_1 = 1


def with_run_label(settings: Optional[dict], run: int = RUN_1) -> dict:
    """Return ``settings`` plus ``{"run": run}``, changing nothing else.

    ⚠ **Idempotent and non-clobbering**: a row already carrying ``run`` is returned unchanged, so
    a re-run after a partial cannot rewrite a generation label that a later Run already set.
    ⚠ A NULL/absent settings dict becomes ``{"run": run}`` rather than raising — there are none in
    production (3,656 of 3,656 populated, measured), and inventing a failure for a case that does
    not exist would be the guard failing in the direction nobody checks.
    """
    current = dict(settings or {})
    if RUN_KEY in current:
        return current
    current[RUN_KEY] = run
    return current


def plan(rows: list[tuple[int, Optional[dict]]], run: int = RUN_1) -> dict[str, Any]:
    """Pure: what the backfill WOULD do to these ``(job_id, inference_settings)`` rows.

    Separated from the session so the guard can assert the decision without a database — and so
    the dry run reports the same object the write applies, never a second implementation of it.
    """
    already = [jid for jid, s in rows if (s or {}).get(RUN_KEY) is not None]
    todo = [(jid, with_run_label(s, run)) for jid, s in rows if (s or {}).get(RUN_KEY) is None]
    return {"total": len(rows), "already_labelled": len(already), "to_write": len(todo),
            "writes": todo}


def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(prog="python scripts/backfill_run_label.py", description=__doc__)
    ap.add_argument("--dry-run", action="store_true",
                    help="⚠ compose and CHECK everything, write nothing")
    ap.add_argument("--i-am-the-owner", action="store_true",
                    help="⚠⚠ required to write. A production write needs the owner at the keyboard.")
    ap.add_argument("--run", type=int, default=RUN_1, help="the generation label (default 1)")
    args = ap.parse_args(argv)

    if not args.dry_run and not args.i_am_the_owner:
        print("refusing: pass --dry-run to report, or --i-am-the-owner deliberately.",
              file=sys.stderr)
        return 2

    from sqlalchemy import create_engine, select        # noqa: PLC0415 — kept off the import path
    from sqlalchemy.orm import Session

    sys.path.insert(0, os.getcwd())
    from db.models import JobRecord                     # noqa: PLC0415

    url = os.environ["DATABASE_URL"].replace("postgresql+psycopg://", "postgresql://")
    engine = create_engine(url)

    with Session(engine) as s:
        rows = [(j.id, j.inference_settings) for j in s.scalars(select(JobRecord)).all()]
        before = plan(rows, args.run)
        print(f"BEFORE | total={before['total']} already_labelled={before['already_labelled']} "
              f"to_write={before['to_write']}")

        if args.dry_run:
            # ASCII only in printed strings: this runs in a console whose codepage nobody
            # controls, and a non-ASCII glyph raises UnicodeEncodeError on cp1252/cp437 and
            # kills the script mid-report. The same rule worker/main.py's banners already carry.
            print("\n[DRY RUN] nothing written.")
            return 0

        by_id = dict(before["writes"])
        for job in s.scalars(select(JobRecord)).all():
            if job.id in by_id:
                job.inference_settings = by_id[job.id]
        s.commit()

        after_rows = [(j.id, j.inference_settings) for j in s.scalars(select(JobRecord)).all()]

    after = plan(after_rows, args.run)
    print(f"AFTER  | total={after['total']} already_labelled={after['already_labelled']} "
          f"to_write={after['to_write']}")

    # ⚠ The falsifiers, checked against the pre-registration rather than eyeballed.
    problems = []
    if after["total"] != before["total"]:
        problems.append(f"row count MOVED: {before['total']} -> {after['total']}")
    if after["to_write"] != 0:
        problems.append(f"{after['to_write']} rows still carry no {RUN_KEY!r} — the partition would "
                        f"be the absence-based one this backfill exists to avoid")
    if after["already_labelled"] != before["total"]:
        problems.append(f"{RUN_KEY!r} is on {after['already_labelled']} of {before['total']}, "
                        f"not all of them")
    if problems:
        for p in problems:
            print(f"  [PROBLEM] {p}", file=sys.stderr)
        return 1

    print(f"\n[OK] {RUN_KEY}={args.run} on {after['already_labelled']} of {before['total']} rows.")
    return 0


if __name__ == "__main__":  # pragma: no cover — the owner entry
    sys.exit(main())
