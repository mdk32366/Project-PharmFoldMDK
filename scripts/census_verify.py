#!/usr/bin/env python3
"""Census Task 2 — VERIFY the accession column; never re-derive it (D-079 dec 5).

    python scripts/census_verify.py --source data/census/membraneome-reconstructed-2026-08-04.csv \
                                    --out-dir data/census --resolved-on 2026-08-06

⚠ THIS VERIFIES, IT DOES NOT DERIVE. The reconstructed membraneome already carries an accession on
all 7,903 rows. Re-deriving the mapping would create a **second accession source with nothing
comparing it to the first** — the two-paths class, caught in a standing Planner order before it
executed. Verification means comparing the two accession columns the CSV already holds:
`UniProt Accession` (as SURFY published it) against `uniprot_current_accession` (what UniProt serves
today). **No network. No lookup. Nothing invented.**

TWO FILES, TWO GRAINS — PARENT AND CHILD, NOT SIBLINGS (SPEC-2026-08-05 §3).

  accession_map.csv   per IDENTIFIER, 7,903 rows.  The verification record.
  census_roster.csv   per PROTEIN,    7,811 rows.  DERIVED. What the pipeline reads.

⚠ They cannot be one file. `verification_bucket` is a fact about an *identifier*, and a protein
with 35 identifiers may carry 35 different buckets; flattening either loses the finding or invents
a summary nobody ruled. And they cannot be siblings — two files describing one population with
nothing comparing them is the class this repo has catalogued more than any other. The roster is
**derived**, carries `parent_sha256`, and a test pins its row count to the map's distinct keys.

⚠ THE COLLAPSE MUST HAPPEN BEFORE THE FETCH. `census_spans.py` fetches one span per row. At
identifier grain that fetches **HLA-B thirty-five times** and weights one family **83-fold** inside
the confidence distribution that is the census's headline use — the exact defect the census-key
amendment closed. The roster's `census_accession` is the fetch key.

OWNER-RESERVED, AND NOT DECIDED HERE: how `disagrees` and `multi` resolve. ⚠ This reports the list.
It does not pick.
"""

from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import sys
from pathlib import Path
from typing import Any, Optional

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from core.census_identity import (  # noqa: E402
    CENSUS_IDENTITY_STATUS,
    FETCH_INELIGIBLE_REASON,
    VERIFICATION_BUCKET,
    fetch_eligible,
)

#: Source columns, named once. A rename upstream fails loudly at `_require_columns`.
SRC_ENTRY = "UniProt Name"
SRC_ACCESSION = "UniProt Accession"
CUR_ACCESSION = "uniprot_current_accession"
SRC_STATUS = "uniprot_status"
SRC_CLASS = "surfy_class"
SRC_CONFLICT = "class_conflict"

MAP_COLUMNS = ("entry_name", "source_accession", "uniprot_accession", "uniprot_status",
               "surfy_class", "class_conflict", "verification_bucket", "census_accession",
               "resolved_on")
ROSTER_COLUMNS = ("census_accession", "source_identifiers", "source_accessions", "census_class",
                  "census_identity_status", "fetch_eligible", "fetch_ineligible_reason",
                  "parent_sha256", "resolved_on")

#: UniProt's own vocabulary, mapped to ours at the one place the translation happens.
_UNIPROT_STATUS = {"active_reviewed": "active", "merged": "merged", "inactive": "inactive"}


class SourceSchemaError(ValueError):
    """A required source column is missing. ⚠ Raised, never worked around."""


def _require_columns(fieldnames: list[str]) -> None:
    missing = [c for c in (SRC_ENTRY, SRC_ACCESSION, CUR_ACCESSION, SRC_STATUS, SRC_CLASS,
                           SRC_CONFLICT) if c not in fieldnames]
    if missing:
        raise SourceSchemaError(
            f"source CSV is missing required column(s): {missing}. Present: {fieldnames}")


def verification_bucket(source_acc: str, uniprot_acc: str) -> str:
    """Compare the two accession columns. ⚠ A FINDING — it never gates a fetch."""
    if source_acc and uniprot_acc:
        return "agrees" if source_acc == uniprot_acc else "disagrees"
    if source_acc:
        return "source_only"
    if uniprot_acc:
        return "uniprot_only"
    return "unresolvable"


def collapse_identity_status(rows: list[dict[str, Any]], census_accession: str) -> str:
    """The protein's identity status: the status of its SELF-IDENTIFIER, or `merged` if none.

    The **self-identifier** is the source row whose `source_accession` equals the protein's
    `census_accession` — the identifier that *names* the protein rather than merely reaching it.

    ⚠ NOT A MAJORITY. A majority rule would make HLA-B `merged` on the strength of 34 identifiers
    that are not it. The merge is a fact about the *identifiers* and is already preserved losslessly
    in `source_identifiers`; **the protein's identity status is a fact about the protein**,
    established by the identifier that names it.

    ⚠ THE RAISE BRANCHES ARE NOT DEFENSIVE DECORATION. **None occurs in the 2026-08-04 file** —
    that is measured, not assumed — and a future UniProt release producing one must stop the
    pipeline rather than be absorbed. **A collapse function with no unrepresentable input is a
    default in disguise.**
    """
    selves = [r for r in rows if r["source_accession"] == census_accession]
    if len(selves) > 1:
        raise ValueError(
            f"{census_accession}: {len(selves)} self-identifiers; a protein is named by at most one")
    if len(selves) == 1:
        status = selves[0]["uniprot_status"]
        if status == "merged":
            raise ValueError(f"{census_accession}: its self-identifier is 'merged' — an accession "
                             f"merged into itself")
        if status not in CENSUS_IDENTITY_STATUS:
            raise ValueError(f"{census_accession}: self-identifier status {status!r} is outside "
                             f"the vocabulary {CENSUS_IDENTITY_STATUS}")
        return status
    if all(r["uniprot_status"] == "merged" for r in rows):
        return "merged"
    raise ValueError(
        f"{census_accession}: no self-identifier and its sources are not all 'merged' "
        f"({sorted({r['uniprot_status'] for r in rows})}) — unrepresentable, not defaulted")


def read_map_rows(source: Path, *, resolved_on: str) -> list[dict[str, Any]]:
    """The per-identifier verification record. One row in, one row out, order preserved."""
    with source.open(encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        _require_columns(list(reader.fieldnames or []))
        out: list[dict[str, Any]] = []
        for raw in reader:
            g = lambda k: (raw.get(k) or "").strip()  # noqa: E731
            src, cur = g(SRC_ACCESSION), g(CUR_ACCESSION)
            status = _UNIPROT_STATUS.get(g(SRC_STATUS))
            if status is None:
                raise ValueError(
                    f"{g(SRC_ENTRY)}: uniprot_status {g(SRC_STATUS)!r} has no mapping into "
                    f"{CENSUS_IDENTITY_STATUS}. ⚠ An unmapped source state is NEVER defaulted.")
            out.append({
                "entry_name": g(SRC_ENTRY),
                "source_accession": src,
                "uniprot_accession": cur,
                "uniprot_status": status,
                "surfy_class": g(SRC_CLASS),
                "class_conflict": g(SRC_CONFLICT),
                "verification_bucket": verification_bucket(src, cur),
                "census_accession": cur,
                "resolved_on": resolved_on,
            })
        return out


def build_roster(map_rows: list[dict[str, Any]], *, parent_sha256: str,
                 resolved_on: str) -> list[dict[str, Any]]:
    """Derive the per-protein roster. ⚠ A collapse that loses its inputs is a deletion."""
    by_acc: dict[str, list[dict[str, Any]]] = collections.OrderedDict()
    for r in map_rows:
        by_acc.setdefault(r["census_accession"], []).append(r)

    roster: list[dict[str, Any]] = []
    for acc, rows in by_acc.items():
        classes = {r["surfy_class"] for r in rows}
        # ⚠ A protein whose source entries disagree on class has NO SURFY class (F-019). First-wins
        # would place it in one of two populations by row order, and those populations are exactly
        # the ones F-016 exists to keep apart.
        census_class = "class_conflict" if len(classes) > 1 else next(iter(classes))
        status = collapse_identity_status(rows, acc)
        eligible = fetch_eligible(status)
        roster.append({
            "census_accession": acc,
            "source_identifiers": "|".join(r["entry_name"] for r in rows),
            "source_accessions": "|".join(r["source_accession"] for r in rows),
            "census_class": census_class,
            "census_identity_status": status,
            "fetch_eligible": "true" if eligible else "false",
            "fetch_ineligible_reason": "" if eligible else FETCH_INELIGIBLE_REASON[status],
            "parent_sha256": parent_sha256,
            "resolved_on": resolved_on,
        })
    return roster


def _write(path: Path, columns: tuple[str, ...], rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(columns))
        w.writeheader()
        w.writerows(rows)


def sha256_of(path: Path) -> str:
    """⚠ A filename is not an identity."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def summarise(map_rows: list[dict[str, Any]], roster: list[dict[str, Any]]) -> dict[str, Any]:
    """Counts with every key stated. ⚠ Empty buckets asserted at 0, never omitted."""
    buckets = {b: 0 for b in VERIFICATION_BUCKET}
    for r in map_rows:
        buckets[r["verification_bucket"]] += 1
    statuses = {s: 0 for s in CENSUS_IDENTITY_STATUS}
    for r in roster:
        statuses[r["census_identity_status"]] += 1
    classes: dict[str, int] = collections.Counter(r["census_class"] for r in roster)
    return {
        "map_rows": len(map_rows),
        "roster_rows": len(roster),
        "verification_buckets": buckets,
        "census_identity_status": statuses,
        "census_class": dict(sorted(classes.items())),
        "fetch_eligible": sum(1 for r in roster if r["fetch_eligible"] == "true"),
    }


def run(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(prog="python scripts/census_verify.py", description=__doc__)
    ap.add_argument("--source", required=True, help="the reconstructed membraneome CSV")
    ap.add_argument("--out-dir", default="data/census")
    ap.add_argument("--resolved-on", required=True, help="date of this verification (YYYY-MM-DD)")
    args = ap.parse_args(argv)

    source = Path(args.source)
    if not source.exists():
        print(f"REFUSING: source not found: {source}")
        return 1
    src_sha = sha256_of(source)
    print(f"source {source} sha256={src_sha}")

    map_rows = read_map_rows(source, resolved_on=args.resolved_on)
    out_dir = Path(args.out_dir)
    map_path = out_dir / "accession_map.csv"
    _write(map_path, MAP_COLUMNS, map_rows)
    parent_sha = sha256_of(map_path)

    roster = build_roster(map_rows, parent_sha256=parent_sha, resolved_on=args.resolved_on)
    _write(out_dir / "census_roster.csv", ROSTER_COLUMNS, roster)

    s = summarise(map_rows, roster)
    print(f"accession_map.csv   | {s['map_rows']} rows (per identifier) | sha256={parent_sha}")
    print(f"census_roster.csv   | {s['roster_rows']} rows (per protein)")
    print(f"verification buckets| {s['verification_buckets']}")
    print(f"identity status     | {s['census_identity_status']}")
    print(f"census_class        | {s['census_class']}  (four denominators, NEVER summed)")
    print(f"fetch_eligible      | {s['fetch_eligible']}")

    disagrees = [r["entry_name"] for r in map_rows if r["verification_bucket"] == "disagrees"]
    multi = [r["census_accession"] for r in roster if r["census_identity_status"] == "multi"]
    print(f"\n⚠ OWNER-RESERVED, reported and NOT picked:")
    print(f"  disagrees ({len(disagrees)}): {disagrees[:20]}{' …' if len(disagrees) > 20 else ''}")
    print(f"  multi     ({len(multi)}): {multi[:20]}{' …' if len(multi) > 20 else ''}")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
