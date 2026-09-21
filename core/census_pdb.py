"""Census experimental PDB metadata selection — D-171 / D-172.

Metadata-only. Never recomputes structural_score / STRUCTURAL_ONLY.
Never treats a PDB entry as the ranked fold or the served predicted fold.
Never invents PDB ids — every candidate must carry a real pdb_id from API evidence.

D-171: ECD coverage ≥ 0.50 for pdb_best; distinct ABSENT / ABSENT_NO_ECD / span_absent.
D-172: match_kind provenance; related_ortholog never silent pdb_best; widen ABSENT cohort.
"""
from __future__ import annotations

from typing import Any, Iterable

ECD_COVER_THRESHOLD = 0.50

STATUS_PRESENT = "present"
STATUS_ABSENT = "ABSENT"
STATUS_ABSENT_NO_ECD = "ABSENT_NO_ECD_COVERING_STRUCTURE"
STATUS_SPAN_ABSENT = "span_absent"
STATUS_INVALID = "invalid"

MATCH_UNIPROT_DIRECT = "uniprot_direct"
MATCH_COMPLEX_CHAIN = "complex_chain"
MATCH_CONSTRUCT_ALT = "construct_alt_accession"
MATCH_DOMAIN_FRAGMENT = "domain_fragment"
MATCH_RELATED_ORTHOLOG = "related_ortholog"

SAME_PROTEIN_KINDS = frozenset({
    MATCH_UNIPROT_DIRECT,
    MATCH_COMPLEX_CHAIN,
    MATCH_CONSTRUCT_ALT,
    MATCH_DOMAIN_FRAGMENT,
})

MATCH_KIND_LABELS = {
    MATCH_UNIPROT_DIRECT: "direct UniProt map",
    MATCH_COMPLEX_CHAIN: "complex chain",
    MATCH_CONSTRUCT_ALT: "alternate construct accession",
    MATCH_DOMAIN_FRAGMENT: "domain fragment",
    MATCH_RELATED_ORTHOLOG: "related ortholog (not this UniProt)",
}

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


def require_pdb_id(raw: dict[str, Any]) -> str:
    """Reject inventable candidates — missing/blank pdb_id is a hard refuse."""
    pdb_id = str(raw.get("pdb_id") or "").strip().lower()
    if not pdb_id or pdb_id in {"none", "null", "n/a"}:
        raise ValueError("candidate missing pdb_id from API evidence — refuse inventing ids")
    return pdb_id


def normalize_candidate(raw: dict[str, Any]) -> dict[str, Any]:
    pdb_id = require_pdb_id(raw)
    chain_id = str(raw.get("chain_id") or "")
    method = raw.get("experimental_method") or raw.get("method")
    res = raw.get("resolution") if raw.get("resolution") is not None else raw.get("resolution_A")
    try:
        resolution_A = float(res) if res is not None else None
    except (TypeError, ValueError):
        resolution_A = None
    tax = raw.get("tax_id")
    try:
        tax_id = int(tax) if tax is not None else None
    except (TypeError, ValueError):
        tax_id = None
    match_kind = str(raw.get("match_kind") or MATCH_UNIPROT_DIRECT).strip()
    if match_kind not in MATCH_KIND_LABELS:
        match_kind = MATCH_UNIPROT_DIRECT
    match_uniprot = raw.get("match_uniprot") or raw.get("related_uniprot")
    if match_uniprot is not None:
        match_uniprot = str(match_uniprot)
    intervals = observed_intervals_from_candidate(raw)
    return {
        "pdb_id": pdb_id,
        "chain_id": chain_id,
        "method": method,
        "resolution_A": resolution_A,
        "tax_id": tax_id,
        "match_kind": match_kind,
        "match_uniprot": match_uniprot,
        "observed_intervals": intervals,
        "note": raw.get("note"),
        "raw": raw,
    }


def prefer_human(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    humans = [c for c in candidates if c.get("tax_id") == 9606]
    return humans if humans else list(candidates)


def _attribution(pdb_id: str) -> dict[str, str]:
    return {
        "source": "PDBe/SIFTS",
        "rcsb_url": rcsb_url(pdb_id),
        "pdbe_url": pdbe_url(pdb_id),
    }


def _entry_from_norm(c: dict[str, Any], *, frac: float | None, covers: bool) -> dict[str, Any]:
    return {
        "pdb_id": c["pdb_id"],
        "chain_id": c["chain_id"],
        "method": c["method"],
        "resolution_A": c["resolution_A"],
        "tax_id": c["tax_id"],
        "match_kind": c["match_kind"],
        "match_uniprot": c.get("match_uniprot"),
        "ecd_coverage_frac": frac,
        "ecd_covers": covers,
        "unp_start": c["observed_intervals"][0][0] if c["observed_intervals"] else None,
        "unp_end": c["observed_intervals"][-1][1] if c["observed_intervals"] else None,
        "attribution": _attribution(c["pdb_id"]),
    }


def select_pdb_for_accession(
    *,
    accession: str,
    candidates_raw: list[dict[str, Any]] | None,
    ecd_segments: str | None,
    span_absent: bool = False,
) -> dict[str, Any]:
    """Return paint dict for one accession (D-171 + D-172 match_kind / related)."""
    _ = accession
    if candidates_raw is None:
        return {
            "pdb_status": STATUS_INVALID,
            "pdb_ids": [],
            "pdb_best": None,
            "pdb_related": [],
            "entries": [],
        }
    if not candidates_raw:
        return {
            "pdb_status": STATUS_ABSENT,
            "pdb_ids": [],
            "pdb_best": None,
            "pdb_related": [],
            "entries": [],
        }

    ecd_intervals = parse_segment_intervals(ecd_segments)
    ecd = residue_set(ecd_intervals)
    span_is_absent = span_absent or not ecd

    norms: list[dict[str, Any]] = []
    for raw in candidates_raw:
        try:
            norms.append(normalize_candidate(raw))
        except ValueError:
            # invent-refuse: drop candidate without pdb_id
            continue

    related_norms = [c for c in norms if c["match_kind"] == MATCH_RELATED_ORTHOLOG]
    same_norms = [c for c in norms if c["match_kind"] in SAME_PROTEIN_KINDS]
    same_norms = prefer_human(same_norms)

    pdb_related = []
    for c in related_norms:
        pdb_related.append({
            "pdb_id": c["pdb_id"],
            "chain_id": c["chain_id"] or None,
            "tax_id": c["tax_id"],
            "related_uniprot": c.get("match_uniprot") or "",
            "match_kind": MATCH_RELATED_ORTHOLOG,
            "note": c.get("note") or "Related experimental structure — not this UniProt",
            "attribution": _attribution(c["pdb_id"]),
        })

    entries: list[dict[str, Any]] = []
    for c in same_norms:
        obs = residue_set(c["observed_intervals"])
        frac = None if span_is_absent else ecd_coverage_frac(ecd, obs)
        covers = (frac is not None and frac >= ECD_COVER_THRESHOLD)
        entries.append(_entry_from_norm(c, frac=frac, covers=covers if not span_is_absent else False))

    pdb_ids = sorted({e["pdb_id"] for e in entries} | {r["pdb_id"] for r in pdb_related})

    if not same_norms and pdb_related:
        # related-only: stay ABSENT
        return {
            "pdb_status": STATUS_ABSENT,
            "pdb_ids": pdb_ids,
            "pdb_best": None,
            "pdb_related": pdb_related,
            "entries": entries,
        }

    if not same_norms and not pdb_related:
        return {
            "pdb_status": STATUS_ABSENT,
            "pdb_ids": [],
            "pdb_best": None,
            "pdb_related": [],
            "entries": [],
        }

    if span_is_absent:
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
                "match_kind": best["match_kind"],
                "match_uniprot": best.get("match_uniprot"),
                "attribution": best["attribution"],
            }
        return {
            "pdb_status": STATUS_SPAN_ABSENT,
            "pdb_ids": pdb_ids,
            "pdb_best": pdb_best,
            "pdb_related": pdb_related,
            "entries": entries,
        }

    eligible = [e for e in entries if e["ecd_covers"]]
    if not eligible:
        return {
            "pdb_status": STATUS_ABSENT_NO_ECD,
            "pdb_ids": pdb_ids,
            "pdb_best": None,
            "pdb_related": pdb_related,
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
        "match_kind": best["match_kind"],
        "match_uniprot": best.get("match_uniprot"),
        "attribution": best["attribution"],
    }
    return {
        "pdb_status": STATUS_PRESENT,
        "pdb_ids": pdb_ids,
        "pdb_best": pdb_best,
        "pdb_related": pdb_related,
        "entries": entries,
    }
