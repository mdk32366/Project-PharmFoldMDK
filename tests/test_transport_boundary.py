"""D-031 transaction-boundary + provenance-projection tests (the ruling's two open
items), written before the code.

The boundary is `persist_fold`: write the Volume files first, then the DB transaction,
and compensate on failure. Both failure directions are asserted hermetically by
injecting a raising collaborator — the same dependency-injection seam the codebase
already uses (fetcher, clock, fold). No real filesystem or DB error is needed; the
point is the ORDERING and the COMPENSATION, which are pure control flow.
"""

from __future__ import annotations

import gzip
import json

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.artifacts import AnalysisNotFound, persist_fold, persist_pae
from db.models import Base, JobRecord, ProteinAnalysis, RankingRun

PROV = {
    "model_id": "facebook/esmfold_v1", "model_revision": "rev", "dtype": "int8",
    "chunk_size": 64, "input_length": 50, "source": "sliced_ecd", "ecd_start": 20,
    "ecd_end": 69, "truncated": True, "length_cap": 2000, "original_length": 2500,
    "mean_plddt": 77.25, "ca_atom_count": 50, "folded_at": "2026-07-22T00:00:00+00:00",
}


@pytest.fixture
def engine():
    eng = create_engine("sqlite://")
    Base.metadata.create_all(eng)
    return eng


def _seed(engine) -> tuple[int, int]:
    with Session(engine) as s:
        run = RankingRun(target_list_version="t", scorer_version="")
        s.add(run)
        s.flush()
        a = ProteinAnalysis(input_type="uniprot", input_value="P0", ranking_run_id=run.id,
                            meta={"gene": "G", "sequence": "AAAA"})
        s.add(a)
        s.flush()
        j = JobRecord(analysis_id=a.id, status="pending", inference_settings={})
        s.add(j)
        s.commit()
        return a.id, j.id


def _cols(engine, analysis_id):
    with Session(engine) as s:
        a = s.get(ProteinAnalysis, analysis_id)
        return a.pdb_path, a.mean_plddt, a.pae_json_path, a.meta


def _kw():
    return dict(pdb="ATOM\n", plddt=[80.0] * 4,
                pae_gz=gzip.compress(json.dumps([[1.0]]).encode()), provenance=PROV)


# ── provenance projection (D-031 ruling (b)) ─────────────────────────────────

def test_projection_columns_and_meta(engine, tmp_path):
    analysis_id, job_id = _seed(engine)
    persist_fold(engine, str(tmp_path), job_id, **_kw())

    pdb_path, mean_plddt, pae_path, meta = _cols(engine, analysis_id)
    assert mean_plddt == 77.25                       # column
    assert pdb_path.endswith("structure.pdb")        # column → Volume path
    assert pae_path.endswith("pae.json.gz")          # column → Volume path
    # the WHOLE record survives into meta, §1a flags included, nothing dropped
    fp = meta["fold_provenance"]
    assert fp["truncated"] is True and fp["original_length"] == 2500
    assert fp["ca_atom_count"] == 50 and fp["dtype"] == "int8"
    # pre-fold meta untouched
    assert meta["gene"] == "G" and meta["sequence"] == "AAAA"


# ── boundary direction 1: failed Volume write leaves NO orphaned DB row ───────

def test_failed_volume_write_leaves_db_untouched(engine, tmp_path):
    analysis_id, job_id = _seed(engine)

    def boom(*a, **k):
        raise OSError("volume full")

    with pytest.raises(OSError):
        persist_fold(engine, str(tmp_path), job_id, **_kw(), write_files=boom)

    # post-fold columns stayed NULL — nothing points at a file that was never written
    pdb_path, mean_plddt, pae_path, meta = _cols(engine, analysis_id)
    assert (pdb_path, mean_plddt, pae_path) == (None, None, None)
    assert "fold_provenance" not in meta


# ── boundary direction 2: failed DB write leaves NO orphaned files ────────────

def test_failed_db_write_removes_written_files(engine, tmp_path):
    analysis_id, job_id = _seed(engine)

    def boom(*a, **k):
        raise RuntimeError("commit failed")

    with pytest.raises(RuntimeError):
        persist_fold(engine, str(tmp_path), job_id, **_kw(), update_analysis=boom)

    # the compensating delete ran: no files left with no row pointing at them
    assert not (tmp_path / str(job_id)).exists()
    pdb_path, mean_plddt, pae_path, _ = _cols(engine, analysis_id)
    assert (pdb_path, mean_plddt, pae_path) == (None, None, None)


# ── persist_pae — the D-036 out-of-band transfer, same compensated boundary ────

def _pae_gz():
    return gzip.compress(json.dumps([[1.0, 2.0]]).encode())


def test_persist_pae_writes_file_and_column(engine, tmp_path):
    analysis_id, job_id = _seed(engine)
    persist_pae(engine, str(tmp_path), job_id, pae_gz=_pae_gz())
    assert (tmp_path / str(job_id) / "pae.json.gz").is_file()
    _, _, pae_path, _ = _cols(engine, analysis_id)
    assert pae_path.endswith("pae.json.gz")


def test_persist_pae_unknown_job_raises(engine, tmp_path):
    with pytest.raises(AnalysisNotFound):
        persist_pae(engine, str(tmp_path), 9999, pae_gz=_pae_gz())


def test_persist_pae_failed_db_write_removes_only_the_pae_file(engine, tmp_path):
    analysis_id, job_id = _seed(engine)
    # a sibling from the earlier fold upload that MUST survive the compensation
    d = tmp_path / str(job_id)
    d.mkdir(parents=True)
    (d / "structure.pdb").write_text("ATOM\n")

    def boom(*a, **k):
        raise RuntimeError("commit failed")

    with pytest.raises(RuntimeError):
        persist_pae(engine, str(tmp_path), job_id, pae_gz=_pae_gz(), update_pae_path=boom)

    # only pae.json.gz was compensated away; the sibling and the NULL column are intact
    assert not (d / "pae.json.gz").exists()
    assert (d / "structure.pdb").is_file()
    _, _, pae_path, _ = _cols(engine, analysis_id)
    assert pae_path is None
