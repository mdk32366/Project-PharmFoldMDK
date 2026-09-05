"""The census rows that were NEVER FOLDED — shown, not hidden.

⚠⚠ WHY THIS EXISTS. The census table listed only folded proteins, so searching `HER2` returned
"no protein matches that search". HER2 is in the manifest; it was never folded. **A reader had to
parse a paragraph of fine print to learn that the protein they asked for exists.** The owner's
ruling: show it in the list with a status of NOT FOLDED.

⚠ AN ABSENCE WITH A STATUS BEATS AN ABSENCE WITH AN EXPLANATION. A paragraph saying "some proteins
are not folded" makes the reader do the join; a row saying `not folded — above the local GPU
ceiling` puts the answer where the question was asked.

⚠⚠ AND THE REASONS ARE NOT POOLED. Measured over the 777:
    427  above_local_ceiling   — measured to exceed what the local GPU can fold
    349  ceiling_unmeasured    — ⚠ NOT proven too large; nobody has tested this band
      1  reason_unrecorded     — ⚠⚠ `P55073`/`DIO3`, `tier: local`, span 237 aa. It should have
                                 folded and did not, and NOTHING RECORDS WHY.
*"Too big" and "never tested" are different claims, and the third is a defect rather than either.*
"""
from __future__ import annotations

import csv
import functools
import json
import pathlib

from core.hold48 import MUCIN_ACCESSIONS

MANIFEST = pathlib.Path("data/census/census_manifest.v7.csv")
FEATURES = pathlib.Path("data/census/census_features.v1.jsonl")
LABELS = pathlib.Path("data/census/census_labels.csv")

#: ⚠ Plain English, because the surface is read by people who do not know what a tier is.
REASON_COPY = {
    # ⚠ D-118: rental for the hold-48 remainder closed 2026-09-05 PT (pod Terminated).
    # "waiting on rented capacity" is a live-queue claim and is forbidden here.
    "above_local_ceiling": ("not folded — its extracellular stretch is longer than the local "
                            "graphics card can fold. Rental for the hold-48 remainder closed "
                            "2026-09-05 (pod Terminated); this is not waiting on rented capacity"),
    "ceiling_unmeasured": ("not folded — it sits in a size band nobody has tested yet, so it is "
                           "not known to be too large, only untried"),
    "reason_unrecorded": ("not folded — and ⚠ nothing records why. It was assigned to the local "
                          "tier and should have folded"),
    "mucin_out_of_class": ("mucin — out of class; never ESMFold (D-111). "
                           "Not waiting on rented capacity"),
}


def _reason(tier_reason: str) -> str:
    t = (tier_reason or "").strip()
    if t == "over_local_ceiling":
        return "above_local_ceiling"
    if t == "unmeasured_local_ceiling":
        return "ceiling_unmeasured"
    # ⚠⚠ NOT defaulted into one of the two above. An unexplained absence is its own category, and
    # folding it into "too big" would invent a fact about a protein nobody measured.
    return "reason_unrecorded"


@functools.lru_cache(maxsize=1)
def _aliases() -> dict:
    """⚠ Accession -> other names. A never-folded row needs these MORE than a folded one: it is
    the row a reader reaches for by its clinical name (`HER2`), not by its HGNC symbol."""
    try:
        from core.protein_aliases import aliases_by_accession
        return aliases_by_accession()
    except Exception:                      # noqa: BLE001
        return {}


@functools.lru_cache(maxsize=1)
def unfolded_rows() -> list[dict]:
    """Every manifest row with no fold, shaped like a census row so one table holds both."""
    if not (MANIFEST.exists() and FEATURES.exists()):
        return []
    folded = set()
    for line in FEATURES.read_text(encoding="utf-8").splitlines():
        acc = json.loads(line).get("accession")
        if acc:
            folded.add(acc)
    labels = {}
    if LABELS.exists():
        with LABELS.open(encoding="utf-8") as fh:
            labels = {r["census_accession"]: r for r in csv.DictReader(fh)}

    out: list[dict] = []
    with MANIFEST.open(encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            acc = r["census_accession"]
            if acc in folded:
                continue
            lab = labels.get(acc, {})
            cause = ("mucin_out_of_class" if acc in MUCIN_ACCESSIONS
                     else _reason(r.get("tier_reason", "")))
            out.append({
                # ⚠ NO `id`: there is no analysis row, so there is nothing to link to. The surface
                # renders these unlinked rather than inventing a route that would 404.
                "id": None,
                "accession": acc,
                "gene": lab.get("gene") or None,
                "label": lab.get("label") or None,
                "span_aa": int(r["span_aa"]) if r.get("span_aa") else None,
                "census_class": r.get("census_class"),
                "tranche": None,
                # ⚠⚠ THE FIELD THE WHOLE TABLE BRANCHES ON.
                "folded": False,
                "not_folded_reason": cause,
                "not_folded_copy": REASON_COPY[cause],
                "structure_kind": "mucin" if cause == "mucin_out_of_class" else None,
                "structure_kind_label": (
                    "mucin — not folded" if cause == "mucin_out_of_class" else None),
                # ⚠ Everything measured FROM a fold is absent, and absent as a category — never 0,
                # never "unknown". There is no structure, so there is no confidence and no profile.
                "mean_plddt": None,
                "topology": None,
                # ⚠ a CATEGORY, not None: "no fold to profile" is not "profile refused"
                "profile_status": "not_folded",
                "staining": None,
                # ⚠⚠ ALIASES, AND LEAVING THEM None WAS THE BUG THAT MADE THIS WHOLE CHANGE USELESS.
                # The row for ERBB2 existed and `HER2` still returned nothing, because the alias
                # index is what joins the two — so the protein the owner asked for was in the table
                # and still unreachable by the name they typed. A row nobody can find is not shown.
                "aliases": _aliases().get(acc) or None,
                "surface_check": None,
                "scored": False,
            })
    return out


def counts_by_reason() -> dict[str, int]:
    """⚠ For the surface, so the split is stated rather than implied."""
    c: dict[str, int] = {}
    for r in unfolded_rows():
        c[r["not_folded_reason"]] = c.get(r["not_folded_reason"], 0) + 1
    return c
