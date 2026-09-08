"""D-120 — Phase 2 assembled-parent review. These must be able to go red.

An assembled parent card carries kind + readiness + tile table (chosen vs spare)
+ PAE yes/no + stitched.* / tileN.* downloads. Spare 3693 is not a second protein.
A structural profile on an assembly is refused_assembled_incommensurable.
The inventory ids are disclosed, not ingested into F-004.

⚠ D-132 amends the inventory the card serves: the live count is the measured **45**
assembled parents (2026-09-08), and the **27** Wave1+Wave2 parents are a dated slice
inside it rather than the whole. Both counts ship; neither may stand for the other.
"""
from __future__ import annotations

from pathlib import Path

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.census_profile_read import census_profile_block
from app.reads import (
    ADDITIONAL_ASSEMBLED_PARENT_IDS,
    ASSEMBLED_PARENT_IDS,
    HOLD48_PREFERRED_TILE_IDS,
    HOLD48_SPARE_TILE_IDS,
    IGF2R_COHORT_JOB_ID,
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
    # ⚠ D-132 — the inventory grew from 27 to 45 and the D-109 bar has to grow with it.
    # A wider disclosure is the easiest place for an ingest to arrive unnoticed.
    for name in ("ASSEMBLED_PARENT_IDS", "ADDITIONAL_ASSEMBLED_PARENT_IDS"):
        assert name not in scorer
        assert name not in fit
        assert name not in ranking_fn


# ⚠⚠ D-132 — THE REGRESSION TRIPWIRE, API SIDE.
#
# The 27 was never wrong about Wave1+Wave2; it was wrong as an answer to "how many parents
# are assembled?", and the payload gave a reader no way to tell those two questions apart.
# These assertions must be able to go red in BOTH directions: if the served count drifts
# back to 27, and if the 27 is deleted rather than demoted to the dated slice it is.
def test_live_inventory_is_the_measured_forty_five_not_the_wave_slice():
    eng = _engine()
    _seed_q9p273(eng)
    inv = get_census_detail(eng, 2817)["assembly_review"]["inventory"]

    assert inv["unique_stitched_parents_n"] == 45
    # ⚠ the named failure: a live count of 27 is the defect this entry exists to fix
    assert inv["unique_stitched_parents_n"] != 27
    assert len(inv["parent_ids"]) == 45
    assert len(set(inv["parent_ids"])) == 45, "unique means unique"

    # the breakdown, not the total (D-016 / method note item 2)
    assert inv["wave1_wave2_closeout_n"] == 27
    assert inv["wave1_pass"] == 10
    assert inv["wave2_pass"] == 17
    assert inv["wave1_pass"] + inv["wave2_pass"] == inv["wave1_wave2_closeout_n"]
    assert inv["additional_assembled_n"] == 18
    assert (
        inv["wave1_wave2_closeout_n"] + inv["additional_assembled_n"]
        == inv["unique_stitched_parents_n"]
    )

    # every count names how it is known, and the two dates do not collapse into one
    assert inv["measured_on"] == "2026-09-08"
    assert inv["wave1_wave2_measured_on"] == "2026-09-05"
    assert inv["measured_on"] != inv["wave1_wave2_measured_on"]
    assert "pdb_path" in inv["source"]


def test_the_two_id_sets_are_disjoint_and_the_union_is_the_served_list():
    assert len(WAVE1_WAVE2_STITCHED_PARENT_IDS) == 27
    assert len(ADDITIONAL_ASSEMBLED_PARENT_IDS) == 18
    assert not (WAVE1_WAVE2_STITCHED_PARENT_IDS & ADDITIONAL_ASSEMBLED_PARENT_IDS)
    assert ASSEMBLED_PARENT_IDS == (
        WAVE1_WAVE2_STITCHED_PARENT_IDS | ADDITIONAL_ASSEMBLED_PARENT_IDS
    )
    assert len(ASSEMBLED_PARENT_IDS) == 45
    # the 18 as handed by owner ops, id for id — a count alone cannot catch a wrong member
    assert ADDITIONAL_ASSEMBLED_PARENT_IDS == frozenset({
        2837, 2920, 2959, 2973, 2974, 3020, 3067, 3082, 3086,
        3094, 3120, 3124, 3131, 3209, 3237, 3356, 3420, 3559,
    })
    # ⚠ D-081 — IGF2R census parent 3356 joins the assembled inventory; cohort job 57 is a
    # different population and does not appear in either set.
    assert 3356 in ADDITIONAL_ASSEMBLED_PARENT_IDS
    assert 3356 not in WAVE1_WAVE2_STITCHED_PARENT_IDS
    assert IGF2R_COHORT_JOB_ID not in ASSEMBLED_PARENT_IDS


def test_the_card_reports_both_memberships_separately():
    """A parent can be assembled and outside the wave slice. One flag cannot say that."""
    eng = _engine()
    _seed_q9p273(eng)
    review = get_census_detail(eng, 2817)["assembly_review"]
    assert review["in_wave1_wave2_inventory"] is True
    assert review["in_assembled_inventory"] is True
    assert 3356 not in WAVE1_WAVE2_STITCHED_PARENT_IDS
    assert 3356 in ASSEMBLED_PARENT_IDS


def test_d132_entry_exists_before_the_code_claims_it():
    """Living-doc rule, and the D-062 defect: check the ENTRY, never a reference to it."""
    log = Path("docs/README.md").read_text(encoding="utf-8")
    assert "### D-132 — Assemble-inventory amend" in log
    # the entry has to carry the provenance the surfaces are now citing
    entry = log[log.index("### D-132"): log.index("### D-130-B")]
    assert "2026-09-08" in entry
    assert "pdb_path" in entry
    assert "read-only" in entry
    # and it must not quietly re-open what the amend explicitly leaves closed
    assert "D-109" in entry
    assert "D-118" in entry
