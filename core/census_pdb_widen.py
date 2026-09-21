"""D-172 widen hunt helpers for ABSENT cohort (metadata-only).

Candidates must come from RCSB/PDBe API-shaped records with real pdb_id + match_kind.
Never invent ids. related_ortholog is recorded but never silent pdb_best.
"""
from __future__ import annotations

from typing import Any

from core.census_pdb import (
    MATCH_COMPLEX_CHAIN,
    MATCH_CONSTRUCT_ALT,
    MATCH_DOMAIN_FRAGMENT,
    MATCH_RELATED_ORTHOLOG,
    MATCH_UNIPROT_DIRECT,
    require_pdb_id,
)


def merge_candidates(*groups: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Dedupe by (pdb_id, chain_id, match_kind); refuse blanks."""
    seen: set[tuple[str, str, str]] = set()
    out: list[dict[str, Any]] = []
    for group in groups:
        for raw in group or []:
            try:
                pdb_id = require_pdb_id(raw)
            except ValueError:
                continue
            chain = str(raw.get("chain_id") or "")
            kind = str(raw.get("match_kind") or MATCH_UNIPROT_DIRECT)
            key = (pdb_id, chain, kind)
            if key in seen:
                continue
            seen.add(key)
            out.append(raw)
    return out


def tag_direct(raw_list: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out = []
    for r in raw_list or []:
        d = dict(r)
        d.setdefault("match_kind", MATCH_UNIPROT_DIRECT)
        out.append(d)
    return out
