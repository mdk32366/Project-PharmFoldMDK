"""D-060 — the scorer fit driver (scripts/fit_scorer.py).

Row assembly is pure and fixture-tested: the label (Group B) and the comparator (evidence score)
are kept separate, and the three exclusion mechanisms get their three names. The `--fixture` path
runs the whole pipeline end to end with no real label, and `persist_ranking_run` stamps the
`scorer_version` into a SQLite `ranking_run`. No real label file is read anywhere here.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

import fit_scorer as fs  # noqa: E402
from core.features import FEATURE_NAMES  # noqa: E402

SIX = (1.13, 2.27, 3.41, 4.59, 5.73, 6.87)


def _rec(symbol, f0, disp="ranked", plddt=71.5, features=None):
    feats = features if features is not None else (f0, *SIX[1:])
    return fs.FeatureRecord(symbol=symbol, features=feats, disposition=disp,
                            mean_plddt=plddt, below_plddt_floor=(plddt < 50 if plddt is not None else None))


def test_build_rows_keeps_label_and_comparator_separate():
    """The label is Group B membership; the evidence score is the comparator. A Group B symbol is a
    positive regardless of its evidence score, and a non-Group-B symbol with a high evidence score
    is still a negative (D-060 §3.1)."""
    records = [_rec("GB_HIGH", 1.4), _rec("NOTGB_HIGH", 1.9)]
    rows = fs.build_scorer_rows(records, group_b_symbols={"GB_HIGH"},
                                evidence_by_symbol={"GB_HIGH": 5.0, "NOTGB_HIGH": 5.0})
    by = {r.symbol: r for r in rows}
    assert by["GB_HIGH"].label == 1 and by["GB_HIGH"].evidence_score == 5.0
    assert by["NOTGB_HIGH"].label == 0 and by["NOTGB_HIGH"].evidence_score == 5.0  # high evidence ≠ label


def test_build_rows_names_the_three_exclusion_mechanisms():
    """Below-floor / held-out / not-folded are three mechanisms with three names (D-060 §3.5),
    each out of the ranking set with its reason recorded, never dropped."""
    records = [
        _rec("RANKED", 1.2, disp="ranked", plddt=71.0),
        _rec("LOW", 0.9, disp="ranked", plddt=47.63),                 # below floor
        _rec("WHOLE", 0.4, disp="held_out", plddt=75.04),             # held out
        _rec("FAILED", 0.0, disp="held_out", plddt=None,
             features=(None, None, None, None, None, None)),          # no features → not folded
    ]
    rows = {r.symbol: r for r in fs.build_scorer_rows(records, set(), {})}
    assert rows["RANKED"].in_ranking_set is True and rows["RANKED"].exclusion_reason is None
    assert rows["LOW"].in_ranking_set is False and rows["LOW"].exclusion_reason == "below_floor"
    assert rows["WHOLE"].in_ranking_set is False and rows["WHOLE"].exclusion_reason == "held_out"
    assert rows["FAILED"].in_ranking_set is False and rows["FAILED"].exclusion_reason == "not_folded"


def test_build_rows_never_imputes_a_mean_for_a_failed_target():
    """A feature-less (failed) target is excluded with inert placeholders it is never scored on —
    NOT an imputed mean (D-027/D-060). It must not enter the ranking set."""
    rec = _rec("FAILED", 0.0, plddt=None, features=(None,) * len(FEATURE_NAMES))
    (row,) = fs.build_scorer_rows([rec], set(), {})
    assert row.in_ranking_set is False
    assert row.exclusion_reason == "not_folded"


def test_persist_ranking_run_stamps_scorer_version():
    from sqlalchemy import create_engine, select
    from sqlalchemy.orm import Session

    from core.scorer import run_scorer
    from db.models import Base, RankingRun

    engine = create_engine("sqlite://", future=True)
    Base.metadata.create_all(engine)
    report = run_scorer(fs._fixture_rows())
    rid = fs.persist_ranking_run(engine, report, target_list_version="test-tl")
    with Session(engine) as s:
        run = s.get(RankingRun, rid)
        assert run.scorer_version == report.scorer_version
        assert run.target_list_version == "test-tl"
    # idempotent-ish: a second call updates the same run's version, does not duplicate
    rid2 = fs.persist_ranking_run(engine, report, target_list_version="test-tl")
    assert rid2 == rid
    with Session(engine) as s:
        assert len(s.execute(select(RankingRun)).scalars().all()) == 1


def test_fixture_run_end_to_end_returns_zero(capsys):
    """--fixture runs the whole pipeline on built-in labels — the §6 'able to run end to end against
    fixture labels' criterion, with no DB and no real label file."""
    rc = fs.run(["--fixture"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "scorer_version=" in out
    assert "ranking set" in out
    assert "head-to-head" in out


def test_run_path_does_not_touch_the_db_without_being_asked():
    """--fixture must never build an engine — a guard that the safe path is genuinely DB-free."""
    def exploding_engine():
        raise AssertionError("--fixture must not build a database engine")
    assert fs.run(["--fixture"], engine_factory=exploding_engine) == 0
