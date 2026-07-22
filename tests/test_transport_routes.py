"""D-031 Fly-transport route tests, written against the ruling BEFORE the code.

Hermetic: in-memory SQLite via SQLAlchemy (the D-005 test-DB pattern — create_all,
NOT the migration chain) + FastAPI's TestClient. These prove the ROUTES' own logic —
the FoldSpec projection, the post-fold write, idempotency, the endpoint-enforced
complete ordering, and per-route auth.

What is deliberately NOT proven here: `claim()`'s `SELECT … FOR UPDATE SKIP LOCKED`
atomicity — it is a syntax error on SQLite (D-012 §3) and stays the primitive's,
proven only in the `postgres` job (D-017). So `/claim`'s projection is tested with a
stubbed queue whose `.claim()` returns a known `Job`; the route's job is to turn that
Job + the stored analysis into the inline 8-field FoldSpec, and THAT is what runs here.
The real claim path reaches the route unchanged (D-031 §1).
"""

from __future__ import annotations

import gzip
import json
from typing import Optional

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select, text
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.main import create_app
from core.queue import Job, PostgresJobQueue
from db.models import Base, JobRecord, ProteinAnalysis, RankingRun

TOKEN = "test-secret-token"
AUTH = {"Authorization": f"Bearer {TOKEN}"}

SEQ = "MKTAYIAKQR" * 5          # 50 aa; the exact residues the worker must fold
SETTINGS = {
    "model_id": "facebook/esmfold_v1",
    "model_revision": "75a3841ee059df2bf4d56688166c8fb459ddd97a",
    "dtype": "int8",
    "chunk_size": 64,
    "source": "sliced_ecd",
    "ecd_start": 20,
    "ecd_end": 69,
}


class StubQueue:
    """Stands in for `PostgresJobQueue` only where SQLite cannot run the real thing
    (`claim`'s SKIP LOCKED). Records complete/fail so delegation is observable."""

    def __init__(self, claimable: Optional[Job] = None) -> None:
        self._claimable = claimable
        self.completed: list[int] = []
        self.failed: list[tuple[int, str]] = []

    def claim(self, worker_id: str) -> Optional[Job]:
        job, self._claimable = self._claimable, None
        return job

    def complete(self, job_id: int) -> None:
        self.completed.append(job_id)

    def fail(self, job_id: int, error: str) -> None:
        self.failed.append((job_id, error))


@pytest.fixture
def engine():
    # StaticPool + check_same_thread=False: one shared in-memory DB across threads, so
    # the TestClient's request thread sees the schema the fixture created (plain
    # `sqlite://` gives each thread its own empty :memory: db). Real Postgres is unaffected.
    eng = create_engine("sqlite://", connect_args={"check_same_thread": False},
                        poolclass=StaticPool)
    Base.metadata.create_all(eng)
    return eng


def _seed(engine) -> tuple[int, int]:
    """Insert a ranking_run + one analysis (with the folded sequence in meta) + one
    pending job. Returns (analysis_id, job_id)."""
    with Session(engine) as s:
        run = RankingRun(target_list_version="test", scorer_version="")
        s.add(run)
        s.flush()
        analysis = ProteinAnalysis(
            input_type="uniprot", input_value="P00001", ranking_run_id=run.id,
            meta={"gene": "TEST", "sequence": SEQ, "source": "sliced_ecd"},
        )
        s.add(analysis)
        s.flush()
        job = JobRecord(analysis_id=analysis.id, status="pending", inference_settings=SETTINGS)
        s.add(job)
        s.commit()
        return analysis.id, job.id


def _provenance(mean_plddt: float = 82.5) -> dict:
    return {
        "model_id": "facebook/esmfold_v1", "model_revision": SETTINGS["model_revision"],
        "dtype": "int8", "chunk_size": 64, "input_length": 50, "source": "sliced_ecd",
        "ecd_start": 20, "ecd_end": 69, "truncated": False, "length_cap": None,
        "original_length": 50, "mean_plddt": mean_plddt, "ca_atom_count": 50,
        "folded_at": "2026-07-22T00:00:00+00:00",
    }


def _upload_files(*, pae: bool = True) -> dict:
    files = {
        "pdb": ("structure.pdb", "ATOM  ...\n", "text/plain"),
        "plddt": ("plddt.json", json.dumps([80.0] * 50), "application/json"),
        "provenance": ("provenance.json", json.dumps(_provenance()), "application/json"),
    }
    if pae:
        files["pae"] = ("pae.json.gz", gzip.compress(json.dumps([[1.0, 2.0]]).encode()),
                        "application/gzip")
    return files


def _client(engine, tmp_path, queue) -> TestClient:
    app = create_app(engine=engine, artifact_root=str(tmp_path),
                     auth_token=TOKEN, queue=queue)
    return TestClient(app, raise_server_exceptions=True)


# ── /claim: the fold spec inline, all eight fields (D-031 §1) ─────────────────

def test_claim_returns_the_full_fold_spec_not_a_bare_id(engine, tmp_path):
    analysis_id, job_id = _seed(engine)
    job = Job(id=job_id, analysis_id=analysis_id, status="claimed",
              inference_settings=SETTINGS)
    client = _client(engine, tmp_path, StubQueue(claimable=job))

    r = client.post("/jobs/claim", json={"worker_id": "w1"}, headers=AUTH)

    assert r.status_code == 200
    body = r.json()
    # All eight FoldSpec fields, sequence joined from the stored analysis, tier params
    # from inference_settings — a bare id would omit these and reintroduce worker-fetch.
    assert body == {
        "job_id": job_id, "sequence": SEQ,
        "model_revision": SETTINGS["model_revision"], "dtype": "int8", "chunk_size": 64,
        "source": "sliced_ecd", "ecd_start": 20, "ecd_end": 69,
    }


def test_claim_empty_queue_is_204(engine, tmp_path):
    client = _client(engine, tmp_path, StubQueue(claimable=None))
    r = client.post("/jobs/claim", json={"worker_id": "w1"}, headers=AUTH)
    assert r.status_code == 204


# ── /artifacts: idempotent, writes the post-fold columns, stores gz as-is ─────

def test_artifacts_writes_post_fold_columns_and_files(engine, tmp_path):
    analysis_id, job_id = _seed(engine)
    client = _client(engine, tmp_path, StubQueue())

    r = client.post(f"/jobs/{job_id}/artifacts", files=_upload_files(), headers=AUTH)
    assert r.status_code == 204

    with Session(engine) as s:
        a = s.get(ProteinAnalysis, analysis_id)
        assert a.mean_plddt == 82.5
        assert a.pdb_path is not None and a.pae_json_path is not None
        assert a.structure_source == "esmfold"
        # full provenance preserved in meta (§1a flags must survive)
        fp = a.meta["fold_provenance"]
        assert fp["ca_atom_count"] == 50 and fp["truncated"] is False
    # the files actually landed on the Volume
    assert (tmp_path / str(job_id) / "structure.pdb").exists()
    assert (tmp_path / str(job_id) / "pae.json.gz").exists()


def test_artifacts_stores_compressed_pae_bytes_verbatim(engine, tmp_path):
    """The route stores the client's gzip bytes; it does not compress (D-031 PAE ruling)."""
    _, job_id = _seed(engine)
    client = _client(engine, tmp_path, StubQueue())
    files = _upload_files()
    sent = files["pae"][1]

    client.post(f"/jobs/{job_id}/artifacts", files=files, headers=AUTH)

    on_disk = (tmp_path / str(job_id) / "pae.json.gz").read_bytes()
    assert on_disk == sent                                   # byte-identical, not re-compressed
    assert json.loads(gzip.decompress(on_disk)) == [[1.0, 2.0]]


def test_artifacts_no_pae_leaves_path_null(engine, tmp_path):
    analysis_id, job_id = _seed(engine)
    client = _client(engine, tmp_path, StubQueue())
    client.post(f"/jobs/{job_id}/artifacts", files=_upload_files(pae=False), headers=AUTH)
    with Session(engine) as s:
        assert s.get(ProteinAnalysis, analysis_id).pae_json_path is None
    assert not (tmp_path / str(job_id) / "pae.json.gz").exists()


def test_artifacts_is_idempotent(engine, tmp_path):
    analysis_id, job_id = _seed(engine)
    client = _client(engine, tmp_path, StubQueue())
    r1 = client.post(f"/jobs/{job_id}/artifacts", files=_upload_files(), headers=AUTH)
    r2 = client.post(f"/jobs/{job_id}/artifacts", files=_upload_files(), headers=AUTH)
    assert r1.status_code == r2.status_code == 204
    # one job dir, one set of files, no error on the retry
    files = list((tmp_path / str(job_id)).iterdir())
    assert sorted(f.name for f in files) == [
        "pae.json.gz", "plddt.json", "provenance.json", "structure.pdb"]


# ── /complete: ordering enforced at the endpoint (D-031 §(3)+(c)) ─────────────

def test_complete_before_artifacts_is_rejected(engine, tmp_path):
    _, job_id = _seed(engine)
    queue = StubQueue()
    client = _client(engine, tmp_path, queue)

    r = client.post(f"/jobs/{job_id}/complete", headers=AUTH)

    assert r.status_code == 409           # no pdb_path yet → the forbidden state is unreachable
    assert queue.completed == []          # and the queue was never asked to flip


def test_complete_after_artifacts_delegates(engine, tmp_path):
    _, job_id = _seed(engine)
    queue = StubQueue()
    client = _client(engine, tmp_path, queue)
    client.post(f"/jobs/{job_id}/artifacts", files=_upload_files(), headers=AUTH)

    r = client.post(f"/jobs/{job_id}/complete", headers=AUTH)

    assert r.status_code == 204
    assert queue.completed == [job_id]


# ── /fail: terminal, delegates to the primitive ──────────────────────────────

def test_fail_delegates_to_queue(engine, tmp_path):
    _, job_id = _seed(engine)
    queue = StubQueue()
    client = _client(engine, tmp_path, queue)

    r = client.post(f"/jobs/{job_id}/fail", json={"error": "CUDA OOM"}, headers=AUTH)

    assert r.status_code == 204
    assert queue.failed == [(job_id, "CUDA OOM")]


# ── auth: asserted on EVERY route (D-031 §4) ─────────────────────────────────

@pytest.mark.parametrize("method,path,kw", [
    ("post", "/jobs/claim", {"json": {"worker_id": "w"}}),
    ("post", "/jobs/1/artifacts", {"files": _upload_files()}),
    ("post", "/jobs/1/complete", {}),
    ("post", "/jobs/1/fail", {"json": {"error": "e"}}),
])
def test_every_route_rejects_missing_token(engine, tmp_path, method, path, kw):
    client = _client(engine, tmp_path, StubQueue())
    r = getattr(client, method)(path, **kw)                  # no Authorization header
    assert r.status_code == 401


def test_wrong_token_rejected(engine, tmp_path):
    client = _client(engine, tmp_path, StubQueue())
    r = client.post("/jobs/claim", json={"worker_id": "w"},
                    headers={"Authorization": "Bearer wrong"})
    assert r.status_code == 401
