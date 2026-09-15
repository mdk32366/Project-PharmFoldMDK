#!/usr/bin/env python3
"""F-078 order B — make slice 2's 37 lost rows unclaimable, and later make them claimable again.

    python scripts/f078_null_tier_the_37.py                      # DRY RUN, writes nothing
    python scripts/f078_null_tier_the_37.py --i-am-the-owner     # the two writes
    python scripts/f078_null_tier_the_37.py --restore            # DRY RUN of the debt payment
    python scripts/f078_null_tier_the_37.py --restore --i-am-the-owner

⚠⚠ **WHY THIS EXISTS.** `run_worker` claims the next job of its **TIER**, so only one bounded
population may be claimable at a time. Slice 3's 1,097 and slice 2's 37 lost rows are both
`pending`/`local`. Order B (owner ruling, 2026-09-15) makes the 37 unclaimable so slice 3 folds
first — **74 writes against order A's 2,194.**

⚠ **The mechanism is the documented one, not a new one.** `core/queue.py`'s claim is
`status = 'pending' AND tier = :tier`, **strict, never `OR tier IS NULL`** — so a NULL-tier job is
claimable by **nobody**, deliberately, which is how the three mucins are held. No new tier is
invented; `KNOWN_TIERS` is a `D-107` matter and this is not that.

⚠⚠ **THE DEBT THIS CREATES IS SILENT, AND THAT IS THE WHOLE RISK.** `refuse_on_strangers`
deliberately does not count a NULL-tier row, so **nothing in this system will ever raise its hand
about these 37 again.** While the debt stood, the guard was `scripts/task4_slice3.py --report`,
which printed it at the moment the fold ends.

⚠⚠ **THE DEBT IS PAID (`D-167` / `F-078` amendment 3, 2026-09-15).** The owner ruled **re-attach**,
not re-fold: the 37 rows were linked to the artifacts that were on the volume all along, and the
database witness reads **480 → 517** (`scripts/d167_reattach.py --url <tunnel> --witness`).

⚠ **`--restore` stays refused anyway** — a re-fold would overwrite the verified bytes those rows now
point at. `tests/test_f078_restore_refused.py` pins that refusal, and the `--report` notices now
record the payment while keeping the prohibition.

⚠ This is a **production write** and it is owner-gated. `F-075` records what happens when that gate
is passed by anyone other than the owner: a Planner instruction cannot discharge it, and an
authenticated session is not an attestation.
"""
from __future__ import annotations

import argparse
import os
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from core.db_identity import assert_campaign_target          # noqa: E402
from scripts.task3_run2_folds import _head_served            # noqa: E402

#: ⚠ The exact rows, from the F-078 measurement. A range, not a query, because the population is
#: a *finding* rather than a live condition — re-deriving it from status would silently widen if
#: anything else ever lands in `pending`.
FIRST_JOB, LAST_JOB = 4869, 4905
EXPECTED_N = 37
TRANSPORT = "https://pharmfoldmdk.fly.dev"


def _rows(conn):
    from sqlalchemy import text                              # noqa: PLC0415
    return conn.execute(text(
        "SELECT j.id, a.input_value, j.status, j.tier, j.analysis_id,"
        " (a.metadata->>'span_aa') AS span"
        " FROM jobs j JOIN protein_analyses a ON a.id = j.analysis_id"
        " WHERE j.id BETWEEN :a AND :b ORDER BY j.id"), {"a": FIRST_JOB, "b": LAST_JOB}).all()


def _refuse(msg: str) -> int:
    print(f"\nREFUSING: {msg}", file=sys.stderr)
    return 1


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--url", default=os.environ.get("DATABASE_URL", ""))
    ap.add_argument("--restore", action="store_true",
                    help="pay the debt: tier NULL -> 'local' so the 37 can be folded")
    ap.add_argument("--i-am-the-owner", dest="owner", action="store_true")
    args = ap.parse_args(argv)

    if not args.url:
        return _refuse("no DATABASE_URL and no --url.")

    # ⚠⚠ F-078 AMENDMENT 2. The 37 were never lost from the volume: all 37 artifacts are present
    # and identity-checked 37/37. --restore makes them claimable, and a re-fold uploads into the
    # same {artifact_root}/{job_id}/ directories and OVERWRITES them. ⚠ This does not try to check
    # the volume first: the only artifact probe here is `_head_served`, which resolves through
    # `pdb_path` and so answers 404 for exactly these rows whether or not the file exists.
    if args.restore:
        return _refuse(
            "--restore is withdrawn by F-078 amendment 2. The 37 artifacts are ON THE VOLUME "
            "(identity 37/37, scripts/f078_identity_check.py) and a re-fold would overwrite them. "
            "The owner rules re-attach or re-fold first; this path returns only if that ruling "
            "is re-fold, and then with a volume check that does not go through pdb_path.")

    from sqlalchemy import create_engine, text                # noqa: PLC0415

    from db.dburl import normalize_db_url                     # noqa: PLC0415

    eng = create_engine(normalize_db_url(args.url), future=True,
                        connect_args={"connect_timeout": 15})
    try:
        with eng.connect() as conn:
            # ⚠⚠ D-159 FIRST. Cluster identity, population floor, anchor row - before anything.
            assert_campaign_target(conn)
            print("D-159: ACCEPTED (cluster identity, floor, anchor)\n")
            rows = _rows(conn)

        if len(rows) != EXPECTED_N:
            return _refuse(f"{len(rows)} rows in {FIRST_JOB}-{LAST_JOB}, expected {EXPECTED_N}. "
                           f"The population is a finding, not a query; resolve the disagreement.")

        mode = "RESTORE (tier -> 'local')" if args.restore else "NULL-TIER (tier -> NULL)"
        print(f"{mode}: jobs {FIRST_JOB}-{LAST_JOB}, {len(rows)} rows\n")
        print(f"  {'job':<6}{'acc':<9}{'status':<10}{'tier':<8}{'span':>5}")
        for r in rows:
            print(f"  {r[0]:<6}{r[1]:<9}{str(r[2]):<10}{str(r[3]):<8}{str(r[5]):>5}")

        if args.restore:
            wrong = [r for r in rows if r[3] is not None]
            if wrong:
                return _refuse(f"{len(wrong)} of the 37 are not NULL-tier "
                               f"(ids {[r[0] for r in wrong][:5]}). Nothing to restore, or the "
                               f"NULL-tier write never ran.")
        else:
            # ⚠⚠ THE OWNER'S CONDITION: any row whose artifact turns out PRESENT is reconcilable,
            # not re-foldable, and this refuses rather than deciding for them.
            print("\nchecking the volume - refuse if ANY artifact is present")
            present = []
            for r in rows:
                found, n = _head_served(TRANSPORT, "structure", r[4])
                if n:
                    present.append((r[0], r[1], n))
            if present:
                return _refuse(
                    f"{len(present)} of the 37 DO have an artifact: {present}. "
                    f"Those rows are reconcilable, not lost, and the F-078 disposition does not "
                    f"cover them. Re-measure before writing anything.")
            print(f"  artifacts present: 0 of {len(rows)} - all 37 are genuinely lost\n")

            wrong = [r for r in rows if r[3] != "local"]
            if wrong:
                return _refuse(f"{len(wrong)} rows are not tier 'local' "
                               f"(ids {[r[0] for r in wrong][:5]}); the write already ran, or the "
                               f"state is not what F-078 measured.")

        if not args.owner:
            print("\nDRY RUN - nothing was written.")
            print("This is a PRODUCTION WRITE and it is the OWNER's (F-075).")
            print("Re-run with --i-am-the-owner, typed by the owner, at the keyboard.")
            return 0

        # ── the writes. Exactly two statements, named in F-078 amendment 1. ──────────────────
        with eng.begin() as conn:
            if args.restore:
                n = conn.execute(text(
                    "UPDATE jobs SET tier = 'local'"
                    " WHERE id BETWEEN :a AND :b AND tier IS NULL"),
                    {"a": FIRST_JOB, "b": LAST_JOB}).rowcount
                print(f"\nrestored tier 'local' on {n} rows.")
                print("The 37 are claimable again. Run --preflight, then fold them.")
            else:
                a = conn.execute(text(
                    "UPDATE jobs SET status = 'pending', claimed_at = NULL, worker_id = NULL"
                    " WHERE id = :j AND status = 'claimed'"), {"j": FIRST_JOB}).rowcount
                b = conn.execute(text(
                    "UPDATE jobs SET tier = NULL"
                    " WHERE id BETWEEN :a AND :b AND tier = 'local'"),
                    {"a": FIRST_JOB, "b": LAST_JOB}).rowcount
                print(f"\nwrote: {a} row claimed -> pending, {b} rows tier -> NULL.")
                print("The 37 are now claimable by NOBODY. Slice 3 is the only claimable")
                print("population, so --preflight will pass.")
                print("\n⚠⚠ A DEBT IS NOW OUTSTANDING. `--report` prints it when the fold ends.")
                print("   It was PAID on 2026-09-15 by RE-ATTACH (D-167), never by --restore:")
                print("   scripts/d167_reattach.py, database witness 480 -> 517.")
                print("   ⚠ --restore stays refused - a re-fold overwrites the verified bytes.")
        return 0
    finally:
        eng.dispose()


if __name__ == "__main__":
    raise SystemExit(main())
