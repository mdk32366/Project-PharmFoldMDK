"""D-120 — Phase 2 assembled-parent review. These must be able to go red.

An assembled parent card carries kind + readiness + tile table (chosen vs spare)
+ PAE yes/no + stitched.* / tileN.* downloads. Spare 3693 is not a second protein.
A structural profile on an assembly is refused_assembled_incommensurable.
The 27 ids are disclosed, not ingested into F-004.
"""
from __future__ import annotations

from pathlib import Path

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.census_profile_read import census_profile_block
from app.reads import (
    HOLD48_PREFERRED_TILE_IDS,
    HOLD48_SPARE_TILE_IDS,
    WAVE1_WAVE2_STITCHED_PARENT_IDS,
    assign_tile_roles,
    download_stem,
    get_census_detail,
    igf2r_two_population_copy,
)
from db.models import Base, ProteinAnalysis


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
    pae: str | None = None,
    plddt: float | None = None,
    parent_job_id: int | None = None,
    tile_start: int = 1,
    tile_end: int | None = None,
    span_aa: int | None = None,
    tile_index: int | None = None,
):
    meta = {
        "hold48_kind": kind,
        "span_aa": span_aa if span_aa is not None else (1656 if kind == "tile" else 2368),
    }
    if parent_job_id is not None:
        meta["parent_job_id"] = parent_job_id
        meta["tile_start"] = tile_start
        meta["tile_end"] = tile_end if tile_end is not None else tile_start + 1655
        if tile_index is not None:
            meta["tile_index"] = tile_index
    session.add(
        ProteinAnalysis(
            id=id,
            input_type="uniprot",
            input_value=acc,
            cohort_tranche=5,
            pdb_path=pdb,
            pae_json_path=pae,
            mean_plddt=plddt,
            meta=meta,
        )
    )


def _seed_q9p273(eng, tmp: Path | None = None):
    stitched = "/tmp/q9p273/stitched.pdb"
    if tmp is not None:
        tmp.mkdir(parents=True, exist_ok=True)
        (tmp / "stitched.pdb").write_text("HEADER\n", encoding="utf-8")
        (tmp / "stitched_plddt.json").write_text("[61.07]", encoding="utf-8")
        (tmp / "stitched_pae.json").write_text("[]", encoding="utf-8")
        stitched = str(tmp / "stitched.pdb")
        pae = str(tmp / "stitched_pae.json")
    else:
        pae = "/tmp/q9p273/stitched_pae.json"
    with Session(eng) as s:
        _add(s, id=2817, acc="Q9P273", kind="parent", pdb=stitched, pae=pae, plddt=61.07)
        _add(
            s, id=3673, acc="Q9P273", kind="tile", pdb="/tmp/tile3673.pdb",
            pae="/tmp/tile3673_pae.json", plddt=70.0, parent_job_id=2817,
            tile_start=1, tile_index=0, span_aa=1656,
        )
        _add(
            s, id=3630, acc="Q9P273", kind="tile", pdb="/tmp/tile3630.pdb",
            pae="/tmp/tile3630_pae.json", plddt=55.0, parent_job_id=2817,
            tile_start=1529, tile_end=2368, tile_index=1, span_aa=840,
        )
        _add(
            s, id=3693, acc="Q9P273", kind="tile", pdb="/tmp/tile3693.pdb",
            pae="/tmp/tile3693_pae.json", plddt=71.0, parent_job_id=2817,
            tile_start=1, tile_index=0, span_aa=1656,
        )
        s.commit()


def test_inventory_is_exactly_the_twenty_seven_named_parents():
    assert WAVE1_WAVE2_STITCHED_PARENT_IDS == frozenset({
        2929, 2938, 2939, 3179, 3188, 3190, 3217, 3321, 3541, 3569,
        2817, 2917, 3027, 3097, 3153, 3272, 3320, 3368, 3379, 3394,
        3404, 3432, 3454, 3469, 3516, 3566, 3575,
    })
    assert 3356 not in WAVE1_WAVE2_STITCHED_PARENT_IDS
    assert HOLD48_PREFERRED_TILE_IDS == frozenset({3673, 3674, 3675})
    assert HOLD48_SPARE_TILE_IDS == frozenset({3693, 3695, 3696})


def test_assembled_parent_review_has_readiness_tiles_and_downloads():
    eng = _engine()
    _seed_q9p273(eng)
    detail = get_census_detail(eng, 2817)
    assert detail is not None
    assert detail["structure_kind"] == "assembled"
    review = detail["assembly_review"]
    assert review["parent_analysis_id"] == 2817
    assert review["in_wave1_wave2_inventory"] is True
    ready = review["readiness"]
    assert ready["expected_n"] == 2
    assert ready["present_complete_n"] == 2
    assert ready["missing"] == []
    assert ready["uncovered_n"] == 0
    assert "restitch" in ready["note"]
    ids = {t["analysis_id"]: t for t in review["tiles"]}
    assert ids[3673]["role"] == "chosen"
    assert ids[3673]["has_pae"] is True
    assert ids[3673]["preferred_lower_id"] is True
    assert ids[3693]["role"] == "spare"
    assert ids[3693]["named_spare"] is True
    assert ids[3630]["role"] == "chosen"
    names = [d["name"] for d in review["downloads"]["stitched"]]
    assert names == ["stitched.pdb", "stitched_plddt.json", "stitched_pae.json"]
    tile_names = [d["name"] for d in review["downloads"]["tiles"]]
    assert "tile1.pdb" in tile_names
    assert "tile2.pdb" in tile_names
    assert any(n.startswith("spare3693") for n in tile_names)
    assert 3693 not in review["chosen_tile_ids"]
    assert 3693 in review["spare_tile_ids"]


def test_assign_tile_roles_prefers_lower_ids_over_named_spares():
    eng = _engine()
    _seed_q9p273(eng)
    with Session(eng) as s:
        tiles = list(s.scalars(
            select(ProteinAnalysis).where(ProteinAnalysis.id.in_({3673, 3630, 3693}))
        ).all())
    roles = assign_tile_roles(tiles)
    assert roles[3673] == "chosen"
    assert roles[3693] == "spare"
    assert roles[3630] == "chosen"


def test_download_stem_is_stitched_for_assembled_parent():
    eng = _engine()
    _seed_q9p273(eng)
    assert download_stem(eng, 2817) == "stitched"
    assert download_stem(eng, 3673) == "tile1"
    assert download_stem(eng, 3693) == "spare3693"


def test_structural_profile_refuses_an_assembly_with_no_number():
    eng = _engine()
    _seed_q9p273(eng)
    block = census_profile_block(eng, 2817)
    assert block is not None
    assert block["status"] == "refused"
    assert block["structural_profile"] is None
    assert block["refusal"]["category"] == "refused_assembled_incommensurable"
    assert "D-109" in block["refusal"]["detail"]


def test_igf2r_copy_names_both_populations():
    copy = igf2r_two_population_copy()
    assert "CUDA OOM" in copy["cohort"]
    assert "57" in copy["cohort"]
    assert "D-081" in copy["census"]
    assert "neither" in copy["census"].lower() or "Neither" in copy["census"]


def test_guide_and_budget_carry_d120_review_stamp():
    guide = Path("docs/GUIDE-renting-hold48.md").read_text(encoding="utf-8")
    assert "D-120" in guide
    assert "CLOSED" in guide
    budget = Path("docs/BUDGET-hold48-tiers-2026-09-04.md").read_text(encoding="utf-8")
    assert "Historical forecast" in budget
    assert "D-120" in budget


def test_d120_entry_exists_before_the_code_claims_it():
    """Living-doc rule: the heading exists; Phase 2 must not claim D-119."""
    log = Path("docs/README.md").read_text(encoding="utf-8")
    assert "### D-120 — Phase 2 review UI" in log
    assert "### D-119 — ADC-A:" in log
    assert "Phase 2 review UI is **D-119**" not in log
    assert "Kabsch" in log


def test_the_twenty_seven_are_not_ingested_into_the_scorer():
    """Disclosure only — F-004 persist path must not grow by the assembled parents."""
    scorer = Path("core/scorer.py").read_text(encoding="utf-8")
    fit = Path("scripts/fit_scorer.py").read_text(encoding="utf-8")
    reads = Path("app/reads.py").read_text(encoding="utf-8")
    assert "WAVE1_WAVE2_STITCHED_PARENT_IDS" not in scorer
    assert "WAVE1_WAVE2_STITCHED_PARENT_IDS" not in fit
    # ranking_payload must not iterate the inventory into target_scores
    ranking_fn = reads[reads.index("def ranking_payload"): reads.index("def ranking_payload") + 2500]
    assert "WAVE1_WAVE2_STITCHED_PARENT_IDS" not in ranking_fn
