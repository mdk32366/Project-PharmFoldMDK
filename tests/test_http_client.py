"""D-031 worker HTTP client tests, written before the code.

Two layers:
  1. UNIT — the client maps the wire to the loop's contract: parses the inline
     FoldSpec, turns 204 into None, gzips PAE into the multipart body, sends the
     bearer token on every call, and raises `TransportError` on any non-2xx or
     connection failure (the loop's already-proven retry signal, D-030 §4).
  2. END-TO-END — the REAL `run_worker` loop drives the REAL `HttpQueueClient`
     against the REAL app through ASGI (TestClient as the httpx transport). This is
     the concrete form of the project rule "the loop's tests do not change": if the
     client implemented the protocol wrongly, this fails without touching
     test_orchestrator.py.
"""

from __future__ import annotations

import gzip
import json

import httpx
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.main import create_app
from core.queue import Job
from db.models import Base, JobRecord, ProteinAnalysis, RankingRun
from worker.http_client import HttpQueueClient
from worker.orchestrator import FoldSpec, TransportError, run_worker
from worker.runner import FoldProvenance, FoldResult

TOKEN = "tok"
SPEC_JSON = {
    "job_id": 7, "sequence": "MKT", "model_revision": "rev", "dtype": "int8",
    "chunk_size": 64, "source": "sliced_ecd", "ecd_start": 1, "ecd_end": 3,
}


def _client(handler) -> HttpQueueClient:
    """An HttpQueueClient whose transport is a MockTransport running `handler`."""
    transport = httpx.MockTransport(handler)
    http = httpx.Client(transport=transport, base_url="http://fly.test")
    return HttpQueueClient("http://fly.test", TOKEN, client=http)


# ── unit: the client sets an explicit timeout (D-035 §3a) ─────────────────────

def test_client_sets_an_explicit_timeout_not_the_5s_default():
    """With no injected client the client builds its own — and it must NOT inherit httpx's 5 s
    default. A 5 s read/write times out a slow upload → `_post` raises `TransportError` → the loop
    retries → exhausts `submit_attempts` → the job reaps and **re-folds on a PAID card** (D-030's
    named cost). Assert the configured values, not merely that a timeout exists — a test that
    passed against the 5 s default would prove nothing."""
    qc = HttpQueueClient("http://fly.test", TOKEN)          # no client injected → builds its own
    t = qc._client._timeout
    assert (t.connect, t.read, t.write, t.pool) == (10.0, 300.0, 300.0, 10.0)


# ── unit: claim ──────────────────────────────────────────────────────────────

def test_claim_parses_inline_fold_spec():
    def handler(req):
        assert req.headers["Authorization"] == f"Bearer {TOKEN}"      # token on the call
        assert json.loads(req.content) == {"worker_id": "w1"}
        return httpx.Response(200, json=SPEC_JSON)

    spec = _client(handler).claim("w1")
    assert spec == FoldSpec(**SPEC_JSON)                              # exact 8-field round-trip


def test_claim_204_is_none():
    spec = _client(lambda req: httpx.Response(204)).claim("w1")
    assert spec is None


def test_claim_non_2xx_is_transport_error():
    with pytest.raises(TransportError):
        _client(lambda req: httpx.Response(500)).claim("w1")


def test_connection_failure_is_transport_error():
    def handler(req):
        raise httpx.ConnectError("refused")
    with pytest.raises(TransportError):
        _client(handler).claim("w1")


# ── unit: upload builds the multipart body, gzipping PAE ──────────────────────

def _result(pae=None):
    prov = FoldProvenance(
        model_id="facebook/esmfold_v1", model_revision="rev", dtype="int8",
        chunk_size=64, input_length=3, source="sliced_ecd", mean_plddt=88.0,
        ca_atom_count=3, folded_at="2026-07-22T00:00:00+00:00",
    )
    return FoldResult(pdb="ATOM\n", plddt=[88.0, 88.0, 88.0], pae=pae, provenance=prov)


def test_upload_sends_pdb_plddt_provenance_and_never_pae():
    """D-035 part 2: PAE leaves the claim→complete cycle. Even when the FoldResult carries a
    PAE, `upload` must NOT put it on the wire — it is persisted locally on the pod and
    transferred out-of-band via the D-036 route. The runner still *produces* it (that is a
    separate test); the client just stops sending it."""
    seen = {}

    def handler(req):
        assert req.headers["Authorization"] == f"Bearer {TOKEN}"
        body = req.content
        seen["has_pdb"] = b"structure.pdb" in body
        seen["has_plddt"] = b"plddt.json" in body
        seen["has_prov"] = b"provenance.json" in body
        seen["has_pae"] = b"pae.json.gz" in body
        return httpx.Response(204)

    _client(handler).upload(7, _result(pae=[[1.0, 2.0]]))          # PAE present in the result…
    assert seen["has_pdb"] and seen["has_plddt"] and seen["has_prov"]
    assert not seen["has_pae"]                                     # …but never on the wire


def test_upload_omits_pae_when_absent():
    def handler(req):
        assert b"pae.json.gz" not in req.content                   # no PAE part at all
        return httpx.Response(204)
    _client(handler).upload(7, _result(pae=None))


def test_upload_non_2xx_is_transport_error():
    with pytest.raises(TransportError):
        _client(lambda req: httpx.Response(500)).upload(7, _result())


# ── unit: complete / fail ─────────────────────────────────────────────────────

def test_complete_posts_to_the_job(monkeypatch):
    hit = {}

    def handler(req):
        hit["url"] = str(req.url)
        return httpx.Response(204)
    _client(handler).complete(7)
    assert hit["url"].endswith("/jobs/7/complete")


def test_fail_posts_error_body():
    hit = {}

    def handler(req):
        hit["json"] = json.loads(req.content)
        hit["url"] = str(req.url)
        return httpx.Response(204)
    _client(handler).fail(7, "CUDA OOM")
    assert hit["url"].endswith("/jobs/7/fail") and hit["json"] == {"error": "CUDA OOM"}


def test_complete_non_2xx_is_transport_error():
    with pytest.raises(TransportError):
        _client(lambda req: httpx.Response(409)).complete(7)


# ── end-to-end: the real loop over the real client over the real app ──────────

class _OneJobQueue:
    """claim() yields one Job then None (SKIP LOCKED can't run on SQLite, so the
    claim primitive is stubbed — its atomicity is proven in the postgres job). The
    rest is real: the route reads the sequence, persists artifacts, and flips status."""

    def __init__(self, job):
        self._job = job
        self.completed = []

    def claim(self, worker_id):
        job, self._job = self._job, None
        return job

    def complete(self, job_id):
        self.completed.append(job_id)

    def fail(self, job_id, error):
        raise AssertionError("should not fail in the happy path")


def test_loop_client_app_end_to_end(tmp_path):
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False},
                           poolclass=StaticPool)
    Base.metadata.create_all(engine)
    with Session(engine) as s:
        run = RankingRun(target_list_version="t", scorer_version="")
        s.add(run); s.flush()
        a = ProteinAnalysis(input_type="uniprot", input_value="P0", ranking_run_id=run.id,
                            meta={"sequence": "MKTMKT"})
        s.add(a); s.flush()
        job_row = JobRecord(analysis_id=a.id, status="pending", inference_settings={
            "model_revision": "rev", "dtype": "int8", "chunk_size": 64,
            "source": "sliced_ecd", "ecd_start": 1, "ecd_end": 6})
        s.add(job_row); s.commit()
        analysis_id, job_id = a.id, job_row.id

    queue = _OneJobQueue(Job(id=job_id, analysis_id=analysis_id, status="claimed",
                             inference_settings={
                                 "model_revision": "rev", "dtype": "int8", "chunk_size": 64,
                                 "source": "sliced_ecd", "ecd_start": 1, "ecd_end": 6}))
    app = create_app(engine=engine, artifact_root=str(tmp_path), auth_token=TOKEN, queue=queue)
    http = TestClient(app)
    client = HttpQueueClient("http://testserver", TOKEN, client=http)

    folded = {}

    def fake_fold(spec: FoldSpec) -> FoldResult:
        folded["spec"] = spec                                       # the loop handed us the inline spec
        prov = FoldProvenance(
            model_id="facebook/esmfold_v1", model_revision=spec.model_revision,
            dtype=spec.dtype, chunk_size=spec.chunk_size, input_length=len(spec.sequence),
            source=spec.source, mean_plddt=91.5, ca_atom_count=6,
            folded_at="2026-07-22T00:00:00+00:00")
        return FoldResult(pdb="ATOM\n", plddt=[91.5] * 6, pae=[[0.1]], provenance=prov)

    stop = {"v": False}
    orig_claim = queue.claim

    def claim_then_stop(worker_id):
        job = orig_claim(worker_id)
        if job is None:
            stop["v"] = True
        return job
    queue.claim = claim_then_stop

    run_worker(client, fake_fold, "w1", poll_interval=0, sleep=lambda _: None,
               should_stop=lambda: stop["v"])

    # the loop folded the sequence the manifest stored, uploaded, and completed — all
    # through the real HTTP surface, with test_orchestrator.py untouched.
    assert folded["spec"].sequence == "MKTMKT"
    assert queue.completed == [job_id]
    with Session(engine) as s:
        a = s.get(ProteinAnalysis, analysis_id)
        assert a.mean_plddt == 91.5 and a.pdb_path is not None
        assert a.meta["fold_provenance"]["ca_atom_count"] == 6
