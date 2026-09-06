"""D-128-A — linker / seam honesty core. Tests that must be able to go red.

Hermetic fixtures. No Fly. No GPU. No restitch run of the 27. No ops numbers.
Cite Spec §1a / §1b / §2 / §3 / §5 / §11 and the existing ``winning_tile``.
D-125 ``write_kabsch_restitch``, D-126 ``write_confidence_kabsch_restitch``,
D-127 ``write_piecewise_kabsch_restitch``, and the assembler stay
independently callable and byte-untouched.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from core.features import parse_pdb
from core.hold48_confidence_kabsch import write_confidence_kabsch_restitch
from core.hold48_kabsch import (
    KABSCH_RESTITCH_PARENT_IDS,
    REFUSE_OVERLAP_CA_LT_3,
    REFUSE_RMSD_GT_10,
    REFUSE_SINGULAR_COVARIANCE,
    RMSD_REFUSE_ANGSTROM,
    ca_xyz_at_parent,
    kabsch_out_dir,
    write_kabsch_restitch,
)
from core.hold48_linker_seam import (
    ABSENCE_REFUSED_BEFORE_TRANSFORM,
    ABSENCE_TREE_ABSENT,
    ACCEPT_REFUSE_PARENT_IDS,
    ALGORITHM,
    DECISION,
    HONESTY_PATHS,
    LINKER_SEAM_RESTITCH_PARENT_IDS,
    NOT_SUCCESS_TARGET_PARENT_IDS,
    OFFENDING_FROM_D127_REFUSE,
    OFFENDING_FROM_MEASURED_JUMP,
    PATH_CONFIDENCE_KABSCH,
    PATH_KABSCH,
    PATH_LINKER_SEAM,
    PATH_PIECEWISE_KABSCH,
    REFUSE_REASONS,
    REFUSE_SEAM_JUMP_GT_10,
    RMSD_CLASS_PARENT_IDS,
    SEAM_HONESTY_GATE_ANGSTROM,
    SEVEN_LINKER_PARENT_IDS,
    SOURCE_ABSENT,
    SOURCE_MEASURED_FROM_ARTIFACTS,
    SOURCE_READ_FROM_RECORD,
    WEIGHT_EPSILON,
    WINDOW_HALF_WIDTH_AA,
    InventoryRefused,
    SiblingOverwriteRefused,
    build_ops_success_report,
    fit_seam_window,
    honest_for_jump,
    linker_seam_out_dir,
    read_path_seam_honesty,
    refuse_sibling_overwrite,
    seam_max_ca_jump,
    write_linker_seam_restitch,
)
from core.hold48_piecewise_kabsch import (
    REFUSE_LINKER_JUMP_GT_10,
    piecewise_kabsch_out_dir,
    write_piecewise_kabsch_restitch,
)
from core.hold48_stitch import TileFold, stitch_plddt, winning_tile, write_stitched
from scripts.confidence_kabsch_restitch import main as d126_main
from scripts.kabsch_restitch import main as d125_main
from scripts.linker_seam_restitch import main as linker_seam_main
from scripts.piecewise_kabsch_restitch import main as d127_main
from tests.test_d125_kabsch import (
    IN_INVENTORY,
    OUT_OF_INVENTORY,
    _apply,
    _curve_xyz,
    _rot_z,
    _tile,
    _write_manifest,
)

SEVEN = (2938, 2939, 3179, 3190, 3321, 3368, 3566)

# Modules that must stay byte-identical: D-128-A is a fifth sibling, not an edit.
D125_KABSCH_SHA256 = "4c7bb45d04507e2a67ba3600b35d6130d62843ca3bc99c15d3568d5cb105ff6e"
D126_CONF_SHA256 = "d526a856ec8f1ba978a3586f3dfcf4a0ee858da12132499f2db37368efc77f18"
D127_PIECEWISE_SHA256 = "ad48b2be577b987466274000c508a621792bc029bb9e087eec94ba7237f13e04"

R_SEAM = _rot_z(40)
T_SEAM = (12.0, -7.5, 3.0)

MODULE = Path(__file__).resolve().parent.parent / "core" / "hold48_linker_seam.py"
CLI = Path(__file__).resolve().parent.parent / "scripts" / "linker_seam_restitch.py"


def _moved_pair(
    *,
    a_span: tuple[int, int] = (1, 50),
    b_span: tuple[int, int] = (20, 75),
    extra_cb: bool = True,
):
    """Reference tile A and a rigidly displaced moving tile B on the same curve.

    B is the *same* backbone as A over the shared residues, moved by one rigid
    ``R, t`` — so a window fit can recover it exactly and the pre-transform seam
    jump is far over the gate.
    """
    a_xyz = [_curve_xyz(i - 1) for i in range(a_span[0], a_span[1] + 1)]
    b_xyz = [_apply(R_SEAM, T_SEAM, _curve_xyz(i - 1)) for i in range(b_span[0], b_span[1] + 1)]
    a = _tile(a_span[0], a_xyz, plddt=40.0, extra_cb=extra_cb)
    b = _tile(b_span[0], b_xyz, plddt=90.0, extra_cb=extra_cb)
    return a, b


def _coincident_pair(*, a_span=(1, 50), b_span=(20, 75)):
    """Two tiles that already agree on the overlap: nothing offends this seam."""
    a_xyz = [_curve_xyz(i - 1) for i in range(a_span[0], a_span[1] + 1)]
    b_xyz = [_curve_xyz(i - 1) for i in range(b_span[0], b_span[1] + 1)]
    return (
        _tile(a_span[0], a_xyz, plddt=40.0, extra_cb=True),
        _tile(b_span[0], b_xyz, plddt=90.0, extra_cb=True),
    )


def _tree_digest(root: Path) -> dict[str, str]:
    return {
        str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(root.rglob("*"))
        if p.is_file()
    }


def _honesty_rows(result, path_name: str) -> list:
    return [row for row in result.honesty if row.path == path_name]


# ── T-1153 — window refuse table (Spec §2) ───────────────────────────────────


def test_window_n_ca_lt_3_refuses(tmp_path):
    """Fewer than three corresponding Cα in the window: no fit, no pose."""
    a = _tile(1, [_curve_xyz(i) for i in range(5)], plddt=90.0)
    b_xyz = [_apply(R_SEAM, (60.0, -40.0, 25.0), _curve_xyz(i)) for i in range(3, 8)]
    b = _tile(4, b_xyz, plddt=80.0)  # overlap 4–5 → 2 corresponding Cα
    result = write_linker_seam_restitch(
        [a, b], 8, tmp_path, parent_job_id=IN_INVENTORY, tile_job_ids=[3673, 3630]
    )
    seam = result.seams[0]
    assert seam.n_ca == 2
    assert seam.refuse_reason == REFUSE_OVERLAP_CA_LT_3
    assert seam.rmsd_angstrom is None
    assert seam.max_ca_jump_angstrom is None
    assert result.accepted is False
    assert result.repaired is False
    assert result.stitched is None
    assert not (result.out_dir / "stitched.pdb").exists()
    assert not (result.out_dir / "tile2_transformed.pdb").exists()
    # The refuse is still a recorded outcome.
    assert (result.out_dir / "seams.jsonl").is_file()
    assert (result.out_dir / "seam_honesty.jsonl").is_file()


def test_window_rmsd_gt_10_refuses(tmp_path):
    a_xyz = [_curve_xyz(i) for i in range(8)]
    b_xyz = [_curve_xyz(i) for i in range(5, 12)]
    b_xyz[0] = (b_xyz[0][0] + 25.0, b_xyz[0][1], b_xyz[0][2])
    b_xyz[1] = (b_xyz[1][0] - 8.0, b_xyz[1][1] + 22.0, b_xyz[1][2])
    b_xyz[2] = (b_xyz[2][0], b_xyz[2][1] - 18.0, b_xyz[2][2] + 20.0)
    a = _tile(1, a_xyz, plddt=90.0)
    b = _tile(6, b_xyz, plddt=80.0)
    result = write_linker_seam_restitch([a, b], 12, tmp_path, parent_job_id=IN_INVENTORY)
    seam = result.seams[0]
    assert seam.n_ca >= 3
    assert seam.rmsd_angstrom is not None
    assert seam.rmsd_angstrom > RMSD_REFUSE_ANGSTROM
    assert seam.refuse_reason == REFUSE_RMSD_GT_10
    assert seam.max_ca_jump_angstrom is None  # refused before any transform
    assert result.accepted is False
    assert not (result.out_dir / "stitched.pdb").exists()


def test_window_singular_covariance_refuses(tmp_path):
    line_a = [(i * 3.8, 0.0, 0.0) for i in range(6)]
    line_b = [(i * 3.8 + 40.0, 0.0, 0.0) for i in range(2, 8)]
    a = _tile(1, line_a, plddt=90.0)
    b = _tile(3, line_b, plddt=80.0)
    result = write_linker_seam_restitch([a, b], 8, tmp_path, parent_job_id=IN_INVENTORY)
    seam = result.seams[0]
    assert seam.n_ca >= 3
    assert seam.refuse_reason == REFUSE_SINGULAR_COVARIANCE
    assert seam.rmsd_angstrom is None
    assert result.accepted is False
    assert not (result.out_dir / "tile2_transformed.pdb").exists()


# ── T-1154 — seam_jump_gt_10, the D-128 refuse (Spec §2) ─────────────────────


def test_post_apply_whole_seam_jump_gt_10_refuses(tmp_path):
    """A window that lands while the rest of the seam flies apart is not a join.

    Overlap 21–100 is wider than the ±32 aa window, so residues outside it keep
    their displaced coordinates. The window's weighted RMSD passes; the seam
    does not. That is the fail-closed case the Spec expects to be common — and
    it is why 0-of-7 repaired is an allowed outcome.
    """
    a, b = _moved_pair(a_span=(1, 100), b_span=(21, 120))
    result = write_linker_seam_restitch([a, b], 120, tmp_path, parent_job_id=IN_INVENTORY)
    seam = result.seams[0]
    assert seam.offending_seam_source == OFFENDING_FROM_MEASURED_JUMP
    assert seam.n_ca is not None and seam.n_ca >= 3
    assert seam.rmsd_angstrom is not None
    assert seam.rmsd_angstrom <= RMSD_REFUSE_ANGSTROM  # the window itself fitted
    assert seam.max_ca_jump_angstrom is not None
    assert seam.max_ca_jump_angstrom > RMSD_REFUSE_ANGSTROM
    assert seam.refuse_reason == REFUSE_SEAM_JUMP_GT_10
    assert result.accepted is False
    assert result.stitched is None
    assert not (result.out_dir / "stitched.pdb").exists()
    assert not (result.out_dir / "tile2_transformed.pdb").exists()
    # Fail closed on the honesty surface too: this seam is dishonest, not unknown.
    row = _honesty_rows(result, PATH_LINKER_SEAM)[0]
    assert row.honest is False
    assert row.max_ca_jump_angstrom == pytest.approx(seam.max_ca_jump_angstrom)


def test_seam_jump_reason_is_not_d127s_linker_reason():
    """Different measurement of a different algorithm — never conflated."""
    assert REFUSE_SEAM_JUMP_GT_10 == "seam_jump_gt_10"
    assert REFUSE_LINKER_JUMP_GT_10 == "linker_jump_gt_10"
    assert REFUSE_SEAM_JUMP_GT_10 != REFUSE_LINKER_JUMP_GT_10
    assert REFUSE_LINKER_JUMP_GT_10 not in REFUSE_REASONS
    assert REFUSE_REASONS == frozenset(
        {
            REFUSE_OVERLAP_CA_LT_3,
            REFUSE_RMSD_GT_10,
            REFUSE_SINGULAR_COVARIANCE,
            REFUSE_SEAM_JUMP_GT_10,
        }
    )


# ── T-1155 — the ±32 aa window is pinned and only it moves (Spec §1b) ────────


def test_window_half_width_is_32_and_only_that_window_moves(tmp_path):
    """W = 32 is a pinned v1 default. This test goes red if the window changes.

    Overlap is 20–50, so the centre is 35 and the window is [3, 67]. Residue 67
    is moved; residue 68 is not, and inherits nothing.
    """
    assert WINDOW_HALF_WIDTH_AA == 32
    a, b = _moved_pair(a_span=(1, 50), b_span=(20, 75))
    before_68 = ca_xyz_at_parent(b, 68)
    result = write_linker_seam_restitch(
        [a, b], 75, tmp_path, parent_job_id=IN_INVENTORY, tile_job_ids=[3673, 3630]
    )
    seam = result.seams[0]
    assert seam.seam_centre == 35
    assert seam.window_start == 35 - WINDOW_HALF_WIDTH_AA
    assert seam.window_end == 35 + WINDOW_HALF_WIDTH_AA
    assert result.accepted is True
    moved = result.tiles[1]

    inside = ca_xyz_at_parent(moved, 67)
    expect_inside = _curve_xyz(66)
    assert inside is not None
    for got, want in zip(inside, expect_inside):
        assert got == pytest.approx(want, abs=0.05)

    outside = ca_xyz_at_parent(moved, 68)
    assert outside is not None and before_68 is not None
    for got, want in zip(outside, before_68):
        assert got == pytest.approx(want, abs=1e-3)
    # …and it is genuinely still in the moved frame, tens of Å from the reference.
    untouched_gap = max(abs(o - r) for o, r in zip(outside, _curve_xyz(67)))
    assert untouched_gap > RMSD_REFUSE_ANGSTROM

    payload = json.loads((result.out_dir / "seams.jsonl").read_text().splitlines()[0])
    assert payload["window_half_width_aa"] == 32
    assert payload["window_start"] == 3
    assert payload["window_end"] == 67


def test_window_bounds_are_not_tuned_per_parent(tmp_path):
    """A second window size is out of v1: the fit is a function of W alone."""
    a, b = _moved_pair(a_span=(1, 100), b_span=(21, 120))
    wide = fit_seam_window(a, b, 60, half_width=64)
    pinned = fit_seam_window(a, b, 60)
    assert pinned.window_end - pinned.window_start == 2 * WINDOW_HALF_WIDTH_AA
    assert wide.n_ca > pinned.n_ca
    # The writer never exposes the wider window as a per-parent default.
    result = write_linker_seam_restitch([a, b], 120, tmp_path, parent_job_id=IN_INVENTORY)
    assert result.seams[0].window_end - result.seams[0].window_start == 2 * WINDOW_HALF_WIDTH_AA


# ── T-1156 — accept feeds the existing assembler (Spec §1b step 6) ───────────


def test_full_accept_feeds_winning_tile_and_pae_stays_null(tmp_path):
    a, b = _moved_pair(a_span=(1, 50), b_span=(20, 65))
    result = write_linker_seam_restitch(
        [a, b], 65, tmp_path, parent_job_id=IN_INVENTORY, tile_job_ids=[3673, 3630]
    )
    assert result.accepted is True
    assert result.repaired is True
    assert result.stitched is not None
    assert result.out_dir == linker_seam_out_dir(tmp_path, IN_INVENTORY)
    assert (result.out_dir / "tile2_transformed.pdb").is_file()
    seam = result.seams[0]
    assert seam.refuse_reason is None
    assert seam.max_ca_jump_angstrom is not None
    assert seam.max_ca_jump_angstrom <= RMSD_REFUSE_ANGSTROM
    assert winning_tile(result.tiles, 30) is result.tiles[1]
    assert stitch_plddt(result.tiles, 65)[29] == 90.0

    pae = json.loads((result.out_dir / "stitched_pae.json").read_text(encoding="utf-8"))
    assert pae[0][64] is None
    assert pae[0][64] != 0
    assert "null" in json.dumps(pae)

    cbs = [atom for atom in parse_pdb(Path(result.stitched["pdb"]).read_text()) if atom.name == "CB"]
    assert cbs, "the window transform must keep all-atom records, not just Cα"

    prov = json.loads((result.out_dir / "provenance.json").read_text())
    assert prov["algorithm"] == ALGORITHM
    assert prov["decision"] == DECISION
    assert prov["window_half_width_aa"] == 32
    assert prov["weight_epsilon"] == WEIGHT_EPSILON
    assert prov["rmsd_refuse_angstrom"] == 10.0
    assert prov["seam_honesty_gate_angstrom"] == 10.0
    assert prov["no_trim_loop"] is True
    assert prov["no_domain_pieces_fitted"] is True
    assert prov["no_linker_inherit"] is True
    assert prov["served_path"] == "assembler"
    assert prov["seams_solved"] is False
    assert prov["repaired"] is True


def test_offending_seam_can_come_from_the_prior_d127_refuse(tmp_path):
    """Spec §1b step 1: the D-127 refuse record may name the seam."""
    a, b = _coincident_pair(a_span=(1, 50), b_span=(20, 65))
    tree = piecewise_kabsch_out_dir(tmp_path, IN_INVENTORY)
    tree.mkdir(parents=True)
    (tree / "seams.jsonl").write_text(
        json.dumps(
            {
                "moving_tile_index": 2,
                "reference_tile_index": 1,
                "max_ca_jump_angstrom": 41.5,
                "linker_n": 4,
                "max_linker_ca_jump": 41.5,
                "refuse_reason": REFUSE_LINKER_JUMP_GT_10,
            }
        )
        + "\n",
        encoding="utf-8",
    )
    result = write_linker_seam_restitch([a, b], 65, tmp_path, parent_job_id=IN_INVENTORY)
    seam = result.seams[0]
    assert seam.offending_seam_source == OFFENDING_FROM_D127_REFUSE
    assert seam.window_start is not None and seam.n_ca is not None
    assert result.accepted is True
    # D-127's reason named the seam; it never becomes a D-128 refuse reason.
    assert seam.refuse_reason is None
    rows = _honesty_rows(result, PATH_PIECEWISE_KABSCH)
    assert rows[0].max_ca_jump_angstrom == pytest.approx(41.5)
    assert rows[0].honest is False
    assert rows[0].linker_n == 4


def test_no_offending_seam_is_a_recorded_absence_not_a_repair(tmp_path):
    """Nothing over the gate and no D-127 record: recorded, not silently skipped."""
    a, b = _coincident_pair(a_span=(1, 50), b_span=(20, 65))
    result = write_linker_seam_restitch([a, b], 65, tmp_path, parent_job_id=IN_INVENTORY)
    seam = result.seams[0]
    assert seam.offending_seam_source is None
    assert seam.window_start is None
    assert seam.max_ca_jump_angstrom is not None
    assert seam.max_ca_jump_angstrom <= RMSD_REFUSE_ANGSTROM
    assert result.accepted is True
    assert result.repaired is False, "an accept with zero transforms is not a repair"
    assert not (result.out_dir / "tile2_transformed.pdb").exists()
    payload = json.loads((result.out_dir / "seams.jsonl").read_text().splitlines()[0])
    assert payload["no_offending_seam"] is True
    assert payload["offending_seam_source"] is None
    assert json.loads((result.out_dir / "provenance.json").read_text())["repaired"] is False


# ── T-1157 — §1a honesty rows, per path, per seam ────────────────────────────


def _all_four_trees(tmp_path):
    """Run D-125, D-126 and D-127 on one pair so their trees exist to be read."""
    a, b = _moved_pair(a_span=(1, 50), b_span=(20, 65))
    assembler = tmp_path / "assembler"
    write_stitched([a, b], 65, assembler)
    d125 = write_kabsch_restitch(
        [a, b], 65, tmp_path, parent_job_id=IN_INVENTORY, assembler_dir=assembler
    )
    d126 = write_confidence_kabsch_restitch(
        [a, b], 65, tmp_path, parent_job_id=IN_INVENTORY,
        assembler_dir=assembler, d125_dir=d125.out_dir,
    )
    d127 = write_piecewise_kabsch_restitch(
        [a, b], 65, tmp_path, parent_job_id=IN_INVENTORY,
        assembler_dir=assembler, d125_dir=d125.out_dir, d126_dir=d126.out_dir,
        domain_intervals=[(1, 65)],
    )
    return a, b, assembler, d125, d126, d127


def test_honesty_rows_exist_for_every_path_and_name_their_source(tmp_path):
    a, b, assembler, d125, d126, d127 = _all_four_trees(tmp_path)
    result = write_linker_seam_restitch(
        [a, b], 65, tmp_path, parent_job_id=IN_INVENTORY,
        assembler_dir=assembler, d125_dir=d125.out_dir,
        d126_dir=d126.out_dir, d127_dir=d127.out_dir,
    )
    paths = {row.path for row in result.honesty}
    assert paths == set(HONESTY_PATHS)
    for row in result.honesty:
        assert row.honest is honest_for_jump(row.max_ca_jump_angstrom)

    # D-125's seams.jsonl carries no jump at all, so the row is MEASURED from the
    # artifacts D-125 itself wrote — not copied, not invented, not skipped.
    kabsch_row = _honesty_rows(result, PATH_KABSCH)[0]
    assert kabsch_row.source == SOURCE_MEASURED_FROM_ARTIFACTS
    assert kabsch_row.max_ca_jump_angstrom is not None
    assert kabsch_row.honest is honest_for_jump(kabsch_row.max_ca_jump_angstrom)
    assert "max_ca_jump_angstrom" not in (d125.out_dir / "seams.jsonl").read_text()

    # D-126 / D-127 record the jump themselves, so those rows are reads.
    for path_name in (PATH_CONFIDENCE_KABSCH, PATH_PIECEWISE_KABSCH):
        row = _honesty_rows(result, path_name)[0]
        assert row.source == SOURCE_READ_FROM_RECORD
        assert row.max_ca_jump_angstrom is not None

    # Only D-127 defines linkers; the others carry absent linker fields, not 0.
    written = [
        json.loads(line)
        for line in (result.out_dir / "seam_honesty.jsonl").read_text().splitlines()
    ]
    by_path = {row["path"]: row for row in written}
    assert by_path[PATH_PIECEWISE_KABSCH]["linker_fields_applicable"] is True
    for path_name in (PATH_KABSCH, PATH_CONFIDENCE_KABSCH, PATH_LINKER_SEAM):
        assert by_path[path_name]["linker_fields_applicable"] is False
        assert by_path[path_name]["linker_n"] is None
        assert by_path[path_name]["max_linker_ca_jump"] is None
    for row in written:
        assert row["honesty_gate_angstrom"] == 10.0


def test_absent_tree_is_an_honest_absence_with_a_reason_never_a_zero(tmp_path):
    a, b = _moved_pair(a_span=(1, 50), b_span=(20, 65))
    result = write_linker_seam_restitch([a, b], 65, tmp_path, parent_job_id=IN_INVENTORY)
    for path_name in (PATH_KABSCH, PATH_CONFIDENCE_KABSCH, PATH_PIECEWISE_KABSCH):
        rows = _honesty_rows(result, path_name)
        assert len(rows) == 1
        row = rows[0]
        assert row.source == SOURCE_ABSENT
        assert row.absence_reason == ABSENCE_TREE_ABSENT
        assert row.max_ca_jump_angstrom is None
        assert row.honest is None, "unknown is not honest"
        assert row.honest is honest_for_jump(row.max_ca_jump_angstrom)
        assert row.max_ca_jump_angstrom != 0.0
    text = (result.out_dir / "seam_honesty.jsonl").read_text()
    assert '"max_ca_jump_angstrom": null' in text
    assert '"honest": null' in text
    written = [json.loads(line) for line in text.splitlines()]
    for row in written:
        # A null jump serialises as null and never as a number — 0.0 would read
        # as a perfectly held seam for a path whose tree is not even there.
        if row["source"] == SOURCE_ABSENT:
            assert row["max_ca_jump_angstrom"] is None
            assert row["honest"] is None
        assert (row["honest"] is None) == (row["max_ca_jump_angstrom"] is None)


def test_refused_prior_path_is_unknown_not_honest(tmp_path):
    """A path that refused before any transform has a null jump, so honest is null."""
    tree = piecewise_kabsch_out_dir(tmp_path, IN_INVENTORY)
    tree.mkdir(parents=True)
    (tree / "seams.jsonl").write_text(
        json.dumps(
            {
                "moving_tile_index": 2,
                "reference_tile_index": 1,
                "max_ca_jump_angstrom": None,
                "linker_n": None,
                "max_linker_ca_jump": None,
                "refuse_reason": "rmsd_gt_10",
            }
        )
        + "\n",
        encoding="utf-8",
    )
    rows = read_path_seam_honesty(tmp_path, IN_INVENTORY, PATH_PIECEWISE_KABSCH)
    assert len(rows) == 1
    assert rows[0].max_ca_jump_angstrom is None
    assert rows[0].honest is None
    assert rows[0].source == SOURCE_ABSENT
    assert rows[0].absence_reason == ABSENCE_REFUSED_BEFORE_TRANSFORM
    assert rows[0].refuse_reason == "rmsd_gt_10"


def test_honesty_gate_is_the_existing_ten_angstrom_gate_and_does_not_loosen():
    assert SEAM_HONESTY_GATE_ANGSTROM == RMSD_REFUSE_ANGSTROM == 10.0
    assert honest_for_jump(0.0) is True
    assert honest_for_jump(10.0) is True
    assert honest_for_jump(10.0000001) is False
    assert honest_for_jump(68.0) is False
    assert honest_for_jump(None) is None


def test_reading_prior_trees_never_writes_to_them(tmp_path):
    a, b, assembler, d125, d126, d127 = _all_four_trees(tmp_path)
    before = {
        name: _tree_digest(path)
        for name, path in (
            ("assembler", assembler),
            ("kabsch", d125.out_dir),
            ("confidence_kabsch", d126.out_dir),
            ("piecewise_kabsch", d127.out_dir),
        )
    }
    write_linker_seam_restitch(
        [a, b], 65, tmp_path, parent_job_id=IN_INVENTORY,
        assembler_dir=assembler, d125_dir=d125.out_dir,
        d126_dir=d126.out_dir, d127_dir=d127.out_dir,
    )
    after = {
        name: _tree_digest(path)
        for name, path in (
            ("assembler", assembler),
            ("kabsch", d125.out_dir),
            ("confidence_kabsch", d126.out_dir),
            ("piecewise_kabsch", d127.out_dir),
        )
    }
    assert after == before
    for tree in (d125.out_dir, d126.out_dir, d127.out_dir):
        assert not (tree / "seam_honesty.jsonl").exists()


# ── T-1158 — fifth sibling tree, no overwrite, prior paths callable ──────────


def test_linker_seam_dir_does_not_overwrite_the_four_existing_paths(tmp_path):
    a, b, assembler, d125, d126, d127 = _all_four_trees(tmp_path)
    result = write_linker_seam_restitch(
        [a, b], 65, tmp_path, parent_job_id=IN_INVENTORY,
        assembler_dir=assembler, d125_dir=d125.out_dir,
        d126_dir=d126.out_dir, d127_dir=d127.out_dir,
    )
    assert result.out_dir == linker_seam_out_dir(tmp_path, IN_INVENTORY)
    for other in (assembler, d125.out_dir, d126.out_dir, d127.out_dir):
        assert result.out_dir.resolve() != other.resolve()
    refuse_sibling_overwrite(result.out_dir, assembler, d125.out_dir, d126.out_dir, d127.out_dir)
    for target in (assembler, d125.out_dir, d126.out_dir, d127.out_dir):
        with pytest.raises(SiblingOverwriteRefused):
            refuse_sibling_overwrite(target, assembler, d125.out_dir, d126.out_dir, d127.out_dir)


def test_only_a_linker_seam_directory_may_receive_d128_artifacts(tmp_path):
    """The catch-all: a caller that names no prior dir still cannot write elsewhere.

    Comparing against the four known dirs only refuses the four we were told
    about. The path guard is what stops a D-128 write landing on a tree nobody
    passed in — including a future fifth caller's own mistake.
    """
    with pytest.raises(SiblingOverwriteRefused):
        refuse_sibling_overwrite(tmp_path / "kabsch" / str(IN_INVENTORY))
    with pytest.raises(SiblingOverwriteRefused):
        refuse_sibling_overwrite(tmp_path / "confidence_kabsch" / str(IN_INVENTORY))
    with pytest.raises(SiblingOverwriteRefused):
        refuse_sibling_overwrite(tmp_path / "piecewise_kabsch" / str(IN_INVENTORY))
    with pytest.raises(SiblingOverwriteRefused):
        refuse_sibling_overwrite(tmp_path / "assembler")
    with pytest.raises(SiblingOverwriteRefused):
        refuse_sibling_overwrite(tmp_path)
    # The one shape that is allowed needs no prior dirs to be recognised.
    refuse_sibling_overwrite(linker_seam_out_dir(tmp_path, IN_INVENTORY))


def test_d128_writes_nothing_outside_its_own_tree(tmp_path):
    """Served stays assembler: this path cannot flip or touch anything it reads."""
    a, b, assembler, d125, d126, d127 = _all_four_trees(tmp_path)
    before = {
        str(p.relative_to(tmp_path)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(tmp_path.rglob("*"))
        if p.is_file()
    }
    write_linker_seam_restitch(
        [a, b], 65, tmp_path, parent_job_id=IN_INVENTORY,
        assembler_dir=assembler, d125_dir=d125.out_dir,
        d126_dir=d126.out_dir, d127_dir=d127.out_dir,
    )
    after = {
        str(p.relative_to(tmp_path)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(tmp_path.rglob("*"))
        if p.is_file()
    }
    changed = {k for k in after if before.get(k) != after[k]}
    assert changed, "the D-128 run must write its own tree"
    assert all(k.startswith("linker_seam/") for k in changed), changed
    assert set(before) - set(after) == set()


def test_prior_paths_and_the_assembler_stay_independently_callable(tmp_path):
    a, b, assembler, d125, d126, d127 = _all_four_trees(tmp_path)
    d128 = write_linker_seam_restitch(
        [a, b], 65, tmp_path, parent_job_id=IN_INVENTORY,
        assembler_dir=assembler, d125_dir=d125.out_dir,
        d126_dir=d126.out_dir, d127_dir=d127.out_dir,
    )
    assert (assembler / "stitched.pdb").is_file()
    assert d125.out_dir == kabsch_out_dir(tmp_path, IN_INVENTORY)
    assert d128.accepted is True

    man = tmp_path / "tiles.json"
    _write_manifest(tmp_path, man, parent_job_id=IN_INVENTORY, tiles=[a, b], length=65)
    raw = json.loads(man.read_text(encoding="utf-8"))
    raw["domain_intervals"] = [[1, 65]]
    man.write_text(json.dumps(raw, indent=2), encoding="utf-8")
    assert d125_main(["--manifest", str(man), "--out-root", str(tmp_path / "ops125")]) in (0, 1)
    assert d126_main(["--manifest", str(man), "--out-root", str(tmp_path / "ops126")]) in (0, 1)
    assert d127_main(["--manifest", str(man), "--out-root", str(tmp_path / "ops127")]) in (0, 1)
    assert linker_seam_main(["--manifest", str(man), "--out-root", str(tmp_path / "ops128")]) == 0
    assert (tmp_path / "ops128" / "linker_seam" / str(IN_INVENTORY) / "stitched.pdb").is_file()
    assert (tmp_path / "ops128" / "linker_seam" / str(IN_INVENTORY) / "seam_honesty.jsonl").is_file()


def test_sibling_modules_bytes_stay_pinned():
    """D-128-A is a fifth sibling module, not an edit of the prior three."""
    root = Path(__file__).resolve().parent.parent
    pins = (
        ("hold48_kabsch.py", D125_KABSCH_SHA256),
        ("hold48_confidence_kabsch.py", D126_CONF_SHA256),
        ("hold48_piecewise_kabsch.py", D127_PIECEWISE_SHA256),
    )
    for name, digest in pins:
        assert hashlib.sha256((root / "core" / name).read_bytes()).hexdigest() == digest, name
    stitch = (root / "core" / "hold48_stitch.py").read_text(encoding="utf-8")
    assert "D-128" not in stitch
    assert "linker_seam" not in stitch


def test_all_or_nothing_parent_refuse_clears_partial_success(tmp_path):
    a, b = _moved_pair(a_span=(1, 50), b_span=(20, 65))
    c_xyz = [_curve_xyz(i) for i in range(59, 90)]
    c_xyz[0] = (c_xyz[0][0] + 48.0, c_xyz[0][1], c_xyz[0][2])
    c_xyz[1] = (c_xyz[1][0] - 30.0, c_xyz[1][1] + 44.0, c_xyz[1][2])
    c_xyz[2] = (c_xyz[2][0], c_xyz[2][1] - 36.0, c_xyz[2][2] + 42.0)
    c = _tile(60, c_xyz, plddt=80.0)
    out = linker_seam_out_dir(tmp_path, IN_INVENTORY)
    out.mkdir(parents=True)
    (out / "tile2_transformed.pdb").write_text("STALE\n", encoding="utf-8")
    (out / "stitched.pdb").write_text("STALE\n", encoding="utf-8")
    result = write_linker_seam_restitch([a, b, c], 90, tmp_path, parent_job_id=IN_INVENTORY)
    assert result.accepted is False
    assert any(s.refuse_reason for s in result.seams)
    assert not (result.out_dir / "stitched.pdb").exists()
    assert not list(result.out_dir.glob("tile*_transformed.pdb"))
    assert (result.out_dir / "seams.jsonl").is_file()
    assert (result.out_dir / "seam_honesty.jsonl").is_file()


# ── T-1159 — inventory: the seven, and who is not a success target ───────────


def test_seven_signed_linker_parents_are_the_primary_inventory():
    assert SEVEN_LINKER_PARENT_IDS == frozenset(SEVEN)
    assert len(SEVEN_LINKER_PARENT_IDS) == 7
    assert SEVEN_LINKER_PARENT_IDS <= KABSCH_RESTITCH_PARENT_IDS
    assert SEVEN_LINKER_PARENT_IDS <= LINKER_SEAM_RESTITCH_PARENT_IDS
    assert len(LINKER_SEAM_RESTITCH_PARENT_IDS) == 27
    assert 3356 not in LINKER_SEAM_RESTITCH_PARENT_IDS


def test_3432_stays_accept_refuse_and_the_rmsd_class_is_out_of_primary():
    assert ACCEPT_REFUSE_PARENT_IDS == frozenset({3432})
    assert RMSD_CLASS_PARENT_IDS == frozenset({3272, 3394})
    assert NOT_SUCCESS_TARGET_PARENT_IDS == frozenset({3272, 3394, 3432})
    for pid in NOT_SUCCESS_TARGET_PARENT_IDS:
        assert pid not in SEVEN_LINKER_PARENT_IDS
        assert pid in LINKER_SEAM_RESTITCH_PARENT_IDS, "runnable and recorded, just not a target"


def test_3432_is_recorded_by_the_cli_and_is_never_a_d128_miss(tmp_path):
    """Signed triage: 3432 may be run, but it is not converted and not a miss."""
    a, b = _moved_pair(a_span=(1, 100), b_span=(21, 120))
    man = tmp_path / "tiles.json"
    _write_manifest(tmp_path, man, parent_job_id=3432, tiles=[a, b], length=120)
    rc = linker_seam_main(["--manifest", str(man), "--out-root", str(tmp_path / "ops")])
    assert rc == 1  # recorded refuse, not a crash and not a silent skip
    tree = tmp_path / "ops" / "linker_seam" / "3432"
    assert (tree / "seams.jsonl").is_file()
    assert not (tree / "stitched.pdb").exists()
    report = build_ops_success_report(
        {3432: True}, {3432: True}, {3432: False}, {3432: False},
        d128_repaired={3432: True},
    )
    assert report.repaired_of_seven == 0, "3432 is not one of the seven"


def test_cli_refuses_parent_ids_outside_the_inventory_including_igf2r(tmp_path):
    assert OUT_OF_INVENTORY == 3356
    a, b = _moved_pair(a_span=(1, 50), b_span=(20, 65))
    man = tmp_path / "tiles.json"
    _write_manifest(tmp_path, man, parent_job_id=OUT_OF_INVENTORY, tiles=[a, b], length=65)
    rc = linker_seam_main(
        ["--manifest", str(man), "--out-root", str(tmp_path / "ops"),
         "--parent-id", str(OUT_OF_INVENTORY)]
    )
    assert rc == 2
    assert not (tmp_path / "ops" / "linker_seam" / str(OUT_OF_INVENTORY)).exists()
    with pytest.raises(InventoryRefused):
        write_linker_seam_restitch([a, b], 65, tmp_path, parent_job_id=OUT_OF_INVENTORY)


def test_cli_runs_a_must_hunt_linker_parent_and_reports_honesty(tmp_path):
    a, b = _moved_pair(a_span=(1, 50), b_span=(20, 65))
    man = tmp_path / "tiles.json"
    _write_manifest(tmp_path, man, parent_job_id=2939, tiles=[a, b], length=65)
    assert linker_seam_main(["--manifest", str(man), "--out-root", str(tmp_path / "ops")]) == 0
    tree = tmp_path / "ops" / "linker_seam" / "2939"
    assert (tree / "stitched.pdb").is_file()
    assert linker_seam_main(
        ["--honesty-report", "--out-root", str(tmp_path / "ops"), "--parent-id", "2939"]
    ) == 0
    assert linker_seam_main(
        ["--honesty-report", "--out-root", str(tmp_path / "ops"), "--parent-id", "3356"]
    ) == 2


# ── T-1160 — ops report + the fences that keep this from becoming D-127 ──────


def test_ops_report_names_drops_and_allows_zero_of_seven(tmp_path):
    d125 = {pid: True for pid in KABSCH_RESTITCH_PARENT_IDS}
    d126 = dict(d125)
    d127 = {pid: pid not in SEVEN_LINKER_PARENT_IDS for pid in KABSCH_RESTITCH_PARENT_IDS}
    d128 = dict(d127)
    d128[2817] = False  # a prior PASS that D-128 refuses — a named finding
    rows = [
        {"path": PATH_KABSCH, "max_ca_jump_angstrom": 41.0, "honest": False},
        {"path": PATH_CONFIDENCE_KABSCH, "max_ca_jump_angstrom": 12.0, "honest": False},
        {"path": PATH_PIECEWISE_KABSCH, "max_ca_jump_angstrom": 3.0, "honest": True},
        {"path": PATH_LINKER_SEAM, "max_ca_jump_angstrom": None, "honest": None},
    ]
    report = build_ops_success_report(d125, d126, d127, d128, honesty_rows=rows)
    payload = report.to_json()
    assert payload["n_d125_pass_d128_refuse"] == 8  # the seven plus 2817
    assert payload["n_d126_pass_d128_refuse"] == 8
    assert payload["n_d127_pass_d128_refuse"] == 1  # 2817 only
    assert payload["n_d127_refuse_d128_pass"] == 0
    assert payload["n_d125_pass_d128_refuse_is_named_finding"] is True
    assert payload["n_seams_measured"] == 3
    assert payload["n_dishonest_kabsch"] == 1
    assert payload["n_dishonest_confidence_kabsch"] == 1
    assert payload["n_dishonest_piecewise_kabsch"] == 0
    assert payload["n_dishonest_linker_seam"] == 0
    assert payload["n_honesty_unknown"] == 1
    assert payload["unknown_is_not_honest"] is True
    assert payload["repaired_of_seven"] == 0
    assert payload["repaired_of_seven_source"] == "none_supplied"
    assert payload["zero_of_seven_repaired_is_allowed"] is True
    assert payload["honesty_gate_angstrom"] == 10.0
    assert payload["seams_recorded_is_not_seams_solved"] is True
    assert payload["d128_algorithm"] == ALGORITHM
    assert payload["d128_decision"] == DECISION


def test_repaired_of_seven_counts_only_recorded_repairs():
    d125 = {pid: True for pid in KABSCH_RESTITCH_PARENT_IDS}
    d128 = {pid: True for pid in KABSCH_RESTITCH_PARENT_IDS}
    # Accepted everywhere, but only two of the seven actually moved a window.
    repaired = {2938: True, 3179: True, 2817: True, 3432: True}
    report = build_ops_success_report(d125, d125, d125, d128, d128_repaired=repaired)
    assert report.repaired_of_seven == 2
    assert report.repaired_of_seven_source == "repair_records"
    none_moved = build_ops_success_report(d125, d125, d125, d128, d128_repaired={})
    assert none_moved.repaired_of_seven == 0
    assert none_moved.to_json()["zero_of_seven_repaired_is_allowed"] is True


def test_confusion_report_cli_reads_outcome_files(tmp_path):
    files = {}
    for name, accepted in (("d125", True), ("d126", True), ("d127", False)):
        path = tmp_path / f"{name}.json"
        path.write_text(
            json.dumps({str(pid): accepted for pid in KABSCH_RESTITCH_PARENT_IDS}),
            encoding="utf-8",
        )
        files[name] = path
    d128 = tmp_path / "d128.json"
    d128.write_text(
        json.dumps(
            {
                str(pid): {"accepted": pid in SEVEN_LINKER_PARENT_IDS, "repaired": False}
                for pid in KABSCH_RESTITCH_PARENT_IDS
            }
        ),
        encoding="utf-8",
    )
    rc = linker_seam_main(
        [
            "--confusion-report",
            "--d125-outcomes", str(files["d125"]),
            "--d126-outcomes", str(files["d126"]),
            "--d127-outcomes", str(files["d127"]),
            "--d128-outcomes", str(d128),
        ]
    )
    assert rc == 0
    assert linker_seam_main(["--confusion-report", "--d125-outcomes", str(files["d125"])]) == 2


def test_no_trim_loop_and_no_piecewise_v2_in_the_module():
    """The two temptations the Spec fences off, checked at the symbol level."""
    src = MODULE.read_text(encoding="utf-8")
    for trim_symbol in (
        "trim_highest_residual",
        "TRIM_ROUND_CAP",
        "TRIM_FRACTION",
        "apply_plddt_floor",
        "PLDDT_FLOOR",
    ):
        assert trim_symbol not in src, trim_symbol
    for piecewise_symbol in (
        "DomainInterval",
        "domain_intervals",
        "domain_ends_span_relative",
        "resolve_domain_intervals",
        "fit_domain_piece",
        "inherit_piece_for_residue",
        "residue_transform_map",
        "PieceFit",
        "UNIPROT_CACHE",
    ):
        assert piecewise_symbol not in src, piecewise_symbol
    assert "from core.hold48 import" not in src, "no second domain annotation source"
    assert "No trim" in src or "NO trim" in src
    assert "no linker-inherit" in src
    assert "weighted_kabsch_rotation_translation" in src
    assert "import numpy" not in src and "from numpy" not in src


def test_neither_module_nor_cli_claims_a_seam_is_solved():
    """Method honesty: seams recorded ≠ seams solved."""
    for path in (MODULE, CLI):
        flat = " ".join(path.read_text(encoding="utf-8").lower().split())
        for banned in (
            "seams solved",
            "seams are solved",
            "seam is solved",
            "seams fixed",
            "seam is fixed",
            "seam repaired",
            "full-length af-quality",
            "superimposed structure",
        ):
            assert banned not in flat, f"{path.name}: {banned}"
        assert "not solved" in flat or "recorded, not solved" in flat


def test_epsilon_and_weight_rule_are_pinned():
    assert WEIGHT_EPSILON == 1e-3
    from core.hold48_confidence_kabsch import pair_weight

    assert pair_weight(80.0, 40.0) == pytest.approx(0.40)
    assert pair_weight(0.0, 0.0) == pytest.approx(WEIGHT_EPSILON)


def test_seam_max_ca_jump_is_null_when_there_is_nothing_to_measure():
    a = _tile(1, [_curve_xyz(i) for i in range(5)], plddt=90.0)
    far = _tile(40, [_curve_xyz(i) for i in range(39, 44)], plddt=90.0)
    assert seam_max_ca_jump(a, far) is None, "no shared Cα is null, never 0.0"
    a2, b2 = _moved_pair(a_span=(1, 50), b_span=(20, 65))
    measured = seam_max_ca_jump(a2, b2)
    assert measured is not None and measured > RMSD_REFUSE_ANGSTROM
