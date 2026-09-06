"""D-128-A — linker / seam honesty, then the existing winning_tile assembler.

Two halves, and the **required** one is the measurement.

**§1a (required).** For every experimental path tree — D-125 ``kabsch/``,
D-126 ``confidence_kabsch/``, D-127 ``piecewise_kabsch/`` and D-128's own
``linker_seam/`` — record, per seam, the max Cα jump that path **ends**
with and whether the path is therefore **honest** at that seam
(``> 10.0`` Å is dishonest). Null is not ``0.0`` and unknown is not
honest. Prior trees are **read**; the rows land in the D-128 tree.

**§1b (optional).** One weighted rigid ``R, t`` on Cα inside a **±32 aa**
window around the offending linker / seam centre, applied to that
window's moving-tile atoms only. Smaller than D-127, not larger:
**no per-domain pieces, no piece list, no domain intervals as the fit
unit, no linker-inherit** — that family is D-127's and stays D-127's.
**No trim loop** (the D-126 lie surface). Repairing **0 of 7** is an
allowed outcome; it is not a licence to move a gate.

Seams are **recorded**, not solved. This module never claims otherwise.
It does **not** replace ``core.hold48_stitch.winning_tile``, does **not**
overwrite the assembler / D-125 / D-126 / D-127 trees, does **not**
jointly place a holoprotein, and does **not** enter F-004.

ZERO third-party imports. Reuses D-125 stdlib SVD + D-126 weighted
Kabsch. Refuse v1 (Spec §2): window Cα ``< 3``; window weighted RMSD
``> 10.0`` Å; covariance rank ``< 2``; **post-apply seam** max Cα jump
``> 10.0`` Å. Fail closed + all-or-nothing parent.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping, Optional, Sequence

from core.hold48_confidence_kabsch import (
    ALGORITHM as D126_ALGORITHM,
    DECISION as D126_DECISION,
    WEIGHT_EPSILON,
    confidence_kabsch_out_dir,
    pair_weight,
    plddt_at_parent,
    weighted_kabsch_rotation_translation,
)
from core.hold48_kabsch import (
    ALGORITHM as D125_ALGORITHM,
    COVARIANCE_RANK_MIN,
    DECISION as D125_DECISION,
    KABSCH_RESTITCH_PARENT_IDS,
    OVERLAP_CA_MIN,
    REFUSE_OVERLAP_CA_LT_3,
    REFUSE_RMSD_GT_10,
    REFUSE_SINGULAR_COVARIANCE,
    RMSD_REFUSE_ANGSTROM,
    AssemblerOverwriteRefused,
    InventoryRefused,
    _add,
    _matvec,
    _norm,
    _sub,
    ca_xyz_at_parent,
    kabsch_out_dir,
    overlap_parent_residues,
    paired_overlap_ca,
    require_inventory_parent,
)
from core.hold48_piecewise_kabsch import (
    ALGORITHM as D127_ALGORITHM,
    DECISION as D127_DECISION,
    REFUSE_LINKER_JUMP_GT_10 as D127_REFUSE_LINKER_JUMP,
    piecewise_kabsch_out_dir,
)
from core.hold48_stitch import TileFold, write_stitched, winning_tile

ALGORITHM = "linker_local_kabsch_then_winning_tile"
DECISION = "D-128"

# Spec §1b pins. v1 defaults, not measured optima — the tests go red on them.
WINDOW_HALF_WIDTH_AA = 32

# Spec §1a: the honesty line **is** the existing refuse gate, not a second
# number. Aliased (never re-valued) so a reader can see they are one gate.
SEAM_HONESTY_GATE_ANGSTROM = RMSD_REFUSE_ANGSTROM

# Spec §2. ⚠ `seam_jump_gt_10` is a NEW name, not a rename of D-127's
# `linker_jump_gt_10`: that one is computed after linker inherit across domain
# pieces, this one after the single window transform. Do not conflate them.
REFUSE_SEAM_JUMP_GT_10 = "seam_jump_gt_10"
REFUSE_REASONS = frozenset(
    {
        REFUSE_OVERLAP_CA_LT_3,
        REFUSE_RMSD_GT_10,
        REFUSE_SINGULAR_COVARIANCE,
        REFUSE_SEAM_JUMP_GT_10,
    }
)

# Spec §3 — the seven signed must-hunt linker parents (the D-127 OPS
# `linker_jump_gt_10` class, as recorded; ⚠ not re-measured here, ⚠ not a Fly
# re-query). Primary evaluation inventory, **not** a named-exclusion: the CLI
# still runs the 27.
SEVEN_LINKER_PARENT_IDS = frozenset({2938, 2939, 3179, 3190, 3321, 3368, 3566})

# Explicitly out of the primary inventory (Spec §3). They may appear as
# **recorded** rows in a CLI run of the 27; they are not success targets, and
# 3432 stays accept-refuse (signed triage) — never counted as a D-128 miss.
RMSD_CLASS_PARENT_IDS = frozenset({3272, 3394})
ACCEPT_REFUSE_PARENT_IDS = frozenset({3432})
NOT_SUCCESS_TARGET_PARENT_IDS = RMSD_CLASS_PARENT_IDS | ACCEPT_REFUSE_PARENT_IDS

# Re-export so callers / tests can compare paths without importing D-125 names.
LINKER_SEAM_RESTITCH_PARENT_IDS = KABSCH_RESTITCH_PARENT_IDS

# Spec §1a — the four path trees a honesty row can describe.
PATH_KABSCH = "kabsch"
PATH_CONFIDENCE_KABSCH = "confidence_kabsch"
PATH_PIECEWISE_KABSCH = "piecewise_kabsch"
PATH_LINKER_SEAM = "linker_seam"
HONESTY_PATHS = (
    PATH_KABSCH,
    PATH_CONFIDENCE_KABSCH,
    PATH_PIECEWISE_KABSCH,
    PATH_LINKER_SEAM,
)

# Only D-127 defines linkers. For the others the linker fields are absent —
# absent, not `0` (Spec §1a).
PATHS_DEFINING_LINKERS = frozenset({PATH_PIECEWISE_KABSCH})

# How a honesty row's jump is known (D-016: the row names its own artefact).
SOURCE_READ_FROM_RECORD = "read_from_path_record"
SOURCE_MEASURED_FROM_ARTIFACTS = "measured_from_path_artifacts"
SOURCE_ABSENT = "absent"

# Why a jump is null. Never a zero, never an assumed pass (Spec §1a).
ABSENCE_TREE_ABSENT = "tree_absent"
ABSENCE_NO_SEAM_ROWS = "no_seam_rows"
ABSENCE_REFUSED_BEFORE_TRANSFORM = "refused_before_transform"
ABSENCE_ARTIFACTS_ABSENT = "path_artifacts_absent"

# Spec §1b step 1 — how the offending seam was identified.
OFFENDING_FROM_D127_REFUSE = "from_d127_refuse"
OFFENDING_FROM_MEASURED_JUMP = "from_measured_jump"


class SiblingOverwriteRefused(AssemblerOverwriteRefused):
    """D-128 artifacts would land on assembler, kabsch/, confidence_kabsch/, or piecewise_kabsch/."""


Rotation = tuple[tuple[float, float, float], tuple[float, float, float], tuple[float, float, float]]
Translation = tuple[float, float, float]


def honest_for_jump(max_ca_jump_angstrom: Optional[float]) -> Optional[bool]:
    """Spec §1a: ``> 10.0`` Å is dishonest, ``≤ 10.0`` Å honest, **null is unknown**.

    Unknown is not honest and null is not ``0.0`` — a caller that turns the
    ``None`` into a number is the failure this function exists to prevent.
    """
    if max_ca_jump_angstrom is None:
        return None
    return float(max_ca_jump_angstrom) <= SEAM_HONESTY_GATE_ANGSTROM


@dataclass(frozen=True)
class SeamHonestyRow:
    """§1a: one row per (path, seam). A null jump stays null all the way out."""

    path: str
    moving_tile_index: Optional[int]
    reference_tile_index: Optional[int]
    max_ca_jump_angstrom: Optional[float]
    honest: Optional[bool]
    source: str
    linker_n: Optional[int] = None
    max_linker_ca_jump: Optional[float] = None
    absence_reason: Optional[str] = None
    refuse_reason: Optional[str] = None

    def to_json_row(self) -> dict:
        return {
            "path": self.path,
            "moving_tile_index": self.moving_tile_index,
            "reference_tile_index": self.reference_tile_index,
            "max_ca_jump_angstrom": self.max_ca_jump_angstrom,
            "honest": self.honest,
            "linker_n": self.linker_n,
            "max_linker_ca_jump": self.max_linker_ca_jump,
            "linker_fields_applicable": self.path in PATHS_DEFINING_LINKERS,
            "source": self.source,
            "absence_reason": self.absence_reason,
            "refuse_reason": self.refuse_reason,
            "honesty_gate_angstrom": SEAM_HONESTY_GATE_ANGSTROM,
        }


@dataclass(frozen=True)
class LinkerSeamRecord:
    """One D-128 seam: what was identified, what was fitted, what it ended at."""

    moving_tile_index: int
    reference_tile_index: int
    overlap_start: int
    overlap_end: int
    offending_seam_source: Optional[str]
    seam_centre: Optional[int]
    window_start: Optional[int]
    window_end: Optional[int]
    n_ca: Optional[int]
    rmsd_angstrom: Optional[float]
    max_ca_jump_angstrom: Optional[float]
    pre_transform_max_ca_jump_angstrom: Optional[float]
    refuse_reason: Optional[str]
    rotation: Optional[Rotation]
    translation: Optional[Translation]

    @property
    def accepted(self) -> bool:
        return self.refuse_reason is None


    @property
    def transformed(self) -> bool:
        return self.rotation is not None and self.translation is not None

    def to_json_row(self) -> dict:
        return {
            "moving_tile_index": self.moving_tile_index,
            "reference_tile_index": self.reference_tile_index,
            "overlap_start": self.overlap_start,
            "overlap_end": self.overlap_end,
            "offending_seam_source": self.offending_seam_source,
            "no_offending_seam": self.offending_seam_source is None,
            "seam_centre": self.seam_centre,
            "window_start": self.window_start,
            "window_end": self.window_end,
            "window_half_width_aa": WINDOW_HALF_WIDTH_AA,
            "n_ca": self.n_ca,
            "rmsd_angstrom": self.rmsd_angstrom,
            "max_ca_jump_angstrom": self.max_ca_jump_angstrom,
            "pre_transform_max_ca_jump_angstrom": self.pre_transform_max_ca_jump_angstrom,
            "refuse_reason": self.refuse_reason,
            "honest": honest_for_jump(self.max_ca_jump_angstrom),
            "R": [list(row) for row in self.rotation] if self.rotation is not None else None,
            "t": list(self.translation) if self.translation is not None else None,
        }


@dataclass(frozen=True)
class LinkerSeamRestitchResult:
    accepted: bool
    parent_job_id: int
    out_dir: Path
    seams: tuple[LinkerSeamRecord, ...]
    honesty: tuple[SeamHonestyRow, ...]
    tiles: tuple[TileFold, ...]
    stitched: Optional[dict[str, str]]

    @property
    def repaired(self) -> bool:
        """Accepted **and** at least one window actually moved. An accept with
        zero transforms is a measurement, not a repair."""
        return self.accepted and any(s.transformed for s in self.seams)


@dataclass(frozen=True)
class OpsSuccessReport:
    """Spec §11 required report fields. **Not** a CI assert against live ops."""

    n_seams_measured: int
    n_dishonest_kabsch: int
    n_dishonest_confidence_kabsch: int
    n_dishonest_piecewise_kabsch: int
    n_dishonest_linker_seam: int
    n_honesty_unknown: int
    n_d125_pass_d128_refuse: int
    n_d126_pass_d128_refuse: int
    n_d127_pass_d128_refuse: int
    n_d127_refuse_d128_pass: int
    repaired_of_seven: int
    repaired_of_seven_source: str

    def to_json(self) -> dict:
        return {
            "n_seams_measured": self.n_seams_measured,
            "n_dishonest_kabsch": self.n_dishonest_kabsch,
            "n_dishonest_confidence_kabsch": self.n_dishonest_confidence_kabsch,
            "n_dishonest_piecewise_kabsch": self.n_dishonest_piecewise_kabsch,
            "n_dishonest_linker_seam": self.n_dishonest_linker_seam,
            "n_honesty_unknown": self.n_honesty_unknown,
            "n_d125_pass_d128_refuse": self.n_d125_pass_d128_refuse,
            "n_d126_pass_d128_refuse": self.n_d126_pass_d128_refuse,
            "n_d127_pass_d128_refuse": self.n_d127_pass_d128_refuse,
            "n_d127_refuse_d128_pass": self.n_d127_refuse_d128_pass,
            "repaired_of_seven": self.repaired_of_seven,
            "repaired_of_seven_source": self.repaired_of_seven_source,
            "n_d125_pass_d128_refuse_is_named_finding": self.n_d125_pass_d128_refuse > 0,
            "n_d126_pass_d128_refuse_is_named_finding": self.n_d126_pass_d128_refuse > 0,
            "n_d127_pass_d128_refuse_is_named_finding": self.n_d127_pass_d128_refuse > 0,
            "zero_of_seven_repaired_is_allowed": True,
            "unknown_is_not_honest": True,
            "honesty_gate_angstrom": SEAM_HONESTY_GATE_ANGSTROM,
            "seams_recorded_is_not_seams_solved": True,
            "d125_algorithm": D125_ALGORITHM,
            "d126_algorithm": D126_ALGORITHM,
            "d127_algorithm": D127_ALGORITHM,
            "d128_algorithm": ALGORITHM,
            "d125_decision": D125_DECISION,
            "d126_decision": D126_DECISION,
            "d127_decision": D127_DECISION,
            "d128_decision": DECISION,
        }


# ── seam geometry (shared by §1a measurement and §1b refuse) ─────────────────


def _ca_distance(p: Sequence[float], q: Sequence[float]) -> float:
    return _norm(_sub(p, q))


def seam_max_ca_jump(reference: TileFold, moving: TileFold) -> Optional[float]:
    """Max ``|Cα_ref − Cα_moved|`` across the whole seam overlap.

    ``None`` when the two tiles share no corresponding Cα — an unmeasurable
    seam is null, never ``0.0``.
    """
    moving_pts, ref_pts, _used = paired_overlap_ca(reference, moving)
    if not moving_pts:
        return None
    return max(_ca_distance(p, q) for p, q in zip(moving_pts, ref_pts))


def seam_centre_parent_residue(reference: TileFold, moving: TileFold) -> Optional[int]:
    """Span-relative centre of the seam, derived from the stored tile windows.

    Spec §1b step 2: the centre comes from ``tile_start`` / ``tile_end`` and the
    identified seam — not from a linker boundary no record names.
    """
    overlap = overlap_parent_residues(reference, moving)
    if not overlap:
        return None
    return (overlap[0] + overlap[-1]) // 2


def window_bounds(centre: int, *, half_width: int = WINDOW_HALF_WIDTH_AA) -> tuple[int, int]:
    """``±W`` around the centre, inclusive. ``W = 32`` is pinned (Spec §1b)."""
    return (centre - int(half_width), centre + int(half_width))


# ── §1b — one weighted Kabsch inside one window (no pieces, no inherit) ──────


@dataclass(frozen=True)
class WindowFit:
    window_start: int
    window_end: int
    n_ca: int
    rmsd_angstrom: Optional[float]
    refuse_reason: Optional[str]
    rotation: Optional[Rotation]
    translation: Optional[Translation]

    @property
    def accepted(self) -> bool:
        return self.refuse_reason is None and self.rotation is not None


def window_overlap_ca(
    reference: TileFold,
    moving: TileFold,
    window: tuple[int, int],
) -> tuple[
    list[tuple[float, float, float]],
    list[tuple[float, float, float]],
    list[int],
    list[float],
]:
    """Corresponding overlap Cα whose parent residue sits inside the window."""
    start, end = int(window[0]), int(window[1])
    moving_pts, ref_pts, used = paired_overlap_ca(reference, moving)
    m: list[tuple[float, float, float]] = []
    r: list[tuple[float, float, float]] = []
    kept: list[int] = []
    weights: list[float] = []
    for p, q, parent_res in zip(moving_pts, ref_pts, used):
        if start <= parent_res <= end:
            m.append(p)
            r.append(q)
            kept.append(parent_res)
            weights.append(
                pair_weight(
                    plddt_at_parent(reference, parent_res),
                    plddt_at_parent(moving, parent_res),
                )
            )
    return m, r, kept, weights


def fit_seam_window(
    reference: TileFold,
    moving: TileFold,
    centre: int,
    *,
    half_width: int = WINDOW_HALF_WIDTH_AA,
) -> WindowFit:
    """One weighted Kabsch on the window's Cα. No trim. No second window size."""
    start, end = window_bounds(centre, half_width=half_width)
    moving_pts, ref_pts, _kept, weights = window_overlap_ca(reference, moving, (start, end))
    n = len(moving_pts)
    if n < OVERLAP_CA_MIN:
        return WindowFit(
            window_start=start,
            window_end=end,
            n_ca=n,
            rmsd_angstrom=None,
            refuse_reason=REFUSE_OVERLAP_CA_LT_3,
            rotation=None,
            translation=None,
        )
    R, t, rmsd, rank = weighted_kabsch_rotation_translation(moving_pts, ref_pts, weights)
    if rank < COVARIANCE_RANK_MIN:
        return WindowFit(
            window_start=start,
            window_end=end,
            n_ca=n,
            rmsd_angstrom=None,
            refuse_reason=REFUSE_SINGULAR_COVARIANCE,
            rotation=None,
            translation=None,
        )
    if rmsd > RMSD_REFUSE_ANGSTROM:
        return WindowFit(
            window_start=start,
            window_end=end,
            n_ca=n,
            rmsd_angstrom=rmsd,
            refuse_reason=REFUSE_RMSD_GT_10,
            rotation=None,
            translation=None,
        )
    return WindowFit(
        window_start=start,
        window_end=end,
        n_ca=n,
        rmsd_angstrom=rmsd,
        refuse_reason=None,
        rotation=R,
        translation=t,
    )


def apply_window_transform_pdb(
    pdb: str,
    tile_start: int,
    window: tuple[int, int],
    rotation: Sequence[Sequence[float]],
    translation: Sequence[float],
) -> str:
    """Apply ``R, t`` to ATOM/HETATM **inside the window only**.

    Atoms outside the window keep their emitted coordinates and inherit
    nothing — there is no piece list and no linker-inherit rule here (that is
    D-127's family). No atom is invented.
    """
    lo, hi = int(window[0]), int(window[1])
    lines: list[str] = []
    ended_nl = pdb.endswith("\n")
    for line in pdb.splitlines():
        if (line.startswith("ATOM") or line.startswith("HETATM")) and len(line) >= 54:
            try:
                res_seq = int(line[22:26])
                x = float(line[30:38])
                y = float(line[38:46])
                z = float(line[46:54])
            except ValueError:
                lines.append(line)
                continue
            parent_res = tile_start + res_seq - 1
            if lo <= parent_res <= hi:
                nx, ny, nz = _add(_matvec(rotation, (x, y, z)), translation)
                line = f"{line[:30]}{nx:8.3f}{ny:8.3f}{nz:8.3f}{line[54:]}"
        lines.append(line)
    text = "\n".join(lines)
    return text + ("\n" if ended_nl or text else "")


def transform_tile_window(tile: TileFold, fit: WindowFit) -> TileFold:
    if not fit.accepted or fit.rotation is None or fit.translation is None:
        raise ValueError("refuse is fail-closed — do not invent a transformed pose")
    return TileFold(
        start=tile.start,
        end=tile.end,
        pdb=apply_window_transform_pdb(
            tile.pdb,
            tile.start,
            (fit.window_start, fit.window_end),
            fit.rotation,
            fit.translation,
        ),
        plddt=tile.plddt,
        pae=tile.pae,
    )


# ── §1b step 1 — identify the offending seam (never guess one) ───────────────


def read_seam_rows(out_root: Path | str, parent_job_id: int, path_name: str) -> Optional[list[dict]]:
    """Read one path tree's ``seams.jsonl``. ``None`` when the tree is absent.

    Read-only: D-128 never writes into ``kabsch/``, ``confidence_kabsch/``, or
    ``piecewise_kabsch/``.
    """
    tree = path_tree_dir(out_root, parent_job_id, path_name)
    if not tree.is_dir():
        return None
    seams = tree / "seams.jsonl"
    if not seams.is_file():
        return []
    rows: list[dict] = []
    for line in seams.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        rows.append(json.loads(line))
    return rows


def d127_linker_refused_seams(out_root: Path | str, parent_job_id: int) -> set[tuple[int, int]]:
    """``(moving_tile_index, reference_tile_index)`` D-127 refused for its linkers.

    D-127's ``linker_jump_gt_10`` is a **different measurement** of a different
    algorithm; it is read here only to point at a seam, never copied into a
    D-128 refuse reason.
    """
    rows = read_seam_rows(out_root, parent_job_id, PATH_PIECEWISE_KABSCH)
    if not rows:
        return set()
    out: set[tuple[int, int]] = set()
    for row in rows:
        if row.get("refuse_reason") != D127_REFUSE_LINKER_JUMP:
            continue
        moving = row.get("moving_tile_index")
        reference = row.get("reference_tile_index")
        if moving is None or reference is None:
            continue
        out.add((int(moving), int(reference)))
    return out


def identify_offending_seam(
    *,
    moving_tile_index: int,
    reference_tile_index: int,
    measured_jump: Optional[float],
    d127_refused: Iterable[tuple[int, int]] = (),
) -> Optional[str]:
    """Spec §1b step 1. Returns the source, or ``None`` for "nothing offends".

    The D-127 refuse record names the seam; failing that, a **measured**
    pre-transform jump over the gate names it. A seam neither names is not
    guessed at and not skipped — the caller records the absence.
    """
    if (int(moving_tile_index), int(reference_tile_index)) in set(d127_refused):
        return OFFENDING_FROM_D127_REFUSE
    if measured_jump is not None and measured_jump > SEAM_HONESTY_GATE_ANGSTROM:
        return OFFENDING_FROM_MEASURED_JUMP
    return None


# ── seam walk ────────────────────────────────────────────────────────────────


def align_tiles(
    tiles: Sequence[TileFold],
    *,
    d127_refused_seams: Iterable[tuple[int, int]] = (),
    half_width: int = WINDOW_HALF_WIDTH_AA,
) -> tuple[list[TileFold], list[LinkerSeamRecord], bool]:
    """N-terminal tile is the reference; later tiles chain onto the last accepted frame.

    All-or-nothing: the first refuse stops further transforms. ``accepted`` is
    True only when every inbound seam ended honest. Untransformed copies stay
    in the returned list for inspection; they are not written.
    """
    if not tiles:
        raise ValueError("align_tiles needs at least one tile")
    ordered = sorted(tiles, key=lambda t: (t.start, t.end))
    out: list[TileFold] = [ordered[0]]
    seams: list[LinkerSeamRecord] = []
    refused = set(d127_refused_seams)
    last_accepted = ordered[0]
    last_accepted_index = 1
    all_ok = True
    for i, moving in enumerate(ordered[1:], start=2):
        overlap = overlap_parent_residues(last_accepted, moving)
        pre_jump = seam_max_ca_jump(last_accepted, moving)
        centre = seam_centre_parent_residue(last_accepted, moving)
        source = identify_offending_seam(
            moving_tile_index=i,
            reference_tile_index=last_accepted_index,
            measured_jump=pre_jump,
            d127_refused=refused,
        )
        record, transformed = _run_seam(
            reference=last_accepted,
            moving=moving,
            moving_tile_index=i,
            reference_tile_index=last_accepted_index,
            overlap=overlap,
            pre_jump=pre_jump,
            centre=centre,
            source=source,
            half_width=half_width,
        )
        seams.append(record)
        if record.refuse_reason is not None or transformed is None:
            all_ok = False
            out.append(moving)
            break
        out.append(transformed)
        last_accepted = transformed
        last_accepted_index = i
    if all_ok and len(out) < len(ordered):
        out.extend(ordered[len(out) :])
        all_ok = False
    return out, seams, all_ok


def _run_seam(
    *,
    reference: TileFold,
    moving: TileFold,
    moving_tile_index: int,
    reference_tile_index: int,
    overlap: Sequence[int],
    pre_jump: Optional[float],
    centre: Optional[int],
    source: Optional[str],
    half_width: int,
) -> tuple[LinkerSeamRecord, Optional[TileFold]]:
    """One seam: identify → window fit → apply → post-apply honesty check."""

    def _record(
        *,
        window: Optional[tuple[int, int]] = None,
        n_ca: Optional[int] = None,
        rmsd: Optional[float] = None,
        post_jump: Optional[float] = None,
        refuse_reason: Optional[str] = None,
        rotation: Optional[Rotation] = None,
        translation: Optional[Translation] = None,
    ) -> LinkerSeamRecord:
        return LinkerSeamRecord(
            moving_tile_index=moving_tile_index,
            reference_tile_index=reference_tile_index,
            overlap_start=overlap[0] if overlap else 0,
            overlap_end=overlap[-1] if overlap else 0,
            offending_seam_source=source,
            seam_centre=centre,
            window_start=window[0] if window else None,
            window_end=window[1] if window else None,
            n_ca=n_ca,
            rmsd_angstrom=rmsd,
            max_ca_jump_angstrom=post_jump,
            pre_transform_max_ca_jump_angstrom=pre_jump,
            refuse_reason=refuse_reason,
            rotation=rotation,
            translation=translation,
        )

    if centre is None or pre_jump is None:
        # No corresponding Cα on this seam: nothing to measure and nothing to
        # fit. Unknown is not honest, so the parent refuses rather than pass an
        # unmeasured join off as one that holds.
        return _record(refuse_reason=REFUSE_OVERLAP_CA_LT_3), None

    if source is None:
        # Nothing offends: the seam is already inside the gate. A **recorded**
        # outcome, not a silent skip — no window is fitted, no atom moves, and
        # the measured jump is written as this path's honesty number. Accepting
        # here is not a repair, and `repaired` stays False because nothing moved.
        return _record(post_jump=pre_jump), moving

    fit = fit_seam_window(reference, moving, centre, half_width=half_width)
    window = (fit.window_start, fit.window_end)
    if not fit.accepted:
        return (
            _record(
                window=window,
                n_ca=fit.n_ca,
                rmsd=fit.rmsd_angstrom,
                refuse_reason=fit.refuse_reason,
            ),
            None,
        )

    transformed = transform_tile_window(moving, fit)
    post_jump = seam_max_ca_jump(reference, transformed)
    if post_jump is None or post_jump > SEAM_HONESTY_GATE_ANGSTROM:
        # Measured across the **whole** seam, not only the fitted window: a
        # window that lands while the rest of the seam flies apart is not a
        # held join, and presenting it as one is the D-126 lie surface.
        return (
            _record(
                window=window,
                n_ca=fit.n_ca,
                rmsd=fit.rmsd_angstrom,
                post_jump=post_jump,
                refuse_reason=REFUSE_SEAM_JUMP_GT_10,
            ),
            None,
        )
    return (
        _record(
            window=window,
            n_ca=fit.n_ca,
            rmsd=fit.rmsd_angstrom,
            post_jump=post_jump,
            rotation=fit.rotation,
            translation=fit.translation,
        ),
        transformed,
    )


# ── §1a — honesty rows for every path (prior trees are READ) ─────────────────


def path_tree_dir(out_root: Path | str, parent_job_id: int, path_name: str) -> Path:
    if path_name == PATH_KABSCH:
        return kabsch_out_dir(out_root, parent_job_id)
    if path_name == PATH_CONFIDENCE_KABSCH:
        return confidence_kabsch_out_dir(out_root, parent_job_id)
    if path_name == PATH_PIECEWISE_KABSCH:
        return piecewise_kabsch_out_dir(out_root, parent_job_id)
    if path_name == PATH_LINKER_SEAM:
        return linker_seam_out_dir(out_root, parent_job_id)
    raise ValueError(f"unknown honesty path {path_name!r}")


def _tiles_from_tree(tree: Path) -> list[TileFold]:
    """Rebuild the tiles a path **wrote**, from that path's own artifacts.

    ``provenance.json`` carries the ordered windows and ``write_stitched`` wrote
    one ``tileN.pdb`` per window, so the pair reconstructs what that path ended
    with. pLDDT / PAE are not needed to measure a Cα jump and are not invented.
    """
    prov_path = tree / "provenance.json"
    if not prov_path.is_file():
        return []
    prov = json.loads(prov_path.read_text(encoding="utf-8"))
    windows = prov.get("windows") or []
    tiles: list[TileFold] = []
    for n, window in enumerate(windows, start=1):
        pdb_path = tree / f"tile{n}.pdb"
        if not pdb_path.is_file() or len(window) < 2:
            return []
        start, end = int(window[0]), int(window[1])
        tiles.append(
            TileFold(
                start=start,
                end=end,
                pdb=pdb_path.read_text(encoding="utf-8"),
                plddt=[0.0] * (end - start + 1),
                pae=[],
            )
        )
    return tiles


def _measured_jumps_from_tree(tree: Path) -> dict[tuple[int, int], Optional[float]]:
    """Seam jumps measured from a path's own written PDBs, keyed (moving, reference)."""
    tiles = _tiles_from_tree(tree)
    out: dict[tuple[int, int], Optional[float]] = {}
    for i in range(1, len(tiles)):
        out[(i + 1, i)] = seam_max_ca_jump(tiles[i - 1], tiles[i])
    return out


def read_path_seam_honesty(
    out_root: Path | str,
    parent_job_id: int,
    path_name: str,
) -> list[SeamHonestyRow]:
    """§1a rows for one prior path, by **reading** that path's tree.

    Three ways a row can be known, and the row says which (D-016):
    the path recorded the jump; the jump was measured from the artifacts that
    path itself wrote; or it is an **honest absence with a stated reason**.
    An absence is never a zero and never an assumed pass.
    """
    rows = read_seam_rows(out_root, parent_job_id, path_name)
    if rows is None:
        return [
            SeamHonestyRow(
                path=path_name,
                moving_tile_index=None,
                reference_tile_index=None,
                max_ca_jump_angstrom=None,
                honest=None,
                source=SOURCE_ABSENT,
                absence_reason=ABSENCE_TREE_ABSENT,
            )
        ]
    if not rows:
        return [
            SeamHonestyRow(
                path=path_name,
                moving_tile_index=None,
                reference_tile_index=None,
                max_ca_jump_angstrom=None,
                honest=None,
                source=SOURCE_ABSENT,
                absence_reason=ABSENCE_NO_SEAM_ROWS,
            )
        ]

    tree = path_tree_dir(out_root, parent_job_id, path_name)
    measured: Optional[dict[tuple[int, int], Optional[float]]] = None
    out: list[SeamHonestyRow] = []
    for row in rows:
        moving = row.get("moving_tile_index")
        reference = row.get("reference_tile_index")
        refuse_reason = row.get("refuse_reason")
        jump = row.get("max_ca_jump_angstrom")
        linker_n = row.get("linker_n") if path_name in PATHS_DEFINING_LINKERS else None
        max_linker = (
            row.get("max_linker_ca_jump") if path_name in PATHS_DEFINING_LINKERS else None
        )
        if jump is not None:
            out.append(
                SeamHonestyRow(
                    path=path_name,
                    moving_tile_index=moving,
                    reference_tile_index=reference,
                    max_ca_jump_angstrom=float(jump),
                    honest=honest_for_jump(float(jump)),
                    source=SOURCE_READ_FROM_RECORD,
                    linker_n=linker_n,
                    max_linker_ca_jump=max_linker,
                    refuse_reason=refuse_reason,
                )
            )
            continue
        # The path did not record a jump for this seam. D-125's SeamRecord never
        # does; D-126 / D-127 leave it null when they refused before any
        # transform. Measure it from that path's own PDBs when they exist,
        # otherwise say plainly that it is unknown.
        if measured is None:
            measured = _measured_jumps_from_tree(tree)
        key = (int(moving), int(reference)) if moving is not None and reference is not None else None
        found = measured.get(key) if key is not None else None
        if found is not None:
            out.append(
                SeamHonestyRow(
                    path=path_name,
                    moving_tile_index=moving,
                    reference_tile_index=reference,
                    max_ca_jump_angstrom=float(found),
                    honest=honest_for_jump(float(found)),
                    source=SOURCE_MEASURED_FROM_ARTIFACTS,
                    linker_n=linker_n,
                    max_linker_ca_jump=max_linker,
                    refuse_reason=refuse_reason,
                )
            )
            continue
        out.append(
            SeamHonestyRow(
                path=path_name,
                moving_tile_index=moving,
                reference_tile_index=reference,
                max_ca_jump_angstrom=None,
                honest=None,
                source=SOURCE_ABSENT,
                linker_n=linker_n,
                max_linker_ca_jump=max_linker,
                absence_reason=(
                    ABSENCE_REFUSED_BEFORE_TRANSFORM
                    if refuse_reason
                    else ABSENCE_ARTIFACTS_ABSENT
                ),
                refuse_reason=refuse_reason,
            )
        )
    return out


def linker_seam_honesty_rows(seams: Sequence[LinkerSeamRecord]) -> list[SeamHonestyRow]:
    """§1a rows for D-128's own path. D-128 does not define linkers."""
    return [
        SeamHonestyRow(
            path=PATH_LINKER_SEAM,
            moving_tile_index=seam.moving_tile_index,
            reference_tile_index=seam.reference_tile_index,
            max_ca_jump_angstrom=seam.max_ca_jump_angstrom,
            honest=honest_for_jump(seam.max_ca_jump_angstrom),
            source=SOURCE_MEASURED_FROM_ARTIFACTS,
            absence_reason=(
                None
                if seam.max_ca_jump_angstrom is not None
                else ABSENCE_REFUSED_BEFORE_TRANSFORM
            ),
            refuse_reason=seam.refuse_reason,
        )
        for seam in seams
    ]


def collect_seam_honesty(
    out_root: Path | str,
    parent_job_id: int,
    seams: Sequence[LinkerSeamRecord],
) -> list[SeamHonestyRow]:
    """All four paths' §1a rows: three read from disk, D-128's from this run."""
    rows: list[SeamHonestyRow] = []
    for path_name in (PATH_KABSCH, PATH_CONFIDENCE_KABSCH, PATH_PIECEWISE_KABSCH):
        rows.extend(read_path_seam_honesty(out_root, parent_job_id, path_name))
    rows.extend(linker_seam_honesty_rows(seams))
    return rows


# ── sibling tree ─────────────────────────────────────────────────────────────


def linker_seam_out_dir(out_root: Path | str, parent_job_id: int) -> Path:
    return Path(out_root) / "linker_seam" / str(parent_job_id)


def refuse_sibling_overwrite(
    out_dir: Path,
    assembler_dir: Optional[Path | str] = None,
    d125_dir: Optional[Path | str] = None,
    d126_dir: Optional[Path | str] = None,
    d127_dir: Optional[Path | str] = None,
) -> None:
    """Never write D-128 artifacts as if they were one of the four prior paths."""
    out = Path(out_dir).resolve()
    if "linker_seam" not in out.parts:
        raise SiblingOverwriteRefused(
            f"D-128 artifacts must land under a linker_seam/ directory, not {out}"
        )
    dest_pdb = (out / "stitched.pdb").resolve()
    checks: list[tuple[Optional[Path | str], str]] = [
        (assembler_dir, "assembler"),
        (d125_dir, "D-125 kabsch"),
        (d126_dir, "D-126 confidence_kabsch"),
        (d127_dir, "D-127 piecewise_kabsch"),
    ]
    for other, label in checks:
        if other is None:
            continue
        other_path = Path(other).resolve()
        if out == other_path or dest_pdb == (other_path / "stitched.pdb").resolve():
            raise SiblingOverwriteRefused(
                f"refusing to write D-128 artifacts over {label} dir {other_path}"
            )


def _clear_success_artifacts(out: Path) -> None:
    """A refuse must not leave a prior accept looking like this run succeeded."""
    for name in ("stitched.pdb", "stitched_plddt.json", "stitched_pae.json"):
        p = out / name
        if p.exists():
            p.unlink()
    for p in out.glob("tile*_transformed.pdb"):
        p.unlink()


def write_provenance(
    out: Path,
    *,
    parent_job_id: int,
    tile_job_ids: Sequence[int],
    windows: Sequence[tuple[int, int]],
    seams: Sequence[LinkerSeamRecord],
    honesty: Sequence[SeamHonestyRow],
    accepted: bool,
) -> None:
    payload = {
        "algorithm": ALGORITHM,
        "decision": DECISION,
        "parent_job_id": parent_job_id,
        "tile_job_ids": list(tile_job_ids),
        "windows": [list(w) for w in windows],
        "accepted": accepted,
        "repaired": accepted and any(s.transformed for s in seams),
        "seams": [s.to_json_row() for s in seams],
        "seam_honesty": [r.to_json_row() for r in honesty],
        "window_half_width_aa": WINDOW_HALF_WIDTH_AA,
        "weight_epsilon": WEIGHT_EPSILON,
        "rmsd_refuse_angstrom": RMSD_REFUSE_ANGSTROM,
        "seam_honesty_gate_angstrom": SEAM_HONESTY_GATE_ANGSTROM,
        "no_trim_loop": True,
        "no_domain_pieces_fitted": True,
        "no_linker_inherit": True,
        "served_path": "assembler",
        "seams_solved": False,
    }
    (out / "provenance.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    with (out / "seams.jsonl").open("w", encoding="utf-8") as fh:
        for seam in seams:
            fh.write(json.dumps(seam.to_json_row()) + "\n")
    with (out / "seam_honesty.jsonl").open("w", encoding="utf-8") as fh:
        for row in honesty:
            fh.write(json.dumps(row.to_json_row()) + "\n")


def write_linker_seam_restitch(
    tiles: Sequence[TileFold],
    length: int,
    out_root: Path | str,
    *,
    parent_job_id: int,
    tile_job_ids: Sequence[int] = (),
    assembler_dir: Optional[Path | str] = None,
    d125_dir: Optional[Path | str] = None,
    d126_dir: Optional[Path | str] = None,
    d127_dir: Optional[Path | str] = None,
    half_width: int = WINDOW_HALF_WIDTH_AA,
) -> LinkerSeamRestitchResult:
    """Measure every path's seam honesty, optionally repair, then the assembler.

    The §1a rows are written whatever the outcome — a refuse is a **recorded**
    outcome. Success artifacts are written only when every seam ended honest,
    and no other path's ``stitched.pdb`` is ever presented as a D-128 result.
    """
    require_inventory_parent(parent_job_id)
    out = linker_seam_out_dir(out_root, parent_job_id)
    if d125_dir is None:
        d125_dir = kabsch_out_dir(out_root, parent_job_id)
    if d126_dir is None:
        d126_dir = confidence_kabsch_out_dir(out_root, parent_job_id)
    if d127_dir is None:
        d127_dir = piecewise_kabsch_out_dir(out_root, parent_job_id)
    refuse_sibling_overwrite(out, assembler_dir, d125_dir, d126_dir, d127_dir)
    if winning_tile is None:  # pragma: no cover — import pin
        raise RuntimeError("winning_tile must remain importable")

    aligned, seams, accepted = align_tiles(
        tiles,
        d127_refused_seams=d127_linker_refused_seams(out_root, parent_job_id),
        half_width=half_width,
    )
    honesty = collect_seam_honesty(out_root, parent_job_id, seams)
    ordered = sorted(tiles, key=lambda t: (t.start, t.end))
    windows = [(t.start, t.end) for t in ordered]
    ids = list(tile_job_ids) if tile_job_ids else [0] * len(ordered)

    out.mkdir(parents=True, exist_ok=True)
    write_provenance(
        out,
        parent_job_id=parent_job_id,
        tile_job_ids=ids,
        windows=windows,
        seams=seams,
        honesty=honesty,
        accepted=accepted,
    )

    stitched = None
    if accepted:
        for n, tile in enumerate(aligned, start=1):
            if n == 1:
                continue
            if seams[n - 2].transformed:
                (out / f"tile{n}_transformed.pdb").write_text(tile.pdb, encoding="utf-8")
        stitched = write_stitched(aligned, length, out)
    else:
        _clear_success_artifacts(out)

    return LinkerSeamRestitchResult(
        accepted=accepted,
        parent_job_id=parent_job_id,
        out_dir=out,
        seams=tuple(seams),
        honesty=tuple(honesty),
        tiles=tuple(aligned),
        stitched=stitched,
    )


# ── ops report (Spec §11) ────────────────────────────────────────────────────


def _dishonest(rows: Iterable[Mapping | SeamHonestyRow], path_name: str) -> int:
    n = 0
    for row in rows:
        payload = row.to_json_row() if isinstance(row, SeamHonestyRow) else row
        if payload.get("path") != path_name:
            continue
        if payload.get("honest") is False:
            n += 1
    return n


def build_ops_success_report(
    d125_accepted: Mapping[int, bool],
    d126_accepted: Mapping[int, bool],
    d127_accepted: Mapping[int, bool],
    d128_accepted: Mapping[int, bool],
    *,
    d128_repaired: Optional[Mapping[int, bool]] = None,
    honesty_rows: Iterable[Mapping | SeamHonestyRow] = (),
) -> OpsSuccessReport:
    """Spec §11 fields. A drop is a **named finding**; 0-of-7 repaired is allowed.

    Not a CI assert against live ops. Confusion counts parents present in all
    four outcome maps that are in the Spec's 27. ``repaired_of_seven`` counts
    only the seven, only where a **repair record** says a window actually moved
    — with no repair map the count is 0 and the payload says the map was not
    supplied, so a zero is never read as a measured zero.
    """
    rows = [r.to_json_row() if isinstance(r, SeamHonestyRow) else dict(r) for r in honesty_rows]
    common = (
        set(d125_accepted)
        & set(d126_accepted)
        & set(d127_accepted)
        & set(d128_accepted)
        & set(KABSCH_RESTITCH_PARENT_IDS)
    )
    n125_pr = n126_pr = n127_pr = n127_rp = 0
    for pid in sorted(common):
        a128 = bool(d128_accepted[pid])
        if bool(d125_accepted[pid]) and not a128:
            n125_pr += 1
        if bool(d126_accepted[pid]) and not a128:
            n126_pr += 1
        if bool(d127_accepted[pid]) and not a128:
            n127_pr += 1
        if (not bool(d127_accepted[pid])) and a128:
            n127_rp += 1

    if d128_repaired is None:
        repaired = 0
        source = "none_supplied"
    else:
        repaired = sum(
            1 for pid in SEVEN_LINKER_PARENT_IDS if bool(d128_repaired.get(pid, False))
        )
        source = "repair_records"

    measured = sum(1 for row in rows if row.get("max_ca_jump_angstrom") is not None)
    unknown = sum(1 for row in rows if row.get("honest") is None)
    return OpsSuccessReport(
        n_seams_measured=measured,
        n_dishonest_kabsch=_dishonest(rows, PATH_KABSCH),
        n_dishonest_confidence_kabsch=_dishonest(rows, PATH_CONFIDENCE_KABSCH),
        n_dishonest_piecewise_kabsch=_dishonest(rows, PATH_PIECEWISE_KABSCH),
        n_dishonest_linker_seam=_dishonest(rows, PATH_LINKER_SEAM),
        n_honesty_unknown=unknown,
        n_d125_pass_d128_refuse=n125_pr,
        n_d126_pass_d128_refuse=n126_pr,
        n_d127_pass_d128_refuse=n127_pr,
        n_d127_refuse_d128_pass=n127_rp,
        repaired_of_seven=repaired,
        repaired_of_seven_source=source,
    )


# Keep the D-125 Cα reader live so a renamed helper fails at import, not later.
assert ca_xyz_at_parent is not None
