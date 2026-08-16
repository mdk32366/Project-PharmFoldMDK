#!/usr/bin/env python3
"""Gene symbol + protein name for every census accession. Cache-only. No network.

    python scripts/census_labels.py

⚠ Census `protein_analyses` rows carry **no gene and no label** — the ingest writes span geometry,
not identity. A surface listing 2,700 bare accessions is unreadable and unsearchable, so the names
are derived here from the same cache the spans came from. ⚠ **Nothing is fetched and no row is
altered.**
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

import sys
REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
CENSUS = REPO / "data" / "census"
CACHE = CENSUS / "spancache"
OUT = CENSUS / "census_labels.csv"


def main() -> int:
    rows = []
    manifest = list(csv.DictReader((CENSUS / "census_manifest.v7.csv").open(encoding="utf-8")))
    missing = 0
    for r in manifest:
        acc = r["census_accession"]
        p = CACHE / f"{acc}.json"
        if not p.exists():
            # ⚠ A category, not a blank row: "no cache entry" is not "no name".
            rows.append({"census_accession": acc, "gene": "", "label": "",
                         "source": "⚠ NO CACHE ENTRY — name unknown, not absent"})
            missing += 1
            continue
        d = json.loads(p.read_text(encoding="utf-8"))
        genes = d.get("genes") or []
        gene = ((genes[0].get("geneName") or {}).get("value", "") if genes else "")
        name = ((((d.get("proteinDescription") or {}).get("recommendedName") or {})
                 .get("fullName") or {}).get("value", ""))
        if not name:
            sub = (d.get("proteinDescription") or {}).get("submissionNames") or []
            name = ((sub[0].get("fullName") or {}).get("value", "") if sub else "")
        rows.append({"census_accession": acc, "gene": gene, "label": name, "source": "spancache"})

    with OUT.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["census_accession", "gene", "label", "source"])
        w.writeheader()
        w.writerows(rows)
    from core.derived_freshness import stamp
    # ⚠ This file had NO provenance at all — it could not be checked for staleness because nothing
    # recorded what it was derived from.
    (CENSUS / "census_labels.provenance.json").write_text(json.dumps({
        **stamp(CENSUS / "census_manifest.v7.csv"),
        "derived_on": "cache-only; no network fetch",
        "rows": len(rows),
        "⚠ scope": "NAMES ONLY — no span, fold or artifact is altered by this file",
    }, indent=2), encoding="utf-8")

    named = sum(1 for r in rows if r["gene"])
    print(f"wrote {OUT.name} | {len(rows)} rows | with a gene symbol {named} "
          f"| ⚠ without {len(rows) - named} | ⚠ no cache entry {missing}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
