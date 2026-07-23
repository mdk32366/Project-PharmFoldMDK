"""D-029 + D-040 — the ADC reference: evidence scores, Group B labels, Group C, one curated file.

Pure and fixture-testable (no network, no DB, no GPU). The live openFDA query lives ONLY in the
scheduled advisory workflow (D-029) — never here and never in the test suite, so a green gate can
never depend on an external service (the D-018/D-029 argument).

Three things this module holds, each a load-bearing part of the scorer arc's data:

- **The evidence score (D-040 decision 2).** The paper publishes exact 1-5 scores for only **17 of
  82** in its text (the rest appear only as Fig 4A/4B). The 65 unpublished carry `null` **with a
  reason**, never a figure-read value and never an imputed one — the same discipline D-027 rules
  for uncomputable features. The score symbols are joined to accessions against the cohort, and a
  symbol that does not resolve is returned as a result, never silently dropped (PREWORK §2).

- **Group B (D-040 decision 1).** The labelled positive set the scorer fits against — DERIVED here
  from a per-row-cited curated file, not inherited. Applied by a pure function: in-cohort ADC rows
  at preclinical/clinical/approved stage. `in_cohort_82` is **computed by join, never typed**, so a
  curation slip cannot move a target between Group B (the labels) and Group C (the sharpest
  evaluation instrument).

- **Group C + reconciliation (D-029).** Approved ADC targets OUTSIDE the 82, and the openFDA diff
  that dates the mapping's staleness. The diff detects; it never extends — assigning an antigen to a
  new approval is a human read every time.
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any, Optional

_ROOT = Path(__file__).resolve().parent.parent
COHORT_MAPPING = _ROOT / "data" / "cohort_82_mapping.csv"
EVIDENCE_SCORES = _ROOT / "data" / "evidence_scores.csv"
ADC_MAPPING = _ROOT / "data" / "adc_reference_mapping.csv"

SCORE_NOT_PUBLISHED = "score_not_published_in_text"       # D-040: the reason, not a value
GROUP_B_STAGES = ("preclinical", "clinical", "approved")  # D-040: Group B admits preclinical+
# in_cohort_82 is COMPUTED (a join); a curated file that TYPES it is a slip that could silently
# move a target between the labelled set and the evaluation instrument (D-040).
COMPUTED_ONLY_COLUMNS = ("in_cohort_82",)


class CurationError(Exception):
    """A structural fault in a curated file: an uncited row, or a typed computed column."""


def _read_csv(path: Any) -> list[dict[str, str]]:
    """Read a CSV, skipping whole-line ``#`` comments (the provenance/status header block)."""
    with open(path, encoding="utf-8") as fh:
        lines = [ln for ln in fh if not ln.lstrip().startswith("#")]
    return list(csv.DictReader(lines))


def cohort_symbol_to_accession(path: Any = COHORT_MAPPING) -> dict[str, str]:
    """The ``symbol -> accession`` join key for the 82 (PREWORK §2: the paper works in symbols)."""
    return {r["symbol"]: r["accession"] for r in _read_csv(path)}


def cohort_accessions(path: Any = COHORT_MAPPING) -> set[str]:
    return {r["accession"] for r in _read_csv(path)}


# ── evidence score: 17 published, 65 null-with-reason, no imputation (D-040 dec. 2) ──

def load_evidence_scores(scores_path: Any = EVIDENCE_SCORES,
                         cohort_path: Any = COHORT_MAPPING) -> dict[str, Any]:
    """For EVERY cohort target: the published 1-5 score, or ``None`` with a reason.

    The published symbols are joined ``symbol -> accession`` against the cohort; a published symbol
    that does not resolve is returned in ``unresolved`` (a silent join loss would drop a comparator
    target and nobody would see it — the same class as the ``data/``-not-in-image bug). The 65 not in
    the published set get ``null_reason = score_not_published_in_text`` — computed, never imputed."""
    cohort = _read_csv(cohort_path)
    scored = {r["symbol"]: r for r in _read_csv(scores_path)}
    cohort_syms = {r["symbol"] for r in cohort}
    unresolved = sorted(s for s in scored if s not in cohort_syms)
    out: list[dict[str, Any]] = []
    for r in cohort:
        s = scored.get(r["symbol"])
        out.append({
            "accession": r["accession"],
            "symbol": r["symbol"],
            "evidence_score": int(s["evidence_score"]) if s else None,
            "null_reason": None if s else SCORE_NOT_PUBLISHED,
            "source_citation": s["source_citation"] if s else None,
        })
    return {"scores": out, "unresolved": unresolved}


# ── the curated mapping: Group B / Group C, in_cohort_82 computed (D-029 + D-040) ──

def load_mapping(path: Any = ADC_MAPPING) -> list[dict[str, str]]:
    """Load the curated drug->antigen->accession file. Raises ``CurationError`` if any row lacks a
    ``source_citation`` (D-029: an uncited assignment cannot enter) or if the file carries an
    ``in_cohort_82`` column (D-040: computed, never typed)."""
    rows = _read_csv(path)
    if not rows:
        return []
    for col in COMPUTED_ONLY_COLUMNS:
        if col in rows[0]:
            raise CurationError(f"{col!r} is computed by join, never typed (D-040)")
    for r in rows:
        if not (r.get("source_citation") or "").strip():
            raise CurationError(f"mapping row {r.get('drug')!r} has no source_citation (D-029)")
    return rows


def with_in_cohort(rows: list[dict], cohort_accs: set[str]) -> list[dict[str, Any]]:
    """Attach the COMPUTED ``in_cohort_82`` (a join — D-040), never a typed value."""
    return [{**r, "in_cohort_82": r["uniprot_accession"] in cohort_accs} for r in rows]


def group_b(rows: list[dict], cohort_accs: set[str]) -> list[dict[str, Any]]:
    """Group B (D-040): in-cohort ADC rows at preclinical/clinical/approved stage. The file holds
    only ADC drug rows by curation, so 'is an ADC, not a bare antibody, not family precedent' is the
    curator's cited judgement; this function applies the cohort + development-stage half."""
    return [r for r in with_in_cohort(rows, cohort_accs)
            if r["in_cohort_82"] and r["development_stage"] in GROUP_B_STAGES]


def group_c(rows: list[dict], cohort_accs: set[str]) -> list[dict[str, Any]]:
    """Group C (D-029): approved ADC targets OUTSIDE the 82 — the class-1 out-of-cohort probe."""
    return [r for r in with_in_cohort(rows, cohort_accs)
            if not r["in_cohort_82"] and r["development_stage"] == "approved"]


def group_b_accessions(rows: list[dict], cohort_accs: set[str]) -> set[str]:
    return {r["uniprot_accession"] for r in group_b(rows, cohort_accs)}


def group_b_folded_count(rows: list[dict], cohort_accs: set[str],
                         folded_accessions: Any) -> int:
    """The number D-040 wants computed the moment labels land: how many Group B positives are in
    the folded set. The scorer can only be fit on targets both LABELLED and FOLDED; if this is
    materially below 22, the fit is thinner than D-027's pre-registration assumed — a finding."""
    return len(group_b_accessions(rows, cohort_accs) & set(folded_accessions))


# ── openFDA reconciliation (D-029) — pure given a fixture response ──

def reconcile_approvals(rows: list[dict],
                        openfda_application_numbers: Any) -> dict[str, list[str]]:
    """Diff the mapping's application numbers against openFDA's. Detection is automatable;
    antigen assignment is not — the diff reports staleness, it never extends the mapping. The
    openFDA list is injected (a fixture in tests; the live query is the scheduled advisory
    workflow, D-029). Returns new approvals (need a human read) and stale application numbers."""
    mapped = {(r.get("application_number") or "").strip()
              for r in rows if (r.get("application_number") or "").strip()}
    live = set(openfda_application_numbers)
    return {
        "new_approvals": sorted(live - mapped),
        "stale_application_numbers": sorted(mapped - live),
    }
