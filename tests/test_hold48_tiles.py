"""D-111 — hold-48 tiling. Tests that must be able to go red.

BUILD GO 2026-09-04 (issue #210). No GPU, no Fly, no prod enqueue.
Fixtures stand in for tile PDBs / PAEs. The 1656 cap is not raised.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.artifacts import build_fold_spec
from core.contracts import TIER_RECIPE
from core.enqueue import FetchedSequence, enqueue_cohort
from core.features import parse_pdb
from core.hold48 import (
    IGF2R_ACCESSION,
    IGF2R_SPAN_AA,
    MIN_OVERLAP_AA,
    MUCIN_ACCESSIONS,
    OUT_OF_CLASS,
    STRIDE_AA,
    TILE_WINDOW_AA,
    Hold48Row,
    OneShotRentalForbidden,
    apply_mucin_ceiling,
    emit_tile_jobs,
    enqueue_oneshot_rental,
    hold48_rows,
    is_tile_job,
    n_tiles,
    place_tiles,
    plan_all_tileable,
    plan_tiles,
    refuse_oneshot_rental,
    tileable_rows,
)
from core.hold48_stitch import TileFold, stitch_pae, stitch_pdb, stitch_plddt, write_stitched
from core.manifest import ManifestRow
from db.models import Base, JobRecord, ProteinAnalysis
from doubles import UnlockedFakeJobQueue
from worker.main import fold_from_spec
from worker.orchestrator import FoldError, FoldSpec
from worker.runner import MODEL_REVISION

REPO = Path(__file__).resolve().parent.parent
REV = MODEL_REVISION


def _ca_pdb(n: int, *, x0: float = 0.0) -> str:
    """One CA per residue, local numbering 1..n. Generated in the test — not committed."""
    lines = []
    for i in range(n):
        x = x0 + i * 3.8
        lines.append(
            f"ATOM  {i + 1:5d}  CA  ALA A{i + 1:4d}    "
            f"{x:8.3f}{0.0:8.3f}{0.0:8.3f}  1.00 50.00           C  "
        )
    return "\n".join(lines) + "\n"


def _const_pae(n: int, value: float) -> list[list[float]]:
    return [[value] * n for _ in range(n)]


def _igf2r_row() -> Hold48Row:
    return next(r for r in tileable_rows() if r.accession == IGF2R_ACCESSION)


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


def _seed_parent(
    eng,
    *,
    accession: str,
    sequence: str,
    jobs_tier=None,
    meta_tier: str = "rental",
    extra_meta: dict | None = None,
    extra_settings: dict | None = None,
):
    meta = {
        "sequence": sequence,
        "tier": meta_tier,
        "source": "sliced_ecd",
        "span_aa": len(sequence),
        "fold_length": len(sequence),
        "ecd_start": 41,
        "ecd_end": 41 + len(sequence) - 1,
        **(extra_meta or {}),
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
            tier=jobs_tier,
            inference_settings=_settings(**(extra_settings or {})),
        )
        s.add(job)
        s.commit()
        return a.id, job.id


# ── geometry (must be able to fail) ───────────────────────────────────────────

def test_window_overlap_stride_are_the_go_numbers():
    assert TILE_WINDOW_AA == 1656
    assert MIN_OVERLAP_AA == 128
    assert STRIDE_AA == 1528


def test_n_tiles_formula():
    assert n_tiles(1656) == 1
    assert n_tiles(1657) == 2
    assert n_tiles(IGF2R_SPAN_AA) == 2
    assert n_tiles(1656 + 1528) == 2
    assert n_tiles(1656 + 1528 + 1) == 3


def test_hold48_is_discovered_from_the_census_manifest_not_invented():
    rows = hold48_rows()
    assert len(rows) == 48
    mucins = {r.accession for r in rows if r.is_mucin}
    assert mucins == set(MUCIN_ACCESSIONS)
    assert len(tileable_rows()) == 45
    assert IGF2R_ACCESSION in {r.accession for r in tileable_rows()}
    assert "Q9NYQ8" in {r.accession for r in tileable_rows()}  # FAT2 is tile, not mucin


def test_every_emitted_tile_is_at_most_1656_and_the_45_sum_to_106():
    specs = plan_all_tileable()
    assert len(specs) == 106
    assert {t.accession for t in specs}.isdisjoint(MUCIN_ACCESSIONS)
    for t in specs:
        assert t.length <= TILE_WINDOW_AA, (
            f"{t.accession} tile {t.tile_index} length {t.length} exceeds {TILE_WINDOW_AA}"
        )
        assert t.end - t.start + 1 == t.length
        assert t.start >= 1 and t.end >= t.start


def test_mucins_are_never_tiled():
    for acc in MUCIN_ACCESSIONS:
        row = next(r for r in hold48_rows() if r.accession == acc)
        assert plan_tiles(row) == []


# ── IGF2R pilot ───────────────────────────────────────────────────────────────

def test_igf2r_pilot_is_exactly_two_tiles():
    specs = plan_tiles(_igf2r_row())
    assert len(specs) == 2
    assert [(t.start, t.end, t.length) for t in specs] == [
        (1, 1656, 1656),
        (1529, 2264, 736),
    ]
    assert specs[0].end - specs[1].start + 1 == MIN_OVERLAP_AA
    assert all(t.accession == IGF2R_ACCESSION for t in specs)
    assert all(t.parent_job_id is None for t in specs)  # planner does not claim the parent


def test_domain_snap_moves_an_internal_edge_within_64():
    windows = place_tiles(IGF2R_SPAN_AA, domain_ends=(1640,))
    assert windows[0] == (1, 1640)
    assert windows[1][1] == IGF2R_SPAN_AA
    assert all(e - s + 1 <= TILE_WINDOW_AA for s, e in windows)


def test_domain_snap_that_would_open_a_gap_is_refused():
    """A domain end that would uncover residues is dropped; unsnapped placement stands."""
    # Snap tile-2 start (1529) to 2000 — far, not within 64 — no change.
    assert place_tiles(IGF2R_SPAN_AA, domain_ends=(2000,)) == place_tiles(IGF2R_SPAN_AA)


# ── stitch + off-block PAE is null, not zeros ─────────────────────────────────

def test_overlap_takes_the_higher_plddt_residue():
    a = TileFold(
        start=1, end=10, pdb=_ca_pdb(10),
        plddt=[90.0] * 7 + [40.0, 40.0, 40.0],
        pae=_const_pae(10, 1.0),
    )
    b = TileFold(
        start=8, end=15, pdb=_ca_pdb(8, x0=100.0),
        plddt=[80.0] * 8,
        pae=_const_pae(8, 2.0),
    )
    plddt = stitch_plddt([a, b], 15)
    assert plddt[:7] == [90.0] * 7
    assert plddt[7:10] == [80.0, 80.0, 80.0]  # overlap: B's 80 beats A's 40
    assert plddt[10:] == [80.0] * 5


def test_stitched_pae_off_block_is_null_not_zero():
    a = TileFold(start=1, end=10, pdb=_ca_pdb(10), plddt=[90.0] * 10, pae=_const_pae(10, 1.0))
    b = TileFold(start=8, end=15, pdb=_ca_pdb(8), plddt=[50.0] * 8, pae=_const_pae(8, 2.0))
    pae = stitch_pae([a, b], 15)
    # On-block: residue 1 vs 1 came from tile A.
    assert pae[0][0] == 1.0
    # Off-block: residue 1 (only in A) vs residue 15 (only in B) never co-resided.
    assert pae[0][14] is None
    assert pae[14][0] is None
    assert pae[0][14] != 0
    assert pae[0][14] != 0.0
    # A zero here would be the defect the GO names.
    dumped = json.dumps(pae)
    assert dumped.startswith("[[")
    assert "null" in dumped
    # The off-block cell serialises as JSON null, not 0.
    parsed = json.loads(dumped)
    assert parsed[0][14] is None


def test_stitch_refuses_to_invent_gap_coordinates():
    a = TileFold(start=1, end=5, pdb=_ca_pdb(5), plddt=[90.0] * 5, pae=_const_pae(5, 1.0))
    with pytest.raises(Exception, match="no tile|invent"):
        stitch_pdb([a], 10)


def test_igf2r_pilot_stitch_writes_two_tile_pdbs_two_paes_and_a_stitched_pdb(tmp_path):
    specs = plan_tiles(_igf2r_row())
    assert len(specs) == 2
    tiles = []
    for spec, x0, plddt_v, pae_v in (
        (specs[0], 0.0, 90.0, 1.0),
        (specs[1], 500.0, 40.0, 2.0),
    ):
        tiles.append(
            TileFold(
                start=spec.start,
                end=spec.end,
                pdb=_ca_pdb(spec.length, x0=x0),
                plddt=[plddt_v] * spec.length,
                pae=_const_pae(spec.length, pae_v),
            )
        )
    paths = write_stitched(tiles, IGF2R_SPAN_AA, tmp_path)
    assert (tmp_path / "tile1.pdb").is_file()
    assert (tmp_path / "tile2.pdb").is_file()
    assert (tmp_path / "tile1_pae.json").is_file()
    assert (tmp_path / "tile2_pae.json").is_file()
    assert Path(paths["pdb"]).is_file()
    assert Path(paths["pae"]).is_file()
    atoms = [a for a in parse_pdb(Path(paths["pdb"]).read_text()) if a.is_ca]
    assert len(atoms) == IGF2R_SPAN_AA
    assert atoms[0].res_seq == 1 and atoms[-1].res_seq == IGF2R_SPAN_AA
    pae = json.loads(Path(paths["pae"]).read_text())
    assert len(pae) == IGF2R_SPAN_AA
    # Residue 1 (tile 1 only) vs residue 2264 (tile 2 only): off-block.
    assert pae[0][IGF2R_SPAN_AA - 1] is None
    assert pae[IGF2R_SPAN_AA - 1][0] is None
    # Overlap prefers tile 1's pLDDT 90 over tile 2's 40.
    plddt = json.loads(Path(paths["plddt"]).read_text())
    assert plddt[1528] == 90.0  # parent res 1529


# ── planner emit: parent stays NULL-tier ──────────────────────────────────────

def test_emit_writes_tiles_and_does_not_claim_the_parent():
    eng = _engine()
    analysis_id, parent_id = _seed_parent(
        eng, accession=IGF2R_ACCESSION, sequence="A" * IGF2R_SPAN_AA, jobs_tier=None,
    )
    with Session(eng) as s:
        parent_job = s.get(JobRecord, parent_id)
        parent_a = s.get(ProteinAnalysis, analysis_id)
        specs = emit_tile_jobs(s, parent_job, parent_a)
        s.commit()
        parent_job = s.get(JobRecord, parent_id)
        assert parent_job.tier is None
        assert parent_job.status == "pending"
        assert len(specs) == 2
        children = s.execute(
            select(JobRecord).where(JobRecord.id != parent_id)
        ).scalars().all()
        assert len(children) == 2
        for child in children:
            assert child.tier == "rental"
            assert child.status == "pending"
            assert is_tile_job(child.inference_settings)
            assert child.inference_settings["parent_job_id"] == parent_id
            a = s.get(ProteinAnalysis, child.analysis_id)
            assert len(a.meta["sequence"]) <= TILE_WINDOW_AA
            assert a.meta["hold48_kind"] == "tile"


def test_emit_for_a_mucin_writes_nothing():
    eng = _engine()
    analysis_id, parent_id = _seed_parent(
        eng, accession="Q8WXI7", sequence="A" * 100, jobs_tier=None,
    )
    with Session(eng) as s:
        specs = emit_tile_jobs(s, s.get(JobRecord, parent_id), s.get(ProteinAnalysis, analysis_id))
        s.commit()
        assert specs == []
        assert s.execute(select(JobRecord)).scalars().all().__len__() == 1


# ── fold-path wiring (no GPU) ─────────────────────────────────────────────────

def test_claimed_tile_resolves_t5_recipe_and_length_cap():
    eng = _engine()
    analysis_id, parent_id = _seed_parent(
        eng, accession=IGF2R_ACCESSION, sequence="A" * IGF2R_SPAN_AA, jobs_tier=None,
    )
    with Session(eng) as s:
        emit_tile_jobs(s, s.get(JobRecord, parent_id), s.get(ProteinAnalysis, analysis_id))
        s.commit()
        child = s.execute(
            select(JobRecord).where(JobRecord.tier == "rental")
        ).scalars().first()
        child_analysis = s.get(ProteinAnalysis, child.analysis_id)
        q = UnlockedFakeJobQueue()
        q.enqueue(
            child.analysis_id,
            inference_settings=child.inference_settings,
            tier="rental",
        )
    spec = build_fold_spec(q, eng, "rental-box", tier="rental")
    assert spec is not None
    assert len(spec.sequence) <= TILE_WINDOW_AA
    assert spec.dtype == TIER_RECIPE["rental"]["dtype"] == "fp16"
    assert spec.chunk_size == TIER_RECIPE["rental"]["chunk_size"] == 64
    assert spec.sequence == child_analysis.meta["sequence"]


def test_fold_from_spec_refuses_a_sequence_over_1656():
    spec = FoldSpec(
        job_id=1, sequence="A" * 1657, model_revision=REV,
        dtype="fp16", chunk_size=64, source="sliced_ecd", ecd_start=1, ecd_end=1657,
    )
    with pytest.raises(FoldError, match="1656"):
        fold_from_spec(spec, fold_fn=lambda *a, **k: None)


# ── mucin ceiling: 0 PDB, 0 PAE, out_of_class ─────────────────────────────────

def test_mucin_ceiling_writes_zero_pdb_zero_pae(tmp_path):
    eng = _engine()
    for acc, n in (("Q8WXI7", 14451), ("Q9UKN1", 5364), ("Q685J3", 4368)):
        _seed_parent(eng, accession=acc, sequence="A" * min(n, 20), jobs_tier=None)
    _seed_parent(eng, accession=IGF2R_ACCESSION, sequence="A" * 20, jobs_tier=None)
    with Session(eng) as s:
        marked = apply_mucin_ceiling(s, artifact_root=str(tmp_path))
        s.commit()
        assert set(marked) == set(MUCIN_ACCESSIONS)
        jobs = s.execute(select(JobRecord)).scalars().all()
        by_acc = {}
        for job in jobs:
            a = s.get(ProteinAnalysis, job.analysis_id)
            by_acc[a.input_value] = (job, a)
        for acc in MUCIN_ACCESSIONS:
            job, a = by_acc[acc]
            assert job.status == OUT_OF_CLASS
            assert a.pdb_path is None
            assert a.pae_json_path is None
        igf_job, _ = by_acc[IGF2R_ACCESSION]
        assert igf_job.status == "pending"
    assert list(tmp_path.rglob("*.pdb")) == []
    assert list(tmp_path.rglob("*pae*")) == []
    assert list(tmp_path.rglob("*.json.gz")) == []


# ── guards ────────────────────────────────────────────────────────────────────

def test_claiming_muc16_as_rental_oneshot_fails():
    eng = _engine()
    analysis_id, _ = _seed_parent(
        eng, accession="Q8WXI7", sequence="A" * 50, jobs_tier="rental",
    )
    q = UnlockedFakeJobQueue()
    q.enqueue(analysis_id, inference_settings=_settings(), tier="rental")
    with pytest.raises(OneShotRentalForbidden, match="mucin"):
        build_fold_spec(q, eng, "rental-box", tier="rental")


def test_claiming_a_hold_parent_as_oneshot_rental_fails():
    eng = _engine()
    analysis_id, _ = _seed_parent(
        eng, accession=IGF2R_ACCESSION, sequence="A" * IGF2R_SPAN_AA, jobs_tier="rental",
    )
    q = UnlockedFakeJobQueue()
    q.enqueue(analysis_id, inference_settings=_settings(), tier="rental")
    with pytest.raises(OneShotRentalForbidden, match="parent"):
        build_fold_spec(q, eng, "rental-box", tier="rental")


def test_enqueue_of_muc16_as_rental_oneshot_fails():
    with pytest.raises(OneShotRentalForbidden, match="mucin"):
        enqueue_oneshot_rental("Q8WXI7", sequence_length=14451, is_tile=False)


def test_enqueue_cohort_refuses_a_non_excluded_mucin_rental_row():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    row = ManifestRow(
        accession="Q8WXI7", gene="MUC16", label="mucin",
        boundary_method="sliced_ecd", span=14451, ecd_start=1, ecd_end=14451,
        tier="rental", tier_reason="over_local_ceiling",
        held_out=False, excluded=False, exclusion_reason=None, primary_match=False,
    )
    with Session(engine) as s:
        with pytest.raises(OneShotRentalForbidden, match="mucin"):
            enqueue_cohort(s, [row], lambda acc: FetchedSequence("A" * 14451, "2024_06"))


def test_census_ingest_assert_claimable_refuses_mucin_rental():
    import scripts.census_ingest as ing
    payload = {
        "accession": "Q8WXI7",
        "tier": "rental",
        "meta": {"sequence": "A" * 80, "tier": "rental"},
        "inference_settings": _settings(),
    }
    with pytest.raises(OneShotRentalForbidden, match="mucin"):
        ing.assert_claimable(payload)


def test_null_tier_parent_is_still_unclaimable_under_d090():
    """The hold itself: NULL tier matches nobody. The D-111 guard is the extra
    refusal for when someone sets tier=rental on the parent."""
    q = UnlockedFakeJobQueue()
    q.enqueue(1, inference_settings=_settings(), tier=None)
    assert q.claim("rental-box", tier="rental") is None


def test_refuse_oneshot_is_silent_for_an_ordinary_rental_tile():
    refuse_oneshot_rental(
        IGF2R_ACCESSION, is_tile=True, jobs_tier="rental", sequence_length=1656,
    )


def test_hold48_module_does_not_import_worker():
    """DEP-001: app/artifacts imports this module. worker/ is not on Fly."""
    src = (REPO / "core" / "hold48.py").read_text(encoding="utf-8")
    assert "from worker" not in src
    assert "import worker" not in src


def test_d111_is_the_go_and_d110_is_the_deferred_surface_integer():
    """⚠ D-094 amendment 1 cited D-110 first. Spending it on tiling would resolve
    that citation to the wrong live entry (F-044 / F-065)."""
    import re
    log = (REPO / "docs" / "README.md").read_text(encoding="utf-8")
    assert re.search(r"^### D-111 — BUILD GO", log, re.M)
    assert re.search(r"^### D-110 — PAE figure provenance", log, re.M)
