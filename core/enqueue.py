"""D-026 enqueue: the manifest becomes `protein_analyses` + `jobs` (feed the queue).

Turns each FOLDABLE manifest row (disposition `ranked` or `held_out`; the 2
`excluded` get nothing — D-022) into a self-contained unit of work:

- a **`protein_analyses`** row — WHAT to fold: the exact residues, the UniProt
  release they came from, the boundary method, the folded span, and the routing
  provenance;
- a **`jobs`** row (`status=pending`) — a claimable unit whose `inference_settings`
  is the tier's fold recipe (D-018 / S-003): local `int8`/chunk-64, rental
  `fp16`/no-chunk.

Ruled in D-026:
- The sequence is fetched and STORED at enqueue **with its UniProt release** — a
  worker fetching later could fold a different molecule, silently, because UniProt
  revises sequences (D-026 i). The fetcher is injected so tests stay hermetic.
- The folded span is the **largest** ECD span, inherited from the bucketing (D-020)
  so routing and fold agree on which span (D-026 ii). Recorded per row.
- One `ranking_runs` row per enqueue; idempotent on `(target_list_version,
  accession)`, so a re-run reports "exists" and writes nothing new (D-026 iii) —
  the enqueue is the irreversible step D-023's manifest-first guard protected.

Held-out means held out of the RANKING, not of folding (D-021/D-024): the 13
whole-method targets are folded — a deliberate spend for the coverage surface and
the single-target view — but are not ranked.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable

from sqlalchemy import select
from sqlalchemy.orm import Session

from core.manifest import ManifestRow
from db.models import JobRecord, ProteinAnalysis, RankingRun
from worker.runner import (
    DEFAULT_CHUNK_SIZE,
    DEFAULT_DTYPE,
    MODEL_ID,
    MODEL_REVISION,
    SLICED_ECD,
    WHOLE,
)

# The Kathad-82 cohort of record (D-020). Stamped on the ranking_run so a ranking
# is always tied to the target-list revision it was computed against.
TARGET_LIST_VERSION = "Kathad-2024-PLOSONE-S3-82"

# Per-tier fold recipe (D-018 / S-003) — recorded here, not re-decided.
TIER_RECIPE: dict[str, dict] = {
    "local":  {"dtype": DEFAULT_DTYPE, "chunk_size": DEFAULT_CHUNK_SIZE},  # int8 / 64
    "rental": {"dtype": "fp16", "chunk_size": None},                      # A6000, D-011
}


@dataclass(frozen=True)
class FetchedSequence:
    sequence: str
    uniprot_release: str    # names WHICH UniProt — sequences get revised (D-026 i)


SequenceFetcher = Callable[[str], FetchedSequence]


@dataclass
class EnqueueSummary:
    ranking_run_id: int
    created: int    # new (analysis, job) pairs written this run
    existed: int    # already present for this cohort version — idempotent skip
    excluded: int   # named exclusions, no job (D-022)

    @property
    def enqueued(self) -> int:
        return self.created + self.existed


def _fold_input(row: ManifestRow, full_sequence: str) -> tuple[str, str]:
    """(residues_to_fold, source). sliced_ecd → the largest ECD span (1-based,
    inclusive); whole → the full sequence."""
    if row.boundary_method == "sliced_ecd":
        assert row.ecd_start is not None and row.ecd_end is not None
        return full_sequence[row.ecd_start - 1: row.ecd_end], SLICED_ECD
    return full_sequence, WHOLE


def enqueue_cohort(
    session: Session,
    rows: Iterable[ManifestRow],
    fetch_sequence: SequenceFetcher,
    *,
    target_list_version: str = TARGET_LIST_VERSION,
) -> EnqueueSummary:
    """Create a ranking_run + protein_analyses + jobs for the foldable manifest rows.

    Idempotent on (target_list_version, accession): a second run finds the existing
    analyses and writes nothing new. A fetch failure propagates — a target that
    cannot be fetched must not be silently dropped (that would understate coverage);
    fix the fetch and re-run, which is safe."""
    rows = list(rows)

    run = session.execute(
        select(RankingRun).where(RankingRun.target_list_version == target_list_version)
    ).scalars().first()
    if run is None:
        # scorer_version empty: the learned scorer (D-015 §3) does not exist yet.
        run = RankingRun(target_list_version=target_list_version, scorer_version="")
        session.add(run)
        session.flush()   # need run.id for the FK below

    created = existed = excluded = 0
    for row in rows:
        if row.excluded:
            excluded += 1
            continue

        already = session.execute(
            select(ProteinAnalysis).where(
                ProteinAnalysis.ranking_run_id == run.id,
                ProteinAnalysis.input_type == "uniprot",
                ProteinAnalysis.input_value == row.accession,
            )
        ).scalars().first()
        if already is not None:
            existed += 1
            continue

        fetched = fetch_sequence(row.accession)
        fold_seq, source = _fold_input(row, fetched.sequence)

        analysis = ProteinAnalysis(
            input_type="uniprot",
            input_value=row.accession,
            ranking_run_id=run.id,
            meta={
                "gene": row.gene,
                "label": row.label,
                "disposition": row.disposition,
                "held_out": row.held_out,
                "tier": row.tier,
                "tier_reason": row.tier_reason,
                "boundary_method": row.boundary_method,
                "source": source,
                "uniprot_release": fetched.uniprot_release,
                "full_length": len(fetched.sequence),
                "fold_length": len(fold_seq),
                "ecd_start": row.ecd_start,
                "ecd_end": row.ecd_end,
                "primary_match": row.primary_match,
                "sequence": fold_seq,   # the exact residues folded (D-026 i)
            },
        )
        session.add(analysis)
        session.flush()   # need analysis.id for the job FK

        recipe = TIER_RECIPE[row.tier]
        session.add(JobRecord(
            analysis_id=analysis.id,
            status="pending",
            inference_settings={
                "model_id": MODEL_ID,
                "model_revision": MODEL_REVISION,
                "dtype": recipe["dtype"],
                "chunk_size": recipe["chunk_size"],
                "source": source,
                "ecd_start": row.ecd_start,
                "ecd_end": row.ecd_end,
            },
        ))
        created += 1

    session.commit()
    return EnqueueSummary(
        ranking_run_id=run.id, created=created, existed=existed, excluded=excluded
    )


# ── Real UniProt sequence fetcher (network; injected, never used in tests) ────
def uniprot_fetcher(accession: str) -> FetchedSequence:
    """Fetch a reviewed sequence and name the UniProt release it came from. Mirrors
    scripts/ecd_lengths.py's client; the release is read from the response header
    (falling back to the entry's sequence version) so provenance names WHICH
    UniProt, per D-026 (i)."""
    import json
    from urllib.request import Request, urlopen

    url = f"https://rest.uniprot.org/uniprotkb/{accession}.json"
    req = Request(url, headers={"User-Agent": "PharmFoldMDK/0.1 (enqueue)"})
    with urlopen(req, timeout=30) as resp:
        release = resp.headers.get("X-UniProt-Release", "")
        data = json.loads(resp.read().decode("utf-8"))
    sequence = (data.get("sequence") or {}).get("value") or ""
    if not sequence:
        raise RuntimeError(f"{accession}: no sequence in UniProt response")
    if not release:
        version = (data.get("entryAudit") or {}).get("sequenceVersion")
        release = f"seqv{version}" if version is not None else "unknown"
    return FetchedSequence(sequence=sequence, uniprot_release=release)
