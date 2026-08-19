"""The census profile ON THE SURFACE — `/api/census/{id}` carries a block, and it is not a score.

⚠⚠ THE RISK THIS FILE EXISTS FOR is named by the rulings themselves: `D-089` says *a census page
still carries no scorer panel*, and `D-079` amendment 1 adds *"a profile block must not become that
page by another name."* A block that renders a number in 0–1 on a protein page, next to nothing,
IS a scorer panel whatever it is called. These tests pin the differences that make it not one.
"""

from __future__ import annotations

import ast
import pathlib

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.main import create_app
from core.features import FEATURE_NAMES
from core.structural_profile import load_support
from db.models import Base, ProteinAnalysis, ProteinFeatures

REPO = pathlib.Path(__file__).resolve().parent.parent
TOKEN = "test-secret-token"


class _DummyQueue:
    def claim(self, worker_id, tier="local"):  # pragma: no cover
        raise AssertionError("a read route touched the queue")


@pytest.fixture
def engine():
    eng = create_engine("sqlite://", connect_args={"check_same_thread": False},
                        poolclass=StaticPool)
    Base.metadata.create_all(eng)
    return eng


def _client(engine, tmp_path):
    return TestClient(create_app(engine=engine, artifact_root=str(tmp_path), auth_token=TOKEN,
                                 queue=_DummyQueue()), raise_server_exceptions=True)


def _mid():
    return {n: (lo + hi) / 2 for n, (lo, hi) in load_support().items()}


def _seed(engine, *, features=None, outcome="ok", tranche=1, accession="Q00000") -> int:
    with Session(engine) as s:
        a = ProteinAnalysis(input_type="uniprot", input_value=accession, cohort_tranche=tranche,
                            structure_source="esmfold", pdb_path="/data/x.pdb", mean_plddt=60.0,
                            meta={"gene": "GENE1", "sequence": "MK"})
        s.add(a)
        s.flush()
        aid = a.id
        if features is not None or outcome != "ok":
            s.add(ProteinFeatures(analysis_id=aid, extraction_outcome=outcome,
                                  **{n: (features or {}).get(n) for n in FEATURE_NAMES}))
        s.commit()
    return aid


def _block(engine, tmp_path, aid):
    r = _client(engine, tmp_path).get(f"/api/census/{aid}")
    assert r.status_code == 200, r.text
    return r.json()["structural_profile_block"]


# ── it is served, and it is a block rather than a bare number ───────────────

def test_a_census_row_carries_a_profile_block(engine, tmp_path):
    b = _block(engine, tmp_path, _seed(engine, features=_mid()))
    assert b["kind"] == "structural_profile"
    assert b["status"] == "computed"
    assert 0.0 < b["structural_profile"] < 1.0


def test_the_payload_carries_no_score_rank_or_suitability_key(engine, tmp_path):
    """⚠ Ruling 1 — the name is the ruling, on the wire and not only in the module."""
    b = _block(engine, tmp_path, _seed(engine, features=_mid()))
    bad = [k for k in b if any(t in k.lower() for t in ("score", "rank", "suitab"))
           and k != "structural_profile"]
    assert not bad, f"the census payload names the value {bad}"


# ── ruling 4: the frame cannot be dropped by the surface ───────────────────

def test_the_mount_preconditions_ride_INSIDE_the_block(engine, tmp_path):
    """⚠⚠ Not a sibling key a UI may forget. A surface cannot receive the number without the
    frame, because they arrive in the same object."""
    b = _block(engine, tmp_path, _seed(engine, features=_mid()))
    assert len(b["mount_preconditions"]) >= 5
    joined = " ".join(b["mount_preconditions"]).lower()
    for token in ("unlabelled", "not a probability", "f-051", "selection artefact"):
        assert token in joined


def test_the_value_never_travels_without_the_cohort_band(engine, tmp_path):
    """⚠ A number in 0–1 alone invites a probability reading. `F-006`'s span rides with it."""
    b = _block(engine, tmp_path, _seed(engine, features=_mid()))
    assert b["band_context"]["cohort_fitted_min"] == 0.116
    assert b["band_context"]["cohort_fitted_max"] == 0.285
    assert "does not separate" in b["band_context"]["note"]


def test_the_bar_is_stated_and_names_the_two_it_is_not(engine, tmp_path):
    b = _block(engine, tmp_path, _seed(engine, features=_mid()))
    assert "min-max" in b["bar"]
    assert "p05-p95" in b["bar"] and "sd" in b["bar"], (
        "the bar must name the alternatives it is not — otherwise the dial is invisible")


# ── ruling 3 / 6: refusals arrive as categories, never as an empty field ───

def test_out_of_range_arrives_as_a_refusal_with_its_cause(engine, tmp_path):
    feats = _mid()
    feats["ecd_length"] = 99999.0
    b = _block(engine, tmp_path, _seed(engine, features=feats))
    assert b["status"] == "refused"
    assert b["structural_profile"] is None
    assert b["refusal"]["category"] == "refused_out_of_distribution"
    assert "ecd_length" in b["out_of_range_features"]
    assert "outside the cohort" in b["refusal"]["detail"]


def test_the_f048_set_is_refused_from_its_extraction_record(engine, tmp_path):
    """⚠ Ruling 6, and the membership is READ from `extraction_outcome` rather than recomputed —
    a second implementation of the F-048 test would drift from the first in silence."""
    b = _block(engine, tmp_path,
               _seed(engine, features=_mid(), outcome="refused_span_below_floor"))
    assert b["refusal"]["category"] == "refused_span_below_floor"
    assert b["structural_profile"] is None


def test_a_census_row_with_no_feature_row_is_a_refusal_not_a_blank(engine, tmp_path):
    """⚠⚠ The reader fills a blank in with an assumption. An absent extraction is a CATEGORY."""
    b = _block(engine, tmp_path, _seed(engine))          # no ProteinFeatures row at all
    assert b["status"] == "refused"
    assert b["refusal"]["category"] == "refused_features_incomplete"


# ── the wall, at the surface ───────────────────────────────────────────────

def test_the_cohort_route_carries_no_profile_block(engine, tmp_path):
    """⚠⚠ Ruling 5. A cohort id is a 404 on the census route (D-081), and the RANKING payload must
    never grow a profile — that is the merge the wall forbids."""
    aid = _seed(engine, features=_mid(), tranche=0, accession="P00001")
    r = _client(engine, tmp_path).get(f"/api/census/{aid}")
    assert r.status_code == 404, "a cohort id resolved on the census route"
    body = _client(engine, tmp_path).get("/api/ranking").json()
    assert "structural_profile_block" not in body
    assert "structural_profile" not in str(body)


def test_app_reads_cannot_reach_the_profile(engine, tmp_path):
    """⚠ The separation is the reason `app/census_profile_read.py` exists. Walked transitively,
    not by a single-file import check — the defect `F-052` records."""
    def mods(rel):
        tree = ast.parse((REPO / rel).read_text(encoding="utf-8"))
        out = set()
        for n in ast.walk(tree):
            if isinstance(n, ast.Import):
                out |= {a.name for a in n.names}
            elif isinstance(n, ast.ImportFrom) and n.module:
                out.add(n.module)
        return out

    seen, stack, hits = set(), ["app/reads.py"], []
    while stack:
        rel = stack.pop()
        if rel in seen:
            continue
        seen.add(rel)
        for m in mods(rel):
            if "structural_profile" in m:
                hits.append((rel, m))
            cand = REPO / (m.replace(".", "/") + ".py")
            if cand.is_file() and m.split(".")[0] in ("app", "core", "db", "scripts"):
                stack.append(str(cand.relative_to(REPO)).replace("\\", "/"))
    assert not hits, f"app/reads.py reaches the profile via {hits} — ruling 5"
