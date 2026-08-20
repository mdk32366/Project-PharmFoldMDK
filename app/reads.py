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

import json
from pathlib import Path
from typing import Any, Optional

from sqlalchemy import func, desc, select
from sqlalchemy.orm import Session

from core.manifest import ManifestRow, build_manifest, coverage
from core.queue import FAILED
from db.models import JobRecord, ProteinAnalysis, RankingResult, RankingRun, TargetScore

# The paper's published Group B count (Kathad et al. 2024, D-040 / F-003). A SOURCE CONSTANT served
# by the API so the surface derives it rather than typing it (D-062 Constraint-A). It never changes;
# the DERIVED count (n_fit_positives = 12) is what the roster produced and is stored per run.
PAPER_PUBLISHED_GROUP_B = 22


def _load_tier_environments() -> dict[str, Any]:
    """D-071 state 2 — the per-TIER environment MEASURED ON THE MACHINE AFTER the folds, keyed by
    tier (never per fold). Only tiers whose machine still exists have an entry; the ephemeral rental
    pods have none, so those folds stay state 3 (D-071 decision 3). A measurement, not the manifest
    (F-007) and not an inference (D-070 decision 2, as amended by D-071). Loaded once at import; a
    missing file yields ``{}`` so the field is simply ``None`` everywhere. Keys ignored: any starting
    ``_`` (the file's own documentation note)."""
    path = Path(__file__).resolve().parent.parent / "data" / "tier_environments.json"
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {}
    return {k: v for k, v in raw.items() if not k.startswith("_")}


_TIER_ENVIRONMENTS = _load_tier_environments()

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
    # D-071 state 2: the tier's measured-later environment, or None. A field on the existing detail
    # route — no new route, no system-model.json change. `rental` has no entry by design (decision 3).
    out["tier_environment"] = _TIER_ENVIRONMENTS.get(out.get("tier"))
    return out


#: The reported cohort. ⚠ Census rows carry a non-zero tranche and must never reach this list.
COHORT_TRANCHE = 0


def list_analyses(engine: Any) -> list[dict[str, Any]]:
    """The **cohort** as light rows, ordered by ``id`` ascending (D-034 / Orders §1; D-079).

    ⚠ FILTERED TO TRANCHE ZERO, and the filter is the point. `protein_analyses` **is** the cohort
    today and `TargetList.jsx` renders whatever this returns, so without the `.where(...)` an
    ingest makes the target list **silently** become the census — no error, no red, just 2,807
    rows where there were 82.

    ⚠ `== COHORT_TRANCHE`, never `!= something` and never `IS NULL OR == 0`. An untagged row is
    *unclassified*, which is a CATEGORY and not a cohort member; treating a null as zero would
    promote it into the reported set by default.
    """
    with Session(engine) as s:
        rows = s.scalars(
            select(ProteinAnalysis)
            .where(ProteinAnalysis.cohort_tranche == COHORT_TRANCHE)
            .order_by(ProteinAnalysis.id)
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
            # ⚠⚠ TRANCHE-FILTERED, AND IT IS NOT OPTIONAL. 75 of the 82 cohort accessions also
            # appear in the census manifest — HER2, EGFR, MSLN, IGF2R, MUC16 among them. Without
            # this, the first census fold of P04626 puts a CENSUS analysis_id under HER2's
            # accession in this dict, and the cohort's coverage row then points at a fold measured
            # under a DIFFERENT SPAN DEFINITION. ⚠ There is no ORDER BY, so which row wins is
            # whatever the database returns last — nondeterministic, and silently so.
            .where(ProteinAnalysis.cohort_tranche == COHORT_TRANCHE)
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
            # ⚠ Same leak, mirrored: an unfiltered failed census fold would mark a COHORT target
            # as failed on the tranche-zero surface. D-024 requires attempted-and-failed be shown
            # as distinct from never-attempted, and a census failure is neither.
            .where(ProteinAnalysis.cohort_tranche == COHORT_TRANCHE)
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


# ── F-049's third instance: `ranked` names two populations on two routes ─────
#
# `/api/coverage` says `ranked = 67`; `/api/ranking` says `n_ranking_set = 56`. Both are right.
# The defect is that neither payload said WHICH population it counted, so a consumer reading the
# JSON had one word, two numbers, and no way to close the gap. D-016: every claim names how it is
# known. ⚠ The UI was never the defect — D-066 dec 2 already renders the 67 → 56 reconciliation
# beside the scorer table; a JSON consumer never sees that page.
#
# ⚠⚠ Each description points AT the number it is NOT, by name and by route. A description that
# only says what a number IS still lets a reader assume the other one means the same thing.
COVERAGE_POPULATION_KEY = {
    "denominator": {"kind": "MANIFEST_COUNT", "text": (
        "The 82 cohort targets, computed by `build_manifest()` from the committed CSVs (D-023). "
        "Never read from `protein_analyses` — that would make the denominator a function of how "
        "much work has happened (D-024)."
    )},
    "ranked": {"kind": "MANIFEST_DISPOSITION", "text": (
        "MANIFEST DISPOSITION (D-024): not excluded and not held out. Computed from the committed "
        "CSVs before any fold exists, so it counts targets that are ELIGIBLE to be ranked. "
        "⚠ It is NOT membership of the ranking set and applies no pLDDT floor: see "
        "`n_ranking_set` on /api/ranking, which is smaller."
    )},
    "held_out": {"kind": "MANIFEST_DISPOSITION", "text": (
        "MANIFEST DISPOSITION: boundary-method incomparable (D-021 §1a). Held out of the ranking "
        "regardless of fold state. Disjoint from `ranked` and from `excluded`."
    )},
    "excluded": {"kind": "MANIFEST_DISPOSITION", "text": (
        "MANIFEST DISPOSITION: named and oversize (D-022). Excluded wins over held_out wins over "
        "ranked, so the three cells partition the denominator exactly."
    )},
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
        "population_key": COVERAGE_POPULATION_KEY,
        "failed": sum(1 for r in projected if r["fold_status"] == "failed"),
        "rows": projected,
    }


# ── ranking (D-062): the persisted scorer result (F-004), latest VALID run only ─
#
# The other half of the `ranked` collision — see COVERAGE_POPULATION_KEY above. ⚠ These two
# descriptions must stay DIFFERENT TEXT: giving both populations one description would re-create
# the defect inside its own fix, and a test pins that.
RANKING_POPULATION_KEY = {
    "n_ranking_set": {"kind": "FIT_TIME_MEASUREMENT", "text": (
        "Rows the scorer actually consumed at FIT TIME: ranked AND folded AND "
        "mean_plddt >= plddt_floor (D-060 dec 5). A DATABASE property, measured after folding. "
        "⚠ It is NOT `coverage.ranked` on /api/coverage, which is the manifest disposition, "
        "applies no floor, and is larger. The difference is rows below the floor, plus ranked "
        "rows not folded — each named, never dropped (`excluded` carries the reasons)."
    )},
    "n_fit_positives": {"kind": "FIT_TIME_MEASUREMENT", "text": (
        "Group B positives INSIDE `n_ranking_set`, joined by ACCESSION (D-064 dec 1). "
        "⚠ Not the Group B positives across the 82, which is a different and larger figure."
    )},
    "distribution": {"kind": "FIT_TIME_MEASUREMENT", "text": (
        "The labelled positives with their percentile in this run — `spearman_n` rows, NOT the "
        "`n_ranking_set` rows the model scored. ⚠ A consumer treating this as the scored set "
        "reads the wrong population."
    )},
}

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
    """The newest VALID, PRE-REGISTERED `ranking_results` row: `status_detail` does NOT start with
    'invalid' (D-064 dec 3 — the zero-positive artifact id=1 is marked invalid and never served) AND
    its run is `run_kind='preregistered'` (D-065 dec 4 — a sensitivity ablation is never served where
    the pre-registered result is expected)."""
    return session.scalars(
        select(RankingResult)
        .join(RankingRun, RankingRun.id == RankingResult.ranking_run_id)
        .where(
            (RankingResult.status_detail.is_(None))
            | (~RankingResult.status_detail.startswith("invalid"))
        )
        .where(RankingRun.run_kind == "preregistered")
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
            "population_key": RANKING_POPULATION_KEY,
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


# ── The census surface (D-087) ───────────────────────────────────────────────
#
# ⚠⚠ SEPARATE FROM THE COHORT, AND THE SEPARATION IS THE POINT. `list_analyses` is
# `cohort_tranche == COHORT_TRANCHE` and stays that way; this is `!= COHORT_TRANCHE`. The two
# populations are measured under different span definitions (D-081) and one is scored while the
# other is barred from scoring (D-079). ⚠ A surface that mixed them would put a V2 census span
# beside a V1 cohort span in one column with nothing saying which was which.

_CENSUS_CTX: dict[str, Any] = {}


def _census_context() -> dict[str, Any]:
    """Accession → name + segment topology, from the derived artifacts. Loaded once.

    ⚠ Read from files rather than the database because neither is in it: census rows carry span
    geometry, not identity (`census_labels.csv`) and not segment structure (`span_segments.csv`,
    F-037). ⚠ **A missing artifact yields an empty context, never a silent zero** — the caller
    renders 'unknown', which is not 'none'.
    """
    if _CENSUS_CTX:
        return _CENSUS_CTX
    import csv as _csv
    base = Path(__file__).resolve().parent.parent / "data" / "census"
    labels: dict[str, dict[str, str]] = {}
    segs: dict[str, dict[str, str]] = {}
    lp, sp = base / "census_labels.csv", base / "span_segments.csv"
    # ⚠⚠ FRESHNESS IS CHECKED BEFORE THE DATA IS USED. Both files are derived from the manifest;
    # a manifest revision leaves them describing something that is no longer there, and they would
    # not fail, warn or change. **A wrong topology is worse than a missing one, because a missing
    # one is visible.** So a stale derivation is DROPPED and its verdict is carried on every row.
    from core.derived_freshness import FRESH, check
    manifest = base / "census_manifest.v7.csv"
    seg_verdict, seg_note = check(base / "span_segments.provenance.json", manifest)
    lab_verdict, lab_note = check(base / "census_labels.provenance.json", manifest)

    if lp.is_file() and lab_verdict == FRESH:
        labels = {r["census_accession"]: r for r in _csv.DictReader(lp.open(encoding="utf-8"))}
    if sp.is_file() and seg_verdict == FRESH:
        segs = {r["census_accession"]: r for r in _csv.DictReader(sp.open(encoding="utf-8"))}

    # ⚠⚠ ALIASES, so a name a person would actually type reaches the protein it names. The census
    # is keyed on HGNC symbols; the ADC field is not. `CD30` is here as `TNFRSF8` and reads as
    # absent to anyone who searches the antigen name — the owner hit exactly that.
    # ⚠ Derived from the pinned UniProt cache, never typed: see `scripts/build_protein_aliases.py`.
    # ⚠ A missing index yields an empty map and the search degrades to what it does today — it
    # does NOT fail, and it does not silently claim a protein has no other names.
    from core.protein_aliases import aliases_by_accession
    alias_map = aliases_by_accession()

    _CENSUS_CTX.update({"labels": labels, "segments": segs, "aliases": alias_map,
                        "segments_verdict": seg_verdict, "segments_note": seg_note,
                        "labels_verdict": lab_verdict, "labels_note": lab_note})
    return _CENSUS_CTX


def _hpa_attribution(gene: str | None, view: str) -> dict[str, Any] | None:
    """The four elements for one HPA-derived value.

    ⚠ A missing ENSG map degrades to an absent link WITH ITS REASON — never a broken anchor, and
    never a silently omitted citation, because the licence makes citation a precondition of display.
    """
    try:
        from core.hpa_attribution import attribution_block
        return attribution_block(gene, view)
    except Exception:                      # noqa: BLE001
        return None


def _surface_payload(accession: str, gene: str | None) -> dict[str, Any] | None:
    """⚠ A missing artifact degrades to None and the surface says nothing — never a false negative."""
    try:
        from core.surface_confirmation import payload_for
        return payload_for(accession, gene)
    except Exception:                      # noqa: BLE001
        return None


def census_projection(row: ProteinAnalysis) -> dict[str, Any]:
    """One census row for the list. ⚠ Carries NO score and no rank — D-079 decision 1."""
    ctx = _census_context()
    meta = row.meta or {}
    acc = row.input_value
    lab = ctx["labels"].get(acc, {})
    seg = ctx["segments"].get(acc, {})
    return {
        "id": row.id,
        "accession": acc,
        "gene": lab.get("gene") or None,
        "label": lab.get("label") or None,
        # ⚠ Other names this protein goes by — searched, never displayed as identity. The gene
        # symbol stays the row's name; an alias is a way IN, not a second title.
        "aliases": ctx["aliases"].get(acc) or None,
        # ⚠⚠ THE SECOND INSTRUMENT (D-103). Every census row asserts an extracellular span from
        # ONE source — UniProt topology. This is an INDEPENDENT reading of the same claim, from
        # antibody imaging. A category, never a score: it says what the two instruments did.
        "surface_check": _surface_payload(acc, lab.get("gene")),
        "tranche": row.cohort_tranche,
        "span_aa": meta.get("span_aa"),
        "span_start": meta.get("ecd_start"),
        "span_end": meta.get("ecd_end"),
        "full_length": meta.get("full_length"),
        "census_class": meta.get("census_class"),
        "mean_plddt": row.mean_plddt,
        # ⚠ F-037 context. `topology` is a WORD; a bare count invites the reader to interpret it.
        # ⚠ A stale derivation reports its VERDICT, not "unknown" and never the old value. The
        # reader must be able to tell "nobody derived this" from "it was derived against a
        # different manifest" — different causes, different fixes.
        "topology": seg.get("topology") or (
            "unknown" if ctx["segments_verdict"] == "fresh" else ctx["segments_verdict"]),
        "derivation_status": ctx["segments_verdict"],
        "derivation_note": ctx["segments_note"],
        "segment_count": int(seg["segment_count"]) if seg.get("segment_count") else None,
        "extracellular_total_aa": int(seg["extracellular_total_aa"]) if seg.get("extracellular_total_aa") else None,
        "discarded_aa": int(seg["discarded_aa"]) if seg.get("discarded_aa") else None,
        "segments": seg.get("segments") or None,
        "span_definition": meta.get("span_definition"),
        # ⚠⚠ NOT a score and never sortable as one. Stated on every row so no consumer has to
        # remember the bar.
        "scored": False,
        "not_scored_reason": meta.get("not_scored_reason"),
    }


def list_census(engine: Any) -> list[dict[str, Any]]:
    """Every FOLDED census row. ⚠ `!= COHORT_TRANCHE` — the cohort is served by `list_analyses`."""
    with Session(engine) as session:
        rows = session.scalars(
            select(ProteinAnalysis)
            # ⚠⚠ `> COHORT_TRANCHE`, NOT `!= COHORT_TRANCHE`. A bare negation reads as "everything
            # that is not the cohort" and would make a NULL-tranche row invisible on BOTH surfaces
            # — the cohort filter is `==` and excludes it, and a negation excludes it too under SQL
            # three-valued logic. An untagged row must not vanish; `census_untranched_count` exists
            # so it is COUNTED rather than quietly dropped.
            .where(ProteinAnalysis.cohort_tranche > COHORT_TRANCHE)
            .where(ProteinAnalysis.pdb_path.isnot(None))
            .order_by(ProteinAnalysis.input_value)          # ⚠ accession, a neutral default
        ).all()
    out = [census_projection(r) for r in rows]

    # ⚠⚠ THE STAINING LENSES (D-102). Attached here rather than in `census_projection` because it
    # needs the database and the projection is a pure shape over one row.
    # ⚠ BOTH lenses ride on every row. Sending one would be the page choosing for the reader, and
    # the whole point of D-102 is that the choice is the reader's and must be named.
    # ⚠ A protein with no staining entry carries `None` and the surface renders a CATEGORY: HPA
    # covers fewer proteins than the census holds, and 960 of 2,687 are absent entirely.
    try:
        from app.census_staining_read import staining_by_gene
        stain = staining_by_gene(engine)
    except Exception:                      # noqa: BLE001
        # ⚠ A missing or unmigrated clinical table must not take the census page down. The
        # surface degrades to what it showed before the lens existed — it does NOT show zeros.
        stain = {}
    for row in out:
        row["staining"] = stain.get(row.get("gene")) if row.get("gene") else None
        row["folded"] = True

    # ⚠⚠ THE NEVER-FOLDED ROWS JOIN THE LIST — owner ruling, 2026-08-20. Searching `HER2` returned
    # "no protein matches"; HER2 is in the manifest and was never folded, and a reader should not
    # have to parse fine print to learn the protein exists. A row with a STATUS beats a paragraph.
    # ⚠ They carry no fold-derived value at all — no pLDDT, no profile, no staining — and each
    # absence is a category, never a zero.
    try:
        from core.census_unfolded import unfolded_rows
        out.extend(unfolded_rows())
    except Exception:                      # noqa: BLE001
        pass                               # ⚠ a missing manifest degrades to the folded list alone
    return out


def census_untranched_count(engine: Any) -> int:
    """Rows with NO tranche at all. ⚠ Visible on NEITHER surface, so it is counted here.

    The cohort filter is `== 0` and the census filter is `> 0`; a NULL falls through both. **That
    is correct behaviour and a silent one**, so the number is exposed rather than left to be
    discovered by a total that does not add up.
    """
    with Session(engine) as session:
        return session.scalar(
            select(func.count()).select_from(ProteinAnalysis)
            .where(ProteinAnalysis.cohort_tranche.is_(None))) or 0


def resolve_census_accession(engine: Any, accession: str) -> tuple[Optional[int], str]:
    """(analysis_id, outcome) for a UniProt accession typed into the census route.

    ⚠⚠ THREE OUTCOMES, NEVER TWO. A person who pastes an accession into `/census/…` deserves to know
    WHICH of these happened, because they mean completely different things:

      `census`  — resolved; the id is returned
      `cohort`  — ⚠ the accession IS one of the 82 ranked targets. It is NOT reachable here and is
                  NOT redirected: `D-081` measures the two populations under different span
                  definitions, and making one reachable through the other's route would silently
                  hand back a row measured by a different rule. The caller is TOLD where it lives.
      `unknown` — no analysis carries that accession at all

    ⚠ Before this existed the route took `analysis_id: int`, so any accession returned **HTTP 422** —
    a validation error, which tells a reader their input was malformed rather than that they used
    the wrong key for the right protein.
    """
    acc = (accession or "").strip().upper()
    if not acc:
        return None, "unknown"
    with Session(engine) as session:
        rows = session.scalars(
            select(ProteinAnalysis).where(ProteinAnalysis.input_value == acc)
        ).all()
    if not rows:
        return None, "unknown"
    # ⚠ census first — an accession can exist in both populations, and this route serves one of them
    for r in rows:
        if r.cohort_tranche is not None and r.cohort_tranche > COHORT_TRANCHE and r.pdb_path:
            return r.id, "census"
    return None, "cohort" if any(r.cohort_tranche == COHORT_TRANCHE for r in rows) else "unknown"


def get_pae_path(engine: Any, analysis_id: int) -> Optional[str]:
    """The row's stored ``pae_json_path``, or None.

    ⚠⚠ WHY A ROUTE AND NOT FILESYSTEM ACCESS. The 79 cohort matrices live on the production volume
    and an analysis question needed them. Reaching in with `fly ssh` would be production filesystem
    access for a read — the exact shape closed the day before, where a tunnel to production looks
    like localhost and the WINDOW is the hazard. A route goes through the gate, is testable, and
    uses the reader role that already exists.

    ⚠ The path is the STORED one. No client value reaches the filesystem — same traversal defence
    as `get_structure_path`, and the same reason.
    """
    with Session(engine) as session:
        row = session.get(ProteinAnalysis, analysis_id)
        return row.pae_json_path if row else None


def get_census_detail(engine: Any, analysis_id: int) -> Optional[dict[str, Any]]:
    """One census row, with its cancer-association STATUS.

    ⚠⚠ THE ASSOCIATION SOURCE COVERS THE 82 COHORT TARGETS ONLY (`targets_covered: 82`). For a
    census protein there is **no association data**, and that is `not_covered` — **NOT "no cancer
    associations found."** *"We did not look"* and *"we looked and found none"* are different
    facts, and rendering the first as the second would be a claim the data does not support.
    """
    with Session(engine) as session:
        row = session.get(ProteinAnalysis, analysis_id)
        if row is None or row.cohort_tranche == COHORT_TRANCHE:
            return None
        out = census_projection(row)
        out["sequence"] = (row.meta or {}).get("sequence")
        out["fold_provenance"] = (row.meta or {}).get("fold_provenance")
        out["structure_source"] = row.structure_source
    from core.cancer_associations import load_associations
    payload = load_associations()
    gene = out.get("gene")
    hits = (payload.get("associations") or {}).get(gene) if gene else None
    out["cancer_associations"] = {
        # ⚠⚠ HPA ATTRIBUTION ON A SURFACE THAT CITES A PAPER. `D-100` established that Kathad's S3
        # is a VERBATIM EXTRACT of `pathology.tsv` — 1,640/1,640 rows, all four count columns
        # identical. **Citing the paper is not citing HPA.** The obligation attaches to the
        # underlying source whichever route the numbers took, and `D-053` predates the clinical
        # layer — so this surface has rendered HPA data unattributed longer than any other.
        "attribution": _hpa_attribution(gene, "pathology"),
        "status": "covered" if hits is not None else "not_covered",
        "hits": hits or [],
        "source": payload.get("source"),
        # ⚠ The denominator travels with the verdict, so 'not_covered' is self-explaining.
        "coverage_note": (f"the association source covers the {payload.get('targets_covered')} "
                          f"cohort targets only; census proteins are outside it"),
    }
    return out
