"""scripts/census_structural_rank.py — compute and persist the census STRUCTURAL rank (`D-144`).

⚠⚠ **`STRUCTURAL_ONLY — not HPA-weighted; not ADC-ready`.** The formula is
`score_membrane × score_ecd × score_model` and lives in `core/census_structural.py`; this file
computes nothing of its own. It reads the population from a **committed file**, reads the fold
half from the **database**, multiplies, ranks, and writes two tables.

⚠⚠ **IT DOES NOT TOUCH THE COHORT-82 LEARNED SCORER.** No `ranking_runs`, no `target_scores`,
no `ranking_results`, no `run_kind`, no `core.scorer` import — asserted by
`tests/test_d144_census_structural_rank.py`, not merely intended. `/api/ranking` serves the
`D-041` / `D-060` pre-registered result and is unaffected by every run this script writes.

═══════════════════════════════════════════════════════════════════════════════
WHERE EACH HALF COMES FROM, AND WHY THEY COME FROM DIFFERENT PLACES
═══════════════════════════════════════════════════════════════════════════════

**The population is a FILE** — `data/census/census_manifest.v7.csv`, 3,467 proteins, hashed
into the run row. `D-024`: a denominator read out of `protein_analyses` is a function of how
much folding has happened, so tranche 5 (776 rows, largely unfolded) would quietly leave the
census and the list would flatter itself by shrinking.

**The fold half is the DATABASE** — `protein_analyses` joined on `input_value = accession`
with `cohort_tranche > 0`, which is why this is a load-time computation rather than a CSV
import: a fold that lands for a tranche-5 protein tomorrow is picked up by the next run with
no change to this script and no re-export from anyone's laptop.

⚠ **ONE representative rule, not a second one.** `app.reads.choose_census_representative` is
the same function `/api/census` and `/api/census/{id}` use — assembled parent wins, a tile is
never the protein (`D-118`), a spare tile never wins (`D-134`). A private copy here would be
free to disagree with the census page this rank is about.

═══════════════════════════════════════════════════════════════════════════════
IDEMPOTENT REPLACE, AND WHAT "REPLACE" IS ALLOWED TO MEAN
═══════════════════════════════════════════════════════════════════════════════

A `--load` marks every existing `valid` run **`superseded`** (naming the new run id in
`status_detail`) and inserts one new `valid` run with its 3,467 rows. So after any number of
runs there is **exactly one** `valid` run, which is what the read route serves.

⚠ **Superseded runs are KEPT, not deleted.** A derived table is cheap and a replaced run is the
only evidence of what the surface said yesterday. `--prune-superseded` deletes them
**explicitly**, on request, in the open — never as a side effect of a load.

Usage:
    python scripts/census_structural_rank.py                      # dry run: compute + summary, no write
    python scripts/census_structural_rank.py --top 25             # ...and print the head of the rank
    python scripts/census_structural_rank.py --load               # persist (needs DATABASE_URL)
    python scripts/census_structural_rank.py --load --prune-superseded
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import sys
from collections import Counter
from typing import Any, Optional

REPO = pathlib.Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from core.census_structural import (  # noqa: E402
    CENSUS_MANIFEST,
    DISCLAIMER,
    STRUCTURAL_ONLY,
    census_population,
    formula_version,
    rank_rows,
    reference_accessions,
    structural_score,
)
from core.source_pin import sha256_of  # noqa: E402
from core.span_definition import V2_RULED_VOCABULARY  # noqa: E402

#: The three `run_status` values. ⚠ A vocabulary in code, never a database CHECK — the 0011
#: precedent: a constraint would be a second copy of the rule and the two would drift.
RUN_VALID = "valid"
RUN_SUPERSEDED = "superseded"
RUN_INVALID = "invalid"
RUN_STATUSES = (RUN_VALID, RUN_SUPERSEDED, RUN_INVALID)


def build_engine():
    """A real engine from `DATABASE_URL`, normalized to the psycopg-3 scheme (`D-012`) the same
    way `scripts/extract_features.py` and `core/enqueue.py` do. Loud `KeyError` when unset — a
    loader that quietly does nothing without a credential is the shape `core/source_pin.py`
    records as *"you probably do not have a database"* being mistaken for a safety property."""
    from sqlalchemy import create_engine

    from db.dburl import normalize_db_url

    return create_engine(normalize_db_url(os.environ["DATABASE_URL"]), future=True)


# ── the fold half: census rows in `protein_analyses`, one representative each ──


def fold_facts(engine) -> dict[str, dict[str, Any]]:
    """`accession -> {analysis_id, has_fold, mean_plddt, structure_kind}` for every CENSUS row.

    ⚠ `cohort_tranche > 0` — the POSITIVE census form, never `!=`, which excludes a NULL-tranche
    row under three-valued logic and would make it invisible here exactly as it does on the read
    surfaces (`app/reads.py`).

    ⚠⚠ A `tiles_only` or `mucin` representative is **NOT a fold**: `STRUCTURE_KINDS_WITH_A_FOLD`
    is the census surface's own definition of folded, and inventing a looser one here would give
    `score_model = plddt/100` to a protein the census page reports as not folded.
    """
    from sqlalchemy import select
    from sqlalchemy.orm import Session

    from app.reads import (
        COHORT_TRANCHE,
        STRUCTURE_KINDS_WITH_A_FOLD,
        choose_census_representative,
    )
    from db.models import ProteinAnalysis

    with Session(engine) as session:
        rows = session.scalars(
            select(ProteinAnalysis)
            .where(ProteinAnalysis.cohort_tranche > COHORT_TRANCHE)
        ).all()

    grouped: dict[str, list[Any]] = {}
    for row in rows:
        acc = (row.input_value or "").strip().upper()
        if acc:
            grouped.setdefault(acc, []).append(row)

    facts: dict[str, dict[str, Any]] = {}
    for acc, group in grouped.items():
        picked = choose_census_representative(group)
        if picked is None:
            # ⚠ A census row exists and carries no usable structure. That is `no_fold`, stated,
            # not an absent key the caller has to interpret.
            facts[acc] = {"analysis_id": None, "has_fold": False,
                          "mean_plddt": None, "structure_kind": None}
            continue
        row, kind = picked
        has_fold = kind in STRUCTURE_KINDS_WITH_A_FOLD and bool(row.pdb_path)
        facts[acc] = {
            "analysis_id": row.id,
            "has_fold": has_fold,
            # ⚠ read as stored, never recomputed (the `protein_features.mean_plddt` rule,
            # D-058 dec 3), and left NULL when the fold carries none — F-042's case, which
            # `score_model` answers with 0.8 rather than with a fabricated confidence.
            "mean_plddt": row.mean_plddt if has_fold else None,
            "structure_kind": kind,
        }
    return facts


# ── compute ───────────────────────────────────────────────────────────────────


def compute_rows(
    fold_by_accession: dict[str, dict[str, Any]],
    *,
    manifest: Any = None,
) -> list[dict[str, Any]]:
    """The whole rank: every population row, scored, flagged, sunk and ranked.

    ⚠ A population row with **no** entry in `fold_by_accession` is `has_fold = False` — never
    skipped. 777 manifest proteins have never been folded and they are part of the census; a
    rank that quietly dropped them would be a rank of what we have already computed.
    """
    refs = reference_accessions()
    out: list[dict[str, Any]] = []
    for row in census_population(manifest):
        acc = row["accession"]
        fold = fold_by_accession.get(acc) or {}
        has_fold = bool(fold.get("has_fold"))
        mean_plddt = fold.get("mean_plddt") if has_fold else None
        is_reference = acc in refs
        try:
            scored = structural_score(
                row["census_class"], row["span_aa"],
                has_pdb=has_fold, mean_plddt=mean_plddt, is_reference=is_reference,
            )
        except Exception as exc:                                   # noqa: BLE001
            # ⚠⚠ NAMED AND RE-RAISED, NEVER SWALLOWED INTO A DEFAULT. A pLDDT this formula
            # cannot read is a data defect; scoring the row as unfolded would turn it into a
            # 0.3 that looks like a measurement (F-020's shape).
            raise SystemExit(
                f"⚠ refusing to persist a run: {acc} — {exc}"
            ) from exc
        out.append({
            "accession": acc,
            "gene": row["gene"],
            "census_class": row["census_class"],
            "tranche": row["tranche"],
            "span_aa": row["span_aa"],
            "score_membrane": scored.score_membrane,
            "score_ecd": scored.score_ecd,
            "score_model": scored.score_model,
            "structural_score": scored.structural_score,
            "has_fold": scored.has_fold,
            "mean_plddt": mean_plddt,
            "is_reference": is_reference,
            "flags": list(scored.flags),
            "analysis_id": fold.get("analysis_id"),
            "structure_kind": fold.get("structure_kind"),
        })
    return rank_rows(out)


def summarise(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """The denominators, and the BREAKDOWN beside every total (method-note item 2).

    ⚠ `n_candidates` EXCLUDES the reference sink. *"3,467 candidates"* would count twelve
    antigens that already have an ADC pointed at them as things to go after."""
    refs = [r for r in rows if r["is_reference"]]
    return {
        "n_population": len(rows),
        "n_candidates": len(rows) - len(refs),
        "n_reference": len(refs),
        "n_with_fold": sum(1 for r in rows if r["has_fold"]),
        "n_without_fold": sum(1 for r in rows if not r["has_fold"]),
        "by_census_class": dict(Counter(r["census_class"] or "unrecorded" for r in rows)),
        "by_tranche": {str(k): v for k, v in
                       sorted(Counter(r["tranche"] for r in rows).items(),
                              key=lambda kv: (kv[0] is None, kv[0]))},
        "by_flag": dict(Counter(f for r in rows for f in r["flags"])),
        "by_structure_kind": dict(Counter(r["structure_kind"] or "none" for r in rows)),
        "reference_accessions": sorted(r["accession"] for r in refs),
    }


# ── persist ───────────────────────────────────────────────────────────────────


def persist(engine, rows: list[dict[str, Any]], *, manifest: Any = None) -> int:
    """Insert one `valid` run + its rows, marking every previously `valid` run `superseded`.

    ⚠⚠ ONE TRANSACTION. The supersede and the insert commit together or not at all: a crash
    between them would leave **zero** valid runs and the route would serve `not_run` — a
    surface that lost a result it still has.

    Returns the new run id.
    """
    from sqlalchemy import select
    from sqlalchemy.orm import Session

    from db.models import CensusStructuralRun, CensusStructuralScore

    counts = summarise(rows)
    manifest_path = pathlib.Path(manifest or CENSUS_MANIFEST)

    with Session(engine) as session:
        run = CensusStructuralRun(
            formula_version=formula_version(),
            span_definition=V2_RULED_VOCABULARY,
            population_source=str(manifest_path.relative_to(REPO))
            if manifest_path.is_absolute() and str(manifest_path).startswith(str(REPO))
            else str(manifest_path),
            population_sha256=sha256_of(manifest_path) if manifest_path.exists() else "",
            run_status=RUN_VALID,
            status_detail=DISCLAIMER,
            n_candidates=counts["n_candidates"],
            n_reference=counts["n_reference"],
            n_with_fold=counts["n_with_fold"],
            n_without_fold=counts["n_without_fold"],
            component_counts=counts,
        )
        session.add(run)
        session.flush()

        # ⚠ AFTER the flush, so the message can name the run that replaced them. A supersede
        # note reading "superseded" and nothing else leaves a reader with no way to find what
        # replaced it.
        for prior in session.scalars(
            select(CensusStructuralRun)
            .where(CensusStructuralRun.run_status == RUN_VALID)
            .where(CensusStructuralRun.id != run.id)
        ).all():
            prior.run_status = RUN_SUPERSEDED
            prior.status_detail = f"superseded by census_structural_runs id={run.id} (D-144)"

        for row in rows:
            session.add(CensusStructuralScore(
                run_id=run.id,
                accession=row["accession"],
                gene=row["gene"],
                census_class=row["census_class"],
                tranche=row["tranche"],
                span_aa=row["span_aa"],
                score_membrane=row["score_membrane"],
                score_ecd=row["score_ecd"],
                score_model=row["score_model"],
                structural_score=row["structural_score"],
                rank=row["rank"],
                has_fold=row["has_fold"],
                mean_plddt=row["mean_plddt"],
                is_reference=row["is_reference"],
                flags=row["flags"],
                analysis_id=row["analysis_id"],
            ))
        session.commit()
        return run.id


def prune_superseded(engine) -> tuple[int, int]:
    """Delete `superseded` runs and their rows. Returns `(runs, scores)` deleted.

    ⚠ EXPLICIT, NEVER A SIDE EFFECT OF A LOAD. A replaced run is the only record of what the
    surface said yesterday, so removing it is a decision someone types."""
    from sqlalchemy import delete, select
    from sqlalchemy.orm import Session

    from db.models import CensusStructuralRun, CensusStructuralScore

    with Session(engine) as session:
        ids = list(session.scalars(
            select(CensusStructuralRun.id)
            .where(CensusStructuralRun.run_status == RUN_SUPERSEDED)
        ).all())
        if not ids:
            return (0, 0)
        scores = session.execute(
            delete(CensusStructuralScore).where(CensusStructuralScore.run_id.in_(ids))
        ).rowcount or 0
        runs = session.execute(
            delete(CensusStructuralRun).where(CensusStructuralRun.id.in_(ids))
        ).rowcount or 0
        session.commit()
        return (runs, scores)


# ── CLI ───────────────────────────────────────────────────────────────────────


def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--load", action="store_true",
                    help="persist a new VALID run and supersede the previous one "
                         "(needs DATABASE_URL). Without it this is a dry run that writes nothing.")
    ap.add_argument("--prune-superseded", action="store_true",
                    help="delete SUPERSEDED runs and their rows. Explicit; never implied by --load.")
    ap.add_argument("--top", type=int, default=0, help="print the first N ranked rows")
    ap.add_argument("--manifest", default=None, help="population CSV (default: the committed manifest)")
    ap.add_argument("--json", action="store_true", help="print the summary as JSON")
    args = ap.parse_args(argv)

    needs_db = args.load or args.prune_superseded
    facts: dict[str, dict[str, Any]] = {}
    engine = None
    if needs_db:
        engine = build_engine()
        facts = fold_facts(engine)
    else:
        # ⚠⚠ A DRY RUN WITHOUT A DATABASE STATES WHAT IT COULD NOT SEE, rather than printing a
        # rank that looks complete. Every protein reads as unfolded, so `score_model` is 0.3
        # everywhere and the ORDER IS NOT THE ORDER — said out loud below, not left to inference.
        url = os.environ.get("DATABASE_URL")
        if url:
            engine = build_engine()
            facts = fold_facts(engine)

    rows = compute_rows(facts, manifest=args.manifest)
    counts = summarise(rows)

    if args.json:
        print(json.dumps(counts, indent=2, sort_keys=True))
    else:
        print(STRUCTURAL_ONLY)
        print(f"formula_version {formula_version()}  span_definition {V2_RULED_VOCABULARY}")
        if not facts:
            print("⚠ NO FOLD FACTS READ (no DATABASE_URL). Every protein scores as unfolded "
                  "(score_model = 0.3), so this ordering is NOT the served ordering — it is the "
                  "membrane × ECD half only.")
        for key in ("n_population", "n_candidates", "n_reference", "n_with_fold", "n_without_fold"):
            print(f"  {key:16s} {counts[key]}")
        for key in ("by_census_class", "by_tranche", "by_flag", "by_structure_kind"):
            print(f"  {key:16s} {counts[key]}")
        print(f"  reference sink   {counts['reference_accessions']}")

    for row in rows[: max(0, args.top)]:
        print(f"  {row['rank']:5d}  {row['accession']:10s} {(row['gene'] or '?'):12s} "
              f"{row['structural_score']:.4f}  "
              f"m={row['score_membrane']:.1f} e={row['score_ecd']:.4f} f={row['score_model']:.4f}"
              f"{'  [REFERENCE]' if row['is_reference'] else ''}")

    if args.load:
        run_id = persist(engine, rows, manifest=args.manifest)
        print(f"✅ wrote census_structural_runs id={run_id} with {len(rows)} scores "
              f"(previous VALID runs marked superseded)")
    elif not args.prune_superseded:
        print("dry run — nothing written. Add --load (with DATABASE_URL) to persist.")

    if args.prune_superseded:
        runs, scores = prune_superseded(engine)
        print(f"pruned {runs} superseded run(s), {scores} score row(s)")
    return 0


if __name__ == "__main__":                                  # pragma: no cover
    raise SystemExit(main())
