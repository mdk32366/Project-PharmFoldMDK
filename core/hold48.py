"""D-111 — T5 hold-48 tiling planner, mucin ceiling, and one-shot rental guards.

Population is **discovered** from `data/census/census_manifest.v7.csv`
(`tranche=5` and `span_aa > 1656`) — 48 rows, of which 3 named mucins are never
tiled. Geometry is the BUILD GO window: 1656 / overlap 128 / stride 1528.

⚠ This module does not talk to Fly, does not rent a GPU, and does not raise the
1656 cap. `emit_tile_jobs` writes only the Session it is given (tests / an
explicit local caller). Parent `jobs.tier` stays NULL.
"""
from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from core.contracts import TIER_RECIPE
from db.models import JobRecord, ProteinAnalysis

# Same pins as `worker.runner` (D-018). Duplicated so `app/artifacts.py` can
# import this module without dragging `worker/` into the Fly image (DEP-001).
# `core/enqueue.py` already imports runner; this module must not.
MODEL_ID = "facebook/esmfold_v1"
MODEL_REVISION = "75a3841ee059df2bf4d56688166c8fb459ddd97a"
SLICED_ECD = "sliced_ecd"

_ROOT = Path(__file__).resolve().parent.parent
MANIFEST_V7 = _ROOT / "data" / "census" / "census_manifest.v7.csv"
UNIPROT_CACHE = _ROOT / "data" / "census" / "spancache"

# BUILD GO geometry (issue #210 / D-111). ⚠ Not D-109 ruling 2's 1,026.
TILE_WINDOW_AA = 1656
MIN_OVERLAP_AA = 128
STRIDE_AA = TILE_WINDOW_AA - MIN_OVERLAP_AA  # 1528
DOMAIN_SNAP_AA = 64

# Named by the GO. The category is the molecule, not the length (D-109 ruling 3).
MUCIN_ACCESSIONS: frozenset[str] = frozenset({"Q8WXI7", "Q9UKN1", "Q685J3"})
IGF2R_ACCESSION = "P11717"
IGF2R_SPAN_AA = 2264

OUT_OF_CLASS = "out_of_class"
HOLD48_KIND_PARENT = "parent"
HOLD48_KIND_TILE = "tile"

CENSUS_TRANCHE = 5


class OneShotRentalForbidden(ValueError):
    """Claim or enqueue of a mucin, or of a hold-48 parent as one sequence, as
    ``tier=rental``. The message names which. Must be able to go red in tests."""


class UncoveredResidue(ValueError):
    """A residue the planner or stitch cannot cover. Never filled with invented
    coordinates (D-111 stitch rule)."""


@dataclass(frozen=True)
class Hold48Row:
    """One hold-48 protein as the census manifest records it."""

    accession: str
    span_aa: int
    span_start: int
    span_end: int
    is_mucin: bool


@dataclass(frozen=True)
class TileSpec:
    """One tile the planner emits. Coordinates are 1-based inclusive on the
    **folded ECD sequence** (length ``span_aa``), not UniProt chain indices."""

    accession: str
    start: int
    end: int
    parent_job_id: Optional[int]
    tile_index: int
    n_tiles: int

    @property
    def length(self) -> int:
        return self.end - self.start + 1


def n_tiles(length: int) -> int:
    """``n_tiles(L) = 1 if L≤1656 else ceil((L-1656)/1528)+1``."""
    if length <= TILE_WINDOW_AA:
        return 1
    return math.ceil((length - TILE_WINDOW_AA) / STRIDE_AA) + 1


def hold48_rows(manifest: Path = MANIFEST_V7) -> list[Hold48Row]:
    """The 48: census v7, tranche 5, ``span_aa > 1656``. Discovered, not listed."""
    with manifest.open(encoding="utf-8", newline="") as fh:
        out = [
            Hold48Row(
                accession=r["census_accession"],
                span_aa=int(r["span_aa"]),
                span_start=int(r["span_start"]),
                span_end=int(r["span_end"]),
                is_mucin=r["census_accession"] in MUCIN_ACCESSIONS,
            )
            for r in csv.DictReader(fh)
            if r.get("tranche") == str(CENSUS_TRANCHE) and int(r["span_aa"]) > TILE_WINDOW_AA
        ]
    return out


def tileable_rows(manifest: Path = MANIFEST_V7) -> list[Hold48Row]:
    return [r for r in hold48_rows(manifest) if not r.is_mucin]


def mucin_rows(manifest: Path = MANIFEST_V7) -> list[Hold48Row]:
    return [r for r in hold48_rows(manifest) if r.is_mucin]


def is_mucin(accession: str) -> bool:
    return accession in MUCIN_ACCESSIONS


def is_hold48_tileable(accession: str, manifest: Path = MANIFEST_V7) -> bool:
    return any(r.accession == accession for r in tileable_rows(manifest))


def is_tile_job(inference_settings: Optional[dict], meta: Optional[dict] = None) -> bool:
    """A tile carries ``parent_job_id`` + start/end, or ``hold48_kind=tile``."""
    s = inference_settings or {}
    m = meta or {}
    if m.get("hold48_kind") == HOLD48_KIND_TILE:
        return True
    return (
        s.get("parent_job_id") is not None
        and s.get("tile_start") is not None
        and s.get("tile_end") is not None
    )


def refuse_oneshot_rental(
    accession: str,
    *,
    is_tile: bool,
    jobs_tier: Optional[str],
    sequence_length: Optional[int] = None,
) -> None:
    """Raise if this would be a mucin or a hold parent claimed/enqueued as
    one-sequence ``tier=rental``. Tile jobs of the 45 are the allowed path.

    ⚠ Called when the *intent* is a rental one-shot (``jobs_tier == 'rental'``
    and not a tile), not on the NULL-tier hold itself — that hold is already
    unclaimable under D-090.
    """
    if jobs_tier != "rental":
        return
    if is_mucin(accession):
        raise OneShotRentalForbidden(
            f"{accession}: mucin is out_of_class under D-111 / D-109 ruling 3 — "
            f"never enqueued or claimed as tier=rental one-shot ESMFold"
        )
    if is_tile:
        if sequence_length is not None and sequence_length > TILE_WINDOW_AA:
            raise OneShotRentalForbidden(
                f"{accession}: tile length {sequence_length} exceeds "
                f"{TILE_WINDOW_AA} — the 1656 cap is not raised"
            )
        return
    if is_hold48_tileable(accession):
        raise OneShotRentalForbidden(
            f"{accession}: hold-48 parent cannot be claimed as one-sequence "
            f"tier=rental until stitch succeeds (D-111); tiles only"
        )


def _snap_edge(edge: int, domain_ends: Sequence[int], *, lo: int, hi: int) -> int:
    """Snap ``edge`` to the nearest domain end within ±64 that stays in ``[lo, hi]``."""
    cands = [d for d in domain_ends if abs(d - edge) <= DOMAIN_SNAP_AA and lo <= d <= hi]
    if not cands:
        return edge
    return min(cands, key=lambda d: (abs(d - edge), d))


def place_tiles(
    length: int,
    *,
    domain_ends: Sequence[int] = (),
) -> list[tuple[int, int]]:
    """1-based inclusive ``(start, end)`` windows covering ``1..length``.

    Fixed stride, last tile clamped to ``L``. Optional domain-end snap on
    internal edges; a snap that would exceed the window, invert a tile, or
    leave a residue uncovered is dropped and the unsnapped placement stands.
    """
    if length < 1:
        raise ValueError(f"length must be ≥1, got {length}")
    n = n_tiles(length)
    raw: list[tuple[int, int]] = []
    for i in range(n):
        start = 1 + i * STRIDE_AA
        end = min(start + TILE_WINDOW_AA - 1, length)
        raw.append((start, end))
    raw[-1] = (raw[-1][0], length)
    if not domain_ends:
        _assert_cover(raw, length)
        return raw

    snapped: list[tuple[int, int]] = []
    for i, (start, end) in enumerate(raw):
        if i > 0:
            start = _snap_edge(start, domain_ends, lo=1, hi=length)
        if i < n - 1:
            end = _snap_edge(end, domain_ends, lo=1, hi=length)
        if end - start + 1 > TILE_WINDOW_AA or start > end:
            start, end = raw[i]
        snapped.append((start, end))
    snapped[-1] = (snapped[-1][0], length)
    try:
        _assert_cover(snapped, length)
    except UncoveredResidue:
        _assert_cover(raw, length)
        return raw
    for s, e in snapped:
        if e - s + 1 > TILE_WINDOW_AA:
            _assert_cover(raw, length)
            return raw
    return snapped


def _assert_cover(windows: Sequence[tuple[int, int]], length: int) -> None:
    covered: set[int] = set()
    for start, end in windows:
        if end - start + 1 > TILE_WINDOW_AA:
            raise UncoveredResidue(
                f"tile {start}-{end} length {end - start + 1} exceeds {TILE_WINDOW_AA}"
            )
        covered.update(range(start, end + 1))
    missing = [i for i in range(1, length + 1) if i not in covered]
    if missing:
        raise UncoveredResidue(
            f"tiles leave residues uncovered: {missing[0]}..{missing[-1]} "
            f"({len(missing)} residues) — a gap is an error, not invented coordinates"
        )


def domain_ends_span_relative(
    *,
    accession: str,
    span_start: int,
    span_end: int,
    cache_dir: Path = UNIPROT_CACHE,
) -> tuple[int, ...]:
    """UniProt ``Domain``/``Repeat`` ends mapped onto the folded span (1-based).

    Empty when the cache file is absent — CI has no spancache (gitignored). A
    missing cache is a category, not a fetch.
    """
    path = cache_dir / f"{accession}.json"
    if not path.is_file():
        return ()
    import json  # noqa: PLC0415 — only when a cache file exists

    doc = json.loads(path.read_text(encoding="utf-8"))
    ends: list[int] = []
    for feat in doc.get("features") or []:
        if feat.get("type") not in ("Domain", "Repeat"):
            continue
        loc = feat.get("location") or {}
        node = loc.get("end") or {}
        value = node.get("value")
        if value is None or node.get("modifier") == "UNKNOWN":
            continue
        chain_end = int(value)
        if chain_end < span_start or chain_end > span_end:
            continue
        ends.append(chain_end - span_start + 1)
    return tuple(sorted(set(ends)))


def plan_tiles(
    row: Hold48Row,
    *,
    parent_job_id: Optional[int] = None,
    domain_ends: Optional[Sequence[int]] = None,
    cache_dir: Path = UNIPROT_CACHE,
) -> list[TileSpec]:
    """Emit tile specs for one hold-48 protein. Mucins → ``[]``. No parent claim."""
    if row.is_mucin:
        return []
    ends: Sequence[int]
    if domain_ends is None:
        ends = domain_ends_span_relative(
            accession=row.accession,
            span_start=row.span_start,
            span_end=row.span_end,
            cache_dir=cache_dir,
        )
    else:
        ends = domain_ends
    windows = place_tiles(row.span_aa, domain_ends=ends)
    n = len(windows)
    return [
        TileSpec(
            accession=row.accession,
            start=start,
            end=end,
            parent_job_id=parent_job_id,
            tile_index=i,
            n_tiles=n,
        )
        for i, (start, end) in enumerate(windows)
    ]


def plan_all_tileable(
    *,
    manifest: Path = MANIFEST_V7,
    parent_job_ids: Optional[dict[str, int]] = None,
    cache_dir: Path = UNIPROT_CACHE,
) -> list[TileSpec]:
    """Planner over the 45. Does not invent an accession list."""
    ids = parent_job_ids or {}
    out: list[TileSpec] = []
    for row in tileable_rows(manifest):
        out.extend(plan_tiles(row, parent_job_id=ids.get(row.accession), cache_dir=cache_dir))
    return out


def emit_tile_jobs(
    session: Session,
    parent_job: JobRecord,
    parent_analysis: ProteinAnalysis,
    *,
    domain_ends: Optional[Sequence[int]] = None,
    cache_dir: Path = UNIPROT_CACHE,
) -> list[TileSpec]:
    """Write tile analysis+job rows for one parent. Parent ``tier`` is not touched.

    ⚠ Mucins emit nothing. ⚠ Does not claim the parent. ⚠ ``jobs.tier`` on
    children is ``rental`` so a later rented-card worker can claim them; this
    function does not call ``claim``.
    """
    accession = parent_analysis.input_value
    if is_mucin(accession):
        return []

    meta = dict(parent_analysis.meta or {})
    sequence = meta["sequence"]
    span_aa = int(meta.get("span_aa") or meta.get("fold_length") or len(sequence))
    span_start = int(meta.get("ecd_start") or meta.get("span_start") or 1)
    span_end = int(meta.get("ecd_end") or meta.get("span_end") or span_aa)
    row = Hold48Row(
        accession=accession,
        span_aa=span_aa,
        span_start=span_start,
        span_end=span_end,
        is_mucin=False,
    )
    specs = plan_tiles(
        row,
        parent_job_id=parent_job.id,
        domain_ends=domain_ends,
        cache_dir=cache_dir,
    )
    parent_ecd_start = meta.get("ecd_start")
    source = meta.get("source") or meta.get("boundary_method") or SLICED_ECD

    merged_parent = dict(meta)
    merged_parent["hold48_kind"] = HOLD48_KIND_PARENT
    parent_analysis.meta = merged_parent
    # ⚠ THE HOLD. Do not set parent_job.tier.

    for spec in specs:
        tile_seq = sequence[spec.start - 1: spec.end]
        if spec.length != len(tile_seq):
            raise UncoveredResidue(
                f"{accession} tile {spec.tile_index}: slice length {len(tile_seq)} "
                f"!= planned {spec.length}"
            )
        if spec.length > TILE_WINDOW_AA:
            raise OneShotRentalForbidden(
                f"{accession} tile {spec.tile_index} length {spec.length} > {TILE_WINDOW_AA}"
            )
        if parent_ecd_start is not None:
            tile_ecd_start = int(parent_ecd_start) + spec.start - 1
            tile_ecd_end = int(parent_ecd_start) + spec.end - 1
        else:
            tile_ecd_start, tile_ecd_end = spec.start, spec.end
        child_meta = {
            **{k: v for k, v in meta.items() if k not in ("sequence", "fold_provenance")},
            "tier": "rental",
            "sequence": tile_seq,
            "span_aa": spec.length,
            "fold_length": spec.length,
            "ecd_start": tile_ecd_start,
            "ecd_end": tile_ecd_end,
            "tile_start": spec.start,
            "tile_end": spec.end,
            "parent_job_id": parent_job.id,
            "tile_index": spec.tile_index,
            "n_tiles": spec.n_tiles,
            "hold48_kind": HOLD48_KIND_TILE,
        }
        child = ProteinAnalysis(
            input_type=parent_analysis.input_type,
            input_value=accession,
            structure_source="",
            ranking_run_id=parent_analysis.ranking_run_id,
            cohort_tranche=parent_analysis.cohort_tranche,
            meta=child_meta,
        )
        session.add(child)
        session.flush()
        session.add(
            JobRecord(
                analysis_id=child.id,
                status="pending",
                tier="rental",
                inference_settings={
                    "model_id": MODEL_ID,
                    "model_revision": MODEL_REVISION,
                    "source": source,
                    "ecd_start": tile_ecd_start,
                    "ecd_end": tile_ecd_end,
                    "parent_job_id": parent_job.id,
                    "tile_start": spec.start,
                    "tile_end": spec.end,
                    "tile_index": spec.tile_index,
                    "n_tiles": spec.n_tiles,
                    "dtype": TIER_RECIPE["rental"]["dtype"],
                    "chunk_size": TIER_RECIPE["rental"]["chunk_size"],
                },
            )
        )
    session.flush()
    return specs


def apply_mucin_ceiling(
    session: Session,
    *,
    artifact_root: Optional[str] = None,
) -> list[str]:
    """Set the 3 mucins to ``out_of_class``. Writes **zero** PDB / PAE files.

    Finds analyses by accession among the hold-48 mucin set. Parent jobs go
    ``out_of_class``; ``pdb_path`` / ``pae_json_path`` stay NULL.
    """
    marked: list[str] = []
    analyses = session.execute(select(ProteinAnalysis)).scalars().all()
    for analysis in analyses:
        acc = analysis.input_value
        if acc not in MUCIN_ACCESSIONS:
            continue
        meta = dict(analysis.meta or {})
        if meta.get("hold48_kind") == HOLD48_KIND_TILE:
            continue
        meta["hold48_disposition"] = OUT_OF_CLASS
        meta["hold48_kind"] = "mucin"
        analysis.meta = meta
        analysis.pdb_path = None
        analysis.pae_json_path = None
        jobs = session.execute(
            select(JobRecord).where(JobRecord.analysis_id == analysis.id)
        ).scalars().all()
        for job in jobs:
            job.status = OUT_OF_CLASS
            job.tier = None
            job.error = (
                f"{acc}: out_of_class — mucin, never ESMFold (D-111 / D-109 ruling 3)"
            )
        marked.append(acc)
        if artifact_root is not None:
            # ⚠ Explicitly do not write. The argument exists so callers cannot
            # "forget" and a test can pass a real directory and still see it empty.
            pass
    session.flush()
    return marked


def stitch_succeeded(parent_job: JobRecord) -> None:
    """Parent becomes claimable-as-stitched only after stitch. Not a one-shot.

    ⚠ Does **not** set ``tier='rental'``. The parent stays NULL-tier; the
    stitched artifact lives on the analysis. A one-sequence rental claim of the
    parent remains forbidden.
    """
    parent_job.error = None
    # status stays pending/complete as the caller decides; tier stays NULL.


def enqueue_oneshot_rental(accession: str, *, sequence_length: int, is_tile: bool = False) -> None:
    """The enqueue-side form of the guard. Tests call this as the one-shot path."""
    refuse_oneshot_rental(
        accession,
        is_tile=is_tile,
        jobs_tier="rental",
        sequence_length=sequence_length,
    )
