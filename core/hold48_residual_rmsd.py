"""D-130-A — residual-RMSD decomposition, then the existing winning_tile assembler.

Two halves, and the **required** one is the measurement.

**§1a (required).** Every earlier path reported *the RMSD it achieved*. None
reported *the smallest RMSD any rigid motion could have achieved*. A rigid
motion preserves internal distances, so the disagreement between the two
overlap copies' own internal Cα distances is a property of the two shapes
alone and lower-bounds the RMSD of **every** rigid transform at once::

    dRMSD = sqrt( 2 / (n(n-1)) * sum_{i<j} (d^A_ij - d^B_ij)^2 )
    RMSD(R, t) >= dRMSD / 2                        for every rigid (R, t)

So for each seam and each of the five path trees — D-125 ``kabsch/``, D-126
``confidence_kabsch/``, D-127 ``piecewise_kabsch/``, D-128 ``linker_seam/``
and D-130's own ``residual_rmsd/`` — this module records the achieved
full-overlap RMSD beside the internal dRMSD, the **floor** ``dRMSD / 2``, and
a three-valued ``residual_class``.

⚠ **The floor is ONE-DIRECTIONAL.** Above ``10.0`` Å it **certifies** that no
rigid transform can pass the gate — ``irreducible``. At or below it, it
**proves nothing**: not that a passing fit exists, not that the parent is
recoverable, and never that the gate is too strict. ``irreducible`` is
**sufficient and never necessary**, because the bound's constant is not
tight. Reading it backwards is a Spec violation, not an interpretation.

**§1b (optional).** The only recovery permitted is one where the earlier fits
were solving the **wrong pairing**. The audit is decided by **residue
identity**, never by RMSD: a correction is accepted only when **exactly one**
integer register offset makes every corrected pair's identity agree — none or
more than one refuses ``correspondence_unverifiable``. The refit is then
**exactly D-125's**: one unweighted, untrimmed Kabsch on the full corrected
overlap Cα, applied to the whole moving tile → existing ``winning_tile``.

⚠ **No new geometry.** No trim (the D-126 lie surface), no weights (D-126),
no pieces (D-127), no window and no linker-inherit (D-128), no blend, no
RMSD-v2. Recovering **0 of 2** is a **pre-registered allowed outcome** and
licenses none of them.

Seams are **measured**, not solved. This module never claims otherwise. It
does **not** replace ``core.hold48_stitch.winning_tile``, does **not**
overwrite the assembler / D-125 / D-126 / D-127 / D-128 trees, does **not**
jointly place a holoprotein, and does **not** enter F-004.

ZERO third-party imports. Refuse v1 (Spec §2): overlap Cα ``< 3``; floor
``> 10.0`` Å; an ambiguous or unverifiable register; post-fit full-overlap
RMSD ``> 10.0`` Å; covariance rank ``< 2``. Fail closed + all-or-nothing
parent.
"""
from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping, Optional, Sequence

from core.features import parse_pdb
from core.hold48_confidence_kabsch import confidence_kabsch_out_dir
from core.hold48_kabsch import (
    COVARIANCE_RANK_MIN,
    KABSCH_RESTITCH_PARENT_IDS,
    OVERLAP_CA_MIN,
    REFUSE_OVERLAP_CA_LT_3,
    REFUSE_RMSD_GT_10,
    REFUSE_SINGULAR_COVARIANCE,
    RMSD_REFUSE_ANGSTROM,
    AssemblerOverwriteRefused,
    InventoryRefused,
    _norm,
    _sub,
    apply_rigid_transform_pdb,
    ca_xyz_at_parent,
    kabsch_out_dir,
    kabsch_rotation_translation,
    overlap_parent_residues,
    paired_overlap_ca,
    require_inventory_parent,
)
# ⚠ ONE import from D-128, and it is a ruler rather than an algorithm:
# `seam_max_ca_jump` is the whole-seam max Cα distance §1b's disclosure list
# requires. None of D-128's window, linker identification or inherit logic is
# imported, and no D-128 refuse name enters this module (Spec §2, §9).
from core.hold48_linker_seam import (
    _tiles_from_tree,
    linker_seam_out_dir,
    read_seam_rows,
    seam_max_ca_jump,
)
from core.hold48_piecewise_kabsch import piecewise_kabsch_out_dir
from core.hold48_stitch import TileFold, write_stitched, winning_tile

ALGORITHM = "residual_rmsd_decomposition_then_winning_tile"
DECISION = "D-130"

# Spec §1a / §2: the SAME 10.0 Å gate, aliased and never re-valued, so a
# reader can see the floor is compared against the existing threshold rather
# than against a second number this Spec introduced.
RESIDUAL_FLOOR_GATE_ANGSTROM = RMSD_REFUSE_ANGSTROM

# Spec §1a, as data rather than as a docstring a surface can ignore. The bound
# runs one way and its constant is not tight.
FLOOR_OVER_GATE_CERTIFIES_REFUSAL = True
FLOOR_UNDER_GATE_PROVES_NOTHING = True
FLOOR_IS_SUFFICIENT_NEVER_NECESSARY = True

# Spec §2. ⚠ `rmsd_irreducible` and `correspondence_unverifiable` are NEW
# names for this module's own two measurements. They are **not** D-127's
# `linker_jump_gt_10` (computed after linker inherit across domain pieces) and
# **not** D-128's `seam_jump_gt_10` (computed after a ±32 aa window
# transform). Different algorithms measuring different things; never conflate
# them in a report, a UI, or a test.
REFUSE_RMSD_IRREDUCIBLE = "rmsd_irreducible"
REFUSE_CORRESPONDENCE_UNVERIFIABLE = "correspondence_unverifiable"
REFUSE_REASONS = frozenset(
    {
        REFUSE_OVERLAP_CA_LT_3,
        REFUSE_RMSD_IRREDUCIBLE,
        REFUSE_CORRESPONDENCE_UNVERIFIABLE,
        REFUSE_RMSD_GT_10,
        REFUSE_SINGULAR_COVARIANCE,
    }
)

# Spec §3 — the Phase 4 must-hunt pair, and only those two. Primary
# evaluation inventory, **not** a named-exclusion: the CLI still runs the 27.
PHASE_4_PAIR_PARENT_IDS = frozenset({3272, 3394})

# Explicitly out of the primary inventory (Spec §3; D-129 Phase 5). They may
# appear as **recorded** rows in a CLI run of the 27; they are not success
# targets, they are not re-hunted, and a refuse among them is never a D-130
# miss. Phase 5 is not reopened by this module.
ACCEPT_REFUSE_PARENT_IDS = frozenset({2938, 2939, 3179, 3190, 3321, 3368, 3566, 3432})
NOT_SUCCESS_TARGET_PARENT_IDS = ACCEPT_REFUSE_PARENT_IDS

# Re-export so callers / tests can compare paths without importing D-125 names.
RESIDUAL_RMSD_RESTITCH_PARENT_IDS = KABSCH_RESTITCH_PARENT_IDS

# Spec §1a / §5 — the five path trees a decomposition row can describe.
PATH_KABSCH = "kabsch"
PATH_CONFIDENCE_KABSCH = "confidence_kabsch"
PATH_PIECEWISE_KABSCH = "piecewise_kabsch"
PATH_LINKER_SEAM = "linker_seam"
PATH_RESIDUAL_RMSD = "residual_rmsd"
DECOMPOSITION_PATHS = (
    PATH_KABSCH,
    PATH_CONFIDENCE_KABSCH,
    PATH_PIECEWISE_KABSCH,
    PATH_LINKER_SEAM,
    PATH_RESIDUAL_RMSD,
)
PRIOR_PATHS = DECOMPOSITION_PATHS[:-1]

# Spec §1a's three-valued class. **Unknown is neither** irreducible nor
# placement, and it is never rendered as a number.
CLASS_IRREDUCIBLE = "irreducible"
CLASS_PLACEMENT = "placement"
CLASS_UNKNOWN = "unknown"
RESIDUAL_CLASSES = (CLASS_IRREDUCIBLE, CLASS_PLACEMENT, CLASS_UNKNOWN)

# How a field is known (D-016: the row names its own artefact, per field).
#
# ⚠ `read_from_path_record` is enumerated and deliberately NOT used for
# `rigid_rmsd_angstrom`: only D-125's recorded `rmsd_angstrom` is a
# full-overlap unweighted number, so copying the other three would stack four
# different statistics in one column. See `_achieved_rmsd_from_tree`.
SOURCE_READ_FROM_RECORD = "read_from_path_record"
SOURCE_MEASURED_FROM_ARTIFACTS = "measured_from_path_artifacts"
SOURCE_MEASURED_PRE_TRANSFORM = "measured_pre_transform_from_input_tiles"
SOURCE_ABSENT = "absent"

# Why a number is null. Never a zero, never an assumed pass (Spec §1a).
ABSENCE_TREE_ABSENT = "tree_absent"
ABSENCE_NO_SEAM_ROWS = "no_seam_rows"
ABSENCE_REFUSED_BEFORE_TRANSFORM = "refused_before_transform"
ABSENCE_ARTIFACTS_ABSENT = "path_artifacts_absent"
ABSENCE_OVERLAP_CA_LT_3 = "overlap_ca_lt_3"
ABSENCE_NO_MATCHING_SEAM_ROW = "no_matching_seam_row"

# Spec §1b — what made (or failed to make) a register correction unique.
IDENTITY_DECLARED_PAIRING_AGREES = "declared_pairing_agrees_on_residue_identity"
IDENTITY_UNIQUE_OFFSET = "unique_offset_agrees_on_residue_identity"
IDENTITY_NO_OFFSET_AGREES = "no_offset_agrees_on_residue_identity"
IDENTITY_MULTIPLE_OFFSETS_AGREE = "multiple_offsets_agree_on_residue_identity"
IDENTITY_UNREADABLE = "residue_identity_unreadable_from_tile_artifacts"
IDENTITY_NOT_AUDITED_CLASS = "audit_not_run_residual_class_is_not_placement"


class SiblingOverwriteRefused(AssemblerOverwriteRefused):
    """D-130 artifacts would land on assembler, or on one of the four prior trees."""


Rotation = tuple[tuple[float, float, float], tuple[float, float, float], tuple[float, float, float]]
Translation = tuple[float, float, float]
Pair = tuple[int, int]  # (reference parent residue, moving parent residue)


# ── §1a — the floor, and the direction it runs ───────────────────────────────


def internal_drmsd(
    a: Sequence[Sequence[float]],
    b: Sequence[Sequence[float]],
) -> Optional[float]:
    """Rigid-invariant internal distance RMSD between two corresponded sets.

    ``None`` when there are fewer than two points — an unmeasurable
    disagreement is null, never ``0.0``. Rigid motion of **either** copy
    leaves this unchanged, which is the whole reason it bounds every
    transform at once.
    """
    n = len(a)
    if n != len(b):
        raise ValueError("dRMSD needs equally many corresponding points")
    if n < 2:
        return None
    total = 0.0
    for i in range(n):
        for j in range(i + 1, n):
            delta = _norm(_sub(a[i], a[j])) - _norm(_sub(b[i], b[j]))
            total += delta * delta
    return math.sqrt(2.0 * total / (n * (n - 1)))


def rmsd_floor(internal_drmsd_angstrom: Optional[float]) -> Optional[float]:
    """Spec §1a: ``dRMSD / 2`` — a **proved** lower bound on every rigid RMSD."""
    if internal_drmsd_angstrom is None:
        return None
    return float(internal_drmsd_angstrom) / 2.0


def floor_exceeds_gate(rmsd_floor_angstrom: Optional[float]) -> Optional[bool]:
    """``True`` above 10.0 Å, ``False`` at or below it, **null** when null.

    ⚠ ``True`` certifies that no rigid transform can pass. ``False`` proves
    **nothing** — it means impossibility was not certified, and it is never a
    recovery forecast or an argument that the gate is too strict.
    """
    if rmsd_floor_angstrom is None:
        return None
    return float(rmsd_floor_angstrom) > RESIDUAL_FLOOR_GATE_ANGSTROM


def classify_residual(
    rmsd_floor_angstrom: Optional[float],
    rigid_rmsd_angstrom: Optional[float],
    n_overlap_ca: Optional[int],
) -> str:
    """Spec §1a's three-valued class, with the precedence the table leaves open.

    ⚠ Two of the Spec's three conditions can hold at once: a floor **over**
    the gate with a **null** achieved RMSD is both ``irreducible`` and
    ``unknown``. ``irreducible`` is evaluated **first**, because §2 refuses on
    the floor *before* any fit and therefore always with a null achieved
    RMSD — if ``unknown`` won, D-130's own path could never emit the
    certificate this Spec is built on.

    ⚠ The Spec writes ``placement`` as "floor ≤ 10.0 **and** achieved > 10.0",
    which leaves a **passing** seam unclassed while requiring the field to be
    three-valued. A pass is classed ``placement`` — impossibility was not
    certified, which is exactly true of it — and §11 keeps counting
    ``n_placement`` on the Spec's own condition so a pass is never folded into
    a count the Spec calls "not a recovery forecast".
    """
    if rmsd_floor_angstrom is not None and float(rmsd_floor_angstrom) > RESIDUAL_FLOOR_GATE_ANGSTROM:
        return CLASS_IRREDUCIBLE
    if (
        rmsd_floor_angstrom is None
        or rigid_rmsd_angstrom is None
        or n_overlap_ca is None
        or int(n_overlap_ca) < OVERLAP_CA_MIN
    ):
        return CLASS_UNKNOWN
    return CLASS_PLACEMENT


@dataclass(frozen=True)
class ResidualDecompositionRow:
    """§1a: one row per (path, seam). A null number stays null all the way out."""

    path: str
    moving_tile_index: Optional[int]
    reference_tile_index: Optional[int]
    n_overlap_ca: Optional[int]
    rigid_rmsd_angstrom: Optional[float]
    internal_drmsd_angstrom: Optional[float]
    rmsd_floor_angstrom: Optional[float]
    residual_class: str
    floor_exceeds_gate: Optional[bool]
    rigid_rmsd_source: str
    internal_drmsd_source: str
    absence_reason: Optional[str] = None
    refuse_reason: Optional[str] = None

    def to_json_row(self) -> dict:
        return {
            "path": self.path,
            "moving_tile_index": self.moving_tile_index,
            "reference_tile_index": self.reference_tile_index,
            "n_overlap_ca": self.n_overlap_ca,
            "rigid_rmsd_angstrom": self.rigid_rmsd_angstrom,
            "internal_drmsd_angstrom": self.internal_drmsd_angstrom,
            "rmsd_floor_angstrom": self.rmsd_floor_angstrom,
            "residual_class": self.residual_class,
            "floor_exceeds_gate": self.floor_exceeds_gate,
            "rigid_rmsd_source": self.rigid_rmsd_source,
            "internal_drmsd_source": self.internal_drmsd_source,
            "absence_reason": self.absence_reason,
            "refuse_reason": self.refuse_reason,
            "floor_gate_angstrom": RESIDUAL_FLOOR_GATE_ANGSTROM,
            # ⚠ Rendered with the row so no surface can show the floor without
            # its direction (Spec §1a / §6).
            "floor_over_gate_certifies_refusal": FLOOR_OVER_GATE_CERTIFIES_REFUSAL,
            "floor_under_gate_proves_nothing": FLOOR_UNDER_GATE_PROVES_NOTHING,
            "irreducible_is_sufficient_never_necessary": FLOOR_IS_SUFFICIENT_NEVER_NECESSARY,
        }


# ── §1b — residue identity, and the register audit it decides ────────────────


def residue_name_at_parent(tile: TileFold, parent_res: int) -> Optional[str]:
    """Residue name of the Cα at a parent residue. ``None`` when unreadable.

    ESMFold local numbering: ``local = parent_res - start + 1`` (the D-125
    convention, unchanged). An empty or ``UNK`` name is **not** an identity and
    is returned as ``None`` rather than matched against another blank.
    """
    local = parent_res - tile.start + 1
    for atom in parse_pdb(tile.pdb):
        if atom.is_ca and atom.res_seq == local:
            name = (atom.res_name or "").strip().upper()
            if not name or name == "UNK":
                return None
            return name
    return None


def _offset_pairs(reference: TileFold, moving: TileFold, offset: int) -> list[Pair]:
    """Corresponded (reference, moving) parent residues under a register shift.

    ``offset = 0`` is the pairing every earlier path used. A non-zero offset
    pairs reference residue ``r`` with moving residue ``r + offset``.
    """
    pairs: list[Pair] = []
    for r in range(reference.start, reference.end + 1):
        m = r + offset
        if not (moving.start <= m <= moving.end):
            continue
        if ca_xyz_at_parent(reference, r) is None or ca_xyz_at_parent(moving, m) is None:
            continue
        pairs.append((r, m))
    return pairs


def _identities_agree(reference: TileFold, moving: TileFold, pairs: Sequence[Pair]) -> Optional[bool]:
    """Do all pairs map identical residues? ``None`` when an identity is unreadable.

    ⚠ Unreadable is not disagreement and not agreement — a blank residue name
    matched against another blank would manufacture a correspondence out of
    missing data.
    """
    if not pairs:
        return None
    for r, m in pairs:
        a = residue_name_at_parent(reference, r)
        b = residue_name_at_parent(moving, m)
        if a is None or b is None:
            return None
        if a != b:
            return False
    return True


def candidate_register_offsets(reference: TileFold, moving: TileFold) -> list[int]:
    """Every integer offset whose shifted overlap still has ≥ 3 corresponded Cα.

    ⚠ **Derived, not tuned.** The range is fixed by the two tile spans, so
    there is no scan width to widen and no window to choose. A short chance
    agreement does not buy a recovery — it adds a **second** candidate and
    makes the audit ambiguous, which refuses (Spec §1b step 3).
    """
    lo = moving.start - reference.end
    hi = moving.end - reference.start
    return [k for k in range(lo, hi + 1) if len(_offset_pairs(reference, moving, k)) >= OVERLAP_CA_MIN]


@dataclass(frozen=True)
class CorrespondenceAudit:
    """Spec §1b: what identity said, and what it therefore licenses."""

    correspondence_verified: bool
    register_offset_aa: Optional[int]
    identity_evidence: str
    n_candidate_offsets: Optional[int]
    refuse_reason: Optional[str]

    @property
    def corrected(self) -> bool:
        """A recovery route only exists where identity moved the register."""
        return (
            self.refuse_reason is None
            and self.register_offset_aa is not None
            and self.register_offset_aa != 0
        )

    def to_json(self) -> dict:
        return {
            "correspondence_verified": self.correspondence_verified,
            "register_offset_aa": self.register_offset_aa,
            "identity_evidence": self.identity_evidence,
            "n_candidate_offsets": self.n_candidate_offsets,
            "audit_refuse_reason": self.refuse_reason,
            "decided_by_residue_identity_never_by_rmsd": True,
        }


def audit_correspondence(reference: TileFold, moving: TileFold) -> CorrespondenceAudit:
    """Spec §1b steps 2–3. Decided by residue identity; never by a score.

    Order matters and is the Spec's: **first** ask whether the pairing every
    earlier path used already agrees on identity. If it does, the
    correspondence is **verified**, the offset is ``0``, and there is nothing
    to correct — refitting the same pairs would recover nothing by
    construction. Only a **disagreeing** declared pairing opens the search for
    a correction, and that correction must be **unique**: none or more than one
    agreeing offset is an ambiguity, and an ambiguity **refuses**.
    """
    declared = _offset_pairs(reference, moving, 0)
    declared_agrees = _identities_agree(reference, moving, declared)
    if declared_agrees is None:
        return CorrespondenceAudit(
            correspondence_verified=False,
            register_offset_aa=None,
            identity_evidence=IDENTITY_UNREADABLE,
            n_candidate_offsets=None,
            refuse_reason=REFUSE_CORRESPONDENCE_UNVERIFIABLE,
        )
    if declared_agrees:
        return CorrespondenceAudit(
            correspondence_verified=True,
            register_offset_aa=0,
            identity_evidence=IDENTITY_DECLARED_PAIRING_AGREES,
            n_candidate_offsets=None,
            refuse_reason=None,
        )

    agreeing = [
        k
        for k in candidate_register_offsets(reference, moving)
        if _identities_agree(reference, moving, _offset_pairs(reference, moving, k)) is True
    ]
    if len(agreeing) == 1:
        return CorrespondenceAudit(
            correspondence_verified=False,
            register_offset_aa=agreeing[0],
            identity_evidence=IDENTITY_UNIQUE_OFFSET,
            n_candidate_offsets=1,
            refuse_reason=None,
        )
    return CorrespondenceAudit(
        correspondence_verified=False,
        register_offset_aa=None,
        identity_evidence=(
            IDENTITY_NO_OFFSET_AGREES if not agreeing else IDENTITY_MULTIPLE_OFFSETS_AGREE
        ),
        n_candidate_offsets=len(agreeing),
        refuse_reason=REFUSE_CORRESPONDENCE_UNVERIFIABLE,
    )


def paired_ca_for_offset(
    reference: TileFold,
    moving: TileFold,
    offset: int,
) -> tuple[list[tuple[float, float, float]], list[tuple[float, float, float]], list[Pair]]:
    """Moving / reference Cα for a register offset, as the **full** shifted overlap.

    ⚠ No pair is dropped to improve a number. Dropping pairs from the
    corrected correspondence is trim, and trim is forbidden (Spec §1b step 4,
    §9).
    """
    pairs = _offset_pairs(reference, moving, offset)
    moving_pts = [ca_xyz_at_parent(moving, m) for _r, m in pairs]
    ref_pts = [ca_xyz_at_parent(reference, r) for r, _m in pairs]
    return moving_pts, ref_pts, pairs


# ── §1b step 5 — exactly D-125's fit, unchanged ──────────────────────────────


@dataclass(frozen=True)
class ResidualFit:
    """One D-125 fit on one (possibly corrected) correspondence."""

    n_ca: int
    rmsd_angstrom: Optional[float]
    refuse_reason: Optional[str]
    rotation: Optional[Rotation]
    translation: Optional[Translation]

    @property
    def accepted(self) -> bool:
        return self.refuse_reason is None and self.rotation is not None


def fit_correspondence(
    moving_pts: Sequence[Sequence[float]],
    ref_pts: Sequence[Sequence[float]],
) -> ResidualFit:
    """One **unweighted, untrimmed** Kabsch on the full correspondence.

    ⚠ This calls ``core.hold48_kabsch.kabsch_rotation_translation`` — D-125's
    fit, imported rather than re-implemented, so "unchanged" is enforced by
    the import and not by a promise. **No weights** (that is D-126). **No trim
    loop** (the D-126 lie surface). **No pieces** (D-127). **No window**
    (D-128).
    """
    n = len(moving_pts)
    if n < OVERLAP_CA_MIN:
        return ResidualFit(n, None, REFUSE_OVERLAP_CA_LT_3, None, None)
    R, t, rmsd, rank = kabsch_rotation_translation(moving_pts, ref_pts)
    if rank < COVARIANCE_RANK_MIN:
        return ResidualFit(n, None, REFUSE_SINGULAR_COVARIANCE, None, None)
    if rmsd > RMSD_REFUSE_ANGSTROM:
        return ResidualFit(n, rmsd, REFUSE_RMSD_GT_10, None, None)
    return ResidualFit(n, rmsd, None, R, t)


def transform_tile(tile: TileFold, fit: ResidualFit) -> TileFold:
    """Apply ``R, t`` to the **whole** moving tile — D-125's apply unit."""
    if not fit.accepted or fit.rotation is None or fit.translation is None:
        raise ValueError("refuse is fail-closed — do not invent a transformed pose")
    return TileFold(
        start=tile.start,
        end=tile.end,
        pdb=apply_rigid_transform_pdb(tile.pdb, fit.rotation, fit.translation),
        plddt=tile.plddt,
        pae=tile.pae,
    )


# ── the D-130 seam record ────────────────────────────────────────────────────


@dataclass(frozen=True)
class ResidualSeamRecord:
    """One D-130 seam: what the floor said, what identity said, what was fitted."""

    moving_tile_index: int
    reference_tile_index: int
    overlap_start: int
    overlap_end: int
    n_overlap_ca: Optional[int]
    internal_drmsd_angstrom: Optional[float]
    rmsd_floor_angstrom: Optional[float]
    residual_class: str
    correspondence_verified: Optional[bool]
    register_offset_aa: Optional[int]
    identity_evidence: Optional[str]
    n_ca: Optional[int]
    rmsd_angstrom: Optional[float]
    max_ca_jump_angstrom: Optional[float]
    pre_fit_rmsd_angstrom: Optional[float]
    refuse_reason: Optional[str]
    rotation: Optional[Rotation]
    translation: Optional[Translation]

    @property
    def accepted(self) -> bool:
        return self.refuse_reason is None

    @property
    def transformed(self) -> bool:
        return self.rotation is not None and self.translation is not None

    @property
    def recovered(self) -> bool:
        """Accepted **and** identity actually moved the register.

        An accept with ``register_offset_aa == 0`` is D-125's result on
        D-125's pairs — a measurement, not a recovery. Calling it one would be
        the pass-by-restatement this Spec exists to refuse.
        """
        return self.accepted and bool(self.register_offset_aa)

    def to_json_row(self) -> dict:
        return {
            "moving_tile_index": self.moving_tile_index,
            "reference_tile_index": self.reference_tile_index,
            "overlap_start": self.overlap_start,
            "overlap_end": self.overlap_end,
            "n_overlap_ca": self.n_overlap_ca,
            "internal_drmsd_angstrom": self.internal_drmsd_angstrom,
            "rmsd_floor_angstrom": self.rmsd_floor_angstrom,
            "floor_exceeds_gate": floor_exceeds_gate(self.rmsd_floor_angstrom),
            "residual_class": self.residual_class,
            "correspondence_verified": self.correspondence_verified,
            "register_offset_aa": self.register_offset_aa,
            "identity_evidence": self.identity_evidence,
            "n_ca": self.n_ca,
            "rmsd_angstrom": self.rmsd_angstrom,
            "pre_fit_rmsd_angstrom": self.pre_fit_rmsd_angstrom,
            "max_ca_jump_angstrom": self.max_ca_jump_angstrom,
            "refuse_reason": self.refuse_reason,
            "recovered": self.recovered,
            "floor_gate_angstrom": RESIDUAL_FLOOR_GATE_ANGSTROM,
            "rmsd_refuse_angstrom": RMSD_REFUSE_ANGSTROM,
            "R": [list(row) for row in self.rotation] if self.rotation is not None else None,
            "t": list(self.translation) if self.translation is not None else None,
        }


@dataclass(frozen=True)
class ResidualRmsdRestitchResult:
    accepted: bool
    parent_job_id: int
    out_dir: Path
    seams: tuple[ResidualSeamRecord, ...]
    decomposition: tuple[ResidualDecompositionRow, ...]
    tiles: tuple[TileFold, ...]
    stitched: Optional[dict[str, str]]

    @property
    def recovered(self) -> bool:
        """Accepted **and** at least one seam's register was identity-corrected."""
        return self.accepted and any(s.recovered for s in self.seams)


# ── seam walk ────────────────────────────────────────────────────────────────


def _run_seam(
    *,
    reference: TileFold,
    moving: TileFold,
    moving_tile_index: int,
    reference_tile_index: int,
) -> tuple[ResidualSeamRecord, Optional[TileFold]]:
    """One seam: floor first, then the audit, then D-125's fit. Fail closed.

    The order is the Spec's and it is not an optimisation. The floor is
    computed **before** any fit, because a floor over the gate makes the
    refusal *certified* rather than observed — and because auditing a
    correspondence no rigid transform could ever satisfy would be a search.
    """
    overlap = overlap_parent_residues(reference, moving)
    moving_pts, ref_pts, _used = paired_overlap_ca(reference, moving)
    n = len(moving_pts)

    def _record(
        *,
        n_overlap_ca: Optional[int] = None,
        drmsd: Optional[float] = None,
        floor: Optional[float] = None,
        residual_class: str = CLASS_UNKNOWN,
        audit: Optional[CorrespondenceAudit] = None,
        n_ca: Optional[int] = None,
        rmsd: Optional[float] = None,
        pre_fit_rmsd: Optional[float] = None,
        max_jump: Optional[float] = None,
        refuse_reason: Optional[str] = None,
        rotation: Optional[Rotation] = None,
        translation: Optional[Translation] = None,
    ) -> ResidualSeamRecord:
        return ResidualSeamRecord(
            moving_tile_index=moving_tile_index,
            reference_tile_index=reference_tile_index,
            overlap_start=overlap[0] if overlap else 0,
            overlap_end=overlap[-1] if overlap else 0,
            n_overlap_ca=n_overlap_ca,
            internal_drmsd_angstrom=drmsd,
            rmsd_floor_angstrom=floor,
            residual_class=residual_class,
            correspondence_verified=audit.correspondence_verified if audit else None,
            register_offset_aa=audit.register_offset_aa if audit else None,
            identity_evidence=audit.identity_evidence if audit else None,
            n_ca=n_ca,
            rmsd_angstrom=rmsd,
            pre_fit_rmsd_angstrom=pre_fit_rmsd,
            max_ca_jump_angstrom=max_jump,
            refuse_reason=refuse_reason,
            rotation=rotation,
            translation=translation,
        )

    # Spec §2 row 1 — Kabsch still needs three corresponding points, and a
    # floor over fewer than two pairs is not a floor.
    if n < OVERLAP_CA_MIN:
        return _record(n_overlap_ca=n, refuse_reason=REFUSE_OVERLAP_CA_LT_3), None

    drmsd = internal_drmsd(moving_pts, ref_pts)
    floor = rmsd_floor(drmsd)

    # Spec §2 row 2 — a CERTIFIED refusal, computed before any transform. The
    # achieved RMSD is null here and stays null: nothing was fitted.
    if floor is not None and floor > RESIDUAL_FLOOR_GATE_ANGSTROM:
        return (
            _record(
                n_overlap_ca=n,
                drmsd=drmsd,
                floor=floor,
                residual_class=CLASS_IRREDUCIBLE,
                refuse_reason=REFUSE_RMSD_IRREDUCIBLE,
            ),
            None,
        )

    declared_fit = fit_correspondence(moving_pts, ref_pts)
    pre_fit_rmsd = declared_fit.rmsd_angstrom
    residual_class = classify_residual(floor, pre_fit_rmsd, n)

    if residual_class == CLASS_UNKNOWN:
        # §1b step 1: an `unknown` seam refuses `correspondence_unverifiable`
        # — unknown is neither irreducible nor placement, and it licenses
        # nothing. A degenerate covariance is the one way this branch is
        # reachable with a floor in hand, and it is named as itself rather
        # than hidden behind the audit's reason.
        return (
            _record(
                n_overlap_ca=n,
                drmsd=drmsd,
                floor=floor,
                residual_class=residual_class,
                n_ca=declared_fit.n_ca,
                pre_fit_rmsd=pre_fit_rmsd,
                refuse_reason=(
                    declared_fit.refuse_reason
                    if declared_fit.refuse_reason == REFUSE_SINGULAR_COVARIANCE
                    else REFUSE_CORRESPONDENCE_UNVERIFIABLE
                ),
            ),
            None,
        )

    if declared_fit.accepted:
        # The declared correspondence already lands inside the gate. Nothing
        # offends: no audit, no correction, no second correspondence tried.
        # A **recorded** accept, and `recovered` stays False because identity
        # moved nothing.
        transformed = transform_tile(moving, declared_fit)
        return (
            _record(
                n_overlap_ca=n,
                drmsd=drmsd,
                floor=floor,
                residual_class=residual_class,
                audit=CorrespondenceAudit(
                    correspondence_verified=True,
                    register_offset_aa=0,
                    identity_evidence=IDENTITY_NOT_AUDITED_CLASS,
                    n_candidate_offsets=None,
                    refuse_reason=None,
                ),
                n_ca=declared_fit.n_ca,
                rmsd=declared_fit.rmsd_angstrom,
                pre_fit_rmsd=pre_fit_rmsd,
                max_jump=seam_max_ca_jump(reference, transformed),
                rotation=declared_fit.rotation,
                translation=declared_fit.translation,
            ),
            transformed,
        )

    # ── §1b: the class is `placement`, so the audit may run ──────────────────
    #
    # Everything else has already returned: `irreducible` refused on the floor
    # before any fit, `unknown` refused above, and an accepted declared fit
    # needs no correction. What is left is exactly the Spec's gate — floor
    # inside the gate, achieved RMSD outside it — so the audit runs here and
    # only here.
    audit = audit_correspondence(reference, moving)
    if audit.refuse_reason is not None:
        return (
            _record(
                n_overlap_ca=n,
                drmsd=drmsd,
                floor=floor,
                residual_class=residual_class,
                audit=audit,
                n_ca=declared_fit.n_ca,
                pre_fit_rmsd=pre_fit_rmsd,
                refuse_reason=audit.refuse_reason,
            ),
            None,
        )

    if audit.correspondence_verified:
        # The pairing was already right, so D-125's fit already achieved the
        # optimum for it. Refitting the same pairs would recover nothing **by
        # construction**; the honest outcome is the refuse D-125's own number
        # earns.
        return (
            _record(
                n_overlap_ca=n,
                drmsd=drmsd,
                floor=floor,
                residual_class=residual_class,
                audit=audit,
                n_ca=declared_fit.n_ca,
                rmsd=declared_fit.rmsd_angstrom,
                pre_fit_rmsd=pre_fit_rmsd,
                refuse_reason=REFUSE_RMSD_GT_10,
            ),
            None,
        )

    # ── a unique, identity-determined correction ────────────────────────────
    offset = int(audit.register_offset_aa or 0)
    corrected_moving, corrected_ref, corrected_pairs = paired_ca_for_offset(
        reference, moving, offset
    )
    corrected_n = len(corrected_pairs)
    corrected_drmsd = internal_drmsd(corrected_moving, corrected_ref)
    corrected_floor = rmsd_floor(corrected_drmsd)

    if corrected_n < OVERLAP_CA_MIN:
        return (
            _record(
                n_overlap_ca=corrected_n,
                drmsd=corrected_drmsd,
                floor=corrected_floor,
                residual_class=classify_residual(corrected_floor, None, corrected_n),
                audit=audit,
                n_ca=corrected_n,
                pre_fit_rmsd=pre_fit_rmsd,
                refuse_reason=REFUSE_OVERLAP_CA_LT_3,
            ),
            None,
        )

    # The correspondence changed, so the floor did too — and a corrected
    # correspondence already certified unreachable is not fitted.
    if corrected_floor is not None and corrected_floor > RESIDUAL_FLOOR_GATE_ANGSTROM:
        return (
            _record(
                n_overlap_ca=corrected_n,
                drmsd=corrected_drmsd,
                floor=corrected_floor,
                residual_class=CLASS_IRREDUCIBLE,
                audit=audit,
                n_ca=corrected_n,
                pre_fit_rmsd=pre_fit_rmsd,
                refuse_reason=REFUSE_RMSD_IRREDUCIBLE,
            ),
            None,
        )

    fit = fit_correspondence(corrected_moving, corrected_ref)
    corrected_class = classify_residual(corrected_floor, fit.rmsd_angstrom, corrected_n)
    if not fit.accepted:
        return (
            _record(
                n_overlap_ca=corrected_n,
                drmsd=corrected_drmsd,
                floor=corrected_floor,
                residual_class=corrected_class,
                audit=audit,
                n_ca=fit.n_ca,
                rmsd=fit.rmsd_angstrom,
                pre_fit_rmsd=pre_fit_rmsd,
                refuse_reason=fit.refuse_reason,
            ),
            None,
        )

    transformed = transform_tile(moving, fit)
    return (
        _record(
            n_overlap_ca=corrected_n,
            drmsd=corrected_drmsd,
            floor=corrected_floor,
            residual_class=corrected_class,
            audit=audit,
            n_ca=fit.n_ca,
            rmsd=fit.rmsd_angstrom,
            pre_fit_rmsd=pre_fit_rmsd,
            max_jump=seam_max_ca_jump(reference, transformed),
            rotation=fit.rotation,
            translation=fit.translation,
        ),
        transformed,
    )


def align_tiles(tiles: Sequence[TileFold]) -> tuple[list[TileFold], list[ResidualSeamRecord], bool]:
    """N-terminal tile is the reference; later tiles chain onto the last accepted frame.

    All-or-nothing: the first refuse stops further transforms. ``accepted`` is
    True only when every inbound seam was accepted. Untransformed copies stay
    in the returned list so a caller can inspect them; they are not written.
    """
    if not tiles:
        raise ValueError("align_tiles needs at least one tile")
    ordered = sorted(tiles, key=lambda t: (t.start, t.end))
    out: list[TileFold] = [ordered[0]]
    seams: list[ResidualSeamRecord] = []
    last_accepted = ordered[0]
    last_accepted_index = 1
    all_ok = True
    for i, moving in enumerate(ordered[1:], start=2):
        record, transformed = _run_seam(
            reference=last_accepted,
            moving=moving,
            moving_tile_index=i,
            reference_tile_index=last_accepted_index,
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


# ── §1a rows for every path (prior trees are READ) ───────────────────────────



def path_tree_dir(out_root: Path | str, parent_job_id: int, path_name: str) -> Path:
    if path_name == PATH_KABSCH:
        return kabsch_out_dir(out_root, parent_job_id)
    if path_name == PATH_CONFIDENCE_KABSCH:
        return confidence_kabsch_out_dir(out_root, parent_job_id)
    if path_name == PATH_PIECEWISE_KABSCH:
        return piecewise_kabsch_out_dir(out_root, parent_job_id)
    if path_name == PATH_LINKER_SEAM:
        return linker_seam_out_dir(out_root, parent_job_id)
    if path_name == PATH_RESIDUAL_RMSD:
        return residual_rmsd_out_dir(out_root, parent_job_id)
    raise ValueError(f"unknown decomposition path {path_name!r}")


def _full_overlap_rmsd(reference: TileFold, moving: TileFold) -> Optional[float]:
    """The full-overlap corresponded Cα RMSD **as the two tiles now sit**.

    ⚠ Not a fit. No transform is computed here — this is the residual the
    coordinates already carry, which is what §1a means by "the RMSD that path
    **ends** with". ``None`` when the two share no corresponded Cα.
    """
    moving_pts, ref_pts, _used = paired_overlap_ca(reference, moving)
    if not moving_pts:
        return None
    total = sum(_norm(_sub(p, q)) ** 2 for p, q in zip(moving_pts, ref_pts))
    return math.sqrt(total / len(moving_pts))


def _achieved_rmsd_from_tree(tree: Path) -> dict[Pair, Optional[float]]:
    """Full-overlap RMSD per seam, measured from the PDBs a path itself wrote.

    ⚠ **A prior path's recorded ``rmsd_angstrom`` is deliberately NOT read.**
    D-125's is the full-overlap unweighted fit, but D-126's is trimmed and
    pLDDT-weighted, D-127's is per-domain and D-128's is weighted inside a
    ±32 aa window. Stacking four different statistics in one column headed
    *full-overlap RMSD* is the D-126 lie surface one level up. So the number
    is **measured** from that path's own artifacts, and its source says so.
    """
    tiles = _tiles_from_tree(tree)
    out: dict[Pair, Optional[float]] = {}
    for i in range(1, len(tiles)):
        out[(i + 1, i)] = _full_overlap_rmsd(tiles[i - 1], tiles[i])
    return out


def _seam_geometry(tiles: Sequence[TileFold]) -> dict[Pair, tuple[Optional[int], Optional[float]]]:
    """Per seam of the INPUT tiles: corresponded Cα count and internal dRMSD.

    ⚠ Measured **before any transform** (Spec §1a). Two of the five paths do
    not move a tile rigidly — D-127 moves per-domain pieces, D-128 moves a
    window — so measuring the floor from their outputs would silently make it
    path-dependent. It is not: the floor is a property of the two ESMFold
    tiles and the correspondence, which is exactly why it bounds all five
    paths at once.
    """
    ordered = sorted(tiles, key=lambda t: (t.start, t.end))
    out: dict[Pair, tuple[Optional[int], Optional[float]]] = {}
    for i in range(1, len(ordered)):
        moving_pts, ref_pts, _used = paired_overlap_ca(ordered[i - 1], ordered[i])
        n = len(moving_pts)
        out[(i + 1, i)] = (n, internal_drmsd(moving_pts, ref_pts) if n >= OVERLAP_CA_MIN else None)
    return out


def _absence_row(path_name: str, reason: str) -> ResidualDecompositionRow:
    """One honest-absence row. Never a zero, never an assumed pass."""
    return ResidualDecompositionRow(
        path=path_name,
        moving_tile_index=None,
        reference_tile_index=None,
        n_overlap_ca=None,
        rigid_rmsd_angstrom=None,
        internal_drmsd_angstrom=None,
        rmsd_floor_angstrom=None,
        residual_class=CLASS_UNKNOWN,
        floor_exceeds_gate=None,
        rigid_rmsd_source=SOURCE_ABSENT,
        internal_drmsd_source=SOURCE_ABSENT,
        absence_reason=reason,
    )


def read_path_decomposition(
    out_root: Path | str,
    parent_job_id: int,
    path_name: str,
    seam_geometry: Mapping[Pair, tuple[Optional[int], Optional[float]]],
) -> list[ResidualDecompositionRow]:
    """§1a rows for one prior path, by **reading** that path's tree.

    The tree is opened read-only: D-130 never writes into ``kabsch/``,
    ``confidence_kabsch/``, ``piecewise_kabsch/`` or ``linker_seam/``. An
    absent tree is one row with a stated reason, and a path that refused
    before any transform carries a **null** achieved RMSD with
    ``refused_before_transform`` — never a zero and never an assumed pass.
    """
    rows = read_seam_rows(out_root, parent_job_id, path_name)
    if rows is None:
        return [_absence_row(path_name, ABSENCE_TREE_ABSENT)]
    if not rows:
        return [_absence_row(path_name, ABSENCE_NO_SEAM_ROWS)]

    tree = path_tree_dir(out_root, parent_job_id, path_name)
    measured: Optional[dict[Pair, Optional[float]]] = None
    out: list[ResidualDecompositionRow] = []
    for row in rows:
        moving = row.get("moving_tile_index")
        reference = row.get("reference_tile_index")
        refuse_reason = row.get("refuse_reason")
        key: Optional[Pair] = (
            (int(moving), int(reference)) if moving is not None and reference is not None else None
        )
        n_overlap, drmsd = seam_geometry.get(key, (None, None)) if key else (None, None)
        floor = rmsd_floor(drmsd)
        drmsd_source = SOURCE_MEASURED_PRE_TRANSFORM if drmsd is not None else SOURCE_ABSENT

        if measured is None:
            measured = _achieved_rmsd_from_tree(tree)
        achieved = measured.get(key) if key is not None else None
        if achieved is not None:
            rmsd_source = SOURCE_MEASURED_FROM_ARTIFACTS
            absence = None
        else:
            rmsd_source = SOURCE_ABSENT
            absence = (
                ABSENCE_REFUSED_BEFORE_TRANSFORM if refuse_reason else ABSENCE_ARTIFACTS_ABSENT
            )
        if key is None:
            absence = ABSENCE_NO_MATCHING_SEAM_ROW
        elif drmsd is None and absence is None:
            absence = ABSENCE_OVERLAP_CA_LT_3

        out.append(
            ResidualDecompositionRow(
                path=path_name,
                moving_tile_index=moving,
                reference_tile_index=reference,
                n_overlap_ca=n_overlap,
                rigid_rmsd_angstrom=achieved,
                internal_drmsd_angstrom=drmsd,
                rmsd_floor_angstrom=floor,
                residual_class=classify_residual(floor, achieved, n_overlap),
                floor_exceeds_gate=floor_exceeds_gate(floor),
                rigid_rmsd_source=rmsd_source,
                internal_drmsd_source=drmsd_source,
                absence_reason=absence,
                refuse_reason=refuse_reason,
            )
        )
    return out


def residual_rmsd_decomposition_rows(
    seams: Sequence[ResidualSeamRecord],
    seam_geometry: Mapping[Pair, tuple[Optional[int], Optional[float]]],
) -> list[ResidualDecompositionRow]:
    """§1a rows for D-130's own path, from this run.

    The achieved RMSD is the seam's **post-fit** full-overlap RMSD, and it is
    **null** when the seam refused before any transform — including every
    ``rmsd_irreducible`` refuse, where the certificate is the floor and no
    transform was ever attempted.
    """
    out: list[ResidualDecompositionRow] = []
    for seam in seams:
        key = (seam.moving_tile_index, seam.reference_tile_index)
        n_overlap, drmsd = seam_geometry.get(key, (None, None))
        # A corrected register changes the correspondence, so the seam's own
        # numbers win over the declared-overlap geometry where they exist.
        if seam.internal_drmsd_angstrom is not None:
            drmsd = seam.internal_drmsd_angstrom
            n_overlap = seam.n_overlap_ca
        floor = rmsd_floor(drmsd)
        achieved = seam.rmsd_angstrom if seam.accepted else None
        out.append(
            ResidualDecompositionRow(
                path=PATH_RESIDUAL_RMSD,
                moving_tile_index=seam.moving_tile_index,
                reference_tile_index=seam.reference_tile_index,
                n_overlap_ca=n_overlap,
                rigid_rmsd_angstrom=achieved,
                internal_drmsd_angstrom=drmsd,
                rmsd_floor_angstrom=floor,
                residual_class=classify_residual(floor, achieved, n_overlap),
                floor_exceeds_gate=floor_exceeds_gate(floor),
                rigid_rmsd_source=(
                    SOURCE_MEASURED_FROM_ARTIFACTS if achieved is not None else SOURCE_ABSENT
                ),
                internal_drmsd_source=(
                    SOURCE_MEASURED_PRE_TRANSFORM if drmsd is not None else SOURCE_ABSENT
                ),
                absence_reason=(
                    None
                    if achieved is not None
                    else (
                        ABSENCE_OVERLAP_CA_LT_3
                        if seam.refuse_reason == REFUSE_OVERLAP_CA_LT_3
                        else ABSENCE_REFUSED_BEFORE_TRANSFORM
                    )
                ),
                refuse_reason=seam.refuse_reason,
            )
        )
    return out


def collect_decomposition(
    out_root: Path | str,
    parent_job_id: int,
    tiles: Sequence[TileFold],
    seams: Sequence[ResidualSeamRecord],
) -> list[ResidualDecompositionRow]:
    """All five paths' §1a rows: four read from disk, D-130's from this run."""
    geometry = _seam_geometry(tiles)
    rows: list[ResidualDecompositionRow] = []
    for path_name in PRIOR_PATHS:
        rows.extend(read_path_decomposition(out_root, parent_job_id, path_name, geometry))
    rows.extend(residual_rmsd_decomposition_rows(seams, geometry))
    return rows


# ── sixth sibling tree ───────────────────────────────────────────────────────


def residual_rmsd_out_dir(out_root: Path | str, parent_job_id: int) -> Path:
    return Path(out_root) / "residual_rmsd" / str(parent_job_id)


def refuse_sibling_overwrite(
    out_dir: Path,
    assembler_dir: Optional[Path | str] = None,
    d125_dir: Optional[Path | str] = None,
    d126_dir: Optional[Path | str] = None,
    d127_dir: Optional[Path | str] = None,
    d128_dir: Optional[Path | str] = None,
) -> None:
    """Never write D-130 artifacts as if they were one of the five prior paths."""
    out = Path(out_dir).resolve()
    if "residual_rmsd" not in out.parts:
        raise SiblingOverwriteRefused(
            f"D-130 artifacts must land under a residual_rmsd/ directory, not {out}"
        )
    dest_pdb = (out / "stitched.pdb").resolve()
    checks: list[tuple[Optional[Path | str], str]] = [
        (assembler_dir, "assembler"),
        (d125_dir, "D-125 kabsch"),
        (d126_dir, "D-126 confidence_kabsch"),
        (d127_dir, "D-127 piecewise_kabsch"),
        (d128_dir, "D-128 linker_seam"),
    ]
    for other, label in checks:
        if other is None:
            continue
        other_path = Path(other).resolve()
        if out == other_path or dest_pdb == (other_path / "stitched.pdb").resolve():
            raise SiblingOverwriteRefused(
                f"refusing to write D-130 artifacts over {label} dir {other_path}"
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
    seams: Sequence[ResidualSeamRecord],
    decomposition: Sequence[ResidualDecompositionRow],
    accepted: bool,
) -> None:
    payload = {
        "algorithm": ALGORITHM,
        "decision": DECISION,
        "parent_job_id": parent_job_id,
        "tile_job_ids": list(tile_job_ids),
        "windows": [list(w) for w in windows],
        "accepted": accepted,
        "recovered": accepted and any(s.recovered for s in seams),
        "seams": [s.to_json_row() for s in seams],
        "residual_decomposition": [r.to_json_row() for r in decomposition],
        "floor_gate_angstrom": RESIDUAL_FLOOR_GATE_ANGSTROM,
        "rmsd_refuse_angstrom": RMSD_REFUSE_ANGSTROM,
        "floor_over_gate_certifies_refusal": FLOOR_OVER_GATE_CERTIFIES_REFUSAL,
        "floor_under_gate_proves_nothing": FLOOR_UNDER_GATE_PROVES_NOTHING,
        "irreducible_is_sufficient_never_necessary": FLOOR_IS_SUFFICIENT_NEVER_NECESSARY,
        "zero_of_two_recovered_is_allowed": True,
        "fit_is_d125_unchanged": True,
        "no_trim_loop": True,
        "no_weights": True,
        "no_domain_pieces_fitted": True,
        "no_window": True,
        "no_linker_inherit": True,
        "served_path": "assembler",
        "seams_solved": False,
    }
    (out / "provenance.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    with (out / "seams.jsonl").open("w", encoding="utf-8") as fh:
        for seam in seams:
            fh.write(json.dumps(seam.to_json_row()) + "\n")
    with (out / "residual_decomposition.jsonl").open("w", encoding="utf-8") as fh:
        for row in decomposition:
            fh.write(json.dumps(row.to_json_row()) + "\n")


def write_residual_rmsd_restitch(
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
    d128_dir: Optional[Path | str] = None,
) -> ResidualRmsdRestitchResult:
    """Decompose every path's residual, optionally audit + refit, then the assembler.

    The §1a rows are written whatever the outcome — a refuse is a **recorded**
    outcome, and recovering nothing is a pre-registered allowed one. Success
    artifacts are written only when every seam was accepted, and no other
    path's ``stitched.pdb`` is ever presented as a D-130 result.
    """
    require_inventory_parent(parent_job_id)
    out = residual_rmsd_out_dir(out_root, parent_job_id)
    if d125_dir is None:
        d125_dir = kabsch_out_dir(out_root, parent_job_id)
    if d126_dir is None:
        d126_dir = confidence_kabsch_out_dir(out_root, parent_job_id)
    if d127_dir is None:
        d127_dir = piecewise_kabsch_out_dir(out_root, parent_job_id)
    if d128_dir is None:
        d128_dir = linker_seam_out_dir(out_root, parent_job_id)
    refuse_sibling_overwrite(out, assembler_dir, d125_dir, d126_dir, d127_dir, d128_dir)
    if winning_tile is None:  # pragma: no cover — import pin
        raise RuntimeError("winning_tile must remain importable")

    aligned, seams, accepted = align_tiles(tiles)
    decomposition = collect_decomposition(out_root, parent_job_id, tiles, seams)
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
        decomposition=decomposition,
        accepted=accepted,
    )

    stitched = None
    if accepted:
        for n, tile in enumerate(aligned, start=1):
            if n == 1:
                continue
            (out / f"tile{n}_transformed.pdb").write_text(tile.pdb, encoding="utf-8")
        stitched = write_stitched(aligned, length, out)
    else:
        _clear_success_artifacts(out)

    return ResidualRmsdRestitchResult(
        accepted=accepted,
        parent_job_id=parent_job_id,
        out_dir=out,
        seams=tuple(seams),
        decomposition=tuple(decomposition),
        tiles=tuple(aligned),
        stitched=stitched,
    )


# ── ops report (Spec §11) ────────────────────────────────────────────────────


@dataclass(frozen=True)
class OpsSuccessReport:
    """Spec §11 required report fields. **Not** a CI assert against live ops."""

    n_overlap_pairs_measured: int
    n_irreducible: int
    n_placement: int
    n_placement_within_gate: int
    n_residual_unknown: int
    n_correspondence_audited: int
    n_correspondence_corrected: int
    n_correspondence_unverifiable: int
    correspondence_counts_source: str
    recovered_of_two: int
    recovered_of_two_source: str
    n_d125_pass_d130_refuse: int
    n_d126_pass_d130_refuse: int
    n_d127_pass_d130_refuse: int
    n_d128_pass_d130_refuse: int
    n_d126_recovered_d130_refuse: int

    def to_json(self) -> dict:
        return {
            "n_overlap_pairs_measured": self.n_overlap_pairs_measured,
            "n_irreducible": self.n_irreducible,
            "n_placement": self.n_placement,
            "n_placement_within_gate": self.n_placement_within_gate,
            "n_residual_unknown": self.n_residual_unknown,
            "n_correspondence_audited": self.n_correspondence_audited,
            "n_correspondence_corrected": self.n_correspondence_corrected,
            "n_correspondence_unverifiable": self.n_correspondence_unverifiable,
            "correspondence_counts_source": self.correspondence_counts_source,
            "recovered_of_two": self.recovered_of_two,
            "recovered_of_two_source": self.recovered_of_two_source,
            "n_d125_pass_d130_refuse": self.n_d125_pass_d130_refuse,
            "n_d126_pass_d130_refuse": self.n_d126_pass_d130_refuse,
            "n_d127_pass_d130_refuse": self.n_d127_pass_d130_refuse,
            "n_d128_pass_d130_refuse": self.n_d128_pass_d130_refuse,
            "n_d126_recovered_d130_refuse": self.n_d126_recovered_d130_refuse,
            "n_d125_pass_d130_refuse_is_named_finding": self.n_d125_pass_d130_refuse > 0,
            "n_d126_pass_d130_refuse_is_named_finding": self.n_d126_pass_d130_refuse > 0,
            "n_d127_pass_d130_refuse_is_named_finding": self.n_d127_pass_d130_refuse > 0,
            "n_d128_pass_d130_refuse_is_named_finding": self.n_d128_pass_d130_refuse > 0,
            "n_d126_recovered_d130_refuse_is_named_finding": (
                self.n_d126_recovered_d130_refuse > 0
            ),
            "zero_of_two_recovered_is_allowed": True,
            "named_refuse_after_a_failed_hunt_is_a_complete_outcome": True,
            "unknown_is_neither_irreducible_nor_placement": True,
            "n_placement_is_not_a_recovery_forecast": True,
            "floor_gate_angstrom": RESIDUAL_FLOOR_GATE_ANGSTROM,
            "floor_over_gate_certifies_refusal": FLOOR_OVER_GATE_CERTIFIES_REFUSAL,
            "floor_under_gate_proves_nothing": FLOOR_UNDER_GATE_PROVES_NOTHING,
            "phase_4_pair": sorted(PHASE_4_PAIR_PARENT_IDS),
            "phase_5_not_reopened": True,
            "accept_refuse_parents_are_not_success_targets": sorted(ACCEPT_REFUSE_PARENT_IDS),
            "served_path": "assembler",
            "seams_solved": False,
            "d130_algorithm": ALGORITHM,
            "d130_decision": DECISION,
        }


# The two D-126 OPS recovered, as recorded at D-126-B / D-127-B. ⚠ Quoted, not
# re-measured — §11's `n_d126_recovered_d130_refuse` is the count most likely
# to embarrass a D-130 run, because 3394 is in this Spec's inventory.
D126_RECOVERED_PARENT_IDS = frozenset({3368, 3394})


def _count_class(rows: Iterable[Mapping | ResidualDecompositionRow], name: str) -> int:
    n = 0
    for row in rows:
        payload = row.to_json_row() if isinstance(row, ResidualDecompositionRow) else row
        if payload.get("residual_class") == name:
            n += 1
    return n


def build_ops_success_report(
    d125_accepted: Mapping[int, bool],
    d126_accepted: Mapping[int, bool],
    d127_accepted: Mapping[int, bool],
    d128_accepted: Mapping[int, bool],
    d130_accepted: Mapping[int, bool],
    *,
    d130_recovered: Optional[Mapping[int, bool]] = None,
    decomposition_rows: Iterable[Mapping | ResidualDecompositionRow] = (),
    seam_rows: Iterable[Mapping] = (),
) -> OpsSuccessReport:
    """Spec §11 fields. A drop is a **named finding**; 0-of-2 recovered is allowed.

    Not a CI assert against live ops. Confusion counts parents present in all
    five outcome maps that are in the Spec's 27. ``recovered_of_two`` counts
    only the two, only where a **recovery record** says identity actually moved
    a register — with no recovery map the count is 0 and the payload says the
    map was not supplied, so a zero is never read as a measured zero.
    """
    rows = [
        r.to_json_row() if isinstance(r, ResidualDecompositionRow) else dict(r)
        for r in decomposition_rows
    ]
    seams = [dict(s) for s in seam_rows]
    common = (
        set(d125_accepted)
        & set(d126_accepted)
        & set(d127_accepted)
        & set(d128_accepted)
        & set(d130_accepted)
        & set(KABSCH_RESTITCH_PARENT_IDS)
    )
    n125 = n126 = n127 = n128 = 0
    for pid in sorted(common):
        a130 = bool(d130_accepted[pid])
        if a130:
            continue
        n125 += 1 if bool(d125_accepted[pid]) else 0
        n126 += 1 if bool(d126_accepted[pid]) else 0
        n127 += 1 if bool(d127_accepted[pid]) else 0
        n128 += 1 if bool(d128_accepted[pid]) else 0
    n126_recovered_refused = sum(
        1
        for pid in sorted(D126_RECOVERED_PARENT_IDS & set(d130_accepted))
        if not bool(d130_accepted[pid])
    )

    if d130_recovered is None:
        recovered = 0
        source = "none_supplied"
    else:
        recovered = sum(
            1 for pid in PHASE_4_PAIR_PARENT_IDS if bool(d130_recovered.get(pid, False))
        )
        source = "recovery_records"

    measured = sum(
        1
        for row in rows
        if row.get("rigid_rmsd_angstrom") is not None
        and row.get("rmsd_floor_angstrom") is not None
    )
    placement_over_gate = sum(
        1
        for row in rows
        if row.get("residual_class") == CLASS_PLACEMENT
        and (row.get("rigid_rmsd_angstrom") or 0.0) > RMSD_REFUSE_ANGSTROM
    )
    # §11 counts these **per parent**, so a parent whose several seams all
    # audited is one audit, not three. That needs `parent_job_id` on the seam
    # rows — the writer does not know it, the caller does — so when it is
    # missing the count falls back to per-seam and the payload says which was
    # used rather than presenting one number as if it were the other.
    def _audited(s: Mapping) -> bool:
        return s.get("identity_evidence") not in (None, IDENTITY_NOT_AUDITED_CLASS)

    def _corrected(s: Mapping) -> bool:
        return bool(s.get("register_offset_aa"))

    def _unverifiable(s: Mapping) -> bool:
        return s.get("refuse_reason") == REFUSE_CORRESPONDENCE_UNVERIFIABLE

    per_parent = bool(seams) and all(s.get("parent_job_id") is not None for s in seams)
    if per_parent:
        counts_source = "per_parent"

        def _count(pred) -> int:
            return len({s["parent_job_id"] for s in seams if pred(s)})
    else:
        counts_source = "per_seam_no_parent_id"

        def _count(pred) -> int:
            return sum(1 for s in seams if pred(s))

    audited = _count(_audited)
    corrected = _count(_corrected)
    unverifiable = _count(_unverifiable)
    return OpsSuccessReport(
        n_overlap_pairs_measured=measured,
        n_irreducible=_count_class(rows, CLASS_IRREDUCIBLE),
        n_placement=placement_over_gate,
        n_placement_within_gate=_count_class(rows, CLASS_PLACEMENT) - placement_over_gate,
        n_residual_unknown=_count_class(rows, CLASS_UNKNOWN),
        n_correspondence_audited=audited,
        n_correspondence_corrected=corrected,
        n_correspondence_unverifiable=unverifiable,
        correspondence_counts_source=counts_source,
        recovered_of_two=recovered,
        recovered_of_two_source=source,
        n_d125_pass_d130_refuse=n125,
        n_d126_pass_d130_refuse=n126,
        n_d127_pass_d130_refuse=n127,
        n_d128_pass_d130_refuse=n128,
        n_d126_recovered_d130_refuse=n126_recovered_refused,
    )


# Keep the D-125 inventory guard live so a renamed helper fails at import.
assert require_inventory_parent is not None
assert InventoryRefused is not None
