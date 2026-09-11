"""Kathad-82 fold audit against the live DB. Cohort rows only (ranking_run_id NOT NULL)."""
from __future__ import annotations

import os
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

if "DATABASE_URL" not in os.environ:
    envp = REPO / ".env"
    for line in envp.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if not s or s.startswith("#") or "=" not in s:
            continue
        k, v = s.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

from sqlalchemy import create_engine, text
from db.dburl import normalize_db_url
from core.manifest import build_manifest

rows = build_manifest()
print(f"MANIFEST n={len(rows)}")
print("MANIFEST_DISPOSITION", dict(Counter(r.disposition for r in rows)))
wanted = {r.accession: r for r in rows}

eng = create_engine(normalize_db_url(os.environ["DATABASE_URL"]), future=True)
q = text("""
SELECT
  a.input_value AS accession,
  a.ranking_run_id,
  a.cohort_tranche,
  j.id AS job_id,
  j.status,
  j.tier AS job_tier,
  j.attempts,
  j.error,
  j.worker_id,
  (a.pdb_path IS NOT NULL) AS has_pdb,
  (a.pae_json_path IS NOT NULL) AS has_pae,
  a.mean_plddt,
  a.metadata->>'fold_length' AS fold_length,
  a.metadata->>'gene' AS gene,
  a.metadata->>'disposition' AS meta_disp
FROM protein_analyses a
LEFT JOIN jobs j ON j.analysis_id = a.id
WHERE a.input_type = 'uniprot'
  AND a.ranking_run_id IS NOT NULL
ORDER BY a.input_value, a.ranking_run_id, j.id
""")

with eng.connect() as c:
    db_rows = [dict(r._mapping) for r in c.execute(q)]

# Restrict to Kathad-82 accessions
db_rows = [r for r in db_rows if r["accession"] in wanted]
print(f"COHORT_DB_ROWS n={len(db_rows)}")

by_acc = {}
for r in db_rows:
    by_acc.setdefault(r["accession"], []).append(r)

missing = []
excluded_with_jobs = []
failed = []
pending = []
claimed = []
complete_no_pdb = []
complete_no_pae = []
folded = []

print("\n== PER TARGET ==")
for r in sorted(rows, key=lambda x: (x.disposition, -(x.span or 0), x.gene or "")):
    hits = by_acc.get(r.accession, [])
    if r.disposition == "excluded":
        if hits:
            excluded_with_jobs.append((r.accession, r.gene, hits))
            print(f"EXCLUDED_HAS_JOBS {r.accession} {r.gene} span={r.span} jobs={len(hits)}")
            for h in hits:
                print("   ", {k: h[k] for k in ('status','job_tier','fold_length','has_pdb','has_pae','error')})
        else:
            print(f"EXCLUDED_NO_JOB {r.accession} {r.gene} span={r.span}")
        continue
    if not hits:
        missing.append((r.accession, r.gene, r.disposition, r.tier, r.span))
        print(f"MISSING {r.accession} {r.gene} disp={r.disposition} tier={r.tier} span={r.span}")
        continue
    h = hits[-1]
    st = h["status"]
    line = (
        f"{r.accession} {r.gene:<10} disp={r.disposition:<9} "
        f"manifest_tier={r.tier:<7} job_tier={h['job_tier']} L={h['fold_length']} "
        f"pdb={h['has_pdb']} pae={h['has_pae']} plddt={h['mean_plddt']} "
        f"attempts={h['attempts']}"
    )
    if st == "failed":
        failed.append(h)
        print("FAILED   " + line)
        print(f"         error={h['error']}")
    elif st == "pending":
        pending.append(h)
        print("PENDING  " + line)
    elif st == "claimed":
        claimed.append(h)
        print("CLAIMED  " + line)
    elif st == "complete":
        folded.append(h)
        if not h["has_pdb"]:
            complete_no_pdb.append(h)
        if not h["has_pae"]:
            complete_no_pae.append(h)
        print("COMPLETE " + line)
    else:
        print(f"OTHER:{st} " + line)
    if len(hits) != 1:
        print(f"         extra_cohort_rows={len(hits)}")

print("\n== SUMMARY ==")
print("manifest", len(rows), dict(Counter(r.disposition for r in rows)))
print("missing_foldable", len(missing), missing)
print("excluded_with_jobs", len(excluded_with_jobs))
print("failed", len(failed))
for x in failed:
    print("  ", x["accession"], x["gene"], "L="+str(x["fold_length"]), "err=", (x["error"] or "")[:400])
print("pending", len(pending), [(x["accession"], x["gene"]) for x in pending])
print("claimed", len(claimed), [(x["accession"], x["gene"]) for x in claimed])
print("complete", len(folded))
print("complete_no_pdb", [x["accession"] for x in complete_no_pdb])
print("complete_no_pae", [x["accession"] for x in complete_no_pae])
print("foldable_accounted", len(missing)+len(failed)+len(pending)+len(claimed)+len(folded), "expect 80")