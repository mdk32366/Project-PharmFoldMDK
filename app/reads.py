"""D-034 — the read API's database + projection work, kept out of the route handlers
so it is unit-testable without HTTP (mirrors the ``routes.py`` / ``artifacts.py`` split).

The load-bearing decisions live here:

- **Two payload shapes (D-034 decision 1).** ``list_projection`` returns the light row a
  ranking table renders — twelve fields, and **never** ``sequence`` or ``fold_provenance``,
  which run to hundreds of residues and a full provenance block per row. ``detail_projection``
  returns the whole record, those heavy fields included. The split is measured, not stylistic
  (D-034: ~tens of KB of sequence across 42 rows a list never shows).

- **Where the fields live.** There is no ``accession``/``gene``/``folded_at`` column. ``accession``
  is ``input_value``; ``gene``/``label``/``tier``/``tier_reason``/``disposition``/``held_out``/
  ``boundary_method``/``fold_length``/``full_length``/``sequence``/``fold_provenance`` are all in
  ``meta`` (``core.enqueue`` writes them, the fold adds ``fold_provenance``). ``mean_plddt`` is a
  column. ``tier_reason`` is a key on every row but ``None`` on non-rental rows — projected as-is.

- **Ordering by ``id`` (D-034 / Orders §1).** ``created_at`` does **not** order the folds — 41 of
  42 rows share one batch timestamp — so the list is ordered by ``id``.

- **Serve the stored ``pdb_path`` (D-034 decision 2 / §2a).** ``pdb_path`` is looked up by integer
  id and returned verbatim; no path is ever reconstructed from ``{root}/{id}`` or built from a
  client value. On an unauthenticated surface that is also the path-traversal defence. The
  per-residue pLDDT lives beside it (``plddt.json`` in the stored path's directory), so it is
  derived from the stored absolute path, never from client input.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from core.manifest import ManifestRow, build_manifest, coverage
from core.queue import FAILED
from db.models import JobRecord, ProteinAnalysis, RankingResult, RankingRun, TargetScore

# The paper's published Group B count (Kathad et al. 2024, D-040 / F-003). A SOURCE CONSTANT served
# by the API so the surface derives it rather than typing it (D-062 Constraint-A). It never changes;
# the DERIVED count (n_fit_positives = 12) is what the roster produced and is stored per run.
PAPER_PUBLISHED_GROUP_B = 22

# Meta keys carried into the light list, in payload order (D-034 decision 1 / Orders §1).
_LIST_META_KEYS = (
    "label", "gene", "disposition", "held_out", "tier", "tier_reason",
    "boundary_method", "fold_length", "full_length",
)
# Extra meta keys the detail record adds on top of the light fields (still excluding the
# two heavy ones, which are appended explicitly last so the split is obvious).
_DETAIL_EXTRA_META_KEYS = (
    "source", "uniprot_release", "ecd_start", "ecd_end", "primary_match",
)


def list_projection(row: ProteinAnalysis) -> dict[str, Any]:
    """The light list row (D-034 decision 1): twelve fields, no ``sequence``/``fold_provenance``.
    ``accession`` comes from ``input_value``, ``mean_plddt`` from the column, the rest from meta."""
    meta = row.meta or {}
    out: dict[str, Any] = {
        "id": row.id,
        "accession": row.input_value,
        "label": meta.get("label"),
        "gene": meta.get("gene"),
        "mean_plddt": row.mean_plddt,
    }
    for key in _LIST_META_KEYS:
        if key not in out:                       # label/gene already placed above
            out[key] = meta.get(key)
    return out


def detail_projection(row: ProteinAnalysis) -> dict[str, Any]:
    """The full record (D-034 decision 1): the light fields, the remaining meta, and the two
    heavy fields — ``sequence`` and the complete ``fold_provenance`` — which the list omits."""
    meta = row.meta or {}
    out = list_projection(row)
    out["structure_source"] = row.structure_source
    out["notes"] = row.notes
    for key in _DETAIL_EXTRA_META_KEYS:
        out[key] = meta.get(key)
    out["sequence"] = meta.get("sequence")
    out["fold_provenance"] = meta.get("fold_provenance")
    return out


def list_analyses(engine: Any) -> list[dict[str, Any]]:
    """Every analysis as a light row, ordered by ``id`` ascending (D-034 / Orders §1)."""
    with Session(engine) as s:
        rows = s.scalars(
            select(ProteinAnalysis).order_by(ProteinAnalysis.id)
        ).all()
        return [list_projection(r) for r in rows]


def get_analysis(engine: Any, analysis_id: int) -> Optional[dict[str, Any]]:
    """The full record for one id, or ``None`` if it does not exist (route → 404)."""
    with Session(engine) as s:
        row = s.get(ProteinAnalysis, analysis_id)
        return detail_projection(row) if row is not None else None


def get_structure_path(engine: Any, analysis_id: int) -> Optional[str]:
    """The row's **stored** ``pdb_path``, or ``None`` if the id is unknown or the fold has no
    structure yet (both → 404, never a 500). Never reconstructs a path (D-034 §2a)."""
    with Session(engine) as s:
        row = s.get(ProteinAnalysis, analysis_id)
        return row.pdb_path if row is not None else None


def get_plddt_path(engine: Any, analysis_id: int) -> Optional[str]:
    """The per-residue ``plddt.json`` beside the stored structure, derived from the absolute
    ``pdb_path`` (never from client input). ``None`` when there is no structure to sit beside."""
    pdb_path = get_structure_path(engine, analysis_id)
    if not pdb_path:
        return None
    return str(Path(pdb_path).parent / "plddt.json")


# ── coverage (D-038): the manifest is the source of 82, the DB is the fold join ─

def _folded_accessions(engine: Any) -> dict[str, int]:
    """``{accession: analysis_id}`` for every **folded** target — a completed ``protein_analyses``
    row (``pdb_path`` set). The join key is ``input_value`` for ``input_type == 'uniprot'`` — the
    accession lives there, there is no accession column (D-034/D-038). Every current row is a
    uniprot input; a future non-uniprot type would need this widened rather than silently miscount."""
    with Session(engine) as s:
        pairs = s.execute(
            select(ProteinAnalysis.id, ProteinAnalysis.input_value)
            .where(ProteinAnalysis.pdb_path.is_not(None))
            .where(ProteinAnalysis.input_type == "uniprot")
        ).all()
    return {input_value: pid for pid, input_value in pairs}


def _failed_accessions(engine: Any) -> dict[str, str | None]:
    """``{accession: error}`` for every target whose latest job is **terminally** ``failed`` (D-043).

    The mirror of ``_folded_accessions``: a ``failed`` job is *attempted-and-failed*, a state D-024
    requires be shown as distinct from *never-attempted*. Same accession-in-``input_value`` join key
    (uniprot inputs only). **Only the terminal ``FAILED`` status counts** — ``claimed``/``pending``
    are in-flight (D-030's status machine), so a target being re-folded never reads as a failure.
    Ordered by job ``id`` so that where multiple failed jobs share an accession the **latest** wins;
    a ``folded`` row overrides this entirely at the call site (fold success is the truth)."""
    with Session(engine) as s:
        pairs = s.execute(
            select(ProteinAnalysis.input_value, JobRecord.error)
            .join(JobRecord, JobRecord.analysis_id == ProteinAnalysis.id)
            .where(ProteinAnalysis.input_type == "uniprot")
            .where(JobRecord.status == FAILED)
            .order_by(JobRecord.id)
        ).all()
    return {input_value: error for input_value, error in pairs}


def _coverage_row(row: ManifestRow, folded: dict[str, int],
                  failed: dict[str, str | None]) -> dict[str, Any]:
    """One manifest row projected for the coverage drill-down, joined to fold state. ``fold_status``
    is the one field neither source has alone (D-038), now three-valued (D-043):
    ``folded`` (a completed row exists) ▸ ``failed`` (else a terminal failed job exists) ▸
    ``not_folded``. ``fail_reason``/``exclusion_reason`` carry the *reason*, not just a flag (D-022 —
    a boolean is not a reason). Precedence puts ``folded`` first so a target that failed once and
    later folded reads ``folded``."""
    analysis_id = folded.get(row.accession)
    if analysis_id is not None:
        fold_status, fail_reason = "folded", None
    elif row.accession in failed:
        fold_status, fail_reason = "failed", failed[row.accession]
    else:
        fold_status, fail_reason = "not_folded", None
    return {
        "accession": row.accession,
        "gene": row.gene,
        "boundary_method": row.boundary_method,
        "span": row.span,
        "tier": row.tier,
        "tier_reason": row.tier_reason,
        "disposition": row.disposition,
        "excluded": row.excluded,
        "exclusion_reason": row.exclusion_reason,
        "fold_status": fold_status,
        "fail_reason": fail_reason,
        "analysis_id": analysis_id,
    }


def coverage_payload(engine: Any) -> dict[str, Any]:
    """The D-038 coverage supplier: the D-024 ``coverage`` object over the full cohort plus the
    per-target drill-down, ``fold_status`` joined from the DB.

    The **cohort is the manifest, not the database** — ``build_manifest`` computes all 82 from the
    committed CSVs deterministically (D-023). Reading the denominator from ``protein_analyses`` would
    make it a function of how much work has happened, the self-flattering failure D-024 forbids. The
    DB contributes only which of those 82 have folded, and (D-043) which were attempted and failed.

    ``failed`` is a **sibling** of ``coverage``, deliberately outside its partition: the ``coverage``
    object stays pure-manifest and keeps ``ranked + held_out + excluded == denominator`` (D-038's
    invariant). ``failed`` is a DB-join fact — a subset of what used to count as ``not_folded`` — so
    it is reported alongside, never summed in."""
    rows = build_manifest()
    folded = _folded_accessions(engine)
    failed = _failed_accessions(engine)
    projected = [_coverage_row(r, folded, failed) for r in rows]
    return {
        "coverage": coverage(rows),
        "failed": sum(1 for r in projected if r["fold_status"] == "failed"),
        "rows": projected,
    }


# ── ranking (D-062): the persisted scorer result (F-004), latest VALID run only ─

def _score_projection(score: TargetScore, row: ProteinAnalysis) -> dict[str, Any]:
    """One ranked target row: rank · symbol · structural score · the six β_k·x_k attributions
    (stored, D-061; the surface may defer rendering them — a display gap, not a data gap)."""
    meta = row.meta or {}
    return {
        "rank": score.rank,
        "accession": row.input_value,
        "gene": meta.get("gene"),
        "score": score.score,
        "attributions": score.attributions,
    }


def _result_status(loo_status: Optional[str], fulldata_status: Optional[str]) -> str:
    """The surface's four-valued run status (D-062 Amendment 1). `raised` = the LOO produced no
    distribution; `partial` = a distribution exists but a pre-registered statistic is blocked (LOO
    partial, or the full-data fit raised → Spearman/ranking blocked, D-064 dec 5); `complete` = all
    produced."""
    if loo_status == "none":
        return "raised"
    if loo_status == "partial" or fulldata_status == "raised":
        return "partial"
    return "complete"


def _latest_valid_result(session: Session) -> Optional[RankingResult]:
    """The newest `ranking_results` row whose `status_detail` does NOT start with 'invalid' (D-064
    dec 3: the zero-positive artifact id=1 is marked invalid and must never be served)."""
    return session.scalars(
        select(RankingResult)
        .where(
            (RankingResult.status_detail.is_(None))
            | (~RankingResult.status_detail.startswith("invalid"))
        )
        .order_by(desc(RankingResult.computed_at), desc(RankingResult.id))
    ).first()


def ranking_payload(engine: Any) -> dict[str, Any]:
    """The D-062 supplier: the latest VALID ranking run's pre-registered result + per-target scores.
    Always 200 with a `result_status`; when no valid run exists it is `not_run` with empty rows, so
    the surface renders the not-run panel rather than a fetch error. Reads persisted rows only —
    nothing is recomputed (F-004: the result is recorded, never re-run)."""
    with Session(engine) as s:
        result = _latest_valid_result(s)
        if result is None:
            return {"result_status": "not_run", "run": None, "result": None, "rows": []}

        run = s.get(RankingRun, result.ranking_run_id)
        pairs = s.execute(
            select(TargetScore, ProteinAnalysis)
            .join(ProteinAnalysis, ProteinAnalysis.id == TargetScore.analysis_id)
            .where(TargetScore.ranking_run_id == result.ranking_run_id)
            .order_by(TargetScore.rank)
        ).all()

        # Pair the LOO distribution to its held-out targets, over the CONVERGED folds only (D-063).
        lpf = result.lambda_per_fold or []
        converged_syms = [f["symbol"] for f in lpf if f.get("converged")]
        distribution = [
            {"symbol": sym, "percentile": pct}
            for sym, pct in zip(converged_syms, result.structural_percentiles or [])  # noqa: B905
        ]
        nonconvergent = [f["symbol"] for f in lpf if not f.get("converged")]

        return {
            "result_status": _result_status(result.loo_status, result.fulldata_status),
            "run": {
                "id": run.id,
                "target_list_version": run.target_list_version,
                "scorer_version": run.scorer_version,
            },
            "result": {
                "loo_status": result.loo_status,
                "fulldata_status": result.fulldata_status,
                "status_detail": result.status_detail,
                "spearman": result.spearman,
                "spearman_n": result.spearman_n,
                "n_ranking_set": result.n_ranking_set,
                "n_fit_positives": result.n_fit_positives,
                "headto_reference_n": result.headto_reference_n,
                "plddt_floor": result.plddt_floor,
                "lambda_at_grid_edge": result.lambda_at_grid_edge,
                "distribution": distribution,                 # [{symbol, percentile}], converged folds
                "nonconvergent": nonconvergent,               # named, never dropped (D-063)
                "headto_structural": result.headto_structural_percentiles or [],
                "headto_evidence": result.headto_evidence_percentiles or [],
                "excluded": result.excluded or [],            # [[symbol, reason], ...] (D-060 §3.5)
                "paper_published_count": PAPER_PUBLISHED_GROUP_B,   # source constant, served not typed
            },
            "rows": [_score_projection(sc, row) for sc, row in pairs],
        }
