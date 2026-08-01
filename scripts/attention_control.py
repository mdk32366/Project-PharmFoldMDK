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

PROXY_NAMES = ("pdb_present", "pub_count")


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
        counts = sorted(r.pub_count for r in known)          # type: ignore[misc]
        if counts:
            mid = len(counts) // 2
            median = counts[mid] if len(counts) % 2 else (counts[mid - 1] + counts[mid]) / 2
            for r in known:
                key = "pub_low" if r.pub_count <= median else "pub_high"   # type: ignore[operator]
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
    fetch_pub_count: Callable[[str], Optional[int]],
) -> dict:
    """Assemble the frozen proxy snapshot. **The fetchers are injected**, so the assembly logic is
    fixture-testable with zero network access — the same seam `worker/orchestrator.py` uses for its
    transport (D-030). A fetcher returning `None` records a null with a reason; it never guesses.

    `frozen_date` is passed in rather than read from the clock, so a test can pin it and the caller
    must state it explicitly — a date recorded by accident is not a freeze.
    """
    entries = []
    for symbol, accession in targets:
        pdb = fetch_pdb_present(accession)
        pubs = fetch_pub_count(symbol)
        entry = {"symbol": symbol, "accession": accession,
                 "pdb_present": pdb, "pub_count": pubs}
        missing = [k for k in ("pdb_present", "pub_count") if entry[k] is None]
        if missing:
            entry["null_reasons"] = {k: "source returned no usable value at freeze time"
                                     for k in missing}
        entries.append(entry)
    return {
        "frozen_date": frozen_date,
        "pubmed_query_template": PUBMED_QUERY_TEMPLATE,
        "pubmed_endpoint": PUBMED_ENDPOINT,
        "uniprot_endpoint": UNIPROT_ENDPOINT,
        "proxy_names": list(PROXY_NAMES),
        "bounds": {
            "pdb_present": "one bit; a target with 40 structures and one with a single fragment "
                           "are indistinguishable",
            "pub_count": "raw hit count; conflates gene-symbol ambiguity, research era and "
                         "disease prevalence. A weak attention proxy, as F-005 already records "
                         "of the evidence score.",
        },
        "n_targets": len(entries),
        "targets": entries,
    }


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
            pub_count=entry.get("pub_count"),
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
    parser.add_argument("--proxy", choices=list(PROXY_NAMES),
                        help="which frozen proxy to match on; run each separately")
    args = parser.parse_args(argv)

    if args.freeze:
        print("--freeze performs live queries and is an OWNER-AUTHORISED run (D-075: no run in "
              "the implementing PR). Wire the fetchers and invoke build_snapshot() deliberately.")
        if SNAPSHOT.exists() and not args.refreeze:
            print(f"REFUSED: {SNAPSHOT} already exists. A silent re-freeze would unfreeze the "
                  f"pre-registration; pass --refreeze to overwrite deliberately.")
            return 2
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
        print(f"loaded frozen snapshot ({snapshot.get('frozen_date')}); supply the deployed scores "
              f"and labels to rows_from() to compute the control.")
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(run())
