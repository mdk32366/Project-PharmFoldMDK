#!/usr/bin/env python3
"""D-149 — load the committed SEER burden artefact into `cancer_burden_runs` / `cancer_burden_stat`.

⚠⚠ **THIS SCRIPT CANNOT REACH THE NETWORK AND THAT IS THE POINT.** It imports no HTTP client and
names no host: the only input is `data/burden/seer_us_cancer_burden.v1.csv`, verified against the
sha256 in its provenance sidecar before a row is written. `scripts/fetch_seer_burden.py` is the
network half, and re-running *it* is a **new ingest of a different release** rather than a refresh.
A serving host therefore cannot silently re-derive a figure this repository was never reviewed with.

⚠⚠ **IT COMPUTES NO BURDEN NUMBER.** Every rate, every confidence interval and every count is
carried through from the source unchanged — nothing is summed across sexes, nothing is imputed,
nothing is rescaled. The only derived fields are two boolean FLAGS (`is_context_row`,
`is_primary_sex_stratum`) whose rule is in `core.cancer_burden` and is shared with the tests.

⚠ **IT WRITES NO ACCESSION, GENE OR SCORE, AND IT TOUCHES NO SCORING TABLE.** `ranking_runs`,
`target_scores`, `ranking_results`, `census_structural_runs`, `census_structural_scores`,
`protein_analyses` and the two clinical tables are neither read nor written. `D-093` decision 1:
burden is a property of a **disease**.

Usage:
    python scripts/seer_cancer_burden.py                 # dry run: parse, verify, summarise
    python scripts/seer_cancer_burden.py --load          # persist one `valid` run
    python scripts/seer_cancer_burden.py --top 15        # dry run + the top 15 by deaths
    python scripts/seer_cancer_burden.py --prune-superseded
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import pathlib
import sys
from typing import Any

REPO = pathlib.Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from core.cancer_burden import (  # noqa: E402
    ATTRIBUTION,
    GEOGRAPHY_US,
    RUN_INVALID,
    RUN_SUPERSEDED,
    RUN_VALID,
    SEX_VALUES,
    STATISTICS,
    US_ONLY_DISCLAIMER,
    is_primary_sex_stratum,
)
from core.source_pin import IngestRefused, verify_source  # noqa: E402

BURDEN_DIR = REPO / "data" / "burden"
ARTEFACT = BURDEN_DIR / "seer_us_cancer_burden.v1.csv"
PROVENANCE = BURDEN_DIR / "seer_us_cancer_burden.provenance.json"

CONTEXT_SITE_ID = 1  # All Cancer Sites Combined — a denominator, never a ranked site.


def load_provenance(path: pathlib.Path = PROVENANCE) -> dict[str, Any]:
    if not path.exists():
        raise IngestRefused(
            f"provenance sidecar {path} is ABSENT. The artefact's sha256, its release pin and its "
            f"attribution live there; loading the CSV without it would persist figures with no "
            f"recorded release. An absent input is not an empty one.")
    return json.loads(path.read_text(encoding="utf-8"))


def read_rows(artefact: pathlib.Path = ARTEFACT,
              provenance: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    """Parse the committed artefact, hash-verified, and refuse on anything it cannot name.

    ⚠⚠ EVERY REFUSAL HERE IS A HARD ERROR, NEVER A SKIPPED ROW. A loader that dropped a row it
    could not parse would produce a shorter table that looks complete — and *"an absent value
    recorded as nothing"* is the defect `F-018` and `F-020` are both about.
    """
    prov = provenance if provenance is not None else load_provenance()
    verify_source(artefact, prov["artefact_sha256"])

    with artefact.open(encoding="utf-8", newline="") as fh:
        raw = list(csv.DictReader(fh))

    expected = int(prov["artefact_rows"])
    if len(raw) != expected:
        raise IngestRefused(
            f"{artefact} holds {len(raw)} rows; its provenance records {expected}. The hash "
            f"matched, so this is a provenance/artefact disagreement rather than a changed file — "
            f"resolve it before loading.")

    # ⚠ Which (statistic, site) pairs publish a `both` row decides `is_primary_sex_stratum`, so it
    # is measured across the whole file BEFORE any row is projected. Computing it per-row would
    # make the flag depend on file order.
    has_both: set[tuple[str, int]] = set()
    for r in raw:
        if r["sex"] == "both":
            has_both.add((r["statistic"], int(r["seer_site_id"])))

    rows: list[dict[str, Any]] = []
    for line, r in enumerate(raw, start=2):
        statistic = r["statistic"]
        if statistic not in STATISTICS:
            raise IngestRefused(
                f"{artefact}:{line} carries statistic {statistic!r}, which is not in the "
                f"vocabulary {STATISTICS}. Refusing rather than persisting a row no consumer can "
                f"interpret.")
        sex = r["sex"]
        if sex not in SEX_VALUES:
            raise IngestRefused(
                f"{artefact}:{line} carries sex {sex!r}, not in {SEX_VALUES}.")
        site_id = int(r["seer_site_id"])
        for required in ("period", "count_population", "rate_basis", "site_label",
                         "recode_group"):
            if not r[required].strip():
                raise IngestRefused(
                    f"{artefact}:{line} has an EMPTY {required}. ⚠ `period` and "
                    f"`count_population` are what keep a national mortality count from being read "
                    f"beside a registry incidence count; a row missing either is unservable, not "
                    f"merely incomplete.")
        substituted = json.loads(r["requested_sex_was_substituted"] or "[]")
        rows.append({
            "statistic": statistic,
            "seer_site_id": site_id,
            "site_label": r["site_label"],
            "recode_group": r["recode_group"],
            "sex": sex,
            "rate_per_100k": float(r["rate_per_100k"]),
            "rate_se": float(r["rate_se"]) if r["rate_se"] else None,
            "rate_lower_ci": float(r["rate_lower_ci"]) if r["rate_lower_ci"] else None,
            "rate_upper_ci": float(r["rate_upper_ci"]) if r["rate_upper_ci"] else None,
            "observed_count": int(r["observed_count"]),
            "count_population": r["count_population"],
            "period": r["period"],
            "rate_basis": r["rate_basis"],
            "sex_substituted": bool(substituted),
            "is_context_row": site_id == CONTEXT_SITE_ID,
            "is_primary_sex_stratum": is_primary_sex_stratum(
                sex=sex, site_has_both_row=(statistic, site_id) in has_both),
        })
    return rows


def summarise(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """⚠ The BREAKDOWN, not the total (method-note item 2). A single `n_stats` would not have shown
    that six mortality rows carry a different period from the other eighty-one."""
    by_statistic = {s: sum(1 for r in rows if r["statistic"] == s) for s in STATISTICS}
    periods: dict[str, list[str]] = {}
    for s in STATISTICS:
        periods[s] = sorted({r["period"] for r in rows if r["statistic"] == s})
    period_rows = {
        f"{r['statistic']}:{r['period']}": 0 for r in rows
    }
    for r in rows:
        period_rows[f"{r['statistic']}:{r['period']}"] += 1
    return {
        "n_rows": len(rows),
        "n_sites": len({r["seer_site_id"] for r in rows}),
        "n_ranked_sites": len({r["seer_site_id"] for r in rows if not r["is_context_row"]}),
        "rows_by_statistic": by_statistic,
        "periods_by_statistic": periods,
        "rows_by_statistic_and_period": dict(sorted(period_rows.items())),
        "rows_by_count_population": {
            p: sum(1 for r in rows if r["count_population"] == p)
            for p in sorted({r["count_population"] for r in rows})
        },
        "rows_by_sex": {
            s: sum(1 for r in rows if r["sex"] == s) for s in SEX_VALUES
        },
        # ⚠⚠ THE NUMBER THAT WOULD HAVE BEEN A SILENT 72x ERROR. It is counted into the run row so
        # a reader of the database can see the substitution happened, not only a reader of the log.
        "n_sex_substituted": sum(1 for r in rows if r["sex_substituted"]),
        "sites_with_sex_substitution": sorted({
            r["site_label"] for r in rows if r["sex_substituted"]
        }),
        "n_primary_sex_stratum": sum(1 for r in rows if r["is_primary_sex_stratum"]),
        "n_context_rows": sum(1 for r in rows if r["is_context_row"]),
    }


def build_engine():
    from sqlalchemy import create_engine

    from db.dburl import normalize_db_url

    url = os.environ.get("DATABASE_URL")
    if not url:
        raise IngestRefused(
            "DATABASE_URL is not set. The loader refuses loudly rather than falling back to a "
            "local file — a quiet default is how a load lands somewhere nobody looks.")
    return create_engine(normalize_db_url(url), future=True)


def persist(engine, rows: list[dict[str, Any]], *,
            provenance: dict[str, Any] | None = None) -> int:
    """Insert one `valid` run + its figures, superseding every previously `valid` run.

    ⚠⚠ ONE TRANSACTION, on `census_structural_rank.persist`'s reasoning: the supersede and the
    insert commit together or not at all. A crash between them would leave **zero** valid runs and
    the route would serve `not_run` — a surface that lost a result it still has.
    """
    from sqlalchemy import select
    from sqlalchemy.orm import Session

    from db.models import CancerBurdenRun, CancerBurdenStat

    prov = provenance if provenance is not None else load_provenance()
    counts = summarise(rows)

    with Session(engine) as session:
        run = CancerBurdenRun(
            source_file=str(ARTEFACT.relative_to(REPO)),
            source_sha256=prov["artefact_sha256"],
            release=prov["release"],
            release_updated=prov["release_application_updated"],
            geography=GEOGRAPHY_US,
            # ⚠ from `core.cancer_burden`, not from the provenance file: the disclaimer the API
            # serves and the disclaimer the tests assert must be ONE string, and a second copy in
            # a data file is a second source that drifts.
            geography_disclaimer=US_ONLY_DISCLAIMER,
            attribution=ATTRIBUTION,
            run_status=RUN_VALID,
            status_detail=None,
            n_sites=counts["n_sites"],
            n_stats=counts["n_rows"],
            component_counts=counts,
        )
        session.add(run)
        session.flush()

        # ⚠ AFTER the flush, so the supersede note can NAME the run that replaced them. A note
        # reading "superseded" alone leaves a reader no way to find what replaced it.
        for prior in session.scalars(
            select(CancerBurdenRun)
            .where(CancerBurdenRun.run_status == RUN_VALID)
            .where(CancerBurdenRun.id != run.id)
        ).all():
            prior.run_status = RUN_SUPERSEDED
            prior.status_detail = f"superseded by cancer_burden_runs id={run.id} (D-149)"

        for row in rows:
            session.add(CancerBurdenStat(run_id=run.id, **row))
        session.commit()
        return run.id


def prune_superseded(engine) -> tuple[int, int]:
    """Delete `superseded` runs and their figures. Returns `(runs, stats)` deleted.

    ⚠ EXPLICIT, NEVER A SIDE EFFECT OF A LOAD — `census_structural_rank.prune_superseded`'s rule.
    A replaced run is the only record of what the surface said yesterday.
    """
    from sqlalchemy import delete, select
    from sqlalchemy.orm import Session

    from db.models import CancerBurdenRun, CancerBurdenStat

    with Session(engine) as session:
        ids = list(session.scalars(
            select(CancerBurdenRun.id).where(CancerBurdenRun.run_status == RUN_SUPERSEDED)
        ).all())
        if not ids:
            return (0, 0)
        n_stats = session.execute(
            delete(CancerBurdenStat).where(CancerBurdenStat.run_id.in_(ids))
        ).rowcount or 0
        n_runs = session.execute(
            delete(CancerBurdenRun).where(CancerBurdenRun.id.in_(ids))
        ).rowcount or 0
        session.commit()
        return (n_runs, n_stats)


def _print_top(rows: list[dict[str, Any]], n: int) -> None:
    ranked = [r for r in rows
              if r["statistic"] == "mortality" and r["is_primary_sex_stratum"]
              and not r["is_context_row"]]
    ranked.sort(key=lambda r: -r["observed_count"])
    print(f"\nTop {n} by US cancer DEATHS ({US_ONLY_DISCLAIMER})")
    for r in ranked[:n]:
        label = r["site_label"] if r["sex"] == "both" else f"{r['site_label']} ({r['sex']})"
        print(f"  {r['observed_count']:>9,}  {r['rate_per_100k']:>8.2f}/100k  "
              f"{r['period']}  {label}")
    ctx = [r for r in rows if r["is_context_row"] and r["statistic"] == "mortality"
           and r["sex"] == "both"]
    if ctx:
        c = ctx[0]
        print(f"  {'—' * 9}  context (NOT ranked beside the above): "
              f"{c['site_label']} {c['observed_count']:,} deaths, {c['rate_per_100k']:.2f}/100k")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--load", action="store_true",
                    help="persist one `valid` run; without it this is a dry run")
    ap.add_argument("--prune-superseded", action="store_true",
                    help="delete superseded runs and their figures (explicit, never automatic)")
    ap.add_argument("--top", type=int, default=0, help="print the top N by deaths")
    ap.add_argument("--json", action="store_true", help="print the summary as JSON")
    args = ap.parse_args(argv)

    prov = load_provenance()
    rows = read_rows(provenance=prov)
    counts = summarise(rows)

    if args.json:
        json.dump(counts, sys.stdout, indent=2)
        print()
    else:
        print(f"release      {prov['release']} (application updated "
              f"{prov['release_application_updated']})")
        print(f"artefact     {ARTEFACT.relative_to(REPO)}")
        print(f"sha256       {prov['artefact_sha256']}")
        print(f"geography    {prov['geography']}")
        print(f"rows         {counts['n_rows']} over {counts['n_sites']} sites "
              f"({counts['n_ranked_sites']} ranked + {counts['n_context_rows']} context rows)")
        print(f"periods      {counts['rows_by_statistic_and_period']}")
        print(f"⚠ sex substituted by the source on {counts['n_sex_substituted']} rows: "
              f"{', '.join(counts['sites_with_sex_substitution'])}")

    if args.top:
        _print_top(rows, args.top)

    if args.prune_superseded:
        engine = build_engine()
        n_runs, n_stats = prune_superseded(engine)
        print(f"pruned {n_runs} superseded run(s), {n_stats} figure(s)")

    if args.load:
        engine = build_engine()
        run_id = persist(engine, rows, provenance=prov)
        print(f"loaded cancer_burden_runs id={run_id} with {len(rows)} figures")
    elif not args.prune_superseded:
        print("\nDRY RUN — nothing written. Re-run with --load to persist.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except IngestRefused as exc:
        print(f"INGEST REFUSED: {exc}", file=sys.stderr)
        sys.exit(2)
