"""D-127-A — piecewise / domain-aware Kabsch, then the existing winning_tile assembler.

A multi-rigid pre-stitch transform of already-emitted ESMFold tiles. One
weighted R, t per UniProt Domain/Repeat interval that intersects the
overlap. Weight changes the **fit set of each piece**. It does **not**
move the 10.0 Å refuse gate. **No trim loop** (D-126 lie surface). It
does **not** replace ``core.hold48_stitch.winning_tile``. It does **not**
overwrite ``core.hold48_kabsch`` / ``kabsch/{id}/`` or
``core.hold48_confidence_kabsch`` / ``confidence_kabsch/{id}/``. It does
**not** jointly place a holoprotein. It does **not** enter F-004. Seams
are not scientifically solved.

ZERO third-party imports. Reuses D-125 stdlib SVD + D-126 weighted
centroids / weighted covariance. One weighted Kabsch per piece.

Refuse v1 (Spec §2): piece Cα ``< 3``; piece weighted RMSD ``> 10.0`` Å;
covariance rank ``< 2``; ``no_domain_pieces``; ``linker_jump_gt_10``.
Fail closed + all-or-nothing parent.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Optional, Sequence

from core.hold48 import UNIPROT_CACHE, domain_ends_span_relative
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
    apply_rigid_transform_pdb,
    ca_xyz_at_parent,
    kabsch_out_dir,
    overlap_parent_residues,
    paired_overlap_ca,
    require_inventory_parent,
)
from core.hold48_stitch import TileFold, write_stitched, winning_tile

# Same emit feature types as core.hold48.domain_ends_span_relative.
DOMAIN_FEATURE_TYPES = ("Domain", "Repeat")

ALGORITHM = "piecewise_domain_kabsch_then_winning_tile"
DECISION = "D-127"

REFUSE_NO_DOMAIN_PIECES = "no_domain_pieces"
REFUSE_LINKER_JUMP_GT_10 = "linker_jump_gt_10"
REFUSE_REASONS = frozenset(
    {
        REFUSE_OVERLAP_CA_LT_3,
        REFUSE_RMSD_GT_10,
        REFUSE_SINGULAR_COVARIANCE,
        REFUSE_NO_DOMAIN_PIECES,
        REFUSE_LINKER_JUMP_GT_10,
    }
)

# Primary evaluation inventory (D-127 §3). Not a named-exclusion — CLI still
# runs the 27. ⚠ Not a Fly re-query.
PRIMARY_THREE_PARENT_IDS = frozenset({2939, 3272, 3432})

# Re-export so callers / tests can compare paths without importing D-125 names.
PIECEWISE_RESTITCH_PARENT_IDS = KABSCH_RESTITCH_PARENT_IDS

# Touch the emit-source name so a renamed domain_ends_span_relative fails import.
# The interval reader below is the same cache / feature-type / span contract.
assert domain_ends_span_relative is not None


class SiblingOverwriteRefused(AssemblerOverwriteRefused):
    """D-127 artifacts would land on assembler, D-125 kabsch/, or D-126 confidence_kabsch/."""


Rotation = tuple[tuple[float, float, float], tuple[float, float, float], tuple[float, float, float]]
Translation = tuple[float, float, float]


@dataclass(frozen=True)
class DomainInterval:
    """Span-relative inclusive interval from one UniProt Domain/Repeat feature."""

    start: int
    end: int
    feature_type: str = "Domain"

    def intersects(self, lo: int, hi: int) -> bool:
        return self.start <= hi and self.end >= lo

    def as_tuple(self) -> tuple[int, int]:
        return (self.start, self.end)


@dataclass(frozen=True)
class PieceFit:
    interval: tuple[int, int]
    n_ca: int
    rmsd_angstrom: Optional[float]
    refuse_reason: Optional[str]
    rotation: Optional[Rotation]
    translation: Optional[Translation]

    @property
    def accepted(self) -> bool:
        return self.refuse_reason is None and self.rotation is not None

    def to_json(self) -> dict:
        return {
            "interval": list(self.interval),
            "n_ca": self.n_ca,
            "rmsd_angstrom": self.rmsd_angstrom,
            "refuse_reason": self.refuse_reason,
            "R": [list(row) for row in self.rotation] if self.rotation is not None else None,
            "t": list(self.translation) if self.translation is not None else None,
        }


@dataclass(frozen=True)
class PiecewiseSeamRecord:
    moving_tile_index: int
    reference_tile_index: int
    overlap_start: int
    overlap_end: int
    pieces: tuple[PieceFit, ...]
    linker_n: Optional[int]
    max_linker_ca_jump: Optional[float]
    rmsd_full_overlap_angstrom: Optional[float]
    max_ca_jump_angstrom: Optional[float]
    refuse_reason: Optional[str]

    def to_json_row(self) -> dict:
        return {
            "moving_tile_index": self.moving_tile_index,
            "reference_tile_index": self.reference_tile_index,
            "overlap_start": self.overlap_start,
            "overlap_end": self.overlap_end,
            "pieces": [p.to_json() for p in self.pieces],
            "linker_n": self.linker_n,
            "max_linker_ca_jump": self.max_linker_ca_jump,
            "rmsd_full_overlap_angstrom": self.rmsd_full_overlap_angstrom,
            "max_ca_jump_angstrom": self.max_ca_jump_angstrom,
            "refuse_reason": self.refuse_reason,
        }


@dataclass(frozen=True)
class PiecewiseKabschRestitchResult:
    accepted: bool
    parent_job_id: int
    out_dir: Path
    seams: tuple[PiecewiseSeamRecord, ...]
    tiles: tuple[TileFold, ...]
    stitched: Optional[dict[str, str]]


@dataclass(frozen=True)
class OpsSuccessReport:
    """Confusion vs D-125 and vs D-126. Required ops fields; not a CI assert."""

    n_d125_pass_d127_pass: int
    n_d125_pass_d127_refuse: int
    n_d126_pass_d127_pass: int
    n_d126_pass_d127_refuse: int
    n_d126_refuse_d127_pass: int
    n_d126_refuse_d127_refuse: int
    recovered_of_primary_three: int

    def to_json(self) -> dict:
        return {
            "n_d125_pass_d127_pass": self.n_d125_pass_d127_pass,
            "n_d125_pass_d127_refuse": self.n_d125_pass_d127_refuse,
            "n_d126_pass_d127_pass": self.n_d126_pass_d127_pass,
            "n_d126_pass_d127_refuse": self.n_d126_pass_d127_refuse,
            "n_d126_refuse_d127_pass": self.n_d126_refuse_d127_pass,
            "n_d126_refuse_d127_refuse": self.n_d126_refuse_d127_refuse,
            "recovered_of_primary_three": self.recovered_of_primary_three,
            "n_d125_pass_d127_refuse_is_named_finding": self.n_d125_pass_d127_refuse > 0,
            "n_d126_pass_d127_refuse_is_named_finding": self.n_d126_pass_d127_refuse > 0,
            "zero_of_three_recovered_is_allowed": True,
            "d125_algorithm": D125_ALGORITHM,
            "d126_algorithm": D126_ALGORITHM,
            "d127_algorithm": ALGORITHM,
            "d125_decision": D125_DECISION,
            "d126_decision": D126_DECISION,
            "d127_decision": DECISION,
        }


# ── same domain-snap source (intervals, not a second annotation) ─────────────


def domain_intervals_span_relative(
    *,
    accession: str,
    span_start: int,
    span_end: int,
    cache_dir: Path = UNIPROT_CACHE,
) -> tuple[DomainInterval, ...]:
    """UniProt ``Domain``/``Repeat`` intervals mapped onto the folded span (1-based).

    Same cache file, feature types, and missing-cache category as
    ``core.hold48.domain_ends_span_relative``. Emit snap uses those features'
    **ends**; piecewise uses the same features' **span-relative intervals**.
    A missing cache is empty intervals, not a fetch.
    """
    path = Path(cache_dir) / f"{accession}.json"
    if not path.is_file():
        return ()
    doc = json.loads(path.read_text(encoding="utf-8"))
    out: list[DomainInterval] = []
    seen: set[tuple[int, int, str]] = set()
    for feat in doc.get("features") or []:
        ftype = feat.get("type")
        if ftype not in DOMAIN_FEATURE_TYPES:
            continue
        loc = feat.get("location") or {}
        start_node = loc.get("start") or {}
        end_node = loc.get("end") or {}
        start_val = start_node.get("value")
        end_val = end_node.get("value")
        if start_val is None or end_val is None:
            continue
        if start_node.get("modifier") == "UNKNOWN" or end_node.get("modifier") == "UNKNOWN":
            continue
        chain_start = int(start_val)
        chain_end = int(end_val)
        if chain_end < span_start or chain_start > span_end:
            continue
        rel_start = max(1, chain_start - span_start + 1)
        rel_end = min(span_end - span_start + 1, chain_end - span_start + 1)
        if rel_end < rel_start:
            continue
        key = (rel_start, rel_end, str(ftype))
        if key in seen:
            continue
        seen.add(key)
        out.append(DomainInterval(start=rel_start, end=rel_end, feature_type=str(ftype)))
    return tuple(sorted(out, key=lambda d: (d.start, d.end, d.feature_type)))


def intervals_from_pairs(pairs: Sequence[Sequence[int]]) -> tuple[DomainInterval, ...]:
    out: list[DomainInterval] = []
    for pair in pairs:
        start, end = int(pair[0]), int(pair[1])
        if end < start:
            raise ValueError(f"domain interval end < start: {pair}")
        out.append(DomainInterval(start=start, end=end))
    return tuple(sorted(out, key=lambda d: (d.start, d.end)))


def resolve_domain_intervals(
    *,
    domain_intervals: Optional[Sequence[Sequence[int]]] = None,
    accession: Optional[str] = None,
    span_start: Optional[int] = None,
    span_end: Optional[int] = None,
    cache_dir: Path = UNIPROT_CACHE,
) -> tuple[DomainInterval, ...]:
    """Prefer an explicit interval list (hermetic tests); else the emit cache."""
    if domain_intervals is not None:
        return intervals_from_pairs(domain_intervals)
    if accession is None or span_start is None or span_end is None:
        return ()
    return domain_intervals_span_relative(
        accession=accession,
        span_start=int(span_start),
        span_end=int(span_end),
        cache_dir=cache_dir,
    )


# ── per-piece weighted Kabsch (NO trim) ──────────────────────────────────────


def piece_overlap_ca(
    reference: TileFold,
    moving: TileFold,
    interval: DomainInterval | tuple[int, int],
) -> tuple[
    list[tuple[float, float, float]],
    list[tuple[float, float, float]],
    list[int],
    list[float],
]:
    """Corresponding overlap Cα whose parent residue sits in this domain interval."""
    start, end = (interval.start, interval.end) if isinstance(interval, DomainInterval) else (interval[0], interval[1])
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
            pa = plddt_at_parent(reference, parent_res)
            pb = plddt_at_parent(moving, parent_res)
            weights.append(pair_weight(pa, pb))
    return m, r, kept, weights


def fit_domain_piece(
    reference: TileFold,
    moving: TileFold,
    interval: DomainInterval | tuple[int, int],
) -> PieceFit:
    """One weighted Kabsch on this piece's overlap Cα. No trim. No floor-then-trim."""
    bounds = interval.as_tuple() if isinstance(interval, DomainInterval) else (int(interval[0]), int(interval[1]))
    moving_pts, ref_pts, _used, weights = piece_overlap_ca(reference, moving, interval)
    n = len(moving_pts)
    if n < OVERLAP_CA_MIN:
        return PieceFit(
            interval=bounds,
            n_ca=n,
            rmsd_angstrom=None,
            refuse_reason=REFUSE_OVERLAP_CA_LT_3,
            rotation=None,
            translation=None,
        )
    R, t, rmsd, rank = weighted_kabsch_rotation_translation(moving_pts, ref_pts, weights)
    if rank < COVARIANCE_RANK_MIN:
        return PieceFit(
            interval=bounds,
            n_ca=n,
            rmsd_angstrom=None,
            refuse_reason=REFUSE_SINGULAR_COVARIANCE,
            rotation=None,
            translation=None,
        )
    if rmsd > RMSD_REFUSE_ANGSTROM:
        return PieceFit(
            interval=bounds,
            n_ca=n,
            rmsd_angstrom=rmsd,
            refuse_reason=REFUSE_RMSD_GT_10,
            rotation=None,
            translation=None,
        )
    return PieceFit(
        interval=bounds,
        n_ca=n,
        rmsd_angstrom=rmsd,
        refuse_reason=None,
        rotation=R,
        translation=t,
    )


def candidates_intersecting_overlap(
    domains: Sequence[DomainInterval],
    overlap: Sequence[int],
) -> tuple[DomainInterval, ...]:
    if not overlap:
        return ()
    lo, hi = overlap[0], overlap[-1]
    return tuple(d for d in domains if d.intersects(lo, hi))


def inherit_piece_for_residue(parent_res: int, accepted: Sequence[PieceFit]) -> PieceFit:
    """Nearest N-terminal accepted piece; else the N-terminal-most accepted piece."""
    if not accepted:
        raise ValueError("linker inherit needs at least one accepted piece")
    containing = [p for p in accepted if p.interval[0] <= parent_res <= p.interval[1]]
    if containing:
        return min(containing, key=lambda p: (p.interval[0], p.interval[1]))
    n_terminal = [p for p in accepted if p.interval[1] < parent_res]
    if n_terminal:
        return max(n_terminal, key=lambda p: (p.interval[1], p.interval[0]))
    return min(accepted, key=lambda p: (p.interval[0], p.interval[1]))


def residue_transform_map(
    moving: TileFold,
    accepted: Sequence[PieceFit],
) -> dict[int, tuple[Rotation, Translation]]:
    """Every moving-tile residue gets a piece (own domain) or inherited transform."""
    if not accepted:
        raise ValueError("refuse is fail-closed — do not invent a transformed pose")
    out: dict[int, tuple[Rotation, Translation]] = {}
    for parent_res in range(moving.start, moving.end + 1):
        piece = inherit_piece_for_residue(parent_res, accepted)
        assert piece.rotation is not None and piece.translation is not None
        out[parent_res] = (piece.rotation, piece.translation)
    return out


def apply_piecewise_transform_pdb(
    pdb: str,
    tile_start: int,
    residue_rt: Mapping[int, tuple[Sequence[Sequence[float]], Sequence[float]]],
) -> str:
    """Apply each residue's R, t to that residue's ATOM/HETATM. No atom invented."""
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
            rt = residue_rt.get(parent_res)
            if rt is None:
                lines.append(line)
                continue
            rotation, translation = rt
            nx, ny, nz = _add(_matvec(rotation, (x, y, z)), translation)
            line = f"{line[:30]}{nx:8.3f}{ny:8.3f}{nz:8.3f}{line[54:]}"
        lines.append(line)
    text = "\n".join(lines)
    return text + ("\n" if ended_nl or text else "")


def transform_tile_piecewise(tile: TileFold, accepted: Sequence[PieceFit]) -> TileFold:
    residue_rt = residue_transform_map(tile, accepted)
    return TileFold(
        start=tile.start,
        end=tile.end,
        pdb=apply_piecewise_transform_pdb(tile.pdb, tile.start, residue_rt),
        plddt=tile.plddt,
        pae=tile.pae,
    )


def _ca_distance(p: Sequence[float], q: Sequence[float]) -> float:
    return _norm(_sub(p, q))


def _disclosure_after_apply(
    reference: TileFold,
    transformed: TileFold,
    overlap: Sequence[int],
    accepted: Sequence[PieceFit],
) -> tuple[Optional[float], Optional[float], int, Optional[float]]:
    """Full-overlap unweighted RMSD + max jump; linker_n + max linker jump."""
    all_m, all_r, used = paired_overlap_ca(reference, transformed)
    if not all_m:
        linker_res = [
            res
            for res in overlap
            if not any(p.interval[0] <= res <= p.interval[1] for p in accepted)
        ]
        return None, None, len(linker_res), None
    acc = 0.0
    jumps: list[float] = []
    for p, q in zip(all_m, all_r):
        d = _ca_distance(p, q)
        acc += d * d
        jumps.append(d)
    full_rmsd = (acc / len(all_m)) ** 0.5
    max_jump = max(jumps)
    fitted = {res for p in accepted for res in range(p.interval[0], p.interval[1] + 1)}
    linker_used = [res for res in used if res not in fitted]
    linker_n_moving = sum(
        1
        for res in range(transformed.start, transformed.end + 1)
        if res not in fitted
    )
    if linker_used:
        # Distances already paired in used-order with all_m / all_r.
        used_index = {res: i for i, res in enumerate(used)}
        linker_jumps = [
            _ca_distance(all_m[used_index[res]], all_r[used_index[res]]) for res in linker_used
        ]
        max_linker = max(linker_jumps)
    else:
        max_linker = 0.0
    return full_rmsd, max_jump, linker_n_moving, max_linker


def fit_overlap_piecewise(
    reference: TileFold,
    moving: TileFold,
    domains: Sequence[DomainInterval],
) -> tuple[tuple[PieceFit, ...], Optional[str], Optional[TileFold], Optional[float], Optional[float], Optional[int], Optional[float]]:
    """Fit every domain piece on this seam. All-or-nothing: refuse before apply.

    Returns ``(pieces, refuse_reason, transformed_or_none, full_rmsd, max_jump,
    linker_n, max_linker_jump)``.
    """
    overlap = overlap_parent_residues(reference, moving)
    candidates = candidates_intersecting_overlap(domains, overlap)
    if not candidates:
        return (), REFUSE_NO_DOMAIN_PIECES, None, None, None, None, None

    pieces: list[PieceFit] = []
    for domain in candidates:
        pieces.append(fit_domain_piece(reference, moving, domain))

    accepted = [p for p in pieces if p.accepted]
    thin = [p for p in pieces if p.refuse_reason == REFUSE_OVERLAP_CA_LT_3]
    other_refused = [
        p
        for p in pieces
        if p.refuse_reason is not None and p.refuse_reason != REFUSE_OVERLAP_CA_LT_3
    ]

    # Pieces that miss ≥3 Cα are not fitted. They refuse the parent only when
    # no fitted piece remains (Spec §1 step 3 / §2 overlap_ca_lt_3).
    if other_refused:
        return tuple(pieces), other_refused[0].refuse_reason, None, None, None, None, None
    if not accepted:
        reason = REFUSE_OVERLAP_CA_LT_3 if thin else REFUSE_NO_DOMAIN_PIECES
        return tuple(pieces), reason, None, None, None, None, None

    fitted_only = tuple(accepted)
    transformed = transform_tile_piecewise(moving, fitted_only)
    full_rmsd, max_jump, linker_n, max_linker = _disclosure_after_apply(
        reference, transformed, overlap, fitted_only
    )
    if max_linker is not None and max_linker > RMSD_REFUSE_ANGSTROM:
        return (
            tuple(pieces),
            REFUSE_LINKER_JUMP_GT_10,
            None,
            full_rmsd,
            max_jump,
            linker_n,
            max_linker,
        )
    return tuple(pieces), None, transformed, full_rmsd, max_jump, linker_n, max_linker


def align_tiles(
    tiles: Sequence[TileFold],
    domains: Sequence[DomainInterval],
) -> tuple[list[TileFold], list[PiecewiseSeamRecord], bool]:
    """N-terminal / earlier tile is the reference; later tiles chain onto the last accepted frame.

    All-or-nothing: the first refuse stops further transforms. ``accepted`` is
    True only when every inbound seam was accepted. Untransformed copies remain
    in the returned list for inspection; they are not written.
    """
    if not tiles:
        raise ValueError("align_tiles needs at least one tile")
    ordered = sorted(tiles, key=lambda t: (t.start, t.end))
    out: list[TileFold] = [ordered[0]]
    seams: list[PiecewiseSeamRecord] = []
    last_accepted = ordered[0]
    last_accepted_index = 1
    all_ok = True
    for i, moving in enumerate(ordered[1:], start=2):
        overlap = overlap_parent_residues(last_accepted, moving)
        pieces, reason, transformed, full_rmsd, max_jump, linker_n, max_linker = fit_overlap_piecewise(
            last_accepted, moving, domains
        )
        rec = PiecewiseSeamRecord(
            moving_tile_index=i,
            reference_tile_index=last_accepted_index,
            overlap_start=overlap[0] if overlap else 0,
            overlap_end=overlap[-1] if overlap else 0,
            pieces=pieces,
            linker_n=linker_n,
            max_linker_ca_jump=max_linker,
            rmsd_full_overlap_angstrom=full_rmsd,
            max_ca_jump_angstrom=max_jump,
            refuse_reason=reason,
        )
        seams.append(rec)
        if reason is not None or transformed is None:
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


# ── sibling tree + ops report ────────────────────────────────────────────────


def piecewise_kabsch_out_dir(out_root: Path | str, parent_job_id: int) -> Path:
    return Path(out_root) / "piecewise_kabsch" / str(parent_job_id)


def refuse_sibling_overwrite(
    out_dir: Path,
    assembler_dir: Optional[Path | str] = None,
    d125_dir: Optional[Path | str] = None,
    d126_dir: Optional[Path | str] = None,
) -> None:
    """Never write D-127 artifacts as if they were assembler / D-125 / D-126."""
    out = Path(out_dir).resolve()
    if "piecewise_kabsch" not in out.parts:
        raise SiblingOverwriteRefused(
            f"D-127 artifacts must land under a piecewise_kabsch/ directory, not {out}"
        )
    dest_pdb = (out / "stitched.pdb").resolve()
    checks: list[tuple[Optional[Path | str], str]] = [
        (assembler_dir, "assembler"),
        (d125_dir, "D-125 kabsch"),
        (d126_dir, "D-126 confidence_kabsch"),
    ]
    for other, label in checks:
        if other is None:
            continue
        other_path = Path(other).resolve()
        other_pdb = (other_path / "stitched.pdb").resolve()
        if out == other_path or dest_pdb == other_pdb:
            raise SiblingOverwriteRefused(
                f"refusing to write D-127 artifacts over {label} dir {other_path}"
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
    seams: Sequence[PiecewiseSeamRecord],
    accepted: bool,
    domain_intervals: Sequence[DomainInterval],
) -> None:
    payload = {
        "algorithm": ALGORITHM,
        "decision": DECISION,
        "parent_job_id": parent_job_id,
        "tile_job_ids": list(tile_job_ids),
        "windows": [list(w) for w in windows],
        "accepted": accepted,
        "seams": [s.to_json_row() for s in seams],
        "domain_intervals": [list(d.as_tuple()) for d in domain_intervals],
        "weight_epsilon": WEIGHT_EPSILON,
        "rmsd_refuse_angstrom": RMSD_REFUSE_ANGSTROM,
        "no_trim_loop": True,
    }
    (out / "provenance.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    with (out / "seams.jsonl").open("w", encoding="utf-8") as fh:
        for seam in seams:
            fh.write(json.dumps(seam.to_json_row()) + "\n")


def write_piecewise_kabsch_restitch(
    tiles: Sequence[TileFold],
    length: int,
    out_root: Path | str,
    *,
    parent_job_id: int,
    tile_job_ids: Sequence[int] = (),
    assembler_dir: Optional[Path | str] = None,
    d125_dir: Optional[Path | str] = None,
    d126_dir: Optional[Path | str] = None,
    domain_intervals: Optional[Sequence[Sequence[int]]] = None,
    accession: Optional[str] = None,
    span_start: Optional[int] = None,
    span_end: Optional[int] = None,
    cache_dir: Path = UNIPROT_CACHE,
) -> PiecewiseKabschRestitchResult:
    """Align tiles with piecewise Kabsch, then existing write_stitched on accept only.

    ``winning_tile`` is imported so the stitch path stays the assembler (A/B
    compare). A refuse is a recorded outcome, not invented coordinates.
    All-or-nothing: success artifacts are written only if every seam accepted.
    """
    require_inventory_parent(parent_job_id)
    out = piecewise_kabsch_out_dir(out_root, parent_job_id)
    if d125_dir is None:
        d125_dir = kabsch_out_dir(out_root, parent_job_id)
    if d126_dir is None:
        d126_dir = confidence_kabsch_out_dir(out_root, parent_job_id)
    refuse_sibling_overwrite(out, assembler_dir, d125_dir, d126_dir)
    if winning_tile is None:  # pragma: no cover — import pin
        raise RuntimeError("winning_tile must remain importable")
    # Keep apply_rigid_transform_pdb import live so a deleted D-125 helper fails here.
    if apply_rigid_transform_pdb is None:  # pragma: no cover
        raise RuntimeError("apply_rigid_transform_pdb must remain importable")

    domains = resolve_domain_intervals(
        domain_intervals=domain_intervals,
        accession=accession,
        span_start=span_start,
        span_end=span_end,
        cache_dir=cache_dir,
    )
    aligned, seams, accepted = align_tiles(tiles, domains)
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
        domain_intervals=domains,
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

    return PiecewiseKabschRestitchResult(
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
    d127_accepted: Mapping[int, bool],
) -> OpsSuccessReport:
    """Confusion vs D-125 and vs D-126. A drop is a named finding. 0-of-3 is allowed.

    Not a CI assert against live ops. Counts parents present in **all three**
    maps that are in the Spec's 27. ``recovered_of_primary_three`` counts
    primary-three ids that D-127 accepted (0 is a valid experimental result).
    """
    common = (
        set(d125_accepted)
        & set(d126_accepted)
        & set(d127_accepted)
        & set(KABSCH_RESTITCH_PARENT_IDS)
    )
    n_d125_pp = n_d125_pr = 0
    n_d126_pp = n_d126_pr = n_d126_rp = n_d126_rr = 0
    for pid in sorted(common):
        a125 = bool(d125_accepted[pid])
        a126 = bool(d126_accepted[pid])
        a127 = bool(d127_accepted[pid])
        if a125 and a127:
            n_d125_pp += 1
        elif a125 and not a127:
            n_d125_pr += 1
        if a126 and a127:
            n_d126_pp += 1
        elif a126 and not a127:
            n_d126_pr += 1
        elif (not a126) and a127:
            n_d126_rp += 1
        else:
            n_d126_rr += 1
    recovered = sum(
        1
        for pid in PRIMARY_THREE_PARENT_IDS
        if bool(d127_accepted.get(pid, False))
    )
    return OpsSuccessReport(
        n_d125_pass_d127_pass=n_d125_pp,
        n_d125_pass_d127_refuse=n_d125_pr,
        n_d126_pass_d127_pass=n_d126_pp,
        n_d126_pass_d127_refuse=n_d126_pr,
        n_d126_refuse_d127_pass=n_d126_rp,
        n_d126_refuse_d127_refuse=n_d126_rr,
        recovered_of_primary_three=recovered,
    )
