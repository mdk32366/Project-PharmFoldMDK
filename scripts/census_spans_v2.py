#!/usr/bin/env python3
"""Census Task 3 — pull ECD spans for the census, per protein, with per-record provenance.

    python scripts/census_spans_v2.py --roster data/census/census_roster.csv \
        --class surface --out data/census/spans_surface.csv --cache data/census/spancache

⚠ READS THE ROSTER, NOT THE MAP. The fetch key is `census_accession` at **per-protein** grain
(SPEC-2026-08-05 §3.2). Fetching the map's `uniprot_accession` at per-identifier grain would fetch
**HLA-B thirty-five times** and weight one family **83-fold** inside the confidence distribution
that is the census's headline use.

⚠ EVERY RECORD CARRIES ITS OWN FETCH DATE, AND THAT IS A RULE FIXED BEFORE THE PULL.
A rate-limited pull of 2,807 proteins may not finish in one sitting. If it halts and resumes
tomorrow, a single "run date" stamped across records fetched on two days is **a plausible, dated,
provenanced, wrong artifact** — the attention-proxy snapshot's shape, in a different file. So:

  · every row records `fetched_on` and the `uniprot_release` read at that moment
  · the header records FIRST and LAST fetch date, and the release at each
  · ⚠ if they differ, BOTH are reported and neither is collapsed
  · a single as-of date is emitted ONLY if first and last agree

⚠ `no_topology` IS A CATEGORY, NEVER A LENGTH, NEVER `0`. A protein with no sliceable ECD is not a
free fold; it is a measurement that did not happen. And it requires a **successful fetch** — a row
that was never fetched cannot be `no_topology`, which is why `fetch_failed` is its own category.

⚠ THE ANNEX IS A SEPARATE FILE (F-011) AND THE 2,793 UNCLASSIFIED ARE NOT PULLED AT ALL. They are
excluded by a *different mechanism* (F-016), and pulling them alongside invites their later
recruitment into F-011's thesis.

⚠ NO PROPORTION OF THE 82 IS MULTIPLIED BY ANYTHING. `core/census.py` carries that refusal and a
test asserts no ratio-and-total path exists. Counts come from spans actually measured, or they do
not come.

⚠ A PERMISSION DENIAL IS STOP-AND-REPORT — never a retry, never a workaround. The disk cache makes
a halted pull resumable; a pull that routed around a denial is not.
"""

from __future__ import annotations

import argparse
import csv
import datetime as _dt
import json
import sys
import time
from pathlib import Path
from typing import Any, Optional

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from scripts.ecd_lengths import fetch_cached, parse  # noqa: E402

OUT_COLUMNS = ("census_accession", "census_class", "census_identity_status", "source_identifiers",
               "span_aa", "no_topology_reason", "fetch_failed", "fetch_error",
               "fetched_on", "uniprot_release")


class UnclassifiedPullRefused(RuntimeError):
    """⚠ The 2,793 unclassified are excluded by a DIFFERENT mechanism (F-016) and are not pulled.

    Pulling them alongside the annex invites their later recruitment into F-011's thesis — F-011 is
    about how the negative class is *defined*; the unclassified are about how a class assignment is
    *keyed*. Adjacent, not the same, and P-002's named failure mode is exactly that promotion.
    """


def uniprot_release(data: dict) -> str:
    """The release the entry was served under. ⚠ Absent is a CATEGORY, never guessed."""
    v = (data or {}).get("entryAudit", {}).get("lastSequenceUpdateDate")
    return str(v) if v else "release_not_reported"


def span_row(entry: dict[str, Any], data: Optional[dict], error: Optional[str],
             *, fetched_on: str) -> dict[str, Any]:
    """One output row. ⚠ Absence is always a named category, never a number."""
    base = {
        "census_accession": entry["census_accession"],
        "census_class": entry["census_class"],
        "census_identity_status": entry["census_identity_status"],
        "source_identifiers": entry["source_identifiers"],
        "span_aa": "",
        "no_topology_reason": "",
        "fetch_failed": "false",
        "fetch_error": "",
        "fetched_on": fetched_on,
        "uniprot_release": "",
    }
    if error is not None:
        # ⚠ A fetch failure is NOT an identity failure and NOT no_topology. The identity is intact;
        # the request is what failed, and `no_topology` requires a successful fetch.
        base.update(fetch_failed="true", fetch_error=error[:160])
        return base
    if data is None:
        # ⚠ NEVER FETCHED — an ineligible row. It does not enter the parse path at all, because
        # `no_topology` is a claim about the PROTEIN and can only be made after looking. The caller
        # supplies the reason; this returns a row with no span and no topology claim.
        return base
    base["uniprot_release"] = uniprot_release(data)
    span = parse(entry["census_accession"], "", data).largest_span
    if span is None or not isinstance(span, int) or span <= 0:
        base["no_topology_reason"] = "no sliceable ECD span in the fetched entry"
    else:
        base["span_aa"] = span
    return base


def read_roster(path: Path, census_class: str) -> list[dict[str, str]]:
    """Roster rows of one class that are fetch-eligible. ⚠ Refuses `unclassified` outright."""
    if census_class == "unclassified":
        raise UnclassifiedPullRefused(
            "the 2,793 unclassified are NOT pulled — a different exclusion mechanism (F-016); "
            "pulling them alongside invites their recruitment into F-011's thesis")
    with path.open(encoding="utf-8", newline="") as fh:
        rows = [r for r in csv.DictReader(fh) if r["census_class"] == census_class]
    if not rows:
        raise ValueError(f"roster has no rows of class {census_class!r} — refusing a silent no-op")
    return rows


def pull(rows: list[dict[str, str]], cache: Optional[str], *, sleep_s: float = 0.34,
         today: Optional[str] = None, progress_every: int = 100) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for i, entry in enumerate(rows, 1):
        stamp = today or _dt.date.today().isoformat()   # ⚠ per RECORD, not per run
        if entry["fetch_eligible"] != "true":
            r = span_row(entry, None, None, fetched_on="")
            r["no_topology_reason"] = f"not fetched: {entry['fetch_ineligible_reason']}"
            out.append(r)
            continue
        try:
            data = fetch_cached(entry["census_accession"], cache)
            out.append(span_row(entry, data, None, fetched_on=stamp))
        except Exception as e:                                        # noqa: BLE001
            out.append(span_row(entry, None, f"{type(e).__name__}: {e}", fetched_on=stamp))
        if sleep_s:
            time.sleep(sleep_s)
        if i % progress_every == 0:
            print(f"  {i}/{len(rows)}", file=sys.stderr, flush=True)
    return out


def provenance(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """⚠ First and last fetch date, both reported. A single as-of date ONLY if they agree."""
    dates = sorted({r["fetched_on"] for r in rows if r["fetched_on"]})
    releases = sorted({r["uniprot_release"] for r in rows if r["uniprot_release"]})
    single = dates[0] if len(dates) == 1 else None
    return {
        "first_fetched_on": dates[0] if dates else "",
        "last_fetched_on": dates[-1] if dates else "",
        "as_of_date": single or "",
        "spans_multiple_days": len(dates) > 1,
        "uniprot_releases_seen": releases,
        "n_fetched": sum(1 for r in rows if r["fetched_on"]),
    }


def band_split(rows: list[dict[str, Any]]) -> dict[str, int]:
    """Counted OFF THE FILE. ⚠ No proportion of the 82 is multiplied by anything."""
    from core.census import categorise
    counts: dict[str, int] = {}
    for r in rows:
        if r["fetch_failed"] == "true":
            key = "fetch_failed"
        elif not r["fetched_on"]:
            key = r["census_identity_status"]            # never fetched: status decides
        else:
            span = int(r["span_aa"]) if str(r["span_aa"]).strip() else None
            key = categorise({"span_aa": span, "id_status": r["census_identity_status"]})
        counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items()))


def run(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(prog="python scripts/census_spans_v2.py", description=__doc__)
    ap.add_argument("--roster", default="data/census/census_roster.csv")
    ap.add_argument("--class", dest="census_class", required=True,
                    choices=["surface", "non_surface"],
                    help="⚠ `unclassified` is deliberately absent — F-016")
    ap.add_argument("--out", required=True)
    ap.add_argument("--cache", default="data/census/spancache")
    ap.add_argument("--limit", type=int, default=None, help="smoke runs only")
    ap.add_argument("--sleep", type=float, default=0.34, help="rate limit, seconds between calls")
    args = ap.parse_args(argv)

    rows = read_roster(Path(args.roster), args.census_class)
    if args.limit:
        rows = rows[: args.limit]
    print(f"roster class={args.census_class} rows={len(rows)} "
          f"fetch_eligible={sum(1 for r in rows if r['fetch_eligible'] == 'true')}", file=sys.stderr)

    out_rows = pull(rows, args.cache, sleep_s=args.sleep)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(OUT_COLUMNS))
        w.writeheader()
        w.writerows(out_rows)

    prov = provenance(out_rows)
    (out.parent / f"{out.stem}.provenance.json").write_text(
        json.dumps({**prov, "class": args.census_class, "rows": len(out_rows),
                    "band_split": band_split(out_rows)}, indent=2), encoding="utf-8")
    print(f"wrote {out} | {len(out_rows)} rows")
    print(f"provenance | {prov}")
    print(f"band split (off the file) | {band_split(out_rows)}")
    if prov["spans_multiple_days"]:
        print("⚠ THIS PULL SPANS MULTIPLE DAYS. first and last are both reported; no single "
              "as_of_date is emitted.")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
