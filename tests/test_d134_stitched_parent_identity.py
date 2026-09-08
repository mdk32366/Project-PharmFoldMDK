"""D-134 — a stitched parent is a parent whichever tag ops wrote. These must go red on `8e53af5`.

⚠⚠ **The defect these pin, and how it is known (D-016).** Measured 2026-09-08 against the
live deployment, `GET https://pharmfoldmdk.fly.dev/api/census` (3,467 rows, read-only):

    structure_kind : {'single-pass': 3463, 'mucin': 3, None: 1}   →  assembled = 0
    hold48_kind    : {None: 3422, 'parent_stitched': 45}

and `GET /api/census/2817` → ``hold48_kind='parent_stitched'``,
``structure_kind='single-pass'`` (Q9P273); same for 2929 (Q9UMZ3) and 3356 (P11717,
IGF2R). The 45 ids carrying ``parent_stitched`` are **exactly** ``ASSEMBLED_PARENT_IDS``
— D-132's measured inventory — one row per accession.

So the D-133 fold-type chips were not broken. They were **correct about a wrong input**:
``core.hold48.HOLD48_KIND_PARENT`` is the single string ``"parent"``, ops `write_stitched`
persisted ``"parent_stitched"``, and every read keyed on the first missed all 45. A chip
reading ``assembled (provisional) · 0`` is the honest rendering of a census in which no
row was recognised as assembled.

⚠ **Why this could sit through D-118, D-120, D-132 and D-133 without anything objecting.**
An unrecognised parent does not raise, does not go null, and does not go absent — it falls
through `choose_census_representative`'s `ordinary` branch and comes back a completely
plausible **single-pass** protein, with the parent's real pLDDT and the parent's real span.
Nothing on any surface distinguishes *folded in one pass* from *we did not notice it was
assembled*. This is the F-052 shape at data-tag scale: a vocabulary with one writer, one
reader, and no test that the two agree.

⚠ **Read-path only.** Nothing here rewrites a Fly row, and that is deliberate (D-134
decision 5): the volume's existing tags must work as they are, because a fix that requires
a migration is a fix that is not deployed until someone runs the migration.
"""
from __future__ import annotations

import re
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.census_profile_read import census_profile_statuses
from app.reads import (
    ASSEMBLED_PARENT_IDS,
    census_summary,
    choose_census_representative,
    detail_projection,
    download_stem_for_row,
    get_census_detail,
    is_assembled_parent_row,
    is_census_parent_row,
    is_census_tile_row,
    list_census,
)
from core.hold48 import (
    HOLD48_KIND_PARENT,
    HOLD48_KIND_PARENT_STITCHED,
    HOLD48_PARENT_KINDS,
    STITCHED_PDB_BASENAME,
    is_parent_kind,
    is_stitched_artifact_path,
)
from db.models import Base, ProteinAnalysis

ROOT = Path(__file__).resolve().parent.parent
LOG = (ROOT / "docs" / "README.md").read_text(encoding="utf-8")
ARCH = (ROOT / "ARCHITECTURE.md").read_text(encoding="utf-8")

#: The tag the live volume actually carries, and the path shape it carries it with:
#: ``/data/artifacts/{parent_job_id}/structure.pdb`` (D-132). ⚠ Note the basename is NOT
#: ``stitched.pdb`` on Fly, which is exactly why the meta tag has to be accepted on its own
#: — the artifact-name fallback below would not have saved these rows.
LIVE_TAG = "parent_stitched"


def _engine():
    eng = create_engine("sqlite://")
    Base.metadata.create_all(eng)
    return eng


def _add(session, *, id, acc, kind, pdb=None, plddt=None, parent_job_id=None,
         tile_start=None, span_aa=2368):
    meta = {"span_aa": span_aa}
    if kind is not None:
        meta["hold48_kind"] = kind
    if parent_job_id is not None:
        meta["parent_job_id"] = parent_job_id
        meta["tile_start"] = tile_start
        meta["tile_end"] = (tile_start or 1) + 1655
    row = ProteinAnalysis(
        id=id, input_type="uniprot", input_value=acc, cohort_tranche=5,
        pdb_path=pdb, mean_plddt=plddt, meta=meta,
    )
    session.add(row)
    return row


def _live_shape_parent(id=2817, acc="Q9P273"):
    """One row in the shape Fly serves: live tag, live path, no ``stitched.pdb`` anywhere."""
    return ProteinAnalysis(
        id=id, input_type="uniprot", input_value=acc, cohort_tranche=5,
        pdb_path=f"/data/artifacts/{id}/structure.pdb", mean_plddt=61.07,
        meta={"hold48_kind": LIVE_TAG, "span_aa": 2368},
    )


# ------------------------------------------------------- the vocabulary itself


def test_the_live_tag_is_in_the_repo_string_table():
    """⚠⚠ THE ROOT CAUSE, asserted where it can go red. ``parent_stitched`` appeared
    **zero** times in the repo at `8e53af5` while sitting on 45 live rows."""
    assert HOLD48_KIND_PARENT_STITCHED == LIVE_TAG
    assert HOLD48_PARENT_KINDS == frozenset({HOLD48_KIND_PARENT, HOLD48_KIND_PARENT_STITCHED})
    assert is_parent_kind(HOLD48_KIND_PARENT), "the emit-side spelling must keep working"
    assert is_parent_kind(LIVE_TAG), "the ops-side spelling is what Fly carries"
    # ⚠ and the set stays a set: a tile, a mucin and an absent tag are not parents
    for other in ("tile", "mucin", "", None, "parent_kabsch"):
        assert not is_parent_kind(other), other


def test_the_second_signal_is_the_artifact_name_write_stitched_produces():
    """Belt and suspenders (D-134 decision 2): a meta string drifted once and may drift
    again; the basename is written by this repo's own ``write_stitched``.

    ⚠ No path is invented here. Only the basename of a path **already stored on the row**
    is read — the D-034 §2a rule that no surface reconstructs a location.
    """
    from core.hold48_stitch import write_stitched  # the writer of the name we key on

    assert STITCHED_PDB_BASENAME == "stitched.pdb"
    assert f'"{STITCHED_PDB_BASENAME}"' in Path(
        ROOT / "core" / "hold48_stitch.py"
    ).read_text(encoding="utf-8").replace("'", '"'), (
        "the basename this reader keys on must be the one write_stitched writes"
    )
    assert callable(write_stitched)
    assert is_stitched_artifact_path("/data/artifacts/2817/stitched.pdb")
    assert not is_stitched_artifact_path("/data/artifacts/2817/structure.pdb")
    assert not is_stitched_artifact_path(None)
    assert not is_stitched_artifact_path("")


# ------------------------------------------------- the fixture that was mis-typed


def test_a_live_shape_stitched_parent_classifies_as_assembled():
    """⚠⚠ THE TRIPWIRE. Red at `8e53af5`: this row came back ``single-pass``."""
    row = _live_shape_parent()
    assert is_census_parent_row(row) is True
    assert is_assembled_parent_row(row) is True
    assert is_census_tile_row(row) is False
    picked = choose_census_representative([row])
    assert picked is not None
    assert picked[0].id == 2817
    assert picked[1] == "assembled", "a stitched parent is not a single forward pass"


def test_the_named_live_rows_open_as_assembled_end_to_end():
    """2817 / 2929 / 3356 — the three the defect report names, through ``list_census``
    and ``get_census_detail`` rather than through the predicate alone."""
    eng = _engine()
    with Session(eng) as s:
        for pid, acc in ((2817, "Q9P273"), (2929, "Q9UMZ3"), (3356, "P11717")):
            _add(s, id=pid, acc=acc, kind=LIVE_TAG,
                 pdb=f"/data/artifacts/{pid}/structure.pdb", plddt=61.07)
            _add(s, id=pid + 10000, acc=acc, kind="tile", pdb=f"/tmp/{acc}/t1.pdb",
                 plddt=70.0, parent_job_id=pid, tile_start=1, span_aa=1656)
        s.commit()
    rows = {r["accession"]: r for r in list_census(eng) if r.get("id") is not None}
    for pid, acc in ((2817, "Q9P273"), (2929, "Q9UMZ3"), (3356, "P11717")):
        assert rows[acc]["id"] == pid, "the parent is the row, never its tile"
        assert rows[acc]["structure_kind"] == "assembled"
        assert rows[acc]["structure_kind_label"] == "assembled (provisional)"
        detail = get_census_detail(eng, pid)
        assert detail["structure_kind"] == "assembled"
        # ⚠ still provisional: the fix restores the identity, it does not solve the seam
        assert "seam not solved" in detail["assembler_note"]


def test_the_fold_type_chips_stop_reading_zero():
    """The success condition, in the shape the chips compute: `structure_kind == 'assembled'`
    over census ROWS. Seeded from D-132's measured id set with the tag Fly carries.

    ⚠ 45 here is the fixture's own cardinality, not a re-measurement of the volume. What
    is asserted is that a row per measured parent survives as `assembled` — the count on
    screen is census rows (D-133 am. 1), a different object from the 45 parent JOBS.
    """
    eng = _engine()
    with Session(eng) as s:
        for n, pid in enumerate(sorted(ASSEMBLED_PARENT_IDS)):
            _add(s, id=pid, acc=f"Q{pid:05d}", kind=LIVE_TAG,
                 pdb=f"/data/artifacts/{pid}/structure.pdb", plddt=60.0 + (n % 7))
        s.commit()
    rows = list_census(eng)
    assembled = [r for r in rows if r.get("structure_kind") == "assembled"]
    assert len(assembled) == len(ASSEMBLED_PARENT_IDS) == 45
    assert {r["id"] for r in assembled} == set(ASSEMBLED_PARENT_IDS)
    # ⚠⚠ and the live symptom itself: not one of them may still read single-pass
    assert [r for r in rows if r.get("structure_kind") == "single-pass"] == []


def test_the_detail_assembled_flag_and_the_download_name_follow_the_same_rule():
    """``out['assembled']`` and ``download_stem_for_row`` each held their own copy of the
    one-string test. On Fly the first said `false` — freeing 3Dmol to present winner-tile
    pLDDT as one forward pass — and the second named the download `structure.pdb`."""
    row = _live_shape_parent()
    out = detail_projection(row)
    assert out["assembled"] is True
    assert out["hold48_kind"] == LIVE_TAG
    assert download_stem_for_row(row) == "stitched"


def test_a_drifted_tag_still_loses_to_the_artifact_name():
    """Decision 2 in force: an unknown meta string plus ``stitched.pdb`` is still assembled.
    ⚠ This is the belt, not the braces — the live rows are caught by the tag, above."""
    row = ProteinAnalysis(
        id=9001, input_type="uniprot", input_value="Q9AAAA", cohort_tranche=5,
        pdb_path="/data/artifacts/9001/stitched.pdb", mean_plddt=60.0,
        meta={"hold48_kind": "parent_restitched_v3", "span_aa": 2000},
    )
    assert is_assembled_parent_row(row) is True
    assert choose_census_representative([row])[1] == "assembled"
    assert download_stem_for_row(row) == "stitched"


def test_the_profile_status_becomes_the_assembly_refusal_not_the_features_one():
    """⚠ The second live symptom of the same one-string test: all 45 read
    ``refused_features_incomplete`` on 2026-09-08 — an absence naming the wrong cause.
    Both are refusals, which is why nothing looked wrong. D-120's category is that an
    assembly is **incommensurable** with a bar calibrated on single-pass folds."""
    eng = _engine()
    with Session(eng) as s:
        _add(s, id=2817, acc="Q9P273", kind=LIVE_TAG,
             pdb="/data/artifacts/2817/structure.pdb", plddt=61.07)
        _add(s, id=1901, acc="A0AVI2", kind=None, pdb="/tmp/a0avi2.pdb", plddt=54.14,
             span_aa=43)
        s.commit()
    statuses = census_profile_statuses(eng)
    assert statuses[2817] == "refused_assembled_incommensurable"
    # ⚠ and an ordinary single-pass row is untouched by the widening
    assert statuses[1901] != "refused_assembled_incommensurable"


# ------------------------------------------------ what must NOT have moved


def test_the_emit_side_parent_still_works():
    """``emit_tile_jobs`` writes ``parent`` and keeps writing it. Widening the READER is
    not licence to mint a second write spelling — a test would otherwise be free to ship
    the fix by changing the writer, which does nothing for the rows already on the volume."""
    row = ProteinAnalysis(
        id=2817, input_type="uniprot", input_value="Q9P273", cohort_tranche=5,
        pdb_path="/tmp/q9p273/stitched.pdb", mean_plddt=61.07,
        meta={"hold48_kind": HOLD48_KIND_PARENT, "span_aa": 2368},
    )
    assert is_census_parent_row(row) is True
    assert detail_projection(row)["assembled"] is True
    assert choose_census_representative([row])[1] == "assembled"
    emit = (ROOT / "core" / "hold48.py").read_text(encoding="utf-8")
    assert 'merged_parent["hold48_kind"] = HOLD48_KIND_PARENT' in emit, (
        "the write path stays the single canonical spelling"
    )


def test_tiles_stay_tiles():
    """⚠ A window is never the protein (D-118), and the looser artifact-name signal must
    not be able to promote one. Tile precedence is checked before either parent signal."""
    eng = _engine()
    with Session(eng) as s:
        _add(s, id=5000, acc="Q9ZZZZ", kind=LIVE_TAG, pdb=None, plddt=None)
        _add(s, id=5001, acc="Q9ZZZZ", kind="tile", pdb="/tmp/t1.pdb", plddt=80.0,
             parent_job_id=5000, tile_start=1, span_aa=1656)
        _add(s, id=5002, acc="Q9ZZZZ", kind="tile", pdb="/tmp/t2.pdb", plddt=70.0,
             parent_job_id=5000, tile_start=1529, span_aa=840)
        s.commit()
    rows = [r for r in list_census(eng) if r.get("accession") == "Q9ZZZZ"]
    assert len(rows) == 1
    assert rows[0]["id"] == 5000, "the tiles-only PARENT is the row, not a tile"
    assert rows[0]["structure_kind"] == "tiles_only"
    assert rows[0]["folded"] is False
    # ⚠ a tile that somehow carries a stitched artifact name is still a tile
    odd = ProteinAnalysis(
        id=5003, input_type="uniprot", input_value="Q9ZZZZ", cohort_tranche=5,
        pdb_path="/tmp/Q9ZZZZ/stitched.pdb", mean_plddt=80.0,
        meta={"hold48_kind": "tile", "parent_job_id": 5000, "tile_start": 1,
              "tile_end": 1656, "span_aa": 1656},
    )
    assert is_census_tile_row(odd) is True
    assert is_census_parent_row(odd) is False
    assert is_assembled_parent_row(odd) is False


def test_mucins_are_unchanged():
    """The 3 named mucins are out_of_class and stay that way (D-111 / D-109 ruling 3)."""
    eng = _engine()
    with Session(eng) as s:
        for n, acc in enumerate(("Q8WXI7", "Q9UKN1", "Q685J3")):
            _add(s, id=6000 + n, acc=acc, kind="mucin", pdb=None, plddt=None)
        s.commit()
    rows = [r for r in list_census(eng) if r.get("id") is not None]
    assert {r["structure_kind"] for r in rows} == {"mucin"}
    for r in rows:
        assert r["folded"] is False
        assert r["not_folded_reason"] == "mucin_out_of_class"
    assert census_summary(eng)["folded"] == 0


def test_an_ordinary_single_pass_row_is_still_single_pass():
    """The widening must not sweep untagged folds into the assembled population."""
    eng = _engine()
    with Session(eng) as s:
        _add(s, id=1901, acc="A0AVI2", kind=None, pdb="/tmp/a0avi2/structure.pdb",
             plddt=54.14, span_aa=43)
        s.commit()
    rows = [r for r in list_census(eng) if r.get("id") == 1901]
    assert rows[0]["structure_kind"] == "single-pass"
    assert rows[0]["folded"] is True


def test_the_fix_is_read_only_and_writes_no_hold48_tag():
    """⚠ Decision 5: read-path only, so the tags already on the volume work as they are.

    A fix that needs 45 live rows rewritten is not a fix until somebody rewrites them, and
    rewriting them is an ops act with its own failure modes — not something a PR discharges.
    Asserted structurally as well as in prose: neither read module mutates a row or commits.
    ⚠ Assigning `hold48_kind` into an outgoing PROJECTION dict is a read; assigning
    `row.meta` is a write. The test has to tell those apart or it is guarding nothing.
    """
    for module in ("app/reads.py", "app/census_profile_read.py"):
        text = (ROOT / module).read_text(encoding="utf-8")
        assert not re.search(r"^\s*\w+\.meta\s*=", text, re.M), f"{module} mutates meta"
        assert not re.search(r"^\s*\w+\.pdb_path\s*=", text, re.M), module
        assert ".commit()" not in text, f"{module} is a read surface"
    # ⚠ and the widening did not sneak a second WRITE spelling into the emit path
    hold48 = (ROOT / "core" / "hold48.py").read_text(encoding="utf-8")
    assert hold48.count("HOLD48_KIND_PARENT_STITCHED") == 2, (
        "the ops spelling is DEFINED and put in the frozenset — and written nowhere"
    )
    entry = _plain(_d134_entry())
    for phrase in ("no rent", "no emit", "no fly write"):
        assert phrase in entry, phrase
    assert "read-path" in entry or "read path" in entry


# ---------------------------------------------------------------- the record


def _plain(text: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[*`]", "", text)).lower()


def _d134_entry() -> str:
    """The D-134 entry only — the log is 24k lines and a substring match anywhere in it
    proves nothing about the entry that is supposed to carry the claim."""
    start = LOG.index("### D-134")
    return LOG[start: LOG.index("### D-133", start)]


def test_d134_entry_exists_before_the_code_claims_it():
    """⚠⚠ Method-note item 7 / the D-062 defect: the check is the ENTRY, never a reference
    to it. A commit message naming D-134 does not discharge the living-documentation rule."""
    assert re.search(
        r"^### D-134 — Stitched parents were invisible", LOG, re.M
    ), "D-134 must be the stitched-parent census-identity entry"
    assert len(re.findall(r"^### D-134", LOG, re.M)) == 1, "exactly one D-134 entry"
    entry = _plain(_d134_entry())
    for cite in ("d-111", "d-118", "d-132", "d-133", "d-016"):
        assert cite in entry, cite


def test_the_entry_names_the_live_miss_with_its_numbers():
    """⚠ D-016: the entry must carry the measurement that disqualified the old code, not a
    recollection of it. The chips read 0 while 45 parents wore the tag."""
    entry = _plain(_d134_entry())
    assert "parent_stitched" in entry, "the tag that was never in the repo"
    assert "45" in entry, "the parents that carried it"
    assert "0 assembled" in entry or "showed 0" in entry, "the count on screen"
    assert "3,463" in entry or "3463" in entry, "the single-pass histogram it hid in"
    assert "/api/census" in entry, "the artefact the numbers came from"
    assert "2026-09-08" in entry


def test_the_entry_keeps_the_out_list_closed():
    """Rental stays CLOSED; no F-004; the D-132 inventory is not re-counted here."""
    entry = _plain(_d134_entry())
    assert "closed" in entry
    assert "not f-004" in entry or "no f-004" in entry
    assert "provisional" in entry, "assembled is still not a solved seam"
    assert "d-109 ruling 7" in entry


def test_the_architecture_doc_records_the_widened_read():
    """Living-doc rule 2: a PR that changes what the served surfaces classify updates
    ARCHITECTURE in the same PR."""
    assert "D-134" in ARCH
    assert "parent_stitched" in ARCH
    assert "test_d134_stitched_parent_identity.py" in ARCH
