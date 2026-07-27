"""D-053 — per-target cancer associations, DERIVED from the cohort's own source paper.

Pure and fixture-testable (no network, no DB, no GPU), mirroring `core/adc_reference.py`. The rows
are the Kathad S3 quasi-H-score grid above the paper's stated 150 cutoff — 337 target-tumour pairs
across all 82 targets. This module loads, validates, groups, and joins them; it derives no new
science and asserts no causation.

Discipline carried from D-040 / D-050:
- an uncited row is not data (rejected);
- a qh_score is a statistic (validated numeric + in range), never trusted blindly;
- the grouping is sorted by score DESCENDING here, in the data contract — not in JSX — because that
  ordering is what makes "render all of them" (D-053 decision 4, no truncation) legible;
- a symbol that does not join to the cohort is FLAGGED in `unmatched_symbols`, never dropped
  (a silent join loss would hide a target and nobody would see it — the same class as the
  data/-not-in-image bug).

Counts (`pair_count` / `targets_covered` / `cohort_size`) are computed from what was actually
loaded — never constants (D-053 decision 5: our statistics derive; the paper's 290/16 are the only
literals, and they live in the UI's derivation-gap note, not here).
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

_ROOT = Path(__file__).resolve().parent.parent
ASSOCIATIONS = _ROOT / "data" / "cancer_associations.csv"
COHORT_MAPPING = _ROOT / "data" / "cohort_82_mapping.csv"

# Metadata about the derivation — facts about a published document (D-053 decision 5: a citation
# may be a literal), so they are constants; the counts below them are not.
SOURCE = ("Kathad et al. 2024, PLOS ONE 10.1371/journal.pone.0308604, "
          "S3 File (sheet Target_expression_in_tumor), CC-BY 4.0")
METHOD = "quasi H-score (0-300 = %low×1 + %med×2 + %high×3, from HPA IHC), the paper's own measure"
CUTOFF = 150  # the paper's stated cutoff; the CSV is already the above-cutoff pairs
QH_MIN, QH_MAX = 0.0, 300.0


class AssociationError(Exception):
    """A structural fault in the associations file: an uncited row, or a bad qh_score."""


def _read_csv(path: Any) -> list[dict[str, str]]:
    """Read a CSV, skipping whole-line ``#`` comments (the provenance header block)."""
    with open(path, encoding="utf-8") as fh:
        lines = [ln for ln in fh if not ln.lstrip().startswith("#")]
    return list(csv.DictReader(lines))


def _cohort_symbols(path: Any) -> set[str]:
    return {r["symbol"] for r in _read_csv(path)}


def load_associations(path: Any = ASSOCIATIONS,
                      cohort_path: Any = COHORT_MAPPING) -> dict[str, Any]:
    """Load, validate, group, and cohort-join the associations. See the module docstring."""
    rows = _read_csv(path)
    cohort_syms = _cohort_symbols(cohort_path)
    assoc: dict[str, list[dict[str, Any]]] = {}
    unmatched: set[str] = set()
    pair_count = 0

    for r in rows:
        sym = (r.get("symbol") or "").strip()
        if not (r.get("source_citation") or "").strip():
            raise AssociationError(
                f"association {sym!r}/{(r.get('cancer') or '').strip()!r} has no "
                f"source_citation (D-040: an uncited row is not data)")
        raw = (r.get("qh_score") or "").strip()
        try:
            qh = float(raw)
        except ValueError:
            raise AssociationError(f"non-numeric qh_score {raw!r} for {sym!r} (D-053)")
        if not (QH_MIN <= qh <= QH_MAX):
            raise AssociationError(
                f"qh_score {qh} out of range [{QH_MIN:.0f}, {QH_MAX:.0f}] for {sym!r} (D-053)")
        if sym not in cohort_syms:
            unmatched.add(sym)
        assoc.setdefault(sym, []).append(
            {"cancer": (r.get("cancer") or "").strip(), "qh_score": qh})
        pair_count += 1

    for sym in assoc:
        assoc[sym].sort(key=lambda a: a["qh_score"], reverse=True)

    return {
        "source": SOURCE,
        "method": METHOD,
        "cutoff": CUTOFF,
        "pair_count": pair_count,
        "targets_covered": len(assoc),
        "cohort_size": len(cohort_syms),
        "unmatched_symbols": sorted(unmatched),
        "associations": assoc,
    }
