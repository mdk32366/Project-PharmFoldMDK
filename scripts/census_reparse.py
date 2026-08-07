#!/usr/bin/env python3
"""Re-PARSE the census cache under the V2 span definition. ⚠ NOT a re-extract, NOT a re-fetch.

    python scripts/census_reparse.py --class surface
    python scripts/census_reparse.py --class non_surface

⚠ **THE DROPPED DOMAINS ARE NOT IN THE CSVs.** `parse()` filtered them out before the file was
written — a `Lumenal` domain never became a row, and the output carries no record that anything was
rejected. So the CSV cannot be reclassified; **there is nothing in it to reclassify.** The
information survives one stage further back:

    network fetch  →  cache (full UniProt JSON)  →  parse() filter  →  spans_*.csv
                      ^ everything survives here     ^ information is destroyed here

**So the saving is real and it is the network fetch:** ~5,016 rate-limited requests and ~30 minutes,
not repeated, **because the cache holds the whole response rather than the parsed output.**

⚠⚠ **THE BINDING CONSTRAINT: TWO FACTS, NEVER ONE DATE.** The data was fetched 2026-08-06 at a
specific UniProt release. **Only the parse changed.** So `fetched_on` and `uniprot_release` are
copied from the existing row **byte-identically and are never restamped**, and a **new**
`parsed_under` column carries the definition. A re-parse that overwrote the fetch date would
manufacture provenance for data that did not move — turning a one-day pull into a two-day pull as an
artifact of housekeeping, **which is the date rule tripped by its own maintenance.**

⚠ **THE V1 ARTIFACTS ARE NOT OVERWRITTEN.** V2 lands in its own file. `### D-081`: two definitions,
both named, and rewriting the V1 output would destroy the before-state that makes `### F-025`
checkable in the first place.

⚠ **A missing cache entry is `absent_with_reason`, named — it is NOT re-fetched.** A partial
re-fetch would put two fetch dates in one file, which is the exact thing above.
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

from core.span_definition import (  # noqa: E402
    ABSENT_WITH_REASON, SPAN_CATEGORIES, SPAN_RULES, V2_RULED_VOCABULARY,
)
from core.span_extract import as_row, extract  # noqa: E402

CENSUS = REPO / "data" / "census"
CACHE = CENSUS / "spancache"

#: ⚠ Carried through UNCHANGED from the V1 row. `fetched_on` and `uniprot_release` are facts about
#: when the data was pulled; this pass changes neither.
CARRIED = ("census_accession", "census_class", "census_identity_status", "source_identifiers",
           "fetch_failed", "fetch_error", "fetched_on", "uniprot_release")

NEW = ("span_aa", "span_rule", "span_category", "no_span_reason", "span_boundary_coordinate",
       "terms_unruled", "terms_held", "guards", "parsed_under")

#: ⚠ The V1 span, carried so the two definitions sit side by side in one file and NEITHER is
#: implied. A reader comparing them can see both and the definition that produced each.
V1_COLUMN = "span_aa_v1"

OUT_COLUMNS = CARRIED + (V1_COLUMN,) + NEW

SOURCES = {"surface": "spans_surface.csv", "non_surface": "spans_annex.csv"}
OUTPUTS = {"surface": "spans_surface.v2.csv", "non_surface": "spans_annex.v2.csv"}


def load_cache(acc: str) -> Optional[dict]:
    p = CACHE / f"{acc}.json"
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except ValueError:
        return None


def reparse_row(row: dict[str, str], *, commit: str) -> dict[str, Any]:
    """One V1 row → one V2 row. ⚠ `fetched_on` and `uniprot_release` are copied, never computed."""
    out: dict[str, Any] = {k: row.get(k, "") for k in CARRIED}
    out[V1_COLUMN] = row.get("span_aa", "")

    if row.get("fetch_failed") == "true" or not row.get("fetched_on"):
        # ⚠ A failed or never-fetched row is neither a span nor an absence of one. It was never
        # asked, or the request is what failed — the identity is intact either way. It keeps its V1
        # reason verbatim and takes no V2 category.
        out.update({k: "" for k in NEW})
        out["no_span_reason"] = row.get("no_topology_reason", "")
        out["parsed_under"] = ""
        return out

    data = load_cache(row["census_accession"])
    if data is None:
        # ⚠ NOT re-fetched. Named.
        out.update({k: "" for k in NEW})
        out["span_category"] = ABSENT_WITH_REASON
        out["no_span_reason"] = ("cache entry absent; NOT re-fetched — a partial re-fetch would put "
                                 "two fetch dates in one file")
        out["parsed_under"] = f"{V2_RULED_VOCABULARY}@{commit}"
        return out

    r = as_row(extract(data))
    r["parsed_under"] = f"{V2_RULED_VOCABULARY}@{commit}"
    out.update(r)
    return out


def bands(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """⚠ Counted OFF THE FILE, and the denominator is declared on the same object.

    Either *N fetched with the never-fetched named beside it*, or *N total with `fetch_ineligible`
    as its own band* — **never N total with them silently absorbed.**
    """
    counts: Counter[str] = Counter()
    for r in rows:
        if r.get("fetch_failed") == "true":
            counts["fetch_failed"] += 1
        elif not r.get("fetched_on"):
            reason = (r.get("no_span_reason") or "").replace("not fetched: ", "") or "unknown"
            counts[f"fetch_ineligible:{reason}"] += 1
        elif str(r.get("span_aa", "")).strip():
            counts[f"span:{r['span_rule']}"] += 1
        else:
            counts[r.get("span_category") or "UNCATEGORISED"] += 1

    fetched = sum(n for k, n in counts.items()
                  if not k.startswith("fetch_ineligible:") and k != "fetch_failed")
    ineligible = sum(n for k, n in counts.items() if k.startswith("fetch_ineligible:"))
    failed = counts.get("fetch_failed", 0)
    return {
        "bands": dict(sorted(counts.items())),
        "denominator_total_rows": len(rows),
        "denominator_fetched": fetched,
        "denominator_fetch_ineligible": ineligible,
        "denominator_fetch_failed": failed,
        "foldable": sum(1 for r in rows if str(r.get("span_aa", "")).strip()),
        "foldable_v1": sum(1 for r in rows if str(r.get(V1_COLUMN, "")).strip()),
    }


def gains(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """⚠ Rows GAINING a span, BY MECHANISM — and rows whose existing span CHANGED.

    The second is the sharp one: the widening is predicted to be purely additive, so a changed span
    means the implementation altered what it was not asked to alter.
    """
    by_mech: Counter[str] = Counter()
    changed: list[tuple[str, str, str]] = []
    for r in rows:
        v1 = str(r.get(V1_COLUMN, "")).strip()
        v2 = str(r.get("span_aa", "")).strip()
        if not v1 and v2:
            by_mech[r["span_rule"]] += 1
        elif v1 and v2 and v1 != v2:
            changed.append((r["census_accession"], v1, v2))
        elif v1 and not v2:
            changed.append((r["census_accession"], v1, "LOST"))
    return {"gained_by_mechanism": dict(sorted(by_mech.items())),
            "gained_total": sum(by_mech.values()),
            "changed_existing_spans": changed}


def run(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(prog="python scripts/census_reparse.py", description=__doc__)
    ap.add_argument("--class", dest="census_class", required=True,
                    choices=["surface", "non_surface"],
                    help="⚠ `unclassified` is deliberately absent — F-016")
    ap.add_argument("--commit", default="working-tree",
                    help="the commit that produced these rows, recorded in `parsed_under`")
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)

    src = CENSUS / SOURCES[args.census_class]
    out = Path(args.out) if args.out else CENSUS / OUTPUTS[args.census_class]

    with src.open(encoding="utf-8", newline="") as fh:
        v1_rows = list(csv.DictReader(fh))
    if not v1_rows:
        raise ValueError(f"{src} has no rows — refusing a silent no-op")

    rows = [reparse_row(r, commit=args.commit) for r in v1_rows]

    # ⚠ THE DATE ASSERTION, in the producer as well as the test. A preserved date is a claim.
    for before, after in zip(v1_rows, rows):
        if before.get("fetched_on", "") != after.get("fetched_on", ""):
            raise AssertionError(
                f"⚠ {after['census_accession']}: fetched_on changed "
                f"{before.get('fetched_on')!r} → {after.get('fetched_on')!r}. A re-parse "
                f"manufactures provenance for data that did not move.")
        if before.get("uniprot_release", "") != after.get("uniprot_release", ""):
            raise AssertionError(f"⚠ {after['census_accession']}: uniprot_release changed")

    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(OUT_COLUMNS))
        w.writeheader()
        w.writerows(rows)

    b, g = bands(rows), gains(rows)
    (out.parent / f"{out.stem}.provenance.json").write_text(
        json.dumps({"class": args.census_class, "parsed_under": V2_RULED_VOCABULARY,
                    "source_v1_file": src.name, "rows": len(rows),
                    "band_split": b, "gains": g,
                    "note": "fetched_on and uniprot_release are carried from the V1 rows unchanged; "
                            "only the parse differs"},
                   indent=2), encoding="utf-8")

    print(f"wrote {out} | {len(rows)} rows")
    print(f"bands | {json.dumps(b['bands'])}")
    print(f"denominators | total {b['denominator_total_rows']} | fetched {b['denominator_fetched']} "
          f"| ineligible {b['denominator_fetch_ineligible']} | failed {b['denominator_fetch_failed']}")
    print(f"foldable | v1 {b['foldable_v1']} -> v2 {b['foldable']}")
    print(f"gained by mechanism | {json.dumps(g['gained_by_mechanism'])} | total {g['gained_total']}")
    print(f"⚠ changed existing spans | {len(g['changed_existing_spans'])} "
          f"| {g['changed_existing_spans'][:10]}")
    unknown = set(b["bands"]) - {f"span:{r}" for r in SPAN_RULES} - set(SPAN_CATEGORIES) \
        - {"fetch_failed"} - {k for k in b["bands"] if k.startswith("fetch_ineligible:")}
    if unknown:
        print(f"⚠ BAND KEYS OUTSIDE THE DECLARED VOCABULARY: {sorted(unknown)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
