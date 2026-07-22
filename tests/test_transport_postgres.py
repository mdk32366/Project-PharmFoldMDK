"""D-031 seam-1 for the route handlers, on REAL Postgres (the half SQLite can't run).

D-026 closed the commit/rollback seam for the ENQUEUE entry point. The route handlers
are a DIFFERENT entry point and inherit the obligation (D-031): a write through the
real `/artifacts` handler must be proven to actually commit — by re-reading on a FRESH
connection, the env.py-bug class (a green write that silently rolled back). Not a mock.

Auto-skips without a postgresql DATABASE_URL (the `pg_engine` fixture), so this file is
inert in the normal `test` job and runs only in the `postgres` job, which applies the
migration chain with `alembic upgrade head` before pytest.
"""

from __future__ import annotations

import gzip
import json

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.main import create_app
from core.queue import PostgresJobQueue

pytestmark = pytest.mark.postgres

TOKEN = "pg-token"
AUTH = {"Authorization": f"Bearer {TOKEN}"}


def _seed(engine) -> tuple[int, int]:
    """Insert an analysis (folded sequence in metadata) + a pending job on real PG.
    Returns (analysis_id, job_id)."""
    with engine.begin() as c:
        analysis_id = c.execute(text(
            "INSERT INTO protein_analyses (input_type, input_value, metadata) "
            "VALUES ('uniprot', 'P0', CAST(:m AS jsonb)) RETURNING id"),
            {"m": json.dumps({"gene": "G", "sequence": "MKTMKT"})},
        ).scalar_one()
        job_id = c.execute(text(
            "INSERT INTO jobs (analysis_id, status, attempts, inference_settings) "
            "VALUES (:a, 'pending', 0, '{}') RETURNING id"),
            {"a": analysis_id},
        ).scalar_one()
    return analysis_id, job_id


def _provenance() -> dict:
    return {
        "model_id": "facebook/esmfold_v1", "model_revision": "rev", "dtype": "int8",
        "chunk_size": 64, "input_length": 6, "source": "sliced_ecd", "truncated": False,
        "original_length": 6, "mean_plddt": 84.0, "ca_atom_count": 6,
        "folded_at": "2026-07-22T00:00:00+00:00",
    }


def test_artifacts_handler_commits_on_real_postgres(pg_engine):
    analysis_id, job_id = _seed(pg_engine)
    import tempfile
    with tempfile.TemporaryDirectory() as root:
        app = create_app(engine=pg_engine, artifact_root=root, auth_token=TOKEN,
                         queue=PostgresJobQueue(pg_engine))
        client = TestClient(app)
        files = {
            "pdb": ("structure.pdb", "ATOM\n", "text/plain"),
            "plddt": ("plddt.json", json.dumps([84.0] * 6), "application/json"),
            "provenance": ("provenance.json", json.dumps(_provenance()), "application/json"),
            "pae": ("pae.json.gz", gzip.compress(json.dumps([[0.1]]).encode()),
                    "application/gzip"),
        }
        r = client.post(f"/jobs/{job_id}/artifacts", files=files, headers=AUTH)
        assert r.status_code == 204

    # FRESH connection — the write must survive outside the request's transaction, or
    # the env.py class of bug (silent rollback under a green response) would hide here.
    with pg_engine.connect() as c:
        row = c.execute(text(
            "SELECT mean_plddt, pdb_path, pae_json_path, structure_source, metadata "
            "FROM protein_analyses WHERE id = :i"), {"i": analysis_id}).mappings().one()
    assert float(row["mean_plddt"]) == 84.0
    assert row["pdb_path"] and row["pae_json_path"]
    assert row["structure_source"] == "esmfold"
    meta = row["metadata"] if isinstance(row["metadata"], dict) else json.loads(row["metadata"])
    assert meta["fold_provenance"]["ca_atom_count"] == 6
    assert meta["sequence"] == "MKTMKT"          # pre-fold meta preserved through the merge


def test_complete_ordering_enforced_on_real_postgres(pg_engine):
    """Endpoint-enforced ordering holds on real PG, not just SQLite: complete before
    artifacts is 409 and does not flip status."""
    _, job_id = _seed(pg_engine)
    import tempfile
    with tempfile.TemporaryDirectory() as root:
        app = create_app(engine=pg_engine, artifact_root=root, auth_token=TOKEN,
                         queue=PostgresJobQueue(pg_engine))
        client = TestClient(app)
        r = client.post(f"/jobs/{job_id}/complete", headers=AUTH)
        assert r.status_code == 409

    with pg_engine.connect() as c:
        status = c.execute(text("SELECT status FROM jobs WHERE id = :i"),
                           {"i": job_id}).scalar_one()
    assert status == "pending"                   # never flipped to complete
