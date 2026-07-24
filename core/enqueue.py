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

import os
from dataclasses import dataclass
from typing import Callable, Iterable

from sqlalchemy import select
from sqlalchemy.orm import Session

from core.manifest import ManifestRow, build_manifest
from core.queue import COMPLETE, PENDING
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
# D-042: rental `chunk_size` was `None` (D-011's assumption: more VRAM makes chunking
# unnecessary). The first rental run FALSIFIED that — the ESMFold trunk's triangular attention
# (`tri_att_start`) is O(L³), so IGF2R (2,491 aa) asked 230 GiB on a 95 GiB card. No rentable
# card closes that gap; chunking is the only mitigation, so rental now chunks like local.
TIER_RECIPE: dict[str, dict] = {
    "local":  {"dtype": DEFAULT_DTYPE, "chunk_size": DEFAULT_CHUNK_SIZE},  # int8 / 64
    "rental": {"dtype": "fp16", "chunk_size": 64},                        # D-011 → D-042 (was None)
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


# ── Requeue: the deliberate re-fold path enqueue idempotency cannot give (D-044) ──

@dataclass
class RequeueSummary:
    requeued: int              # non-complete jobs reset to pending
    skipped_complete: int      # already folded — left untouched (re-folding is paid, pointless)
    not_found: list[str]       # accessions with no job at all — reported, never silently dropped


def requeue_jobs(session: Session, accessions: Iterable[str]) -> RequeueSummary:
    """Reset the jobs for ``accessions`` to ``pending`` so a worker can claim them again (D-044).

    Works around D-026's one-way idempotency: enqueue keys on the ``protein_analyses`` row, so it
    cannot re-offer a target that already has one but failed. Joined to jobs via
    ``protein_analyses.input_value`` (the D-038 uniprot key). A **non-``complete``** job → ``pending``
    with the stale claim/error cleared and ``attempts`` reset to 0 (a deliberate operator retry gets
    a full budget — distinct from ``fail()``'s attempts-untouched rule, D-009 §1 Am. 2, which is
    about *automatic* history). A **``complete``** job is left untouched: requeue never destroys a
    good fold. An accession with **no job** is reported, not dropped. Idempotent."""
    requeued = skipped = 0
    not_found: list[str] = []
    for accession in accessions:
        jobs = session.execute(
            select(JobRecord)
            .join(ProteinAnalysis, JobRecord.analysis_id == ProteinAnalysis.id)
            .where(ProteinAnalysis.input_type == "uniprot")
            .where(ProteinAnalysis.input_value == accession)
        ).scalars().all()
        if not jobs:
            not_found.append(accession)
            continue
        for job in jobs:
            if job.status == COMPLETE:
                skipped += 1
                continue
            job.status = PENDING
            job.claimed_at = None
            job.worker_id = None
            job.error = None
            job.attempts = 0
            requeued += 1
    session.commit()
    return RequeueSummary(requeued=requeued, skipped_complete=skipped, not_found=not_found)


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


# ── CLI: the prod invocation entry point (wires D-023 manifest → D-026 enqueue) ──
#
# Same shape as worker/main.py: nothing new is decided here, it INVOKES ruled pieces.
# The one baked capability is subset enqueuing — because the first fold is deliberately
# ONE local-tier target (prove the path before A6000 spend, the pre-work's step 3), and
# `enqueue_cohort` already takes `Iterable[ManifestRow]`, so a subset is just the manifest
# filtered before it is passed in. Idempotency (D-026 iii) makes "one now, the rest later"
# safe by construction: the single target is not re-created when the full cohort runs.
#
#   python -m core.enqueue --accession Q96NY8      # one target (NECTIN4, local)
#   python -m core.enqueue --bucket local --limit 1
#   python -m core.enqueue --dry-run               # show the selection, touch nothing
#   python -m core.enqueue                         # the full cohort (80 foldable / 82)
#   python -m core.enqueue --requeue P78536 P11717 # deliberate re-fold: reset these jobs to pending (D-044)

def select_rows(
    rows: Iterable[ManifestRow],
    *,
    accession: str | None = None,
    bucket: str | None = None,
    limit: int | None = None,
) -> list[ManifestRow]:
    """Filter the manifest to a subset before enqueue. Composable: `accession`, then
    `bucket` (tier), then `limit`. `--limit` counts FOLDABLE rows — a named exclusion
    yields no job, so exclusions are dropped before taking N, making `--limit N` mean N
    jobs. No filters → the whole manifest (the enqueue skips exclusions itself, D-022)."""
    selected = list(rows)
    if accession is not None:
        selected = [r for r in selected if r.accession == accession]
    if bucket is not None:
        selected = [r for r in selected if r.tier == bucket]
    if limit is not None:
        selected = [r for r in selected if not r.excluded][:limit]
    return selected


def _build_engine():
    """A real SQLAlchemy engine from `DATABASE_URL`, normalized to the psycopg 3 scheme
    (D-012) the same way app/config.py and env.py do — so a raw `postgresql://` from the
    Fly attach works. Loud `KeyError` if `DATABASE_URL` is unset."""
    from sqlalchemy import create_engine

    from db.dburl import normalize_db_url

    return create_engine(normalize_db_url(os.environ["DATABASE_URL"]), future=True)


def run(
    argv: list[str] | None = None,
    *,
    engine_factory: Callable[[], object] = _build_engine,
    fetch: SequenceFetcher = uniprot_fetcher,
) -> int:
    """Parse args, filter the manifest, and enqueue the selection. `engine_factory` and
    `fetch` are injected in tests (a SQLite engine + a fake fetcher) and default to the
    real prod engine + UniProt fetcher. Returns a process exit code."""
    import argparse

    parser = argparse.ArgumentParser(
        prog="python -m core.enqueue",
        description="Enqueue cohort targets to the queue (D-023 manifest → D-026 enqueue).",
    )
    parser.add_argument("--accession", help="enqueue only this UniProt accession")
    parser.add_argument("--bucket", choices=["local", "rental"],
                        help="enqueue only this compute tier")
    parser.add_argument("--limit", type=int,
                        help="enqueue at most N foldable rows (after --accession/--bucket)")
    parser.add_argument("--dry-run", action="store_true",
                        help="print the selected targets; do not touch the database")
    parser.add_argument("--requeue", nargs="+", metavar="ACCESSION",
                        help="reset these targets' jobs to pending and exit (D-044) — a deliberate "
                             "re-fold; no fetch, no new rows. A complete fold is left untouched")
    args = parser.parse_args(argv)

    # --requeue short-circuits before the manifest/fetch path: it only moves existing jobs.
    if args.requeue:
        engine = engine_factory()
        with Session(engine) as session:
            summary = requeue_jobs(session, args.requeue)
        print(f"requeued: requeued={summary.requeued} "
              f"skipped_complete={summary.skipped_complete} not_found={summary.not_found}")
        return 1 if summary.not_found else 0   # an unknown accession is loud, per D-044

    rows = build_manifest()
    selected = select_rows(rows, accession=args.accession, bucket=args.bucket, limit=args.limit)

    if not selected:
        print("no targets match the filter — nothing to enqueue")
        return 1

    if args.dry_run:
        print(f"DRY RUN — {len(selected)} target(s) selected, database untouched:")
        for r in selected:
            print(f"  {r.accession}  {r.gene:<10} tier={r.tier:<7} "
                  f"span={r.span}  disposition={r.disposition}")
        return 0

    engine = engine_factory()
    with Session(engine) as session:
        summary = enqueue_cohort(session, selected, fetch)
    print(f"enqueued: created={summary.created} existed={summary.existed} "
          f"excluded={summary.excluded}  (ranking_run_id={summary.ranking_run_id})")
    return 0


def main() -> int:
    return run()


if __name__ == "__main__":
    raise SystemExit(main())
