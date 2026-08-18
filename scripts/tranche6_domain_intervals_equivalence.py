"""§9 proof obligation — the unified `domain_intervals` is byte-identical to what it replaces.

⚠⚠ **THE ORACLES BELOW ARE FROZEN VERBATIM COPIES** of the three implementations the
reconciliation deletes, kept here so the proof survives the deletion. They are **not** imported
from the modules they came from: after the reconciliation those functions do not exist, and a
proof that imports the thing it is proving against proves nothing once that thing is gone.

  `_oracle_admit_raw` — `scripts/tranche6_domain_survey.py:67` as of `7011e24`
  `_oracle_drop`      — `scripts/tranche6_runs.py:64`          as of `7011e24`
  `_oracle_clip`      — `clip_intervals` in `scripts/tranche6_runs_clip_compare.py` as of `7591164`

⚠ **Compared on HASHES OF SERIALISED INTERVALS, never on counts.** Two interval lists of equal
length can differ in every coordinate, and a count comparison would call that agreement — which is
the two-paths-to-one-quantity defect this whole task exists to close, committed one level up.

⚠ **Cache-wide for `admit_raw`, not sampled** — every document in `data/census/spancache`.

⚠⚠ **AND THE PROOF CHECKS ITSELF.** A corpus in which no domain ever crosses a span boundary makes
all three rules agree, and an equivalence proof over it would pass while proving nothing. The
`DISCRIMINATION` section below counts the documents on which the rules actually disagree. **If that
count is zero the proof is vacuous and this script says so and fails.**

READ-ONLY. Cache-only: no network, no database, no GPU.

Usage:
    python scripts/tranche6_domain_intervals_equivalence.py
    python scripts/tranche6_domain_intervals_equivalence.py --limit 200   # a quick pass
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from scripts.tranche6_domain_census import (  # noqa: E402
    MANIFEST,
    STRADDLE_RULES,
    UNIPROT_CACHE,
    domain_intervals,
)

DOMAINLIKE = ("Domain", "Repeat")


# ══════════════════════════════════════════ frozen oracles — DO NOT "TIDY" OR RE-IMPORT THESE ══

def _oracle_admit_raw(doc, s0, s1):
    """VERBATIM `scripts/tranche6_domain_survey.py:67` at 7011e24. Note: no `int()` cast."""
    out = []
    for f in doc.get("features", []):
        if f.get("type") not in DOMAINLIKE:
            continue
        a = f["location"]["start"].get("value")
        b = f["location"]["end"].get("value")
        if a is None or b is None or b < s0 or a > s1:
            continue
        out.append((a, b, f.get("description", ""), f.get("type")))
    return sorted(out)


def _oracle_drop(doc, s0, s1):
    """VERBATIM `scripts/tranche6_runs.py:64` at 7011e24."""
    out = []
    for f in doc.get("features", []):
        if f.get("type") not in ("Domain", "Repeat"):
            continue
        a = f["location"]["start"].get("value")
        b = f["location"]["end"].get("value")
        if a is None or b is None or a < s0 or b > s1:
            continue
        out.append((int(a), int(b), f.get("description", ""), f.get("type")))
    return sorted(out)


def _oracle_clip(doc, s0, s1):
    """VERBATIM `clip_intervals` in `scripts/tranche6_runs_clip_compare.py` at 7591164."""
    out = []
    for f in doc.get("features", []):
        if f.get("type") not in ("Domain", "Repeat"):
            continue
        a = f["location"]["start"].get("value")
        b = f["location"]["end"].get("value")
        if a is None or b is None:
            continue
        a, b = int(a), int(b)
        if b < s0 or a > s1:
            continue
        out.append((max(a, s0), min(b, s1), f.get("description", ""), f.get("type")))
    return sorted(out)


ORACLES = {"admit_raw": _oracle_admit_raw, "drop": _oracle_drop, "clip": _oracle_clip}


def _serialise(intervals) -> bytes:
    """⚠ Coordinates AND description AND type, in order. A hash over coordinates alone would let a
    mislabelled feature through, and the tuple's last two fields are what name it."""
    return repr([tuple(x) for x in intervals]).encode("utf-8")


def _spans_for(doc: dict, manifest_span) -> list[tuple[int, int]]:
    """The manifest span when there is one, PLUS a span built to FORCE straddlers.

    ⚠ The straddle-forcing span starts inside the first domain-like feature and ends inside the
    last, so both boundaries cut through a real annotation. Without it, a cache document whose
    domains happen to sit clear of its span would exercise none of the difference under test.
    """
    spans = []
    if manifest_span:
        spans.append(manifest_span)
    feats = [f for f in doc.get("features", []) if f.get("type") in DOMAINLIKE]
    coords = []
    for f in feats:
        a = (f.get("location") or {}).get("start", {}).get("value")
        b = (f.get("location") or {}).get("end", {}).get("value")
        if a is not None and b is not None:
            coords.append((int(a), int(b)))
    if coords:
        first, last = min(coords), max(coords, key=lambda t: t[1])
        s0 = (first[0] + first[1]) // 2
        s1 = (last[0] + last[1]) // 2
        if s0 < s1:
            spans.append((s0, s1))
    return spans


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--limit", type=int, help="evaluate only the first N cache documents")
    args = ap.parse_args()

    with MANIFEST.open(encoding="utf-8") as fh:
        manifest_spans = {r["census_accession"]: (int(r["span_start"]), int(r["span_end"]))
                          for r in csv.DictReader(fh)}

    files = sorted(UNIPROT_CACHE.glob("*.json"))
    if args.limit:
        files = files[:args.limit]

    running = {r: (hashlib.sha256(), hashlib.sha256()) for r in STRADDLE_RULES}  # (oracle, new)
    n_docs = n_spans = n_intervals = 0
    n_manifest_spans = 0
    differ = {"drop_vs_clip": 0, "drop_vs_admit_raw": 0, "clip_vs_admit_raw": 0}
    mismatches = []

    for p in files:
        doc = json.loads(p.read_bytes().decode("utf-8"))
        n_docs += 1
        ms = manifest_spans.get(p.stem)
        if ms:
            n_manifest_spans += 1
        for (s0, s1) in _spans_for(doc, ms):
            n_spans += 1
            got = {}
            for rule in STRADDLE_RULES:
                oracle_iv = ORACLES[rule](doc, s0, s1)
                new_iv = domain_intervals(doc, s0, s1, straddle=rule)
                o_bytes, n_bytes = _serialise(oracle_iv), _serialise(new_iv)
                running[rule][0].update(o_bytes)
                running[rule][1].update(n_bytes)
                if o_bytes != n_bytes and len(mismatches) < 10:
                    mismatches.append((p.stem, rule, s0, s1, oracle_iv[:3], new_iv[:3]))
                got[rule] = n_bytes
                n_intervals += len(new_iv)
            if got["drop"] != got["clip"]:
                differ["drop_vs_clip"] += 1
            if got["drop"] != got["admit_raw"]:
                differ["drop_vs_admit_raw"] += 1
            if got["clip"] != got["admit_raw"]:
                differ["clip_vs_admit_raw"] += 1

    W = 100
    print("=" * W)
    print("§9 EQUIVALENCE PROOF — unified `domain_intervals` vs the three frozen oracles")
    print("=" * W)
    print(f"  cache documents evaluated : {n_docs:,}   (cache-wide, not sampled)"
          if not args.limit else f"  cache documents evaluated : {n_docs:,}   ⚠ --limit IN USE")
    print(f"  spans evaluated           : {n_spans:,}  "
          f"({n_manifest_spans:,} manifest spans + straddle-forcing spans)")
    print(f"  intervals produced        : {n_intervals:,}")

    print(f"\n  {'rule':11s} {'oracle sha256':>20s} {'unified sha256':>20s}  verdict")
    print("  " + "-" * (W - 4))
    all_match = True
    for rule in STRADDLE_RULES:
        o, n = running[rule][0].hexdigest(), running[rule][1].hexdigest()
        match = o == n
        all_match &= match
        print(f"  {rule:11s} {o[:20]:>20s} {n[:20]:>20s}  "
              f"{'IDENTICAL' if match else '*** DIFFERS ***'}")

    print("\n  ⚠⚠ DISCRIMINATION — did the corpus actually exercise the difference?")
    print("  " + "-" * (W - 4))
    for k, v in differ.items():
        print(f"    spans where {k:22s} produce different intervals : {v:,}")
    vacuous = all(v == 0 for v in differ.values())
    print(f"    ⚠ proof is vacuous: {vacuous}"
          + ("   *** a corpus with no straddlers proves nothing ***" if vacuous else ""))

    if mismatches:
        print("\n  *** MISMATCHES (first 10) ***")
        for acc, rule, s0, s1, o, n in mismatches:
            print(f"    {acc} {rule} span {s0}-{s1}\n      oracle {o}\n      new    {n}")

    ok = all_match and not vacuous
    print(f"\n  VERDICT: {'PASS' if ok else '*** FAIL ***'}"
          f"   (byte-identical under all three rules: {all_match}; non-vacuous: {not vacuous})")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
