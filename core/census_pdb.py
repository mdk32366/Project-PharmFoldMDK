"""Census experimental PDB metadata selection — D-171.

Metadata-only. Never recomputes structural_score / STRUCTURAL_ONLY.
Never treats a PDB entry as the ranked fold or the served predicted fold.

Selection rules (pinned by ### D-171 and tests):
1. Prefer tax_id=9606; keep non-human only if no human candidate exists.
2. ECD = union of census V2 extracellular segment residues.
   OBS = union of UniProt residue ranges observed in the PDB map.
   ecd_coverage_frac = |ECD ∩ OBS| / |ECD| when |ECD| > 0.
3. Eligible for pdb_best when ECD exists: ecd_coverage_frac >= 0.50.
   Else pdb_best=null and pdb_status=ABSENT_NO_ECD_COVERING_STRUCTURE
   (other ids remain in pdb_ids with fracs).
4. Among eligible: higher frac, better resolution (null last),
   method X-ray > EM > NMR > other, pdb_id ascending.
5. No map: pdb_ids=[], pdb_best=null, pdb_status=ABSENT.
"""
from __future__ import annotations

from typing import Any, Iterable, Optional

ECD_COVER_THRESHOLD = 0.50

STATUS_PRESENT = "present"
STATUS_ABSENT = "ABSENT"
STATUS_ABSENT_NO_ECD = "ABSENT_NO_ECD_COVERING_STRUCTURE"
STATUS_SPAN_ABSENT = "span_absent"
STATUS_INVALID = "invalid"

METHOD_RANK = {
    "x-ray diffraction": 0,
    "x-ray": 0,
    "electron microscopy": 1,
    "em": 1,
    "electron crystallography": 1,
    "solution nmr": 2,
    "solid-state nmr": 2,
    "nmr": 2,
}


def parse_segment_intervals(segments: str | None) -> list[tuple[int, int]]:
    """Parse ``42-483;544-551`` → inclusive intervals."""
    if not segments or not str(segments).strip():
        return []
    out: list[tuple[int, int]] = []
    for part in str(segments).split(";"):
        part = part.strip()
        if not part or "-" not in part:
            continue
        a, b = part.split("-", 1)
        try:
            lo, hi = int(a), int(b)
        except ValueError:
            continue
        if hi < lo:
            lo, hi = hi, lo
        out.append((lo, hi))
    return out


def residue_set(intervals: Iterable[tuple[int, int]]) -> set[int]:
    residues: set[int] = set()
    for lo, hi in intervals:
        residues.update(range(lo, hi + 1))
    return residues


def observed_intervals_from_candidate(cand: dict[str, Any]) -> list[tuple[int, int]]:
    regions = cand.get("observed_regions") or []
    if regions:
        out: list[tuple[int, int]] = []
        for r in regions:
            try:
                lo = int(r["unp_start"])
                hi = int(r["unp_end"])
            except (KeyError, TypeError, ValueError):
                continue
            if hi < lo:
                lo, hi = hi, lo
            out.append((lo, hi))
        if out:
            return out
    # fallback: whole mapped unp range
    try:
        lo = int(cand["unp_start"])
        hi = int(cand["unp_end"])
    except (KeyError, TypeError, ValueError):
        return []
    if hi < lo:
        lo, hi = hi, lo
    return [(lo, hi)]


def method_rank(method: str | None) -> int:
    if not method:
        return 99
    return METHOD_RANK.get(str(method).strip().lower(), 50)


def resolution_sort_key(resolution_A: float | None) -> tuple[int, float]:
    # null sorts last
    if resolution_A is None:
        return (1, 0.0)
    return (0, float(resolution_A))


def ecd_coverage_frac(ecd: set[int], obs: set[int]) -> float | None:
    if not ecd:
        return None
    return len(ecd & obs) / len(ecd)


def rcsb_url(pdb_id: str) -> str:
    return f"https://www.rcsb.org/structure/{pdb_id.upper()}"


def pdbe_url(pdb_id: str) -> str:
    return f"https://www.ebi.ac.uk/pdbe/entry/pdb/{pdb_id.lower()}"


def normalize_candidate(raw: dict[str, Any]) -> dict[str, Any]:
    pdb_id = str(raw.get("pdb_id") or "").lower()
    chain_id = str(raw.get("chain_id") or "")
    method = raw.get("experimental_method") or raw.get("method")
    res = raw.get("resolution")
    if res is raw.get("resolution_A"):
        pass
    resolution_A: float | None
    try:
        resolution_A = float(res) if res is not None else None
    except (TypeError, ValueError):
        resolution_A = None
    tax = raw.get("tax_id")
    try:
        tax_id = int(tax) if tax is not None else None
    except (TypeError, ValueError):
        tax_id = None
    intervals = observed_intervals_from_candidate(raw)
    return {
        "pdb_id": pdb_id,
        "chain_id": chain_id,
        "method": method,
        "resolution_A": resolution_A,
        "tax_id": tax_id,
        "observed_intervals": intervals,
        "raw": raw,
    }


def prefer_human(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    humans = [c for c in candidates if c.get("tax_id") == 9606]
    return humans if humans else list(candidates)


def select_pdb_for_accession(
    *,
    accession: str,
    candidates_raw: list[dict[str, Any]] | None,
    ecd_segments: str | None,
    span_absent: bool = False,
) -> dict[str, Any]:
    """Return paint dict for one accession.

    Keys: pdb_status, pdb_ids, pdb_best, entries (detail list with fracs).
    """
    _ = accession
    if candidates_raw is None:
        return {
            "pdb_status": STATUS_INVALID,
            "pdb_ids": [],
            "pdb_best": None,
            "entries": [],
        }
    if not candidates_raw:
        return {
            "pdb_status": STATUS_ABSENT,
            "pdb_ids": [],
            "pdb_best": None,
            "entries": [],
        }

    ecd_intervals = parse_segment_intervals(ecd_segments)
    ecd = residue_set(ecd_intervals)
    span_is_absent = span_absent or not ecd

    norms = [normalize_candidate(c) for c in candidates_raw]
    norms = [c for c in norms if c["pdb_id"]]
    norms = prefer_human(norms)

    entries: list[dict[str, Any]] = []
    for c in norms:
        obs = residue_set(c["observed_intervals"])
        frac = None if span_is_absent else ecd_coverage_frac(ecd, obs)
        covers = (frac is not None and frac >= ECD_COVER_THRESHOLD)
        entries.append({
            "pdb_id": c["pdb_id"],
            "chain_id": c["chain_id"],
            "method": c["method"],
            "resolution_A": c["resolution_A"],
            "tax_id": c["tax_id"],
            "ecd_coverage_frac": frac,
            "ecd_covers": covers if not span_is_absent else False,
            "unp_start": c["observed_intervals"][0][0] if c["observed_intervals"] else None,
            "unp_end": c["observed_intervals"][-1][1] if c["observed_intervals"] else None,
            "attribution": {
                "source": "PDBe/SIFTS",
                "rcsb_url": rcsb_url(c["pdb_id"]),
                "pdbe_url": pdbe_url(c["pdb_id"]),
            },
        })

    pdb_ids = sorted({e["pdb_id"] for e in entries})

    if span_is_absent:
        # May still pick a best on resolution/method among all candidates.
        ranked = sorted(
            entries,
            key=lambda e: (
                resolution_sort_key(e["resolution_A"]),
                method_rank(e["method"]),
                e["pdb_id"],
                e["chain_id"],
            ),
        )
        best = ranked[0] if ranked else None
        pdb_best = None
        if best:
            pdb_best = {
                "pdb_id": best["pdb_id"],
                "chain_id": best["chain_id"],
                "method": best["method"],
                "resolution_A": best["resolution_A"],
                "ecd_coverage_frac": None,
                "ecd_covers": False,
                "tax_id": best["tax_id"],
                "attribution": best["attribution"],
            }
        return {
            "pdb_status": STATUS_SPAN_ABSENT,
            "pdb_ids": pdb_ids,
            "pdb_best": pdb_best,
            "entries": entries,
        }

    eligible = [e for e in entries if e["ecd_covers"]]
    if not eligible:
        return {
            "pdb_status": STATUS_ABSENT_NO_ECD,
            "pdb_ids": pdb_ids,
            "pdb_best": None,
            "entries": entries,
        }

    eligible_sorted = sorted(
        eligible,
        key=lambda e: (
            -(e["ecd_coverage_frac"] or 0.0),
            resolution_sort_key(e["resolution_A"]),
            method_rank(e["method"]),
            e["pdb_id"],
            e["chain_id"],
        ),
    )
    best = eligible_sorted[0]
    pdb_best = {
        "pdb_id": best["pdb_id"],
        "chain_id": best["chain_id"],
        "method": best["method"],
        "resolution_A": best["resolution_A"],
        "ecd_coverage_frac": best["ecd_coverage_frac"],
        "ecd_covers": True,
        "tax_id": best["tax_id"],
        "attribution": best["attribution"],
    }
    return {
        "pdb_status": STATUS_PRESENT,
        "pdb_ids": pdb_ids,
        "pdb_best": pdb_best,
        "entries": entries,
    }
