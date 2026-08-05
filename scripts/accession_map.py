#!/usr/bin/env python3
"""Map UniProt entry names to accessions, with the failure modes as outputs.

    python scripts/accession_map.py --ids data/census/surfaceome_ids.txt \
                                    --out data/census/accession_map.csv \
                                    --cache data/census/idcache

⚠ WHY THIS IS A HARD PREREQUISITE. `surfaceome_ids.txt` holds 2,886 UniProt
**entry names** (`1A01_HUMAN`). **Zero of them are accession-shaped.** Every join
in this project is keyed by accession, so the overlap between what we have and
what we can join on is EMPTY BY CONSTRUCTION — not small, empty. A "try the
accession, else map it" fallback would succeed on nothing and say nothing. Until
this runs, the census has 2,886 identifiers and 0 joinable rows.

⚠ THE BAR. A **ten-line** seed file once carried **two** wrong accessions
(2026-07-22). At 2,886 rows an unverified mapping is not a risk, it is a
certainty. Entry names are explicitly not stable identifiers; accessions are.
That asymmetry is the whole reason this step exists.

FOUR BUCKETS, AND THEY PARTITION THE INPUT:

  resolved   — exactly one active accession
  obsolete   — the accession exists but is retired (a replacement may be known)
  multi      — the entry name maps to several accessions
  unresolved — it maps to none, or the lookup failed

**Counts sum to the input count.** Nothing is dropped, nothing is invented, and an
empty bucket is reported as `0` rather than omitted — `unresolved: 0` is a
finding, a missing `unresolved` key is an unanswered question wearing the same
clothes.

⚠ TWO THINGS THIS DELIBERATELY DOES NOT DO:

  **It does not pick among `multi` candidates.** How a one-to-many is resolved is
  an identity judgement, not a mechanical one, and it is owner-reserved. The
  mapper reports the candidate list. First-wins would be a silent decision with a
  plausible-looking output.

  **It does not synthesize an accession from a string pattern.** A derived
  accession would be well-formed, joinable, and wrong — the worst combination,
  because nothing downstream would notice. A test fails if a derivation appears.

⚠ AND OBSOLETE KEEPS ITS PROVENANCE. If a retired entry resolves to a
replacement, the row stays `obsolete` and records both accessions. It does not
become `resolved` as though nothing happened — the census must be able to answer
*"how many of these came through a retirement?"* later, and overwriting the status
destroys that answer. Same principle as D-071's three-valued provenance strength.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Any, Callable, Iterable, Sequence

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

RESOLVED = "resolved"
OBSOLETE = "obsolete"
MULTI = "multi"
UNRESOLVED = "unresolved"

BUCKETS = (RESOLVED, OBSOLETE, MULTI, UNRESOLVED)

SEARCH = "https://rest.uniprot.org/uniprotkb/search"
UA = "PharmFoldMDK/0.1 (course project; UniProt REST client)"
REQUEST_PAUSE_S = 0.34          # ~3 req/s, the same politeness the cohort pull used


# ── the lookup client (injected in tests, so the logic is testable offline) ───

def uniprot_client(entry_name: str) -> list[dict]:
    """Look one entry name up against the UniProtKB search API.

    Returns a list of candidate dicts: `{accession, active, replaced_by?}`.
    An empty list means the name resolved to nothing — which is a RESULT, not an
    error, and the caller records it as `unresolved`.
    """
    from urllib.parse import urlencode
    from urllib.request import Request, urlopen

    query = urlencode({
        "query": f"id:{entry_name}",
        "fields": "accession,id,protein_name",
        "format": "json",
        "size": "10",
    })
    req = Request(f"{SEARCH}?{query}", headers={"User-Agent": UA})
    with urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    out = []
    for r in data.get("results", []):
        acc = r.get("primaryAccession")
        if not acc:
            continue
        out.append({
            "accession": acc,
            "active": (r.get("entryType") != "Inactive"),
            "replaced_by": (r.get("inactiveReason") or {}).get("mergeDemergeTo", [None])[0],
        })
    time.sleep(REQUEST_PAUSE_S)
    return out


# ── the pure mapping logic ───────────────────────────────────────────────────

def _classify(entry_name: str, candidates: Sequence[dict], resolved_on: str | None) -> dict:
    """One entry name's row. The precedence here is the whole design.

    `multi` is checked BEFORE activity, because a name resolving to several
    accessions is an ambiguity regardless of which of them are active — resolving
    it by activity would be picking, and picking is owner-reserved.
    """
    row: dict[str, Any] = {
        "entry_name": entry_name,
        "accession": "",
        "status": UNRESOLVED,
        "candidates": "",
        "obsolete_accession": "",
        "resolved_on": resolved_on or "",
        "reason": "",
    }

    if not candidates:
        row["reason"] = "no UniProt entry matched this identifier"
        return row

    if len(candidates) > 1:
        row["status"] = MULTI
        row["candidates"] = ";".join(c["accession"] for c in candidates)
        row["reason"] = f"{len(candidates)} accessions matched; resolution is owner-reserved"
        return row                      # accession stays EMPTY — no first-wins

    only = candidates[0]
    if only.get("active", True):
        row["status"] = RESOLVED
        row["accession"] = only["accession"]
        return row

    # Retired. The replacement is recorded, the retirement is NOT erased.
    row["status"] = OBSOLETE
    row["obsolete_accession"] = only["accession"]
    row["accession"] = only.get("replaced_by") or ""
    row["reason"] = ("entry is retired upstream; replacement recorded, provenance kept "
                     "(CORRECTION-RULINGS-2026-08-04 §2)")
    return row


def map_entry_names(entry_names: Iterable[str],
                    client: Callable[[str], list[dict]] = uniprot_client,
                    cache_dir: str | None = None,
                    resolved_on: str | None = None) -> list[dict]:
    """Map many entry names. Order-preserving, cached, and total.

    Every input yields exactly one output row, so the buckets partition the input
    and a count can be reconciled against the file it came from.

    A client exception becomes `unresolved` with its reason — a transient failure
    must not abort 2,886 rows, and must not be recorded as a successful mapping to
    nothing.
    """
    cache = Path(cache_dir) if cache_dir else None
    if cache:
        cache.mkdir(parents=True, exist_ok=True)

    rows: list[dict] = []
    for name in entry_names:
        hit = (cache / f"{name}.json") if cache else None

        if hit is not None and hit.exists():
            try:
                candidates = json.loads(hit.read_text(encoding="utf-8"))
            except ValueError:
                candidates = None       # torn file from a crash — re-query, don't die
            if candidates is not None:
                rows.append(_classify(name, candidates, resolved_on))
                continue

        try:
            candidates = client(name)
        except Exception as e:          # noqa: BLE001 — a failure is an unknown, not a crash
            row = _classify(name, [], resolved_on)
            row["reason"] = f"lookup failed: {type(e).__name__}: {e}"[:200]
            rows.append(row)
            continue

        if hit is not None:
            hit.write_text(json.dumps(candidates), encoding="utf-8")
        rows.append(_classify(name, candidates, resolved_on))

    return rows


def bucket_counts(rows: Iterable[dict]) -> dict[str, int]:
    """Counts for all four buckets, including the empty ones.

    An omitted key and a zero are different statements and only one of them is an
    answer.
    """
    seen = Counter(r["status"] for r in rows)
    return {bucket: seen.get(bucket, 0) for bucket in BUCKETS}


# ── CLI ──────────────────────────────────────────────────────────────────────

FIELDS = ["entry_name", "accession", "status", "resolved_on",
          "candidates", "obsolete_accession", "reason"]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ids", default="data/census/surfaceome_ids.txt")
    ap.add_argument("--out", default="data/census/accession_map.csv")
    ap.add_argument("--cache", default="data/census/idcache")
    ap.add_argument("--resolved-on", required=True, help="date of this mapping (YYYY-MM-DD)")
    ap.add_argument("--limit", type=int, default=None, help="stop after N ids (smoke runs)")
    args = ap.parse_args(argv)

    ids_path = Path(args.ids)
    if not ids_path.exists():
        raise SystemExit(f"MISSING INPUT: {ids_path}")

    names = [l.strip() for l in ids_path.read_text(encoding="utf-8").splitlines() if l.strip()]
    if args.limit:
        names = names[:args.limit]
    print(f"mapping {len(names)} entry names (cache: {args.cache})", file=sys.stderr)

    rows = map_entry_names(names, cache_dir=args.cache, resolved_on=args.resolved_on)

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)

    counts = bucket_counts(rows)
    print(f"\n  input rows   {len(names):>6}")
    for bucket in BUCKETS:
        print(f"  {bucket:<12} {counts[bucket]:>6}")
    print(f"  {'-' * 12} {'-' * 6}")
    print(f"  {'total':<12} {sum(counts.values()):>6}"
          f"   {'OK' if sum(counts.values()) == len(names) else 'PARTITION BROKEN'}")

    if counts[MULTI]:
        print(f"\n  ** {counts[MULTI]} multi row(s) — resolution is owner-reserved, NOT picked here:",
              file=sys.stderr)
        for r in rows:
            if r["status"] == MULTI:
                print(f"     {r['entry_name']}: {r['candidates']}", file=sys.stderr)

    print(f"\nwrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
