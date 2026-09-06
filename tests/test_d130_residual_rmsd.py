"""D-130-A — residual-RMSD core. Tests that must be able to go red.

Hermetic fixtures. No Fly. No GPU. No restitch run of the 27. No ops numbers.
Cite D-130 Spec §1a / §1b / §2 / §3 / §5 / §11 and the existing
``winning_tile``. D-125 ``write_kabsch_restitch``, D-126
``write_confidence_kabsch_restitch``, D-127
``write_piecewise_kabsch_restitch``, D-128 ``write_linker_seam_restitch`` and
the assembler stay independently callable and byte-untouched.

WHAT THESE EXIST TO REDDEN, in the Spec's own order of danger.

**The floor read backwards.** ``rmsd_floor_angstrom <= 10.0`` proves
*nothing*: not that a passing fit exists, not that the parent is recoverable,
and never that the gate is too strict. The bound is exercised as
**arithmetic** — over real rigid transforms including far-from-optimal ones —
and its **non-tightness** is pinned too, because that is exactly why
``irreducible`` is *sufficient and never necessary*.

**A search dressed as an audit.** §1b's correction is decided by **residue
identity**. An offset chosen because it scored better is the thing this Spec
was written to refuse, so ambiguity (none *or* more than one agreeing offset)
must refuse rather than pick, and a pairing that was already right must not be
refitted.

**A fifth knob smuggled in.** The only fit permitted is D-125's, and the test
compares this module's transform against ``core.hold48_kabsch`` on the same
pairs rather than trusting the docstring. No window, no piece, no trim, no
weight, no third-party import.

**A statistic laundered across paths.** A prior path's recorded
``rmsd_angstrom`` is a *different statistic* in four of the five trees, so
``rigid_rmsd_angstrom`` is measured from that path's own artifacts and an
absence stays an absence — never a zero, never an assumed pass.
"""
from __future__ import annotations

import ast
import hashlib
import json
import math
import sys
from pathlib import Path

import pytest

from core.hold48_confidence_kabsch import (
    confidence_kabsch_out_dir,
    write_confidence_kabsch_restitch,
)
from core.hold48_kabsch import (
    OVERLAP_CA_MIN,
    REFUSE_OVERLAP_CA_LT_3,
    REFUSE_RMSD_GT_10,
    REFUSE_SINGULAR_COVARIANCE,
    RMSD_REFUSE_ANGSTROM,
    InventoryRefused,
    fit_overlap_kabsch,
    kabsch_out_dir,
    kabsch_rotation_translation,
    write_kabsch_restitch,
)
from core.hold48_linker_seam import linker_seam_out_dir, write_linker_seam_restitch
from core.hold48_piecewise_kabsch import piecewise_kabsch_out_dir
from core.hold48_residual_rmsd import (
    ABSENCE_REFUSED_BEFORE_TRANSFORM,
    ABSENCE_TREE_ABSENT,
    ACCEPT_REFUSE_PARENT_IDS,
    ALGORITHM,
    CLASS_IRREDUCIBLE,
    CLASS_PLACEMENT,
    CLASS_UNKNOWN,
    DECISION,
    DECOMPOSITION_PATHS,
    IDENTITY_DECLARED_PAIRING_AGREES,
    IDENTITY_MULTIPLE_OFFSETS_AGREE,
    IDENTITY_NO_OFFSET_AGREES,
    IDENTITY_UNIQUE_OFFSET,
    IDENTITY_UNREADABLE,
    NOT_SUCCESS_TARGET_PARENT_IDS,
    PATH_CONFIDENCE_KABSCH,
    PATH_KABSCH,
    PATH_LINKER_SEAM,
    PATH_PIECEWISE_KABSCH,
    PATH_RESIDUAL_RMSD,
    PHASE_4_PAIR_PARENT_IDS,
    REFUSE_CORRESPONDENCE_UNVERIFIABLE,
    REFUSE_REASONS,
    REFUSE_RMSD_IRREDUCIBLE,
    RESIDUAL_CLASSES,
    RESIDUAL_FLOOR_GATE_ANGSTROM,
    RESIDUAL_RMSD_RESTITCH_PARENT_IDS,
    SOURCE_ABSENT,
    SOURCE_MEASURED_FROM_ARTIFACTS,
    SOURCE_MEASURED_PRE_TRANSFORM,
    SiblingOverwriteRefused,
    audit_correspondence,
    build_ops_success_report,
    candidate_register_offsets,
    classify_residual,
    fit_correspondence,
    floor_exceeds_gate,
    internal_drmsd,
    paired_ca_for_offset,
    read_path_decomposition,
    refuse_sibling_overwrite,
    residual_rmsd_out_dir,
    rmsd_floor,
    write_residual_rmsd_restitch,
)
from core.hold48_stitch import TileFold, winning_tile
from scripts.residual_rmsd_restitch import main as d130_main
from tests.test_d125_kabsch import (
    IN_INVENTORY,
    OUT_OF_INVENTORY,
    _apply,
    _const_pae,
    _curve_xyz,
    _rot_z,
    _tile,
    _write_manifest,
)

MODULE = Path(__file__).resolve().parent.parent / "core" / "hold48_residual_rmsd.py"
CLI = Path(__file__).resolve().parent.parent / "scripts" / "residual_rmsd_restitch.py"

# Modules that must stay byte-identical: D-130-A is a sixth sibling, not an edit.
FROZEN_MODULES = {
    "core/hold48_kabsch.py": "4c7bb45d04507e2a67ba3600b35d6130d62843ca3bc99c15d3568d5cb105ff6e",
    "core/hold48_confidence_kabsch.py": "d526a856ec8f1ba978a3586f3dfcf4a0ee858da12132499f2db37368efc77f18",
    "core/hold48_piecewise_kabsch.py": "ad48b2be577b987466274000c508a621792bc029bb9e087eec94ba7237f13e04",
    "core/hold48_linker_seam.py": "c270f8711040471a9080a23ab4c1e167a0cc2eedf546c3481cd9ed4f4eb19843",
    "core/hold48_stitch.py": "6e2fcb643e4f5549297182e42def2a54fbb48d2e33659798d7314d56486ef629",
}

R_SEAM = _rot_z(35)
T_SEAM = (20.0, -9.0, 4.0)

AMINO_ACIDS = (
    "ALA", "CYS", "ASP", "GLU", "PHE", "GLY", "HIS", "ILE", "LYS", "LEU",
    "MET", "ASN", "PRO", "GLN", "ARG", "SER", "THR", "VAL", "TRP", "TYR",
)


def _sequence(n: int, seed: int = 12345) -> list[str]:
    """A deterministic, aperiodic residue sequence.

    ⚠ Aperiodic on purpose: a repeating sequence would make several register
    offsets agree on identity, which the audit is required to refuse. That is
    the *right* behaviour and it has its own test — but it would make the
    recovery fixture untestable, so this sequence is built not to trigger it.
    """
    out: list[str] = []
    x = seed
    for _ in range(n + 1):
        x = (1103515245 * x + 12345) % 2147483648
        out.append(AMINO_ACIDS[x % 20])
    return out


SEQ = _sequence(400)


def _helix(i: int, radius: float = 10.0, rise: float = 1.5, deg: float = 100.0):
    a = math.radians(deg * i)
    return (radius * math.cos(a), radius * math.sin(a), rise * i)


def _named_pdb(points, names) -> str:
    lines = []
    for serial, (xyz, name) in enumerate(zip(points, names), start=1):
        x, y, z = xyz
        lines.append(
            f"ATOM  {serial:5d}  CA  {name} A{serial:4d}    "
            f"{x:8.3f}{y:8.3f}{z:8.3f}  1.00 50.00           C  "
        )
    return "\n".join(lines) + "\n"


def _named_tile(start: int, points, names, *, plddt: float = 90.0) -> TileFold:
    n = len(points)
    return TileFold(
        start=start,
        end=start + n - 1,
        pdb=_named_pdb(points, names),
        plddt=[plddt] * n,
        pae=_const_pae(n),
    )


def _happy_pair():
    """Tile A 1–8; tile B 6–12 is A's overlap plus unique residues, rigidly moved."""
    a = _tile(1, [_curve_xyz(i) for i in range(8)], plddt=40.0, extra_cb=True)
    b = _tile(
        6,
        [_apply(R_SEAM, T_SEAM, _curve_xyz(i)) for i in range(5, 12)],
        plddt=90.0,
        extra_cb=True,
    )
    return a, b


def _irreducible_pair():
    """Two tiles whose overlap copies disagree about their OWN internal distances.

    No rigid transform can bring them within the gate, and the floor says so
    before anything is fitted.
    """
    a = _tile(1, [_curve_xyz(i) for i in range(12)], plddt=40.0)
    stretched = [(x * 9.0, y * 9.0, z * 9.0) for (x, y, z) in (_curve_xyz(i) for i in range(5, 16))]
    b = _tile(6, stretched, plddt=90.0)
    return a, b


REGISTER_SHIFT_AA = 3
#: Reference r pairs with moving ``r + EXPECTED_OFFSET_AA`` once identity has
#: spoken: B stores parent ``m + shift``'s residue at declared position ``m``,
#: so the agreeing register runs the other way.
EXPECTED_OFFSET_AA = -REGISTER_SHIFT_AA
_KICK = 28.0


def _kicked(p, kick: float):
    return (p[0] + kick, p[1] + kick * 0.5, p[2] - kick * 0.3)


def _reference_tile():
    """Parent 1–20 of the true backbone, with the true residue names."""
    return _named_tile(
        1, [_helix(r - 1) for r in range(1, 21)], [SEQ[r] for r in range(1, 21)], plddt=40.0
    )


def _register_error_pair(*, kick: float = _KICK, shift: int = REGISTER_SHIFT_AA, names=None):
    """A moving tile whose stored register is ``shift`` residues out.

    Reference A holds parent 1–20. Moving B declares parent 11–30 but its
    stored coordinates and residue names are those of parent ``11+shift`` –
    ``30+shift``, so the pairing every earlier path used compares the wrong Cα
    to the wrong Cα — and exactly one integer offset makes the residue
    identities agree again.

    ⚠ **A constructed fixture, not a physical story.** ``kick`` displaces the
    three moving residues the corrected register never reaches (18–20), purely
    so the *declared* correspondence lands in the Spec's ``placement`` class —
    floor inside the gate, achieved RMSD outside it — which is the only class
    §1b lets the audit run in. Without it a self-similar backbone fits its own
    shifted copy perfectly and the audit is (correctly) never reached.
    """
    a = _reference_tile()
    b_points = []
    for m in range(11, 31):
        p = _apply(R_SEAM, T_SEAM, _helix(m - 1 + shift))
        if m >= 18:
            p = _kicked(p, kick)
        b_points.append(p)
    if names is None:
        names = [SEQ[m + shift] for m in range(11, 31)]
    return a, _named_tile(11, b_points, names, plddt=90.0)


def _right_register_pair(*, kick: float = _KICK, names=None):
    """Reference and moving agree on register; the moving copy is still misplaced.

    Two of the overlap residues are displaced, so the declared correspondence
    sits in ``placement`` — the audit runs, finds the pairing already correct,
    and the seam refuses on D-125's own number rather than being refitted.
    """
    a = _reference_tile()
    b_points = []
    for m in range(11, 31):
        p = _apply(R_SEAM, T_SEAM, _helix(m - 1))
        if m <= 12:
            p = _kicked(p, kick)
        b_points.append(p)
    if names is None:
        names = [SEQ[m] for m in range(11, 31)]
    return a, _named_tile(11, b_points, names, plddt=90.0)


def _module_identifiers() -> set[str]:
    """Every name this module DEFINES or USES, from the AST.

    ⚠ Deliberately not a substring hunt over the source text. D-128-B learned
    that banning bare words fires on the very copy that forbids them — the
    docstring saying *"no window"* would trip a ban on ``window``, and a
    docstring is not a knob. Identifiers are the class the guard is about.
    """
    tree = ast.parse(MODULE.read_text(encoding="utf-8"))
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.add(node.name)
        elif isinstance(node, ast.Name):
            names.add(node.id)
        elif isinstance(node, ast.Attribute):
            names.add(node.attr)
        elif isinstance(node, ast.arg):
            names.add(node.arg)
        elif isinstance(node, ast.keyword) and node.arg:
            names.add(node.arg)
        elif isinstance(node, ast.alias):
            names.add((node.asname or node.name).split(".")[0])
    return names


def _module_imports() -> set[str]:
    """Top-level package each ``import`` in the module pulls in."""
    tree = ast.parse(MODULE.read_text(encoding="utf-8"))
    out: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            out.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            out.add(node.module.split(".")[0])
    return out


def _tree_digest(root: Path) -> dict[str, str]:
    return {
        str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(root.rglob("*"))
        if p.is_file()
    }


def _rows(result, path_name: str) -> list:
    return [row for row in result.decomposition if row.path == path_name]


def _dist(a, b):
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


# ── T-1200 — the floor is a proved bound, and it is not tight ────────────────


def test_the_floor_bounds_every_rigid_transform():
    """RMSD(R, t) >= dRMSD / 2 for EVERY rigid motion, not just the best one.

    ⚠ The Spec's load-bearing claim, checked as arithmetic. A module that
    computed a different constant, or that quietly divided by something else,
    fails here rather than in a report nobody can reproduce.
    """
    reference = [
        (0.0, 0.0, 0.0),
        (3.8, 0.0, 0.0),
        (7.1, 1.9, 0.0),
        (9.6, 4.8, 1.2),
        (10.4, 8.6, 3.1),
        (8.2, 11.9, 2.4),
    ]
    deformed = [
        (0.0, 0.0, 0.0),
        (3.8, 0.0, 0.0),
        (6.9, 2.2, 0.4),
        (7.4, 6.0, 2.9),
        (4.8, 9.1, 4.6),
        (0.9, 9.9, 3.3),
    ]
    floor = rmsd_floor(internal_drmsd(reference, deformed))
    assert floor is not None and floor > 0, "the fixture must actually disagree"

    def _rmsd(p, q):
        return math.sqrt(sum(_dist(a, b) ** 2 for a, b in zip(p, q)) / len(p))

    for deg in (0.0, 23.0, 63.0, 155.0, 338.0):
        for shift in ((0.0, 0.0, 0.0), (2.5, -1.0, 0.7), (-40.0, 12.0, 3.0)):
            moved = [_apply(_rot_z(deg), shift, p) for p in reference]
            assert _rmsd(moved, deformed) >= floor - 1e-9, (
                f"the floor must bound every rigid transform; failed at {deg=} {shift=}"
            )


def test_the_floor_constant_is_the_specs_and_is_attained():
    """⚠ Found by mutation: the bound above held with the divisor changed to 4.

    A test that only asserts ``RMSD >= floor`` is satisfied by a floor of
    ``dRMSD / 4``, or ``/ 400`` — **a weaker claim passes a weaker test**, and
    the clause the whole Spec rests on was unpinned. Two things are pinned
    here instead.

    First, the module's constant **is** the Spec's, checked as an identity
    rather than inferred from an inequality it cannot fail.

    Second, the constant is **attained**: on two corresponded points the best
    rigid placement achieves *exactly* ``dRMSD / 2``. So ``/ 2`` is the
    greatest lower bound the proof gives, not a conservative guess — and a
    divisor that made the bound "safer" would be reporting a floor no
    configuration can reach, which is a different (and weaker) claim than the
    one §1a makes.
    """
    for value in (0.0, 1.0, 4.0, 13.7):
        assert rmsd_floor(value) == value / 2.0

    # dRMSD's own normalisation, hand-computed rather than round-tripped.
    # n = 2 → one pair → dRMSD = |d^A - d^B|.
    a = [(0.0, 0.0, 0.0), (10.0, 0.0, 0.0)]
    b = [(0.0, 0.0, 0.0), (6.0, 0.0, 0.0)]
    assert internal_drmsd(a, b) == pytest.approx(4.0)
    floor = rmsd_floor(internal_drmsd(a, b))
    assert floor == pytest.approx(2.0)

    # The optimal placement of `a` onto `b`: shared centroid, shared axis.
    best = [(-2.0, 0.0, 0.0), (8.0, 0.0, 0.0)]
    achieved = math.sqrt(sum(_dist(p, q) ** 2 for p, q in zip(best, b)) / len(b))
    assert achieved == pytest.approx(floor), "the floor must be reachable, not merely safe"
    for deg in (0.0, 31.0, 97.0, 214.0):
        for shift in ((0.0, 0.0, 0.0), (7.0, -3.0, 1.0)):
            moved = [_apply(_rot_z(deg), shift, p) for p in a]
            got = math.sqrt(sum(_dist(p, q) ** 2 for p, q in zip(moved, b)) / len(b))
            assert got >= floor - 1e-9, "and nothing beats it"

    # n = 3 pins the 2 / (n(n-1)) normalisation independently of the n = 2 case.
    three_a = [(0.0, 0.0, 0.0), (10.0, 0.0, 0.0), (20.0, 0.0, 0.0)]
    three_b = [(0.0, 0.0, 0.0), (6.0, 0.0, 0.0), (12.0, 0.0, 0.0)]
    # pairwise distance differences: 4, 8, 4 → sqrt((16 + 64 + 16) / 3)
    assert internal_drmsd(three_a, three_b) == pytest.approx(math.sqrt(96.0 / 3.0))


def test_the_floor_is_rigid_invariant():
    """Moving one copy must not move the floor — that is why it bounds all paths."""
    a = [_curve_xyz(i) for i in range(9)]
    b = [(x * 1.4, y - 2.0, z * 0.6) for x, y, z in a]
    base = internal_drmsd(a, b)
    spun = [_apply(_rot_z(117.0), (11.0, -4.0, 2.0), p) for p in a]
    assert base is not None
    assert abs(internal_drmsd(spun, b) - base) < 1e-9


def test_the_bound_is_not_tight_so_irreducible_is_sufficient_never_necessary():
    """A zero floor coexists with an enormous achieved RMSD.

    ⚠ This is the arithmetic behind the Spec's hardest sentence. If the floor
    were tight, ``floor <= 10`` would be a promise. It is not one.
    """
    a = [_curve_xyz(i) for i in range(9)]
    far = [_apply(_rot_z(126.0), (95.0, -60.0, 40.0), p) for p in a]
    assert rmsd_floor(internal_drmsd(a, far)) < 1e-9
    achieved = math.sqrt(sum(_dist(p, q) ** 2 for p, q in zip(a, far)) / len(a))
    assert achieved > 50.0


def test_an_unmeasurable_drmsd_is_null_and_never_zero():
    """Fewer than two pairs is unknown, and unknown is not 0.0."""
    assert internal_drmsd([], []) is None
    assert internal_drmsd([(0.0, 0.0, 0.0)], [(1.0, 1.0, 1.0)]) is None
    assert rmsd_floor(None) is None
    with pytest.raises(ValueError):
        internal_drmsd([(0.0, 0.0, 0.0)], [])


# ── T-1201 — one-directional, and it refuses before any fit ──────────────────


def test_a_floor_over_the_gate_refuses_before_anything_is_fitted(tmp_path):
    a, b = _irreducible_pair()
    result = write_residual_rmsd_restitch(
        [a, b], 16, tmp_path, parent_job_id=3272, tile_job_ids=[3673, 3630]
    )
    seam = result.seams[0]
    assert seam.rmsd_floor_angstrom > RESIDUAL_FLOOR_GATE_ANGSTROM
    assert seam.refuse_reason == REFUSE_RMSD_IRREDUCIBLE
    assert seam.residual_class == CLASS_IRREDUCIBLE
    # ⚠ Certified BEFORE any transform: no fit was attempted, so the achieved
    # RMSD is null — and null is not 0.0.
    assert seam.rmsd_angstrom is None
    assert seam.pre_fit_rmsd_angstrom is None
    assert seam.max_ca_jump_angstrom is None
    # ⚠ §1b step 1: the audit runs ONLY on a `placement` seam. Auditing an
    # irreducible one could not help, and running it to see what happens is a
    # search — so the record carries no audit field at all, not even a zero.
    assert seam.correspondence_verified is None, "an irreducible seam is not audited"
    assert seam.register_offset_aa is None
    assert seam.identity_evidence is None
    row = json.loads(
        (result.out_dir / "seams.jsonl").read_text(encoding="utf-8").splitlines()[0]
    )
    assert row["correspondence_verified"] is None
    assert row["register_offset_aa"] is None
    assert row["identity_evidence"] is None
    assert row["floor_exceeds_gate"] is True
    assert result.accepted is False
    assert result.stitched is None
    assert not (result.out_dir / "stitched.pdb").exists()


def test_floor_exceeds_gate_is_three_valued_and_uses_the_existing_gate():
    assert RESIDUAL_FLOOR_GATE_ANGSTROM == RMSD_REFUSE_ANGSTROM == 10.0
    assert floor_exceeds_gate(10.5) is True
    assert floor_exceeds_gate(10.0) is False, "the gate is not loosened at the boundary"
    assert floor_exceeds_gate(0.0) is False
    assert floor_exceeds_gate(None) is None, "null is not False and not 0.0"


def test_the_module_computes_no_distance_to_recovery():
    """⚠ The failure this pins: a floor rendered as how close a parent is to a fix.

    A floor under the gate licenses nothing, so nothing in this module may
    subtract it from the gate, rank parents by it, or name a per-parent
    exception argued from it. Checked against **identifiers**, not prose — the
    docstrings that forbid these things say their names out loud.
    """
    names = _module_identifiers()
    for banned in (
        "distance_to_recovery",
        "recovery_forecast",
        "gate_exception",
        "per_parent_gate",
        "named_exclusion",
        "headroom",
        "recoverable",
    ):
        assert banned not in names, banned
    assert "FLOOR_UNDER_GATE_PROVES_NOTHING" in names
    assert "FLOOR_IS_SUFFICIENT_NEVER_NECESSARY" in names


# ── T-1202 — the three-valued class and its precedence ───────────────────────


def test_unknown_is_neither_irreducible_nor_placement():
    assert set(RESIDUAL_CLASSES) == {CLASS_IRREDUCIBLE, CLASS_PLACEMENT, CLASS_UNKNOWN}
    assert classify_residual(None, 4.0, 9) == CLASS_UNKNOWN
    assert classify_residual(2.0, None, 9) == CLASS_UNKNOWN
    assert classify_residual(2.0, 4.0, 2) == CLASS_UNKNOWN
    assert CLASS_UNKNOWN not in (CLASS_IRREDUCIBLE, CLASS_PLACEMENT)


def test_irreducible_wins_over_unknown_when_the_floor_is_known():
    """⚠ Precedence the Spec's table leaves open, and the certificate needs.

    §2 refuses on the floor *before* any fit, so an irreducible seam always
    has a null achieved RMSD. If ``unknown`` won that overlap, D-130's own
    path could never emit the certificate this Spec is built on.
    """
    assert classify_residual(12.0, None, 20) == CLASS_IRREDUCIBLE
    assert classify_residual(12.0, 30.0, 20) == CLASS_IRREDUCIBLE
    # A known floor is still required — a null floor cannot certify anything.
    assert classify_residual(None, None, 20) == CLASS_UNKNOWN


def test_a_pass_is_placement_and_is_never_counted_as_a_recovery_forecast():
    """A seam inside the gate was not certified impossible — but it is not a forecast.

    §11's ``n_placement`` keeps the Spec's own condition (achieved > 10.0), so
    a passing row lands in ``n_placement_within_gate`` instead of inflating the
    count the Spec calls "not a recovery forecast".
    """
    assert classify_residual(1.0, 2.0, 20) == CLASS_PLACEMENT
    assert classify_residual(1.0, 40.0, 20) == CLASS_PLACEMENT
    rows = [
        {"residual_class": CLASS_PLACEMENT, "rigid_rmsd_angstrom": 2.0, "rmsd_floor_angstrom": 1.0},
        {"residual_class": CLASS_PLACEMENT, "rigid_rmsd_angstrom": 40.0, "rmsd_floor_angstrom": 1.0},
        {"residual_class": CLASS_IRREDUCIBLE, "rigid_rmsd_angstrom": None, "rmsd_floor_angstrom": 12.0},
    ]
    report = build_ops_success_report({}, {}, {}, {}, {}, decomposition_rows=rows).to_json()
    assert report["n_placement"] == 1
    assert report["n_placement_within_gate"] == 1
    assert report["n_irreducible"] == 1
    assert report["n_placement_is_not_a_recovery_forecast"] is True


# ── T-1203 — §1a rows for every path, with per-field provenance ──────────────


def test_rows_are_written_for_every_path_even_when_a_tree_is_absent(tmp_path):
    a, b = _happy_pair()
    write_kabsch_restitch([a, b], 12, tmp_path, parent_job_id=IN_INVENTORY)
    result = write_residual_rmsd_restitch([a, b], 12, tmp_path, parent_job_id=IN_INVENTORY)

    assert {row.path for row in result.decomposition} == set(DECOMPOSITION_PATHS)
    for absent_path in (PATH_CONFIDENCE_KABSCH, PATH_PIECEWISE_KABSCH, PATH_LINKER_SEAM):
        rows = _rows(result, absent_path)
        assert len(rows) == 1
        row = rows[0]
        # ⚠ An absence, with a reason — never a zero and never an assumed pass.
        assert row.rigid_rmsd_angstrom is None
        assert row.internal_drmsd_angstrom is None
        assert row.rmsd_floor_angstrom is None
        assert row.floor_exceeds_gate is None
        assert row.residual_class == CLASS_UNKNOWN
        assert row.absence_reason == ABSENCE_TREE_ABSENT
        assert row.rigid_rmsd_source == SOURCE_ABSENT

    kabsch_row = _rows(result, PATH_KABSCH)[0]
    assert kabsch_row.rigid_rmsd_source == SOURCE_MEASURED_FROM_ARTIFACTS
    assert kabsch_row.internal_drmsd_source == SOURCE_MEASURED_PRE_TRANSFORM
    assert kabsch_row.rmsd_floor_angstrom is not None

    written = [
        json.loads(line)
        for line in (result.out_dir / "residual_decomposition.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
        if line.strip()
    ]
    assert len(written) == len(result.decomposition)
    for row in written:
        # The direction of the bound travels with every row (Spec §1a / §6).
        assert row["floor_over_gate_certifies_refusal"] is True
        assert row["floor_under_gate_proves_nothing"] is True
        assert row["floor_gate_angstrom"] == 10.0


def test_a_prior_path_that_refused_carries_a_null_achieved_rmsd(tmp_path):
    """A refused path wrote no PDB, so its achieved RMSD is unknown, not zero."""
    a, b = _irreducible_pair()
    d125 = write_kabsch_restitch([a, b], 16, tmp_path, parent_job_id=3272)
    assert d125.accepted is False
    result = write_residual_rmsd_restitch([a, b], 16, tmp_path, parent_job_id=3272)
    row = _rows(result, PATH_KABSCH)[0]
    assert row.rigid_rmsd_angstrom is None
    assert row.absence_reason == ABSENCE_REFUSED_BEFORE_TRANSFORM
    assert row.rigid_rmsd_source == SOURCE_ABSENT
    # The floor is still known — it is a property of the two tiles, not of a path.
    assert row.rmsd_floor_angstrom is not None
    assert row.residual_class == CLASS_IRREDUCIBLE


def test_the_achieved_rmsd_is_measured_not_copied_from_a_prior_record(tmp_path):
    """⚠ The laundering this pins: four different statistics in one column.

    D-126's recorded ``rmsd_angstrom`` is trimmed and pLDDT-weighted. If this
    module copied it into ``rigid_rmsd_angstrom`` — a column headed
    *full-overlap RMSD* — the D-126 lie surface would reappear one level up.
    So the recorded number and the measured one are checked to be **different
    quantities**, and the row's source says which it is.
    """
    a, b = _happy_pair()
    write_confidence_kabsch_restitch([a, b], 12, tmp_path, parent_job_id=IN_INVENTORY)
    result = write_residual_rmsd_restitch([a, b], 12, tmp_path, parent_job_id=IN_INVENTORY)
    row = _rows(result, PATH_CONFIDENCE_KABSCH)[0]
    assert row.rigid_rmsd_source == SOURCE_MEASURED_FROM_ARTIFACTS

    recorded = [
        json.loads(line)
        for line in (confidence_kabsch_out_dir(tmp_path, IN_INVENTORY) / "seams.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
        if line.strip()
    ]
    assert recorded, "the D-126 tree must have written a seam row to compare against"
    assert "read_from_path_record" not in json.dumps(row.to_json_row())
    source = MODULE.read_text(encoding="utf-8")
    assert 'row.get("rmsd_angstrom")' not in source, (
        "a prior path's recorded rmsd_angstrom must never become rigid_rmsd_angstrom"
    )


def test_a_d130_run_leaves_every_prior_tree_byte_unchanged(tmp_path):
    """Prior trees are READ. A sixth path that edited a fifth would fail here."""
    a, b = _happy_pair()
    write_kabsch_restitch([a, b], 12, tmp_path, parent_job_id=IN_INVENTORY)
    write_confidence_kabsch_restitch([a, b], 12, tmp_path, parent_job_id=IN_INVENTORY)
    write_linker_seam_restitch([a, b], 12, tmp_path, parent_job_id=IN_INVENTORY)
    before = {
        name: _tree_digest(tree)
        for name, tree in (
            ("kabsch", kabsch_out_dir(tmp_path, IN_INVENTORY)),
            ("confidence_kabsch", confidence_kabsch_out_dir(tmp_path, IN_INVENTORY)),
            ("linker_seam", linker_seam_out_dir(tmp_path, IN_INVENTORY)),
        )
    }
    write_residual_rmsd_restitch([a, b], 12, tmp_path, parent_job_id=IN_INVENTORY)
    after = {
        name: _tree_digest(tree)
        for name, tree in (
            ("kabsch", kabsch_out_dir(tmp_path, IN_INVENTORY)),
            ("confidence_kabsch", confidence_kabsch_out_dir(tmp_path, IN_INVENTORY)),
            ("linker_seam", linker_seam_out_dir(tmp_path, IN_INVENTORY)),
        )
    }
    assert after == before
    assert not piecewise_kabsch_out_dir(tmp_path, IN_INVENTORY).exists()


def test_an_empty_prior_tree_reports_its_own_reason(tmp_path):
    tree = piecewise_kabsch_out_dir(tmp_path, IN_INVENTORY)
    tree.mkdir(parents=True)
    rows = read_path_decomposition(tmp_path, IN_INVENTORY, PATH_PIECEWISE_KABSCH, {})
    assert len(rows) == 1
    assert rows[0].absence_reason == "no_seam_rows"
    assert rows[0].residual_class == CLASS_UNKNOWN


# ── T-1204 — the audit is decided by identity, never by score ────────────────


def test_a_verified_declared_pairing_is_not_refitted(tmp_path):
    """If the pairing was already right, D-125 already achieved the optimum.

    Refitting the same pairs would recover nothing **by construction**, so the
    seam refuses on D-125's own number rather than pretending to try again.
    """
    a, b = _right_register_pair()
    audit = audit_correspondence(a, b)
    assert audit.correspondence_verified is True
    assert audit.register_offset_aa == 0
    assert audit.identity_evidence == IDENTITY_DECLARED_PAIRING_AGREES
    assert audit.corrected is False

    result = write_residual_rmsd_restitch([a, b], 30, tmp_path, parent_job_id=3394)
    seam = result.seams[0]
    assert seam.residual_class == CLASS_PLACEMENT
    assert seam.rmsd_floor_angstrom <= RESIDUAL_FLOOR_GATE_ANGSTROM
    assert seam.refuse_reason == REFUSE_RMSD_GT_10
    assert seam.register_offset_aa == 0
    assert seam.recovered is False
    assert result.accepted is False
    assert result.recovered is False


def test_a_unique_identity_determined_offset_is_the_correction(tmp_path):
    a, b = _register_error_pair()
    audit = audit_correspondence(a, b)
    assert audit.correspondence_verified is False
    assert audit.register_offset_aa == EXPECTED_OFFSET_AA
    assert audit.identity_evidence == IDENTITY_UNIQUE_OFFSET
    assert audit.n_candidate_offsets == 1
    assert audit.corrected is True

    result = write_residual_rmsd_restitch(
        [a, b], 30, tmp_path, parent_job_id=3272, tile_job_ids=[3673, 3630]
    )
    seam = result.seams[0]
    assert seam.pre_fit_rmsd_angstrom > RMSD_REFUSE_ANGSTROM, (
        "the declared pairing must be the one that fails, or the audit never runs"
    )
    assert seam.correspondence_verified is False
    assert seam.register_offset_aa == EXPECTED_OFFSET_AA
    assert seam.refuse_reason is None
    assert seam.rmsd_angstrom <= RMSD_REFUSE_ANGSTROM
    assert seam.recovered is True
    assert result.accepted is True
    assert result.recovered is True
    assert (result.out_dir / "tile2_transformed.pdb").exists()


def test_no_agreeing_offset_refuses_rather_than_guessing(tmp_path):
    """Identity says nothing; the audit says so and refuses."""
    # A moving tile whose residue names come from a different sequence entirely.
    other = _sequence(400, seed=999)
    a, b = _right_register_pair(names=[other[m] for m in range(11, 31)])
    audit = audit_correspondence(a, b)
    assert audit.refuse_reason == REFUSE_CORRESPONDENCE_UNVERIFIABLE
    assert audit.identity_evidence == IDENTITY_NO_OFFSET_AGREES
    assert audit.register_offset_aa is None

    result = write_residual_rmsd_restitch([a, b], 30, tmp_path, parent_job_id=3272)
    seam = result.seams[0]
    assert seam.refuse_reason == REFUSE_CORRESPONDENCE_UNVERIFIABLE
    assert seam.rmsd_angstrom is None
    assert result.accepted is False


def test_more_than_one_agreeing_offset_refuses_instead_of_picking_one(tmp_path):
    """⚠ Ambiguity is a refusal, not an invitation to choose by score.

    A repeating residue sequence makes several registers agree on identity.
    The Spec's answer is to refuse, and a module that broke the tie by RMSD —
    by taking the offset that fitted best — would pass its own happy path and
    fail here.
    """
    poly = ["GLY"] * 400
    a_poly = _named_tile(
        1, [_helix(r - 1) for r in range(1, 21)], [poly[r] for r in range(1, 21)], plddt=40.0
    )
    # A homopolymer agrees at offset 0 too, so the declared pairing verifies
    # and there is nothing to correct — which is itself a refusal, not a pick.
    _a, b = _register_error_pair(names=[poly[m] for m in range(11, 31)])
    assert audit_correspondence(a_poly, b).correspondence_verified is True

    # Break offset 0 alone, so the search runs and finds many candidates.
    names = [poly[m] for m in range(11, 31)]
    names[0] = "TRP"
    _a, b_broken = _register_error_pair(names=names)
    a = a_poly
    broken = audit_correspondence(a, b_broken)
    assert broken.refuse_reason == REFUSE_CORRESPONDENCE_UNVERIFIABLE
    assert broken.identity_evidence == IDENTITY_MULTIPLE_OFFSETS_AGREE
    assert broken.n_candidate_offsets > 1
    assert broken.register_offset_aa is None, "no offset may be chosen from a tie"

    result = write_residual_rmsd_restitch([a, b_broken], 30, tmp_path, parent_job_id=3394)
    assert result.seams[0].refuse_reason == REFUSE_CORRESPONDENCE_UNVERIFIABLE
    assert result.accepted is False


def test_unreadable_residue_identity_refuses(tmp_path):
    """A blank residue name is not an identity, and two blanks are not a match."""
    a = _named_tile(
        1, [_helix(r - 1) for r in range(1, 21)], ["UNK"] * 20, plddt=40.0
    )
    _a, b = _right_register_pair(names=["UNK"] * 20)
    audit = audit_correspondence(a, b)
    assert audit.refuse_reason == REFUSE_CORRESPONDENCE_UNVERIFIABLE
    assert audit.identity_evidence == IDENTITY_UNREADABLE
    assert audit.correspondence_verified is False


def test_the_audit_never_reads_a_score():
    """⚠ The whole difference between an indexing fix and tuning.

    ``audit_correspondence`` is handed two tiles and nothing else. It must not
    reach for an RMSD, a pLDDT, or a seam jump to break a tie.
    """
    source = MODULE.read_text(encoding="utf-8")
    body = source.split("def audit_correspondence", 1)[1].split("\ndef ", 1)[0]
    for banned in ("rmsd", "plddt", "weight", "jump", "min(", "max(", "sorted("):
        assert banned not in body.lower().replace("never by rmsd", ""), banned


# ── T-1205 — the corrected correspondence is the FULL identity-agreeing overlap


def test_the_corrected_correspondence_is_the_full_overlap_and_is_never_trimmed():
    """Dropping pairs to improve a number is trim, and trim is forbidden."""
    a, b = _register_error_pair()
    moving, ref, pairs = paired_ca_for_offset(a, b, EXPECTED_OFFSET_AA)
    assert len(moving) == len(ref) == len(pairs)
    expected = [
        (r, r + EXPECTED_OFFSET_AA)
        for r in range(a.start, a.end + 1)
        if b.start <= r + EXPECTED_OFFSET_AA <= b.end
    ]
    assert pairs == expected, "every identity-agreeing pair must be kept"
    names = _module_identifiers()
    for banned in ("trim", "trim_loop", "drop_worst", "keep_best", "subset", "prune"):
        assert banned not in names, banned


def test_candidate_offsets_are_derived_from_the_spans_not_tuned():
    """No scan width to widen: the range is fixed by the two tile spans."""
    a, b = _register_error_pair()
    offsets = candidate_register_offsets(a, b)
    assert offsets, "there must be candidates to be unique among"
    assert min(offsets) >= b.start - a.end
    assert max(offsets) <= b.end - a.start
    for k in offsets:
        assert len(paired_ca_for_offset(a, b, k)[2]) >= OVERLAP_CA_MIN
    names = _module_identifiers()
    for banned in ("SEARCH_HALF_WIDTH", "WINDOW_HALF_WIDTH_AA", "OFFSET_SCAN_WIDTH"):
        assert banned not in names, banned


# ── T-1206 — the fit is D-125's, unchanged ───────────────────────────────────


def test_the_fit_is_d125s_transform_on_the_same_pairs():
    """Not "equivalent to" D-125 — the same numbers, from the same function."""
    a, b = _happy_pair()
    moving, ref, _pairs = paired_ca_for_offset(a, b, 0)
    fit = fit_correspondence(moving, ref)
    R, t, rmsd, _rank = kabsch_rotation_translation(moving, ref)
    assert fit.rotation == R
    assert fit.translation == t
    assert fit.rmsd_angstrom == rmsd
    d125 = fit_overlap_kabsch(a, b)
    assert fit.n_ca == d125.n_ca
    assert fit.rmsd_angstrom == pytest.approx(d125.rmsd_angstrom)


def test_the_whole_moving_tile_is_transformed_not_a_window(tmp_path):
    """D-125's apply unit. A window transform would leave outside atoms fixed."""
    a, b = _happy_pair()
    result = write_residual_rmsd_restitch([a, b], 12, tmp_path, parent_job_id=IN_INVENTORY)
    assert result.accepted is True
    moved = result.tiles[1]
    assert moved.pdb != b.pdb
    original = [line for line in b.pdb.splitlines() if line.startswith("ATOM")]
    transformed = [line for line in moved.pdb.splitlines() if line.startswith("ATOM")]
    assert len(original) == len(transformed)
    unchanged = [o for o, n in zip(original, transformed) if o[30:54] == n[30:54]]
    assert unchanged == [], "every atom of the moving tile moves, not a window's worth"


def test_the_module_defines_no_window_no_piece_no_weight():
    """A fifth knob would have to appear here first — as a NAME, not as prose."""
    names = _module_identifiers()
    for banned in (
        "WINDOW_HALF_WIDTH_AA",
        "WEIGHT_EPSILON",
        "pair_weight",
        "weighted_kabsch_rotation_translation",
        "DomainInterval",
        "inherit_piece_for_residue",
        "domain_pieces",
        "window_overlap_ca",
        "fit_seam_window",
        "apply_window_transform_pdb",
    ):
        assert banned not in names, banned


# ── T-1207 — refuse table, fail closed, all-or-nothing ───────────────────────


def test_overlap_ca_lt_3_refuses(tmp_path):
    a = _tile(1, [_curve_xyz(i) for i in range(5)], plddt=90.0)
    b = _tile(4, [_curve_xyz(i) for i in range(3, 8)], plddt=80.0)  # overlap 4–5
    result = write_residual_rmsd_restitch([a, b], 8, tmp_path, parent_job_id=IN_INVENTORY)
    seam = result.seams[0]
    assert seam.n_overlap_ca == 2
    assert seam.refuse_reason == REFUSE_OVERLAP_CA_LT_3
    assert seam.rmsd_floor_angstrom is None
    assert seam.residual_class == CLASS_UNKNOWN
    assert result.accepted is False


def test_singular_covariance_refuses(tmp_path):
    line = [(i * 3.8, 0.0, 0.0) for i in range(6)]
    a = _tile(1, line, plddt=90.0)
    b = _tile(1, [(x + 4.0, y, z) for x, y, z in line], plddt=80.0)
    result = write_residual_rmsd_restitch([a, b], 6, tmp_path, parent_job_id=IN_INVENTORY)
    seam = result.seams[0]
    assert seam.refuse_reason == REFUSE_SINGULAR_COVARIANCE
    assert seam.rmsd_angstrom is None
    assert result.accepted is False


def test_a_refuse_writes_its_rows_and_clears_a_prior_success(tmp_path):
    """A refuse is a recorded outcome — and it may not wear an earlier accept."""
    good_a, good_b = _happy_pair()
    ok = write_residual_rmsd_restitch(
        [good_a, good_b], 12, tmp_path, parent_job_id=IN_INVENTORY
    )
    assert ok.accepted is True
    assert (ok.out_dir / "stitched.pdb").exists()
    assert (ok.out_dir / "tile2_transformed.pdb").exists()

    bad_a, bad_b = _irreducible_pair()
    bad = write_residual_rmsd_restitch([bad_a, bad_b], 16, tmp_path, parent_job_id=IN_INVENTORY)
    assert bad.accepted is False
    assert bad.out_dir == ok.out_dir
    assert not (bad.out_dir / "stitched.pdb").exists()
    assert not (bad.out_dir / "tile2_transformed.pdb").exists()
    # The rows survive: a refuse is recorded, not a gap.
    assert (bad.out_dir / "seams.jsonl").read_text(encoding="utf-8").strip()
    assert (bad.out_dir / "residual_decomposition.jsonl").read_text(encoding="utf-8").strip()
    prov = json.loads((bad.out_dir / "provenance.json").read_text(encoding="utf-8"))
    assert prov["accepted"] is False
    assert prov["recovered"] is False
    assert prov["algorithm"] == ALGORITHM
    assert prov["decision"] == DECISION
    assert prov["served_path"] == "assembler"
    assert prov["seams_solved"] is False
    assert prov["zero_of_two_recovered_is_allowed"] is True


def test_the_parent_is_all_or_nothing(tmp_path):
    """One refusing seam refuses the parent — no partial transformed tile."""
    a = _tile(1, [_curve_xyz(i) for i in range(12)], plddt=40.0)
    b = _tile(
        6,
        [_apply(R_SEAM, T_SEAM, _curve_xyz(i)) for i in range(5, 18)],
        plddt=90.0,
    )
    bad = _tile(
        14,
        [(x * 9.0, y * 9.0, z * 9.0) for x, y, z in (_curve_xyz(i) for i in range(13, 26))],
        plddt=95.0,
    )
    result = write_residual_rmsd_restitch([a, b, bad], 26, tmp_path, parent_job_id=IN_INVENTORY)
    assert result.accepted is False
    assert any(s.refuse_reason for s in result.seams)
    assert result.stitched is None
    assert not list(result.out_dir.glob("tile*_transformed.pdb"))


def test_the_refuse_reason_set_is_the_specs_and_conflates_no_prior_name():
    """⚠ A reason name from another algorithm is a different measurement."""
    assert REFUSE_REASONS == {
        REFUSE_OVERLAP_CA_LT_3,
        REFUSE_RMSD_IRREDUCIBLE,
        REFUSE_CORRESPONDENCE_UNVERIFIABLE,
        REFUSE_RMSD_GT_10,
        REFUSE_SINGULAR_COVARIANCE,
    }
    assert "linker_jump_gt_10" not in REFUSE_REASONS, "that is D-127's, after linker inherit"
    assert "seam_jump_gt_10" not in REFUSE_REASONS, "that is D-128's, after a window transform"
    source = MODULE.read_text(encoding="utf-8")
    for foreign in ("REFUSE_LINKER_JUMP_GT_10", "REFUSE_SEAM_JUMP_GT_10"):
        assert foreign not in source, foreign


# ── T-1208 — the sixth tree, no overwrite, the inventory ─────────────────────


def test_the_sixth_tree_name_collides_with_none_of_the_five(tmp_path):
    out = residual_rmsd_out_dir(tmp_path, IN_INVENTORY)
    assert out.parts[-2:] == ("residual_rmsd", str(IN_INVENTORY))
    others = {
        kabsch_out_dir(tmp_path, IN_INVENTORY),
        confidence_kabsch_out_dir(tmp_path, IN_INVENTORY),
        piecewise_kabsch_out_dir(tmp_path, IN_INVENTORY),
        linker_seam_out_dir(tmp_path, IN_INVENTORY),
        tmp_path / str(IN_INVENTORY),
    }
    assert out not in others


def test_a_write_onto_any_prior_tree_is_refused(tmp_path):
    out = residual_rmsd_out_dir(tmp_path, IN_INVENTORY)
    for other in (
        tmp_path / str(IN_INVENTORY),
        kabsch_out_dir(tmp_path, IN_INVENTORY),
        confidence_kabsch_out_dir(tmp_path, IN_INVENTORY),
        piecewise_kabsch_out_dir(tmp_path, IN_INVENTORY),
        linker_seam_out_dir(tmp_path, IN_INVENTORY),
    ):
        with pytest.raises(SiblingOverwriteRefused):
            refuse_sibling_overwrite(other, other, None, None, None, None)
    # A destination nobody named, outside the sixth tree, is refused too.
    with pytest.raises(SiblingOverwriteRefused):
        refuse_sibling_overwrite(tmp_path / "somewhere_else")
    refuse_sibling_overwrite(out, tmp_path / str(IN_INVENTORY))


def test_a_parent_outside_the_27_is_refused(tmp_path):
    a, b = _happy_pair()
    with pytest.raises(InventoryRefused):
        write_residual_rmsd_restitch([a, b], 12, tmp_path, parent_job_id=OUT_OF_INVENTORY)
    assert not (tmp_path / "residual_rmsd").exists()


def test_the_phase_4_pair_is_the_inventory_and_phase_5_is_not_reopened():
    assert PHASE_4_PAIR_PARENT_IDS == {3272, 3394}
    assert ACCEPT_REFUSE_PARENT_IDS == {2938, 2939, 3179, 3190, 3321, 3368, 3566, 3432}
    assert not PHASE_4_PAIR_PARENT_IDS & ACCEPT_REFUSE_PARENT_IDS, "the fate sets are disjoint"
    assert NOT_SUCCESS_TARGET_PARENT_IDS == ACCEPT_REFUSE_PARENT_IDS
    # Recorded, never a success target — and still inside the runnable 27.
    assert ACCEPT_REFUSE_PARENT_IDS <= RESIDUAL_RMSD_RESTITCH_PARENT_IDS
    assert PHASE_4_PAIR_PARENT_IDS <= RESIDUAL_RMSD_RESTITCH_PARENT_IDS
    assert len(RESIDUAL_RMSD_RESTITCH_PARENT_IDS) == 27


def test_an_accept_refuse_parent_can_be_recorded_without_becoming_a_target(tmp_path):
    a, b = _happy_pair()
    result = write_residual_rmsd_restitch([a, b], 12, tmp_path, parent_job_id=3368)
    assert result.accepted is True
    assert result.recovered is False, "an accept with no register correction is not a recovery"
    report = build_ops_success_report(
        {3368: False}, {3368: True}, {3368: False}, {3368: False}, {3368: True},
        d130_recovered={3368: True},
    ).to_json()
    assert report["recovered_of_two"] == 0, "only 3272 / 3394 can be a Phase 4 recovery"
    assert report["phase_5_not_reopened"] is True


# ── T-1209 — the §11 report and module hygiene ───────────────────────────────


def test_the_ops_report_carries_every_required_field():
    report = build_ops_success_report({}, {}, {}, {}, {}).to_json()
    for field in (
        "n_overlap_pairs_measured",
        "n_irreducible",
        "n_placement",
        "n_residual_unknown",
        "n_correspondence_audited",
        "n_correspondence_corrected",
        "n_correspondence_unverifiable",
        "recovered_of_two",
        "n_d125_pass_d130_refuse",
        "n_d126_pass_d130_refuse",
        "n_d127_pass_d130_refuse",
        "n_d128_pass_d130_refuse",
        "n_d126_recovered_d130_refuse",
    ):
        assert field in report, field
    assert report["zero_of_two_recovered_is_allowed"] is True
    assert report["named_refuse_after_a_failed_hunt_is_a_complete_outcome"] is True
    assert report["unknown_is_neither_irreducible_nor_placement"] is True
    assert report["seams_solved"] is False
    assert report["served_path"] == "assembler"


def test_zero_recovered_names_its_source_and_is_never_a_measured_zero():
    """⚠ A zero with no record behind it is not a finding — say which it is."""
    no_map = build_ops_success_report({}, {}, {}, {}, {}).to_json()
    assert no_map["recovered_of_two"] == 0
    assert no_map["recovered_of_two_source"] == "none_supplied"
    measured = build_ops_success_report(
        {}, {}, {}, {}, {}, d130_recovered={3272: False, 3394: False}
    ).to_json()
    assert measured["recovered_of_two"] == 0
    assert measured["recovered_of_two_source"] == "recovery_records"
    both = build_ops_success_report(
        {}, {}, {}, {}, {}, d130_recovered={3272: True, 3394: True}
    ).to_json()
    assert both["recovered_of_two"] == 2


def test_a_drop_on_a_prior_paths_pass_set_is_a_named_finding():
    """⚠ Do not bury a drop inside an overall accept count."""
    d125 = {3272: True, 3394: True}
    d126 = {3272: False, 3394: True}
    d127 = {3272: False, 3394: False}
    d128 = {3272: False, 3394: False}
    d130 = {3272: False, 3394: False}
    report = build_ops_success_report(d125, d126, d127, d128, d130).to_json()
    assert report["n_d125_pass_d130_refuse"] == 2
    assert report["n_d126_pass_d130_refuse"] == 1
    assert report["n_d127_pass_d130_refuse"] == 0
    assert report["n_d128_pass_d130_refuse"] == 0
    assert report["n_d125_pass_d130_refuse_is_named_finding"] is True
    assert report["n_d126_pass_d130_refuse_is_named_finding"] is True
    # 3394 is one of the two D-126 OPS recovered, so refusing it is named.
    assert report["n_d126_recovered_d130_refuse"] == 1
    assert report["n_d126_recovered_d130_refuse_is_named_finding"] is True


def test_the_module_imports_no_third_party_package():
    """CPU, stdlib, no rent — the D-125-A through D-128-A footprint.

    Checked against the import graph rather than the prose, and against the
    interpreter's own stdlib list rather than a hand-kept allowlist that would
    quietly bless a new dependency someone remembered to add to it.
    """
    imports = _module_imports()
    assert imports, "the guard must actually see the imports"
    for name in imports:
        assert name in sys.stdlib_module_names or name == "core", (
            f"{name} is neither stdlib nor this repo's core — D-130-A is CPU, "
            "zero third-party, no rent"
        )
    names = _module_identifiers()
    for banned in ("requests", "httpx", "runpod", "torch", "numpy"):
        assert banned not in names, banned


def test_the_prior_modules_stay_byte_identical():
    """D-130-A is a sixth sibling. Editing a fifth would be a different PR."""
    root = Path(__file__).resolve().parent.parent
    for name, digest in FROZEN_MODULES.items():
        path = root / name
        assert path.is_file(), name
        assert hashlib.sha256(path.read_bytes()).hexdigest() == digest, (
            f"{name} was edited — D-130-A adds a module beside the five, it does not "
            "touch their geometry, thresholds, or served bytes"
        )


def test_the_assembler_is_called_and_never_replaced():
    source = MODULE.read_text(encoding="utf-8")
    assert "winning_tile" in source
    assert "write_stitched" in source
    assert "def winning_tile" not in source, "the assembler is imported, not re-implemented"
    assert winning_tile is not None


# ── the CLI ──────────────────────────────────────────────────────────────────


def test_cli_restitches_into_the_sixth_tree(tmp_path, capsys):
    a, b = _happy_pair()
    manifest = tmp_path / "tiles.json"
    _write_manifest(tmp_path, manifest, parent_job_id=IN_INVENTORY, tiles=[a, b], length=12)
    out_root = tmp_path / "ops"
    code = d130_main(["--manifest", str(manifest), "--out-root", str(out_root)])
    assert code == 0
    tree = residual_rmsd_out_dir(out_root, IN_INVENTORY)
    assert (tree / "provenance.json").is_file()
    assert (tree / "residual_decomposition.jsonl").is_file()
    err = capsys.readouterr().err
    assert "seams measured, not solved" in err
    assert "one-directional" in err


def test_cli_refuses_a_parent_outside_the_inventory(tmp_path, capsys):
    a, b = _happy_pair()
    manifest = tmp_path / "tiles.json"
    _write_manifest(tmp_path, manifest, parent_job_id=OUT_OF_INVENTORY, tiles=[a, b], length=12)
    code = d130_main(["--manifest", str(manifest), "--out-root", str(tmp_path / "ops")])
    assert code == 2
    assert "not in the D-125 27-id inventory" in capsys.readouterr().err


def test_cli_decomposition_report_needs_the_input_tiles(tmp_path, capsys):
    """⚠ The floor comes from the pre-transform tiles; it is not guessed from a tree."""
    code = d130_main(
        ["--decomposition-report", "--out-root", str(tmp_path), "--parent-id", "3272"]
    )
    assert code == 2
    assert "needs --manifest" in capsys.readouterr().err


def test_cli_decomposition_report_reads_without_writing(tmp_path, capsys):
    a, b = _happy_pair()
    manifest = tmp_path / "tiles.json"
    _write_manifest(tmp_path, manifest, parent_job_id=IN_INVENTORY, tiles=[a, b], length=12)
    out_root = tmp_path / "ops"
    out_root.mkdir()
    code = d130_main(
        [
            "--decomposition-report",
            "--out-root", str(out_root),
            "--parent-id", str(IN_INVENTORY),
            "--manifest", str(manifest),
        ]
    )
    assert code == 0
    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert {row["path"] for row in payload["residual_decomposition"]} == set(DECOMPOSITION_PATHS[:-1])
    assert "proves NOTHING" in captured.err
    assert not (out_root / "residual_rmsd").exists(), "a report writes nothing"


def test_cli_confusion_report_names_the_drop(tmp_path, capsys):
    def _write(name: str, payload: dict) -> str:
        path = tmp_path / name
        path.write_text(json.dumps(payload), encoding="utf-8")
        return str(path)

    args = [
        "--confusion-report",
        "--d125-outcomes", _write("d125.json", {"3272": True, "3394": True}),
        "--d126-outcomes", _write("d126.json", {"3272": False, "3394": True}),
        "--d127-outcomes", _write("d127.json", {"3272": False, "3394": False}),
        "--d128-outcomes", _write("d128.json", {"3272": False, "3394": False}),
        "--d130-outcomes",
        _write(
            "d130.json",
            {
                "3272": {"accepted": False, "recovered": False},
                "3394": {"accepted": False, "recovered": False},
            },
        ),
    ]
    assert d130_main(args) == 0
    captured = capsys.readouterr()
    report = json.loads(captured.out)
    assert report["recovered_of_two"] == 0
    assert report["recovered_of_two_source"] == "recovery_records"
    assert report["n_d125_pass_d130_refuse"] == 2
    assert "named finding" in captured.err
    assert "pre-registered allowed outcome" in captured.err
