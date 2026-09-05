"""D-125-A — Kabsch on overlap Cα, then the existing winning_tile assembler.

A rigid pre-stitch transform of already-emitted ESMFold tiles. It does **not**
replace ``core.hold48_stitch.winning_tile``. It does **not** jointly place a
holoprotein. It does **not** enter F-004. Seams are not scientifically solved.

ZERO third-party imports. ``numpy`` is in no serving-tier lock (D-058 / D-060);
``core/`` ships in the image. 3×3 SVD is Jacobi + reconstruction.

Refuse v1 defaults (Spec §2): overlap Cα ``< 3``; RMSD ``> 10.0`` Å;
covariance rank ``< 2``. Fail closed: a refuse writes the seam record and
does not write ``tileN_transformed.pdb`` or a Kabsch-path ``stitched.pdb``.
"""
from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Sequence

from core.features import parse_pdb
from core.hold48_stitch import TileFold, write_stitched, winning_tile

# Spec §2 — named so tests can go red. Not fitted on the 27.
OVERLAP_CA_MIN = 3
RMSD_REFUSE_ANGSTROM = 10.0
COVARIANCE_RANK_MIN = 2
SINGULAR_EPS = 1e-8

REFUSE_OVERLAP_CA_LT_3 = "overlap_ca_lt_3"
REFUSE_RMSD_GT_10 = "rmsd_gt_10"
REFUSE_SINGULAR_COVARIANCE = "singular_covariance"
REFUSE_REASONS = frozenset(
    {REFUSE_OVERLAP_CA_LT_3, REFUSE_RMSD_GT_10, REFUSE_SINGULAR_COVARIANCE}
)

ALGORITHM = "kabsch_ca_then_winning_tile"
DECISION = "D-125"

# Same closed-out 27 as D-117 / D-118 / D-120 / WAVE1_WAVE2_STITCHED_PARENT_IDS.
# ⚠ Not a Fly re-query. IGF2R parent 3356 is deliberately absent.
KABSCH_RESTITCH_PARENT_IDS = frozenset(
    {
        2817,
        2917,
        2929,
        2938,
        2939,
        3027,
        3097,
        3153,
        3179,
        3188,
        3190,
        3217,
        3272,
        3320,
        3321,
        3368,
        3379,
        3394,
        3404,
        3432,
        3454,
        3469,
        3516,
        3541,
        3566,
        3569,
        3575,
    }
)


class InventoryRefused(ValueError):
    """CLI / writer pointed at a parent id that is not the Spec's 27."""


class AssemblerOverwriteRefused(ValueError):
    """Kabsch output would land on (or as) an assembler PDB directory."""


@dataclass(frozen=True)
class KabschFit:
    n_ca: int
    rmsd_angstrom: Optional[float]
    refuse_reason: Optional[str]
    rotation: Optional[tuple[tuple[float, float, float], tuple[float, float, float], tuple[float, float, float]]]
    translation: Optional[tuple[float, float, float]]

    @property
    def accepted(self) -> bool:
        return self.refuse_reason is None


@dataclass(frozen=True)
class SeamRecord:
    moving_tile_index: int  # 1-based, Spec tile{n}
    reference_tile_index: int
    overlap_start: int
    overlap_end: int
    n_ca: int
    rmsd_angstrom: Optional[float]
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
            "rmsd_angstrom": self.rmsd_angstrom,
            "refuse_reason": self.refuse_reason,
            "R": [list(row) for row in self.rotation] if self.rotation is not None else None,
            "t": list(self.translation) if self.translation is not None else None,
        }


@dataclass(frozen=True)
class KabschRestitchResult:
    accepted: bool
    parent_job_id: int
    out_dir: Path
    seams: tuple[SeamRecord, ...]
    tiles: tuple[TileFold, ...]
    stitched: Optional[dict[str, str]]


# ── 3×3 linear algebra (stdlib) ──────────────────────────────────────────────


def _transpose(A: Sequence[Sequence[float]]) -> list[list[float]]:
    return [[A[j][i] for j in range(3)] for i in range(3)]


def _matmul(A: Sequence[Sequence[float]], B: Sequence[Sequence[float]]) -> list[list[float]]:
    return [
        [sum(A[i][k] * B[k][j] for k in range(3)) for j in range(3)]
        for i in range(3)
    ]


def _matvec(A: Sequence[Sequence[float]], v: Sequence[float]) -> tuple[float, float, float]:
    return (
        A[0][0] * v[0] + A[0][1] * v[1] + A[0][2] * v[2],
        A[1][0] * v[0] + A[1][1] * v[1] + A[1][2] * v[2],
        A[2][0] * v[0] + A[2][1] * v[1] + A[2][2] * v[2],
    )


def _det3(A: Sequence[Sequence[float]]) -> float:
    return (
        A[0][0] * (A[1][1] * A[2][2] - A[1][2] * A[2][1])
        - A[0][1] * (A[1][0] * A[2][2] - A[1][2] * A[2][0])
        + A[0][2] * (A[1][0] * A[2][1] - A[1][1] * A[2][0])
    )


def _cross(a: Sequence[float], b: Sequence[float]) -> tuple[float, float, float]:
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def _norm(v: Sequence[float]) -> float:
    return math.sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2])


def _jacobi_symmetric(A: Sequence[Sequence[float]], *, max_sweeps: int = 64) -> tuple[list[float], list[list[float]]]:
    """Eigen-decomposition of a 3×3 symmetric matrix. V's columns are eigenvectors."""
    S = [list(row) for row in A]
    V = [[1.0 if i == j else 0.0 for j in range(3)] for i in range(3)]
    for _ in range(max_sweeps):
        p, q = 0, 1
        max_off = abs(S[0][1])
        for i, j in ((0, 2), (1, 2)):
            if abs(S[i][j]) > max_off:
                max_off = abs(S[i][j])
                p, q = i, j
        if max_off < 1e-15:
            break
        app, aqq, apq = S[p][p], S[q][q], S[p][q]
        if abs(apq) < 1e-18:
            break
        tau = (aqq - app) / (2.0 * apq)
        t = math.copysign(1.0, tau) / (abs(tau) + math.sqrt(1.0 + tau * tau))
        c = 1.0 / math.sqrt(1.0 + t * t)
        s = t * c
        for k in range(3):
            if k == p or k == q:
                continue
            spk, sqk = S[p][k], S[q][k]
            S[p][k] = S[k][p] = c * spk - s * sqk
            S[q][k] = S[k][q] = s * spk + c * sqk
        S[p][p] = c * c * app - 2.0 * s * c * apq + s * s * aqq
        S[q][q] = s * s * app + 2.0 * s * c * apq + c * c * aqq
        S[p][q] = S[q][p] = 0.0
        for k in range(3):
            vip, viq = V[k][p], V[k][q]
            V[k][p] = c * vip - s * viq
            V[k][q] = s * vip + c * viq
    return [S[0][0], S[1][1], S[2][2]], V


def _col(M: Sequence[Sequence[float]], j: int) -> tuple[float, float, float]:
    return (M[0][j], M[1][j], M[2][j])


def _set_col(M: list[list[float]], j: int, v: Sequence[float]) -> None:
    for i in range(3):
        M[i][j] = float(v[i])


def _complete_orthonormal(U: list[list[float]], s: Sequence[float]) -> list[list[float]]:
    """Fill missing left-singular vectors so U is a proper rotation basis when possible."""
    set_cols = [j for j in range(3) if s[j] > SINGULAR_EPS and _norm(_col(U, j)) > 0.5]
    if len(set_cols) == 3:
        return U
    if len(set_cols) == 0:
        return [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]
    if len(set_cols) == 1:
        j = set_cols[0]
        u = _col(U, j)
        axis = (1.0, 0.0, 0.0) if abs(u[0]) < 0.9 else (0.0, 1.0, 0.0)
        v = _cross(u, axis)
        n = _norm(v)
        if n < 1e-12:
            v = _cross(u, (0.0, 0.0, 1.0))
            n = _norm(v)
        v = (v[0] / n, v[1] / n, v[2] / n)
        w = _cross(u, v)
        missing = [k for k in range(3) if k not in set_cols]
        _set_col(U, missing[0], v)
        _set_col(U, missing[1], w)
        return U
    # two columns known — third is the cross product (right-handed)
    j0, j1 = set_cols
    missing = next(k for k in range(3) if k not in set_cols)
    w = _cross(_col(U, j0), _col(U, j1))
    n = _norm(w)
    if n < 1e-12:
        w = (0.0, 0.0, 1.0)
        n = 1.0
    # permutation parity: (j0, j1, missing) should match even/odd of (0,1,2)
    even = (j0, j1, missing) in {(0, 1, 2), (1, 2, 0), (2, 0, 1)}
    if not even:
        w = (-w[0], -w[1], -w[2])
    _set_col(U, missing, (w[0] / n, w[1] / n, w[2] / n))
    return U


def _svd3(H: Sequence[Sequence[float]]) -> tuple[list[list[float]], list[float], list[list[float]]]:
    """Thin 3×3 SVD: H = U @ diag(s) @ Vt, singular values descending."""
    Ht = _transpose(H)
    HtH = _matmul(Ht, H)
    w, V = _jacobi_symmetric(HtH)
    order = sorted(range(3), key=lambda i: w[i], reverse=True)
    w = [w[i] for i in order]
    V = [[V[r][c] for c in order] for r in range(3)]
    s = [math.sqrt(max(wi, 0.0)) for wi in w]
    U = [[0.0] * 3 for _ in range(3)]
    for j in range(3):
        if s[j] > SINGULAR_EPS:
            uj = _matvec(H, _col(V, j))
            _set_col(U, j, (uj[0] / s[j], uj[1] / s[j], uj[2] / s[j]))
    U = _complete_orthonormal(U, s)
    return U, s, _transpose(V)


def _centroid(pts: Sequence[Sequence[float]]) -> tuple[float, float, float]:
    n = len(pts)
    return (
        sum(p[0] for p in pts) / n,
        sum(p[1] for p in pts) / n,
        sum(p[2] for p in pts) / n,
    )


def _sub(a: Sequence[float], b: Sequence[float]) -> tuple[float, float, float]:
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def _add(a: Sequence[float], b: Sequence[float]) -> tuple[float, float, float]:
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def kabsch_rotation_translation(
    moving: Sequence[Sequence[float]],
    reference: Sequence[Sequence[float]],
) -> tuple[
    tuple[tuple[float, float, float], tuple[float, float, float], tuple[float, float, float]],
    tuple[float, float, float],
    float,
    int,
]:
    """Kabsch: H = Pᵀ Q, SVD, det R = +1. Returns (R, t, rmsd, rank).

    Transform is ``R @ p + t``. ``rank`` is the number of singular values of H
    above ``SINGULAR_EPS``.
    """
    if len(moving) != len(reference) or not moving:
        raise ValueError("Kabsch needs equally many corresponding points")
    pc = _centroid(moving)
    qc = _centroid(reference)
    P = [_sub(p, pc) for p in moving]
    Q = [_sub(q, qc) for q in reference]
    H = [[0.0] * 3 for _ in range(3)]
    for p, q in zip(P, Q):
        for i in range(3):
            for j in range(3):
                H[i][j] += p[i] * q[j]
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
    for p, q in zip(moving, reference):
        d = _sub(_add(_matvec(R, p), t), q)
        acc += d[0] * d[0] + d[1] * d[1] + d[2] * d[2]
    rmsd = math.sqrt(acc / len(moving))
    return R_t, t, rmsd, rank


# ── overlap Cα + tile transform ──────────────────────────────────────────────


def overlap_parent_residues(a: TileFold, b: TileFold) -> list[int]:
    lo = max(a.start, b.start)
    hi = min(a.end, b.end)
    if lo > hi:
        return []
    return list(range(lo, hi + 1))


def ca_xyz_at_parent(tile: TileFold, parent_res: int) -> Optional[tuple[float, float, float]]:
    """ESMFold local numbering: local = parent_res - start + 1."""
    local = parent_res - tile.start + 1
    for atom in parse_pdb(tile.pdb):
        if atom.is_ca and atom.res_seq == local:
            return (atom.x, atom.y, atom.z)
    return None


def paired_overlap_ca(
    reference: TileFold, moving: TileFold
) -> tuple[list[tuple[float, float, float]], list[tuple[float, float, float]], list[int]]:
    """Corresponding overlap Cα. Missing Cα on either side is dropped (counts against n_ca)."""
    moving_pts: list[tuple[float, float, float]] = []
    ref_pts: list[tuple[float, float, float]] = []
    used: list[int] = []
    for parent_res in overlap_parent_residues(reference, moving):
        p = ca_xyz_at_parent(moving, parent_res)
        q = ca_xyz_at_parent(reference, parent_res)
        if p is None or q is None:
            continue
        moving_pts.append(p)
        ref_pts.append(q)
        used.append(parent_res)
    return moving_pts, ref_pts, used


def fit_overlap_kabsch(reference: TileFold, moving: TileFold) -> KabschFit:
    moving_pts, ref_pts, _used = paired_overlap_ca(reference, moving)
    n = len(moving_pts)
    if n < OVERLAP_CA_MIN:
        return KabschFit(
            n_ca=n,
            rmsd_angstrom=None,
            refuse_reason=REFUSE_OVERLAP_CA_LT_3,
            rotation=None,
            translation=None,
        )
    R, t, rmsd, rank = kabsch_rotation_translation(moving_pts, ref_pts)
    if rank < COVARIANCE_RANK_MIN:
        return KabschFit(
            n_ca=n,
            rmsd_angstrom=None,
            refuse_reason=REFUSE_SINGULAR_COVARIANCE,
            rotation=None,
            translation=None,
        )
    if rmsd > RMSD_REFUSE_ANGSTROM:
        return KabschFit(
            n_ca=n,
            rmsd_angstrom=rmsd,
            refuse_reason=REFUSE_RMSD_GT_10,
            rotation=None,
            translation=None,
        )
    return KabschFit(
        n_ca=n,
        rmsd_angstrom=rmsd,
        refuse_reason=None,
        rotation=R,
        translation=t,
    )


def apply_rigid_transform_pdb(
    pdb: str,
    rotation: Sequence[Sequence[float]],
    translation: Sequence[float],
) -> str:
    """Apply R, t to every ATOM/HETATM. No atom is invented."""
    lines: list[str] = []
    ended_nl = pdb.endswith("\n")
    for line in pdb.splitlines():
        if (line.startswith("ATOM") or line.startswith("HETATM")) and len(line) >= 54:
            try:
                x = float(line[30:38])
                y = float(line[38:46])
                z = float(line[46:54])
            except ValueError:
                lines.append(line)
                continue
            nx, ny, nz = _add(_matvec(rotation, (x, y, z)), translation)
            line = f"{line[:30]}{nx:8.3f}{ny:8.3f}{nz:8.3f}{line[54:]}"
        lines.append(line)
    text = "\n".join(lines)
    return text + ("\n" if ended_nl or text else "")


def transform_tile(tile: TileFold, fit: KabschFit) -> TileFold:
    if not fit.accepted or fit.rotation is None or fit.translation is None:
        raise ValueError("refuse is fail-closed — do not invent a transformed pose")
    return TileFold(
        start=tile.start,
        end=tile.end,
        pdb=apply_rigid_transform_pdb(tile.pdb, fit.rotation, fit.translation),
        plddt=tile.plddt,
        pae=tile.pae,
    )


def align_tiles(tiles: Sequence[TileFold]) -> tuple[list[TileFold], list[SeamRecord], bool]:
    """N-terminal / earlier tile is the reference; later tiles chain onto the last accepted frame.

    Fail closed: the first refuse stops further transforms. ``accepted`` is True
    only when every inbound seam was accepted. Untransformed copies remain in
    the returned list so a caller can still inspect them; they are not written.
    """
    if not tiles:
        raise ValueError("align_tiles needs at least one tile")
    ordered = sorted(tiles, key=lambda t: (t.start, t.end))
    out: list[TileFold] = [ordered[0]]
    seams: list[SeamRecord] = []
    last_accepted = ordered[0]
    last_accepted_index = 1
    all_ok = True
    for i, moving in enumerate(ordered[1:], start=2):
        overlap = overlap_parent_residues(last_accepted, moving)
        fit = fit_overlap_kabsch(last_accepted, moving)
        rec = SeamRecord(
            moving_tile_index=i,
            reference_tile_index=last_accepted_index,
            overlap_start=overlap[0] if overlap else 0,
            overlap_end=overlap[-1] if overlap else 0,
            n_ca=fit.n_ca,
            rmsd_angstrom=fit.rmsd_angstrom,
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


def require_inventory_parent(parent_job_id: int) -> None:
    if parent_job_id not in KABSCH_RESTITCH_PARENT_IDS:
        raise InventoryRefused(
            f"parent_job_id {parent_job_id} is not in the D-125 27-id inventory "
            f"(not a Fly re-query; IGF2R 3356 is out of class here)"
        )


def kabsch_out_dir(out_root: Path | str, parent_job_id: int) -> Path:
    return Path(out_root) / "kabsch" / str(parent_job_id)


def refuse_assembler_overwrite(out_dir: Path, assembler_dir: Optional[Path | str]) -> None:
    """Never write Kabsch artifacts as if they were the assembler tree."""
    out = Path(out_dir).resolve()
    if "kabsch" not in out.parts:
        raise AssemblerOverwriteRefused(
            f"Kabsch artifacts must land under a kabsch/ directory, not {out}"
        )
    if assembler_dir is None:
        return
    asm = Path(assembler_dir).resolve()
    dest_pdb = (out / "stitched.pdb").resolve()
    asm_pdb = (asm / "stitched.pdb").resolve()
    if out == asm or dest_pdb == asm_pdb:
        raise AssemblerOverwriteRefused(
            f"refusing to write Kabsch artifacts over assembler dir {asm}"
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
    seams: Sequence[SeamRecord],
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
    }
    (out / "provenance.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    with (out / "seams.jsonl").open("w", encoding="utf-8") as fh:
        for seam in seams:
            fh.write(json.dumps(seam.to_json_row()) + "\n")


def write_kabsch_restitch(
    tiles: Sequence[TileFold],
    length: int,
    out_root: Path | str,
    *,
    parent_job_id: int,
    tile_job_ids: Sequence[int] = (),
    assembler_dir: Optional[Path | str] = None,
) -> KabschRestitchResult:
    """Align tiles, then call existing ``write_stitched`` on accept only.

    ``winning_tile`` is imported so the stitch path stays the assembler (A/B
    compare). A refuse is a recorded outcome, not invented coordinates.
    """
    require_inventory_parent(parent_job_id)
    out = kabsch_out_dir(out_root, parent_job_id)
    refuse_assembler_overwrite(out, assembler_dir)
    # Touch winning_tile so a deleted assembler import fails this module, not later.
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

    return KabschRestitchResult(
        accepted=accepted,
        parent_job_id=parent_job_id,
        out_dir=out,
        seams=tuple(seams),
        tiles=tuple(aligned),
        stitched=stitched,
    )
