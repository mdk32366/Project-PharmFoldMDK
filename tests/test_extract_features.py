"""D-058 — the extraction driver and loader (scripts/extract_features.py).

The read-API client is exercised against an injected `httpx.MockTransport`, so no network is
touched and the gate stays hermetic. The two D-058 Addendum-2 disciplines are the point:

- **§1** a structure-less row (IGF2R: 404 on structure and pLDDT) is recorded null-with-a-reason
  and does **not** crash the batch;
- **§2** features are extracted for **every** folded row, `held_out` included.

The loader writes `protein_features` into a SQLite engine (the D-005 test path), proving the row
shape round-trips before it is ever pointed at Postgres.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import httpx
import pytest

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

import extract_features as ef  # noqa: E402
from core.features import FEATURE_NAMES  # noqa: E402
from core.manifest import build_manifest  # noqa: E402

FIX = Path(__file__).resolve().parent / "fixtures"
PDB = (FIX / "gpbar1_id16.pdb").read_text(encoding="utf-8")
PLDDT = json.loads((FIX / "gpbar1_id16.plddt.json").read_text(encoding="utf-8"))

_MANIFEST = {r.accession: r for r in build_manifest()}


def _accession(method: str) -> str:
    for r in build_manifest():
        if r.boundary_method == method and not r.excluded:
            return r.accession
    raise AssertionError(f"no {method} accession in the manifest")


def _client(rows, structures, plddts) -> httpx.Client:
    """A hermetic read-API. `structures`/`plddts` map analysis_id -> value, or None to 404."""
    def handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path
        if path == "/api/analyses":
            return httpx.Response(200, json=rows)
        _, _, _, aid, kind = path.split("/")   # /api/analyses/{id}/{structure|plddt}
        store = structures if kind == "structure" else plddts
        val = store.get(int(aid))
        if val is None:
            return httpx.Response(404, text="not found")
        if kind == "structure":
            return httpx.Response(200, text=val)
        return httpx.Response(200, json=val)

    return httpx.Client(transport=httpx.MockTransport(handler))


def test_extract_one_target_end_to_end():
    """The §5 'done' criterion: pull one target end to end and get its six features, with the
    boundary method joined from the manifest, not the API row."""
    acc = _accession("sliced_ecd")
    row = {"id": 16, "accession": acc, "gene": "GPBAR1", "mean_plddt": 56.02,
           "disposition": "ranked", "tier": "local", "boundary_method": "sliced_ecd", "held_out": False}
    with _client([row], {16: PDB}, {16: PLDDT}) as client:
        rec = ef.extract_target(row, _MANIFEST.get(acc), client, "http://test")
    assert rec.boundary_method == "sliced_ecd"                      # joined from the manifest
    for name in FEATURE_NAMES:
        assert getattr(rec.row, name) is not None
    assert rec.row.null_reasons == {}


def test_structureless_row_is_null_with_reason_and_does_not_crash_the_batch():
    """IGF2R-shaped: an analysis row whose structure and pLDDT both 404 (D-058 Addendum 2 §1).
    The batch completes; the failed row records all six null with a reason naming the failure and
    is NOT confused with a low-confidence fold."""
    good_acc = _accession("sliced_ecd")
    fail_acc = _accession("whole")
    good = {"id": 16, "accession": good_acc, "gene": "GPBAR1", "mean_plddt": 56.02,
            "disposition": "ranked", "boundary_method": "sliced_ecd"}
    failed = {"id": 99, "accession": fail_acc, "gene": "IGF2R-LIKE", "mean_plddt": None,
              "disposition": "held_out", "boundary_method": "whole"}
    with _client([good, failed], {16: PDB, 99: None}, {16: PLDDT, 99: None}) as client:
        records = ef.extract_all("http://test", client)

    assert len(records) == 2, "the failed row must not drop out of the batch"
    by_id = {r.analysis_id: r for r in records}
    failed_row = by_id[99].row
    for name in FEATURE_NAMES:
        assert getattr(failed_row, name) is None
        assert name in failed_row.null_reasons
    assert "no structure" in failed_row.null_reasons["sasa_normalized"]
    assert failed_row.below_plddt_floor is None            # no pLDDT → floor undecidable, not a bool
    assert by_id[16].row.null_reasons == {}                # the good row still computes


def test_extraction_is_broad_and_includes_held_out():
    """D-058 Addendum 2 §2: extract broadly, filter late. A well-folded held_out target (MSLN's
    class) gets a feature row — it is not filtered at extraction, else it could never be
    *reported* as excluded (D-024)."""
    whole_acc = _accession("whole")
    sliced_acc = _accession("sliced_ecd")
    rows = [
        {"id": 16, "accession": sliced_acc, "gene": "RANKED", "mean_plddt": 70.0,
         "disposition": "ranked", "boundary_method": "sliced_ecd"},
        {"id": 17, "accession": whole_acc, "gene": "HELDOUT", "mean_plddt": 75.04,
         "disposition": "held_out", "boundary_method": "whole"},
    ]
    with _client(rows, {16: PDB, 17: PDB}, {16: PLDDT, 17: PLDDT}) as client:
        records = ef.extract_all("http://test", client)
    dispositions = {r.disposition for r in records}
    assert "held_out" in dispositions, "held_out targets must be extracted, not filtered"
    held = next(r for r in records if r.disposition == "held_out")
    assert held.boundary_method == "whole"                 # cross-method flag travels (D-021)
    assert held.row.mean_plddt_ecd is not None             # a well-folded target still computes


def test_loader_writes_protein_features_to_sqlite():
    """The loader round-trips the row shape into `protein_features` (the D-005 SQLite path) before
    it is ever pointed at Postgres. A null-with-reason row persists its reasons, never a mean."""
    from sqlalchemy import create_engine, select
    from sqlalchemy.orm import Session

    from core.features import extract_features
    from db.models import Base, ProteinAnalysis, ProteinFeatures, RankingRun

    engine = create_engine("sqlite://", future=True)
    Base.metadata.create_all(engine)
    with Session(engine) as s:
        run = RankingRun(target_list_version="test-v1", scorer_version="")
        s.add(run)
        s.flush()
        good = ProteinAnalysis(input_type="uniprot", input_value="ACC-GOOD")
        failed = ProteinAnalysis(input_type="uniprot", input_value="ACC-FAIL")
        s.add_all([good, failed])
        s.commit()
        good_id, failed_id = good.id, failed.id

    records = [
        ef.ExtractedRecord("ACC-GOOD", "GOOD", good_id, "ranked", "local", "sliced_ecd",
                           extract_features(PDB, PLDDT, boundary_method="sliced_ecd", mean_plddt=56.02)),
        ef.ExtractedRecord("ACC-FAIL", "FAIL", failed_id, "held_out", "rental", "whole",
                           extract_features(None, None, boundary_method="whole")),
    ]
    written = ef.load_features(engine, records)
    assert written == 2

    with Session(engine) as s:
        rows = s.execute(select(ProteinFeatures).order_by(ProteinFeatures.analysis_id)).scalars().all()
        assert len(rows) == 2
        stored = {r.analysis_id: r for r in rows}
        assert stored[good_id].sasa_normalized is not None
        assert stored[good_id].null_reasons == {}
        assert stored[good_id].ranking_run_id is not None          # tied to the latest ranking_run
        assert stored[failed_id].sasa_normalized is None
        assert set(FEATURE_NAMES) <= set(stored[failed_id].null_reasons)
        assert stored[failed_id].feature_version                   # version recorded even on a null row
