#!/usr/bin/env python3
"""Derive the extracellular SEGMENT structure behind each span. Cache-only. No network, no GPU.

    python scripts/span_segments.py --dry-run
    python scripts/span_segments.py

⚠⚠ **WHY THIS EXISTS: `span_aa` IS THE LARGEST EXTRACELLULAR SEGMENT, NOT THE EXTRACELLULAR
CONTENT.** `core/span_extract.extract()` keeps the longest accepted topological domain
(`if best is None or n > best`) and **silently discards every other one**. For a single-pass
receptor that is the whole ectodomain and the two are the same thing. **For a multi-pass protein it
is one loop out of several**, and no artifact said so.

**Measured: 1,649 of 3,467 manifest proteins (47.6%) have more than one accepted extracellular
segment, and 92,709 residues of extracellular material are discarded.**

⚠ **This does not change any span, and re-derives nothing that was folded.** Every existing
`span_aa`, every fold and every artifact stands exactly as measured — the longest segment is a
defensible choice and D-081 freezes what has been produced. **What was missing was the CONTEXT**:
whether that span is *the* ectodomain or *a* loop. This adds the context beside it and changes
nothing behind it.

⚠ **Why it matters on an ADC platform specifically.** A reader seeing `span_aa = 272` reasonably
reads *"the extracellular region is 272 aa"*. For `Q9UHC9` the extracellular region is **830 aa
across 7 segments**; 272 is the biggest one. ⚠ **An antibody can bind a conformational epitope
spanning several loops — a structure of one loop in isolation is not a model of that site.**
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from core.span_definition import classify_term  # noqa: E402
from core.span_extract import _bounds, _features  # noqa: E402

CENSUS = REPO / "data" / "census"
CACHE = CENSUS / "spancache"
MANIFEST = CENSUS / "census_manifest.v7.csv"
OUT = CENSUS / "span_segments.csv"

COLUMNS = ("census_accession", "span_aa", "segment_count", "extracellular_total_aa",
           "discarded_aa", "folded_fraction", "topology", "segments")

#: ⚠ A SENTENCE per row, because "1" and "7" mean different things to a reader deciding whether a
#: structure models the binding site. Never a bare integer in the UI.
CONTIGUOUS = "contiguous"
INTERMITTENT = "intermittent"
NONE_FOUND = "no_accepted_segment"


def segments_for(accession: str) -> list[tuple[int, int, int]]:
    """Accepted extracellular segments as `(start, end, length)`. ⚠ Cache only — never fetched."""
    p = CACHE / f"{accession}.json"
    if not p.exists():
        return []
    data = json.loads(p.read_text(encoding="utf-8"))
    out = []
    for f in _features(data, "Topological domain"):
        if classify_term(f.get("description", "") or "") != "accepted":
            continue
        s, e = _bounds(f)
        if s is not None and e is not None:
            out.append((s, e, e - s + 1))
    return sorted(out)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    rows, topo = [], Counter()
    for r in csv.DictReader(MANIFEST.open(encoding="utf-8")):
        acc = r["census_accession"]
        segs = segments_for(acc)
        total = sum(x[2] for x in segs)
        longest = max((x[2] for x in segs), default=0)
        # ⚠ GPI-anchored spans come from a different rule and have NO topological domains. That is
        # `no_accepted_segment`, and it is NOT "intermittent" and NOT a defect — it is a different
        # molecular architecture (D-081), so it takes its own word.
        kind = (NONE_FOUND if not segs else CONTIGUOUS if len(segs) == 1 else INTERMITTENT)
        topo[kind] += 1
        rows.append({
            "census_accession": acc,
            "span_aa": r["span_aa"],
            "segment_count": str(len(segs)),
            "extracellular_total_aa": str(total),
            "discarded_aa": str(max(0, total - longest)),
            # ⚠ Blank rather than 0/1 when there is nothing to divide — a fraction of nothing is
            # not "none of it", and the two must not print the same.
            "folded_fraction": f"{longest / total:.3f}" if total else "",
            "topology": kind,
            "segments": ";".join(f"{s}-{e}" for s, e, _ in segs),
        })

    disc = sum(int(r["discarded_aa"]) for r in rows)
    inter = topo[INTERMITTENT]
    print(f"manifest rows | {len(rows)}")
    print(f"  topology composition | {dict(topo)}")
    print(f"  ⚠ INTERMITTENT (>1 accepted segment) | {inter} ({100 * inter / len(rows):.1f}%)")
    print(f"  ⚠ extracellular residues DISCARDED   | {disc:,}")
    worst = sorted(rows, key=lambda r: -int(r["discarded_aa"]))[:5]
    for w in worst:
        print(f"      {w['census_accession']} | {w['segment_count']} segments | folded "
              f"{w['span_aa']} aa of {w['extracellular_total_aa']} aa "
              f"| ⚠ discarded {w['discarded_aa']}")

    if args.dry_run:
        print("\n⚠ DRY RUN — nothing written.")
        return 0

    with OUT.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(COLUMNS))
        w.writeheader()
        w.writerows(rows)
    (CENSUS / "span_segments.provenance.json").write_text(json.dumps({
        "derived_on": "cache-only; no network fetch, no span changed",
        "source_manifest": MANIFEST.name,
        "span_definition": "v2-ruled-vocabulary-2026-08-07",
        "rows": len(rows),
        "intermittent": inter,
        "discarded_residues": disc,
        "⚠ scope": "CONTEXT ONLY — no span_aa, fold or artifact is altered by this file",
    }, indent=2), encoding="utf-8")
    print(f"\nwrote {OUT.name} ({len(rows)} rows) + provenance")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
