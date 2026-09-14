#!/usr/bin/env python3
"""Regenerate `data/census/hold48_domain_ends.v1.json` — the `D-165` pin. READ-ONLY on the database.

    python scripts/pin_hold48_domain_ends.py --check     # compare, write nothing
    python scripts/pin_hold48_domain_ends.py --write

⚠⚠ **WHY A PIN AND NOT THE CACHE.** `data/census/spancache` is **243 MB across 4,990 raw UniProt
entries** and is gitignored. What planning actually needs is the **derived** ends — 24 KB — and
those travel with the repository.

⚠ **`F-076` is what happens without it.** `plan_tiles` read the cache, so a machine that had fetched
spans snapped tile edges and a fresh clone did not. The same parent planned two different tilings
depending on who ran it, and five tests asserted a geometry that was true only on CI.

⚠ Regenerating requires the spancache. A machine without it cannot rebuild the pin and **should not
try** — `--check` will say so rather than writing an empty file over a good one.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from core.hold48 import (                                  # noqa: E402
    PINNED_DOMAIN_ENDS,
    UNIPROT_CACHE,
    domain_ends_span_relative,
    hold48_rows,
)


def build() -> dict:
    entries, missing = {}, []
    for row in hold48_rows():
        src = UNIPROT_CACHE / f"{row.accession}.json"
        if not src.is_file():
            missing.append(row.accession)
            continue
        ends = domain_ends_span_relative(
            accession=row.accession, span_start=row.span_start,
            span_end=row.span_end, cache_dir=UNIPROT_CACHE)
        entries[row.accession] = {
            "span_start": row.span_start,
            "span_end": row.span_end,
            "domain_ends": list(ends),
            "source_sha256": hashlib.sha256(src.read_bytes()).hexdigest(),
        }
    return {"entries": entries, "_missing": missing}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)

    if not UNIPROT_CACHE.is_dir():
        print(f"refusing: {UNIPROT_CACHE} is absent. This machine cannot rebuild the pin, and an "
              f"empty pin written over a good one is worse than no pin.", file=sys.stderr)
        return 2

    built = build()
    if built["_missing"]:
        print(f"refusing: no cache entry for {built['_missing']}. A partial pin would make "
              f"planning deterministic for some parents and not others.", file=sys.stderr)
        return 1

    current = {}
    if PINNED_DOMAIN_ENDS.is_file():
        current = json.loads(PINNED_DOMAIN_ENDS.read_text(encoding="utf-8")).get("entries", {})

    drift = [a for a in built["entries"]
             if current.get(a, {}).get("domain_ends") != built["entries"][a]["domain_ends"]]
    print(f"accessions: {len(built['entries'])}   drifted vs the committed pin: {len(drift)}")
    for a in drift[:10]:
        print(f"   {a}: pinned {current.get(a, {}).get('domain_ends')} -> "
              f"built {built['entries'][a]['domain_ends']}")

    if args.check or not args.write:
        print("\n--check: nothing written." if args.check else "\nno --write: nothing written.")
        return 1 if drift else 0

    doc = {
        "_note": "D-165: the hold-48 domain ends, pinned so tile geometry is deterministic from a "
                 "fresh clone. Derived from data/census/spancache, which is 243 MB of raw UniProt "
                 "entries and gitignored. Regenerate with scripts/pin_hold48_domain_ends.py.",
        "_derived": "core.hold48.domain_ends_span_relative",
        "_generated": "2026-09-15",
        "entries": built["entries"],
    }
    PINNED_DOMAIN_ENDS.write_text(json.dumps(doc, indent=1, sort_keys=True) + "\n",
                                  encoding="utf-8")
    print(f"\nwrote {PINNED_DOMAIN_ENDS.name}: {len(built['entries'])} accessions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
