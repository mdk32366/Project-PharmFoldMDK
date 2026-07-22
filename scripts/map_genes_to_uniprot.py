#!/usr/bin/env python3
"""Map gene symbols to reviewed human UniProt accessions — and report what it cannot
resolve (D-020).

The mapping is trusted NOT because it is automated but because it reports its misses.
A hand-curated list has the same error rate with none of the flags — the seed's MUC4
(for CLDN18.2) and PTPRU (for NECTIN4) were confident and wrong. Everything here is
built so that an unresolved or renamed symbol is a visible flag, never a silent guess.

Method (per accession, against the UniProtKB REST search API):
  query  (gene_exact:<SYMBOL>) AND (organism_id:9606) AND (reviewed:true)
  - **reviewed only** (SwissProt) — no TrEMBL noise.
  - **taxon 9606 pinned** — UniProt will otherwise return plausible-looking orthologs.
  - exactly 1 hit whose PRIMARY gene equals the requested symbol -> clean.
  - 1 hit matched via a SYNONYM (primary differs) -> flag `renamed`: the paper's symbol
    is now a synonym; the primary is the current name. A real, fixable finding.
  - >1 reviewed hit -> flag `ambiguous`; list all candidates, pick nothing.
  - 0 hits -> retry with (gene:<SYMBOL>) to tell `deprecated` (a synonym/older symbol
    that resolves loosely) from `absent` (no reviewed human entry at all).

The census (requested symbol in, returned PRIMARY symbol out, asserted equal) runs on
ALL rows, not a sample — that is the check that would have caught both seed errors.

stdlib only: it reads the committed cohort of record (data/cohort_82.txt), so it is
reproducible without the openpyxl/xlsx step that produced that file.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from urllib.parse import quote
from urllib.request import Request, urlopen

SEARCH = "https://rest.uniprot.org/uniprotkb/search"
UA = "PharmFoldMDK/0.1 (course project; UniProt REST client)"
PAUSE = 0.3


def _search(query: str, fields: str) -> list[dict]:
    url = f"{SEARCH}?query={quote(query)}&fields={fields}&format=json&size=25"
    with urlopen(Request(url, headers={"User-Agent": UA}), timeout=30) as r:
        return json.loads(r.read().decode("utf-8")).get("results", [])


def _primary_and_synonyms(entry: dict) -> tuple[str, list[str]]:
    genes = entry.get("genes") or [{}]
    primary = (genes[0].get("geneName") or {}).get("value", "")
    syns = [s.get("value", "") for s in (genes[0].get("synonyms") or [])]
    return primary, syns


def map_symbol(symbol: str) -> dict:
    fields = "accession,gene_primary,gene_synonym,protein_name"
    hits = _search(f"(gene_exact:{symbol}) AND (organism_id:9606) AND (reviewed:true)", fields)
    rec = {"symbol": symbol, "accession": "", "primary": "", "protein": "",
           "status": "", "note": "", "candidates": ""}

    if len(hits) == 1:
        acc = hits[0].get("primaryAccession", "")
        primary, syns = _primary_and_synonyms(hits[0])
        protein = ((hits[0].get("proteinDescription") or {}).get("recommendedName") or {}).get("fullName", {}).get("value", "")
        rec.update(accession=acc, primary=primary, protein=protein)
        # THE CENSUS: requested symbol vs returned primary (case-insensitive).
        if primary.upper() == symbol.upper():
            rec["status"] = "clean"
        elif symbol.upper() in {s.upper() for s in syns}:
            rec["status"] = "renamed"          # matched via synonym; primary has changed
            rec["note"] = f"requested {symbol!r} is now a synonym of primary {primary!r}"
        else:
            rec["status"] = "mismatch"          # matched but neither primary nor a listed synonym
            rec["note"] = f"returned primary {primary!r} != requested {symbol!r}"
        return rec

    if len(hits) > 1:
        # Primary-match rule: a synonym-only hit is a DIFFERENT gene, never a candidate.
        # Keep only hits whose primary gene equals the requested symbol.
        primary_hits = [h for h in hits if _primary_and_synonyms(h)[0].upper() == symbol.upper()]
        cands = "; ".join(f"{h.get('primaryAccession','')}({_primary_and_synonyms(h)[0]})" for h in hits)
        if len(primary_hits) == 1:
            h = primary_hits[0]
            protein = ((h.get("proteinDescription") or {}).get("recommendedName") or {}).get("fullName", {}).get("value", "")
            rec.update(accession=h.get("primaryAccession", ""),
                       primary=_primary_and_synonyms(h)[0], protein=protein,
                       status="resolved_primary", candidates=cands,
                       note=f"{len(hits)} reviewed hits; exactly one primary-matches — synonym-only hits discarded")
        else:
            # 0 or >=2 primary matches -> a GENUINE ambiguity; pick nothing, escalate.
            rec.update(status="ambiguous", candidates=cands,
                       note=f"{len(hits)} reviewed hits, {len(primary_hits)} primary-match — needs a human")
        return rec

    # 0 hits — distinguish a deprecated/synonym symbol from a genuine absence.
    loose = _search(f"(gene:{symbol}) AND (organism_id:9606) AND (reviewed:true)", fields)
    if loose:
        cands = []
        for h in loose[:10]:
            p, _ = _primary_and_synonyms(h)
            cands.append(f"{h.get('primaryAccession','')}({p})")
        rec.update(status="deprecated", candidates="; ".join(cands),
                   note="no exact-gene match; resolves loosely — likely renamed/synonym")
    else:
        rec.update(status="absent", note="no reviewed human entry for this symbol")
    return rec


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("infile", help="gene symbols, one per line (# comments ok)")
    ap.add_argument("--out", default="cohort_mapping.csv")
    args = ap.parse_args()

    symbols = []
    for line in open(args.infile, encoding="utf-8"):
        line = line.strip()
        if line and not line.startswith("#"):
            symbols.append(line.split()[0])

    print(f"Mapping {len(symbols)} symbols (reviewed, human 9606)...", file=sys.stderr)
    recs = []
    for i, sym in enumerate(symbols, 1):
        try:
            rec = map_symbol(sym)
        except Exception as e:  # noqa: BLE001
            rec = {"symbol": sym, "accession": "", "primary": "", "protein": "",
                   "status": "error", "note": f"{type(e).__name__}: {e}", "candidates": ""}
        recs.append(rec)
        print(f"  [{i}/{len(symbols)}] {sym:<12} {rec['status']:<10} {rec['accession']:<10} {rec['note']}", file=sys.stderr)
        time.sleep(PAUSE)

    with open(args.out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["symbol", "accession", "primary", "protein", "status", "note", "candidates"])
        w.writeheader()
        w.writerows(recs)

    counts: dict[str, int] = {}
    for r in recs:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    print("\n" + "=" * 60)
    print("MAPPING SUMMARY")
    print("=" * 60)
    for k in ("clean", "resolved_primary", "renamed", "ambiguous", "deprecated", "absent", "mismatch", "error"):
        if counts.get(k):
            print(f"  {k:<11} {counts[k]:>3}")
    print(f"  {'TOTAL':<11} {len(recs):>3}")
    flagged = [r for r in recs if r["status"] != "clean"]
    if flagged:
        print("\nFLAGGED (need a human decision before use):")
        for r in flagged:
            print(f"  {r['symbol']:<12} [{r['status']}] {r['note']}"
                  + (f"  candidates: {r['candidates']}" if r["candidates"] else ""))
    print(f"\nWrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
