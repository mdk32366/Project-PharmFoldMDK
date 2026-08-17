#!/usr/bin/env python3
"""Census ingest — one tranche at a time. ⚠ THE ORM's MODELS, NEVER HAND-WRITTEN SQL.

    python scripts/census_ingest.py --tranche 1 --dry-run     # ⚠ ALWAYS FIRST
    python scripts/census_ingest.py --tranche 1

⚠⚠ **BOUNDED DELIBERATELY.** One tranche per invocation — not the 3,467 foldable rows and not the
5,016 census rows. **A bounded write that can be inspected beats one that cannot be undone.**

⚠ **`ranking_run_id` IS NULL ON EVERY CENSUS ROW.** `scripts/fit_scorer.py` selects **by
`ranking_run_id`**, so a census row attached to a run could be scored — and `### D-079` decision 1
bars that absolutely. **A NULL run id is what makes the bar structural rather than remembered.**

⚠ **`meta["tier"]` IS REQUIRED AND IS NOT DECORATION.** `app/artifacts.py` resolves the fold recipe
from `TIER_RECIPE[meta["tier"]]` **at claim time** (D-047) and **raises** without it. The recipe is
deliberately **not** stored as authority in `inference_settings`: storing it would create a second
source for one quantity with nothing comparing them.

⚠ **THE SLICE IS CHECKED BEFORE THE ROW IS WRITTEN.** `core.fold_reconcile.check_sliced_length`
raises on a disagreement, because a slice that disagrees with its recorded length is a construction
defect — and writing 1,307 of them would produce 1,307 plausible wrong artifacts.

⚠ **IDEMPOTENT on `(cohort_tranche, input_value)`.** A cohort row for the same accession is **not**
a collision: 75 of the 82 cohort accessions also appear in the census, and `P04626` holding both a
tranche-0 and a tranche-1 row is the **intended** state — which is precisely why every cohort
surface is tranche-filtered.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Optional

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from core.contracts import TIER_RECIPE, FoldSpec  # noqa: E402
from core.fold_reconcile import check_sliced_length  # noqa: E402
from worker.runner import MODEL_ID, MODEL_REVISION  # noqa: E402  (torch is lazy; safe to import)

CENSUS = REPO / "data" / "census"
CACHE = CENSUS / "spancache"
MANIFEST = CENSUS / "census_manifest.v7.csv"

#: ⚠ Tranche 0 is the 82-target cohort. A census row carrying it is a named stop condition.
COHORT_TRANCHE = 0


def manifest_rows(tranche: int) -> list[dict[str, str]]:
    with MANIFEST.open(encoding="utf-8", newline="") as fh:
        rows = [r for r in csv.DictReader(fh) if int(r["tranche"]) == tranche]
    if not rows:
        raise SystemExit(f"⚠ no manifest rows in tranche {tranche} — refusing a silent no-op")
    if tranche == COHORT_TRANCHE:
        raise SystemExit("⚠⚠ tranche 0 is the 82-target cohort and is never census. Refusing.")
    return rows


def sequence_from_cache(accession: str) -> str:
    p = CACHE / f"{accession}.json"
    if not p.exists():
        raise SystemExit(f"⚠ no cache entry for {accession} — NOT fetched; stop and report")
    return (json.loads(p.read_text(encoding="utf-8")).get("sequence") or {}).get("value", "")


#: ⚠ The ESM vocabulary's 20 standard residues plus `X` (unknown), which IS in the vocabulary and
#: tokenises — measured, not assumed (F-033). `U` (selenocysteine) and `O` (pyrrolysine) are NOT.
TOKENISABLE = set("ACDEFGHIKLMNPQRSTVWYX")


def untokenisable_residues(span: str) -> list[str]:
    """⚠ Residues ESMFold has no word for. Returns a LIST, so the reason can NAME them.

    D-085: a span carrying one of these cannot be tokenised, let alone folded — and left
    unguarded it fails as *"Unable to create tensor … excessive nesting"*, a message about
    batching that names nothing real (F-033). **A named category beats a true-but-useless error.**
    """
    return sorted(set(span) - TOKENISABLE)


def build_row(r: dict[str, str]) -> dict[str, Any]:
    """The analysis payload for one manifest row. ⚠ Raises rather than writing a bad slice."""
    span = int(r["span_aa"])
    start, end = int(r["span_start"]), int(r["span_end"])
    full = sequence_from_cache(r["census_accession"])
    fold_seq = full[start - 1: end]

    # ⚠ BEFORE the write, not after. Raises on disagreement.
    check_sliced_length(r["census_accession"], "sliced_ecd", span, fold_seq, len(full))

    return {
        "accession": r["census_accession"],
        "tranche": int(r["tranche"]),
        "tier": r["tier"],
        "meta": {
            # ⚠ `tier` and `sequence` are load-bearing: /claim raises without the first and cannot
            # fold without the second.
            "tier": r["tier"],
            "sequence": fold_seq,
            "boundary_method": r["boundary_method"],
            "source": r["boundary_method"],
            "census_class": r["census_class"],
            "span_aa": span,
            "ecd_start": start,
            "ecd_end": end,
            "full_length": len(full),
            "fold_length": len(fold_seq),
            "band": r["band"],
            "tier_reason": r["tier_reason"],
            "span_rule": r["span_rule"],
            "span_definition": r["span_definition"],
            "guards": r["guards"],
            "fold_order": int(r["fold_order"]),
            "cohort_tranche": int(r["tranche"]),
            # ⚠ Named on the row so nothing downstream has to infer it.
            "is_census": True,
            "scored": False,
            "not_scored_reason": "D-079 decision 1 — no census row is scored",
        },
        "inference_settings": {
            # ⚠⚠ `model_revision` IS REQUIRED AND ITS ABSENCE STRANDED TEN JOBS. /claim reads
            # `s["model_revision"]` and raises KeyError — AFTER the job is marked `claimed` — so a
            # malformed job becomes permanently STUCK rather than failed: attempts=0, no error, no
            # retry. ⚠ It is the pinned weights and D-047 explicitly keeps it authoritative here,
            # unlike dtype/chunk_size which are resolved from TIER_RECIPE at claim time.
            "model_id": MODEL_ID,
            "model_revision": MODEL_REVISION,
            "source": r["boundary_method"],
            "ecd_start": start,
            "ecd_end": end,
        },
    }


def assert_claimable(payload: dict[str, Any]) -> FoldSpec:
    """⚠⚠ BUILD THE CONSUMER'S OBJECT BEFORE WRITING THE ROW.

    The first tranche-1 ingest wrote ten rows whose `inference_settings` lacked `model_revision`.
    The dry run passed — it validated slices and invariants, **but never called the contract it was
    writing for**. `/claim` then raised `KeyError` *after* marking each job `claimed`, leaving ten
    jobs permanently stuck: `attempts=0`, no error, nothing retryable.

    ⚠ **A dry run that does not exercise the consumer is not a dry run.** This mirrors
    `app/artifacts.py:build_fold_spec` field for field, so a missing key raises HERE, before any
    write. `test_census_ingest_satisfies_the_claim_contract` pins the mirror against drift.
    """
    meta, s = payload["meta"], payload["inference_settings"]
    tier = meta.get("tier")
    if tier not in TIER_RECIPE:
        raise SystemExit(f"⚠ {payload['accession']}: meta['tier']={tier!r} resolves no recipe "
                         f"(D-047). Known: {sorted(TIER_RECIPE)}")
    recipe = TIER_RECIPE[tier]
    try:
        return FoldSpec(job_id=0, sequence=meta["sequence"], model_revision=s["model_revision"],
                        dtype=recipe["dtype"], chunk_size=recipe["chunk_size"],
                        source=s["source"], ecd_start=s["ecd_start"], ecd_end=s["ecd_end"])
    except KeyError as e:
        raise SystemExit(
            f"⚠⚠ {payload['accession']}: /claim would raise KeyError({e}) AFTER marking the job "
            f"claimed, stranding it. Refusing to write.") from e


def run(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(prog="python scripts/census_ingest.py", description=__doc__)
    ap.add_argument("--tranche", type=int, required=True)
    ap.add_argument("--dry-run", action="store_true",
                    help="⚠ compose and CHECK everything, write nothing")
    ap.add_argument("--limit", type=int, default=None, help="smoke runs only")
    args = ap.parse_args(argv)

    rows = manifest_rows(args.tranche)
    if args.limit:
        rows = rows[: args.limit]

    payloads = [build_row(r) for r in rows]      # ⚠ every slice checked before any write

    # ⚠⚠ D-085: a span the model cannot TOKENISE is excluded as a NAMED CATEGORY, before any
    # write. Left unguarded it reaches the GPU and fails as "Unable to create tensor … excessive
    # nesting" — a message about batching that names nothing real (F-033). ⚠ It is EXCLUDED, not
    # fatal: one untokenisable row must not stop a tranche of 500 that are fine.
    untok = [(p, untokenisable_residues(p["meta"]["sequence"])) for p in payloads]
    blocked = [(p, bad) for p, bad in untok if bad]
    payloads = [p for p, bad in untok if not bad]
    for p, bad in blocked:
        print(f"  ⚠ EXCLUDED_UNTOKENISABLE_RESIDUE | {p['accession']} | "
              f"residue(s) {bad} absent from the ESM vocabulary — cannot be tokenised, so the "
              f"fold is not attempted rather than failing as a tensor-shape error (F-033, D-085)")
    # ⚠ Stated even at zero, so "none were blocked" and "the check never ran" differ in the output.
    print(f"  ⚠ untokenisable spans excluded | {len(blocked)}")

    specs = [assert_claimable(p) for p in payloads]   # ⚠ and the CLAIM CONTRACT, before any write

    spans = [p["meta"]["span_aa"] for p in payloads]
    print(f"tranche {args.tranche} | manifest rows {len(payloads)}")
    print(f"  span range | {min(spans)}-{max(spans)} aa")
    print(f"  tiers      | {dict(Counter(p['tier'] for p in payloads))}")
    print(f"  ⚠ every sliced length equals its span_aa | "
          f"{all(len(p['meta']['sequence']) == p['meta']['span_aa'] for p in payloads)}")
    print(f"  ⚠ any tranche 0 | {sum(1 for p in payloads if p['tranche'] == COHORT_TRANCHE)}")
    print(f"  ⚠ every payload builds a valid FoldSpec | {len(specs)}/{len(payloads)} | "
          f"dtype {specs[0].dtype} chunk {specs[0].chunk_size} rev {specs[0].model_revision[:12]}…")

    import os
    import sqlalchemy as sa
    from sqlalchemy import func, select
    from sqlalchemy.orm import Session

    from db.models import JobRecord, ProteinAnalysis, RankingResult, RankingRun, TargetScore

    url = os.environ.get("DATABASE_URL")
    if not url:
        raise SystemExit("⚠ no DATABASE_URL — stop and report")
    engine = sa.create_engine(url, connect_args={"connect_timeout": 10})

    def snapshot(s: Session) -> dict[str, Any]:
        """⚠ The invariants that must not move, read as a composition."""
        by_tr = dict(s.execute(select(ProteinAnalysis.cohort_tranche, func.count())
                               .group_by(ProteinAnalysis.cohort_tranche)).all())
        return {
            "protein_analyses": s.scalar(select(func.count()).select_from(ProteinAnalysis)),
            "by_tranche": {str(k): v for k, v in sorted(by_tr.items(), key=lambda kv: (kv[0] is None, kv[0]))},
            "jobs": s.scalar(select(func.count()).select_from(JobRecord)),
            "ranking_runs": s.scalar(select(func.count()).select_from(RankingRun)),
            "ranking_results": s.scalar(select(func.count()).select_from(RankingResult)),
            "target_scores": s.scalar(select(func.count()).select_from(TargetScore)),
        }

    with Session(engine) as s:
        before = snapshot(s)
        print(f"\nBEFORE | {json.dumps(before)}")

        existing = set(s.scalars(
            select(ProteinAnalysis.input_value)
            .where(ProteinAnalysis.cohort_tranche == args.tranche)).all())
        todo = [p for p in payloads if p["accession"] not in existing]
        print(f"already present in tranche {args.tranche} | {len(existing)} | to write | {len(todo)}")

        if args.dry_run:
            print("\n⚠ DRY RUN — nothing written.")
            return 0

        for p in todo:
            analysis = ProteinAnalysis(
                input_type="uniprot",
                input_value=p["accession"],
                structure_source="esmfold_local",
                # ⚠⚠ NULL, and it is the structural bar on scoring: fit_scorer selects BY run id.
                ranking_run_id=None,
                cohort_tranche=p["tranche"],
                meta=p["meta"],
            )
            s.add(analysis)
            s.flush()
            # ⚠ `tier` on the JOB (F-035), not only in the analysis meta. `claim()` filters
            # on it inside one atomic UPDATE, and reaching through a JSON column there would need
            # dialect-split SQL in the one statement that must not have two versions.
            s.add(JobRecord(analysis_id=analysis.id, status="pending", tier=p["tier"],
                            inference_settings={**p["inference_settings"],
                                                "model_id": "facebook/esmfold_v1"}))
        s.commit()

        after = snapshot(s)
        print(f"AFTER  | {json.dumps(after)}")

        # ⚠ The falsifiers, checked against the pre-registration rather than eyeballed.
        problems = []
        if after["by_tranche"].get("0") != before["by_tranche"].get("0"):
            problems.append("the tranche-0 cohort count MOVED")
        if after["by_tranche"].get("None"):
            problems.append(f"{after['by_tranche']['None']} rows have a NULL cohort_tranche")
        for k in ("ranking_runs", "ranking_results", "target_scores"):
            if after[k] != before[k]:
                problems.append(f"{k} moved {before[k]} -> {after[k]} — nothing here scores")
        n_run = s.scalar(select(func.count()).select_from(ProteinAnalysis)
                         .where(ProteinAnalysis.cohort_tranche == args.tranche)
                         .where(ProteinAnalysis.ranking_run_id.is_not(None)))
        if n_run:
            problems.append(f"{n_run} census rows carry a non-NULL ranking_run_id")
        if problems:
            print("\n⚠⚠ STOP AND REPORT:")
            for x in problems:
                print(f"  · {x}")
            return 1
        print("\n✅ every pre-registered invariant held")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
