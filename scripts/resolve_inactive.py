#!/usr/bin/env python3
"""Resolve the census rows whose UniProt identity is inactive. ⚠ NETWORK, and deliberately so.

    python scripts/resolve_inactive.py --dry-run     # ⚠ always first
    python scripts/resolve_inactive.py

⚠⚠ **THIS IS THE ONLY CENSUS SCRIPT THAT TOUCHES THE NETWORK.** Every other one is cache-only. It
is separate *because* it fetches: mixing a live fetch into the re-parse path would put **two fetch
dates in one file**, which the provenance model forbids (`census_reparse.py`: *two facts, never one
date*).

## ⚠ It writes its OWN file, and never restamps an existing row

`spans_*.v2.csv` were fetched **2026-08-06**. This runs later. So the result lands in
`census_identity_resolution.csv` with **its own `resolved_on`**, and the V2 files are **not
touched**. A reader joins on `census_accession`. ⚠ **Rewriting `fetched_on` on those rows would
manufacture provenance for data that did not move.**

## ⚠ What it CANNOT do

**It does not produce sequences.** An inactive UniProt entry carries **no sequence** — measured, all
26 of them. So this converts *"we do not know"* into **a stated, final reason**; it does not convert
a single row into a foldable one.

  · **`DELETED`** — withdrawn from Swiss-Prot. ⚠ **No target, no sequence, nothing to fetch, ever.**
    *"Unknown"* resolves to *"this entry no longer exists"*, which is an answer, not a gap.
  · **`DEMERGED`** — split into N accessions. ⚠ **Resolvable, but ONE-TO-MANY**: following the
    targets would change the census denominator, and one target is **already a census row**. That
    is a **scope decision and is NOT taken here** — the targets are recorded, not followed.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
import time
import urllib.error
import urllib.request
from collections import Counter
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
CENSUS = REPO / "data" / "census"
SOURCES = ("spans_surface.v2.csv", "spans_annex.v2.csv")
OUT = CENSUS / "census_identity_resolution.csv"

#: ⚠ Unhurried on purpose. 26 requests against a public API is not a place to save nine seconds.
DELAY_S = 0.35

COLUMNS = ("census_accession", "census_class", "source_identifiers", "resolution",
           "targets", "target_count", "deleted_reason", "carries_sequence",
           "resolvable", "resolved_on", "api")


def inactive_rows() -> list[dict[str, str]]:
    out = []
    for f in SOURCES:
        for r in csv.DictReader((CENSUS / f).open(encoding="utf-8")):
            if "uniprot_inactive" in (r.get("no_span_reason") or ""):
                out.append(r)
    if not out:
        raise SystemExit("⚠ no inactive rows found — refusing a silent no-op")
    return out


def fetch(acc: str) -> dict:
    url = f"https://rest.uniprot.org/uniprotkb/{acc}.json"
    with urllib.request.urlopen(url, timeout=45) as r:
        return json.loads(r.read().decode())


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="⚠ fetch and report, write nothing")
    args = ap.parse_args()

    rows = inactive_rows()
    print(f"inactive census rows: {len(rows)}")

    census = set()
    for f in SOURCES:
        census |= {r["census_accession"] for r in csv.DictReader((CENSUS / f).open(encoding="utf-8"))}

    today = date.today().isoformat()
    out: list[dict[str, str]] = []
    for r in rows:
        acc = r["census_accession"]
        try:
            d = fetch(acc)
            ir = d.get("inactiveReason") or {}
            targets = ir.get("mergeDemergeTo") or []
            reason = ir.get("inactiveReasonType") or "UNKNOWN_INACTIVE_REASON"
            seq = bool((d.get("sequence") or {}).get("value"))
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as e:
            # ⚠ A fetch failure is its OWN category. It must never look like DELETED — one is
            # "the entry is gone", the other is "we could not ask".
            reason, targets, seq = f"FETCH_FAILED_{type(e).__name__}", [], False
            ir = {}
        out.append({
            "census_accession": acc,
            "census_class": r.get("census_class", ""),
            "source_identifiers": r.get("source_identifiers", ""),
            "resolution": reason,
            "targets": ";".join(targets),
            "target_count": str(len(targets)),
            "deleted_reason": ir.get("deletedReason", "") if isinstance(ir, dict) else "",
            "carries_sequence": "true" if seq else "false",
            # ⚠ A SENTENCE, never a bool — "resolvable" means different things for the two reasons.
            "resolvable": ("no — withdrawn, no target and no sequence" if reason == "DELETED"
                           else f"yes, but ONE-TO-{len(targets)} — following targets changes the "
                                f"census denominator (scope decision, not taken here)"
                           if reason == "DEMERGED"
                           else "unknown — the fetch itself failed"),
            "resolved_on": today,
            "api": "rest.uniprot.org/uniprotkb",
        })
        time.sleep(DELAY_S)

    comp = Counter(o["resolution"] for o in out)
    tgts = [t for o in out for t in o["targets"].split(";") if t]
    print(f"  resolution composition | {dict(comp)}")
    print(f"  ⚠ any carrying a SEQUENCE | {sum(1 for o in out if o['carries_sequence'] == 'true')}"
          f"  — a resolution is NOT a foldable row")
    print(f"  demerge targets named | {len(tgts)} | ⚠ already in the census | "
          f"{sorted(set(tgts) & census)}")

    if args.dry_run:
        print("\n⚠ DRY RUN — nothing written.")
        return 0

    with OUT.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(COLUMNS))
        w.writeheader()
        w.writerows(out)
    (CENSUS / "census_identity_resolution.provenance.json").write_text(json.dumps({
        "resolved_on": today,
        "api": "rest.uniprot.org/uniprotkb",
        "rows": len(out),
        "⚠ scope": "identity resolution ONLY — no sequence was retrieved and none exists",
        "⚠ fetched_on of the span files": "2026-08-06 — NOT restamped by this run",
        "⚠ demerge targets": "recorded, NOT followed — following them is a denominator change",
    }, indent=2), encoding="utf-8")
    print(f"\nwrote {OUT.name} ({len(out)} rows) + provenance")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
