"""`F-049`'s third instance on the surface: `ranked` names two different populations.

`/api/coverage` reports `coverage.ranked = 67`; `/api/ranking` reports `n_ranking_set = 56`.
Both are correct. **Neither payload says which population it is counting**, so a consumer
reading the JSON — which is not the UI and cannot see `/scorer`'s reconciliation — has two
numbers, one word, and an eleven-row gap with no way to close it.

⚠ `D-016`: every claim names how it is known. These two did not.

⚠⚠ WHAT THIS DOES **NOT** DO. It does not close `F-049`, whose closure condition is about
`scorer_version` — *"two runs cannot be presented as comparable on the strength of a matching
version string"*. This is the third INSTANCE of the family, not the finding itself.

⚠ And the UI is NOT the defect: `D-066` decision 2 already renders
*"67 ranked · 56 rankable after the pLDDT-50 floor"* on `/scorer`, verified live in the
deployed bundle. The residue is the PAYLOAD, for a consumer that never renders the page.

Written before the code. Each assertion fails on the payload as it stands today.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.main import create_app
from db.models import Base, ProteinAnalysis, RankingResult, RankingRun, TargetScore

TOKEN = "test-secret-token"


class _DummyQueue:
    def claim(self, worker_id, tier="local"):  # pragma: no cover - reads never touch the queue
        raise AssertionError("a read route touched the queue")


@pytest.fixture
def engine():
    eng = create_engine("sqlite://", connect_args={"check_same_thread": False},
                        poolclass=StaticPool)
    Base.metadata.create_all(eng)
    return eng


def _client(engine, tmp_path) -> TestClient:
    app = create_app(engine=engine, artifact_root=str(tmp_path), auth_token=TOKEN,
                     queue=_DummyQueue())
    return TestClient(app, raise_server_exceptions=True)


def _seed_run(engine) -> None:
    with Session(engine) as s:
        run = RankingRun(target_list_version="Kathad-2024-PLOSONE-S3-82",
                         scorer_version="good-91e6", run_kind="preregistered")
        s.add(run)
        s.flush()
        s.add(RankingResult(
            ranking_run_id=run.id, loo_status="complete", fulldata_status="converged",
            status_detail="all pre-registered statistics produced",
            spearman=0.123, spearman_n=5, n_ranking_set=7, n_fit_positives=3,
            headto_reference_n=5, structural_percentiles=[0.71, 0.62, 0.44],
            lambda_per_fold=[], excluded=[]))
        a = ProteinAnalysis(input_type="uniprot", input_value="ACC-1", meta={"gene": "G1"})
        s.add(a)
        s.flush()
        s.add(TargetScore(ranking_run_id=run.id, analysis_id=a.id, score=0.5,
                          attributions=[0.1, -0.2, 0.3, 0.4, -0.5, 0.6], rank=1))
        s.commit()


def _coverage_key(engine, tmp_path) -> dict:
    body = _client(engine, tmp_path).get("/api/coverage").json()
    assert "population_key" in body, (
        "/api/coverage does not say which population `ranked` counts — F-049's third instance")
    return body["population_key"]


def _ranking_key(engine, tmp_path) -> dict:
    _seed_run(engine)
    body = _client(engine, tmp_path).get("/api/ranking").json()
    assert "population_key" in body, (
        "/api/ranking does not say which population `n_ranking_set` counts")
    return body["population_key"]


# ── each payload names its own population ────────────────────────────────────

def test_coverage_says_ranked_is_a_manifest_disposition(engine, tmp_path):
    text = _coverage_key(engine, tmp_path)["ranked"]["text"].lower()
    assert "disposition" in text, "`ranked` must be named as the manifest DISPOSITION"
    assert "manifest" in text


def test_ranking_says_n_ranking_set_applies_the_plddt_floor(engine, tmp_path):
    text = _ranking_key(engine, tmp_path)["n_ranking_set"]["text"].lower()
    assert "plddt" in text, "`n_ranking_set` must name the pLDDT floor that produces it"
    assert "floor" in text


# ── ⚠⚠ and each DISCLAIMS the other, which is the actual defect ──────────────
# A description that only says what a number IS still lets a reader assume the other number
# means the same thing. The gap closes only when each payload points AT the other.

def test_coverage_disclaims_ranking_set_membership_and_points_at_it(engine, tmp_path):
    text = _coverage_key(engine, tmp_path)["ranked"]["text"]
    assert "n_ranking_set" in text, (
        "`coverage.ranked` must point at the number it is NOT, by name")
    assert "/api/ranking" in text, "and at the route that carries it"


def test_ranking_disclaims_the_disposition_and_points_at_it(engine, tmp_path):
    text = _ranking_key(engine, tmp_path)["n_ranking_set"]["text"]
    assert "coverage.ranked" in text, (
        "`n_ranking_set` must point at the number it is NOT, by name")
    assert "/api/coverage" in text


# ── the copy-paste guard: one word, two meanings, must stay two descriptions ──

def test_the_two_descriptions_are_not_the_same_text(engine, tmp_path):
    cov = _coverage_key(engine, tmp_path)["ranked"]["text"]
    rank = _ranking_key(engine, tmp_path)["n_ranking_set"]["text"]
    assert cov.strip() != rank.strip(), (
        "the two populations were given ONE description — the defect, re-created in the fix")


def test_each_description_claims_its_own_kind_and_refuses_the_other_s(engine, tmp_path):
    """⚠⚠ THIS TEST EXISTS BECAUSE THE REVERT PROOF DEFEATED THE ONE ABOVE.

    Flipping `n_ranking_set`'s description to a MANIFEST-DISPOSITION description left every
    required token in place — `plddt`, `floor`, `coverage.ranked`, `/api/coverage` — and all six
    tests stayed green. A token scan pins that words are PRESENT, never that the sentence means
    what it should, and keyword-stuffing walks straight through it. (`EE-0`'s lesson, and
    `F-045`'s: a proof that cannot fail is not a proof.)

    ⚠ And the SECOND attempt at this test also failed, on the honest code, for a reason worth
    keeping: a prose scan for "MANIFEST DISPOSITION" inside `n_ranking_set` matched the
    legitimate DISCLAIMER — *"it is NOT `coverage.ranked`, which is the manifest disposition"*.
    Prose cannot distinguish "I am one" from "that other one is one".

    ⚠⚠ So the KIND became structured data instead of a sentence to be scanned. `kind` is the
    claim; `text` is for the human. A test against `kind` cannot be satisfied by wording.
    """
    cov = _coverage_key(engine, tmp_path)["ranked"]
    rank = _ranking_key(engine, tmp_path)["n_ranking_set"]

    assert cov["kind"] == "MANIFEST_DISPOSITION", (
        "`coverage.ranked` is computed from the committed CSVs before any fold exists")
    assert rank["kind"] == "FIT_TIME_MEASUREMENT", (
        "`n_ranking_set` is measured after folding, with the pLDDT floor applied")
    assert cov["kind"] != rank["kind"], (
        "the two populations were given ONE kind — the collision re-created inside its own fix")


def test_every_partition_cell_carries_a_key_not_just_ranked(engine, tmp_path):
    """`held_out` and `excluded` are the same shape of claim. A rule applied to one cell and
    not the others is not a rule."""
    key = _coverage_key(engine, tmp_path)
    for cell in ("ranked", "held_out", "excluded", "denominator"):
        assert cell in key and key[cell]["text"].strip(), f"`{cell}` has no stated population"
