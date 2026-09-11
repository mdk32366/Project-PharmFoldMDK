"""T5 queue snapshot. Needs DATABASE_URL (dev-up window)."""
from __future__ import annotations
import os
from datetime import datetime, timezone
from sqlalchemy import create_engine, text
from db.dburl import normalize_db_url

e = create_engine(normalize_db_url(os.environ["DATABASE_URL"]), future=True)
q = text(
    "SELECT j.status, COALESCE(j.tier, 'NULL') AS tier, COUNT(1) AS n "
    "FROM jobs j JOIN protein_analyses a ON a.id = j.analysis_id "
    "WHERE a.cohort_tranche = 5 "
    "GROUP BY j.status, j.tier ORDER BY 1, 2"
)
print(datetime.now(timezone.utc).strftime("%H:%M:%SZ"))
with e.connect() as c:
    for r in c.execute(q):
        print(dict(r._mapping))