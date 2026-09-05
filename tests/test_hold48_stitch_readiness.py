"""D-116 — stitch_readiness gate. Tests that must be able to go red without the gate.

BUILD GO 2026-09-04 (Trinity / Architect). Wave1 false-ready class: parent 2817
``n_tiles_rows=1`` on a long span; wave1 FAIL 17. Cite D-111 UncoveredResidue
refuse. No GPU, no Fly, no ``hold48_stitch.py`` change.
"""
from __future__ import annotations

from pathlib import Path

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from core.hold48 import (
    IGF2R_ACCESSION,
    IGF2R_SPAN_AA,
    MUCIN_ACCESSIONS,
    emit_tile_jobs,
    n_tiles,
    stitch_readiness,
)
from db.models import Base, JobRecord, ProteinAnalysis

REPO = Path(__file__).resolve().parent.parent
REV = "75a3841ee059df2bf4d56688166c8fb459ddd97a"


def _settings(**kw):
    s = {
        "model_revision": REV,
        "dtype": "fp16",
        "chunk_size": 64,
        "source": "sliced_ecd",
        "ecd_start": 41,
        "ecd_end": 2304,
    }
    s.update(kw)
    return s


def _engine():
    eng = create_engine("sqlite://")
    Base.metadata.create_all(eng)
    return eng


def _seed_parent(eng, *, accession: str, sequence: str):
    meta = {
        "sequence": sequence,
        "tier": "rental",
        "source": "sliced_ecd",
        "span_aa": len(sequence),
        "fold_length": len(sequence),
        "ecd_start": 41,
        "ecd_end": 41 + len(sequence) - 1,
    }
    with Session(eng) as s:
        a = ProteinAnalysis(
            input_type="uniprot",
            input_value=accession,
            cohort_tranche=5,
            meta=meta,
        )
        s.add(a)
        s.flush()
        job = JobRecord(
            analysis_id=a.id,
            status="pending",
            tier=None,
            inference_settings=_settings(),
        )
        s.add(job)
        s.commit()
        return a.id, job.id


def _rental_children(session, parent_id):
    return [
        j
        for j in session.execute(select(JobRecord)).scalars().all()
        if (j.inference_settings or {}).get("parent_job_id") == parent_id
    ]


def _mark_complete(session, job, *, pdb: str | None = "/tmp/tile.pdb", pae: str | None = "/tmp/tile_pae.json"):
    job.status = "complete"
    analysis = session.get(ProteinAnalysis, job.analysis_id)
    analysis.pdb_path = pdb
    analysis.pae_json_path = pae


def test_long_parent_with_one_complete_tile_is_not_ready():
    """T-1078 — wave1 / parent-2817 class: n_tiles_rows=1 on a long span.

    Wave A emit writes only the short last-tile. Loose SQL "any pdb+pae" would
    call that ready. The gate must refuse and list the rest as missing.
    """
    assert n_tiles(IGF2R_SPAN_AA) == 2
    eng = _engine()
    analysis_id, parent_id = _seed_parent(
        eng, accession=IGF2R_ACCESSION, sequence="A" * IGF2R_SPAN_AA,
    )
    with Session(eng) as s:
        parent_job = s.get(JobRecord, parent_id)
        parent_a = s.get(ProteinAnalysis, analysis_id)
        specs = emit_tile_jobs(s, parent_job, parent_a, length_max=800)
        s.flush()
        assert len(specs) == 1
        children = _rental_children(s, parent_id)
        assert len(children) == 1
        _mark_complete(s, children[0])
        s.flush()

        ready = stitch_readiness(s, s.get(JobRecord, parent_id), s.get(ProteinAnalysis, analysis_id))
        assert ready.ready is False
        assert ready.expected_n == 2
        assert ready.present_complete_n == 1
        assert len(ready.missing) == 1
        # The rest: the long first tile Wave A never emitted.
        assert ready.missing[0].tile_index == 0
        assert ready.missing[0].length == 1656
        assert ready.uncovered_n == 0  # the *plan* covers; the rows do not


def test_full_cover_complete_with_pae_is_ready():
    """T-1079 — every expected tile complete + PDB + PAE."""
    eng = _engine()
    analysis_id, parent_id = _seed_parent(
        eng, accession=IGF2R_ACCESSION, sequence="A" * IGF2R_SPAN_AA,
    )
    with Session(eng) as s:
        parent_job = s.get(JobRecord, parent_id)
        parent_a = s.get(ProteinAnalysis, analysis_id)
        specs = emit_tile_jobs(s, parent_job, parent_a)
        s.flush()
        assert len(specs) == 2
        for child in _rental_children(s, parent_id):
            _mark_complete(s, child)
        s.flush()

        ready = stitch_readiness(s, s.get(JobRecord, parent_id), s.get(ProteinAnalysis, analysis_id))
        assert ready.ready is True
        assert ready.expected_n == 2
        assert ready.present_complete_n == 2
        assert ready.missing == ()
        assert ready.uncovered_n == 0


def test_full_cover_missing_one_pae_is_not_ready():
    """T-1080 — both tiles complete+PDB; one PAE path absent (D-106 category)."""
    eng = _engine()
    analysis_id, parent_id = _seed_parent(
        eng, accession=IGF2R_ACCESSION, sequence="A" * IGF2R_SPAN_AA,
    )
    with Session(eng) as s:
        parent_job = s.get(JobRecord, parent_id)
        parent_a = s.get(ProteinAnalysis, analysis_id)
        emit_tile_jobs(s, parent_job, parent_a)
        s.flush()
        children = sorted(
            _rental_children(s, parent_id),
            key=lambda j: (j.inference_settings or {}).get("tile_index"),
        )
        assert len(children) == 2
        _mark_complete(s, children[0])
        _mark_complete(s, children[1], pae=None)
        s.flush()

        ready = stitch_readiness(s, s.get(JobRecord, parent_id), s.get(ProteinAnalysis, analysis_id))
        assert ready.ready is False
        assert ready.expected_n == 2
        assert ready.present_complete_n == 1
        assert len(ready.missing) == 1
        assert ready.missing[0].tile_index == children[1].inference_settings["tile_index"]
        assert ready.uncovered_n == 0


def test_mucin_or_no_tiles_is_not_ready():
    """T-1081 — mucin / empty plan is not a pass. Empty missing is not ready."""
    eng = _engine()
    analysis_id, parent_id = _seed_parent(
        eng, accession="Q8WXI7", sequence="A" * 80,
    )
    with Session(eng) as s:
        specs = emit_tile_jobs(
            s, s.get(JobRecord, parent_id), s.get(ProteinAnalysis, analysis_id),
        )
        assert specs == []
        ready = stitch_readiness(
            s, s.get(JobRecord, parent_id), s.get(ProteinAnalysis, analysis_id),
        )
        assert ready.ready is False
        assert ready.expected_n == 0
        assert ready.present_complete_n == 0
        assert ready.missing == ()
        assert ready.uncovered_n == 80  # empty plan covers none of the span
        assert set(MUCIN_ACCESSIONS)  # named set still the category, not length


def test_d116_is_a_log_header():
    """The check is the entry, not a reference to one (D-062)."""
    import re

    log = (REPO / "docs" / "README.md").read_text(encoding="utf-8")
    assert re.search(r"^### D-116 — ", log, re.M)
    assert "stitch_readiness" in log
    assert "parent **2817**" in log
    assert "wave1 FAIL **17**" in log
