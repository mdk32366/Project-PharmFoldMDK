"""D-034 read-API tests, written against the ruling BEFORE the code.

Hermetic, the D-005 pattern: in-memory SQLite via SQLAlchemy (`create_all`, NOT the
migration chain) + FastAPI's `TestClient`. These prove the read surface's own logic —
the light/full payload split, the id ordering, the stored-`pdb_path` structure serve,
the plddt array, 404s, the restated auth property, and read-only-ness — without a real
Postgres or Volume.

Seed `meta` mirrors the production shape exactly: the keys `core.enqueue` writes
(`enqueue.py:137-153`) plus the `fold_provenance` the fold adds (`app.artifacts`). Two
dispositions are seeded — a `ranked`/`sliced_ecd` local row and a `held_out`/`whole`
local row — because the landed cohort contains both (D-034, 40 + 2).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.deps import require_token
from app.main import create_app
from db.models import Base, ProteinAnalysis

TOKEN = "test-secret-token"

# The exact light-list field set (D-034 decision 1 / Orders §1) — no more, no less.
LIST_FIELDS = {
    "id", "accession", "label", "gene", "mean_plddt", "disposition", "held_out",
    "tier", "tier_reason", "boundary_method", "fold_length", "full_length",
}
# Heavy fields that MUST NOT appear in the list payload (the payload-weight ruling).
HEAVY_FIELDS = {"sequence", "fold_provenance"}


class _DummyQueue:
    """Reads never touch the queue; create_app still wants one. This asserts that by
    exploding if a read path ever calls it."""

    def claim(self, worker_id):  # pragma: no cover - must never be reached by a read
        raise AssertionError("a read route touched the queue")


def _provenance(mean_plddt: float) -> dict:
    return {
        "model_id": "facebook/esmfold_v1",
        "model_revision": "75a3841ee059df2bf4d56688166c8fb459ddd97a",
        "dtype": "int8", "chunk_size": 64, "source": "sliced_ecd",
        "ecd_start": 20, "ecd_end": 337, "truncated": False, "length_cap": None,
        "original_length": 510, "input_length": 318, "mean_plddt": mean_plddt,
        "ca_atom_count": 318, "folded_at": "2026-07-22T00:02:54+00:00",
    }


def _meta(*, gene: str, label: str, disposition: str, held_out: bool, tier: str,
          tier_reason, boundary_method: str, source: str, fold_length: int,
          full_length: int, sequence: str, mean_plddt: float) -> dict:
    """The full landed-row meta: enqueue keys (enqueue.py:137-153) + fold_provenance."""
    return {
        "gene": gene, "label": label, "disposition": disposition, "held_out": held_out,
        "tier": tier, "tier_reason": tier_reason, "boundary_method": boundary_method,
        "source": source, "uniprot_release": "2025_03",
        "full_length": full_length, "fold_length": fold_length,
        "ecd_start": 20, "ecd_end": 337, "primary_match": False,
        "sequence": sequence, "fold_provenance": _provenance(mean_plddt),
    }


@pytest.fixture
def engine():
    eng = create_engine("sqlite://", connect_args={"check_same_thread": False},
                        poolclass=StaticPool)
    Base.metadata.create_all(eng)
    return eng


def _seed(engine, tmp_path) -> dict:
    """Seed three analyses and write their Volume files to directories that are
    DELIBERATELY not `{root}/{id}/`, so a route that reconstructs a path instead of
    serving the stored `pdb_path` fails. Returns a map of role -> id."""
    ids: dict[str, int] = {}
    with Session(engine) as s:
        # Row 1 — NECTIN4-like: ranked, sliced_ecd, local, confident.
        r1 = ProteinAnalysis(
            input_type="uniprot", input_value="Q96NY8", structure_source="esmfold",
            mean_plddt=77.26,
            meta=_meta(gene="NECTIN4", label="Nectin-4", disposition="ranked",
                       held_out=False, tier="local", tier_reason=None,
                       boundary_method="sliced_ecd", source="sliced_ecd",
                       fold_length=318, full_length=510, sequence="M" + "A" * 317,
                       mean_plddt=77.26),
        )
        # Row 2 — held-out, whole-chain, local (the 2 the batch also folded).
        r2 = ProteinAnalysis(
            input_type="uniprot", input_value="Q9NV96", structure_source="esmfold",
            mean_plddt=65.0,
            meta=_meta(gene="TMEM30A", label="CDC50A", disposition="held_out",
                       held_out=True, tier="local", tier_reason=None,
                       boundary_method="whole", source="whole",
                       fold_length=361, full_length=361, sequence="M" + "G" * 360,
                       mean_plddt=65.0),
        )
        # Row 3 — a row with NO structure (pdb_path stays NULL): 404, not 500.
        r3 = ProteinAnalysis(
            input_type="uniprot", input_value="P00000", structure_source="",
            mean_plddt=None,
            meta=_meta(gene="NONE", label="unfolded", disposition="ranked",
                       held_out=False, tier="local", tier_reason=None,
                       boundary_method="sliced_ecd", source="sliced_ecd",
                       fold_length=100, full_length=200, sequence="M" + "C" * 99,
                       mean_plddt=0.0),
        )
        for r in (r1, r2, r3):
            s.add(r)
        s.flush()
        ids = {"nectin4": r1.id, "held_out": r2.id, "unfolded": r3.id}

        # Write structure.pdb + plddt.json for rows 1 and 2 to NON-canonical dirs.
        for role, row, plddt_len in (("nectin4", r1, 318), ("held_out", r2, 361)):
            d = tmp_path / f"elsewhere_{role}"
            d.mkdir()
            pdb = d / "structure.pdb"
            pdb.write_text(f"HEADER    {role}\nATOM      1  N   MET A   1\nEND\n",
                           encoding="utf-8")
            (d / "plddt.json").write_text(json.dumps([80.0] * plddt_len), encoding="utf-8")
            row.pdb_path = str(pdb)          # stored ABSOLUTE, outside {root}/{id}
        s.commit()
    return ids


def _client(engine, tmp_path) -> TestClient:
    app = create_app(engine=engine, artifact_root=str(tmp_path),
                     auth_token=TOKEN, queue=_DummyQueue())
    return TestClient(app, raise_server_exceptions=True)


# ── list: exact light field set, no heavy fields (D-034 decision 1) ───────────

def test_list_returns_exactly_the_light_fields(engine, tmp_path):
    _seed(engine, tmp_path)
    r = _client(engine, tmp_path).get("/api/analyses")
    assert r.status_code == 200
    rows = r.json()
    assert len(rows) == 3
    for row in rows:
        assert set(row.keys()) == LIST_FIELDS         # exact — no more, no less
        for heavy in HEAVY_FIELDS:
            assert heavy not in row                    # payload-weight ruling, asserted


def test_list_projects_meta_and_columns(engine, tmp_path):
    ids = _seed(engine, tmp_path)
    rows = {r["id"]: r for r in _client(engine, tmp_path).get("/api/analyses").json()}
    nectin4 = rows[ids["nectin4"]]
    assert nectin4["accession"] == "Q96NY8"            # from input_value, not a meta key
    assert nectin4["gene"] == "NECTIN4"
    assert nectin4["mean_plddt"] == 77.26              # from the column
    assert nectin4["disposition"] == "ranked"
    assert nectin4["held_out"] is False
    assert nectin4["boundary_method"] == "sliced_ecd"
    held = rows[ids["held_out"]]
    assert held["held_out"] is True                    # the second disposition renders too
    assert held["boundary_method"] == "whole"
    assert held["tier_reason"] is None                 # None on local rows, present as a key


def test_list_is_ordered_by_id_ascending(engine, tmp_path):
    _seed(engine, tmp_path)
    got = [row["id"] for row in _client(engine, tmp_path).get("/api/analyses").json()]
    assert got == sorted(got)


# ── detail: the full record, incl. sequence + provenance (decision 1) ─────────

def test_detail_includes_sequence_and_full_provenance(engine, tmp_path):
    ids = _seed(engine, tmp_path)
    r = _client(engine, tmp_path).get(f"/api/analyses/{ids['nectin4']}")
    assert r.status_code == 200
    body = r.json()
    assert body["sequence"].startswith("M")           # heavy field present here
    prov = body["fold_provenance"]
    for key in ("model_id", "model_revision", "dtype", "chunk_size", "truncated",
                "folded_at", "mean_plddt"):
        assert key in prov                             # provenance keys intact (auditable DL)


def test_detail_404_on_unknown_id(engine, tmp_path):
    _seed(engine, tmp_path)
    assert _client(engine, tmp_path).get("/api/analyses/9999").status_code == 404


# ── structure: serve the STORED pdb_path, never a reconstructed one (§2a) ─────

def test_structure_serves_the_stored_pdb_path(engine, tmp_path):
    ids = _seed(engine, tmp_path)
    r = _client(engine, tmp_path).get(f"/api/analyses/{ids['nectin4']}/structure")
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("text/plain")
    # Body is the file at the row's stored pdb_path (an `elsewhere_*` dir). A route that
    # rebuilt `{root}/{id}/structure.pdb` would 404 here — that path was never written.
    assert r.text.startswith("HEADER    nectin4")
    assert "ATOM" in r.text


def test_structure_404_on_unknown_id(engine, tmp_path):
    _seed(engine, tmp_path)
    assert _client(engine, tmp_path).get("/api/analyses/9999/structure").status_code == 404


def test_structure_404_not_500_when_pdb_path_null(engine, tmp_path):
    ids = _seed(engine, tmp_path)
    r = _client(engine, tmp_path).get(f"/api/analyses/{ids['unfolded']}/structure")
    assert r.status_code == 404                        # null pdb_path is 404, never a 500


# ── plddt: the per-residue array (decision 3) ─────────────────────────────────

def test_plddt_returns_the_array(engine, tmp_path):
    ids = _seed(engine, tmp_path)
    r = _client(engine, tmp_path).get(f"/api/analyses/{ids['nectin4']}/plddt")
    assert r.status_code == 200
    arr = r.json()
    assert isinstance(arr, list) and len(arr) == 318 and arr[0] == 80.0


def test_plddt_404_on_unknown_id(engine, tmp_path):
    _seed(engine, tmp_path)
    assert _client(engine, tmp_path).get("/api/analyses/9999/plddt").status_code == 404


# ── auth: the RESTATED property (D-034 decision 5 / Orders §2b) ────────────────
# Not a hardcoded list of paths — introspect the app's real route table so a route
# added later in a THIRD namespace breaks the build instead of slipping through.

_FRAMEWORK_PATHS = {"/openapi.json", "/docs", "/docs/oauth2-redirect", "/redoc"}


def _route_is_guarded(route) -> bool:
    return any(dep.call is require_token for dep in route.dependant.dependencies)


def test_auth_property_jobs_guarded_api_open_no_third_category(engine, tmp_path):
    app = create_app(engine=engine, artifact_root=str(tmp_path),
                     auth_token=TOKEN, queue=_DummyQueue())
    checked = {"jobs": 0, "api": 0}
    for route in app.routes:
        path = getattr(route, "path", None)
        if path is None or not hasattr(route, "dependant"):
            continue
        if path in _FRAMEWORK_PATHS:
            continue
        if path.startswith("/jobs"):
            assert _route_is_guarded(route), f"{path} must require the bearer token"
            checked["jobs"] += 1
        elif path.startswith("/api"):
            assert not _route_is_guarded(route), f"{path} must be open"
            checked["api"] += 1
        else:
            pytest.fail(f"route {path} matches neither /jobs nor /api — third category")
    # Both namespaces are actually present, so the assertions above weren't vacuous.
    # Five /jobs routes since D-036 (claim/artifacts/complete/fail/pae); five /api since D-038
    # (analyses, analyses/{id}, .../structure, .../plddt, coverage).
    assert checked["jobs"] >= 5 and checked["api"] >= 5


def test_auth_property_holds_behaviourally(engine, tmp_path):
    client = _client(engine, tmp_path)
    # /api is open — no Authorization header, still 200.
    assert client.get("/api/analyses").status_code == 200
    # /jobs is guarded — no header, 401 (structure and behaviour agree).
    assert client.post("/jobs/claim", json={"worker_id": "w"}).status_code == 401


# ── reads never mutate (D-034 consequences) ───────────────────────────────────

def test_reads_do_not_mutate_state(engine, tmp_path):
    ids = _seed(engine, tmp_path)
    client = _client(engine, tmp_path)

    def _snapshot():
        with Session(engine) as s:
            n = s.scalar(select(func.count()).select_from(ProteinAnalysis))
            row = s.get(ProteinAnalysis, ids["nectin4"])
            return n, row.pdb_path, row.mean_plddt, dict(row.meta)

    before = _snapshot()
    client.get("/api/analyses")
    client.get(f"/api/analyses/{ids['nectin4']}")
    client.get(f"/api/analyses/{ids['nectin4']}/structure")
    client.get(f"/api/analyses/{ids['nectin4']}/plddt")
    assert _snapshot() == before
