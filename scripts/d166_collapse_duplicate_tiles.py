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

Run, in this order, with the tunnel open (`D-162` rule 5 — bind by name, corroborate against
`fly mpg status`'s Direct IP, one tunnel, close it after):

    python scripts/d166_collapse_duplicate_tiles.py                      # verify only, no writes
    python scripts/d166_collapse_duplicate_tiles.py --i-am-the-owner     # the write

⚠⚠ **This file's first version built its engine from a raw `DATABASE_URL`, and the local
suite was GREEN.** `tests/test_every_engine_normalizes_the_url.py` enumerates
**git-tracked** files (`_tracked_sources`), so a script that has been written but not
`git add`-ed is invisible to it. CI saw it on the first commit. **A green local gate is
not evidence about a file the gate cannot see** — `git add` before trusting a local run
on a new file.

⚠ **Pair this with the `F-078` restore of the 37** (`PREWORK-2026-09-16.md` item 1). Both are owner
writes against the same cluster and one sitting costs less than two.
"""

from __future__ import annotations

import hashlib
import pathlib
import re
import sys
import urllib.error
import urllib.request

from sqlalchemy import create_engine, text

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from db.dburl import normalize_db_url              # noqa: E402

BASE = "https://pharmfoldmdk.fly.dev"
PORT = "16391"

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


def _db_url() -> str:
    line = [ln for ln in (REPO / ".env").read_text(encoding="utf-8").splitlines()
            if ln.startswith("DATABASE_URL=")][0]
    return re.sub(r"(@[^/:]+):\d+", r"\g<1>:" + PORT,
                  line.split("=", 1)[1].strip().strip('"').strip("'"))


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


def main() -> int:
    owner = "--i-am-the-owner" in sys.argv
    # ⚠ `normalize_db_url`, never a raw URL: on Fly's bare `postgresql://` SQLAlchemy
    # resolves psycopg2, which `D-012` does not install. Caught by
    # `tests/test_every_engine_normalizes_the_url.py` — in CI, not locally, see below.
    eng = create_engine(normalize_db_url(_db_url()))

    print("=" * 78)
    print("D-166 - COLLAPSE THE DUPLICATE TILE IDENTITIES" + ("" if owner else "   [DRY RUN]"))
    print("=" * 78)

    with eng.begin() as c:
        live = {(r["parent"], r["tile_index"]): tuple(r["ids"])
                for r in c.execute(DUPLICATES_SQL).mappings()}

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

    print("\n2. RE-MEASURING BYTE-IDENTITY NOW (not trusting F-077's 2026-09-15 measurement)")
    plan: list[tuple[int, int, str]] = []
    for k, (keep, drop) in sorted(live.items()):
        with eng.begin() as c:
            rows = {r["job_id"]: dict(r) for r in
                    c.execute(PAIR_SQL, {"ids": [keep, drop]}).mappings()}
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

    print("\n3. WHAT THE WRITE WOULD DO")
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
        # ⚠⚠ Re-check INSIDE the write transaction. The verification above ran in transactions of
        # its own, and D-166 is itself a finding about acting on a read taken earlier.
        again = {(r["parent"], r["tile_index"]): tuple(r["ids"])
                 for r in c.execute(DUPLICATES_SQL).mappings()}
        if again != EXPECTED:
            raise SystemExit("REFUSING inside the write: the duplicate set changed under us.")
        for job_id, analysis_id, _path in plan:
            c.execute(text("DELETE FROM jobs WHERE id = :j"), {"j": job_id})
            c.execute(text("DELETE FROM protein_analyses WHERE id = :a"), {"a": analysis_id})
        left = c.execute(DUPLICATES_SQL).mappings().all()
        if left:
            raise SystemExit(f"REFUSING to commit: {len(left)} duplicate identities remain.")

    print(f"\n✓ COLLAPSED {len(plan)} duplicate rows. No duplicate tile identity remains.")
    print("\nNEXT, and it is the check rather than a formality:")
    print("   python -m alembic upgrade head")
    print("   ⚠ If 0014 still refuses, a duplicate exists that nobody has looked at.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
