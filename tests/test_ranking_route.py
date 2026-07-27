"""D-062 — GET /api/ranking serves the latest VALID ranking run, never the invalid one.

The route reads the persisted scorer result (F-004): the pre-registered LOO distribution, the
head-to-head, the Spearman, the 56 per-target scores, and the excluded set. `ranking_results` id=1
(the zero-positive artifact, marked invalid — D-064 dec 3) must NEVER be served; the route filters on
validity and serves the latest valid run. No fit is run — the route reads the persisted row.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from app.main import create_app  # noqa: E402
from db.models import (  # noqa: E402
    Base,
    ProteinAnalysis,
    RankingResult,
    RankingRun,
    TargetScore,
)

TOKEN = "test-token"


class _DummyQueue:
    def claim(self, worker_id):  # pragma: no cover - a read must never touch the queue
        raise AssertionError("a read route touched the queue")


@pytest.fixture
def engine():
    eng = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(eng)
    return eng


def _client(engine, tmp_path) -> TestClient:
    app = create_app(engine=engine, artifact_root=str(tmp_path), auth_token=TOKEN, queue=_DummyQueue())
    return TestClient(app, raise_server_exceptions=True)


def _seed(engine):
    """Two runs: id=1 the invalid zero-positive artifact (must never be served), id=2 the valid
    result. Distinctive fixture numbers that cannot coincide with the live run."""
    with Session(engine) as s:
        # --- run 1: the invalid artifact (D-064) ---
        run1 = RankingRun(target_list_version="v", scorer_version="bad")
        s.add(run1)
        s.flush()
        s.add(RankingResult(
            ranking_run_id=run1.id, n_fit_positives=0, n_ranking_set=7,
            structural_percentiles=[], lambda_per_fold=[], excluded=[],
            loo_status="none", fulldata_status="raised",
            status_detail="invalid - zero-positive label set (D-064)",
        ))
        # a stray score on the invalid run — must never surface
        bad_a = ProteinAnalysis(input_type="uniprot", input_value="ACC-BAD", meta={"gene": "BADGENE"})
        s.add(bad_a)
        s.flush()
        s.add(TargetScore(ranking_run_id=run1.id, analysis_id=bad_a.id, score=0.99, attributions=[], rank=1))

        # --- run 2: the valid result ---
        run2 = RankingRun(target_list_version="v", scorer_version="good-91e6")
        s.add(run2)
        s.flush()
        s.add(RankingResult(
            ranking_run_id=run2.id, n_fit_positives=3, n_ranking_set=7, headto_reference_n=5,
            spearman=0.123, spearman_n=5,
            structural_percentiles=[0.71, 0.62, 0.44],
            lambda_per_fold=[{"symbol": "GENE_HI", "lam": 1.0, "converged": True},
                             {"symbol": "GENE_MID", "lam": 1.0, "converged": True},
                             {"symbol": "GENE_LO", "lam": 1.0, "converged": True}],
            headto_structural_percentiles=[0.71, 0.44],
            headto_evidence_percentiles=[0.75, 0.25],
            excluded=[["FIXLOW", "below_floor"], ["FIXWHOLE", "held_out"]],
            loo_status="complete", fulldata_status="converged",
            status_detail="all pre-registered statistics produced",
        ))
        genes = [("ACC-HI", "GENE_HI", 0.91, 1), ("ACC-MID", "GENE_MID", 0.55, 2),
                 ("ACC-LO", "GENE_LO", 0.33, 3)]
        for acc, gene, score, rank in genes:
            a = ProteinAnalysis(input_type="uniprot", input_value=acc, meta={"gene": gene})
            s.add(a)
            s.flush()
            s.add(TargetScore(ranking_run_id=run2.id, analysis_id=a.id, score=score,
                              attributions=[0.1, -0.2, 0.3, 0.4, -0.5, 0.6], rank=rank))
        s.commit()


def test_ranking_route_is_open_and_serves_the_valid_run(engine, tmp_path):
    _seed(engine)
    r = _client(engine, tmp_path).get("/api/ranking")           # no auth header — /api is open (D-034)
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("application/json")
    body = r.json()
    assert body["result_status"] == "complete"
    assert body["run"]["scorer_version"] == "good-91e6"          # the VALID run, not "bad"
    # 56-analog: the three scored rows, ordered by rank ascending
    assert [row["rank"] for row in body["rows"]] == [1, 2, 3]
    assert [row["gene"] for row in body["rows"]] == ["GENE_HI", "GENE_MID", "GENE_LO"]
    assert body["rows"][0]["score"] == 0.91
    assert len(body["rows"][0]["attributions"]) == 6


def test_invalid_run_is_never_served(engine, tmp_path):
    _seed(engine)
    body = _client(engine, tmp_path).get("/api/ranking").json()
    genes = {row["gene"] for row in body["rows"]}
    assert "BADGENE" not in genes                                 # the invalid run's score never surfaces
    assert body["run"]["scorer_version"] != "bad"


def test_ranking_result_fields_are_projected(engine, tmp_path):
    _seed(engine)
    result = _client(engine, tmp_path).get("/api/ranking").json()["result"]
    assert result["spearman"] == 0.123 and result["spearman_n"] == 5
    assert result["n_fit_positives"] == 3 and result["n_ranking_set"] == 7
    assert result["headto_reference_n"] == 5
    # the distribution is paired to the held-out targets, over converged folds
    assert result["distribution"] == [{"symbol": "GENE_HI", "percentile": 0.71},
                                      {"symbol": "GENE_MID", "percentile": 0.62},
                                      {"symbol": "GENE_LO", "percentile": 0.44}]
    assert result["headto_structural"] == [0.71, 0.44]
    assert result["headto_evidence"] == [0.75, 0.25]
    assert result["excluded"] == [["FIXLOW", "below_floor"], ["FIXWHOLE", "held_out"]]
    assert result["paper_published_count"] == 22                 # source constant, served not typed


def test_invalid_run_excluded_even_when_newer_and_preregistered(engine, tmp_path):
    """The predicate is validity ∧ run_kind, not one replacing the other. After 0006 the backfill
    tags every existing run (incl. the invalid id=1) `preregistered`, so run_kind alone would NOT
    exclude it. A NEWER invalid `preregistered` run must still be filtered out — proving validity is
    still ANDed. Ordering alone cannot catch this (the invalid row here is the newest); only the
    validity clause can, so a regression that dropped it would redden."""
    _seed(engine)                                            # id=2 valid preregistered (good-91e6)
    with Session(engine) as s:
        bad = RankingRun(target_list_version="v", scorer_version="newer-invalid",
                         run_kind="preregistered")           # explicitly preregistered, like the backfill
        s.add(bad)
        s.flush()
        s.add(RankingResult(
            ranking_run_id=bad.id, n_fit_positives=0, structural_percentiles=[],
            lambda_per_fold=[], excluded=[],
            status_detail="invalid - zero-positive label set (D-064)",
        ))
        s.commit()
    body = _client(engine, tmp_path).get("/api/ranking").json()
    assert body["run"]["scorer_version"] == "good-91e6"      # the VALID run, not the newer invalid one
    assert body["run"]["scorer_version"] != "newer-invalid"


def test_sensitivity_run_is_never_served_as_the_result(engine, tmp_path):
    """D-065 dec 4: the route filters on run_kind — a NEWER, valid `sensitivity` ablation run must
    never be served where the pre-registered result is expected."""
    _seed(engine)                                            # id=2 is the valid preregistered run
    with Session(engine) as s:
        sen = RankingRun(target_list_version="v", scorer_version="ablation-no_plddt",
                         run_kind="sensitivity")
        s.add(sen)
        s.flush()
        s.add(RankingResult(
            ranking_run_id=sen.id, n_fit_positives=3, n_ranking_set=7,
            structural_percentiles=[0.9], lambda_per_fold=[{"symbol": "X", "lam": 1.0, "converged": True}],
            excluded=[], loo_status="complete", fulldata_status="converged",
            status_detail="all pre-registered statistics produced",   # valid, but sensitivity
        ))
        s.commit()
    body = _client(engine, tmp_path).get("/api/ranking").json()
    assert body["run"]["scorer_version"] == "good-91e6"      # the preregistered run, NOT the ablation
    assert body["run"]["scorer_version"] != "ablation-no_plddt"


def test_no_valid_run_reports_not_run(engine, tmp_path):
    # only the invalid run exists → result_status not_run, empty rows, no crash
    with Session(engine) as s:
        run = RankingRun(target_list_version="v", scorer_version="bad")
        s.add(run)
        s.flush()
        s.add(RankingResult(ranking_run_id=run.id, n_fit_positives=0,
                            structural_percentiles=[], lambda_per_fold=[], excluded=[],
                            status_detail="invalid - zero-positive label set"))
        s.commit()
    body = _client(engine, tmp_path).get("/api/ranking").json()
    assert body["result_status"] == "not_run"
    assert body["rows"] == []
    assert body["run"] is None
