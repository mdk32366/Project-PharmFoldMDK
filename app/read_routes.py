"""D-034 — the four public read routes the React UI (D-033) consumes.

Thin over ``app/reads.py`` (the query/projection logic is unit-tested there without HTTP,
the same discipline as ``routes.py`` over ``artifacts.py``). All four are ``GET`` under
``/api`` and carry **no** ``require_token`` — the read surface is unauthenticated by design
(D-034 decision 4: public UniProt structures, no PII), while the ``/jobs`` write routes stay
bearer-guarded. The auth *property* that keeps this honest — ``/jobs`` guarded, ``/api`` open,
no third category — is pinned by an introspecting test (D-034 decision 5), not by a check on
these handlers.

| Route | Returns |
|---|---|
| `GET /api/analyses` | light list — one object per row (no sequence/provenance) |
| `GET /api/analyses/{id}` | full record incl. `sequence` + `fold_provenance` |
| `GET /api/analyses/{id}/structure` | the stored PDB file, `text/plain`, streamed |
| `GET /api/analyses/{id}/plddt` | the per-residue pLDDT array |
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse

from app import reads
from app.deps import get_engine
from core.cancer_associations import load_associations

read_router = APIRouter(prefix="/api")


@read_router.get("/analyses")
def list_analyses(engine: Any = Depends(get_engine)) -> list[dict]:
    """The light list — every fold as a ranking-table row (D-034 decision 1). No credential."""
    return reads.list_analyses(engine)


@read_router.get("/analyses/{analysis_id}")
def get_analysis(analysis_id: int, engine: Any = Depends(get_engine)) -> dict:
    """The full record for one fold, incl. ``sequence`` + ``fold_provenance`` (D-034 decision 1)."""
    record = reads.get_analysis(engine, analysis_id)
    if record is None:
        raise HTTPException(status_code=404, detail="unknown analysis")
    # ⚠⚠ THE SAME BLOCK THE CENSUS CARD GETS, DELIBERATELY. The 82 targets already carry the D-053
    # EXPRESSION grid; this is the IHC panel, a different measurement from a different source over
    # a different population. They sit as two distinct sections and are never merged — D-093's
    # traversal framing, and F-049's family is why the distinction is kept visible.
    from app.clinical_read import clinical_block
    record["clinical_block"] = clinical_block(engine, record.get("gene"))
    return record


@read_router.get("/analyses/{analysis_id}/structure")
def get_structure(analysis_id: int, engine: Any = Depends(get_engine)) -> FileResponse:
    """Stream the PDB at the row's **stored** ``pdb_path`` as ``text/plain`` (D-034 decision 2).
    404 — never 500 — when the id is unknown or the fold has no structure. The path is the
    stored absolute one; no client value reaches the filesystem (§2a, traversal defence)."""
    pdb_path = reads.get_structure_path(engine, analysis_id)
    if not pdb_path or not Path(pdb_path).is_file():
        raise HTTPException(status_code=404, detail="no structure for this analysis")
    return FileResponse(pdb_path, media_type="text/plain", filename="structure.pdb")


@read_router.get("/analyses/{analysis_id}/pae")
def get_pae(analysis_id: int, engine: Any = Depends(get_engine)) -> FileResponse:
    """Stream the stored PAE matrix. 404 — never 500 — when the id is unknown or carries no PAE.

    ⚠⚠ 2,692 of 2,771 rows have NO PAE and that is `F-042`, not a fault here. A 404 from this route
    is the ordinary case for a census protein, and the message says which so a caller does not read
    it as a missing file.

    ⚠ The path is the row's STORED path; no client value reaches the filesystem. Read-only: this
    route opens a file and returns it, and touches nothing.
    """
    pae_path = reads.get_pae_path(engine, analysis_id)
    if not pae_path:
        raise HTTPException(
            status_code=404,
            detail=("this analysis carries no PAE — 2,692 of 2,771 rows do not (F-042). "
                    "That is a recorded finding, not a missing file."))
    if not Path(pae_path).is_file():
        # ⚠ a stored path that does not resolve is a DIFFERENT failure from no path at all
        raise HTTPException(status_code=404,
                            detail="this analysis records a PAE path that does not resolve")
    return FileResponse(pae_path, media_type="application/json",
                        filename="pae.json.gz" if pae_path.endswith(".gz") else "pae.json")


@read_router.get("/analyses/{analysis_id}/plddt")
def get_plddt(analysis_id: int, engine: Any = Depends(get_engine)) -> list:
    """The per-residue pLDDT array that colours the viewer (D-034 decision 3). 404 when the id
    is unknown or the structure — and so its sibling ``plddt.json`` — does not exist."""
    plddt_path = reads.get_plddt_path(engine, analysis_id)
    if not plddt_path or not Path(plddt_path).is_file():
        raise HTTPException(status_code=404, detail="no plddt for this analysis")
    return json.loads(Path(plddt_path).read_text(encoding="utf-8"))


@read_router.get("/ranking")
def get_ranking(engine: Any = Depends(get_engine)) -> dict:
    """D-062: the latest VALID ranking run — the persisted pre-registered result (F-004) plus the
    56 per-target scores. Filters on validity so the zero-positive artifact (`ranking_results` id=1,
    marked invalid — D-064 dec 3) is never served; when no valid run exists, `result_status` is
    `not_run` (200, empty rows). No credential (D-034 posture). Reads persisted rows only."""
    return reads.ranking_payload(engine)


@read_router.get("/coverage")
def get_coverage(engine: Any = Depends(get_engine)) -> dict:
    """The D-038 coverage supplier UI Plan v2 §3.3/§4.1 need — the honest denominator the read
    list cannot give. The D-024 coverage object (partition over **all 82**, computed from the
    committed manifest, not the 42 folded rows) plus the per-target drill-down with `fold_status`
    joined from the DB. No credential (D-034 posture)."""
    return reads.coverage_payload(engine)


@read_router.get("/associations")
def get_associations() -> dict:
    """D-053: per-target cancer associations, DERIVED from the Kathad S3 grid (the whole map — 337
    pairs is ~30 KB, one route for one picture, per D-038). No engine: it is a pure file-derived
    supplier (``core/cancer_associations.py``); counts are computed from what loaded, never
    constants. No credential (D-034 posture)."""
    return load_associations()


@read_router.get("/census")
def list_census(engine: Any = Depends(get_engine)) -> list[dict]:
    """Every folded CENSUS row (D-087). ⚠ Separate from `/analyses`, which is the 82-target cohort.

    ⚠⚠ **No score, no rank, no order-by-suitability** — D-079 decision 1 bars scoring census rows,
    and every row states `scored: false` with its reason rather than relying on the absence of a
    field to convey it.
    """
    rows = reads.list_census(engine)
    # ⚠⚠ A STATUS, NEVER A VALUE. D-079 amendment 1 ruling 2: the census table is sortable on every
    # column (D-087), so a profile VALUE here would be one header click from a ranked shortlist —
    # and with null sorting last, the 1,293 refusals would sweep to the bottom with nothing on
    # screen saying the order means nothing. The supplier computes the profile and keeps only its
    # CATEGORY; `structural_profile()` stays the single implementation of the bar.
    # ⚠ Composed at the route, from a module `app/reads.py` does not import — ruling 5's wall.
    from app.census_profile_read import census_profile_statuses
    statuses = census_profile_statuses(engine)
    for r in rows:
        # ⚠⚠ ONLY FOLDED ROWS TAKE A PROFILE STATUS FROM THE SUPPLIER. A never-folded row already
        # carries `not_folded`, and `statuses.get(None)` would overwrite that with None — turning a
        # stated category back into the absent value it was written to replace.
        if r.get("folded") is not False:
            r["profile_status"] = statuses.get(r.get("id"))
    return rows


@read_router.get("/census/summary")
def census_summary(engine: Any = Depends(get_engine)) -> dict:
    """The census in four numbers, for the cold-open Story.

    ⚠⚠ REGISTERED **BEFORE** `/census/{analysis_id}`, AND THE ORDER IS LOAD-BEARING. FastAPI matches
    routes in declaration order, and `{analysis_id}` is a `str` since accessions became valid keys —
    so declared after, `/api/census/summary` would match the DETAIL route, be looked up as the
    accession `SUMMARY`, and return **404 with a perfectly sensible message about an unknown census
    protein**. A wrong-but-plausible answer, produced by declaration order.
    """
    return reads.census_summary(engine)


@read_router.get("/census/{analysis_id}")
def get_census_detail(analysis_id: str, engine: Any = Depends(get_engine)) -> dict:
    """One census protein: status, span topology (F-037), and cancer-association COVERAGE.

    ⚠ A cohort id here is a 404, not a redirect — the two populations are measured under different
    span definitions (D-081) and must not be reachable through one another's route.

    ⚠⚠ AN ACCESSION IS ACCEPTED HERE AND IT USED TO 422. The param was `int`, so `/census/P28908` —
    the first thing a person tries, because the accession is what the table SHOWS — failed
    validation. **422 says "your input was malformed." It was not: it was the right protein under
    the wrong key**, which is a different message and a different fix.

    ⚠ The population boundary is unchanged and is the reason this resolves rather than redirects: a
    COHORT accession still does not load here. It returns 404 **naming where it lives**, because
    `D-081` measures the two under different span definitions and silently serving one for the other
    would hand back a row measured by a rule the caller did not ask for.
    """
    if analysis_id.isdigit():
        resolved = int(analysis_id)
    else:
        resolved, outcome = reads.resolve_census_accession(engine, analysis_id)
        # ⚠⚠ THE NEVER-FOLDED MANIFEST IS CHECKED BEFORE THE COHORT VERDICT, AND THE ORDER IS THE
        # WHOLE BUG. `P04626`/ERBB2 is in BOTH populations: it is one of the ranked 82 AND a census
        # manifest row that was never folded. Asking "is it cohort?" first answered yes and 404'd
        # the very card the census list had just linked to. A protein being in one population does
        # not stop it being in the other, and this route serves the census one.
        if resolved is None:
            from core.census_unfolded import unfolded_rows
            acc = analysis_id.strip().upper()
            row = next((r for r in unfolded_rows() if r["accession"] == acc), None)
            if row is not None:
                # ⚠⚠ THE SAME ATTACHMENT AS THE LIST, AND IT MUST BE. The card is where a reader
                # actually decides what to believe, so a card that omitted the cohort fold while
                # the list showed it would be the worse half of the defect, not a smaller one.
                out = dict(row)
                reads._attach_cohort_fold(engine, [out])
                return out
        if outcome == "cohort":
            raise HTTPException(
                status_code=404,
                detail=("%s is one of the 82 ranked targets, not a census protein. It is measured "
                        "under a different span definition (D-081) and is served at /targets, not "
                        "here." % analysis_id.strip().upper()))
        if resolved is None:
            raise HTTPException(
                status_code=404,
                detail=("no census protein carries the accession %s"
                        % analysis_id.strip().upper()))
    record = reads.get_census_detail(engine, resolved)
    if record is None:
        raise HTTPException(status_code=404, detail="unknown census analysis")
    # ⚠ D-079 amendment 1, ruled by amendment 2. Composed HERE, at the route, from a supplier that
    # `app/reads.py` does not import — ruling 5's wall is checkable at file granularity because the
    # module serving run 2's scores and the module serving census profiles are different files.
    # ⚠⚠ D-089 ruling 7: no second route. A block on the response this route already serves.
    from app.census_profile_read import census_profile_block
    # ⚠⚠ `resolved`, NEVER `analysis_id`. The path param is a `str` so an accession can be used as a
    # key; `resolved` is the int it resolves to. This line passed the RAW STRING to a supplier whose
    # signature is `analysis_id: int`, and `session.get(ProteinAnalysis, "A0AVI2")` on Postgres
    # raises — so EVERY ONE of the 2,690 folded census cards returned HTTP 500 in production.
    # ⚠⚠ AND THE GATE COULD NOT SEE IT. The suite runs on SQLite, whose type affinity accepts
    # `"1970"` as an integer primary key and returns `None` for `"A0AVI2"` WITHOUT RAISING. The
    # tests were green on a database that forgives exactly the mistake production rejects.
    record["structural_profile_block"] = census_profile_block(engine, resolved)
    # ⚠ D-093 edges 1 and 2 — the human-legible half: which tumours stained, and which
    # normal tissues also stain. Composed at the route from its own supplier.
    from app.clinical_read import clinical_block
    record["clinical_block"] = clinical_block(engine, record.get("gene"))
    return record
