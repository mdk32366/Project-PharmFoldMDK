"""D-125-A — Kabsch restitch core. Tests that must be able to go red.

Hermetic fixtures. No Fly. No GPU. No restitch run of the 27.
Cite Spec §2 refuse defaults and existing ``winning_tile``.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import pytest

from core.features import parse_pdb
from core.hold48_kabsch import (
    ALGORITHM,
    DECISION,
    KABSCH_RESTITCH_PARENT_IDS,
    OVERLAP_CA_MIN,
    REFUSE_OVERLAP_CA_LT_3,
    REFUSE_RMSD_GT_10,
    REFUSE_SINGULAR_COVARIANCE,
    RMSD_REFUSE_ANGSTROM,
    AssemblerOverwriteRefused,
    InventoryRefused,
    apply_rigid_transform_pdb,
    ca_xyz_at_parent,
    fit_overlap_kabsch,
    kabsch_rotation_translation,
    write_kabsch_restitch,
)
from core.hold48_stitch import TileFold, stitch_plddt, winning_tile, write_stitched
from scripts.kabsch_restitch import main as restitch_main

IN_INVENTORY = 2817
OUT_OF_INVENTORY = 3356  # IGF2R parent — Spec says not in the 27


def _const_pae(n: int, value: float = 1.0) -> list[list[float]]:
    return [[value] * n for _ in range(n)]


def _curve_xyz(i: int) -> tuple[float, float, float]:
    """Non-collinear CA path so covariance rank is 2+."""
    return (
        i * 3.8,
        1.4 * math.sin(i * 0.8),
        0.9 * math.cos(i * 0.5),
    )


def _atom_line(serial: int, name: str, res_seq: int, xyz: tuple[float, float, float], element: str) -> str:
    x, y, z = xyz
    nm = name if len(name) >= 4 else f"{name:>3s} "
    return (
        f"ATOM  {serial:5d} {nm} ALA A{res_seq:4d}    "
        f"{x:8.3f}{y:8.3f}{z:8.3f}  1.00 50.00          {element:>2s}  "
    )


def _pdb_from_xyz(points: list[tuple[float, float, float]], *, extra_cb: bool = False) -> str:
    lines = []
    serial = 1
    for i, xyz in enumerate(points, start=1):
        lines.append(_atom_line(serial, "CA", i, xyz, "C"))
        serial += 1
        if extra_cb:
            cb = (xyz[0] + 1.2, xyz[1] + 0.4, xyz[2] - 0.3)
            lines.append(_atom_line(serial, "CB", i, cb, "C"))
            serial += 1
    return "\n".join(lines) + "\n"


def _rot_z(deg: float) -> tuple[tuple[float, float, float], ...]:
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    return ((c, -s, 0.0), (s, c, 0.0), (0.0, 0.0, 1.0))


def _apply(R, t, p):
    return (
        R[0][0] * p[0] + R[0][1] * p[1] + R[0][2] * p[2] + t[0],
        R[1][0] * p[0] + R[1][1] * p[1] + R[1][2] * p[2] + t[1],
        R[2][0] * p[0] + R[2][1] * p[1] + R[2][2] * p[2] + t[2],
    )


def _tile(start: int, xyzs, *, plddt=90.0, extra_cb=False) -> TileFold:
    n = len(xyzs)
    return TileFold(
        start=start,
        end=start + n - 1,
        pdb=_pdb_from_xyz(list(xyzs), extra_cb=extra_cb),
        plddt=[plddt] * n,
        pae=_const_pae(n),
    )


def _happy_pair():
    """Tile A 1–8; tile B 6–12 is A-overlap plus unique residues, rigidly moved."""
    a_xyz = [_curve_xyz(i) for i in range(8)]
    b_local = [_curve_xyz(i) for i in range(5, 12)]  # parent 6–12
    R = _rot_z(40)
    t = (12.0, -7.5, 3.0)
    b_moved = [_apply(R, t, p) for p in b_local]
    a = _tile(1, a_xyz, plddt=40.0, extra_cb=True)
    b = _tile(6, b_moved, plddt=90.0, extra_cb=True)
    return a, b


# ── T-1088 ───────────────────────────────────────────────────────────────────


def test_overlap_ca_lt_3_refuses_align(tmp_path):
    a = _tile(1, [_curve_xyz(i) for i in range(5)], plddt=90.0)
    b = _tile(4, [_curve_xyz(i) for i in range(3, 8)], plddt=80.0)  # overlap parent 4–5 → 2 Cα
    assert OVERLAP_CA_MIN == 3
    fit = fit_overlap_kabsch(a, b)
    assert fit.n_ca < 3
    assert fit.refuse_reason == REFUSE_OVERLAP_CA_LT_3
    assert fit.rmsd_angstrom is None
    result = write_kabsch_restitch(
        [a, b], 8, tmp_path, parent_job_id=IN_INVENTORY, tile_job_ids=[3673, 3630]
    )
    assert result.accepted is False
    assert result.stitched is None
    assert not (result.out_dir / "stitched.pdb").exists()
    assert not (result.out_dir / "tile2_transformed.pdb").exists()
    row = result.seams[0]
    assert row.refuse_reason == REFUSE_OVERLAP_CA_LT_3
    assert row.rmsd_angstrom is None
    prov = json.loads((result.out_dir / "provenance.json").read_text())
    assert prov["algorithm"] == ALGORITHM
    assert prov["decision"] == DECISION
    assert prov["accepted"] is False


# ── T-1089 ───────────────────────────────────────────────────────────────────


def test_rmsd_gt_10_refuses_seam_and_records_rmsd(tmp_path):
    a_xyz = [_curve_xyz(i) for i in range(8)]
    # Overlap 6–8 (3 pts) but B's overlap is translated by 20 Å in a non-rigid way
    # (each point shoved differently) so RMSD cannot be Kabsch-closed under 10 Å.
    b_xyz = [_curve_xyz(i) for i in range(5, 12)]
    b_xyz[0] = (b_xyz[0][0] + 25.0, b_xyz[0][1], b_xyz[0][2])
    b_xyz[1] = (b_xyz[1][0] - 8.0, b_xyz[1][1] + 22.0, b_xyz[1][2])
    b_xyz[2] = (b_xyz[2][0], b_xyz[2][1] - 18.0, b_xyz[2][2] + 20.0)
    a = _tile(1, a_xyz, plddt=90.0)
    b = _tile(6, b_xyz, plddt=80.0)
    fit = fit_overlap_kabsch(a, b)
    assert fit.n_ca >= 3
    assert fit.rmsd_angstrom is not None
    assert fit.rmsd_angstrom > RMSD_REFUSE_ANGSTROM
    assert fit.refuse_reason == REFUSE_RMSD_GT_10
    result = write_kabsch_restitch([a, b], 12, tmp_path, parent_job_id=IN_INVENTORY)
    assert result.accepted is False
    assert not (result.out_dir / "stitched.pdb").exists()
    assert result.seams[0].rmsd_angstrom == pytest.approx(fit.rmsd_angstrom)
    assert result.seams[0].refuse_reason == REFUSE_RMSD_GT_10


# ── T-1090 ───────────────────────────────────────────────────────────────────


def test_singular_covariance_refuses_align(tmp_path):
    # Four collinear Cα in both tiles (same line) → covariance rank < 2.
    line = [(i * 3.8, 0.0, 0.0) for i in range(6)]
    a = _tile(1, line, plddt=90.0)
    b = _tile(3, [(i * 3.8, 0.0, 0.0) for i in range(2, 8)], plddt=80.0)
    fit = fit_overlap_kabsch(a, b)
    assert fit.n_ca >= 3
    assert fit.refuse_reason == REFUSE_SINGULAR_COVARIANCE
    assert fit.rmsd_angstrom is None
    result = write_kabsch_restitch([a, b], 8, tmp_path, parent_job_id=IN_INVENTORY)
    assert result.accepted is False
    assert not (result.out_dir / "tile2_transformed.pdb").exists()


def test_coincident_points_are_singular():
    pts = [(0.0, 0.0, 0.0)] * 4
    a = _tile(1, pts + [_curve_xyz(9)], plddt=90.0)
    b = _tile(1, pts + [_curve_xyz(10)], plddt=80.0)
    # overlap is all 5 residues but first 4 are coincident — still may have rank
    # from the fifth. Force all-overlap coincident:
    a = _tile(1, [(0.0, 0.0, 0.0)] * 5, plddt=90.0)
    b = _tile(1, [(1.0, 1.0, 1.0)] * 5, plddt=80.0)
    fit = fit_overlap_kabsch(a, b)
    assert fit.refuse_reason == REFUSE_SINGULAR_COVARIANCE


# ── T-1091 ───────────────────────────────────────────────────────────────────


def test_accepted_seam_transforms_and_feeds_winning_tile(tmp_path):
    a, b = _happy_pair()
    # Assembler winner on overlap is B (plddt 90 > 40) — unchanged by Kabsch.
    assert winning_tile([a, b], 7) is b
    result = write_kabsch_restitch(
        [a, b], 12, tmp_path, parent_job_id=IN_INVENTORY, tile_job_ids=[3673, 3630]
    )
    assert result.accepted is True
    assert result.stitched is not None
    assert (result.out_dir / "tile2_transformed.pdb").is_file()
    assert (result.out_dir / "stitched.pdb").is_file()
    assert result.seams[0].refuse_reason is None
    assert result.seams[0].rmsd_angstrom is not None
    assert result.seams[0].rmsd_angstrom <= 0.05
    # Transformed overlap Cα sit on the reference frame.
    aligned_b = result.tiles[1]
    for parent_res in (6, 7, 8):
        q = ca_xyz_at_parent(a, parent_res)
        p = ca_xyz_at_parent(aligned_b, parent_res)
        assert q is not None and p is not None
        assert p[0] == pytest.approx(q[0], abs=0.02)
        assert p[1] == pytest.approx(q[1], abs=0.02)
        assert p[2] == pytest.approx(q[2], abs=0.02)
    # Winner selection is still per-residue pLDDT via the existing assembler.
    assert winning_tile(result.tiles, 7) is result.tiles[1]
    assert stitch_plddt(result.tiles, 12)[6] == 90.0
    atoms = [atom for atom in parse_pdb(Path(result.stitched["pdb"]).read_text()) if atom.is_ca]
    assert len(atoms) == 12
    # A non-Cα atom was transformed too (CB present on residue 1 from tile A).
    cbs = [atom for atom in parse_pdb(Path(result.stitched["pdb"]).read_text()) if atom.name == "CB"]
    assert cbs, "all-atom transform must keep CB; Kabsch must not drop to Cα-only"
    # D-111: off-block PAE is null, never 0 — via write_kabsch_restitch (feeds write_stitched).
    pae_path = result.out_dir / "stitched_pae.json"
    assert pae_path.is_file()
    pae = json.loads(pae_path.read_text(encoding="utf-8"))
    assert len(pae) == 12
    # Residue 1 (tile A only) vs residue 12 (tile B only) never shared a forward pass.
    assert pae[0][11] is None
    assert pae[11][0] is None
    assert pae[0][11] != 0
    assert pae[0][11] != 0.0
    dumped = json.dumps(pae)
    assert "null" in dumped
    parsed = json.loads(dumped)
    assert parsed[0][11] is None


def test_kabsch_recovers_known_rotation():
    Q = [_curve_xyz(i) for i in range(5)]
    R = _rot_z(90)
    t = (4.0, -2.0, 1.5)
    P = [_apply(R, t, q) for q in Q]
    R_hat, t_hat, rmsd, rank = kabsch_rotation_translation(P, Q)
    assert rank >= 2
    assert rmsd < 1e-6
    for p, q in zip(P, Q):
        got = _apply(R_hat, t_hat, p)
        assert got[0] == pytest.approx(q[0], abs=1e-6)
        assert got[1] == pytest.approx(q[1], abs=1e-6)
        assert got[2] == pytest.approx(q[2], abs=1e-6)


# ── T-1092 ───────────────────────────────────────────────────────────────────


def test_assembler_path_stays_callable_without_kabsch(tmp_path):
    a, b = _happy_pair()
    paths = write_stitched([a, b], 12, tmp_path / "assembler")
    assert Path(paths["pdb"]).is_file()
    # Kabsch is a different tree. Assembler files stay put.
    write_kabsch_restitch(
        [a, b],
        12,
        tmp_path,
        parent_job_id=IN_INVENTORY,
        assembler_dir=tmp_path / "assembler",
    )
    assert Path(paths["pdb"]).read_text() == (tmp_path / "assembler" / "stitched.pdb").read_text()


# ── T-1093 ───────────────────────────────────────────────────────────────────


def test_cli_refuses_parent_id_outside_inventory(tmp_path):
    assert OUT_OF_INVENTORY not in KABSCH_RESTITCH_PARENT_IDS
    assert IN_INVENTORY in KABSCH_RESTITCH_PARENT_IDS
    a, b = _happy_pair()
    man = tmp_path / "tiles.json"
    _write_manifest(tmp_path, man, parent_job_id=OUT_OF_INVENTORY, tiles=[a, b], length=12)
    rc = restitch_main(
        ["--manifest", str(man), "--out-root", str(tmp_path / "ops"), "--parent-id", str(OUT_OF_INVENTORY)]
    )
    assert rc == 2
    assert not (tmp_path / "ops" / "kabsch" / str(OUT_OF_INVENTORY) / "stitched.pdb").exists()
    with pytest.raises(InventoryRefused):
        write_kabsch_restitch([a, b], 12, tmp_path, parent_job_id=OUT_OF_INVENTORY)


def test_cli_accepts_inventory_parent_on_happy_path(tmp_path):
    a, b = _happy_pair()
    man = tmp_path / "tiles.json"
    _write_manifest(tmp_path, man, parent_job_id=IN_INVENTORY, tiles=[a, b], length=12)
    rc = restitch_main(["--manifest", str(man), "--out-root", str(tmp_path / "ops")])
    assert rc == 0
    assert (tmp_path / "ops" / "kabsch" / str(IN_INVENTORY) / "stitched.pdb").is_file()


# ── T-1094 ───────────────────────────────────────────────────────────────────


def test_kabsch_dir_does_not_overwrite_assembler_pdbs(tmp_path):
    a, b = _happy_pair()
    assembler = tmp_path / "assembler"
    write_stitched([a, b], 12, assembler)
    before = (assembler / "stitched.pdb").read_text()
    with pytest.raises(AssemblerOverwriteRefused):
        write_kabsch_restitch(
            [a, b],
            12,
            tmp_path,
            parent_job_id=IN_INVENTORY,
            assembler_dir=assembler / ".." / "kabsch" / str(IN_INVENTORY),
        )
    # Direct "out is assembler" pin:
    from core.hold48_kabsch import refuse_assembler_overwrite, kabsch_out_dir

    refuse_assembler_overwrite(kabsch_out_dir(tmp_path, IN_INVENTORY), assembler)
    result = write_kabsch_restitch(
        [a, b], 12, tmp_path, parent_job_id=IN_INVENTORY, assembler_dir=assembler
    )
    assert result.out_dir == tmp_path / "kabsch" / str(IN_INVENTORY)
    assert (assembler / "stitched.pdb").read_text() == before
    assert result.out_dir.resolve() != assembler.resolve()


def test_transform_pdb_moves_all_atoms_not_just_ca():
    pdb = _pdb_from_xyz([_curve_xyz(0), _curve_xyz(1)], extra_cb=True)
    R = _rot_z(15)
    t = (1.0, 2.0, 3.0)
    out = apply_rigid_transform_pdb(pdb, R, t)
    before = parse_pdb(pdb)
    after = parse_pdb(out)
    assert len(before) == len(after) == 4
    for old, new in zip(before, after):
        exp = _apply(R, t, (old.x, old.y, old.z))
        assert new.x == pytest.approx(exp[0], abs=5e-4)
        assert new.y == pytest.approx(exp[1], abs=5e-4)
        assert new.z == pytest.approx(exp[2], abs=5e-4)


def _write_manifest(tmp_path: Path, man: Path, *, parent_job_id: int, tiles, length: int) -> None:
    rows = []
    for i, tile in enumerate(tiles, start=1):
        (tmp_path / f"tile{i}.pdb").write_text(tile.pdb, encoding="utf-8")
        (tmp_path / f"tile{i}_plddt.json").write_text(json.dumps(list(tile.plddt)), encoding="utf-8")
        (tmp_path / f"tile{i}_pae.json").write_text(json.dumps([list(r) for r in tile.pae]), encoding="utf-8")
        rows.append(
            {
                "pdb": f"tile{i}.pdb",
                "plddt": f"tile{i}_plddt.json",
                "pae": f"tile{i}_pae.json",
                "start": tile.start,
                "end": tile.end,
            }
        )
    man.write_text(
        json.dumps(
            {
                "parent_job_id": parent_job_id,
                "length": length,
                "tile_job_ids": [3673, 3630],
                "tiles": rows,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
