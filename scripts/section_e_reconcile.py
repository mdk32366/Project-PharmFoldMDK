"""SECTION E - state reconciliation after the 2026-09-13 truncation. READ-ONLY.

Plus the F-076 section 4 measurement, in the same tunnel session (D-162 rule 5: one tunnel).

WHAT THIS FILE CONTAINS, AND THE SELF-CHECK BELOW ENFORCES IT: bare SELECTs only.
No DDL, no DML, no pytest. The needles are SPLIT so this check cannot match itself -
D-145 amendment 1, which this wave paid for four times.
"""
from __future__ import annotations

import json
import pathlib
import re
import sys
from collections import Counter

REPO = pathlib.Path(r"C:\Projects\Project-PharmFoldMDK")
sys.path.insert(0, str(REPO))

SELF = pathlib.Path(__file__).read_text(encoding="utf-8")
BODY = SELF.split('"""', 2)[2]
for a, b in (("TRUN", "CATE"), ("DELE", "TE "), ("DR", "OP "), ("ALT", "ER "),
             ("INSE", "RT "), ("UPDA", "TE "), ("CREA", "TE ")):
    assert (a + b) not in BODY.upper(), f"this script contains {a + b!r}"
assert ("impo" + "rt pytest") not in BODY

from sqlalchemy import create_engine, text          # noqa: E402
from db.dburl import normalize_db_url              # noqa: E402

PORT = sys.argv[1] if len(sys.argv) > 1 else "16391"
line = [l for l in (REPO / ".env").read_text(encoding="utf-8").splitlines()
        if l.startswith("DATABASE_URL=")][0]
URL = re.sub(r"(@[^/:]+):\d+", r"\g<1>:" + PORT,
             line.split("=", 1)[1].strip().strip('"').strip("'"))

BACKUP_AT = "2026-09-13 15:24:33+00"
TRUNC_AT = "2026-09-13 16:38:09+00"

eng = create_engine(normalize_db_url(URL), future=True, connect_args={"connect_timeout": 15})


def q(conn, sql, **p):
    return conn.execute(text(sql), p)


print("=" * 78)
print("SECTION E - STATE RECONCILIATION. READ-ONLY.")
print("=" * 78)

with eng.connect() as c:
    # -- 0. which database am I actually reading? -------------------------------------------
    marker = q(c, "SELECT cluster_id FROM keel_live_cluster LIMIT 1").scalar()
    print(f"\ncluster marker           : {marker!r}")
    print(f"current_database()       : {q(c, 'SELECT current_database()').scalar()!r}")

    # -- 1. the headline counts -------------------------------------------------------------
    pa = q(c, "SELECT count(*) FROM protein_analyses").scalar()
    jb = q(c, "SELECT count(*) FROM jobs").scalar()
    mx = q(c, "SELECT max(id) FROM protein_analyses").scalar()
    print(f"\nprotein_analyses         : {pa}")
    print(f"jobs                     : {jb}")
    print(f"max(protein_analyses.id) : {mx}")
    print(f"cohort_tranche > 0       : "
          f"{q(c, 'SELECT count(*) FROM protein_analyses WHERE cohort_tranche > 0').scalar()}")

    # -- 2. THE 73-MINUTE WINDOW ------------------------------------------------------------
    print("\n" + "-" * 78)
    print("2. THE WINDOW: backup 15:24:33Z -> truncation 16:38:09Z (73 minutes)")
    print("-" * 78)
    print("   The restore is FROM the 15:24:33Z backup, so anything written in the window is")
    print("   absent BY CONSTRUCTION. The question is what SHOULD be there and is not.")
    newest_pa = q(c, "SELECT max(created_at) FROM protein_analyses").scalar()
    print(f"\n   max(protein_analyses.created_at) : {newest_pa}")
    in_window = q(c, "SELECT count(*) FROM protein_analyses "
                     "WHERE created_at > :a AND created_at < :b",
                  a=BACKUP_AT, b=TRUNC_AT).scalar()
    after = q(c, "SELECT count(*) FROM protein_analyses WHERE created_at >= :b",
              b=TRUNC_AT).scalar()
    print(f"   rows created INSIDE the window   : {in_window}")
    print(f"   rows created AFTER the truncation: {after}")
    print("   (non-zero 'after' = written since recovery, which is expected and fine)")

    # -- 3. the on-disk enumerations, reconciled by ACCESSION and JOB ID ---------------------
    print("\n" + "-" * 78)
    print("3. ON-DISK ENUMERATIONS vs THE RESTORED DATABASE (by accession AND job id)")
    print("-" * 78)
    for name in ("task3_run2", "task4_slice1", "task4_slice2", "task4_slice3"):
        p = REPO / "data" / "control" / name / "enqueued.json"
        if not p.is_file():
            print(f"\n   {name:<14} enqueued.json ABSENT on disk "
                  f"({'expected - never enqueued' if name.endswith('3') else 'UNEXPECTED'})")
            continue
        rows = json.loads(p.read_text(encoding="utf-8"))
        jids = [int(r["job_id"]) for r in rows]
        accs = sorted({r["accession"] for r in rows})
        have_j = {r[0] for r in q(c, "SELECT id FROM jobs WHERE id = ANY(:v)", v=jids)}
        have_a = {r[0] for r in q(c, "SELECT DISTINCT input_value FROM protein_analyses "
                                     "WHERE input_value = ANY(:v)", v=accs)}
        miss_j = sorted(set(jids) - have_j)
        miss_a = sorted(set(accs) - have_a)
        print(f"\n   {name:<14} on disk: {len(jids)} job ids, {len(accs)} accessions")
        print(f"   {'':<14} present : {len(have_j)} job ids, {len(have_a)} accessions")
        print(f"   {'':<14} MISSING : {len(miss_j)} job ids, {len(miss_a)} accessions")
        if miss_j:
            print(f"   {'':<14}   job ids   : {miss_j[:20]}{' ...' if len(miss_j) > 20 else ''}")
        if miss_a:
            print(f"   {'':<14}   accessions: {miss_a[:20]}{' ...' if len(miss_a) > 20 else ''}")

    # -- 4. artifact paths resolve to bytes -------------------------------------------------
    print("\n" + "-" * 78)
    print("4. ARTIFACT PATHS (a restored DB pointing at absent artifacts looks like success)")
    print("-" * 78)
    tot = q(c, "SELECT count(*) FROM protein_analyses WHERE pdb_path IS NOT NULL").scalar()
    print(f"   rows carrying pdb_path   : {tot}")
    print(f"   rows carrying mean_plddt : "
          f"{q(c, 'SELECT count(*) FROM protein_analyses WHERE mean_plddt IS NOT NULL').scalar()}")
    print(f"   rows carrying pae_json   : "
          f"{q(c, 'SELECT count(*) FROM protein_analyses WHERE pae_json_path IS NOT NULL').scalar()}")
    print("   NOTE: the artifacts live on the FLY VOLUME, not on this machine, so byte")
    print("   resolution is checked against the served surface, not the local filesystem.")

    # -- 5. run partition -------------------------------------------------------------------
    print("\n" + "-" * 78)
    print("5. RUN PARTITION")
    print("-" * 78)
    rows = q(c, "SELECT inference_settings ->> 'run' AS run, count(*) "
                "FROM jobs GROUP BY 1 ORDER BY 1").all()
    for r in rows:
        print(f"   run = {str(r[0]):<8} : {r[1]}")

    # -- 6. F-076 section 4: landed hold-48 tile boundaries, cold vs warm --------------------
    print("\n" + "=" * 78)
    print("F-076 SECTION 4 - LANDED HOLD-48 TILE GEOMETRY, cold vs warm")
    print("=" * 78)
    from core.hold48 import plan_tiles, tileable_rows        # noqa: PLC0415

    tiles = q(c, "SELECT j.id, j.inference_settings, a.input_value "
                 "FROM jobs j JOIN protein_analyses a ON a.id = j.analysis_id "
                 "WHERE j.inference_settings ? 'tile_start'").all()
    print(f"\n   tile jobs found in the database: {len(tiles)}")
    by_acc: dict[str, list[tuple[int, int]]] = {}
    for _jid, st, acc in tiles:
        s = st or {}
        if s.get("tile_start") is None:
            continue
        by_acc.setdefault(acc, []).append((int(s["tile_start"]), int(s["tile_end"])))
    print(f"   distinct parents with tiles    : {len(by_acc)}")

    rows_by_acc = {r.accession: r for r in tileable_rows()}
    verdicts: Counter = Counter()
    print(f"\n   {'accession':<11} {'landed':<28} {'verdict'}")
    for acc in sorted(by_acc):
        landed = sorted(by_acc[acc])
        row = rows_by_acc.get(acc)
        if row is None:
            verdicts["not in hold48"] += 1
            print(f"   {acc:<11} {str(landed)[:26]:<28} not a hold-48 tileable row")
            continue
        cold = sorted((t.start, t.end) for t in plan_tiles(row, domain_ends=[]))
        warm = sorted((t.start, t.end) for t in plan_tiles(row))
        if landed == cold and landed == warm:
            v = "1+2 cold==warm (no snap)"
        elif landed == cold:
            v = "1 MATCHES COLD"
        elif landed == warm:
            v = "2 MATCHES WARM-NOW"
        else:
            v = "3 *** MATCHES NEITHER ***"
        verdicts[v] += 1
        print(f"   {acc:<11} {str(landed)[:26]:<28} {v}")
        if v.startswith("3"):
            print(f"   {'':<11}   cold: {cold}")
            print(f"   {'':<11}   warm: {warm}")

    print("\n   -- classification --")
    for k, n in sorted(verdicts.items()):
        print(f"   {k:<30} {n}")

eng.dispose()
print("\n(no write of any kind was issued)")
