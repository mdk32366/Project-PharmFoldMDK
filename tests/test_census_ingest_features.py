"""The census feature ingest, on the `GC` pattern. Written against the bar, not against the code.

The four things that had to be true before an ingest was allowed to exist, each tested here:

  1. It reads the ARTIFACT and refuses if the bytes are not the ones its manifest pins.
  2. It UPSERTS. A second run cannot double the table — and the database enforces that too.
  3. The acceptance bar runs INSIDE the transaction and a failure ROLLS BACK (`GC3`).
  4. Completion is recorded against the source sha256, so a re-run is a no-op (`GC4`).

⚠ `GC3` is the one that matters and it is the easy one to fake: a test that asserts "the bar
raised" proves nothing about persistence. Every rollback test here asserts the DATABASE IS
UNCHANGED afterwards, which is the actual claim.
"""

from __future__ import annotations

import json

import pytest
from sqlalchemy import create_engine, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from db.models import Base, ProteinAnalysis, ProteinFeatures
from scripts import census_ingest_features as CI
from core.clinical_ingest import IngestRefused


@pytest.fixture
def engine():
    eng = create_engine("sqlite://", connect_args={"check_same_thread": False},
                        poolclass=StaticPool)
    Base.metadata.create_all(eng)
    # ingest_markers is migration-only (0010); create it for the SQLite path.
    with eng.begin() as c:
        from sqlalchemy import text
        c.execute(text(
            "CREATE TABLE ingest_markers (id INTEGER PRIMARY KEY, ingest_name TEXT NOT NULL,"
            " source_path TEXT NOT NULL, source_sha256 TEXT NOT NULL, rows_written INTEGER NOT NULL,"
            " code_revision TEXT DEFAULT '', completed_at TEXT DEFAULT CURRENT_TIMESTAMP,"
            " detail TEXT DEFAULT '', UNIQUE (ingest_name, source_path))"))
    return eng


def _analyses(engine, n: int) -> list[int]:
    ids = []
    with Session(engine) as s:
        for i in range(n):
            a = ProteinAnalysis(input_type="uniprot", input_value=f"ACC{i}", cohort_tranche=1,
                                pdb_path=f"/data/artifacts/{i}/structure.pdb", mean_plddt=60.0)
            s.add(a)
            s.flush()
            ids.append(a.id)
        s.commit()
    return ids


def _rows(ids, outcome="ok"):
    out = []
    for k, aid in enumerate(ids):
        feats = {"ecd_length": float(100 + k), "radius_of_gyration": 0.1 + k / 100,
                 "mean_plddt_ecd": 60.0 + k, "membrane_proximal_plddt": 55.0 + k,
                 "sasa_normalized": 70.0 + k, "largest_patch_fraction": 0.5,
                 "membrane_proximal_sasa": 12.0}
        out.append({"analysis_id": aid, "accession": f"ACC{k}", "outcome": outcome,
                    "features": feats if outcome == "ok" else None,
                    "null_reasons": {}, "feature_version": "vtest"})
    return out


def _manifest(rows, sha="0" * 64):
    return {"sha256": sha, "lines": len(rows), "census_rows_expected": len(rows),
            "partial": False}


def _count(engine) -> int:
    with Session(engine) as s:
        return s.execute(select(func.count()).select_from(ProteinFeatures)).scalar_one()


# ── 2. upsert, and the database backs it ─────────────────────────────────────

def test_a_second_ingest_updates_rather_than_doubling_the_table(engine):
    ids = _analyses(engine, 5)
    rows = _rows(ids)
    CI.ingest(engine, rows, _manifest(rows), "sha-A", dry_run=False)
    assert _count(engine) == 5

    # a NEW artifact (different sha), same analyses, changed values
    rows2 = _rows(ids)
    rows2[0]["features"]["ecd_length"] = 999.0
    CI.ingest(engine, rows2, _manifest(rows2), "sha-B", dry_run=False)
    assert _count(engine) == 5, "F-021: the second generation doubled the table"
    with Session(engine) as s:
        f = s.execute(select(ProteinFeatures)
                      .where(ProteinFeatures.analysis_id == ids[0])).scalar_one()
        assert f.ecd_length == 999.0, "the upsert did not update in place"


def test_the_database_itself_refuses_a_second_feature_row(engine):
    """⚠ The constraint is the backstop for the loader being wrong, so it is tested against a
    RAW insert, not through the loader — testing it through the code it protects proves nothing."""
    ids = _analyses(engine, 1)
    with Session(engine) as s:
        s.add(ProteinFeatures(analysis_id=ids[0], ecd_length=1.0))
        s.commit()
    with Session(engine) as s:
        s.add(ProteinFeatures(analysis_id=ids[0], ecd_length=2.0))
        with pytest.raises(IntegrityError):
            s.commit()


# ── 3. GC3: the bar rolls back, and the database is UNCHANGED ────────────────

def test_a_failing_bar_rolls_back_and_writes_nothing(engine, monkeypatch):
    ids = _analyses(engine, 4)
    rows = _rows(ids)
    # Corrupt the bar's expectation: the digest it compares against is computed from a
    # DIFFERENT row set, so the read-back cannot match. (`GC3`: corrupt one count, watch it abort.)
    real = CI.six_digest
    monkeypatch.setattr(CI, "six_digest",
                        lambda rs: "deadbeef" if rs is rows else real(rs))
    with pytest.raises(CI.IngestBarFailed) as e:
        CI.ingest(engine, rows, _manifest(rows), "sha-A", dry_run=False)
    assert "ROLLED BACK" in str(e.value)
    assert _count(engine) == 0, "⚠⚠ the bar raised but rows persisted — the rollback is decorative"


def test_a_failing_bar_leaves_no_marker(engine, monkeypatch):
    ids = _analyses(engine, 3)
    rows = _rows(ids)
    real = CI.six_digest
    monkeypatch.setattr(CI, "six_digest",
                        lambda rs: "deadbeef" if rs is rows else real(rs))
    with pytest.raises(CI.IngestBarFailed):
        CI.ingest(engine, rows, _manifest(rows), "sha-A", dry_run=False)
    with Session(engine) as s:
        assert CI._read_marker(s) is None, "a failed ingest recorded itself as completed"


def test_dry_run_runs_the_whole_bar_and_still_writes_nothing(engine):
    ids = _analyses(engine, 4)
    rows = _rows(ids)
    rep = CI.ingest(engine, rows, _manifest(rows), "sha-A", dry_run=True)
    assert rep["outcome"] == "dry_run_rolled_back"
    assert rep["readback_digest"] == rep["expected_digest"], "the bar did not actually run"
    assert _count(engine) == 0


# ── 4. GC4: idempotency keyed to the SOURCE hash ─────────────────────────────

def test_the_same_sha_is_a_noop_rerun(engine):
    ids = _analyses(engine, 3)
    rows = _rows(ids)
    CI.ingest(engine, rows, _manifest(rows), "sha-A", dry_run=False)
    rep = CI.ingest(engine, rows, _manifest(rows), "sha-A", dry_run=False)
    assert rep["outcome"] == "noop_rerun"
    assert _count(engine) == 3


def test_a_different_sha_is_a_new_ingest_and_says_so(engine):
    ids = _analyses(engine, 3)
    rows = _rows(ids)
    CI.ingest(engine, rows, _manifest(rows), "sha-A", dry_run=False)
    rep = CI.ingest(engine, rows, _manifest(rows), "sha-B", dry_run=False)
    assert rep["outcome"] == "committed"
    assert "NEW ingest" in rep["outcome_note"], "a different source was silently treated as a re-run"


# ── the refusals: each an absence with its own message ───────────────────────

def test_a_partial_artifact_is_refused(engine, tmp_path, monkeypatch):
    rows = _rows(_analyses(engine, 2))
    man = _manifest(rows)
    man["partial"] = True
    art = tmp_path / "a.jsonl"
    art.write_text("\n".join(json.dumps(r) for r in rows), encoding="utf-8")
    manp = tmp_path / "a.manifest.json"
    import hashlib
    man["sha256"] = hashlib.sha256(art.read_bytes()).hexdigest()
    manp.write_text(json.dumps(man), encoding="utf-8")
    monkeypatch.setattr(CI, "ART", art)
    monkeypatch.setattr(CI, "MAN", manp)
    with pytest.raises(IngestRefused, match="PARTIAL"):
        CI.load_artifact()


def test_a_hash_mismatch_is_refused_and_names_both_hashes(engine, tmp_path, monkeypatch):
    rows = _rows(_analyses(engine, 2))
    art = tmp_path / "a.jsonl"
    art.write_text("\n".join(json.dumps(r) for r in rows), encoding="utf-8")
    manp = tmp_path / "a.manifest.json"
    manp.write_text(json.dumps(_manifest(rows, sha="f" * 64)), encoding="utf-8")
    monkeypatch.setattr(CI, "ART", art)
    monkeypatch.setattr(CI, "MAN", manp)
    with pytest.raises(IngestRefused, match="does not match its pinned sha256"):
        CI.load_artifact()


def test_rows_pointing_at_absent_analyses_are_refused_by_name(engine):
    rows = _rows([4242, 4243])
    with pytest.raises(IngestRefused, match="do not exist here"):
        CI.ingest(engine, rows, _manifest(rows), "sha-A", dry_run=False)
    assert _count(engine) == 0


# ── the refusal category survives the round trip ─────────────────────────────

def test_a_refused_row_persists_as_a_category_not_as_a_blank(engine):
    """`D-079` amendment 1 ruling 6: the F-048 set carries `refused_span_below_floor` as a
    CATEGORY. Before `extraction_outcome` existed, a refused row and a failed row were both
    just nulls — indistinguishable, which is the thing the ruling forbids."""
    ids = _analyses(engine, 2)
    rows = _rows(ids[:1]) + _rows(ids[1:], outcome="refused_span_below_floor")
    CI.ingest(engine, rows, _manifest(rows), "sha-A", dry_run=False)
    with Session(engine) as s:
        got = {f.analysis_id: f.extraction_outcome for f in
               s.execute(select(ProteinFeatures)).scalars().all()}
    assert got[ids[1]] == "refused_span_below_floor"
    assert got[ids[0]] == "ok"


def test_an_unknown_outcome_token_is_refused_not_stored(engine, tmp_path, monkeypatch):
    rows = _rows(_analyses(engine, 1))
    rows[0]["outcome"] = "probably_fine"
    art = tmp_path / "a.jsonl"
    art.write_text("\n".join(json.dumps(r) for r in rows), encoding="utf-8")
    import hashlib
    manp = tmp_path / "a.manifest.json"
    manp.write_text(json.dumps(_manifest(rows, sha=hashlib.sha256(art.read_bytes()).hexdigest())),
                    encoding="utf-8")
    monkeypatch.setattr(CI, "ART", art)
    monkeypatch.setattr(CI, "MAN", manp)
    with pytest.raises(IngestRefused, match="unknown outcome"):
        CI.load_artifact()


def test_census_rows_are_bound_to_no_ranking_run(engine):
    """⚠ A null here is a CATEGORY: belongs to no run. Stamping the newest run — which is what
    the old latest-run default did — would assert a relationship that does not exist."""
    ids = _analyses(engine, 3)
    rows = _rows(ids)
    CI.ingest(engine, rows, _manifest(rows), "sha-A", dry_run=False)
    with Session(engine) as s:
        runs = {f.ranking_run_id for f in s.execute(select(ProteinFeatures)).scalars().all()}
    assert runs == {None}
