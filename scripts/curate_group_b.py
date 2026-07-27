#!/usr/bin/env python3
"""
curate_group_b.py — assemble CANDIDATE evidence for the Group B roster (D-040).

WHAT THIS DOES NOT DO
---------------------
It does not label anything. D-040 decision 1 reserves the classification judgement to the owner,
and the six calibration cases (NOTCH2, CSF1R, OSMR, IGF2R, SORT1, ENPP5) each turn on reading a
description and deciding what kind of molecule it is. No heuristic makes that call here.

It never emits `is_group_b = false`. A registry with no matching trial is not evidence that no ADC
exists: ClinicalTrials.gov holds no preclinical work, and PODXL is in the roster ONLY because of a
preclinical ADC that will never appear in any trial registry. A confident `false` generated from
registry silence would be worse than a blank, because a blank announces its own ignorance.

Stages (run independently, each cached to disk):
    aliases   UniProt accession -> gene synonyms and alternative protein names
    search    ClinicalTrials.gov v2 -> trials whose interventions match those aliases
    sheet     emit a review CSV for the owner

Usage:
    python scripts/curate_group_b.py probe            # validate both APIs before a real run
    python scripts/curate_group_b.py aliases
    python scripts/curate_group_b.py search
    python scripts/curate_group_b.py sheet
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
COHORT_MAPPING = REPO / "data" / "cohort_82_mapping.csv"
CACHE = REPO / "data" / "derived"
ALIASES_JSON = CACHE / "target_aliases.json"
TRIALS_JSON = CACHE / "group_b_trial_hits.json"
REVIEW_CSV = CACHE / "adc_reference_mapping_REVIEW.csv"

UNIPROT = "https://rest.uniprot.org/uniprotkb/{accession}.json"
CTG = "https://clinicaltrials.gov/api/v2/studies"


def _http():
    """Deferred import (D-057 §1): `requests` is in no requirements file in this repo, so importing
    it at module scope would fail pytest collection and redden the gate. The pure functions the tests
    exercise (`classify_evidence`, `parse_uniprot_aliases`) never call this; only the network stages
    do, and they run offline-of-CI, once, by hand."""
    import requests
    return requests

# ~50 requests/minute per IP is the documented ceiling; stay well under it.
REQUEST_PAUSE_S = 1.5
TIMEOUT_S = 30

# --------------------------------------------------------------------------------------
# Modality evidence. These produce FLAGS, never decisions.
# --------------------------------------------------------------------------------------

# International nonproprietary-name stems for cytotoxic payloads carried by ADCs.
ADC_PAYLOAD_STEMS = (
    "vedotin",       # MMAE
    "mafodotin",     # MMAF
    "emtansine",     # DM1
    "ravtansine",    # DM4
    "soravtansine",  # DM4
    "deruxtecan",    # DXd
    "govitecan",     # SN-38
    "ozogamicin",    # calicheamicin
    "tesirine",      # PBD dimer
    "duocarmazine",  # duocarmycin
    "tirumotecan",   # topo-I
)
ADC_PHRASES = (
    "antibody-drug conjugate", "antibody drug conjugate",
    "antibody-drug-conjugate", "immunoconjugate",
)
RADIO_MARKERS = (
    "radioimmunoconjugate", "radiolabeled", "radiolabelled", "radioconjugate",
    "lutetium", "177lu", "lu-177", "actinium", "225ac", "ac-225",
    "zirconium", "89zr", "iodine-131", "i-131", "yttrium-90", "90y",
)
PEPTIDE_CONJUGATE_MARKERS = (
    "peptide-drug conjugate", "peptide drug conjugate", "peptide conjugate",
)
IMMUNOTOXIN_MARKERS = ("immunotoxin", "pasudotox")

_MAB_SUFFIX = re.compile(r"\b\w+mab\b", re.IGNORECASE)


def classify_evidence(text: str) -> dict:
    """Flag what a trial's text *looks* like. Returns evidence, never a label.

    `suggested_status` is a routing hint for the reviewer's attention only. It is deliberately
    never 'false' and never 'true' — see the module docstring.
    """
    t = (text or "").lower()
    flags = []

    if any(stem in t for stem in ADC_PAYLOAD_STEMS):
        flags.append("adc_payload_stem")
    if any(p in t for p in ADC_PHRASES):
        flags.append("adc_phrase")
    if any(m in t for m in RADIO_MARKERS):
        flags.append("radioimmunoconjugate_suspected")
    if any(m in t for m in PEPTIDE_CONJUGATE_MARKERS):
        flags.append("peptide_drug_conjugate_suspected")
    if any(m in t for m in IMMUNOTOXIN_MARKERS):
        flags.append("immunotoxin_suspected")

    looks_adc = "adc_payload_stem" in flags or "adc_phrase" in flags
    if _MAB_SUFFIX.search(t) and not looks_adc:
        flags.append("naked_antibody_suspected")

    # ⚠ Exclusion markers take precedence over ADC phrasing, and this is not a stylistic choice.
    # "radioimmunoconjugate" CONTAINS "immunoconjugate"; without this rule the IGF2R case routes as
    # a probable positive — the precise error D-040's definition exists to prevent. A caught
    # exclusion marker means the reviewer must look at the molecule, whatever else matched.
    excluded = {
        "radioimmunoconjugate_suspected",
        "peptide_drug_conjugate_suspected",
        "immunotoxin_suspected",
    } & set(flags)

    if excluded:
        suggested = "review_as_probable_exclusion"
    elif looks_adc:
        suggested = "review_as_probable_group_b"
    elif flags:
        suggested = "review_as_probable_exclusion"
    else:
        suggested = "review_unclear"

    return {"flags": sorted(set(flags)), "suggested_status": suggested}


# --------------------------------------------------------------------------------------
# Aliases
# --------------------------------------------------------------------------------------

def read_cohort() -> list[tuple[str, str]]:
    with COHORT_MAPPING.open(newline="", encoding="utf-8") as f:
        rows = [r for r in csv.DictReader(f)]
    return [(r["symbol"].strip(), r["accession"].strip()) for r in rows]


def parse_uniprot_aliases(symbol: str, payload: dict) -> list[str]:
    """Pull gene synonyms and alternative protein names. The symbol is ALWAYS included, so a
    UniProt miss degrades the query rather than emptying it."""
    out = {symbol}
    for gene in payload.get("genes", []) or []:
        name = (gene.get("geneName") or {}).get("value")
        if name:
            out.add(name)
        for syn in gene.get("synonyms", []) or []:
            if syn.get("value"):
                out.add(syn["value"])
    desc = payload.get("proteinDescription", {}) or {}
    for alt in desc.get("alternativeNames", []) or []:
        full = (alt.get("fullName") or {}).get("value")
        if full:
            out.add(full)
        for short in alt.get("shortNames", []) or []:
            if short.get("value"):
                out.add(short["value"])
    # Single characters and pure numbers make useless free-text queries.
    return sorted(a for a in out if len(a) > 2 and not a.isdigit())


def stage_aliases() -> None:
    CACHE.mkdir(parents=True, exist_ok=True)
    result, failures = {}, []
    for symbol, accession in read_cohort():
        try:
            r = _http().get(UNIPROT.format(accession=accession), timeout=TIMEOUT_S)
            r.raise_for_status()
            result[symbol] = parse_uniprot_aliases(symbol, r.json())
        except Exception as exc:  # noqa: BLE001 - degrade, never crash the batch
            failures.append(f"{symbol} ({accession}): {exc}")
            result[symbol] = [symbol]
        time.sleep(REQUEST_PAUSE_S)
    ALIASES_JSON.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    print(f"aliases -> {ALIASES_JSON}  ({len(result)} targets)")
    if failures:
        print(f"⚠ {len(failures)} UniProt lookups failed; those fell back to the symbol alone:")
        for f in failures:
            print(f"   {f}")


# --------------------------------------------------------------------------------------
# Trial search
# --------------------------------------------------------------------------------------

def ctg_query(term: str, page_size: int = 50) -> list[dict]:
    params = {
        "query.term": term,
        "pageSize": page_size,
        "format": "json",
        "countTotal": "true",
    }
    r = _http().get(CTG, params=params, timeout=TIMEOUT_S)
    r.raise_for_status()
    return r.json().get("studies", []) or []


def summarise_study(study: dict) -> dict:
    proto = study.get("protocolSection", {}) or {}
    ident = proto.get("identificationModule", {}) or {}
    arms = proto.get("armsInterventionsModule", {}) or {}
    interventions = arms.get("interventions", []) or []
    names = [i.get("name", "") for i in interventions]
    descs = [i.get("description", "") for i in interventions]
    return {
        "nct_id": ident.get("nctId", ""),
        "title": ident.get("briefTitle", ""),
        "interventions": [n for n in names if n],
        "text": " ".join([ident.get("briefTitle", ""), *names, *descs]),
    }


def stage_search() -> None:
    if not ALIASES_JSON.exists():
        sys.exit("run the `aliases` stage first")
    aliases = json.loads(ALIASES_JSON.read_text(encoding="utf-8"))
    hits: dict[str, list[dict]] = {}
    for symbol, names in sorted(aliases.items()):
        seen, collected = set(), []
        # Query the symbol and the two most specific aliases; more queries buy noise, not recall.
        for term in [symbol, *[n for n in names if n != symbol][:2]]:
            try:
                studies = ctg_query(f'{term} AND ("conjugate" OR "ADC")')
            except Exception as exc:  # noqa: BLE001
                print(f"⚠ {symbol}: query {term!r} failed: {exc}")
                continue
            for s in studies:
                summary = summarise_study(s)
                if not summary["nct_id"] or summary["nct_id"] in seen:
                    continue
                seen.add(summary["nct_id"])
                summary["evidence"] = classify_evidence(summary["text"])
                summary["matched_term"] = term
                collected.append(summary)
            time.sleep(REQUEST_PAUSE_S)
        hits[symbol] = collected
        print(f"{symbol}: {len(collected)} candidate trials")
    TRIALS_JSON.write_text(json.dumps(hits, indent=2, sort_keys=True), encoding="utf-8")
    print(f"trials -> {TRIALS_JSON}")


# --------------------------------------------------------------------------------------
# Review sheet
# --------------------------------------------------------------------------------------

HEADER = """# CANDIDATE evidence for the Group B roster — FOR OWNER REVIEW. NOT a label set.
# Generated by scripts/curate_group_b.py. Every row needs a human decision.
#
# `is_group_b` is INTENTIONALLY BLANK on every row. This script does not label; D-040 dec. 1
# reserves that judgement to the owner.
#
# ⚠ NO TRIALS FOUND DOES NOT MEAN NO ADC. ClinicalTrials.gov holds no preclinical work. PODXL is a
#   Group B positive on the strength of a preclinical ADC that appears in no registry. Rows with no
#   hits are `needs_literature_check` — they are NOT negatives and must not be filled in as false
#   on this file's evidence alone.
#
# `evidence_flags` are pattern matches on trial text, not determinations. `adc_payload_stem` means
#   an INN payload stem (vedotin, deruxtecan, emtansine, ...) appeared. `naked_antibody_suspected`
#   means a -mab name appeared with no conjugate stem. Both can be wrong; open the NCT record.
"""


def stage_sheet() -> None:
    if not TRIALS_JSON.exists():
        sys.exit("run the `search` stage first")
    hits = json.loads(TRIALS_JSON.read_text(encoding="utf-8"))
    with REVIEW_CSV.open("w", newline="", encoding="utf-8") as f:
        f.write(HEADER)
        w = csv.writer(f)
        w.writerow([
            "symbol", "is_group_b", "agent_name", "development_stage",
            "source_citation", "exclusion_reason", "curation_status",
            "evidence_flags", "nct_ids", "trial_titles",
        ])
        for symbol, trials in sorted(hits.items()):
            if not trials:
                w.writerow([symbol, "", "", "", "", "", "needs_literature_check", "", "", ""])
                continue
            flags = sorted({fl for t in trials for fl in t["evidence"]["flags"]})
            probable = any(
                t["evidence"]["suggested_status"] == "review_as_probable_group_b" for t in trials
            )
            ncts = [t["nct_id"] for t in trials][:8]
            agents = sorted({i for t in trials for i in t["interventions"]})[:6]
            w.writerow([
                symbol, "", "; ".join(agents), "",
                "ClinicalTrials.gov: " + ", ".join(ncts), "",
                "review_as_probable_group_b" if probable else "review_as_probable_exclusion",
                "; ".join(flags), ", ".join(ncts),
                " | ".join(t["title"] for t in trials[:3]),
            ])
    print(f"review sheet -> {REVIEW_CSV}")


# --------------------------------------------------------------------------------------
# Probe — validate the world before trusting a 200-request run against it
# --------------------------------------------------------------------------------------

def stage_probe() -> None:
    ok = True

    print("probing UniProt (P78536 / ADAM17) ...")
    try:
        r = _http().get(UNIPROT.format(accession="P78536"), timeout=TIMEOUT_S)
        r.raise_for_status()
        aliases = parse_uniprot_aliases("ADAM17", r.json())
        print(f"  OK — {len(aliases)} aliases, e.g. {aliases[:4]}")
        if len(aliases) < 2:
            print("  ⚠ only the symbol came back; the response shape may have changed")
            ok = False
    except Exception as exc:  # noqa: BLE001
        print(f"  FAILED: {exc}")
        ok = False

    print("probing ClinicalTrials.gov (known-positive control: enfortumab vedotin) ...")
    try:
        studies = ctg_query("enfortumab vedotin", page_size=5)
        if not studies:
            print("  ⚠ zero results for a known marketed ADC — query syntax is wrong")
            ok = False
        else:
            s = summarise_study(studies[0])
            ev = classify_evidence(s["text"])
            print(f"  OK — {len(studies)} studies, first {s['nct_id']}: {s['title'][:70]}")
            print(f"       flags: {ev['flags']}")
            if "adc_payload_stem" not in ev["flags"]:
                print("  ⚠ control did not trip the ADC stem flag — check field extraction")
                ok = False
    except Exception as exc:  # noqa: BLE001
        print(f"  FAILED: {exc}")
        ok = False

    print("\nPROBE PASSED" if ok else "\nPROBE FAILED — fix before running the full pass")
    sys.exit(0 if ok else 1)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("stage", choices=["probe", "aliases", "search", "sheet"])
    args = p.parse_args()
    {"probe": stage_probe, "aliases": stage_aliases,
     "search": stage_search, "sheet": stage_sheet}[args.stage]()


if __name__ == "__main__":
    main()
