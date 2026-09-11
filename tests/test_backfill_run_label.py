"""AMENDMENT 2 §3.1's guard — the backfill changes the key it names and NOTHING else.

⚠⚠ THIS IS `A-030`'S TEST. The assumption — *a JSONB column can take an additive key without
changing any consumer* — is registered **ASSUMED and untested** in `docs/assumptions.md`, and this
file is what decides whether it becomes HELD or BROKE. It is the first entry in that register whose
outcome was not known before it was written.

⚠ The backfill is an **express exception** to *no original row is updated*, granted by the owner
with named bounds: the key ``run`` only, value ``1``, ``inference_settings`` only, no other column,
table, or row. **A guard for an exception has to assert the bounds, not just the effect.**
"""
from __future__ import annotations

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from db.models import Base, JobRecord, ProteinAnalysis
from scripts.backfill_run_label import RUN_KEY, plan, with_run_label

# ⚠ Deliberately heterogeneous, and it mirrors what production actually holds: `dtype`/`chunk_size`
# are on 189 of 3,656 rows and ZERO of the census, so a fixture where every row has the same keys
# would not exercise the case the backfill must not disturb.
SEED = [
    (1, {"source": "sliced_ecd", "ecd_start": 1, "ecd_end": 3, "model_id": "m",
         "model_revision": "r"}),
    (2, {"source": "sliced_ecd", "ecd_start": 4, "ecd_end": 9, "model_id": "m",
         "model_revision": "r", "dtype": "int8", "chunk_size": 64}),
    (3, {"source": "whole", "ecd_start": None, "ecd_end": None, "model_id": "m",
         "model_revision": "r", "tile_index": 0, "parent_job_id": 11, "n_tiles": 2}),
]


def _engine():
    eng = create_engine("sqlite://")
    Base.metadata.create_all(eng)
    with Session(eng) as s:
        for jid, settings in SEED:
            s.add(ProteinAnalysis(id=jid, input_type="uniprot", input_value=f"P{jid:05d}",
                                  cohort_tranche=1, pdb_path=f"/data/artifacts/{jid}/s.pdb",
                                  mean_plddt=70.0, meta={"tier": "local"}))
            s.add(JobRecord(id=jid, analysis_id=jid, status="succeeded", tier="local",
                            inference_settings=dict(settings)))
        s.commit()
    return eng


# ── A-017: the fixture must reach the write path ─────────────────────────────────────────────

def test_the_fixture_actually_needs_the_backfill():
    """⚠⚠ A-017 POSITIVE CONTROL. If any seed row already carried ``run``, the assertions below
    would pass against a backfill that did nothing at all."""
    assert all(RUN_KEY not in s for _, s in SEED), "a seed row already carries the label"
    p = plan(SEED)
    assert p["to_write"] == len(SEED), "the plan would skip rows — the guard would prove nothing"
    assert p["already_labelled"] == 0


# ── the bound: the named key, and nothing else ───────────────────────────────────────────────

def test_the_backfill_adds_the_key_and_changes_nothing_else():
    """⚠ The bound the owner granted, asserted key-by-key rather than by spot check."""
    for _jid, settings in SEED:
        out = with_run_label(settings)
        assert out[RUN_KEY] == 1
        assert set(out) == set(settings) | {RUN_KEY}, "a key appeared or vanished"
        for k, v in settings.items():
            assert out[k] == v, f"the backfill altered {k!r}"
        assert settings.get(RUN_KEY) is None, "the input dict was mutated in place"


def test_it_is_idempotent_and_never_clobbers_a_later_generation():
    """⚠⚠ A re-run after a partial must not rewrite a label a later Run already set. A backfill
    that overwrote ``run: 2`` with ``run: 1`` would silently move rows between generations —
    the defect this whole partition exists to prevent."""
    assert with_run_label({"run": 2})["run"] == 2
    assert with_run_label({"run": 1})["run"] == 1
    once = with_run_label({"source": "whole"})
    assert with_run_label(once) == once


def test_a_null_settings_row_becomes_the_label_alone():
    """⚠ There are none in production — 3,656 of 3,656 are populated, measured — so this asserts
    the behaviour rather than inventing a failure for a case that does not occur."""
    assert with_run_label(None) == {RUN_KEY: 1}
    assert with_run_label({}) == {RUN_KEY: 1}


# ── the bound at row scope: no other column, no other table, no other row ────────────────────

def test_no_other_column_table_or_row_is_touched():
    """⚠⚠ THE EXCEPTION'S BOUNDS, ASSERTED AT ROW SCOPE. Asserting the dict transform alone would
    miss a backfill that got the key right and wrote a neighbouring column on the way past."""
    eng = _engine()
    with Session(eng) as s:
        before_jobs = {j.id: (j.status, j.tier, j.analysis_id) for j in s.scalars(select(JobRecord))}
        before_pa = {a.id: (a.pdb_path, a.pae_json_path, a.mean_plddt, a.ranking_run_id,
                            a.cohort_tranche) for a in s.scalars(select(ProteinAnalysis))}

        rows = [(j.id, j.inference_settings) for j in s.scalars(select(JobRecord)).all()]
        by_id = dict(plan(rows)["writes"])
        for job in s.scalars(select(JobRecord)).all():
            if job.id in by_id:
                job.inference_settings = by_id[job.id]
        s.commit()

    with Session(eng) as s:
        after_jobs = {j.id: (j.status, j.tier, j.analysis_id) for j in s.scalars(select(JobRecord))}
        after_pa = {a.id: (a.pdb_path, a.pae_json_path, a.mean_plddt, a.ranking_run_id,
                           a.cohort_tranche) for a in s.scalars(select(ProteinAnalysis))}
        labelled = [j.inference_settings.get(RUN_KEY) for j in s.scalars(select(JobRecord))]

    assert after_jobs == before_jobs, "a jobs column other than inference_settings moved"
    assert after_pa == before_pa, "⚠⚠ a protein_analyses column moved — outside the granted bounds"
    assert len(after_jobs) == len(before_jobs) == len(SEED), "the row count moved"
    assert labelled == [1] * len(SEED), (
        f"{RUN_KEY!r} is not on every row — a hole makes the partition the absence-based one "
        f"this backfill exists to avoid")


def test_the_plan_reports_the_counts_the_ruling_requires():
    """⚠ AMENDMENT 2 §3.1: report the count before and after, and that the label is on ALL rows.
    A hole is the failure mode, so the count is the deliverable, not a log line."""
    p = plan(SEED)
    assert (p["total"], p["already_labelled"], p["to_write"]) == (3, 0, 3)
    after = plan([(jid, with_run_label(s)) for jid, s in SEED])
    assert (after["total"], after["already_labelled"], after["to_write"]) == (3, 3, 0)


def test_the_script_refuses_to_write_without_the_owner_flag():
    """⚠⚠ A production write has no default that writes."""
    from scripts.backfill_run_label import main
    assert main([]) == 2, "the script wrote, or reported, without being told which"
