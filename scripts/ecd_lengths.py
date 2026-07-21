#!/usr/bin/env python3
"""
Measure extracellular-domain (ECD) lengths for a cohort of UniProt accessions.

Purpose (D-015 §4): the local GPU has a MEASURED fold ceiling in (440, 630) aa
(S-004/S-005). Folding a cohort means some fraction exceeds it and must go to the
D-011 rented GPU. This script measures that fraction instead of assuming it, and
reports the distribution as a finding in its own right.

Method (D-009 §2): for each accession, query the UniProt REST API, read `features`
of type "Topological domain", select spans whose description is "Extracellular",
and report their lengths. NO SEQUENCES ARE SLICED HERE and no folding is done --
this measures only, so it is cheap, local, and repeatable.

WHAT THIS SCRIPT DOES NOT DO
----------------------------
- It does not choose WHICH extracellular span to fold when a protein has several.
  Multi-pass membrane proteins have many. It reports every span plus the total and
  the largest; the fold-target selection rule is a separate decision (see below).
- It does not verify that the reported span is the ADC-relevant epitope region.
- It does not account for signal-peptide cleavage shifting mature numbering.

Usage:
    python ecd_lengths.py accessions.txt --out ecd_lengths.csv
    python ecd_lengths.py --accessions P04626,P09758,Q92729

Input file: one accession per line. Blank lines and lines starting with # ignored.
An optional second column (whitespace- or comma-separated) is carried through as a
label, so a cohort file can name its groups (e.g. "P04626  A" / "P09758  C").
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from dataclasses import dataclass, field
from typing import Iterable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

UNIPROT_URL = "https://rest.uniprot.org/uniprotkb/{acc}.json"

# Measured local ceiling, S-004/S-005 (docs/README.md).
# 440 aa folded clean (28.6 s, peak 6665 MiB, no spill, host stable).
# 630 aa is 4-for-4 fatal (HYPERVISOR_ERROR 0x00020001).
# The exact ceiling within (440, 630) is UNMEASURED -- we bucket against both
# bounds rather than pretending to a single number.
CEILING_KNOWN_GOOD = 440
CEILING_KNOWN_BAD = 630

USER_AGENT = "PharmFoldMDK/0.1 (course project; UniProt REST client)"
REQUEST_PAUSE_S = 0.34  # be a polite API citizen: ~3 req/s


@dataclass
class Span:
    start: int | None
    end: int | None
    description: str

    @property
    def length(self) -> int | None:
        if self.start is None or self.end is None:
            return None
        return self.end - self.start + 1


@dataclass
class Record:
    accession: str
    label: str = ""
    gene: str = ""
    protein_name: str = ""
    sequence_length: int | None = None
    extracellular: list[Span] = field(default_factory=list)
    error: str = ""

    @property
    def n_spans(self) -> int:
        return len(self.extracellular)

    @property
    def largest_span(self) -> int | None:
        lengths = [s.length for s in self.extracellular if s.length is not None]
        return max(lengths) if lengths else None

    @property
    def total_extracellular(self) -> int | None:
        lengths = [s.length for s in self.extracellular if s.length is not None]
        return sum(lengths) if lengths else None

    def bucket(self, value: int | None) -> str:
        """Classify against the MEASURED ceiling bounds.

        Deliberately three buckets, not two. The exact ceiling is unmeasured, so
        anything in (440, 630) is 'untested' -- not 'probably fine' and not
        'definitely fails'. Guessing either way costs a host crash or a needless
        rental.
        """
        if value is None:
            return "unknown"
        if value <= CEILING_KNOWN_GOOD:
            return "local"
        if value >= CEILING_KNOWN_BAD:
            return "rental"
        return "untested"


def fetch(accession: str, retries: int = 3) -> dict:
    """Fetch one UniProt entry as JSON. Raises on unrecoverable failure."""
    url = UNIPROT_URL.format(acc=accession)
    last_err: Exception | None = None
    for attempt in range(retries):
        try:
            req = Request(url, headers={"User-Agent": USER_AGENT})
            with urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except HTTPError as e:
            if e.code == 404:
                raise RuntimeError(f"not found (404)") from e
            last_err = e
        except (URLError, TimeoutError, json.JSONDecodeError) as e:
            last_err = e
        if attempt < retries - 1:
            time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"fetch failed after {retries} attempts: {last_err}")


def parse(accession: str, label: str, data: dict) -> Record:
    rec = Record(accession=accession, label=label)

    genes = data.get("genes") or []
    if genes:
        rec.gene = (genes[0].get("geneName") or {}).get("value", "")

    desc = data.get("proteinDescription") or {}
    rec_name = desc.get("recommendedName") or {}
    rec.protein_name = (rec_name.get("fullName") or {}).get("value", "")

    rec.sequence_length = (data.get("sequence") or {}).get("length")

    for feat in data.get("features") or []:
        if feat.get("type") != "Topological domain":
            continue
        description = feat.get("description", "") or ""
        if "extracellular" not in description.lower():
            continue
        loc = feat.get("location") or {}
        start = (loc.get("start") or {}).get("value")
        end = (loc.get("end") or {}).get("value")
        rec.extracellular.append(Span(start=start, end=end, description=description))

    return rec


def read_accessions(path: str) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = [p for p in line.replace(",", " ").split() if p]
            acc = parts[0]
            label = parts[1] if len(parts) > 1 else ""
            out.append((acc, label))
    return out


def collect(pairs: Iterable[tuple[str, str]]) -> list[Record]:
    records: list[Record] = []
    pairs = list(pairs)
    for i, (acc, label) in enumerate(pairs, 1):
        try:
            data = fetch(acc)
            rec = parse(acc, label, data)
        except Exception as e:  # noqa: BLE001 -- record the failure, never drop it
            rec = Record(accession=acc, label=label, error=str(e))
        records.append(rec)
        print(
            f"  [{i}/{len(pairs)}] {acc:<10} "
            f"{rec.gene or '?':<10} "
            f"{'ERROR: ' + rec.error if rec.error else f'{rec.n_spans} extracellular span(s)'}",
            file=sys.stderr,
        )
        time.sleep(REQUEST_PAUSE_S)
    return records


def write_csv(records: list[Record], path: str) -> None:
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow([
            "accession", "label", "gene", "protein_name", "sequence_length",
            "n_extracellular_spans", "largest_span_aa", "total_extracellular_aa",
            "bucket_by_largest", "bucket_by_total", "spans", "error",
        ])
        for r in records:
            spans = "; ".join(
                f"{s.start}-{s.end}({s.length})" for s in r.extracellular
            )
            w.writerow([
                r.accession, r.label, r.gene, r.protein_name, r.sequence_length,
                r.n_spans, r.largest_span, r.total_extracellular,
                r.bucket(r.largest_span), r.bucket(r.total_extracellular),
                spans, r.error,
            ])


def summarise(records: list[Record]) -> None:
    ok = [r for r in records if not r.error]
    failed = [r for r in records if r.error]
    no_topo = [r for r in ok if r.n_spans == 0]
    multi = [r for r in ok if r.n_spans > 1]

    print("\n" + "=" * 68)
    print("ECD LENGTH DISTRIBUTION")
    print("=" * 68)
    print(f"  queried              {len(records)}")
    print(f"  retrieved            {len(ok)}")
    print(f"  fetch failures       {len(failed)}")
    print(f"  no topology annot.   {len(no_topo)}   <- D-009 §2 cannot slice these")
    print(f"  multi-span (>1 ECD)  {len(multi)}   <- fold-target rule needed")

    print(f"\n  Ceiling bounds (MEASURED, S-004/S-005):")
    print(f"    <= {CEILING_KNOWN_GOOD} aa  local    (440 folded clean, no spill)")
    print(f"    >= {CEILING_KNOWN_BAD} aa  rental   (630 is 4-for-4 host bugcheck)")
    print(f"    between      untested (exact ceiling UNMEASURED)")

    for basis in ("largest", "total"):
        counts: dict[str, int] = {"local": 0, "untested": 0, "rental": 0, "unknown": 0}
        for r in ok:
            value = r.largest_span if basis == "largest" else r.total_extracellular
            counts[r.bucket(value)] += 1
        n = len(ok) or 1
        print(f"\n  By {basis} extracellular span:")
        for k in ("local", "untested", "rental", "unknown"):
            print(f"    {k:<9} {counts[k]:>4}   ({100 * counts[k] / n:5.1f}%)")

    lengths = sorted(r.largest_span for r in ok if r.largest_span is not None)
    if lengths:
        def pct(p: float) -> int:
            return lengths[min(int(p * len(lengths)), len(lengths) - 1)]
        print(f"\n  Largest-span length: min {lengths[0]}, median {pct(0.5)}, "
              f"p90 {pct(0.9)}, max {lengths[-1]}")

    if failed:
        print("\n  FAILURES (recorded, not dropped):")
        for r in failed:
            print(f"    {r.accession}: {r.error}")
    if no_topo:
        print("\n  NO TOPOLOGICAL DOMAIN ANNOTATION "
              "(these need a different boundary rule -- D-009 §2 does not cover them):")
        for r in no_topo:
            print(f"    {r.accession} ({r.gene or '?'}) len={r.sequence_length}")
    print()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("infile", nargs="?", help="file of accessions, one per line")
    ap.add_argument("--accessions", help="comma-separated accessions instead of a file")
    ap.add_argument("--out", default="ecd_lengths.csv", help="output CSV path")
    args = ap.parse_args()

    if args.accessions:
        pairs = [(a.strip(), "") for a in args.accessions.split(",") if a.strip()]
    elif args.infile:
        pairs = read_accessions(args.infile)
    else:
        ap.error("provide an accessions file or --accessions")

    print(f"Querying UniProt for {len(pairs)} accession(s)...", file=sys.stderr)
    records = collect(pairs)
    write_csv(records, args.out)
    summarise(records)
    print(f"Wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
