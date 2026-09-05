"""D-126-A — overlap-confidence Kabsch, then the existing winning_tile assembler.

A rigid pre-stitch transform of already-emitted ESMFold tiles. Weight and trim
change the **fit set**; they do not move the 10.0 Å refuse gate. It does **not**
replace ``core.hold48_stitch.winning_tile``. It does **not** overwrite
``core.hold48_kabsch`` or the D-125 ``kabsch/{id}/`` tree. It does **not**
jointly place a holoprotein. It does **not** enter F-004. Seams are not
scientifically solved.

ZERO third-party imports. Reuses D-125 stdlib SVD; weighted centroids +
weighted covariance live here.

Refuse v1 (amended Spec §2): effective Cα ``< 3``; final weighted RMSD
``> 10.0`` Å; covariance rank ``< 2``. Fail closed + all-or-nothing parent.
"""
from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Optional, Sequence

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
    SINGULAR_EPS,
    AssemblerOverwriteRefused,
    InventoryRefused,
    apply_rigid_transform_pdb,
    kabsch_out_dir,
    overlap_parent_residues,
    paired_overlap_ca,
    require_inventory_parent,
    _add,
    _det3,
    _matmul,
    _matvec,
    _norm,
    _sub,
    _svd3,
    _transpose,
)
from core.hold48_stitch import TileFold, write_stitched, winning_tile

# Amendment 1 pins — named so tests can go red. Not fitted on the 27.
WEIGHT_EPSILON = 1e-3
PLDDT_FLOOR = 50.0
TRIM_FRACTION = 0.10
TRIM_ROUND_CAP = 5

ALGORITHM = "overlap_confidence_kabsch_then_winning_tile"
DECISION = "D-126"

# Primary evaluation inventory (D-126 §3). Not a named-exclusion — CLI still
# runs the 27. ⚠ Not a Fly re-query.
PRIMARY_FIVE_PARENT_IDS = frozenset({2939, 3272, 3368, 3394, 3432})

# Re-export so callers / tests can compare paths without importing D-125 names.
CONFIDENCE_RESTITCH_PARENT_IDS = KABSCH_RESTITCH_PARENT_IDS


class SiblingOverwriteRefused(AssemblerOverwriteRefused):
    """D-126 artifacts would land on assembler or D-125 kabsch/ files."""


@dataclass(frozen=True)
class ConfidenceKabschFit:
    n_ca: int
    n_ca_eff: int
    rmsd_angstrom: Optional[float]
    rmsd_full_overlap_angstrom: Optional[float]
    max_ca_jump_angstrom: Optional[float]
    trim_rounds: int
    refuse_reason: Optional[str]
    rotation: Optional[tuple[tuple[float, float, float], tuple[float, float, float], tuple[float, float, float]]]
    translation: Optional[tuple[float, float, float]]

    @property
    def accepted(self) -> bool:
        return self.refuse_reason is None


@dataclass(frozen=True)
class ConfidenceSeamRecord:
    moving_tile_index: int
    reference_tile_index: int
    overlap_start: int
    overlap_end: int
    n_ca: int
    n_ca_eff: int
    rmsd_angstrom: Optional[float]
    rmsd_full_overlap_angstrom: Optional[float]
    max_ca_jump_angstrom: Optional[float]
    trim_rounds: int
    refuse_reason: Optional[str]
    rotation: Optional[tuple[tuple[float, float, float], ...]]
    translation: Optional[tuple[float, float, float]]

    def to_json_row(self) -> dict:
        return {
            "moving_tile_index": self.moving_tile_index,
            "reference_tile_index": self.reference_tile_index,
            "overlap_start": self.overlap_start,
            "overlap_end": self.overlap_end,
            "n_ca": self.n_ca,
            "n_ca_eff": self.n_ca_eff,
            "rmsd_angstrom": self.rmsd_angstrom,
            "rmsd_full_overlap_angstrom": self.rmsd_full_overlap_angstrom,
            "max_ca_jump_angstrom": self.max_ca_jump_angstrom,
            "trim_rounds": self.trim_rounds,
            "refuse_reason": self.refuse_reason,
            "R": [list(row) for row in self.rotation] if self.rotation is not None else None,
            "t": list(self.translation) if self.translation is not None else None,
        }


@dataclass(frozen=True)
class ConfidenceKabschRestitchResult:
    accepted: bool
    parent_job_id: int
    out_dir: Path
    seams: tuple[ConfidenceSeamRecord, ...]
    tiles: tuple[TileFold, ...]
    stitched: Optional[dict[str, str]]


@dataclass(frozen=True)
class OpsSuccessReport:
    """Confusion vs D-125. Required ops fields; not a CI assert against live ops."""

    n_d125_pass_d126_pass: int
    n_d125_pass_d126_refuse: int
    n_d125_refuse_d126_pass: int
    n_d125_refuse_d126_refuse: int
    recovered_of_primary_five: int

    def to_json(self) -> dict:
        return {
            "n_d125_pass_d126_pass": self.n_d125_pass_d126_pass,
            "n_d125_pass_d126_refuse": self.n_d125_pass_d126_refuse,
            "n_d125_refuse_d126_pass": self.n_d125_refuse_d126_pass,
            "n_d125_refuse_d126_refuse": self.n_d125_refuse_d126_refuse,
            "recovered_of_primary_five": self.recovered_of_primary_five,
            "n_d125_pass_d126_refuse_is_named_finding": self.n_d125_pass_d126_refuse > 0,
            "zero_of_five_recovered_is_allowed": True,
            "d125_algorithm": D125_ALGORITHM,
            "d126_algorithm": ALGORITHM,
            "d125_decision": D125_DECISION,
            "d126_decision": DECISION,
        }


# ── weights + weighted Kabsch ────────────────────────────────────────────────


def plddt_at_parent(tile: TileFold, parent_res: int) -> float:
    """0-based local index: parent_res - start. Same convention as winning_tile."""
    return float(tile.plddt[parent_res - tile.start])


def pair_weight(plddt_a: float, plddt_b: float, *, epsilon: float = WEIGHT_EPSILON) -> float:
    """w_i = min(pLDDT_A, pLDDT_B)/100, clamped ≥ ε (ε = 1e-3)."""
    return max(float(epsilon), min(float(plddt_a), float(plddt_b)) / 100.0)


def _weighted_centroid(
    pts: Sequence[Sequence[float]], weights: Sequence[float]
) -> tuple[float, float, float]:
    wsum = sum(weights)
    if wsum <= 0.0:
        raise ValueError("weighted centroid needs a positive weight sum")
    return (
        sum(w * p[0] for w, p in zip(weights, pts)) / wsum,
        sum(w * p[1] for w, p in zip(weights, pts)) / wsum,
        sum(w * p[2] for w, p in zip(weights, pts)) / wsum,
    )


def weighted_kabsch_rotation_translation(
    moving: Sequence[Sequence[float]],
    reference: Sequence[Sequence[float]],
    weights: Sequence[float],
) -> tuple[
    tuple[tuple[float, float, float], tuple[float, float, float], tuple[float, float, float]],
    tuple[float, float, float],
    float,
    int,
]:
    """Weighted Kabsch: H = Σ w_i (p_i − c_p)(q_i − c_q)ᵀ, SVD, det R = +1.

    Weighted RMSD = sqrt(Σ w_i ||R p_i + t − q_i||² / Σ w_i) on this fit set.
    """
    if len(moving) != len(reference) or len(moving) != len(weights) or not moving:
        raise ValueError("weighted Kabsch needs equally many corresponding points and weights")
    w = [max(WEIGHT_EPSILON, float(wi)) for wi in weights]
    pc = _weighted_centroid(moving, w)
    qc = _weighted_centroid(reference, w)
    P = [_sub(p, pc) for p in moving]
    Q = [_sub(q, qc) for q in reference]
    H = [[0.0] * 3 for _ in range(3)]
    for p, q, wi in zip(P, Q, w):
        for i in range(3):
            for j in range(3):
                H[i][j] += wi * p[i] * q[j]
    U, s, Vt = _svd3(H)
    rank = sum(1 for si in s if si > SINGULAR_EPS)
    V = _transpose(Vt)
    R = _matmul(V, _transpose(U))
    if _det3(R) < 0.0:
        Vt = [list(row) for row in Vt]
        Vt[2] = [-x for x in Vt[2]]
        V = _transpose(Vt)
        R = _matmul(V, _transpose(U))
    R_t = (
        (R[0][0], R[0][1], R[0][2]),
        (R[1][0], R[1][1], R[1][2]),
        (R[2][0], R[2][1], R[2][2]),
    )
    Rpc = _matvec(R, pc)
    t = _sub(qc, Rpc)
    acc = 0.0
    wsum = sum(w)
    for p, q, wi in zip(moving, reference, w):
        d = _sub(_add(_matvec(R, p), t), q)
        acc += wi * (d[0] * d[0] + d[1] * d[1] + d[2] * d[2])
    rmsd = math.sqrt(acc / wsum)
    return R_t, t, rmsd, rank


def weighted_rmsd_after(
    rotation: Sequence[Sequence[float]],
    translation: Sequence[float],
    moving: Sequence[Sequence[float]],
    reference: Sequence[Sequence[float]],
    weights: Sequence[float],
) -> float:
    w = [max(WEIGHT_EPSILON, float(wi)) for wi in weights]
    acc = 0.0
    for p, q, wi in zip(moving, reference, w):
        d = _sub(_add(_matvec(rotation, p), translation), q)
        acc += wi * (d[0] * d[0] + d[1] * d[1] + d[2] * d[2])
    return math.sqrt(acc / sum(w))


def unweighted_rmsd_after(
    rotation: Sequence[Sequence[float]],
    translation: Sequence[float],
    moving: Sequence[Sequence[float]],
    reference: Sequence[Sequence[float]],
) -> float:
    acc = 0.0
    for p, q in zip(moving, reference):
        d = _sub(_add(_matvec(rotation, p), translation), q)
        acc += d[0] * d[0] + d[1] * d[1] + d[2] * d[2]
    return math.sqrt(acc / len(moving))


def max_ca_jump_after(
    rotation: Sequence[Sequence[float]],
    translation: Sequence[float],
    moving: Sequence[Sequence[float]],
    reference: Sequence[Sequence[float]],
) -> float:
    return max(
        _norm(_sub(_add(_matvec(rotation, p), translation), q))
        for p, q in zip(moving, reference)
    )


def residuals_after(
    rotation: Sequence[Sequence[float]],
    translation: Sequence[float],
    moving: Sequence[Sequence[float]],
    reference: Sequence[Sequence[float]],
) -> list[float]:
    return [
        _norm(_sub(_add(_matvec(rotation, p), translation), q))
        for p, q in zip(moving, reference)
    ]


# ── overlap + floor + trim ───────────────────────────────────────────────────


def paired_overlap_ca_with_weights(
    reference: TileFold, moving: TileFold
) -> tuple[
    list[tuple[float, float, float]],
    list[tuple[float, float, float]],
    list[int],
    list[float],
    list[tuple[float, float]],
]:
    moving_pts, ref_pts, used = paired_overlap_ca(reference, moving)
    weights: list[float] = []
    plddt_pairs: list[tuple[float, float]] = []
    for parent_res in used:
        pa = plddt_at_parent(reference, parent_res)
        pb = plddt_at_parent(moving, parent_res)
        plddt_pairs.append((pa, pb))
        weights.append(pair_weight(pa, pb))
    return moving_pts, ref_pts, used, weights, plddt_pairs


def apply_plddt_floor(
    moving: Sequence[Sequence[float]],
    reference: Sequence[Sequence[float]],
    used: Sequence[int],
    weights: Sequence[float],
    plddt_pairs: Sequence[tuple[float, float]],
) -> tuple[
    list[tuple[float, float, float]],
    list[tuple[float, float, float]],
    list[int],
    list[float],
    list[tuple[float, float]],
]:
    """(a) Drop min(pLDDT) < 50 **if** that leaves n ≥ 3; else keep the full set."""
    kept = [i for i, (pa, pb) in enumerate(plddt_pairs) if min(pa, pb) >= PLDDT_FLOOR]
    if len(kept) < OVERLAP_CA_MIN:
        return (
            [tuple(p) for p in moving],
            [tuple(p) for p in reference],
            list(used),
            list(weights),
            list(plddt_pairs),
        )
    return (
        [tuple(moving[i]) for i in kept],
        [tuple(reference[i]) for i in kept],
        [used[i] for i in kept],
        [weights[i] for i in kept],
        [plddt_pairs[i] for i in kept],
    )


def trim_highest_residual(
    moving: Sequence[Sequence[float]],
    reference: Sequence[Sequence[float]],
    used: Sequence[int],
    weights: Sequence[float],
    residuals: Sequence[float],
) -> tuple[
    list[tuple[float, float, float]],
    list[tuple[float, float, float]],
    list[int],
    list[float],
]:
    """Drop the highest-residual 10% of points (minimum 1)."""
    n = len(moving)
    n_drop = max(1, math.ceil(n * TRIM_FRACTION))
    n_drop = min(n_drop, n)
    order = sorted(range(n), key=lambda i: residuals[i], reverse=True)
    drop = set(order[:n_drop])
    keep = [i for i in range(n) if i not in drop]
    return (
        [tuple(moving[i]) for i in keep],
        [tuple(reference[i]) for i in keep],
        [used[i] for i in keep],
        [weights[i] for i in keep],
    )


def _disclosure(
    rotation: Optional[Sequence[Sequence[float]]],
    translation: Optional[Sequence[float]],
    all_moving: Sequence[Sequence[float]],
    all_reference: Sequence[Sequence[float]],
) -> tuple[Optional[float], Optional[float]]:
    if rotation is None or translation is None or not all_moving:
        return None, None
    return (
        unweighted_rmsd_after(rotation, translation, all_moving, all_reference),
        max_ca_jump_after(rotation, translation, all_moving, all_reference),
    )


def fit_overlap_confidence_kabsch(reference: TileFold, moving: TileFold) -> ConfidenceKabschFit:
    """(a) pLDDT floor 50 if n≥3 remains; (b) weighted Kabsch; (c) trim loop.

    Gate is final **weighted** RMSD on the fit set ≤ 10.0 Å. Full-overlap
    unweighted RMSD + max Cα jump are disclosure, not the gate.
    """
    all_m, all_r, all_used, all_w, all_pp = paired_overlap_ca_with_weights(reference, moving)
    n_ca = len(all_m)
    if n_ca < OVERLAP_CA_MIN:
        return ConfidenceKabschFit(
            n_ca=n_ca,
            n_ca_eff=n_ca,
            rmsd_angstrom=None,
            rmsd_full_overlap_angstrom=None,
            max_ca_jump_angstrom=None,
            trim_rounds=0,
            refuse_reason=REFUSE_OVERLAP_CA_LT_3,
            rotation=None,
            translation=None,
        )

    # (a) floor first — drop is skipped only when it would leave n < 3.
    m, r, used, w, _pp = apply_plddt_floor(all_m, all_r, all_used, all_w, all_pp)

    last_R = None
    last_t = None
    last_rmsd: Optional[float] = None
    last_rank = 0
    trim_rounds = 0

    def _refuse(reason: str, n_eff: int, rmsd: Optional[float], R, t) -> ConfidenceKabschFit:
        full_rmsd, jump = _disclosure(R, t, all_m, all_r)
        return ConfidenceKabschFit(
            n_ca=n_ca,
            n_ca_eff=n_eff,
            rmsd_angstrom=rmsd,
            rmsd_full_overlap_angstrom=full_rmsd,
            max_ca_jump_angstrom=jump,
            trim_rounds=trim_rounds,
            refuse_reason=reason,
            rotation=None,
            translation=None,
        )

    # (b) weighted Kabsch
    R, t, rmsd, rank = weighted_kabsch_rotation_translation(m, r, w)
    last_R, last_t, last_rmsd, last_rank = R, t, rmsd, rank
    if rank < COVARIANCE_RANK_MIN:
        return _refuse(REFUSE_SINGULAR_COVARIANCE, len(m), None, None, None)

    # (c) trim loop — while n_eff ≥ 3 and weighted RMSD > 10.0 Å, cap 5.
    while len(m) >= OVERLAP_CA_MIN and rmsd > RMSD_REFUSE_ANGSTROM and trim_rounds < TRIM_ROUND_CAP:
        resids = residuals_after(R, t, m, r)
        m, r, used, w = trim_highest_residual(m, r, used, w, resids)
        trim_rounds += 1
        if len(m) < OVERLAP_CA_MIN:
            return _refuse(REFUSE_OVERLAP_CA_LT_3, len(m), last_rmsd, last_R, last_t)
        prev_R, prev_t = last_R, last_t
        R, t, rmsd, rank = weighted_kabsch_rotation_translation(m, r, w)
        if rank < COVARIANCE_RANK_MIN:
            return _refuse(REFUSE_SINGULAR_COVARIANCE, len(m), None, prev_R, prev_t)
        last_R, last_t, last_rmsd, last_rank = R, t, rmsd, rank

    n_eff = len(m)
    if n_eff < OVERLAP_CA_MIN:
        return _refuse(REFUSE_OVERLAP_CA_LT_3, n_eff, last_rmsd, last_R, last_t)
    if last_rank < COVARIANCE_RANK_MIN:
        return _refuse(REFUSE_SINGULAR_COVARIANCE, n_eff, None, None, None)
    if rmsd > RMSD_REFUSE_ANGSTROM:
        return _refuse(REFUSE_RMSD_GT_10, n_eff, rmsd, last_R, last_t)

    full_rmsd, jump = _disclosure(R, t, all_m, all_r)
    return ConfidenceKabschFit(
        n_ca=n_ca,
        n_ca_eff=n_eff,
        rmsd_angstrom=rmsd,
        rmsd_full_overlap_angstrom=full_rmsd,
        max_ca_jump_angstrom=jump,
        trim_rounds=trim_rounds,
        refuse_reason=None,
        rotation=R,
        translation=t,
    )


def transform_tile(tile: TileFold, fit: ConfidenceKabschFit) -> TileFold:
    if not fit.accepted or fit.rotation is None or fit.translation is None:
        raise ValueError("refuse is fail-closed — do not invent a transformed pose")
    return TileFold(
        start=tile.start,
        end=tile.end,
        pdb=apply_rigid_transform_pdb(tile.pdb, fit.rotation, fit.translation),
        plddt=tile.plddt,
        pae=tile.pae,
    )


def align_tiles(tiles: Sequence[TileFold]) -> tuple[list[TileFold], list[ConfidenceSeamRecord], bool]:
    """N-terminal / earlier tile is the reference; later tiles chain onto the last accepted frame.

    All-or-nothing: the first refuse stops further transforms. ``accepted`` is
    True only when every inbound seam was accepted. Untransformed copies remain
    in the returned list for inspection; they are not written.
    """
    if not tiles:
        raise ValueError("align_tiles needs at least one tile")
    ordered = sorted(tiles, key=lambda t: (t.start, t.end))
    out: list[TileFold] = [ordered[0]]
    seams: list[ConfidenceSeamRecord] = []
    last_accepted = ordered[0]
    last_accepted_index = 1
    all_ok = True
    for i, moving in enumerate(ordered[1:], start=2):
        overlap = overlap_parent_residues(last_accepted, moving)
        fit = fit_overlap_confidence_kabsch(last_accepted, moving)
        rec = ConfidenceSeamRecord(
            moving_tile_index=i,
            reference_tile_index=last_accepted_index,
            overlap_start=overlap[0] if overlap else 0,
            overlap_end=overlap[-1] if overlap else 0,
            n_ca=fit.n_ca,
            n_ca_eff=fit.n_ca_eff,
            rmsd_angstrom=fit.rmsd_angstrom,
            rmsd_full_overlap_angstrom=fit.rmsd_full_overlap_angstrom,
            max_ca_jump_angstrom=fit.max_ca_jump_angstrom,
            trim_rounds=fit.trim_rounds,
            refuse_reason=fit.refuse_reason,
            rotation=fit.rotation,
            translation=fit.translation,
        )
        seams.append(rec)
        if not fit.accepted:
            all_ok = False
            out.append(moving)
            break
        transformed = transform_tile(moving, fit)
        out.append(transformed)
        last_accepted = transformed
        last_accepted_index = i
    if all_ok and len(out) < len(ordered):
        out.extend(ordered[len(out) :])
        all_ok = False
    return out, seams, all_ok


# ── sibling tree + ops report ────────────────────────────────────────────────


def confidence_kabsch_out_dir(out_root: Path | str, parent_job_id: int) -> Path:
    return Path(out_root) / "confidence_kabsch" / str(parent_job_id)


def refuse_sibling_overwrite(
    out_dir: Path,
    assembler_dir: Optional[Path | str] = None,
    d125_dir: Optional[Path | str] = None,
) -> None:
    """Never write D-126 artifacts as if they were assembler or D-125 kabsch/."""
    out = Path(out_dir).resolve()
    if "confidence_kabsch" not in out.parts:
        raise SiblingOverwriteRefused(
            f"D-126 artifacts must land under a confidence_kabsch/ directory, not {out}"
        )
    dest_pdb = (out / "stitched.pdb").resolve()
    if assembler_dir is not None:
        asm = Path(assembler_dir).resolve()
        asm_pdb = (asm / "stitched.pdb").resolve()
        if out == asm or dest_pdb == asm_pdb:
            raise SiblingOverwriteRefused(
                f"refusing to write D-126 artifacts over assembler dir {asm}"
            )
    if d125_dir is not None:
        d125 = Path(d125_dir).resolve()
        d125_pdb = (d125 / "stitched.pdb").resolve()
        if out == d125 or dest_pdb == d125_pdb:
            raise SiblingOverwriteRefused(
                f"refusing to write D-126 artifacts over D-125 kabsch dir {d125}"
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
    seams: Sequence[ConfidenceSeamRecord],
    accepted: bool,
) -> None:
    payload = {
        "algorithm": ALGORITHM,
        "decision": DECISION,
        "parent_job_id": parent_job_id,
        "tile_job_ids": list(tile_job_ids),
        "windows": [list(w) for w in windows],
        "accepted": accepted,
        "seams": [s.to_json_row() for s in seams],
        "weight_epsilon": WEIGHT_EPSILON,
        "plddt_floor": PLDDT_FLOOR,
        "trim_fraction": TRIM_FRACTION,
        "trim_round_cap": TRIM_ROUND_CAP,
        "rmsd_refuse_angstrom": RMSD_REFUSE_ANGSTROM,
    }
    (out / "provenance.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    with (out / "seams.jsonl").open("w", encoding="utf-8") as fh:
        for seam in seams:
            fh.write(json.dumps(seam.to_json_row()) + "\n")


def write_confidence_kabsch_restitch(
    tiles: Sequence[TileFold],
    length: int,
    out_root: Path | str,
    *,
    parent_job_id: int,
    tile_job_ids: Sequence[int] = (),
    assembler_dir: Optional[Path | str] = None,
    d125_dir: Optional[Path | str] = None,
) -> ConfidenceKabschRestitchResult:
    """Align tiles with overlap-confidence Kabsch, then existing write_stitched on accept only.

    ``winning_tile`` is imported so the stitch path stays the assembler (A/B
    compare). A refuse is a recorded outcome, not invented coordinates.
    All-or-nothing: success artifacts are written only if every seam accepted.
    """
    require_inventory_parent(parent_job_id)
    out = confidence_kabsch_out_dir(out_root, parent_job_id)
    if d125_dir is None:
        d125_dir = kabsch_out_dir(out_root, parent_job_id)
    refuse_sibling_overwrite(out, assembler_dir, d125_dir)
    if winning_tile is None:  # pragma: no cover — import pin
        raise RuntimeError("winning_tile must remain importable")

    aligned, seams, accepted = align_tiles(tiles)
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

    return ConfidenceKabschRestitchResult(
        accepted=accepted,
        parent_job_id=parent_job_id,
        out_dir=out,
        seams=tuple(seams),
        tiles=tuple(aligned),
        stitched=stitched,
    )


def build_ops_success_report(
    d125_accepted: Mapping[int, bool],
    d126_accepted: Mapping[int, bool],
) -> OpsSuccessReport:
    """Confusion vs D-125. A drop on the 22 is a named finding. 0-of-5 is allowed.

    Not a CI assert against live ops. Counts parents present in **both** maps
    that are in the Spec's 27. ``recovered_of_primary_five`` counts primary-five
    ids that D-126 accepted (0 is a valid experimental result).
    """
    common = (
        set(d125_accepted)
        & set(d126_accepted)
        & set(KABSCH_RESTITCH_PARENT_IDS)
    )
    n_pp = n_pr = n_rp = n_rr = 0
    for pid in sorted(common):
        a125 = bool(d125_accepted[pid])
        a126 = bool(d126_accepted[pid])
        if a125 and a126:
            n_pp += 1
        elif a125 and not a126:
            n_pr += 1
        elif (not a125) and a126:
            n_rp += 1
        else:
            n_rr += 1
    recovered = sum(
        1
        for pid in PRIMARY_FIVE_PARENT_IDS
        if bool(d126_accepted.get(pid, False))
    )
    return OpsSuccessReport(
        n_d125_pass_d126_pass=n_pp,
        n_d125_pass_d126_refuse=n_pr,
        n_d125_refuse_d126_pass=n_rp,
        n_d125_refuse_d126_refuse=n_rr,
        recovered_of_primary_five=recovered,
    )
