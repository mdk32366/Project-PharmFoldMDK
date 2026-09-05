"""D-127-A — piecewise / domain-aware Kabsch core. Tests that must be able to go red.

Hermetic fixtures. No Fly. No GPU. No restitch run of the 27.
Cite Spec §1–§3 / §5 and existing ``winning_tile``.
D-125 ``write_kabsch_restitch``, D-126 ``write_confidence_kabsch_restitch``,
and the assembler stay independently callable.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from core.features import parse_pdb
from core.hold48 import domain_ends_span_relative
from core.hold48_confidence_kabsch import (
    write_confidence_kabsch_restitch,
)
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
from core.hold48_piecewise_kabsch import (
    ALGORITHM,
    DECISION,
    PIECEWISE_RESTITCH_PARENT_IDS,
    PRIMARY_THREE_PARENT_IDS,
    REFUSE_LINKER_JUMP_GT_10,
    REFUSE_NO_DOMAIN_PIECES,
    WEIGHT_EPSILON,
    InventoryRefused,
    SiblingOverwriteRefused,
    build_ops_success_report,
    domain_intervals_span_relative,
    fit_domain_piece,
    inherit_piece_for_residue,
    piecewise_kabsch_out_dir,
    refuse_sibling_overwrite,
    write_piecewise_kabsch_restitch,
)
from core.hold48_stitch import TileFold, stitch_plddt, winning_tile, write_stitched
from scripts.confidence_kabsch_restitch import main as d126_main
from scripts.kabsch_restitch import main as d125_main
from scripts.piecewise_kabsch_restitch import main as piecewise_main
from tests.test_d125_kabsch import (
    IN_INVENTORY,
    OUT_OF_INVENTORY,
    _apply,
    _curve_xyz,
    _rot_z,
    _tile,
    _write_manifest,
)

PRIMARY_THREE = (2939, 3272, 3432)
D125_KABSCH_SHA256 = "4c7bb45d04507e2a67ba3600b35d6130d62843ca3bc99c15d3568d5cb105ff6e"
D126_CONF_SHA256 = "d526a856ec8f1ba978a3586f3dfcf4a0ee858da12132499f2db37368efc77f18"

# Two-domain geometry: overlap 8–20; D1=1–12; linker=13–15; D2=16–27.
TWO_DOMAIN_INTERVALS = ((1, 12), (16, 27))
R1 = _rot_z(40)
T1 = (12.0, -7.5, 3.0)
R2 = _rot_z(-25)
T2 = (-8.0, 10.0, -4.0)


def _tile_plddt(start: int, xyzs, plddts, *, extra_cb=False) -> TileFold:
    n = len(xyzs)
    assert len(plddts) == n
    t = _tile(start, xyzs, plddt=90.0, extra_cb=extra_cb)
    return TileFold(start=t.start, end=t.end, pdb=t.pdb, plddt=list(plddts), pae=t.pae)


def _two_domain_pair(*, shove_linker: float = 0.0, extra_cb: bool = True):
    """Reference A 1–20; moving B 8–27 with a different rigid on each domain."""
    a_xyz = [_curve_xyz(i) for i in range(20)]
    b_xyz = []
    for parent in range(8, 28):
        q = _curve_xyz(parent - 1)
        if parent <= 15:
            p = _apply(R1, T1, q)
            if shove_linker and 13 <= parent <= 15:
                p = (p[0] + shove_linker, p[1] - shove_linker * 0.4, p[2] + shove_linker * 0.2)
            b_xyz.append(p)
        else:
            b_xyz.append(_apply(R2, T2, q))
    a = _tile(1, a_xyz, plddt=40.0, extra_cb=extra_cb)
    b = _tile(8, b_xyz, plddt=90.0, extra_cb=extra_cb)
    return a, b


def _write_piecewise_manifest(
    tmp_path: Path,
    man: Path,
    *,
    parent_job_id: int,
    tiles,
    length: int,
    domain_intervals=TWO_DOMAIN_INTERVALS,
) -> None:
    _write_manifest(tmp_path, man, parent_job_id=parent_job_id, tiles=tiles, length=length)
    raw = json.loads(man.read_text(encoding="utf-8"))
    raw["domain_intervals"] = [list(iv) for iv in domain_intervals]
    man.write_text(json.dumps(raw, indent=2), encoding="utf-8")


# ── T-1127 ───────────────────────────────────────────────────────────────────


def test_piece_n_ca_lt_3_refuses(tmp_path):
    a = _tile(1, [_curve_xyz(i) for i in range(5)], plddt=90.0)
    b = _tile(4, [_curve_xyz(i) for i in range(3, 8)], plddt=80.0)  # overlap 4–5 → 2 Cα
    piece = fit_domain_piece(a, b, (1, 10))
    assert piece.n_ca < 3
    assert piece.refuse_reason == REFUSE_OVERLAP_CA_LT_3
    assert piece.rmsd_angstrom is None
    result = write_piecewise_kabsch_restitch(
        [a, b],
        8,
        tmp_path,
        parent_job_id=IN_INVENTORY,
        tile_job_ids=[3673, 3630],
        domain_intervals=[(1, 10)],
    )
    assert result.accepted is False
    assert result.stitched is None
    assert not (result.out_dir / "stitched.pdb").exists()
    assert not (result.out_dir / "tile2_transformed.pdb").exists()
    assert result.seams[0].refuse_reason == REFUSE_OVERLAP_CA_LT_3
    assert result.seams[0].rmsd_full_overlap_angstrom is None
    assert result.seams[0].max_ca_jump_angstrom is None


# ── T-1128 ───────────────────────────────────────────────────────────────────


def test_piece_rmsd_gt_10_refuses(tmp_path):
    a_xyz = [_curve_xyz(i) for i in range(8)]
    b_xyz = [_curve_xyz(i) for i in range(5, 12)]
    b_xyz[0] = (b_xyz[0][0] + 25.0, b_xyz[0][1], b_xyz[0][2])
    b_xyz[1] = (b_xyz[1][0] - 8.0, b_xyz[1][1] + 22.0, b_xyz[1][2])
    b_xyz[2] = (b_xyz[2][0], b_xyz[2][1] - 18.0, b_xyz[2][2] + 20.0)
    a = _tile(1, a_xyz, plddt=90.0)
    b = _tile(6, b_xyz, plddt=80.0)
    piece = fit_domain_piece(a, b, (1, 20))
    assert piece.n_ca >= 3
    assert piece.rmsd_angstrom is not None
    assert piece.rmsd_angstrom > RMSD_REFUSE_ANGSTROM
    assert piece.refuse_reason == REFUSE_RMSD_GT_10
    result = write_piecewise_kabsch_restitch(
        [a, b], 12, tmp_path, parent_job_id=IN_INVENTORY, domain_intervals=[(1, 20)]
    )
    assert result.accepted is False
    assert not (result.out_dir / "stitched.pdb").exists()
    assert result.seams[0].refuse_reason == REFUSE_RMSD_GT_10
    assert result.seams[0].pieces[0].rmsd_angstrom == pytest.approx(piece.rmsd_angstrom)
    assert result.seams[0].rmsd_full_overlap_angstrom is None


# ── T-1129 ───────────────────────────────────────────────────────────────────


def test_piece_singular_covariance_refuses(tmp_path):
    line = [(i * 3.8, 0.0, 0.0) for i in range(6)]
    a = _tile(1, line, plddt=90.0)
    b = _tile(3, [(i * 3.8, 0.0, 0.0) for i in range(2, 8)], plddt=80.0)
    piece = fit_domain_piece(a, b, (1, 20))
    assert piece.n_ca >= 3
    assert piece.refuse_reason == REFUSE_SINGULAR_COVARIANCE
    assert piece.rmsd_angstrom is None
    result = write_piecewise_kabsch_restitch(
        [a, b], 8, tmp_path, parent_job_id=IN_INVENTORY, domain_intervals=[(1, 20)]
    )
    assert result.accepted is False
    assert not (result.out_dir / "tile2_transformed.pdb").exists()
    assert result.seams[0].refuse_reason == REFUSE_SINGULAR_COVARIANCE


# ── T-1130 ───────────────────────────────────────────────────────────────────


def test_no_domain_pieces_refuses_parent(tmp_path):
    a, b = _two_domain_pair()
    result = write_piecewise_kabsch_restitch(
        [a, b], 27, tmp_path, parent_job_id=IN_INVENTORY, domain_intervals=[]
    )
    assert result.accepted is False
    assert result.seams[0].refuse_reason == REFUSE_NO_DOMAIN_PIECES
    assert result.seams[0].pieces == ()
    assert not (result.out_dir / "stitched.pdb").exists()
    assert not (result.out_dir / "tile2_transformed.pdb").exists()
    assert result.seams[0].rmsd_full_overlap_angstrom is None
    # Domains that miss the overlap entirely are also no_domain_pieces.
    miss = write_piecewise_kabsch_restitch(
        [a, b], 27, tmp_path / "miss", parent_job_id=IN_INVENTORY, domain_intervals=[(1, 4)]
    )
    assert miss.accepted is False
    assert miss.seams[0].refuse_reason == REFUSE_NO_DOMAIN_PIECES


# ── T-1131 ───────────────────────────────────────────────────────────────────


def test_linker_jump_gt_10_refuses_parent(tmp_path):
    a, b = _two_domain_pair(shove_linker=20.0)
    result = write_piecewise_kabsch_restitch(
        [a, b],
        27,
        tmp_path,
        parent_job_id=IN_INVENTORY,
        domain_intervals=TWO_DOMAIN_INTERVALS,
    )
    assert result.accepted is False
    assert result.seams[0].refuse_reason == REFUSE_LINKER_JUMP_GT_10
    assert result.seams[0].max_linker_ca_jump is not None
    assert result.seams[0].max_linker_ca_jump > RMSD_REFUSE_ANGSTROM
    assert result.seams[0].linker_n is not None
    assert result.seams[0].linker_n >= 3
    # Linker refuse is after apply — full-overlap disclosure is written.
    assert result.seams[0].rmsd_full_overlap_angstrom is not None
    assert result.seams[0].max_ca_jump_angstrom is not None
    assert not (result.out_dir / "stitched.pdb").exists()
    assert not (result.out_dir / "tile2_transformed.pdb").exists()
    assert RMSD_REFUSE_ANGSTROM == 10.0


# ── T-1132 ───────────────────────────────────────────────────────────────────


def test_accepted_piece_applies_only_to_its_domain(tmp_path):
    a, b = _two_domain_pair()
    result = write_piecewise_kabsch_restitch(
        [a, b],
        27,
        tmp_path,
        parent_job_id=IN_INVENTORY,
        domain_intervals=TWO_DOMAIN_INTERVALS,
    )
    assert result.accepted is True
    aligned_b = result.tiles[1]
    for parent_res in (8, 9, 10, 11, 12):
        q = ca_xyz_at_parent(a, parent_res)
        p = ca_xyz_at_parent(aligned_b, parent_res)
        assert q is not None and p is not None
        assert p[0] == pytest.approx(q[0], abs=0.05)
        assert p[1] == pytest.approx(q[1], abs=0.05)
        assert p[2] == pytest.approx(q[2], abs=0.05)
    for parent_res in (16, 17, 18, 19, 20):
        q = ca_xyz_at_parent(a, parent_res)
        p = ca_xyz_at_parent(aligned_b, parent_res)
        assert q is not None and p is not None
        assert p[0] == pytest.approx(q[0], abs=0.05)
        assert p[1] == pytest.approx(q[1], abs=0.05)
        assert p[2] == pytest.approx(q[2], abs=0.05)
    # C-terminal unique residue of B must sit in the D2 / reference frame,
    # not the D1 frame (would miss by tens of Å if the wrong R,t were used).
    p21 = ca_xyz_at_parent(aligned_b, 21)
    expect = _curve_xyz(20)
    assert p21 is not None
    assert p21[0] == pytest.approx(expect[0], abs=0.05)
    assert p21[1] == pytest.approx(expect[1], abs=0.05)
    assert p21[2] == pytest.approx(expect[2], abs=0.05)
    # Two accepted pieces, two different transforms.
    pieces = result.seams[0].pieces
    assert len(pieces) == 2
    assert all(p.accepted for p in pieces)
    assert pieces[0].rotation != pieces[1].rotation


def test_linker_inherits_n_terminal_piece(tmp_path):
    a, b = _two_domain_pair()
    result = write_piecewise_kabsch_restitch(
        [a, b],
        27,
        tmp_path,
        parent_job_id=IN_INVENTORY,
        domain_intervals=TWO_DOMAIN_INTERVALS,
    )
    # Re-run through inherit helper so the N-terminal rule is pinned.
    accepted = [p for p in result.seams[0].pieces if p.accepted]
    d1 = inherit_piece_for_residue(10, accepted)
    d2 = inherit_piece_for_residue(18, accepted)
    linker = inherit_piece_for_residue(14, accepted)
    n_of_all = inherit_piece_for_residue(1, accepted)
    assert d1.interval == (1, 12)
    assert d2.interval == (16, 27)
    assert linker.interval == (1, 12)  # nearest N-terminal accepted piece
    assert n_of_all.interval == (1, 12)  # residue 1 sits inside D1
    only_d2 = [p for p in accepted if p.interval == (16, 27)]
    assert inherit_piece_for_residue(5, only_d2).interval == (16, 27)
    # After apply, constructed linkers (same R as D1) land on the reference.
    aligned_b = result.tiles[1]
    for parent_res in (13, 14, 15):
        q = ca_xyz_at_parent(result.tiles[0], parent_res)
        p = ca_xyz_at_parent(aligned_b, parent_res)
        assert q is not None and p is not None
        assert p[0] == pytest.approx(q[0], abs=0.05)
        assert p[1] == pytest.approx(q[1], abs=0.05)
        assert p[2] == pytest.approx(q[2], abs=0.05)


def test_full_accept_feeds_winning_tile(tmp_path):
    a, b = _two_domain_pair()
    assert winning_tile([a, b], 10) is b
    result = write_piecewise_kabsch_restitch(
        [a, b],
        27,
        tmp_path,
        parent_job_id=IN_INVENTORY,
        tile_job_ids=[3673, 3630],
        domain_intervals=TWO_DOMAIN_INTERVALS,
    )
    assert result.accepted is True
    assert result.stitched is not None
    assert (result.out_dir / "tile2_transformed.pdb").is_file()
    assert result.out_dir == tmp_path / "piecewise_kabsch" / str(IN_INVENTORY)
    assert result.seams[0].refuse_reason is None
    assert result.seams[0].rmsd_full_overlap_angstrom is not None
    assert result.seams[0].max_ca_jump_angstrom is not None
    assert result.seams[0].linker_n is not None
    assert result.seams[0].max_linker_ca_jump is not None
    assert result.seams[0].max_linker_ca_jump <= RMSD_REFUSE_ANGSTROM
    assert winning_tile(result.tiles, 10) is result.tiles[1]
    assert stitch_plddt(result.tiles, 27)[9] == 90.0
    pae = json.loads((result.out_dir / "stitched_pae.json").read_text(encoding="utf-8"))
    assert pae[0][26] is None
    assert pae[0][26] != 0
    dumped = json.dumps(pae)
    assert "null" in dumped
    cbs = [atom for atom in parse_pdb(Path(result.stitched["pdb"]).read_text()) if atom.name == "CB"]
    assert cbs, "all-atom transform must keep CB"
    prov = json.loads((result.out_dir / "provenance.json").read_text())
    assert prov["algorithm"] == ALGORITHM
    assert prov["decision"] == DECISION
    assert prov["weight_epsilon"] == WEIGHT_EPSILON
    assert prov["rmsd_refuse_angstrom"] == 10.0
    assert prov["no_trim_loop"] is True


def test_piecewise_dir_does_not_overwrite_assembler_d125_or_d126(tmp_path):
    a, b = _two_domain_pair()
    assembler = tmp_path / "assembler"
    write_stitched([a, b], 27, assembler)
    before_asm = (assembler / "stitched.pdb").read_text()
    d125 = write_kabsch_restitch(
        [a, b], 27, tmp_path, parent_job_id=IN_INVENTORY, assembler_dir=assembler
    )
    before_d125 = (d125.out_dir / "stitched.pdb").read_text() if d125.accepted else None
    d126 = write_confidence_kabsch_restitch(
        [a, b],
        27,
        tmp_path,
        parent_job_id=IN_INVENTORY,
        assembler_dir=assembler,
        d125_dir=d125.out_dir,
    )
    before_d126 = (d126.out_dir / "stitched.pdb").read_text() if d126.accepted else None
    result = write_piecewise_kabsch_restitch(
        [a, b],
        27,
        tmp_path,
        parent_job_id=IN_INVENTORY,
        assembler_dir=assembler,
        d125_dir=d125.out_dir,
        d126_dir=d126.out_dir,
        domain_intervals=TWO_DOMAIN_INTERVALS,
    )
    assert result.out_dir == piecewise_kabsch_out_dir(tmp_path, IN_INVENTORY)
    assert (assembler / "stitched.pdb").read_text() == before_asm
    if before_d125 is not None:
        assert (d125.out_dir / "stitched.pdb").read_text() == before_d125
    if before_d126 is not None:
        assert (d126.out_dir / "stitched.pdb").read_text() == before_d126
    assert result.out_dir.resolve() != assembler.resolve()
    assert result.out_dir.resolve() != d125.out_dir.resolve()
    assert result.out_dir.resolve() != d126.out_dir.resolve()
    refuse_sibling_overwrite(result.out_dir, assembler, d125.out_dir, d126.out_dir)
    with pytest.raises(SiblingOverwriteRefused):
        refuse_sibling_overwrite(assembler, assembler, d125.out_dir, d126.out_dir)
    with pytest.raises(SiblingOverwriteRefused):
        refuse_sibling_overwrite(d125.out_dir, assembler, d125.out_dir, d126.out_dir)
    with pytest.raises(SiblingOverwriteRefused):
        refuse_sibling_overwrite(d126.out_dir, assembler, d125.out_dir, d126.out_dir)


def test_d125_d126_and_assembler_stay_independently_callable(tmp_path):
    a, b = _two_domain_pair()
    asm = write_stitched([a, b], 27, tmp_path / "assembler")
    d125 = write_kabsch_restitch(
        [a, b], 27, tmp_path, parent_job_id=IN_INVENTORY, assembler_dir=tmp_path / "assembler"
    )
    d126 = write_confidence_kabsch_restitch(
        [a, b],
        27,
        tmp_path,
        parent_job_id=IN_INVENTORY,
        assembler_dir=tmp_path / "assembler",
        d125_dir=d125.out_dir,
    )
    d127 = write_piecewise_kabsch_restitch(
        [a, b],
        27,
        tmp_path,
        parent_job_id=IN_INVENTORY,
        assembler_dir=tmp_path / "assembler",
        d125_dir=d125.out_dir,
        d126_dir=d126.out_dir,
        domain_intervals=TWO_DOMAIN_INTERVALS,
    )
    assert Path(asm["pdb"]).is_file()
    assert d127.accepted
    assert d125.out_dir == kabsch_out_dir(tmp_path, IN_INVENTORY)
    man = tmp_path / "tiles.json"
    _write_piecewise_manifest(
        tmp_path, man, parent_job_id=IN_INVENTORY, tiles=[a, b], length=27
    )
    rc125 = d125_main(["--manifest", str(man), "--out-root", str(tmp_path / "ops125")])
    rc126 = d126_main(["--manifest", str(man), "--out-root", str(tmp_path / "ops126")])
    rc127 = piecewise_main(["--manifest", str(man), "--out-root", str(tmp_path / "ops127")])
    assert rc125 in (0, 1)  # single-rigid may refuse this two-domain pair
    assert rc126 in (0, 1)
    assert rc127 == 0
    assert (tmp_path / "ops127" / "piecewise_kabsch" / str(IN_INVENTORY) / "stitched.pdb").is_file()


def test_no_trim_loop_in_piecewise_module():
    src = Path(__file__).resolve().parent.parent / "core" / "hold48_piecewise_kabsch.py"
    text = src.read_text(encoding="utf-8")
    assert "trim_highest_residual" not in text
    assert "TRIM_ROUND_CAP" not in text
    assert "apply_plddt_floor" not in text
    assert "fit_overlap_confidence_kabsch" not in text
    assert "NO trim" in text or "No trim" in text
    assert "weighted_kabsch_rotation_translation" in text


def test_all_or_nothing_parent_refuse_clears_partial_success(tmp_path):
    a_xyz = [_curve_xyz(i) for i in range(8)]
    b_local = [_curve_xyz(i) for i in range(5, 14)]
    b_xyz = [_apply(R1, T1, p) for p in b_local]
    c_xyz = [_curve_xyz(i) for i in range(11, 20)]
    c_xyz[0] = (c_xyz[0][0] + 28.0, c_xyz[0][1], c_xyz[0][2])
    c_xyz[1] = (c_xyz[1][0] - 10.0, c_xyz[1][1] + 24.0, c_xyz[1][2])
    c_xyz[2] = (c_xyz[2][0], c_xyz[2][1] - 16.0, c_xyz[2][2] + 22.0)
    a = _tile(1, a_xyz, plddt=40.0)
    b = _tile(6, b_xyz, plddt=90.0)
    c = _tile(12, c_xyz, plddt=80.0)
    out = tmp_path / "piecewise_kabsch" / str(IN_INVENTORY)
    out.mkdir(parents=True)
    (out / "tile2_transformed.pdb").write_text("STALE\n", encoding="utf-8")
    (out / "stitched.pdb").write_text("STALE\n", encoding="utf-8")
    result = write_piecewise_kabsch_restitch(
        [a, b, c],
        20,
        tmp_path,
        parent_job_id=IN_INVENTORY,
        domain_intervals=[(1, 20)],
    )
    assert result.accepted is False
    assert any(s.refuse_reason for s in result.seams)
    assert not (result.out_dir / "stitched.pdb").exists()
    assert not list(result.out_dir.glob("tile*_transformed.pdb"))
    assert (result.out_dir / "seams.jsonl").is_file()


# ── domain-snap source identity ──────────────────────────────────────────────


def test_domain_intervals_use_same_emit_source(tmp_path):
    cache = tmp_path / "spancache"
    cache.mkdir()
    (cache / "QTEST.json").write_text(
        json.dumps(
            {
                "features": [
                    {
                        "type": "Domain",
                        "location": {"start": {"value": 10}, "end": {"value": 40}},
                    },
                    {
                        "type": "Repeat",
                        "location": {"start": {"value": 50}, "end": {"value": 80}},
                    },
                    {
                        "type": "Chain",
                        "location": {"start": {"value": 1}, "end": {"value": 200}},
                    },
                    {
                        "type": "Domain",
                        "location": {
                            "start": {"value": 90},
                            "end": {"value": 120, "modifier": "UNKNOWN"},
                        },
                    },
                ]
            }
        ),
        encoding="utf-8",
    )
    intervals = domain_intervals_span_relative(
        accession="QTEST", span_start=1, span_end=200, cache_dir=cache
    )
    ends = domain_ends_span_relative(
        accession="QTEST", span_start=1, span_end=200, cache_dir=cache
    )
    assert {(d.start, d.end) for d in intervals} == {(10, 40), (50, 80)}
    assert set(ends) == {40, 80}
    assert all(d.end in ends for d in intervals)
    assert domain_intervals_span_relative(
        accession="MISSING", span_start=1, span_end=200, cache_dir=cache
    ) == ()


# ── inventory / CLI ──────────────────────────────────────────────────────────


def test_cli_refuses_parent_id_outside_inventory_including_igf2r(tmp_path):
    assert OUT_OF_INVENTORY not in PIECEWISE_RESTITCH_PARENT_IDS
    assert OUT_OF_INVENTORY == 3356
    a, b = _two_domain_pair()
    man = tmp_path / "tiles.json"
    _write_piecewise_manifest(
        tmp_path, man, parent_job_id=OUT_OF_INVENTORY, tiles=[a, b], length=27
    )
    rc = piecewise_main(
        ["--manifest", str(man), "--out-root", str(tmp_path / "ops"), "--parent-id", str(OUT_OF_INVENTORY)]
    )
    assert rc == 2
    assert not (tmp_path / "ops" / "piecewise_kabsch" / str(OUT_OF_INVENTORY) / "stitched.pdb").exists()
    with pytest.raises(InventoryRefused):
        write_piecewise_kabsch_restitch(
            [a, b],
            27,
            tmp_path,
            parent_job_id=OUT_OF_INVENTORY,
            domain_intervals=TWO_DOMAIN_INTERVALS,
        )


def test_primary_three_are_not_a_named_exclusion():
    assert PRIMARY_THREE_PARENT_IDS == frozenset(PRIMARY_THREE)
    assert PRIMARY_THREE_PARENT_IDS <= KABSCH_RESTITCH_PARENT_IDS
    assert PRIMARY_THREE_PARENT_IDS <= PIECEWISE_RESTITCH_PARENT_IDS
    assert 3356 not in PIECEWISE_RESTITCH_PARENT_IDS
    assert len(PIECEWISE_RESTITCH_PARENT_IDS) == 27


def test_cli_accepts_a_primary_three_id_as_inventory(tmp_path):
    a, b = _two_domain_pair()
    man = tmp_path / "tiles.json"
    _write_piecewise_manifest(tmp_path, man, parent_job_id=2939, tiles=[a, b], length=27)
    rc = piecewise_main(["--manifest", str(man), "--out-root", str(tmp_path / "ops")])
    assert rc == 0
    assert (tmp_path / "ops" / "piecewise_kabsch" / "2939" / "stitched.pdb").is_file()


def test_sibling_modules_bytes_stay_pinned():
    root = Path(__file__).resolve().parent.parent
    assert hashlib.sha256((root / "core" / "hold48_kabsch.py").read_bytes()).hexdigest() == D125_KABSCH_SHA256
    assert hashlib.sha256((root / "core" / "hold48_confidence_kabsch.py").read_bytes()).hexdigest() == D126_CONF_SHA256


# ── ops report ───────────────────────────────────────────────────────────────


def test_ops_success_report_names_drops_vs_d125_and_d126_and_allows_zero_of_three():
    d125 = {pid: (pid not in PRIMARY_THREE_PARENT_IDS) for pid in KABSCH_RESTITCH_PARENT_IDS}
    d126 = dict(d125)
    d126[3368] = False  # a prior D-126 PASS that is not one of the three
    d126[3394] = True
    d127 = dict(d126)
    d127[2817] = False  # D-125 PASS → D-127 REFUSE
    d127[3368] = False
    report = build_ops_success_report(d125, d126, d127)
    payload = report.to_json()
    assert payload["n_d125_pass_d127_refuse"] == 2  # 2817 and 3368
    assert payload["n_d125_pass_d127_refuse_is_named_finding"] is True
    assert payload["n_d126_pass_d127_refuse"] == 1  # 2817 (3368 already D-126 refuse)
    assert payload["n_d126_pass_d127_refuse_is_named_finding"] is True
    assert payload["recovered_of_primary_three"] == 0
    assert payload["zero_of_three_recovered_is_allowed"] is True
    assert payload["d127_algorithm"] == ALGORITHM
    assert payload["d127_decision"] == DECISION
    assert RMSD_REFUSE_ANGSTROM == 10.0


def test_ops_report_counts_a_recovery_without_loosening_the_gate(tmp_path):
    d125 = {pid: (pid not in PRIMARY_THREE_PARENT_IDS) for pid in KABSCH_RESTITCH_PARENT_IDS}
    d126 = dict(d125)
    d127 = dict(d125)
    d127[2939] = True
    report = build_ops_success_report(d125, d126, d127)
    assert report.n_d126_refuse_d127_pass == 1
    assert report.recovered_of_primary_three == 1
    assert RMSD_REFUSE_ANGSTROM == 10.0
    d125_path = tmp_path / "d125.json"
    d126_path = tmp_path / "d126.json"
    d127_path = tmp_path / "d127.json"
    d125_path.write_text(json.dumps({str(k): v for k, v in d125.items()}), encoding="utf-8")
    d126_path.write_text(json.dumps({str(k): v for k, v in d126.items()}), encoding="utf-8")
    d127_path.write_text(json.dumps({str(k): v for k, v in d127.items()}), encoding="utf-8")
    rc = piecewise_main(
        [
            "--confusion-report",
            "--d125-outcomes",
            str(d125_path),
            "--d126-outcomes",
            str(d126_path),
            "--d127-outcomes",
            str(d127_path),
        ]
    )
    assert rc == 0


def test_weight_epsilon_is_pinned():
    assert WEIGHT_EPSILON == 1e-3
    from core.hold48_confidence_kabsch import pair_weight

    assert pair_weight(80.0, 40.0) == pytest.approx(0.40)
    assert pair_weight(0.0, 0.0) == pytest.approx(WEIGHT_EPSILON)
