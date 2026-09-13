#!/usr/bin/env python3
"""scripts/attention_control.py — D-075 Decision 3: the popularity-matched control.

D-065 tested the pLDDT-attention confound only **indirectly**, by removing features. This tests it
**directly**: does the structural ranking still enrich for ADC positives once research attention is
held constant?

Two frozen proxies (D-075 dec 3):

| proxy         | definition                                              | character                  |
|---------------|---------------------------------------------------------|----------------------------|
| `pdb_present` | 1 if the target has an experimentally solved PDB structure | binary, low-noise, strong |
| `pub_count`   | PubMed hit count for the gene symbol                     | continuous, noisier        |

Run against each **separately** — a sensitivity pair, never one blessed number.

════════════════════════════════════════════════════════════════════════════════
⚠ THE FREEZE IS THE WHOLE POINT (D-075 dec 3, and §3 bite 2)
════════════════════════════════════════════════════════════════════════════════
Re-querying PubMed after seeing a result is exactly the fishing D-075 exists to prevent. So the
proxies are **snapshotted to a file once**, with their query string and the UTC date, and the
control **only ever reads the snapshot**:

    1. `--freeze`   queries the sources ONCE and writes `data/attention_proxies.json`.
                    REFUSES to overwrite an existing snapshot without `--refreeze`, which is
                    itself recorded in the file's history so a re-freeze can never be silent.
    2. `--control`  reads the snapshot and computes the matched enrichment. **Never queries.**

Because the control reads only the snapshot, re-running it is **byte-identical** — the
reproducibility property D-075's test surface requires. `--control` fails loudly if the snapshot is
absent rather than fetching a fresh one, since a silently-refreshed proxy is an unfrozen proxy.

⚠ NO RUN IN THE D-075 PR. The pure functions here are fixture-tested; `--freeze` and `--control`
are **owner-authorised runs after merge**, with the interpretation already frozen in the log.

⚠ THIS INSTRUMENT STATES WHAT IT GETS WRONG (D-074 dec 3). `pub_count` is a weak attention proxy:
raw PubMed counts conflate gene-symbol ambiguity (a symbol that is also an English word inflates),
research era, and disease prevalence. `pdb_present` is cleaner but coarse — one bit for a target
with 40 structures and one with a single low-resolution fragment. Both bounds print with the
report; neither is silently treated as "attention, measured".

Standard library only (like `scripts/intersection_check.py`), no third-party math — this is offline,
excluded from the serving image, and not gated.

Usage:
    python scripts/attention_control.py --freeze              # ONCE: snapshot both proxies
    python scripts/attention_control.py --control --proxy pdb_present
    python scripts/attention_control.py --control --proxy pub_count
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

SNAPSHOT = REPO / "data" / "attention_proxies.json"

# ── the FROZEN query definitions. Changing a string here invalidates an existing snapshot; the
# snapshot records which query produced it, so a mismatch is detectable rather than assumed. ──
PUBMED_QUERY_TEMPLATE = '{symbol}[Title/Abstract] AND (protein[Title/Abstract] OR gene[Title/Abstract])'
PUBMED_ENDPOINT = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
UNIPROT_ENDPOINT = "https://rest.uniprot.org/uniprotkb/{accession}.json"

PROXY_NAMES = ("pdb_present", "pub_count_tagged", "pub_count_atm")

# ── D-075 amendment 2: the three arms. `AND (protein OR gene)` is DROPPED from both PubMed
# arms - it discarded 46% of results on whether two specific words appear in an abstract, a
# word-presence filter presenting as a semantic one (F-047's class). The template above is
# retained unchanged because an existing snapshot records it; these are the arms that will be
# frozen from here. ──
PUBMED_TAGGED_TEMPLATE = "{symbol}[Title/Abstract]"
PUBMED_ATM_TEMPLATE = "{symbol}"
#: NCBI allows 3 requests/second without a key.
NCBI_DELAY_S = 0.40
PROXY_NAMES_V2 = ("pdb_present", "pub_count_tagged", "pub_count_atm")


def parse_pdb_present(body: bytes) -> int:
    """1 if UniProt lists an experimentally solved PDB structure, else 0. PURE and STRICT.

    !! THE NEGATIVE CASE IS THE HARD ONE AND IT IS PINNED TO A RECORDED RESPONSE. `E2RYF6` has
    `uniProtKBCrossReferences` PRESENT with 55 entries and ZERO of them PDB. So:

      - "is the key missing?"          -> wrong, it is there
      - "is the list empty?"           -> wrong, it has 55 entries
      - "any structure database?"      -> !! WRONG, and dangerously: E2RYF6 carries an
                                          AlphaFoldDB entry, and AlphaFold is a PREDICTION, not
                                          a solved structure (`A-014`)

    ! It RAISES on a malformed body rather than returning 0. Turning garbage into a zero is how
    a parse failure becomes a low-attention stratum - the fetcher converts the raise into `None`,
    which is a different value with a different meaning, and that separation is the whole point.
    """
    doc = json.loads(body.decode("utf-8"))
    xrefs = doc["uniProtKBCrossReferences"]
    return 1 if any(x.get("database") == "PDB" for x in xrefs) else 0


def parse_pub_count(body: bytes) -> int:
    """The esearch hit count. PURE and STRICT, pinned to a recorded esearch response.

    ! `esearchresult.count` arrives as a STRING in the eutils JSON, which is why this converts
    explicitly rather than trusting the type.
    """
    doc = json.loads(body.decode("utf-8"))
    return int(doc["esearchresult"]["count"])


def _urlopen(url: str, timeout: float = 60.0):
    """The default opener. ! Standard library only - the freeze must be reproducible from a
    checkout, and this module is excluded from the serving image."""
    import urllib.request                                    # noqa: PLC0415

    return urllib.request.urlopen(url, timeout=timeout)


def _fetch(url: str, parse, *, opener=None, sleep=None):
    """Fetch, parse, and turn EVERY failure into `None`.

    !! `None` IS NOT `0`, AND THAT IS THE TRAP THIS WHOLE DESIGN EXISTS AROUND. A genuine zero -
    a target with no solved structure, a symbol with no literature - is a real measurement and
    belongs in the low-attention stratum. A fetch that failed belongs nowhere. Returning 0 for
    both would push every network failure into the stratum the control is trying to measure, and
    would do it silently.

    ! The delay comes BEFORE the request so the first call in a loop waits too. 82 targets x 2
    PubMed arms is 164 calls against a 3 req/s limit, and a throttled run records real absences
    as fetch failures.
    """
    (sleep or time.sleep)(NCBI_DELAY_S)
    try:
        with (opener or _urlopen)(url, timeout=60.0) as r:
            body = r.read()
        return parse(body)
    except Exception:                                        # noqa: BLE001 - every failure is None
        return None


def fetch_pdb_present(accession, *, opener=None, sleep=None):
    """0 / 1 / None for one accession. ! `None` only on failure; a real absence is `0`."""
    return _fetch(UNIPROT_ENDPOINT.format(accession=accession), parse_pdb_present,
                  opener=opener, sleep=sleep)


def _esearch_url(term: str) -> str:
    import urllib.parse                                      # noqa: PLC0415

    params = urllib.parse.urlencode({"db": "pubmed", "term": term, "retmode": "json",
                                     "retmax": 0})
    return f"{PUBMED_ENDPOINT}?{params}"


def fetch_pub_count_tagged(symbol, *, opener=None, sleep=None):
    """`SYMBOL[Title/Abstract]` - a literal string match, no MeSH expansion."""
    return _fetch(_esearch_url(PUBMED_TAGGED_TEMPLATE.format(symbol=symbol)), parse_pub_count,
                  opener=opener, sleep=sleep)


def fetch_pub_count_atm(symbol, *, opener=None, sleep=None):
    """Bare `SYMBOL` - ! no field tag, so MeSH Automatic Term Mapping resolves the gene CONCEPT
    rather than matching the STRING."""
    return _fetch(_esearch_url(PUBMED_ATM_TEMPLATE.format(symbol=symbol)), parse_pub_count,
                  opener=opener, sleep=sleep)


# ── pure: the matched control ────────────────────────────────────────────────
@dataclass(frozen=True)
class TargetRow:
    """One ranking-set target as the control sees it: its structural rank, its label, and its
    attention proxies. `structural_score` is read from `target_scores`, never recomputed."""

    symbol: str
    structural_score: float
    label: int                        # Group B positive (1) or not (0)
    pdb_present: Optional[int] = None
    pub_count: Optional[int] = None
    pub_count_tagged: Optional[int] = None
    pub_count_atm: Optional[int] = None


@dataclass
class StratumResult:
    name: str
    n: int
    n_positives: int
    mean_positive_percentile: Optional[float]
    positive_percentiles: list[float] = field(default_factory=list)


def percentile_within(value: float, population: list[float]) -> float:
    """Fraction of the population at or below `value`, ties taking half credit — the SAME
    convention as `core.scorer.percentile_within` (D-060 dec 6). Reimplemented rather than imported
    so this offline script stays standard-library-only and independent of the fitted model."""
    if not population:
        raise ValueError("empty population - a percentile against nothing is not a number")
    below = sum(1 for p in population if p < value)
    equal = sum(1 for p in population if p == value)
    return (below + 0.5 * equal) / len(population)


def stratify(rows: list[TargetRow], proxy: str, *, n_bins: int = 2) -> dict[str, list[TargetRow]]:
    """Split rows into attention strata.

    - `pdb_present` is binary, so it yields exactly two strata regardless of `n_bins`.
    - `pub_count` is continuous and is cut at its **median** (n_bins=2) into low/high attention.
      The median is computed over the rows present, so the split is defined by the data rather than
      by a threshold invented for the occasion (D-041 dec 4's discipline).

    A row missing the proxy is placed in a named `unknown` stratum, **never dropped and never
    imputed** (D-027). An `unknown` stratum with members is reported, not hidden.
    """
    if proxy not in PROXY_NAMES:
        raise ValueError(f"unknown proxy {proxy!r}; only {list(PROXY_NAMES)} are permitted "
                         f"(D-075 dec 3 - no third proxy without a new dated entry)")
    strata: dict[str, list[TargetRow]] = {}
    known = [r for r in rows if getattr(r, proxy) is not None]
    unknown = [r for r in rows if getattr(r, proxy) is None]

    if proxy == "pdb_present":
        for r in known:
            strata.setdefault("pdb_absent" if r.pdb_present == 0 else "pdb_present", []).append(r)
    else:
        # ! Each PubMed arm splits at ITS OWN median, computed over the rows present. The two
        # arms measure different things, so a target can sit in the low stratum under one and the
        # high stratum under the other - and that disagreement is a finding about the proxy, not
        # a fault to reconcile.
        counts = sorted(getattr(r, proxy) for r in known)
        if counts:
            mid = len(counts) // 2
            median = counts[mid] if len(counts) % 2 else (counts[mid - 1] + counts[mid]) / 2
            for r in known:
                key = "pub_low" if getattr(r, proxy) <= median else "pub_high"
                strata.setdefault(key, []).append(r)
    if unknown:
        strata["unknown"] = unknown
    return strata


def matched_enrichment(rows: list[TargetRow], proxy: str) -> list[StratumResult]:
    """The control: **within each attention stratum**, where do the labelled positives sit in that
    stratum's own structural-score distribution?

    If the enrichment were purely research attention, then holding attention constant should
    flatten it — positives would land near the 0.5 mid-percentile inside every stratum. If the
    structural axis carries something attention does not, positives stay high **within** strata.

    Percentiles are computed **within the stratum**, so a stratum's result never borrows the other
    stratum's spread. A stratum with no positives reports `None`, not 0.0 — an absent statistic is
    null with a reason, never a number (D-027 / D-064 dec 5).
    """
    results: list[StratumResult] = []
    for name, members in sorted(stratify(rows, proxy).items()):
        population = [r.structural_score for r in members]
        positives = [r for r in members if r.label == 1]
        pcts = [percentile_within(r.structural_score, population) for r in positives]
        results.append(StratumResult(
            name=name,
            n=len(members),
            n_positives=len(positives),
            mean_positive_percentile=(sum(pcts) / len(pcts)) if pcts else None,
            positive_percentiles=sorted(pcts),
        ))
    return results


# ── the frozen snapshot ──────────────────────────────────────────────────────
def build_snapshot(
    targets: list[tuple[str, str]],
    *,
    frozen_date: str,
    fetch_pdb_present: Callable[[str], Optional[int]],
    fetch_pub_count_tagged: Callable[[str], Optional[int]],
    fetch_pub_count_atm: Callable[[str], Optional[int]],
) -> dict:
    """Assemble the frozen three-arm proxy snapshot (`D-075 amendment 2`).

    **The fetchers are injected**, so the assembly is fixture-testable with zero network access -
    the same seam `worker/orchestrator.py` uses for its transport (D-030).

    !! THREE ARMS, RECORDED SEPARATELY, NEVER MERGED INTO ONE FIELD. Separate keys, separate
    bounds, separate null counts. Averaging them would produce one blessed number out of three
    measurements that disagree by construction, and the disagreement is the point.

    ! A fetcher returning `None` records a null WITH A REASON and never guesses. A genuine zero -
    no solved structure, no literature - is a real measurement; conflating the two would push
    every fetch failure into the low-attention stratum, which is the stratum the control exists
    to measure.

    ! `frozen_date` is PASSED, never read from a clock. A date recorded by accident is not a
    freeze.
    """
    arms = {
        "pdb_present": fetch_pdb_present,
        "pub_count_tagged": fetch_pub_count_tagged,
        "pub_count_atm": fetch_pub_count_atm,
    }
    entries = []
    null_counts = {name: 0 for name in PROXY_NAMES}
    for symbol, accession in targets:
        entry = {"symbol": symbol, "accession": accession}
        # ! pdb_present is keyed on the ACCESSION and the PubMed arms on the SYMBOL - they are
        # different identifiers for the same target and passing one where the other is expected
        # would silently query the wrong thing.
        entry["pdb_present"] = arms["pdb_present"](accession)
        entry["pub_count_tagged"] = arms["pub_count_tagged"](symbol)
        entry["pub_count_atm"] = arms["pub_count_atm"](symbol)
        missing = [k for k in PROXY_NAMES if entry[k] is None]
        for k in missing:
            null_counts[k] += 1
        if missing:
            entry["null_reasons"] = {k: "source returned no usable value at freeze time"
                                     for k in missing}
        entries.append(entry)
    return {
        "frozen_date": frozen_date,
        # !! THE SENTENCE, ON THE FACE, UNSOFTENED. It is not a footnote and it is not optional:
        # the proxies were chosen and frozen AFTER Run A's result was known, and a reader who
        # does not know that cannot weigh what follows.
        "note": "The proxies are frozen KNOWING Run A survived.",
        # ! Both query strings verbatim. The snapshot records the query that was RUN; if this
        # disagrees with what the fetchers send, the snapshot is not frozen - it describes a
        # query nobody executed.
        "pubmed_query_tagged": PUBMED_TAGGED_TEMPLATE,
        "pubmed_query_atm": PUBMED_ATM_TEMPLATE,
        "pubmed_endpoint": PUBMED_ENDPOINT,
        "uniprot_endpoint": UNIPROT_ENDPOINT,
        "proxy_names": list(PROXY_NAMES),
        "bounds": {
            "pdb_present": "one bit; a target with 40 structures and one with a single fragment "
                           "are indistinguishable. AlphaFold does NOT count - it is a prediction, "
                           "not a solved structure (A-014).",
            "pub_count_tagged": "literal string match on SYMBOL[Title/Abstract], no MeSH "
                                "expansion; misses synonym usage entirely - the community writes "
                                "HER2 where the record says ERBB2.",
            "pub_count_atm": "untagged, resolved by MeSH Automatic Term Mapping - the gene "
                             "concept rather than the string; inflates symbols that are ordinary "
                             "English words.",
        },
        # ! A high null rate is a RESULT ABOUT THE INSTRUMENT, so it is readable here rather than
        # re-derived from the rows by whoever thinks to look.
        "null_counts": null_counts,
        "n_targets": len(entries),
        "targets": entries,
    }


def cohort_targets() -> list[tuple[str, str]]:
    """The 82 as `(symbol, accession)`. ! Read from the mapping artifact, never re-derived - the
    same file `core.adc_reference` keys on, so the freeze and the labels cannot disagree about
    which cohort they mean."""
    import csv                                              # noqa: PLC0415

    path = REPO / "data" / "cohort_82_mapping.csv"
    with open(path, encoding="utf-8") as fh:
        return [(r["symbol"], r["accession"]) for r in csv.DictReader(fh) if r.get("accession")]


def deployed_scores_and_labels(
    ranking_url: str = "https://pharmfoldmdk.fly.dev/api/ranking",
) -> tuple[dict[str, float], set[str]]:
    """`(scores, labels)` for the control.

    ! Scores are READ from the SERVED ranking - `target_scores` via `/api/ranking`, the
    pre-registered run - and never recomputed (`D-075` dec 5). Recomputing them here would make
    the control a measurement of this script rather than of the deployed model.

    ! Labels are Group B, COMPUTED BY JOIN through `core.adc_reference` rather than typed
    (`D-040`), and mapped back to symbols because the control keys on symbol.
    """
    import urllib.request                                   # noqa: PLC0415

    from core.adc_reference import (cohort_accessions, group_b_accessions,   # noqa: PLC0415
                                    load_mapping, cohort_symbol_to_accession)

    with urllib.request.urlopen(ranking_url, timeout=60) as r:
        doc = json.loads(r.read().decode("utf-8"))
    rows = doc if isinstance(doc, list) else (doc.get("rows") or doc.get("results") or [])
    scores = {row["gene"]: float(row["score"]) for row in rows}

    gb = group_b_accessions(load_mapping(), cohort_accessions())
    by_symbol = cohort_symbol_to_accession()
    labels = {sym for sym, acc in by_symbol.items() if acc in gb}
    return scores, labels


def load_snapshot(path: Path = SNAPSHOT) -> dict:
    """Read the frozen snapshot. **Raises if absent** — the control must never silently fall back
    to a live query, because a refreshed proxy is an unfrozen proxy (D-075 dec 3)."""
    if not path.exists():
        raise FileNotFoundError(
            f"no frozen proxy snapshot at {path}. Run `--freeze` FIRST and commit the snapshot; "
            f"the control reads only frozen inputs so that re-running it is byte-identical "
            f"(D-075 dec 3). It will not query on your behalf."
        )
    return json.loads(path.read_text(encoding="utf-8"))


def rows_from(snapshot: dict, scores: dict[str, float], labels: set[str]) -> list[TargetRow]:
    """Join the frozen proxies to the deployed structural scores and the Group B labels.

    `scores` comes from `target_scores` via `/api/ranking` (the served, pre-registered run — read,
    never recomputed, D-075 dec 5). A snapshot target absent from `scores` is **skipped with a
    warning**, never given a fabricated score.
    """
    rows: list[TargetRow] = []
    for entry in snapshot["targets"]:
        symbol = entry["symbol"]
        if symbol not in scores:
            print(f"WARNING: {symbol} is in the frozen snapshot but has no structural score "
                  f"- skipped, not fabricated")
            continue
        rows.append(TargetRow(
            symbol=symbol,
            structural_score=scores[symbol],
            label=1 if symbol in labels else 0,
            pdb_present=entry.get("pdb_present"),
            pub_count_tagged=entry.get("pub_count_tagged"),
            pub_count_atm=entry.get("pub_count_atm"),
        ))
    return rows


# ── reporting ────────────────────────────────────────────────────────────────
def format_report(results: list[StratumResult], proxy: str, snapshot: dict) -> str:
    lines = [
        f"D-075 Decision 3 - popularity-matched control on `{proxy}`",
        f"  proxy frozen: {snapshot.get('frozen_date')}  (n_targets={snapshot.get('n_targets')})",
        f"  bound: {snapshot.get('bounds', {}).get(proxy, 'not recorded')}",
        "",
        f"  {'stratum':<14} {'n':>4} {'n_pos':>6} {'mean positive percentile':>26}",
    ]
    for r in results:
        shown = "null (no positives)" if r.mean_positive_percentile is None \
            else f"{r.mean_positive_percentile:.4f}"
        lines.append(f"  {r.name:<14} {r.n:>4} {r.n_positives:>6} {shown:>26}")
    lines += [
        "",
        "  Read against D-075 Decision 4, which was frozen before this ran. Enrichment surviving",
        "  inside BOTH strata is the confound substantially excluded; vanishing under matching is",
        "  Branch B and is the finding. A split across strata is reported as a split, not averaged.",
        "  ⚠ Judge on the explicit triple where a distribution is compared - never one statistic.",
    ]
    return "\n".join(lines)


def run(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python scripts/attention_control.py",
        description="D-075 dec 3: freeze the attention proxies, then run the matched control.",
    )
    parser.add_argument("--freeze", action="store_true",
                        help="query the sources ONCE and write the frozen snapshot")
    parser.add_argument("--refreeze", action="store_true",
                        help="permit overwriting an existing snapshot (recorded, never silent)")
    parser.add_argument("--control", action="store_true",
                        help="run the matched control from the frozen snapshot (never queries)")
    parser.add_argument("--frozen-date", dest="frozen_date", default="2026-09-12",
                        help="the freeze date, PASSED not clocked (D-075 dec 3)")
    parser.add_argument("--proxy", choices=list(PROXY_NAMES),
                        help="which frozen proxy to match on; run each separately")
    args = parser.parse_args(argv)

    if args.freeze:
        # !! THE REFUSAL COMES FIRST. A silent re-freeze would unfreeze the pre-registration, and
        # the check must happen before a single query is sent.
        if SNAPSHOT.exists() and not args.refreeze:
            print(f"REFUSED: {SNAPSHOT} already exists. A silent re-freeze would unfreeze the "
                  f"pre-registration; pass --refreeze to overwrite deliberately.")
            return 2
        targets = cohort_targets()
        print(f"FREEZING {len(targets)} targets, three arms, {NCBI_DELAY_S}s between calls.")
        print(f"  pdb_present      {UNIPROT_ENDPOINT}")
        print(f"  pub_count_tagged {PUBMED_TAGGED_TEMPLATE}")
        print(f"  pub_count_atm    {PUBMED_ATM_TEMPLATE}")
        snap = build_snapshot(
            targets,
            # ! PASSED, never clocked. A date recorded by accident is not a freeze.
            frozen_date=args.frozen_date,
            fetch_pdb_present=fetch_pdb_present,
            fetch_pub_count_tagged=fetch_pub_count_tagged,
            fetch_pub_count_atm=fetch_pub_count_atm,
        )
        SNAPSHOT.parent.mkdir(parents=True, exist_ok=True)
        SNAPSHOT.write_text(json.dumps(snap, indent=2, sort_keys=True), encoding="utf-8")
        # !! CONFIRM THE WRITE FROM THE FILESYSTEM, NOT FROM REACHING THIS LINE. The previous
        # version of this branch exited 0 having written nothing.
        if not SNAPSHOT.exists() or SNAPSHOT.stat().st_size == 0:
            print(f"REFUSED: {SNAPSHOT} was not written.")
            return 2
        print(f"wrote {SNAPSHOT} ({SNAPSHOT.stat().st_size:,} bytes)")
        print(f"frozen_date {snap['frozen_date']} | n_targets {snap['n_targets']}")
        # ! NULL COUNTS BEFORE ANYTHING IS INTERPRETED. A high null rate is a result about the
        # instrument, not noise to absorb.
        print("null counts per proxy:")
        for name, n in snap["null_counts"].items():
            print(f"  {name:<18}{n:>4} of {snap['n_targets']}")
        print(snap["note"])
        return 0

    if args.control:
        if not args.proxy:
            print("--control requires --proxy (run pdb_present and pub_count SEPARATELY - a "
                  "sensitivity pair, not one blessed number, D-075 dec 3)")
            return 2
        try:
            snapshot = load_snapshot()
        except FileNotFoundError as exc:
            print(f"REFUSED: {exc}")
            return 2
        scores, labels = deployed_scores_and_labels()
        rows = rows_from(snapshot, scores, labels)
        print(f"frozen snapshot {snapshot.get('frozen_date')} | {len(rows)} rows joined to the "
              f"served ranking | {sum(r.label for r in rows)} Group B positives")
        print(format_report(matched_enrichment(rows, args.proxy), args.proxy, snapshot))
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(run())
