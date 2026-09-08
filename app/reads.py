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

from app.confidence_kabsch_path_read import confidence_kabsch_sibling_path
from app.linker_seam_path_read import five_path_payload, seam_note_for_five
from app.phase5_named_refuse import phase5_fate
from app.served_path_policy import (
    SERVED_CONFIDENCE_KABSCH,
    resolve_served_path,
)

from sqlalchemy import func, desc, select
from sqlalchemy.orm import Session

from core.hold48 import (
    HOLD48_KIND_TILE,
    is_mucin,
    is_parent_kind,
    is_stitched_artifact_path,
)
from core.manifest import ManifestRow, build_manifest, coverage
from core.queue import FAILED
from db.models import JobRecord, ProteinAnalysis, RankingResult, RankingRun, TargetScore

# ⚠ D-118 / D-117 owner closeout. Spare tile *jobs* must never surface as a second protein.
# Production numbering is not guaranteed to make job id == analysis id, so both are checked
# wherever an id is in hand. Prefer the lower ids already chosen in ops.
HOLD48_SPARE_TILE_IDS = frozenset({3693, 3695, 3696})
HOLD48_PREFERRED_TILE_IDS = frozenset({3673, 3674, 3675})

# 27 unique Wave1+Wave2 stitched parents (D-117 / D-120 inventory). Owner closeout
# 2026-09-05 PT — not re-queried on Fly in the D-120 PR.
#
# ⚠ D-132: THIS IS A WAVE SLICE, NOT THE VOLUME. It is correct about Wave1 PASS 10 +
# Wave2 PASS 17 and it is kept verbatim for that. It is NOT the count of parents that
# are assembled on the Fly volume, and no surface may render it as one.
WAVE1_WAVE2_STITCHED_PARENT_IDS = frozenset({
    2929, 2938, 2939, 3179, 3188, 3190, 3217, 3321, 3541, 3569,
    2817, 2917, 3027, 3097, 3153, 3272, 3320, 3368, 3379, 3394,
    3404, 3432, 3454, 3469, 3516, 3566, 3575,
})
assert len(WAVE1_WAVE2_STITCHED_PARENT_IDS) == 27

# D-132 — the 18 parents the 2026-09-05 wave slice did not count. Parent job ids;
# accessions O75096, O75445, P09848, P11717, P17927, P46531, Q58EX2, Q86XX4, Q8TDX9,
# Q8TEM1, Q8WXG9, Q92673, Q96JQ0, Q96PZ7, Q9H251, Q9NYQ8, Q9NZR2, Q9Y493.
#
# ⚠ These already carried `pdb_path` at inventory time. They are not a fresh persist —
# the 2026-09-08 laptop `write_stitched` batch (18/18 PASS, off-block PAE null-only) is
# LOCAL PROOF under C:\Users\mdk32\artifacts\hold48_stitch_18_2026-09-08\, not the Fly
# write event, and must never be cited as one.
#
# ⚠ 3356 is IGF2R P11717 on the CENSUS side. Cohort job 57 is still the CUDA-OOM row —
# two populations, neither substituted (D-081).
ADDITIONAL_ASSEMBLED_PARENT_IDS = frozenset({
    3020, 3131, 3082, 3356, 3420, 3120, 3559, 3086, 3237,
    2974, 3209, 2973, 3067, 2920, 3094, 2837, 2959, 3124,
})
assert len(ADDITIONAL_ASSEMBLED_PARENT_IDS) == 18
assert not (ADDITIONAL_ASSEMBLED_PARENT_IDS & WAVE1_WAVE2_STITCHED_PARENT_IDS)

# D-132 — the MEASURED assembled inventory: parent jobs with tile children AND a non-null
# ``protein_analyses.pdb_path`` (path shape /data/artifacts/{parent_job_id}/structure.pdb
# with pae.json.gz beside it). Owner ops read the live Fly DB read-only through the proxy
# on 2026-09-08 and counted 45; the figure is handed here AS RECORDED and this module did
# not run the query.
#
# A frozenset and a date, deliberately — not a live COUNT(*). Every figure on these
# surfaces is a frozen literal carrying the date it was measured (D-053 dec 5 / D-094
# amendment 1), so a number that moves without a commit would be unattributable. When the
# volume changes, this set and ``ASSEMBLED_INVENTORY_MEASURED_ON`` move in the same commit
# that records the new query output, or they are wrong.
ASSEMBLED_PARENT_IDS = WAVE1_WAVE2_STITCHED_PARENT_IDS | ADDITIONAL_ASSEMBLED_PARENT_IDS
assert len(ASSEMBLED_PARENT_IDS) == 45
ASSEMBLED_INVENTORY_MEASURED_ON = "2026-09-08"
ASSEMBLED_INVENTORY_SOURCE = (
    "read-only Fly DB query 2026-09-08 — parent jobs with tile children and "
    "protein_analyses.pdb_path set; handed to the repo as recorded, not re-run here"
)
WAVE1_WAVE2_CLOSEOUT_MEASURED_ON = "2026-09-05"

IGF2R_ACCESSION = "P11717"
IGF2R_COHORT_JOB_ID = 57

STRUCTURE_KIND_LABEL = {
    "single-pass": "single-pass",
    "assembled": "assembled (provisional)",
    "tiles_only": "tiles only",
    "mucin": "mucin — not folded",
}

# ⚠ The bucket a row with no `structure_kind` falls into, and its label says the absence rather
# than implying a fold. A blank reads as `single-pass` — a forward pass that never happened
# (D-133) — so the missing field is named here once and both the payload and the surface read it.
STRUCTURE_KIND_NONE = "none"
STRUCTURE_KIND_NOT_RECORDED_LABEL = "not recorded"

# ⚠ The order the kinds are SERVED in (D-135), not a ranking — the two folded kinds first because
# they are what a reader came for, then the two absences, then the unrecorded rows. It ships in the
# payload so a consumer never has to type its own list of categories to iterate (Constraint A's
# neighbouring failure: a component that decides which kinds exist stops showing a new one).
STRUCTURE_KIND_ORDER = (
    "assembled", "single-pass", "tiles_only", "mucin", STRUCTURE_KIND_NONE,
)

# ⚠ The two kinds that mean a STRUCTURE EXISTS — mirrors `apply_structure_kind`, which sets
# `folded: True` for exactly these and `False` for `tiles_only` / `mucin`. Named so a consumer of a
# structure kind never has to re-derive "does this protein have a fold", which is the kind of second
# definition that drifts silently (a tile window is not the outward-facing region; a mucin was never
# folded here).
STRUCTURE_KINDS_WITH_A_FOLD = frozenset({"assembled", "single-pass"})

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
    # ⚠ D-118: /target/:id is a primary-key lookup (tranche-exempt). A stitched census
    # parent typed as /target/2817 must still carry the assembler flag so 3Dmol cannot
    # present winner-tile pLDDT as one forward pass.
    # ⚠ D-134: one rule, `is_assembled_parent_row`. This used to compare the meta tag to
    # the bare string `parent`, which the live volume does not use — so `/api/target/2817`
    # answered `assembled: false` for a stitched parent and 3Dmol was free to present
    # winner-tile pLDDT as one forward pass, the exact thing this flag exists to prevent.
    out["hold48_kind"] = meta.get("hold48_kind")
    out["assembled"] = is_assembled_parent_row(row)
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
        out = [list_projection(r) for r in rows]

    # ⚠⚠ ALIASES, so `HER2` reaches `ERBB2` HERE TOO. The alias index (`D-101`) was built for the
    # census and wired only there, so the owner searching the cohort for the name on the drug label
    # found nothing — while `ERBB2` sat in this very list, folded and ranked. `F-052`'s shape: the
    # convention obeyed by every caller except the one nobody revisited.
    # ⚠ Derived from the pinned UniProt cache, never typed (`scripts/build_protein_aliases.py`).
    # ⚠⚠ THE ROWS ARE ALREADY BUILT. A failure here costs the aliases and NOTHING ELSE — `F-054` is
    # the entry for what happens when a guard is wider than the optional thing it guards.
    try:
        from core.protein_aliases import aliases_by_accession
        alias_map = aliases_by_accession()
    except Exception:                          # noqa: BLE001
        alias_map = {}                         # ⚠ search degrades to gene/accession/label matching
    for row in out:
        row["aliases"] = alias_map.get(row.get("accession")) or None
    return out


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
    """The per-residue pLDDT array beside the stored structure, derived from the absolute
    ``pdb_path`` (never from client input). ``None`` when there is no structure to sit beside.

    ⚠ D-118: ``write_stitched`` writes ``stitched_plddt.json`` next to ``stitched.pdb``.
    Looking only for ``plddt.json`` 404s an assembled parent and the viewer degrades.
    The path is still a sibling of the stored PDB — no client value reaches the filesystem.
    """
    pdb_path = get_structure_path(engine, analysis_id)
    if not pdb_path:
        return None
    parent = Path(pdb_path).parent
    name = Path(pdb_path).name
    stitched = parent / "stitched_plddt.json"
    classic = parent / "plddt.json"
    if name == "stitched.pdb":
        if stitched.is_file():
            return str(stitched)
        if classic.is_file():
            return str(classic)
        return str(stitched)
    if classic.is_file():
        return str(classic)
    if stitched.is_file():
        return str(stitched)
    return str(classic)


# ── D-139: which path's bytes we actually hand out, per parent ──────────────────
#
# ⚠ Everything below is SELECTION, over paths the readers above already resolve.
# It writes nothing, copies nothing, and moves no threshold. The default is still
# the assembler: a parent flips only by allowlist + gate (app/served_path_policy).

def _job_id_for(session: Session, analysis_id: int) -> Optional[int]:
    """The job id for an analysis row, or ``None``. Production numbering does not
    guarantee job id == analysis id, so the served-path gate is offered both."""
    return session.scalar(
        select(JobRecord.id).where(JobRecord.analysis_id == analysis_id)
    )


def served_path_block(
    engine: Any,
    analysis_id: int,
    *,
    artifact_root: Optional[Path | str] = None,
) -> Optional[dict[str, Any]]:
    """The D-139 served-path decision for one analysis id, or ``None`` if unknown.

    ⚠ Fail-closed at every step: an unknown id, a row with no ``pdb_path``, a
    parent outside the recorded 17, an absent or refused D-126 tree, or a
    missing ``stitched.pdb`` all resolve to the assembler under a named reason.
    """
    with Session(engine) as s:
        row = s.get(ProteinAnalysis, analysis_id)
        if row is None:
            return None
        job_id = _job_id_for(s, analysis_id)
        meta = row.meta
        pdb_path = row.pdb_path
    return resolve_served_path(
        artifact_root,
        parent_analysis_id=analysis_id,
        parent_job_id=job_id,
        assembler_pdb_path=pdb_path,
        meta=meta,
    )


def served_structure_path(
    engine: Any,
    analysis_id: int,
    *,
    artifact_root: Optional[Path | str] = None,
) -> Optional[str]:
    """The PDB actually served for this id (D-139), or ``None`` → 404.

    Identical to ``get_structure_path`` for every parent the gate does not
    clear, which today is every parent in this repository: no
    ``confidence_kabsch/`` tree is committed here.
    """
    block = served_path_block(engine, analysis_id, artifact_root=artifact_root)
    if block is None:
        return None
    return block.get("served_pdb_path") or get_structure_path(engine, analysis_id)


def served_plddt_path(
    engine: Any,
    analysis_id: int,
    *,
    artifact_root: Optional[Path | str] = None,
) -> Optional[str]:
    """pLDDT for the path actually served (D-139), falling back to the assembler's.

    ⚠ The D-126 tree runs its own ``winning_tile``, so its pLDDT array can
    differ from the assembler's; colouring served D-126 coordinates with
    assembler confidence would be an incoherence. The fallback is independent
    and fail-closed — a flipped parent whose tree carries no
    ``stitched_plddt.json`` keeps the assembler's rather than 404ing.
    """
    block = served_path_block(engine, analysis_id, artifact_root=artifact_root)
    if block is not None and block.get("served") == SERVED_CONFIDENCE_KABSCH:
        sibling = confidence_kabsch_sibling_path(
            block["served_pdb_path"], "stitched_plddt.json"
        )
        if sibling is not None:
            return str(sibling)
    return get_plddt_path(engine, analysis_id)


def served_pae_path(
    engine: Any,
    analysis_id: int,
    *,
    artifact_root: Optional[Path | str] = None,
) -> Optional[str]:
    """PAE for the path actually served (D-139), falling back to the stored one."""
    block = served_path_block(engine, analysis_id, artifact_root=artifact_root)
    if block is not None and block.get("served") == SERVED_CONFIDENCE_KABSCH:
        sibling = confidence_kabsch_sibling_path(
            block["served_pdb_path"], "stitched_pae.json"
        )
        if sibling is not None:
            return str(sibling)
    return get_pae_path(engine, analysis_id)


def served_download_stem(
    engine: Any,
    analysis_id: int,
    *,
    artifact_root: Optional[Path | str] = None,
) -> str:
    """The download stem for the path actually served (D-139).

    ⚠ A flipped parent downloads as ``stitched_confidence_kabsch``, never
    ``stitched``. Two files with one name and different coordinates is a bug
    that outlives the browser tab it started in.
    """
    block = served_path_block(engine, analysis_id, artifact_root=artifact_root)
    if block is not None and block.get("served") == SERVED_CONFIDENCE_KABSCH:
        return str(block["download_stem"])
    return download_stem(engine, analysis_id)


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
    _attach_census_sibling(engine, projected)
    return {
        "coverage": coverage(rows),
        "population_key": COVERAGE_POPULATION_KEY,
        "census_sibling_key": CENSUS_SIBLING_KEY,
        "failed": sum(1 for r in projected if r["fold_status"] == "failed"),
        "rows": projected,
    }


# ⚠⚠ THE POPULATION THIS FIELD BELONGS TO, NAMED IN THE PAYLOAD (D-016 / D-135). A JSON consumer
# that finds `structure_kind: "assembled"` on a coverage row and no statement of which population it
# describes will read it as the cohort's own fold — which is the precise mistake the field exists to
# prevent. So it says so, on the wire, beside the value.
CENSUS_SIBLING_KEY = {"kind": "CROSS_POPULATION_FACT", "text": (
    "Present only on a cohort row that did NOT fold here, and only when that accession has a "
    "representative in the CENSUS (D-087 / D-118). It states that a different measurement of the "
    "same protein exists — a different span definition (D-081) — and it is NEVER the cohort's own "
    "fold: `fold_status` stays `failed` or `not_folded` (D-043) and `coverage` is untouched. "
    "⚠ It deliberately carries NO `analysis_id`: 75 of the 82 cohort accessions also appear in the "
    "census, so an id here is one careless render away from putting a census fold under a cohort "
    "target's own link. Consumers address the census row by ACCESSION, which /api/census/{id} has "
    "resolved since D-118."
)}


def _attach_census_sibling(engine: Any, rows: list[dict[str, Any]]) -> None:
    """Name the CENSUS representative of a cohort row that did not fold here (D-135).

    ⚠⚠ THE DIRECTION IS THE ONLY NEW THING. ``_attach_cohort_fold`` already tells a census row that
    a cohort fold of the same accession exists; this tells a cohort row the same about the census.
    **IGF2R is the case that asked for it:** the cohort attempted it and died of CUDA OOM, and since
    **D-134** the census representative of `P11717` is finally visible as an **assembled** parent
    rather than mis-served as single-pass. Two measurements of one protein by one model, and the
    coverage table could describe only one of them — in a paragraph, in a table cell.

    ⚠⚠ NO ``analysis_id``, AND THAT IS THE POINT rather than an omission. See
    ``tests/test_no_census_leak_on_tranche_zero.py``: 75 of the 82 cohort accessions are also census
    rows, and a census id reaching a cohort surface is a *named stop condition* — the row's Target
    link would then open a fold measured under a different span definition (D-081) with nothing on
    screen saying so. A field that does not exist cannot be rendered by mistake; the surface links
    by **accession**, which the census detail route resolves (D-118).

    ⚠ ONE representative rule, not a second one. ``choose_census_representative`` is the same
    function ``list_census`` and ``resolve_census_accession`` use, so this cannot come to disagree
    with the census page it points at — including *"never a tile as the protein"* (D-118).

    ⚠ SCOPED QUERY, not the whole census. ``list_census(engine)`` is the 7.1 MB build; coverage is a
    hot page and asks about a handful of accessions, so the read is narrowed to them. The
    REPRESENTATIVE RULE is still shared — it is the *query* that is narrowed, never the definition.

    ⚠ A folded cohort row is skipped entirely. Where the cohort has its own measurement, the census
    is not the interesting fact and a note there would be noise on 60-odd rows.

    ⚠ Additive and non-load-bearing: a failure here costs the note and nothing else. Coverage is
    the honest-denominator page and must render without it (the ``_attach_cohort_fold`` posture).
    """
    wanted = [
        r["accession"] for r in rows
        if r.get("accession") and r.get("fold_status") != "folded"
    ]
    if not wanted:
        return
    try:
        with Session(engine) as session:
            census = session.scalars(
                select(ProteinAnalysis)
                # ⚠ `> COHORT_TRANCHE`, the POSITIVE census form — never `!=`, which excludes a
                # NULL-tranche row under three-valued logic and makes it invisible on both surfaces.
                .where(ProteinAnalysis.cohort_tranche > COHORT_TRANCHE)
                .where(ProteinAnalysis.input_value.in_(wanted))
            ).all()
    except Exception:                      # noqa: BLE001
        return
    by_acc: dict[str, list[ProteinAnalysis]] = {}
    for row in census:
        by_acc.setdefault(row.input_value, []).append(row)
    for row in rows:
        group = by_acc.get(row.get("accession"))
        if not group:
            continue
        picked = choose_census_representative(group)
        # ⚠ A tile is a window, not a protein (D-118). `choose_census_representative` already
        # refuses to return one as the representative; the guard states the requirement anyway,
        # because a caller inheriting that rule silently is how it stops holding.
        if picked is None or is_census_tile_row(picked[0]):
            continue
        _, kind = picked
        row["census_sibling"] = {
            "structure_kind": kind,
            "structure_kind_label": STRUCTURE_KIND_LABEL[kind],
            # ⚠⚠ SERVED, NOT RE-DERIVED ON THE SURFACE. `tiles_only` and `mucin` are NOT folded
            # proteins (see `apply_structure_kind`), and a surface deciding for itself which kinds
            # count as a structure is a second definition of "folded" one edit from disagreeing
            # with the census page it links to. The bridge is only honest where a structure exists.
            "folded": kind in STRUCTURE_KINDS_WITH_A_FOLD,
            # ⚠ the same note the census card carries, so "assembled" is never bare here either
            "assembler_note": (
                "assembled by pLDDT overlap, not superimposed; seam not solved"
                if kind == "assembled" else None
            ),
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


def _hold48_kind(row: ProteinAnalysis) -> Optional[str]:
    return (row.meta or {}).get("hold48_kind")


def is_census_tile_row(row: ProteinAnalysis) -> bool:
    """A tile is a window, not a protein (D-118)."""
    m = row.meta or {}
    if m.get("hold48_kind") == HOLD48_KIND_TILE:
        return True
    return m.get("parent_job_id") is not None and m.get("tile_start") is not None


def is_census_parent_row(row: ProteinAnalysis) -> bool:
    """A parent is the whole protein — whichever tag the volume happens to carry (D-134).

    ⚠⚠ THIS FUNCTION WAS `_hold48_kind(row) == HOLD48_KIND_PARENT` AND THAT IS THE D-134
    DEFECT. Ops persisted `parent_stitched`, a string the repo never held, so on Fly this
    returned `False` for **all 45** assembled parents: they fell through
    `choose_census_representative` into the `ordinary` branch and were served as
    `single-pass`, and the D-133 fold-type chips truthfully reported **0 assembled**.
    Measured 2026-09-08 on `https://pharmfoldmdk.fly.dev/api/census`.

    Two independent signals, because one of them already drifted once:
    the meta tag (any spelling in `HOLD48_PARENT_KINDS`), **or** a stored `pdb_path` whose
    basename is the one `write_stitched` writes. ⚠ A tile is disqualified first — a window
    is never the protein (D-118), and that precedence is what keeps the second, looser
    signal safe to add.
    """
    if is_census_tile_row(row):
        return False
    return is_parent_kind(_hold48_kind(row)) or is_stitched_artifact_path(row.pdb_path)


def is_assembled_parent_row(row: ProteinAnalysis) -> bool:
    """A parent that actually has a structure on disk — the one `assembled` rule (D-134).

    ⚠ THE single definition. `detail_projection`, `download_stem_for_row` and
    `census_detail`'s fallback each carried their own copy keyed on the bare string
    `parent`, so a fix in one would have left the others reporting the old answer.
    """
    return is_census_parent_row(row) and bool(row.pdb_path)


def _is_spare_tile(row: ProteinAnalysis) -> bool:
    if row.id in HOLD48_SPARE_TILE_IDS:
        return True
    return (row.meta or {}).get("parent_job_id") in HOLD48_SPARE_TILE_IDS


def choose_census_representative(
    group: list[ProteinAnalysis],
) -> Optional[tuple[ProteinAnalysis, str]]:
    """One analysis per accession. Never a tile as the protein. Prefer assembled parent.

    Spare tile ids 3693/3695/3696 never win. When a tile is the only complete cover
    (tiles-only parent), the *parent* row is returned, not the tile.

    ⚠⚠ D-134: `parents` is empty when `is_census_parent_row` does not recognise the tag
    ops wrote, and an empty `parents` does not fail — the row keeps falling to `ordinary`
    and comes back a perfectly plausible **single-pass** protein. That silence is why the
    defect survived D-118, D-120, D-132 and D-133: nothing on any surface distinguishes
    *this protein was folded in one pass* from *we failed to notice it was assembled*.
    """
    if not group:
        return None
    tiles = [r for r in group if is_census_tile_row(r)]
    parents = [r for r in group if is_census_parent_row(r)]
    usable_tiles = [r for r in tiles if r.pdb_path and not _is_spare_tile(r)]
    if not usable_tiles:
        # last resort: a spare may be the only complete cover — still return the PARENT
        usable_tiles = [r for r in tiles if r.pdb_path]
    assembled = [r for r in parents if is_assembled_parent_row(r)]
    if assembled:
        return min(assembled, key=lambda r: r.id), "assembled"
    if parents and usable_tiles:
        return min(parents, key=lambda r: r.id), "tiles_only"
    mucin_rows = [
        r for r in group
        if (_hold48_kind(r) == "mucin" or is_mucin(r.input_value)) and not is_census_tile_row(r)
    ]
    non_tile_folded = [r for r in group if r.pdb_path and not is_census_tile_row(r)]
    if mucin_rows and not non_tile_folded:
        return min(mucin_rows, key=lambda r: r.id), "mucin"
    ordinary = [r for r in non_tile_folded if not is_census_parent_row(r)]
    if ordinary:
        return min(ordinary, key=lambda r: r.id), "single-pass"
    if non_tile_folded:
        row = min(non_tile_folded, key=lambda r: r.id)
        return row, "assembled" if is_assembled_parent_row(row) else "single-pass"
    return None


def apply_structure_kind(proj: dict[str, Any], row: ProteinAnalysis, kind: str) -> dict[str, Any]:
    """Stamp the D-118 identity fields. Tiles-only / mucin are not folded proteins."""
    proj["hold48_kind"] = _hold48_kind(row)
    proj["structure_kind"] = kind
    proj["structure_kind_label"] = STRUCTURE_KIND_LABEL[kind]
    if kind == "assembled":
        proj["folded"] = True
        proj["assembler_note"] = (
            "assembled by pLDDT overlap, not superimposed; seam not solved"
        )
    elif kind == "single-pass":
        proj["folded"] = True
    elif kind == "tiles_only":
        proj["folded"] = False
        proj["mean_plddt"] = None
        proj["not_folded_reason"] = "tiles_only"
        proj["not_folded_copy"] = (
            "tiles exist for this protein; they have not been assembled into a parent "
            "structure. A tile window is not the ectodomain"
        )
        proj["profile_status"] = "not_folded"
    elif kind == "mucin":
        proj["folded"] = False
        proj["mean_plddt"] = None
        proj["not_folded_reason"] = "mucin_out_of_class"
        proj["not_folded_copy"] = (
            "mucin — out of class; never ESMFold (D-111). Rental is closed (pod Terminated)"
        )
        proj["profile_status"] = "not_folded"
    return proj


def igf2r_two_population_copy() -> dict[str, str]:
    """Cohort OOM and census tiles are different measurements (D-081 / D-120)."""
    return {
        "gene": "IGF2R",
        "accession": IGF2R_ACCESSION,
        "cohort": (
            f"Cohort IGF2R (tranche 0, job {IGF2R_COHORT_JOB_ID}) is a CUDA OOM "
            "failure — a different measurement under a different span definition."
        ),
        "census": (
            "Census IGF2R tiles (and any later assembly) are a later span "
            "definition (D-081). Neither substitutes for the other."
        ),
    }


def _tile_window(row: ProteinAnalysis) -> tuple[Optional[int], Optional[int]]:
    m = row.meta or {}
    return m.get("tile_start"), m.get("tile_end")


def assign_tile_roles(tiles: list[ProteinAnalysis]) -> dict[int, str]:
    """Chosen vs spare per window. Prefer lower ids; named unused 3693/3695/3696."""
    by_window: dict[tuple[Any, Any], list[ProteinAnalysis]] = {}
    for t in tiles:
        by_window.setdefault(_tile_window(t), []).append(t)
    roles: dict[int, str] = {}
    for group in by_window.values():
        named_spares = [t for t in group if t.id in HOLD48_SPARE_TILE_IDS]
        rest = [t for t in group if t.id not in HOLD48_SPARE_TILE_IDS]
        pool = rest if rest else named_spares
        preferred = [t for t in pool if t.id in HOLD48_PREFERRED_TILE_IDS]
        choose_from = preferred if preferred else pool
        chosen = min(choose_from, key=lambda t: t.id)
        for t in group:
            roles[t.id] = "chosen" if t.id == chosen.id else "spare"
    return roles


def _tile_is_complete(row: ProteinAnalysis) -> bool:
    return bool(row.pdb_path) and bool(row.pae_json_path)


def sibling_readiness(parent: ProteinAnalysis, tiles: list[ProteinAnalysis]) -> dict[str, Any]:
    """Readiness from sibling tile rows — not a restitch GO (D-120)."""
    span = int((parent.meta or {}).get("span_aa") or 0)
    windows: list[tuple[int, int]] = []
    seen: set[tuple[Any, Any]] = set()
    for t in tiles:
        start, end = _tile_window(t)
        key = (start, end)
        if start is None or end is None or key in seen:
            continue
        seen.add(key)
        windows.append((int(start), int(end)))
    present = 0
    missing: list[dict[str, Any]] = []
    for start, end in windows:
        group = [t for t in tiles if _tile_window(t) == (start, end)]
        if any(_tile_is_complete(t) for t in group):
            present += 1
        else:
            missing.append({"start": start, "end": end})
    uncovered = None
    if span >= 1 and windows:
        covered: set[int] = set()
        for start, end in windows:
            covered.update(range(start, end + 1))
        uncovered = sum(1 for i in range(1, span + 1) if i not in covered)
    return {
        "source": "sibling_snapshot",
        "expected_n": len(windows),
        "present_complete_n": present,
        "missing": missing,
        "uncovered_n": uncovered if uncovered is not None else 0,
        "ready": (not missing) and (uncovered == 0) and len(windows) > 0,
        "note": (
            "sibling snapshot from analyses on this accession — ops numbers, "
            "not a restitch GO. Live stitch_readiness needs a parent jobs row "
            "and the emit-time UniProt snap (D-116)."
        ),
    }


def _readiness_from_gate(session: Session, parent: ProteinAnalysis) -> Optional[dict[str, Any]]:
    """Try D-116 stitch_readiness. None if the parent job or snap is unavailable."""
    parent_job = session.scalars(
        select(JobRecord).where(JobRecord.analysis_id == parent.id)
    ).first()
    if parent_job is None:
        return None
    try:
        from core.hold48 import stitch_readiness
        ready = stitch_readiness(session, parent_job, parent)
    except Exception:  # noqa: BLE001 — a missing snap must not 500 the card
        return None
    return {
        "source": "stitch_readiness",
        "expected_n": ready.expected_n,
        "present_complete_n": ready.present_complete_n,
        "missing": [
            {"start": spec.start, "end": spec.end, "tile_index": spec.tile_index}
            for spec in ready.missing
        ],
        "uncovered_n": ready.uncovered_n,
        "ready": ready.ready,
        "note": "live stitch_readiness (D-116) — ops numbers, not a restitch GO.",
    }


def download_stem_for_row(
    row: ProteinAnalysis,
    *,
    role: Optional[str] = None,
    tile_n: Optional[int] = None,
) -> str:
    """Honest download basename: stitched / tileN / spare{id} / structure."""
    # ⚠ D-134: same one rule as the `assembled` flag. Keyed on the bare string `parent`,
    # this named a live stitched parent's download `structure.pdb` — an assembled artifact
    # downloaded under the filename of a single forward pass.
    if is_assembled_parent_row(row):
        return "stitched"
    if is_census_tile_row(row):
        if role == "spare" or row.id in HOLD48_SPARE_TILE_IDS:
            return f"spare{row.id}"
        if tile_n is not None:
            return f"tile{tile_n}"
        idx = (row.meta or {}).get("tile_index")
        if idx is not None:
            return f"tile{int(idx) + 1}"
        return "tile"
    return "structure"


def download_stem(engine: Any, analysis_id: int) -> str:
    """Route-layer filename stem from the stored row (D-034 §2a — no client path)."""
    with Session(engine) as session:
        row = session.get(ProteinAnalysis, analysis_id)
        if row is None:
            return "structure"
        if is_census_tile_row(row):
            siblings = [
                r for r in session.scalars(
                    select(ProteinAnalysis)
                    .where(ProteinAnalysis.input_value == row.input_value)
                    .where(ProteinAnalysis.cohort_tranche > COHORT_TRANCHE)
                ).all()
                if is_census_tile_row(r)
            ]
            roles = assign_tile_roles(siblings)
            chosen = sorted(
                [t for t in siblings if roles.get(t.id) == "chosen"],
                key=lambda t: (_tile_window(t)[0] or 0, t.id),
            )
            n = next((i + 1 for i, t in enumerate(chosen) if t.id == row.id), None)
            return download_stem_for_row(row, role=roles.get(row.id), tile_n=n)
        return download_stem_for_row(row)


def assembly_review(
    session: Session,
    parent: ProteinAnalysis,
    siblings: list[ProteinAnalysis],
    *,
    artifact_root: Optional[Path | str] = None,
) -> dict[str, Any]:
    """Review payload for an assembled parent (D-120 / PLAN §3.6 / D-125-B / D-126-B / D-127-B).

    Ops numbers, not a restitch GO. Kabsch-path, D-126-path, and
    D-127-path metrics are *read* from A's sibling trees when present —
    never invented, never persisted here. Default served PDB stays
    assembler.
    """
    tiles = [r for r in siblings if is_census_tile_row(r)]
    roles = assign_tile_roles(tiles)
    chosen = sorted(
        [t for t in tiles if roles.get(t.id) == "chosen"],
        key=lambda t: (_tile_window(t)[0] or 0, t.id),
    )
    chosen_n = {t.id: i + 1 for i, t in enumerate(chosen)}
    job_by_analysis = {
        j.analysis_id: j.id
        for j in session.scalars(
            select(JobRecord).where(
                JobRecord.analysis_id.in_([t.id for t in tiles] + [parent.id] or [0])
            )
        ).all()
    }
    readiness = _readiness_from_gate(session, parent) or sibling_readiness(parent, tiles)
    tile_rows: list[dict[str, Any]] = []
    tile_downloads: list[dict[str, Any]] = []
    for t in sorted(tiles, key=lambda r: (_tile_window(r)[0] or 0, r.id)):
        start, end = _tile_window(t)
        role = roles.get(t.id, "spare")
        stem = download_stem_for_row(t, role=role, tile_n=chosen_n.get(t.id))
        has_pae = bool(t.pae_json_path)
        status = "complete" if t.pdb_path else "incomplete"
        if t.pdb_path and not has_pae:
            status = "complete_no_pae"
        tile_rows.append({
            "analysis_id": t.id,
            "job_id": job_by_analysis.get(t.id),
            "tile_index": (t.meta or {}).get("tile_index"),
            "start": start,
            "end": end,
            "span_aa": (t.meta or {}).get("span_aa"),
            "status": status,
            "has_pae": has_pae,
            "role": role,
            "named_spare": t.id in HOLD48_SPARE_TILE_IDS,
            "preferred_lower_id": t.id in HOLD48_PREFERRED_TILE_IDS,
            "download_stem": stem,
        })
        tile_downloads.extend([
            {
                "name": f"{stem}.pdb",
                "href": f"/api/analyses/{t.id}/structure",
                "kind": "pdb",
                "available": bool(t.pdb_path),
                "role": role,
            },
            {
                "name": f"{stem}_plddt.json",
                "href": f"/api/analyses/{t.id}/plddt",
                "kind": "plddt",
                "available": bool(t.pdb_path),
                "role": role,
            },
            {
                "name": f"{stem}_pae.json",
                "href": f"/api/analyses/{t.id}/pae",
                "kind": "pae",
                "available": has_pae,
                "role": role,
            },
        ])
    parent_has_pae = bool(parent.pae_json_path)
    parent_job_id = job_by_analysis.get(parent.id)
    five_path = five_path_payload(
        artifact_root,
        parent_analysis_id=parent.id,
        parent_job_id=parent_job_id,
        assembler_pdb_path=parent.pdb_path,
        meta=parent.meta,
    )
    # D-125-B / D-126-B / D-127-B consumers keep their narrower views; the
    # wider payload is additive so an older reader cannot silently gain a path.
    four_path = {
        "assembler": five_path["assembler"],
        "kabsch": five_path["kabsch"],
        "confidence_kabsch": five_path["confidence_kabsch"],
        "piecewise_kabsch": five_path["piecewise_kabsch"],
    }
    triple_path = {
        "assembler": five_path["assembler"],
        "kabsch": five_path["kabsch"],
        "confidence_kabsch": five_path["confidence_kabsch"],
    }
    dual_path = {
        "assembler": five_path["assembler"],
        "kabsch": five_path["kabsch"],
    }
    # D-139 — which of those five is actually handed out for THIS parent. ⚠ The
    # D-126 block is passed in rather than re-read, so the card and the download
    # route cannot disagree about what is on disk. `default_served` is left
    # exactly as the path readers set it (assembler True, the rest False): the
    # default genuinely is still the assembler, and the flip is a per-parent
    # exception granted by allowlist + gate. The resolved answer rides on a
    # separate `served` key so no earlier decision's meaning is rewritten.
    served = resolve_served_path(
        artifact_root,
        parent_analysis_id=parent.id,
        parent_job_id=parent_job_id,
        assembler_pdb_path=parent.pdb_path,
        meta=parent.meta,
        confidence_kabsch=five_path["confidence_kabsch"],
    )
    for name, block in five_path.items():
        block["served"] = served["served"] == name
    return {
        "parent_analysis_id": parent.id,
        "parent_job_id": parent_job_id,
        "hold48_kind": _hold48_kind(parent),
        "in_wave1_wave2_inventory": parent.id in WAVE1_WAVE2_STITCHED_PARENT_IDS,
        # D-132 — membership in the measured 45. Checked against BOTH ids because
        # production numbering does not guarantee job id == analysis id (same reason the
        # spare-tile ids are checked both ways above), and the 18 arrived as job ids.
        "in_assembled_inventory": (
            parent.id in ASSEMBLED_PARENT_IDS
            or (parent_job_id is not None and parent_job_id in ASSEMBLED_PARENT_IDS)
        ),
        # ⚠ D-132. The live figure is 45 — parents assembled on the volume, measured
        # 2026-09-08. The 27 is the 2026-09-05 Wave1+Wave2 closeout slice INSIDE that 45
        # and is disclosed as such; it is never the live count. Both breakdowns ship, so
        # a reader gets the split rather than a total (D-016 / method note item 2).
        "inventory": {
            "unique_stitched_parents_n": 45,
            "measured_on": ASSEMBLED_INVENTORY_MEASURED_ON,
            "source": ASSEMBLED_INVENTORY_SOURCE,
            "wave1_wave2_closeout_n": 27,
            "wave1_wave2_measured_on": WAVE1_WAVE2_CLOSEOUT_MEASURED_ON,
            "wave1_pass": 10,
            "wave2_pass": 17,
            "additional_assembled_n": 18,
            "additional_note": (
                "18 additional assembled parents already on volume at inventory time "
                "(measured 2026-09-08) — not a fresh persist, and not restitched by any "
                "D-127 / D-128 / D-130 OPS run, all of which ran on the 27"
            ),
            "parent_ids": sorted(ASSEMBLED_PARENT_IDS),
            "wave1_wave2_parent_ids": sorted(WAVE1_WAVE2_STITCHED_PARENT_IDS),
            "additional_parent_ids": sorted(ADDITIONAL_ASSEMBLED_PARENT_IDS),
        },
        "readiness": readiness,
        "tiles": tile_rows,
        "chosen_tile_ids": [t.id for t in chosen],
        "spare_tile_ids": [t.id for t in tiles if roles.get(t.id) == "spare"],
        "downloads": {
            "stitched": [
                {
                    "name": "stitched.pdb",
                    "href": f"/api/analyses/{parent.id}/structure",
                    "kind": "pdb",
                    "available": bool(parent.pdb_path),
                },
                {
                    "name": "stitched_plddt.json",
                    "href": f"/api/analyses/{parent.id}/plddt",
                    "kind": "plddt",
                    "available": bool(parent.pdb_path),
                },
                {
                    "name": "stitched_pae.json",
                    "href": f"/api/analyses/{parent.id}/pae",
                    "kind": "pae",
                    "available": parent_has_pae,
                },
            ],
            "tiles": tile_downloads,
        },
        "assembler_note": (
            "assembled by pLDDT overlap, not superimposed; seam not solved"
        ),
        "seam_note": seam_note_for_five(
            five_path["kabsch"],
            five_path["confidence_kabsch"],
            five_path["piecewise_kabsch"],
            five_path["linker_seam"],
        ),
        "dual_path": dual_path,
        "triple_path": triple_path,
        "four_path": four_path,
        "five_path": five_path,
        # D-139 — the served path, named per parent with the reason it is that
        # one. A surface showing "assembler" without the reason cannot tell
        # "never eligible" from "the run refused it".
        "served_path": served,
        # D-129-B — the Phase 5 fate, keyed by parent job id. A label, never a
        # metric: it rewrites no seam row and reads no artifact tree. The
        # accept-refuse block arrives carrying the D-128 OPS rollup, because
        # the label may not travel without it (D-129 Spec §4).
        "phase5_fate": phase5_fate(parent_job_id),
    }


def canonical_census_analysis_id(engine: Any, analysis_id: int) -> Optional[int]:
    """Map a census analysis id to the protein representative (D-118).

    A missing id is returned unchanged so the caller 404s as unknown.
    A tile with no parent returns ``None`` — never serve the tile as the protein.
    """
    with Session(engine) as session:
        row = session.get(ProteinAnalysis, analysis_id)
        if row is None or row.cohort_tranche == COHORT_TRANCHE:
            return analysis_id
        if not is_census_tile_row(row):
            return analysis_id
        siblings = session.scalars(
            select(ProteinAnalysis)
            .where(ProteinAnalysis.input_value == row.input_value)
            .where(ProteinAnalysis.cohort_tranche > COHORT_TRANCHE)
        ).all()
    picked = choose_census_representative(list(siblings))
    if picked is None or is_census_tile_row(picked[0]):
        return None
    return picked[0].id


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
        "hold48_kind": meta.get("hold48_kind"),
        # ⚠⚠ NOT a score and never sortable as one. Stated on every row so no consumer has to
        # remember the bar.
        "scored": False,
        "not_scored_reason": meta.get("not_scored_reason"),
    }


def census_structure_kinds(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """One ``{kind, label, n}`` per structure kind PRESENT in ``rows`` (D-135).

    ⚠⚠ WHY THE ORDER IS IN THE PAYLOAD. The consumers are `/coverage`'s second-population strip
    and the Story's cold strip, and **Constraint A** (D-050 / D-051) bars them from typing a count
    — but a component that typed its own list of kinds to iterate would decide, in JSX, which
    categories exist. It would then quietly stop showing a kind the census acquires later, which is
    the same class of failure as a hardcoded count and harder to see. So the ORDER ships with the
    counts and the surface iterates what it is given.

    ⚠ The order is not a ranking, and there is nothing here to rank: the two folded kinds come
    first because they are what a reader came for, then the two absences, then the unrecorded rows.
    D-079 dec 1 bars scoring a census row and this orders categories, not proteins.

    ⚠ A kind with no rows gets **no entry**, so a surface cannot print `assembled 0` as though the
    census had been asked and answered zero — which is exactly what the D-133 chips truthfully
    showed for all 45 assembled parents before **D-134** repaired the identity check. A category
    that is absent from the data is absent from the payload; a category that is present states its
    own count.

    ⚠ The LABEL is the API's own (`STRUCTURE_KIND_LABEL`, plus the stated absence for a row with no
    kind), so the strip cannot come to spell a category differently from the column it links to.
    """
    n: dict[str, int] = {}
    labels: dict[str, str] = {}
    for r in rows:
        kind = r.get("structure_kind") or "none"
        n[kind] = n.get(kind, 0) + 1
        if kind not in labels and r.get("structure_kind_label"):
            labels[kind] = r["structure_kind_label"]
    return [
        {"kind": k, "label": labels.get(k, STRUCTURE_KIND_NOT_RECORDED_LABEL), "n": n[k]}
        for k in STRUCTURE_KIND_ORDER
        if k in n
    ]


def census_summary(engine: Any) -> dict[str, Any]:
    """The census in four numbers, for the cold-open Story (`D-051` decision 1).

    ⚠⚠ WHY THIS ROUTE EXISTS AND IS NOT `/census` FILTERED CLIENT-SIDE. The census list is
    **7.1 MB uncompressed, 825 KB gzipped, and takes ~4.8 s** — measured against production. The
    Story is the most-read screen on the site and `D-051` calls it *"the thirty-second answer"*;
    making it download 3,467 rows to print two counts would spend five of those seconds on data it
    never renders. **The weight is the argument, not the tidiness.**

    ⚠ DERIVED FROM THE SAME BUILDER AS THE LIST, deliberately. Counting these separately — a second
    query with its own `where` — is how two surfaces come to disagree about one population, and this
    project has an entry for that. `list_census` is the single definition of *what a census row is*;
    this reduces it and adds nothing.

    ⚠ Every count states its key, in the payload, so the Story cannot print a number whose
    denominator a reader has to guess.

    ⚠ D-135 adds ``structure_kinds`` — the per-kind breakdown, reduced from the SAME rows, so
    `/coverage`'s second-population strip and the Story's cold strip can state how the census folds
    were produced without downloading the 7.1 MB list to count them. Method-note item 2: prefer the
    breakdown to the total. It is **not** a second coverage denominator and carries no fraction.
    """
    rows = list_census(engine)
    folded = [r for r in rows if r.get("folded") is not False and r.get("mean_plddt") is not None]
    plddts = [r["mean_plddt"] for r in folded]
    return {
        "manifest_rows": len(rows),
        "folded": len(folded),
        "max_mean_plddt": max(plddts) if plddts else None,
        "structure_kinds": census_structure_kinds(rows),
        "keys": {
            "manifest_rows": "every census protein row after D-118 identity (one per accession), folded or not (D-087)",
            "folded": ("census proteins with a parent or single-pass structure and a mean pLDDT "
                       "(tile windows are not proteins; D-118)"),
            "max_mean_plddt": "the highest mean pLDDT among those parent/single-pass folds",
            "structure_kinds": (
                "how each census protein's representative structure was PRODUCED (D-118 / D-133), "
                "counted over the same census rows as `manifest_rows` — one entry per kind present, "
                "in payload order, each carrying the API's own label. ⚠ These are census ROWS, "
                "never D-132's 45 assembled parent JOBS, and this is a breakdown of a DIFFERENT "
                "population from the cohort's 82 (D-081): it is not coverage of anything and has "
                "no denominator in common with /api/coverage."
            ),
        },
    }


def list_census(engine: Any) -> list[dict[str, Any]]:
    """Every census *protein* — one row per accession (D-118).

    ⚠ A tile is a window, not a protein. ``pdb_path`` on a ``hold48_kind=tile`` row must not
    mint a second census protein with the parent accession.
    """
    with Session(engine) as session:
        rows = session.scalars(
            select(ProteinAnalysis)
            # ⚠⚠ `> COHORT_TRANCHE`, NOT `!= COHORT_TRANCHE`. A bare negation reads as "everything
            # that is not the cohort" and would make a NULL-tranche row invisible on BOTH surfaces
            # — the cohort filter is `==` and excludes it, and a negation excludes it too under SQL
            # three-valued logic. An untagged row must not vanish; `census_untranched_count` exists
            # so it is COUNTED rather than quietly dropped.
            .where(ProteinAnalysis.cohort_tranche > COHORT_TRANCHE)
            .order_by(ProteinAnalysis.input_value)          # ⚠ accession, a neutral default
        ).all()
    by_acc: dict[str, list[ProteinAnalysis]] = {}
    for r in rows:
        by_acc.setdefault(r.input_value, []).append(r)
    out: list[dict[str, Any]] = []
    represented: set[str] = set()
    for acc, group in by_acc.items():
        picked = choose_census_representative(group)
        if picked is None:
            continue
        row, kind = picked
        proj = apply_structure_kind(census_projection(row), row, kind)
        out.append(proj)
        represented.add(acc)

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

    # ⚠⚠ THE NEVER-FOLDED ROWS JOIN THE LIST — owner ruling, 2026-08-20. Searching `HER2` returned
    # "no protein matches"; HER2 is in the manifest and was never folded, and a reader should not
    # have to parse fine print to learn the protein exists. A row with a STATUS beats a paragraph.
    # ⚠ They carry no fold-derived value at all — no pLDDT, no profile, no staining — and each
    # absence is a category, never a zero.
    # ⚠⚠ THE ROWS ARE ADDED BEFORE THE ENRICHMENT, AND THAT ORDERING IS THE FIX. The first version
    # wrapped BOTH in one `try`, so an AttributeError inside `_attach_cohort_fold` — reading a
    # column that does not exist — silently dropped ALL 777 unfolded rows from production. The
    # census list went back to 2,690 and HER2 vanished again, with no error anywhere.
    # ⚠ A degradation that removes 777 rows is not a degradation, it is the original defect
    # restored by an exception handler. The list survives without the enrichment; it must never
    # survive without the rows.
    # ⚠ D-118: skip accessions already represented (assembled / tiles-only / mucin-in-DB).
    # The v1 features artifact has zero tranche-5 lines, so the 48 hold parents would otherwise
    # appear as NOT FOLDED *and* as a folded/tiled row.
    try:
        from core.census_unfolded import unfolded_rows
        unfolded = [dict(r) for r in unfolded_rows() if r.get("accession") not in represented]
    except Exception:                      # noqa: BLE001
        unfolded = []                      # ⚠ only a missing MANIFEST can empty this
    out.extend(unfolded)
    if unfolded:
        try:
            _attach_cohort_fold(engine, unfolded)
        except Exception:                  # noqa: BLE001
            pass                           # ⚠ enrichment is optional; the rows are not
    out.sort(key=lambda r: r.get("accession") or "")
    return out


def _attach_cohort_fold(engine: Any, rows: list[dict]) -> None:
    """⚠⚠ THE CARD SAID "WAITING ON RENTED CAPACITY" FOR PROTEINS ALREADY FOLDED.

    Measured 2026-08-20 by walking the Targets surface: **30 of the 777 census rows marked NOT
    FOLDED also sit in the ranked 82**, and **29 of those are FOLDED there** — at the same span,
    same `boundary_method`, on rental/fp16. `ERBB2` is the case the owner asked about: the census
    said it awaited a fold that already existed one click away.

    ⚠ THE STATUS WAS NEVER WRONG. `above_local_ceiling` is true: 630 aa does exceed the local
    ceiling of 440, and the cohort fold ran on rented hardware. **The COPY was wrong.**

    ⚠⚠ THREE OUTCOMES, NOT TWO — and the thirtieth row is why. `IGF2R` is in the cohort and was
    NEVER FOLDED THERE EITHER: it was ATTEMPTED on rental and died of CUDA OOM at 2,491 aa. Saying
    "a fold exists" would be false, and saying "awaiting capacity" would also be false — it was
    tried and it failed. **An attempt that failed is neither of the other two.**

    ⚠ This attaches a FACT, not a link target. `D-081` measures the two populations under different
    span definitions and bars making one reachable through the other's route; the census route still
    refuses a cohort-only accession. What is added here is a statement that the other fold exists,
    with the span it was measured at, so a reader can judge the comparison rather than be handed it.
    """
    accs = [r["accession"] for r in rows if r.get("accession")]
    if not accs:
        return
    with Session(engine) as session:
        cohort = {
            r.input_value: r
            for r in session.scalars(
                select(ProteinAnalysis)
                .where(ProteinAnalysis.cohort_tranche == COHORT_TRANCHE)
                .where(ProteinAnalysis.input_value.in_(accs))
            ).all()
        }
    # ⚠ one query for the failure texts, from the JOB records where they actually live
    try:
        errors = _failed_accessions(engine)
    except Exception:                      # noqa: BLE001
        errors = {}                        # ⚠ a missing reason is a blank, never a dropped row
    for row in rows:
        c = cohort.get(row.get("accession"))
        if c is None:
            continue
        if c.pdb_path:
            row["cohort_fold"] = {
                "analysis_id": c.id,
                "mean_plddt": c.mean_plddt,
                # ⚠ the span it was folded at, so the reader can see whether it is the same molecule
                "fold_length": (c.meta or {}).get("span_aa") or (c.meta or {}).get("fold_length"),
                "census_span_aa": row.get("span_aa"),
            }
        else:
            # ⚠⚠ in the cohort and unfolded THERE too — an attempt, not a queue position
            row["cohort_attempt_failed"] = {
                "analysis_id": c.id,
                # ⚠⚠ `ProteinAnalysis` HAS NO `error` COLUMN. The first version read `c.error`,
                # which raised AttributeError — and the caller's broad `except` swallowed it and
                # silently dropped all 777 unfolded rows from the census list in production. The
                # failure text lives on the JOB, not the analysis: `failed_target_errors()`.
                "reason": (errors or {}).get(row.get("accession")),
            }
    return


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
    # ⚠ D-118: prefer the parent / assembled representative, never an arbitrary tile.
    census = [
        r for r in rows
        if r.cohort_tranche is not None and r.cohort_tranche > COHORT_TRANCHE
    ]
    picked = choose_census_representative(census)
    if picked is not None and not is_census_tile_row(picked[0]):
        return picked[0].id, "census"
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


def get_census_detail(
    engine: Any,
    analysis_id: int,
    *,
    artifact_root: Optional[Path | str] = None,
) -> Optional[dict[str, Any]]:
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
        # ⚠ D-118: a tile id is not a protein. The route remaps first; if we still have a
        # tile here, refuse rather than render a 1,656-aa window as the ectodomain.
        if is_census_tile_row(row):
            return None
        siblings = session.scalars(
            select(ProteinAnalysis)
            .where(ProteinAnalysis.input_value == row.input_value)
            .where(ProteinAnalysis.cohort_tranche > COHORT_TRANCHE)
        ).all()
        picked = choose_census_representative(list(siblings))
        kind = picked[1] if picked and picked[0].id == row.id else (
            # ⚠ D-134: `is_assembled_parent_row`, the same rule the representative used.
            "assembled" if is_assembled_parent_row(row)
            else "single-pass" if row.pdb_path else "tiles_only"
        )
        out = apply_structure_kind(census_projection(row), row, kind)
        out["sequence"] = (row.meta or {}).get("sequence")
        out["fold_provenance"] = (row.meta or {}).get("fold_provenance")
        out["structure_source"] = row.structure_source
        if kind == "assembled":
            out["assembly_review"] = assembly_review(
                session, row, list(siblings), artifact_root=artifact_root
            )
        if row.input_value == IGF2R_ACCESSION:
            out["igf2r_two_population"] = igf2r_two_population_copy()
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
