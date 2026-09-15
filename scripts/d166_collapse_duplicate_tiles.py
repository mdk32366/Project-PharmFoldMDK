"""D-166 — collapse the three duplicate tile identities so `0014` can build. OWNER-GATED.

⚠⚠ **This is a destructive production write and it is gated on `--i-am-the-owner`** (`F-075`: an
authenticated session is not an attestation, and a Planner instruction cannot discharge the gate).

⚠⚠ **IT RE-MEASURES BYTE-IDENTITY AT RUN TIME AND DOES NOT TRUST `F-077`.** `F-077` established
that every pair is byte-identical on 2026-09-15, and that is exactly the kind of fact this project
has twice acted on after it stopped being checkable. **A duplicate is either wasted compute or two
different answers**, and the collapse is only safe under the first. So both artifacts are fetched
from the serving surface and hashed **in this run**, and a single mismatch refuses everything.

⚠ **It deletes ROWS, never BYTES.** The volume artifacts are left in place and named. A row can be
re-derived from an artifact; an artifact deleted on a guess cannot be re-derived from anything.

⚠ **It keeps the LOWER id of each pair** — the first written. Not because the bytes differ (they do
not) but because a rule that does not need to consult the data cannot be applied inconsistently.

⚠⚠ **`F-079` — FOUR REFUSALS THE FIRST VERSION DID NOT HAVE**, each checked before the read that
decides and again inside the write transaction:

1. **The target names itself** (`D-159`, `assert_campaign_target`). The first version took its
   target from a hard-coded port on a URL read from a dotenv file. ⚠ The forensic cluster
   `zp2wjrej9lwodn4q` holds the same three duplicates, so nothing about the data would have refused
   it. **The operator now names the target** (`--url`, or `DATABASE_URL`), and the database is asked
   which database it is before anything else.
2. **No live fold.** *"Must not run during a live fold"* was prose (`D-162` rule 3). Any `claimed`
   job refuses, by id.
3. **No referencing row.** Foreign keys into `jobs.id` and `protein_analyses.id` are enumerated from
   the **catalog** (`pg_constraint`), not from a table list, so a table added by a later migration is
   seen. ⚠ Not `information_schema`: its constraint views show only tables the connected role OWNS,
   so a non-owner would read *no references* — a probe that answers "absent" because it cannot see.
4. **The enumeration is calibrated in the run** (`D-162` rule 7): `jobs.analysis_id` references
   `protein_analyses(id)` on every migrated schema, so a catalog read that does not return it
   refuses rather than reporting a clean database.

Run, in this order, with the tunnel open (`D-162` rules 4–5 — bind by name, corroborate against
`fly mpg status`'s Direct IP, `127.0.0.1` in the URL, one tunnel, close it after):

    python scripts/d166_collapse_duplicate_tiles.py --url <tunnel url>                      # verify only
    python scripts/d166_collapse_duplicate_tiles.py --url <tunnel url> --i-am-the-owner     # the write

⚠⚠ **This file's first version built its engine from a raw `DATABASE_URL`, and the local
suite was GREEN.** `tests/test_every_engine_normalizes_the_url.py` enumerates
**git-tracked** files (`_tracked_sources`), so a script that has been written but not
`git add`-ed is invisible to it. CI saw it on the first commit. **A green local gate is
not evidence about a file the gate cannot see** — `git add` before trusting a local run
on a new file.

⚠ **Pair this with the re-attach of the 37** (`PREWORK-2026-09-16.md` §1,
`ORDERS-Code-2026-09-16-reattach-and-collapse.md` Phase D). Both are owner writes against the same
cluster and one sitting costs less than two.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import pathlib
import sys
import urllib.error
import urllib.request

from sqlalchemy import create_engine, text

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from core.db_identity import WrongDatabase, assert_campaign_target  # noqa: E402
from core.db_role import format_preamble, index_build_refusal, role_preamble  # noqa: E402
from db.dburl import normalize_db_url              # noqa: E402

BASE = "https://pharmfoldmdk.fly.dev"

# ⚠ The expected duplicates, NAMED. If the live set is anything other than exactly this, the
# script refuses — a fourth duplicate is a finding, not something to sweep up in passing.
EXPECTED: dict[tuple[str, str], tuple[int, int]] = {
    ("2817", "0"): (3673, 3693),
    ("2837", "1"): (3674, 3695),
    ("2917", "0"): (3675, 3696),
}

DUPLICATES_SQL = text("""
    SELECT inference_settings->>'parent_job_id' AS parent,
           inference_settings->>'tile_index'    AS tile_index,
           array_agg(id ORDER BY id)            AS ids
    FROM jobs
    WHERE inference_settings ? 'tile_index' AND inference_settings ? 'parent_job_id'
    GROUP BY 1, 2 HAVING COUNT(*) > 1 ORDER BY 1
""")

PAIR_SQL = text("""
    SELECT j.id AS job_id, j.analysis_id, a.mean_plddt, a.pdb_path
    FROM jobs j JOIN protein_analyses a ON a.id = j.analysis_id
    WHERE j.id = ANY(:ids)
""")

CLAIMED_SQL = text("SELECT id FROM jobs WHERE status = 'claimed' ORDER BY id")

#: ⚠ Single-column foreign keys INTO `jobs.id` / `protein_analyses.id`, from the catalog.
#: `::regclass::text` is schema-qualified only when it must be, and quoted when it must be.
FOREIGN_KEYS_SQL = text("""
    SELECT con.conrelid::regclass::text AS tbl,
           quote_ident(att.attname)     AS col,
           con.confrelid::regclass::text AS ref
    FROM pg_constraint con
    JOIN pg_attribute att  ON att.attrelid = con.conrelid  AND att.attnum = con.conkey[1]
    JOIN pg_attribute ratt ON ratt.attrelid = con.confrelid AND ratt.attnum = con.confkey[1]
    WHERE con.contype = 'f'
      AND cardinality(con.conkey) = 1
      AND ratt.attname = 'id'
      AND con.confrelid IN ('jobs'::regclass, 'protein_analyses'::regclass)
    ORDER BY 1, 2
""")


def foreign_keys(conn) -> list[tuple[str, str, str]]:
    """Every (table, column, referenced table) pointing at the two tables the collapse deletes from.

    ⚠ Refuses when the enumeration cannot see `jobs.analysis_id`: that reference exists on every
    migrated schema, so its absence means the probe is blind, not that the database is clean."""
    fks = [(r.tbl, r.col, r.ref) for r in conn.execute(FOREIGN_KEYS_SQL)]
    if ("jobs", "analysis_id", "protein_analyses") not in fks:
        raise SystemExit(
            "REFUSING: the catalog enumeration of foreign keys did not return "
            "jobs.analysis_id -> protein_analyses(id), which every migrated schema carries. "
            f"The probe cannot see, so it cannot say nothing references the rows. Found: {fks}")
    return fks


def referencing_rows(conn, fks, drop_jobs: list[int], drop_analyses: list[int]):
    """Rows OUTSIDE the delete set that reference a row inside it: [(table, column, count)].

    ⚠ The dropped `jobs` rows reference the dropped analyses and are deleted with them, so they are
    excluded — every other referencing row is a refusal."""
    found = []
    for tbl, col, ref in fks:
        ids = drop_jobs if ref == "jobs" else drop_analyses
        sql = f"SELECT count(*) FROM {tbl} WHERE {col} = ANY(:ids)"
        params = {"ids": ids}
        if tbl == "jobs":
            sql += " AND NOT (id = ANY(:own))"
            params["own"] = drop_jobs
        n = conn.execute(text(sql), params).scalar()
        if n:
            found.append((tbl, col, n))
    return found


#: ⚠ `ORDERS` A2.1: a reference NO constraint declares. `inference_settings->>'parent_job_id'` names
#: a `jobs.id` from inside JSON, so `FOREIGN_KEYS_SQL` is blind to it by construction.
JSON_PARENT_SQL = text("""
    SELECT id FROM jobs
    WHERE inference_settings ? 'parent_job_id'
      AND inference_settings->>'parent_job_id' = ANY(:ids)
    ORDER BY id
""")


def json_parent_references(conn, drop_jobs: list[int]) -> list[int]:
    """Job ids whose `inference_settings.parent_job_id` names a row the collapse would delete."""
    return [r[0] for r in conn.execute(JSON_PARENT_SQL, {"ids": [str(j) for j in drop_jobs]})]


def _fetch(analysis_id: int) -> tuple[int, str]:
    """GET the served structure and hash it.

    ⚠ A 5xx or an unreachable host RAISES. Reporting "absent" for an outage would fabricate a
    verdict on a row that is about to be deleted.
    """
    url = f"{BASE}/api/analyses/{analysis_id}/structure"
    try:
        with urllib.request.urlopen(url, timeout=60) as r:
            body = r.read()
    except urllib.error.HTTPError as e:
        if e.code == 404:
            raise SystemExit(
                f"REFUSING: {url} is 404. A row whose artifact the surface will not serve is "
                f"not a row to collapse on.")
        raise
    return len(body), hashlib.sha256(body).hexdigest()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="D-166 duplicate tile collapse (F-079 guarded)")
    ap.add_argument("--url", default=os.environ.get("DATABASE_URL", ""),
                    help="the tunnel URL; defaults to DATABASE_URL. Never inferred from a port.")
    ap.add_argument("--i-am-the-owner", dest="owner", action="store_true")
    args = ap.parse_args(argv)
    owner = args.owner

    if not args.url:
        print("REFUSING: no --url and no DATABASE_URL. The operator names the target (F-079).")
        return 1

    # ⚠ `normalize_db_url`, never a raw URL: on Fly's bare `postgresql://` SQLAlchemy
    # resolves psycopg2, which `D-012` does not install. Caught by
    # `tests/test_every_engine_normalizes_the_url.py` — in CI, not locally, see above.
    eng = create_engine(normalize_db_url(args.url), future=True)

    print("=" * 78)
    print("D-166 - COLLAPSE THE DUPLICATE TILE IDENTITIES" + ("" if owner else "   [DRY RUN]"))
    print("=" * 78)

    try:
        with eng.begin() as c:
            # ⚠⚠ D-167 amendment 1 §2 (ORDERS A3.2 + A4.2): WHICH ROLE, printed before anything
            # else, and whether it can build 0014's index. This delete exists only so that index
            # can build; if the role cannot build it, the collapse WAITS with 0014.
            pre = role_preamble(c)
            for line in format_preamble(pre):
                print(line)
            refusal = index_build_refusal(pre)
            if refusal:
                print(f"\n{refusal}")
                return 1
            # ⚠⚠ F-079: WHICH DATABASE, before the read that decides what is deleted.
            try:
                assert_campaign_target(c)
            except WrongDatabase as e:
                print(f"\n{e}")
                return 1
            print("\n0. D-159: ACCEPTED (cluster identity, floor, anchor)")

            claimed = [r[0] for r in c.execute(CLAIMED_SQL)]
            if claimed:
                print(f"\nREFUSING: {len(claimed)} job(s) are claimed - a fold is live: {claimed}")
                print("  The 0014 index build that follows this collapse takes locks on `jobs`, "
                      "which the worker writes on every completion (D-162 rule 3).")
                return 1
            print("   no claimed jobs: no live fold")

            live = {(r["parent"], r["tile_index"]): tuple(r["ids"])
                    for r in c.execute(DUPLICATES_SQL).mappings()}
            fks = foreign_keys(c)

        print(f"\n1. LIVE DUPLICATE IDENTITIES: {len(live)}")
        for k, ids in sorted(live.items()):
            print(f"   parent {k[0]} tile {k[1]} -> jobs {list(ids)}")
        if live != EXPECTED:
            print("\nREFUSING: the live duplicate set is not the one this script was written against.")
            print(f"  expected {EXPECTED}")
            print(f"  found    {live}")
            print("  ⚠ A duplicate that is not one of the three named in F-077 is a NEW finding.")
            return 1
        print("   ✓ exactly the three F-077 named, and no others")

        with eng.begin() as c:
            rows = {r["job_id"]: dict(r) for r in
                    c.execute(PAIR_SQL, {"ids": [i for pair in live.values() for i in pair]})
                    .mappings()}
            drop_jobs = [drop for _keep, drop in live.values()]
            drop_analyses = [rows[j]["analysis_id"] for j in drop_jobs]
            refs = referencing_rows(c, fks, drop_jobs, drop_analyses)
            children = json_parent_references(c, drop_jobs)

        print(f"\n2. ROWS ELSEWHERE THAT REFERENCE A ROW TO BE DELETED "
              f"({len(fks)} foreign keys, from the catalog)")
        for tbl, col, ref in fks:
            print(f"   {tbl}.{col} -> {ref}(id)")
        print("   + jobs.inference_settings->>'parent_job_id' -> jobs(id)   (no declared constraint)")
        if refs or children:
            print("\nREFUSING: rows outside the delete set reference rows inside it:")
            for tbl, col, n in refs:
                print(f"   {tbl}.{col}: {n} row(s)")
            if children:
                print(f"   jobs.inference_settings->>'parent_job_id': jobs {children}")
            print("  A delete here either fails mid-transaction, cascades, or orphans a child tile. "
                  "None of those is this script's to decide; stop and report.")
            return 1
        print("   none")

        print("\n3. RE-MEASURING BYTE-IDENTITY NOW (not trusting F-077's 2026-09-15 measurement)")
        plan: list[tuple[int, int, str]] = []
        for k, (keep, drop) in sorted(live.items()):
            n_k, h_k = _fetch(rows[keep]["analysis_id"])
            n_d, h_d = _fetch(rows[drop]["analysis_id"])
            same = (n_k == n_d) and (h_k == h_d)
            print(f"   parent {k[0]} tile {k[1]}")
            print(f"      KEEP job {keep} analysis {rows[keep]['analysis_id']}  "
                  f"{n_k} bytes  sha {h_k[:16]}...  plddt {rows[keep]['mean_plddt']}")
            print(f"      DROP job {drop} analysis {rows[drop]['analysis_id']}  "
                  f"{n_d} bytes  sha {h_d[:16]}...  plddt {rows[drop]['mean_plddt']}")
            print(f"      => {'BYTE-IDENTICAL' if same else '*** DIFFERENT ***'}")
            if not same:
                print("\nREFUSING: a pair is NOT byte-identical. That is two different answers for "
                      "one tile identity, and collapsing it would destroy the evidence that decides "
                      "which is right. This is a finding; stop and report it.")
                return 1
            print(f"      ⚠ volume artifact of the dropped row is LEFT IN PLACE: "
                  f"{rows[drop]['pdb_path']}")
            plan.append((rows[drop]["job_id"], rows[drop]["analysis_id"], rows[drop]["pdb_path"]))

        print("\n4. WHAT THE WRITE WOULD DO")
        print(f"   DELETE {len(plan)} jobs rows and {len(plan)} protein_analyses rows:")
        for job_id, analysis_id, _path in plan:
            print(f"      job {job_id}  +  analysis {analysis_id}")
        print("   ⚠ No artifact file is deleted. No kept row is touched. No other table is "
              "written.")

        if not owner:
            print("\nDRY RUN - nothing was written.")
            print("Re-run with --i-am-the-owner to write. ⚠ OWNER AT THE KEYBOARD (F-075).")
            return 0

        with eng.begin() as c:
            # ⚠⚠ Re-check INSIDE the write transaction. The verification above ran in transactions
            # of its own, and D-166 is itself a finding about acting on a read taken earlier.
            assert_campaign_target(c)
            if [r[0] for r in c.execute(CLAIMED_SQL)]:
                raise SystemExit("REFUSING inside the write: a job became claimed under us.")
            again = {(r["parent"], r["tile_index"]): tuple(r["ids"])
                     for r in c.execute(DUPLICATES_SQL).mappings()}
            if again != EXPECTED:
                raise SystemExit("REFUSING inside the write: the duplicate set changed under us.")
            if (referencing_rows(c, foreign_keys(c), drop_jobs, drop_analyses)
                    or json_parent_references(c, drop_jobs)):
                raise SystemExit("REFUSING inside the write: a referencing row appeared under us.")
            for job_id, analysis_id, _path in plan:
                c.execute(text("DELETE FROM jobs WHERE id = :j"), {"j": job_id})
                c.execute(text("DELETE FROM protein_analyses WHERE id = :a"), {"a": analysis_id})
            left = c.execute(DUPLICATES_SQL).mappings().all()
            if left:
                raise SystemExit(f"REFUSING to commit: {len(left)} duplicate identities remain.")
    finally:
        eng.dispose()

    print(f"\n✓ COLLAPSED {len(plan)} duplicate rows. No duplicate tile identity remains.")
    print("\nNEXT, and it is the check rather than a formality:")
    print("   python -m alembic upgrade head")
    print("   ⚠ If 0014 still refuses, a duplicate exists that nobody has looked at.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
