"""D-118 — Phase 1 P0 census identity. These must be able to go red.

A parent plus two complete tiles is ONE protein. An accession opens the parent,
never a tile (Q9P273 / 2817, not 3673). Spare ids 3693/3695/3696 are not a
second protein. ``census_summary.folded`` does not grow by tile cardinality.
Assembled ``stitched.pdb`` resolves ``stitched_plddt.json``.
"""
from __future__ import annotations

import json
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.reads import (
    HOLD48_SPARE_TILE_IDS,
    canonical_census_analysis_id,
    census_summary,
    get_census_detail,
    get_plddt_path,
    list_census,
    resolve_census_accession,
)
from db.models import Base, ProteinAnalysis

# 27 unique Wave1+Wave2 stitched parents (D-117 inventory) + IGF2R 3356 if distinct.
WAVE_PARENTS = ["Q9P273"] + [f"A{i:05d}" for i in range(1, 27)]
assert len(WAVE_PARENTS) == 27
IGF2R = "P11717"
TILE_IDS_MUST_NOT_SURFACE = {3673, 3630, 3693, 3695, 3696, 3589, 3590}


def _engine():
    eng = create_engine("sqlite://")
    Base.metadata.create_all(eng)
    return eng


def _add(
    session,
    *,
    id: int,
    acc: str,
    kind: str,
    pdb: str | None = None,
    plddt: float | None = None,
    parent_job_id: int | None = None,
    tile_start: int = 1,
    span_aa: int | None = None,
):
    meta = {
        "hold48_kind": kind,
        "span_aa": span_aa if span_aa is not None else (1656 if kind == "tile" else 2368),
    }
    if parent_job_id is not None:
        meta["parent_job_id"] = parent_job_id
        meta["tile_start"] = tile_start
        meta["tile_end"] = tile_start + 1655
    session.add(
        ProteinAnalysis(
            id=id,
            input_type="uniprot",
            input_value=acc,
            cohort_tranche=5,
            pdb_path=pdb,
            mean_plddt=plddt,
            meta=meta,
        )
    )


def _seed_inventory(eng, *, stitched_dir: Path | None = None):
    """27 assembled parents, each with two tiles, plus IGF2R, plus named dups/spares."""
    stitched = None
    if stitched_dir is not None:
        stitched_dir.mkdir(parents=True, exist_ok=True)
        (stitched_dir / "stitched.pdb").write_text("HEADER\n", encoding="utf-8")
        (stitched_dir / "stitched_plddt.json").write_text("[61.07]", encoding="utf-8")
        stitched = str(stitched_dir / "stitched.pdb")
    with Session(eng) as s:
        # Q9P273 — named exemplar: parent 2817, tiles 3673+3630, spare 3693
        _add(s, id=2817, acc="Q9P273", kind="parent", pdb=stitched or "/tmp/q9p273/stitched.pdb",
             plddt=61.07)
        _add(s, id=3673, acc="Q9P273", kind="tile", pdb="/tmp/tile3673.pdb", plddt=70.0,
             parent_job_id=2817, tile_start=1, span_aa=1656)
        _add(s, id=3630, acc="Q9P273", kind="tile", pdb="/tmp/tile3630.pdb", plddt=55.0,
             parent_job_id=2817, tile_start=1529, span_aa=840)
        _add(s, id=3693, acc="Q9P273", kind="tile", pdb="/tmp/tile3693.pdb", plddt=71.0,
             parent_job_id=2817, tile_start=1, span_aa=1656)
        # 26 more assembled parents (A00001..A00026), two tiles each
        next_id = 4000
        for i, acc in enumerate(WAVE_PARENTS[1:], start=1):
            parent_id = 2900 + i
            _add(s, id=parent_id, acc=acc, kind="parent", pdb=f"/tmp/{acc}/stitched.pdb",
                 plddt=60.0 + (i % 5))
            t1, t2 = next_id, next_id + 1
            next_id += 2
            _add(s, id=t1, acc=acc, kind="tile", pdb=f"/tmp/{acc}/t1.pdb", plddt=80.0,
                 parent_job_id=parent_id, tile_start=1)
            _add(s, id=t2, acc=acc, kind="tile", pdb=f"/tmp/{acc}/t2.pdb", plddt=50.0,
                 parent_job_id=parent_id, tile_start=1529, span_aa=800)
            if acc == "A00001":
                _add(s, id=3695, acc=acc, kind="tile", pdb="/tmp/spare3695.pdb", plddt=99.0,
                     parent_job_id=parent_id, tile_start=1)
            if acc == "A00002":
                _add(s, id=3696, acc=acc, kind="tile", pdb="/tmp/spare3696.pdb", plddt=99.0,
                     parent_job_id=parent_id, tile_start=1)
        # IGF2R census parent 3356 + tiles 3589/3590
        _add(s, id=3356, acc=IGF2R, kind="parent", pdb="/tmp/igf2r/stitched.pdb", plddt=58.0,
             span_aa=2264)
        _add(s, id=3589, acc=IGF2R, kind="tile", pdb="/tmp/igf2r/t3589.pdb", plddt=66.0,
             parent_job_id=3356, tile_start=1, span_aa=1608)
        _add(s, id=3590, acc=IGF2R, kind="tile", pdb="/tmp/igf2r/t3590.pdb", plddt=64.0,
             parent_job_id=3356, tile_start=1481, span_aa=797)
        # one single-pass census fold, to prove tiles are the ones excluded
        _add(s, id=1901, acc="A0AVI2", kind="single-pass", pdb="/tmp/a0avi2.pdb", plddt=54.14,
             span_aa=43)
        s.commit()


def test_parent_plus_two_tiles_is_one_census_row():
    eng = _engine()
    _seed_inventory(eng)
    rows = [r for r in list_census(eng) if r.get("accession") == "Q9P273"]
    assert len(rows) == 1, rows
    assert rows[0]["id"] == 2817
    assert rows[0]["structure_kind"] == "assembled"
    assert rows[0]["span_aa"] != 1656


def test_accession_opens_parent_not_tile_3673():
    eng = _engine()
    _seed_inventory(eng)
    aid, outcome = resolve_census_accession(eng, "q9p273")
    assert outcome == "census"
    assert aid == 2817
    assert canonical_census_analysis_id(eng, 3673) == 2817
    assert canonical_census_analysis_id(eng, 3693) == 2817
    detail = get_census_detail(eng, 2817)
    assert detail["id"] == 2817
    assert detail["structure_kind"] == "assembled"
    assert get_census_detail(eng, 3673) is None


def test_spare_tiles_are_not_a_second_protein():
    eng = _engine()
    _seed_inventory(eng)
    rows = list_census(eng)
    ids = {r.get("id") for r in rows if r.get("id") is not None}
    assert ids.isdisjoint(HOLD48_SPARE_TILE_IDS)
    assert ids.isdisjoint(TILE_IDS_MUST_NOT_SURFACE)
    accs = [r["accession"] for r in rows if r.get("accession") in {"Q9P273", "A00001", "A00002"}]
    assert accs.count("Q9P273") == 1
    assert accs.count("A00001") == 1
    assert accs.count("A00002") == 1


def test_twenty_seven_parents_plus_igf2r_are_not_inflated_by_tiles():
    """The closed-out inventory is 27 unique + IGF2R 3356 — not 27 plus every tile."""
    eng = _engine()
    _seed_inventory(eng)
    rows = list_census(eng)
    by_acc = {}
    for r in rows:
        by_acc.setdefault(r["accession"], []).append(r)
    for acc in WAVE_PARENTS + [IGF2R]:
        hits = by_acc.get(acc, [])
        assert len(hits) == 1, (acc, hits)
        assert hits[0]["id"] not in TILE_IDS_MUST_NOT_SURFACE
        assert hits[0]["structure_kind"] == "assembled"
    summary = census_summary(eng)
    # 27 + IGF2R + A0AVI2 single-pass = 29 folded proteins, not 29 + ~60 tiles
    assert summary["folded"] == 29
    assert "tile" in summary["keys"]["folded"]


def test_tiles_only_parent_is_one_row_not_each_tile():
    eng = _engine()
    with Session(eng) as s:
        _add(s, id=5000, acc="Q9ZZZZ", kind="parent", pdb=None, plddt=None)
        _add(s, id=5001, acc="Q9ZZZZ", kind="tile", pdb="/tmp/t1.pdb", plddt=80.0,
             parent_job_id=5000, tile_start=1)
        _add(s, id=5002, acc="Q9ZZZZ", kind="tile", pdb="/tmp/t2.pdb", plddt=70.0,
             parent_job_id=5000, tile_start=1529)
        s.commit()
    rows = [r for r in list_census(eng) if r.get("accession") == "Q9ZZZZ"]
    assert len(rows) == 1
    assert rows[0]["id"] == 5000
    assert rows[0]["structure_kind"] == "tiles_only"
    assert rows[0]["folded"] is False
    assert rows[0]["mean_plddt"] is None
    aid, outcome = resolve_census_accession(eng, "Q9ZZZZ")
    assert (aid, outcome) == (5000, "census")


def test_assembled_plddt_uses_stitched_sibling(tmp_path):
    eng = _engine()
    _seed_inventory(eng, stitched_dir=tmp_path)
    path = get_plddt_path(eng, 2817)
    assert path is not None
    assert Path(path).name == "stitched_plddt.json"
    assert Path(path).is_file()
    assert json.loads(Path(path).read_text(encoding="utf-8")) == [61.07]
    # classic sibling must not be required
    assert not (tmp_path / "plddt.json").exists()


def test_guide_opens_closed_and_does_not_invite_deploy():
    text = Path("docs/GUIDE-renting-hold48.md").read_text(encoding="utf-8")
    head = text.split("## Historical", 1)[0]
    assert "CLOSED" in head
    assert "Terminated" in head
    assert "Do not Deploy" in head
    assert "Historical — do not run unless Matt re-opens rental" in text
    # the live-path invitation must not sit above the historical collapse
    assert head.index("CLOSED") < head.index("Do not Deploy")
