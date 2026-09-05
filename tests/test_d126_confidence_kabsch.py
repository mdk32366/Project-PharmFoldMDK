"""D-126-A — overlap-confidence Kabsch core. Tests that must be able to go red.

Hermetic fixtures. No Fly. No GPU. No restitch run of the 27.
Cite amended Spec §1–§3 / §5 / §8 / §10 and existing ``winning_tile``.
D-125 ``write_kabsch_restitch`` and the assembler stay independently callable.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import pytest

from core.features import parse_pdb
from core.hold48_confidence_kabsch import (
    ALGORITHM,
    CONFIDENCE_RESTITCH_PARENT_IDS,
    DECISION,
    PLDDT_FLOOR,
    PRIMARY_FIVE_PARENT_IDS,
    RMSD_REFUSE_ANGSTROM,
    TRIM_ROUND_CAP,
    WEIGHT_EPSILON,
    InventoryRefused,
    SiblingOverwriteRefused,
    apply_plddt_floor,
    build_ops_success_report,
    confidence_kabsch_out_dir,
    fit_overlap_confidence_kabsch,
    pair_weight,
    refuse_sibling_overwrite,
    weighted_kabsch_rotation_translation,
    write_confidence_kabsch_restitch,
)
from core.hold48_kabsch import (
    KABSCH_RESTITCH_PARENT_IDS,
    REFUSE_OVERLAP_CA_LT_3,
    REFUSE_RMSD_GT_10,
    REFUSE_SINGULAR_COVARIANCE,
    kabsch_out_dir,
    kabsch_rotation_translation,
    write_kabsch_restitch,
)
from core.hold48_stitch import TileFold, stitch_plddt, winning_tile, write_stitched
from scripts.confidence_kabsch_restitch import main as confidence_main
from scripts.kabsch_restitch import main as d125_main
from tests.test_d125_kabsch import (
    IN_INVENTORY,
    OUT_OF_INVENTORY,
    _apply,
    _curve_xyz,
    _happy_pair,
    _pdb_from_xyz,
    _rot_z,
    _tile,
    _write_manifest,
)

PRIMARY_FIVE = (2939, 3272, 3368, 3394, 3432)


def _tile_plddt(start: int, xyzs, plddts, *, extra_cb=False) -> TileFold:
    n = len(xyzs)
    assert len(plddts) == n
    t = _tile(start, xyzs, plddt=90.0, extra_cb=extra_cb)
    return TileFold(start=t.start, end=t.end, pdb=t.pdb, plddt=list(plddts), pae=t.pae)


# ── T-1103 weights + ε ───────────────────────────────────────────────────────


def test_pair_weight_is_min_plddt_over_100_clamped_at_epsilon():
    assert WEIGHT_EPSILON == 1e-3
    assert pair_weight(80.0, 40.0) == pytest.approx(0.40)
    assert pair_weight(40.0, 80.0) == pytest.approx(0.40)
    assert pair_weight(100.0, 100.0) == pytest.approx(1.0)
    assert pair_weight(0.0, 0.0) == pytest.approx(WEIGHT_EPSILON)
    assert pair_weight(0.05, 0.05) == pytest.approx(WEIGHT_EPSILON)  # 0.0005 < ε


def test_weighted_fit_uses_min_plddt_weights():
    """A down-weighted outlier pulls less than unweighted Kabsch (T-1103)."""
    Q = [_curve_xyz(i) for i in range(6)]
    R = _rot_z(25)
    t = (3.0, -2.0, 1.0)
    P = [_apply(R, t, q) for q in Q]
    P = list(P)
    P[0] = (P[0][0] + 30.0, P[0][1] - 8.0, P[0][2] + 12.0)
    w = [0.5] + [1.0] * 5  # min(pLDDT)/100 for 50 vs 100
    Rw, tw, w_rmsd, rank_w = weighted_kabsch_rotation_translation(P, Q, w)
    Ru, tu, u_rmsd, rank_u = kabsch_rotation_translation(P, Q)
    assert rank_w >= 2 and rank_u >= 2
    assert w_rmsd < u_rmsd
    # Recovered frame on the five high-weight points is tighter when weighted.
    acc_w = acc_u = 0.0
    for p, q in zip(P[1:], Q[1:]):
        dw = ((Rw[0][0] * p[0] + Rw[0][1] * p[1] + Rw[0][2] * p[2] + tw[0] - q[0]) ** 2
              + (Rw[1][0] * p[0] + Rw[1][1] * p[1] + Rw[1][2] * p[2] + tw[1] - q[1]) ** 2
              + (Rw[2][0] * p[0] + Rw[2][1] * p[1] + Rw[2][2] * p[2] + tw[2] - q[2]) ** 2)
        du = ((Ru[0][0] * p[0] + Ru[0][1] * p[1] + Ru[0][2] * p[2] + tu[0] - q[0]) ** 2
              + (Ru[1][0] * p[0] + Ru[1][1] * p[1] + Ru[1][2] * p[2] + tu[1] - q[1]) ** 2
              + (Ru[2][0] * p[0] + Ru[2][1] * p[1] + Ru[2][2] * p[2] + tu[2] - q[2]) ** 2)
        acc_w += dw
        acc_u += du
    assert acc_w < acc_u


def test_zero_plddt_is_not_a_silent_zero_weight():
    """ε = 1e-3: a 0 pLDDT pair still participates when the floor cannot drop it."""
    a_xyz = [_curve_xyz(i) for i in range(5)]
    b_xyz = [_curve_xyz(i) for i in range(2, 7)]  # overlap parent 3–5 → 3 Cα
    a = _tile_plddt(1, a_xyz, [90, 90, 0.0, 90, 90])
    b = _tile_plddt(3, b_xyz, [0.0, 90, 90, 90, 90])
    # Floor would leave 2 < 3, so the 0-pLDDT pair is kept and weighted at ε.
    moving, ref, used, weights, pairs = __import__(
        "core.hold48_confidence_kabsch", fromlist=["paired_overlap_ca_with_weights"]
    ).paired_overlap_ca_with_weights(a, b)
    assert len(used) == 3
    floored = apply_plddt_floor(moving, ref, used, weights, pairs)
    assert len(floored[0]) == 3  # drop skipped
    assert min(weights) == pytest.approx(WEIGHT_EPSILON)
    fit = fit_overlap_confidence_kabsch(a, b)
    assert fit.n_ca == 3
    assert fit.n_ca_eff == 3


# ── T-1109 floor-then-Kabsch-then-trim ───────────────────────────────────────


def test_plddt_floor_drops_below_50_when_n_ge_3_remains():
    assert PLDDT_FLOOR == 50.0
    a_xyz = [_curve_xyz(i) for i in range(8)]
    R = _rot_z(20)
    t = (5.0, -3.0, 1.5)
    b_local = [_curve_xyz(i) for i in range(5, 12)]
    b_xyz = [_apply(R, t, p) for p in b_local]
    # Overlap parent 6–8 (3 pts). Two extra overlap… wait windows 1–8 and 6–12 → 6,7,8.
    # Need more overlap: A 1–12, B 3–14 with overlap 3–12 = 10 pts.
    a_xyz = [_curve_xyz(i) for i in range(12)]
    b_local = [_curve_xyz(i) for i in range(2, 14)]
    b_xyz = [_apply(R, t, p) for p in b_local]
    a_plddt = [20.0 if i < 4 else 90.0 for i in range(12)]  # parent 1–4 low
    b_plddt = [20.0 if i < 2 else 90.0 for i in range(12)]  # parent 3–4 low on B
    a = _tile_plddt(1, a_xyz, a_plddt)
    b = _tile_plddt(3, b_xyz, b_plddt)
    fit = fit_overlap_confidence_kabsch(a, b)
    assert fit.n_ca == 10  # parent 3–12
    # Floor drops parent 3–4 (min pLDDT 20); 8 remain ≥ 3.
    assert fit.n_ca_eff == 8
    assert fit.accepted
    assert fit.trim_rounds == 0


def test_floor_then_kabsch_then_trim_order_floor_clears_outliers_before_trim():
    """Floor-first: low-pLDDT outliers never enter the trim loop (trim_rounds=0).

    Trim-first would spend rounds dropping those same points. Order is pinned.
    """
    n_a = 20
    a_xyz = [_curve_xyz(i) for i in range(n_a)]
    b_local = [_curve_xyz(i) for i in range(n_a)]
    R = _rot_z(15)
    t = (4.0, 1.0, -2.0)
    b_xyz = [_apply(R, t, p) for p in b_local]
    # First 10 overlap residues: pLDDT 20 and shoved 40 Å (would be high residual).
    a_plddt = [20.0] * 10 + [90.0] * 10
    b_plddt = [20.0] * 10 + [90.0] * 10
    for i in range(10):
        b_xyz[i] = (b_xyz[i][0] + 40.0, b_xyz[i][1] - 15.0, b_xyz[i][2] + 10.0)
    a = _tile_plddt(1, a_xyz, a_plddt)
    b = _tile_plddt(1, b_xyz, b_plddt)
    fit = fit_overlap_confidence_kabsch(a, b)
    assert fit.n_ca == 20
    assert fit.n_ca_eff == 10
    assert fit.trim_rounds == 0
    assert fit.accepted
    assert fit.rmsd_angstrom is not None
    assert fit.rmsd_angstrom <= RMSD_REFUSE_ANGSTROM


# ── T-1104 trim loop ─────────────────────────────────────────────────────────


def test_trim_loop_drops_highest_residual_decile(tmp_path):
    """All pLDDT ≥ 50 so the floor is a no-op; outliers are trimmed (T-1104)."""
    n = 12
    a_xyz = [_curve_xyz(i) for i in range(n)]
    R = _rot_z(12)
    t = (2.0, -1.0, 0.5)
    b_xyz = [_apply(R, t, p) for p in a_xyz]
    # Three high-residual outliers on B — enough to push a no-trim fit over 10 Å.
    for i in (0, 1, 2):
        b_xyz[i] = (b_xyz[i][0] + 35.0, b_xyz[i][1] - 20.0, b_xyz[i][2] + 18.0)
    a = _tile_plddt(1, a_xyz, [90.0] * n)
    b = _tile_plddt(1, b_xyz, [90.0] * n)
    fit = fit_overlap_confidence_kabsch(a, b)
    assert fit.n_ca == n
    assert fit.trim_rounds >= 1
    assert fit.trim_rounds <= TRIM_ROUND_CAP
    assert fit.n_ca_eff < fit.n_ca
    assert fit.n_ca_eff >= 3
    assert fit.accepted
    assert fit.rmsd_angstrom is not None
    assert fit.rmsd_angstrom <= RMSD_REFUSE_ANGSTROM
    result = write_confidence_kabsch_restitch([a, b], n, tmp_path, parent_job_id=IN_INVENTORY)
    assert result.accepted is True
    assert result.seams[0].trim_rounds == fit.trim_rounds


# ── T-1105 refuse table stays at 10 ──────────────────────────────────────────


def _nonrigid_pair(n: int = 16):
    """Many overlap Cα, each shoved differently — trim cannot close under 10 Å."""
    a_xyz = [_curve_xyz(i) for i in range(n)]
    b_xyz = [_curve_xyz(i) for i in range(n)]
    for i in range(n):
        b_xyz[i] = (
            b_xyz[i][0] + 18.0 * math.sin(i + 0.3),
            b_xyz[i][1] + 20.0 * math.cos(i * 1.7),
            b_xyz[i][2] + 16.0 * math.sin(i * 2.2 + 1.0),
        )
    a = _tile(1, a_xyz, plddt=90.0)
    b = _tile(1, b_xyz, plddt=80.0)
    return a, b


def test_refuse_table_stays_at_10_after_trim(tmp_path):
    assert RMSD_REFUSE_ANGSTROM == 10.0
    a, b = _nonrigid_pair(16)
    fit = fit_overlap_confidence_kabsch(a, b)
    assert fit.n_ca >= 3
    assert fit.n_ca_eff >= 3
    assert fit.rmsd_angstrom is not None
    assert fit.rmsd_angstrom > RMSD_REFUSE_ANGSTROM
    assert fit.refuse_reason == REFUSE_RMSD_GT_10
    assert fit.trim_rounds == TRIM_ROUND_CAP
    result = write_confidence_kabsch_restitch([a, b], 16, tmp_path, parent_job_id=IN_INVENTORY)
    assert result.accepted is False
    assert not (result.out_dir / "stitched.pdb").exists()
    assert not (result.out_dir / "tile2_transformed.pdb").exists()
    assert result.seams[0].refuse_reason == REFUSE_RMSD_GT_10


def test_overlap_ca_lt_3_refuses_align(tmp_path):
    a = _tile(1, [_curve_xyz(i) for i in range(5)], plddt=90.0)
    b = _tile(4, [_curve_xyz(i) for i in range(3, 8)], plddt=80.0)  # 2 Cα
    fit = fit_overlap_confidence_kabsch(a, b)
    assert fit.n_ca < 3
    assert fit.refuse_reason == REFUSE_OVERLAP_CA_LT_3
    assert fit.rmsd_angstrom is None
    assert fit.rmsd_full_overlap_angstrom is None
    assert fit.max_ca_jump_angstrom is None
    result = write_confidence_kabsch_restitch(
        [a, b], 8, tmp_path, parent_job_id=IN_INVENTORY, tile_job_ids=[3673, 3630]
    )
    assert result.accepted is False
    assert result.stitched is None
    assert not (result.out_dir / "stitched.pdb").exists()
    assert not (result.out_dir / "tile2_transformed.pdb").exists()


def test_singular_covariance_refuses_align(tmp_path):
    line = [(i * 3.8, 0.0, 0.0) for i in range(6)]
    a = _tile(1, line, plddt=90.0)
    b = _tile(3, [(i * 3.8, 0.0, 0.0) for i in range(2, 8)], plddt=80.0)
    fit = fit_overlap_confidence_kabsch(a, b)
    assert fit.n_ca >= 3
    assert fit.refuse_reason == REFUSE_SINGULAR_COVARIANCE
    assert fit.rmsd_angstrom is None
    result = write_confidence_kabsch_restitch([a, b], 8, tmp_path, parent_job_id=IN_INVENTORY)
    assert result.accepted is False
    assert not (result.out_dir / "tile2_transformed.pdb").exists()


# ── T-1107 anti trim-to-pass lie ─────────────────────────────────────────────


def test_accepted_trim_still_discloses_full_overlap_rmsd_and_max_jump(tmp_path):
    """Trim-to-pass is recorded, not hidden: full-overlap metrics stay on the row."""
    n = 12
    a_xyz = [_curve_xyz(i) for i in range(n)]
    R = _rot_z(12)
    t = (2.0, -1.0, 0.5)
    b_xyz = [_apply(R, t, p) for p in a_xyz]
    for i in (0, 1, 2):
        b_xyz[i] = (b_xyz[i][0] + 35.0, b_xyz[i][1] - 20.0, b_xyz[i][2] + 18.0)
    a = _tile_plddt(1, a_xyz, [90.0] * n)
    b = _tile_plddt(1, b_xyz, [90.0] * n)
    fit = fit_overlap_confidence_kabsch(a, b)
    assert fit.accepted
    assert fit.trim_rounds >= 1
    assert fit.rmsd_full_overlap_angstrom is not None
    assert fit.max_ca_jump_angstrom is not None
    # Full-overlap unweighted RMSD is the disclosure; it may still exceed the gate.
    assert fit.rmsd_full_overlap_angstrom > fit.rmsd_angstrom
    assert fit.max_ca_jump_angstrom > 10.0
    result = write_confidence_kabsch_restitch([a, b], n, tmp_path, parent_job_id=IN_INVENTORY)
    row = json.loads((result.out_dir / "seams.jsonl").read_text().splitlines()[0])
    assert row["rmsd_full_overlap_angstrom"] == pytest.approx(fit.rmsd_full_overlap_angstrom)
    assert row["max_ca_jump_angstrom"] == pytest.approx(fit.max_ca_jump_angstrom)
    assert row["rmsd_angstrom"] <= RMSD_REFUSE_ANGSTROM


def test_rmsd_gt_10_still_records_full_overlap_when_transform_was_attempted():
    a, b = _nonrigid_pair(16)
    fit = fit_overlap_confidence_kabsch(a, b)
    assert fit.refuse_reason == REFUSE_RMSD_GT_10
    assert fit.rmsd_full_overlap_angstrom is not None
    assert fit.max_ca_jump_angstrom is not None


# ── T-1110 all-or-nothing ────────────────────────────────────────────────────


def test_all_or_nothing_parent_refuse_clears_partial_success(tmp_path):
    """Seam 1 would accept; seam 2 refuses → no transformed PDB / no stitched.pdb."""
    a_xyz = [_curve_xyz(i) for i in range(8)]
    R = _rot_z(20)
    t = (6.0, -3.0, 1.0)
    b_local = [_curve_xyz(i) for i in range(5, 14)]
    b_xyz = [_apply(R, t, p) for p in b_local]
    c_xyz = [_curve_xyz(i) for i in range(11, 20)]
    c_xyz[0] = (c_xyz[0][0] + 28.0, c_xyz[0][1], c_xyz[0][2])
    c_xyz[1] = (c_xyz[1][0] - 10.0, c_xyz[1][1] + 24.0, c_xyz[1][2])
    c_xyz[2] = (c_xyz[2][0], c_xyz[2][1] - 16.0, c_xyz[2][2] + 22.0)
    a = _tile(1, a_xyz, plddt=40.0)
    b = _tile(6, b_xyz, plddt=90.0)
    c = _tile(12, c_xyz, plddt=80.0)
    out = tmp_path / "confidence_kabsch" / str(IN_INVENTORY)
    out.mkdir(parents=True)
    (out / "tile2_transformed.pdb").write_text("STALE\n", encoding="utf-8")
    (out / "stitched.pdb").write_text("STALE\n", encoding="utf-8")
    result = write_confidence_kabsch_restitch(
        [a, b, c], 20, tmp_path, parent_job_id=IN_INVENTORY
    )
    assert result.accepted is False
    assert len(result.seams) >= 1
    assert any(s.refuse_reason for s in result.seams)
    assert not (result.out_dir / "stitched.pdb").exists()
    assert not list(result.out_dir.glob("tile*_transformed.pdb"))
    prov = json.loads((result.out_dir / "provenance.json").read_text())
    assert prov["accepted"] is False
    assert prov["algorithm"] == ALGORITHM
    assert prov["decision"] == DECISION
    # Seam rows still recorded.
    assert (result.out_dir / "seams.jsonl").is_file()
    rows = [json.loads(line) for line in (result.out_dir / "seams.jsonl").read_text().splitlines()]
    assert rows


# ── T-1106 no overwrite ──────────────────────────────────────────────────────


def test_confidence_kabsch_dir_does_not_overwrite_assembler_or_d125_tree(tmp_path):
    a, b = _happy_pair()
    assembler = tmp_path / "assembler"
    write_stitched([a, b], 12, assembler)
    before_asm = (assembler / "stitched.pdb").read_text()
    d125 = write_kabsch_restitch(
        [a, b], 12, tmp_path, parent_job_id=IN_INVENTORY, assembler_dir=assembler
    )
    before_d125 = (d125.out_dir / "stitched.pdb").read_text()
    result = write_confidence_kabsch_restitch(
        [a, b],
        12,
        tmp_path,
        parent_job_id=IN_INVENTORY,
        assembler_dir=assembler,
        d125_dir=d125.out_dir,
    )
    assert result.out_dir == tmp_path / "confidence_kabsch" / str(IN_INVENTORY)
    assert (assembler / "stitched.pdb").read_text() == before_asm
    assert (d125.out_dir / "stitched.pdb").read_text() == before_d125
    assert result.out_dir.resolve() != assembler.resolve()
    assert result.out_dir.resolve() != d125.out_dir.resolve()
    refuse_sibling_overwrite(result.out_dir, assembler, d125.out_dir)
    with pytest.raises(SiblingOverwriteRefused):
        refuse_sibling_overwrite(assembler, assembler, d125.out_dir)
    with pytest.raises(SiblingOverwriteRefused):
        refuse_sibling_overwrite(d125.out_dir, assembler, d125.out_dir)


def test_d125_and_assembler_stay_independently_callable(tmp_path):
    a, b = _happy_pair()
    asm = write_stitched([a, b], 12, tmp_path / "assembler")
    d125 = write_kabsch_restitch(
        [a, b], 12, tmp_path, parent_job_id=IN_INVENTORY, assembler_dir=tmp_path / "assembler"
    )
    d126 = write_confidence_kabsch_restitch(
        [a, b],
        12,
        tmp_path,
        parent_job_id=IN_INVENTORY,
        assembler_dir=tmp_path / "assembler",
        d125_dir=d125.out_dir,
    )
    assert Path(asm["pdb"]).is_file()
    assert d125.accepted and d126.accepted
    assert d125.out_dir == kabsch_out_dir(tmp_path, IN_INVENTORY)
    assert d126.out_dir == confidence_kabsch_out_dir(tmp_path, IN_INVENTORY)
    # D-125 CLI still writes kabsch/, D-126 CLI writes confidence_kabsch/.
    man = tmp_path / "tiles.json"
    _write_manifest(tmp_path, man, parent_job_id=IN_INVENTORY, tiles=[a, b], length=12)
    rc125 = d125_main(["--manifest", str(man), "--out-root", str(tmp_path / "ops125")])
    rc126 = confidence_main(["--manifest", str(man), "--out-root", str(tmp_path / "ops126")])
    assert rc125 == 0 and rc126 == 0
    assert (tmp_path / "ops125" / "kabsch" / str(IN_INVENTORY) / "stitched.pdb").is_file()
    assert (tmp_path / "ops126" / "confidence_kabsch" / str(IN_INVENTORY) / "stitched.pdb").is_file()


# ── happy path still feeds winning_tile ──────────────────────────────────────


def test_accepted_seam_transforms_and_feeds_winning_tile(tmp_path):
    a, b = _happy_pair()
    assert winning_tile([a, b], 7) is b
    result = write_confidence_kabsch_restitch(
        [a, b], 12, tmp_path, parent_job_id=IN_INVENTORY, tile_job_ids=[3673, 3630]
    )
    assert result.accepted is True
    assert result.stitched is not None
    assert (result.out_dir / "tile2_transformed.pdb").is_file()
    assert result.seams[0].refuse_reason is None
    assert result.seams[0].rmsd_angstrom <= 0.05
    assert result.seams[0].rmsd_full_overlap_angstrom is not None
    assert result.seams[0].max_ca_jump_angstrom is not None
    assert result.seams[0].n_ca_eff >= 3
    assert winning_tile(result.tiles, 7) is result.tiles[1]
    assert stitch_plddt(result.tiles, 12)[6] == 90.0
    pae = json.loads((result.out_dir / "stitched_pae.json").read_text(encoding="utf-8"))
    assert pae[0][11] is None
    assert pae[0][11] != 0
    cbs = [atom for atom in parse_pdb(Path(result.stitched["pdb"]).read_text()) if atom.name == "CB"]
    assert cbs, "all-atom transform must keep CB"
    prov = json.loads((result.out_dir / "provenance.json").read_text())
    assert prov["algorithm"] == ALGORITHM
    assert prov["decision"] == DECISION
    assert prov["weight_epsilon"] == WEIGHT_EPSILON
    assert prov["rmsd_refuse_angstrom"] == 10.0


# ── inventory / CLI ──────────────────────────────────────────────────────────


def test_cli_refuses_parent_id_outside_inventory_including_igf2r(tmp_path):
    assert OUT_OF_INVENTORY not in CONFIDENCE_RESTITCH_PARENT_IDS
    assert OUT_OF_INVENTORY == 3356
    a, b = _happy_pair()
    man = tmp_path / "tiles.json"
    _write_manifest(tmp_path, man, parent_job_id=OUT_OF_INVENTORY, tiles=[a, b], length=12)
    rc = confidence_main(
        ["--manifest", str(man), "--out-root", str(tmp_path / "ops"), "--parent-id", str(OUT_OF_INVENTORY)]
    )
    assert rc == 2
    assert not (tmp_path / "ops" / "confidence_kabsch" / str(OUT_OF_INVENTORY) / "stitched.pdb").exists()
    with pytest.raises(InventoryRefused):
        write_confidence_kabsch_restitch([a, b], 12, tmp_path, parent_job_id=OUT_OF_INVENTORY)


def test_primary_five_are_not_a_named_exclusion():
    """CLI inventory is the 27; the five are inside it (T-1112 / no named-exclusion)."""
    assert PRIMARY_FIVE_PARENT_IDS == frozenset(PRIMARY_FIVE)
    assert PRIMARY_FIVE_PARENT_IDS <= KABSCH_RESTITCH_PARENT_IDS
    assert PRIMARY_FIVE_PARENT_IDS <= CONFIDENCE_RESTITCH_PARENT_IDS
    assert 3356 not in CONFIDENCE_RESTITCH_PARENT_IDS


def test_cli_accepts_a_primary_five_id_as_inventory(tmp_path):
    a, b = _happy_pair()
    man = tmp_path / "tiles.json"
    _write_manifest(tmp_path, man, parent_job_id=2939, tiles=[a, b], length=12)
    rc = confidence_main(["--manifest", str(man), "--out-root", str(tmp_path / "ops")])
    assert rc == 0
    assert (tmp_path / "ops" / "confidence_kabsch" / "2939" / "stitched.pdb").is_file()


# ── T-1111 / T-1112 ops report ───────────────────────────────────────────────


def test_ops_success_report_names_a_drop_on_the_22_and_allows_zero_of_five():
    d125 = {pid: (pid not in PRIMARY_FIVE_PARENT_IDS) for pid in KABSCH_RESTITCH_PARENT_IDS}
    # D-126 recovers none of the five and silently? No — we drop one prior PASS.
    d126 = dict(d125)
    d126[2817] = False  # a D-125 PASS → D-126 REFUSE
    report = build_ops_success_report(d125, d126)
    payload = report.to_json()
    assert payload["n_d125_pass_d126_pass"] == 21
    assert payload["n_d125_pass_d126_refuse"] == 1
    assert payload["n_d125_refuse_d126_pass"] == 0
    assert payload["n_d125_refuse_d126_refuse"] == 5
    assert payload["recovered_of_primary_five"] == 0
    assert payload["n_d125_pass_d126_refuse_is_named_finding"] is True
    assert payload["zero_of_five_recovered_is_allowed"] is True
    # 0-of-5 does not raise and does not change the gate.
    assert RMSD_REFUSE_ANGSTROM == 10.0


def test_ops_report_counts_a_recovery_without_loosening_the_gate(tmp_path):
    d125 = {pid: (pid not in PRIMARY_FIVE_PARENT_IDS) for pid in KABSCH_RESTITCH_PARENT_IDS}
    d126 = dict(d125)
    d126[2939] = True
    report = build_ops_success_report(d125, d126)
    assert report.n_d125_refuse_d126_pass == 1
    assert report.recovered_of_primary_five == 1
    assert RMSD_REFUSE_ANGSTROM == 10.0
    d125_path = tmp_path / "d125.json"
    d126_path = tmp_path / "d126.json"
    d125_path.write_text(json.dumps({str(k): v for k, v in d125.items()}), encoding="utf-8")
    d126_path.write_text(json.dumps({str(k): v for k, v in d126.items()}), encoding="utf-8")
    rc = confidence_main(
        [
            "--confusion-report",
            "--d125-outcomes",
            str(d125_path),
            "--d126-outcomes",
            str(d126_path),
        ]
    )
    assert rc == 0
