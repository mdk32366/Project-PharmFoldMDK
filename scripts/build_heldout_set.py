#!/usr/bin/env python3
"""scripts/build_heldout_set.py — Phase A: build `data/heldout_positives.csv`.

The held-out validation set: clinically-validated ADC targets **absent from the Kathad 82**. Its
purpose is to test generalization — whether the structural axis says anything about ADC targets it
was never fitted on.

⚠ **ZERO RECALLED IDENTIFIERS** (order dec 3). Every accession is resolved live from the **UniProt**
REST API; every clinical phase and its citable URL come from the **ClinicalTrials.gov** API. This
script's own tables contain only *queries* — a gene symbol to look up and a drug name to search.
The drug→antigen pairing is the one human claim, and each row carries the registry study title that
evidences it.

⚠ **THE DEFINING PROPERTY** (order dec 1): every emitted row is **disjoint from the 82 by
ACCESSION**, asserted before the file is written. Checking by *symbol* would not do — a cohort
member under a different symbol would masquerade as held-out. A candidate that resolves into the
cohort is screened out **with its reason printed**; if one ever survives into the output, the
assertion aborts the build. That is the bug the order names, and it has fired once in anger:
**vobramitamab duocarmazine / CD276 (Q5ZPR3) is a cohort member**, caught on the first run.

⚠ **WHAT THIS INSTRUMENT GETS WRONG** (D-074 dec 3), stated in itself rather than only in the log:
- **The candidate list is not exhaustive.** It is a hand-assembled roster of approved and late-phase
  ADCs. A real ADC absent from `DRUG_CANDIDATES` is invisible to this script and will be silently
  missing from the output. Absence from the CSV is **not** evidence of absence from the field.
- **`clinical_status` carries the trial's overall status on purpose.** Reaching phase 3 and
  *finishing* it are different claims; several rows have TERMINATED lead trials. "Clinically
  validated" here means *the antigen was prosecuted into late-phase trials*, never that the agent
  succeeded.
- **Phase is per-agent, not per-target.** A target whose furthest agent is phase 1 is excluded even
  if another sponsor is further along with an agent not listed here.
- **Registry search is by intervention name.** An agent indexed only under a code name this table
  does not use returns no hit and is recorded as unverified, not as phase 0.

⚠ **NO OVER-CLAIM** (order dec 3 / F-009 §3): this set tests generalization. It does **not**
retroactively validate the scorer, and no artifact may say "our method would have caught these."

⚠ **PHASE A IS CURATION ONLY.** No folds, no scoring, no run. Phase B (fold + validate) is **gated
on D-075 surviving** and requires explicit owner authorisation citing that survival.

Standard library only; offline; `scripts/` is in `.dockerignore` so this never reaches the image.

Usage:
    python scripts/build_heldout_set.py            # queries both APIs, rewrites the CSV
    python scripts/build_heldout_set.py --dry-run  # report only, write nothing
"""
from __future__ import annotations

import argparse
import csv
import json
import pathlib
import sys
import time
import urllib.parse
import urllib.request

REPO = pathlib.Path(__file__).resolve().parent.parent
OUT = REPO / "data" / "heldout_positives.csv"
VERIFIED_DATE = "2026-08-01"        # stated, not read from the clock — a date captured by accident
                                    # is not a verification date (same discipline as D-075 dec 3)

UNIPROT = ("https://rest.uniprot.org/uniprotkb/search"
           "?query=gene_exact:{sym}+AND+organism_id:9606+AND+reviewed:true"
           "&fields=accession,protein_name,gene_primary,length&format=json&size=5")
CTGOV = ("https://clinicaltrials.gov/api/v2/studies?query.intr={drug}"
         "&fields=NCTId,BriefTitle,Phase,OverallStatus&pageSize=25&format=json")

PHASE_RANK = {"EARLY_PHASE1": 0, "PHASE1": 1, "PHASE2": 2, "PHASE3": 3, "PHASE4": 4, "NA": -1}
MIN_RANK = 2                        # phase >= 2 (order dec 1: FDA-approved and phase-2/3 ADCs)

# (agent, claimed target gene symbol). Both are QUERIES, not answers: the symbol is looked up in
# UniProt and the agent is searched in the registry. See the exhaustiveness caveat above.
DRUG_CANDIDATES: list[tuple[str, str]] = [
    ("gemtuzumab ozogamicin", "CD33"),          ("brentuximab vedotin", "TNFRSF8"),
    ("inotuzumab ozogamicin", "CD22"),          ("polatuzumab vedotin", "CD79B"),
    ("sacituzumab govitecan", "TACSTD2"),       ("datopotamab deruxtecan", "TACSTD2"),
    ("sacituzumab tirumotecan", "TACSTD2"),     ("belantamab mafodotin", "TNFRSF17"),
    ("loncastuximab tesirine", "CD19"),         ("tisotumab vedotin", "F3"),
    ("mirvetuximab soravtansine", "FOLR1"),     ("luveltamab tazevibulin", "FOLR1"),
    ("rinatabart sesutecan", "FOLR1"),          ("patritumab deruxtecan", "ERBB3"),
    ("tusamitamab ravtansine", "CEACAM5"),      ("telisotuzumab vedotin", "MET"),
    ("rovalpituzumab tesirine", "DLL3"),        ("raludotatug deruxtecan", "CDH6"),
    ("upifitamab rilsodotin", "SLC34A2"),       ("cofetuzumab pelidotin", "PTK7"),
    ("enapotamab vedotin", "AXL"),              ("glembatumumab vedotin", "GPNMB"),
    ("vorsetuzumab mafodotin", "CD70"),         ("naratuximab emtansine", "CD37"),
    ("camidanlumab tesirine", "IL2RA"),         ("sirtratumab vedotin", "LY6E"),
    ("tamrintamab pamozirine", "DPEP3"),        ("zilovertamab vedotin", "ROR1"),
    ("vobramitamab duocarmazine", "CD276"),     ("CMG901", "CLDN18"),
]


def _get(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "PharmFoldMDK-PhaseA/1.0"})
    with urllib.request.urlopen(req, timeout=45) as r:
        return json.loads(r.read().decode("utf-8"))


def resolve_accession(symbol: str) -> dict | None:
    """Gene symbol → reviewed human UniProt entry. Returns None on a miss; never guesses."""
    hits = _get(UNIPROT.format(sym=urllib.parse.quote(symbol))).get("results", [])
    if not hits:
        return None
    h = hits[0]
    return {
        "accession": h["primaryAccession"],
        # UniProt's PRIMARY symbol, which is not always the queried alias (SIGLEC3→CD33, PSMA→FOLH1).
        "primary_symbol": (h.get("genes") or [{}])[0].get("geneName", {}).get("value", ""),
        "protein_name": (h.get("proteinDescription", {}).get("recommendedName", {})
                          .get("fullName", {}).get("value", "")),
        "length": h.get("sequence", {}).get("length"),
    }


def furthest_phase(drug: str) -> dict | None:
    """The furthest-phase registry study for an agent, with its NCT id, title and overall status."""
    studies = _get(CTGOV.format(drug=urllib.parse.quote(drug))).get("studies", [])
    best, best_rank = None, -2
    for s in studies:
        pr = s.get("protocolSection", {})
        phases = pr.get("designModule", {}).get("phases", []) or ["NA"]
        rank = max(PHASE_RANK.get(p, -1) for p in phases)
        if rank > best_rank:
            best_rank, best = rank, {
                "rank": rank,
                "max_phase": "/".join(phases),
                "nct": pr.get("identificationModule", {}).get("nctId"),
                "title": pr.get("identificationModule", {}).get("briefTitle", ""),
                "overall_status": pr.get("statusModule", {}).get("overallStatus", "UNKNOWN"),
            }
    return best


HEADER = f"""\
# Phase A (held-out validation set) - clinically-validated ADC targets ABSENT from the Kathad 82.
# Built {VERIFIED_DATE} by scripts/build_heldout_set.py. CURATION ONLY - no folds, no scoring, no run.
#
# HOW EACH FIELD IS KNOWN (D-016). uniprot_accession: resolved live from the UniProt REST API
#   (gene_exact + organism_id:9606 + reviewed:true), never recalled. gene_symbol is UniProt's PRIMARY
#   symbol, which is not always the queried alias (SIGLEC3 -> CD33). clinical_status + source_url:
#   ClinicalTrials.gov API v2, the furthest-phase study found for that agent.
#
# DEFINING PROPERTY: every row is DISJOINT FROM THE 82 BY ACCESSION - asserted in the build, not
#   eyeballed. Checking by symbol would not do: a cohort member under a different symbol would
#   masquerade as held-out. This fired in anger - vobramitamab duocarmazine / CD276 (Q5ZPR3) is a
#   cohort member and was screened out.
#
# ONE ROW PER TARGET, carrying the agent that reaches the furthest phase. This is a TARGET set, not
#   a drug roster; other agents against the same antigen are not listed.
#
# INCLUSION: registry-confirmed phase >= 2. Anything below, or with no registry hit, is EXCLUDED and
#   named in the build log - a recorded exclusion, not an unexamined gap.
#
# ⚠ clinical_status CARRIES THE TRIAL'S OVERALL STATUS ON PURPOSE. Reaching phase 3 and FINISHING it
#   are different claims, and four rows have a TERMINATED lead trial (CEACAM5, DLL3, SLC34A2, IL2RA).
#   "Clinically validated" here means THE ANTIGEN WAS PROSECUTED INTO LATE-PHASE TRIALS - it does NOT
#   mean the agent succeeded. Phase alone would have implied a success no source supports.
#
# ⚠ ONE BORDERLINE INCLUSION, NAMED: AXL (enapotamab vedotin) is PHASE1/PHASE2. It satisfies
#   "phase >= 2" only because a phase-1/2 trial contains a phase-2 arm. Flagged for an owner ruling
#   rather than silently kept or silently dropped.
#
# ⚠ THE CANDIDATE LIST IS NOT EXHAUSTIVE. An ADC absent from DRUG_CANDIDATES is invisible to the
#   build. Absence from this file is NOT evidence of absence from the field.
#
# ⚠ NO OVER-CLAIM (order dec 3 / F-009 section 3): this set tests GENERALIZATION. It does not
#   retroactively validate the scorer, and nothing may say "our method would have caught these".
#
# ⚠ PHASE B (fold + validate) IS GATED on D-075 surviving, and needs explicit owner authorisation
#   citing that survival. Phase A is curation only.
"""


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="python scripts/build_heldout_set.py")
    ap.add_argument("--dry-run", action="store_true", help="report only; write nothing")
    args = ap.parse_args(argv)

    sys.path.insert(0, str(REPO))
    from core.adc_reference import cohort_accessions
    cohort = set(cohort_accessions())
    print(f"cohort accessions: {len(cohort)}   candidates: {len(DRUG_CANDIDATES)}\n")

    resolved: dict[str, dict] = {}
    kept: dict[str, dict] = {}
    dropped: list[tuple[str, str, str]] = []

    for drug, symbol in DRUG_CANDIDATES:
        try:
            ph = furthest_phase(drug)
        except Exception as exc:                                    # noqa: BLE001
            dropped.append((drug, symbol, f"registry query failed: {type(exc).__name__}"))
            continue
        if ph is None:
            dropped.append((drug, symbol, "no registry hit - unverified, NOT phase 0"))
            time.sleep(0.4)
            continue
        if ph["rank"] < MIN_RANK:
            dropped.append((drug, symbol, f"registry max phase {ph['max_phase']} - below phase 2"))
            time.sleep(0.4)
            continue

        if symbol not in resolved:
            try:
                resolved[symbol] = resolve_accession(symbol)
            except Exception as exc:                                # noqa: BLE001
                dropped.append((drug, symbol, f"UniProt query failed: {type(exc).__name__}"))
                continue
            time.sleep(0.4)
        u = resolved[symbol]
        if u is None:
            dropped.append((drug, symbol, "no reviewed human UniProt entry"))
            continue

        acc = u["accession"]
        if acc in cohort:
            dropped.append((drug, symbol, f"IN THE 82 ({acc}) - cohort member, not held-out"))
            continue

        prev = kept.get(acc)
        if prev is None or ph["rank"] > prev["_rank"]:
            kept[acc] = {
                "gene_symbol": u["primary_symbol"] or symbol,
                "uniprot_accession": acc,
                "adc_name": drug,
                "clinical_status": f"{ph['max_phase']} ({ph['overall_status']})",
                "source_url": f"https://clinicaltrials.gov/study/{ph['nct']}",
                "verified_date": VERIFIED_DATE,
                "_rank": ph["rank"], "_len": u.get("length"), "_title": ph["title"],
            }
        time.sleep(0.4)

    rows = sorted(kept.values(), key=lambda r: (-r["_rank"], r["gene_symbol"]))

    # ── the defining property, asserted rather than assumed ──
    accs = [r["uniprot_accession"] for r in rows]
    assert len(accs) == len(set(accs)), "duplicate accession survived the dedupe"
    overlap = set(accs) & cohort
    assert not overlap, (f"BUG: cohort member(s) {overlap} survived into the held-out set - a target "
                         f"in the 82 under another symbol is a bug, not a duplicate (order dec 1)")

    fields = ["gene_symbol", "uniprot_accession", "adc_name", "clinical_status",
              "source_url", "verified_date"]
    print(f"{'symbol':<10} {'acc':<8} {'status':<26} {'len':>5}  agent")
    print("-" * 104)
    for r in rows:
        print(f"{r['gene_symbol']:<10} {r['uniprot_accession']:<8} {r['clinical_status']:<26} "
              f"{str(r['_len']):>5}  {r['adc_name']}")

    print(f"\nEXCLUDED, each with a reason ({len(dropped)}):")
    for d, s, why in dropped:
        print(f"   {d:<28} ({s:<8}) - {why}")
    print(f"\ndisjoint-from-82 asserted: {len(accs)} accessions, 0 overlap with {len(cohort)} cohort")

    if args.dry_run:
        print("\n--dry-run: nothing written")
        return 0
    with OUT.open("w", newline="", encoding="utf-8") as fh:
        fh.write(HEADER)
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({k: r[k] for k in fields})
    print(f"\nwrote {OUT} ({len(rows)} targets)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
