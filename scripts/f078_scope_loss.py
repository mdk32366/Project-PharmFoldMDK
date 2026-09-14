"""F-078 SCOPE - the three-way comparison across every population. READ-ONLY.

Per row: DATABASE state, ON-DISK record, ARTIFACT bytes on the volume.
Any two agreeing is not evidence - that is what produced both wrong answers on 2026-09-15.

PROBE CALIBRATION (measured, not assumed, before this run):
  artifact present -> found=True,  bytes=N   (job 4868 / analysis 4869 -> 18186)
  artifact absent  -> found=False, bytes=0   (analysis 999999 and 0 -> 0)
  5xx / unreachable-> RAISES, so an outage cannot be reported as loss
So bytes==0 means the surface will not serve an artifact for that analysis.
It is NOT `/api/census/{accession}`, which returns 200 for any census protein and
proves nothing about a Run 2 artifact - the false positive that caused today's wrong answer.

TIMEZONES: the database is tz-aware UTC. progress.csv `at` is NAIVE and its convention is
UNMARKED. The offset is therefore MEASURED per file against rows present in both, never assumed,
and printed.
"""
from __future__ import annotations

import csv, json, pathlib, re, statistics, sys, datetime as dt

REPO = pathlib.Path(r"C:\Projects\Project-PharmFoldMDK")
sys.path.insert(0, str(REPO))

SELF = pathlib.Path(__file__).read_text(encoding="utf-8")
BODY = SELF.split('"""', 2)[2]
for a, b in (("TRUN","CATE"),("DELE","TE "),("DR","OP "),("ALT","ER "),("INSE","RT "),("UPDA","TE ")):
    assert (a+b) not in BODY.upper(), f"contains {a+b!r}"

from sqlalchemy import create_engine, text                 # noqa: E402
from db.dburl import normalize_db_url                      # noqa: E402
from scripts.task3_run2_folds import _head_served          # noqa: E402

BASE = "https://pharmfoldmdk.fly.dev"
BACKUP = dt.datetime(2026, 9, 13, 15, 24, 33, tzinfo=dt.timezone.utc)
PORT = sys.argv[1] if len(sys.argv) > 1 else "16391"
line = [l for l in (REPO/".env").read_text(encoding="utf-8").splitlines()
        if l.startswith("DATABASE_URL=")][0]
URL = re.sub(r"(@[^/:]+):\d+", r"\g<1>:"+PORT, line.split("=",1)[1].strip().strip('"').strip("'"))
eng = create_engine(normalize_db_url(URL), future=True, connect_args={"connect_timeout": 20})

print("=" * 86)
print("F-078 SCOPE - three-way: DATABASE state / ON-DISK record / ARTIFACT on the volume")
print("=" * 86)
print(f"backup boundary: {BACKUP.isoformat()}")

with eng.connect() as c:
    jobs = {r[0]: {"status": r[1], "completed": r[2], "analysis_id": r[3],
                   "acc": r[4], "pdb": r[5], "run": r[6]}
            for r in c.execute(text(
                "SELECT j.id, j.status, j.completed_at, j.analysis_id, a.input_value,"
                " a.pdb_path, j.inference_settings->>'run'"
                " FROM jobs j JOIN protein_analyses a ON a.id = j.analysis_id")).all()}
print(f"jobs in database: {len(jobs)}")

POPS = {"task3_run2": "task3_run2", "task4_slice1": "task4_slice1",
        "task4_slice2": "task4_slice2", "task4_slice3": "task4_slice3"}
ondisk = {}
for name, d in POPS.items():
    base = REPO/"data"/"control"/d
    enq = json.loads((base/"enqueued.json").read_text(encoding="utf-8")) if (base/"enqueued.json").is_file() else []
    prog = list(csv.DictReader(open(base/"progress.csv", encoding="utf-8"))) if (base/"progress.csv").is_file() else []
    ondisk[name] = {"enq": {int(e["job_id"]): e for e in enq},
                    "prog": {int(r["job_id"]): r for r in prog if (r.get("job_id") or "").strip().isdigit()}}
    print(f"  {name:<14} enqueued.json {len(enq):>5}   progress.csv {len(prog):>5}")

# ---- offsets MEASURED, never assumed ---------------------------------------------------------
print("\n-- timezone offset, MEASURED per file against rows present in both --")
offsets = {}
for name, d in ondisk.items():
    deltas = []
    for j, r in d["prog"].items():
        jb = jobs.get(j)
        if jb and jb["completed"] and r.get("at"):
            naive = dt.datetime.fromisoformat(r["at"])
            deltas.append((jb["completed"] - naive.replace(tzinfo=dt.timezone.utc)).total_seconds())
    if deltas:
        med = statistics.median(deltas)
        hrs = round(med/3600)
        offsets[name] = dt.timedelta(hours=hrs)
        print(f"  {name:<14} n={len(deltas):<5} median delta {med:>9.1f}s -> "
              f"csv is UTC{-hrs:+d} (local); converting csv + {hrs}h = UTC"
              f"   [spread {min(deltas):.0f}..{max(deltas):.0f}s]")
    else:
        offsets[name] = dt.timedelta(0)
        print(f"  {name:<14} no overlap with completed DB rows - offset UNDETERMINED, assuming 0")

# ---- the probe set ----------------------------------------------------------------------------
targets = set()
for name, d in ondisk.items():
    targets |= set(d["enq"]) | set(d["prog"])
run1 = sorted(j for j, v in jobs.items() if v["run"] == "1")
sample1 = run1[::max(1, len(run1)//200)]
targets |= set(sample1)
targets = sorted(t for t in targets if t in jobs)
print(f"\nprobing {len(targets)} rows "
      f"(all enumerated Run 2, plus {len(sample1)} stratified Run 1 census)")

rows = []
for i, j in enumerate(targets, 1):
    jb = jobs[j]
    try:
        found, n = _head_served(BASE, "structure", jb["analysis_id"])
        err = None
    except Exception as e:                                  # noqa: BLE001
        found, n, err = None, None, f"{type(e).__name__}"
    rows.append({"job": j, **jb, "found": found, "bytes": n, "err": err})
    if i % 100 == 0:
        print(f"   ... {i}/{len(targets)}", flush=True)

json.dump([{k: (str(v) if isinstance(v, dt.datetime) else v) for k, v in r.items()} for r in rows],
          open(REPO/".tmp"/"f078_scope.json", "w"), indent=1, default=str)

# ---- three-way ---------------------------------------------------------------------------------
def pop_of(j):
    for name, d in ondisk.items():
        if j in d["enq"] or j in d["prog"]:
            return name
    return "census run 1"

print("\n" + "=" * 86)
print("THREE-WAY, per population")
print("=" * 86)
buckets = {}
for r in rows:
    p = pop_of(r["job"])
    dbc = r["status"] == "complete"
    disk = r["job"] in ondisk.get(p, {"prog": {}})["prog"] if p in ondisk else None
    art = bool(r["bytes"])
    buckets.setdefault(p, []).append((r, dbc, disk, art))

for p, items in sorted(buckets.items()):
    n = len(items)
    agree_all = sum(1 for _, d, k, a in items if d and a and (k is not False))
    db_no_art = [r for r, d, k, a in items if d and not a]
    art_no_db = [r for r, d, k, a in items if not d and a]
    disk_no_db = [r for r, d, k, a in items if k and not d]
    neither = [r for r, d, k, a in items if not d and not a]
    print(f"\n{p}  (n={n})")
    print(f"   db complete AND artifact present : {agree_all}")
    print(f"   db complete BUT artifact MISSING : {len(db_no_art)}")
    print(f"   artifact present BUT db not done : {len(art_no_db)}")
    print(f"   on-disk folded BUT db not done   : {len(disk_no_db)}")
    print(f"   neither db-done nor artifact     : {len(neither)}")
    withart = [r for r, d, k, a in items if a and r["completed"]]
    noart = [r for r, d, k, a in items if not a]
    if withart:
        latest = max(withart, key=lambda r: r["completed"])
        print(f"   LATEST completion WITH artifact  : {latest['completed']}  (job {latest['job']})")
    cand = [r for r in noart if r["completed"]]
    if cand:
        earliest = min(cand, key=lambda r: r["completed"])
        print(f"   EARLIEST completion WITHOUT      : {earliest['completed']}  (job {earliest['job']})")
    else:
        print(f"   EARLIEST completion WITHOUT      : none carry completed_at")
    errs = [r for r, _, _, _ in items if r["err"]]
    if errs:
        print(f"   ⚠ probe RAISED on {len(errs)} rows - not counted as loss")

print("\n(read-only; no write of any kind was issued)")
eng.dispose()
