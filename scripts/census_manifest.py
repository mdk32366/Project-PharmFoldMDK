#!/usr/bin/env python3
"""Census Task 4 — the manifest. ⚠ THE SEED IS RECORDED BEFORE THE FIRST SHUFFLE.

    python scripts/census_manifest.py --seed 20260807 --class surface --class non_surface

⚠⚠ **A SEED CHOSEN AFTER SEEING THE ORDER IS NOT A SEED, IT IS A SELECTION.** The seed is a
required argument, it is written into the provenance object **before** `shuffle` is called, and the
provenance is emitted even if the run then fails. A fold order that cannot be reproduced from a
recorded seed is a fold order somebody could have chosen.

⚠ **BANDS CHOOSE THE TIER, NEVER WHETHER A TARGET FOLDS.** `above_local` is a routing fact — it
sends a protein to the rented GPU. It is **not** an exclusion, and a manifest that quietly dropped
those rows would report a foldable population it had shrunk itself.

⚠ **THE SPAN DEFINITION IS NAMED ON EVERY ROW** (`### D-081`). Two definitions exist:
`v1-extracellular-substring-2026-07-21` measured the frozen 82; this manifest is built on
`v2-ruled-vocabulary-2026-08-07`. **A foldable count under one is not comparable to a count under
the other unless both are named** — 2,582 surface / 886 annex here against 2,352 / 332 under V1.

⚠ **THE ATTENTION-TILT LIMITATION TRAVELS WITH THE MANIFEST.** `no_topology` (now
`no_extracellular_span`) correlates weakly with UniProt entry recency — ρ ≈ −0.142 against
`entryVersion`, ρ ≈ +0.120 against `firstPublicDate`, real at n≈2,800 but ~2% of variance, and the
two proxies are mechanically confounded. **It is not a correction and nothing is adjusted for it.**
It is recorded because a fold order drawn from a population with a known tilt should say so.

⚠ **NOTHING IS SCORED, RANKED, ORDERED BY SUITABILITY, REFIT OR FEATURE-EXTRACTED HERE.** D-079
decision 1 stands. This emits a routing table and a seeded fold order — **folding is not scoring,
and the gate is on scoring.**

⚠ **NO DATABASE. NO NETWORK.** Reads the committed V2 span artifacts and writes files.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import random
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Optional

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from core.contracts import TIER_RECIPE  # noqa: E402
from core.manifest import LOCAL_CEILING, tier_for_span  # noqa: E402
from core.span_definition import V2_RULED_VOCABULARY  # noqa: E402

CENSUS = REPO / "data" / "census"
SOURCES = {"surface": "spans_surface.v2.csv", "non_surface": "spans_annex.v2.csv"}

#: ⚠ Recorded verbatim on the manifest so a reader of the fold order meets it there, not three
#: documents away. Not a correction; nothing is adjusted for it.
ATTENTION_TILT = (
    "The no_extracellular_span band correlates weakly with UniProt entry recency: Spearman "
    "rho = -0.142 against entryVersion and +0.120 against firstPublicDate, real at n≈2,800 but "
    "about 2% of variance, and the two proxies are mechanically confounded. Nothing is adjusted "
    "for it."
)

#: ⚠ R11.1 — A STATED PROPERTY OF THE CENSUS, NOT AN IMPLEMENTATION DETAIL. It belongs in the
#: provenance and in the paper, where a reader meets it, rather than in a function nobody opens.
LARGEST_CONTIGUOUS_DISCLOSURE = (
    "For multi-pass membrane proteins the census folds the LARGEST CONTIGUOUS extracellular "
    "segment and discards the remainder. 1,650 of 3,343 vocabulary rows (49.4%) carry more than "
    "one accepted span. Verified: rows where span_aa differs from the largest contiguous accepted "
    "span = 0, across 3,343. CCR4 (P51679) folds a 39 aa N-terminus and discards 61 residues "
    "across three further segments; the manifest does NOT sum them to 100. This inherits the "
    "cohort's rule (F-004 banded on largest), so the two agree."
)

#: ⚠ R11 — MEASURED AND RECORDED, NOT ACTED ON. NO LENGTH FLOOR IS RULED and none is applied.
#: PLDDT_FLOOR = 50.0 is a mean-pLDDT floor applied AFTER folding; there is no length floor in the
#: cohort or the census, so the two agree and the two-definitions concern dissolves. A short span
#: folds and then stands or falls on its own confidence.
#: ⚠ Recorded so a FUTURE scoring ruling has the number in hand rather than a fresh measurement
#: taken after the answer is wanted.
SPAN_LENGTH_DISCLOSURE_NOTE = (
    "Span-length distribution recorded as a disclosure. NO FLOOR IS APPLIED. ⚠ Two features of "
    "the tail are named rather than filtered: 73 spans are 5 aa or shorter, of which 10 are "
    "exactly 1 residue (e.g. Q8WXF7 471-471) — a one-residue topological domain is a real UniProt "
    "annotation and not a foldable object; and the longest span is Q8WXI7 (MUC16) at 14,451 aa, "
    "which routes to `rental` because tier_for_span has NO UPPER BOUND. ⚠ The A6000 single-fold "
    "ceiling is explicitly unmeasured and owner-reserved (D-022), so `rental` here is a routing "
    "destination, not a claim that the fold succeeds."
)

OUT_COLUMNS = (
    "census_accession", "census_class", "span_aa", "span_start", "span_end", "span_rule",
    "boundary_method", "band", "tier", "tier_reason", "dtype", "chunk_size", "fold_order",
    "span_definition", "guards",
)

#: ⚠ THE MANIFEST IS THE PRE-REGISTRATION OF WHAT FOLDS AND HOW. **How belongs in it.**
#: Every census row folds a sliced ECD — it has coordinates by construction, since a row without
#: them is `not_foldable` and never reaches here. Ingest COPIES this; **ingest never defaults it.**
#: ⚠ A field invented at the ingest boundary is exactly the class of thing that gets invented
#: differently next time, and `core/enqueue.py` used to treat any unrecognised value as
#: "fold the whole sequence".
BOUNDARY_METHOD = "sliced_ecd"

#: ⚠⚠ TWO IDENTITIES, AND NEITHER MAY STAND FOR THE OTHER.
#:
#: Revisions 1 and 3 had **identical membership (3,468) and an identical fold order — 3,468 of
#: 3,468 — while two spans differed** (`P51654` 529→195, `Q13421` 561→302). The seeded shuffle keys
#: on the accession SET, so an unchanged order says nothing about whether the manifest changed.
#: **A reader diffing r1 against r3 by row count, membership or order would have concluded nothing
#: moved — on the revision where the whole point of the work moved.**
#:
#: So the manifest carries two numbers with two jobs:
#:
#: · `fold_order_key`        — what the shuffle is keyed on. ⚠ Deliberately membership-only, so a
#:                             fold order stays reproducible ACROSS span revisions.
#: · `manifest_content_hash` — what the manifest SAYS. Covers the coordinates, the band, the tier,
#:                             the rule that produced the span and the definition version.
#:
#: ⚠ One number standing for both is the defect this exists to prevent.
#: ⚠ `boundary_method` is IN the tuple: a row that folds whole and a row that folds sliced are not
#: the same row, even with identical coordinates.
CONTENT_FIELDS = ("census_accession", "span_start", "span_end", "boundary_method", "band", "tier",
                  "span_rule", "span_definition")

#: ⚠⚠ THE IDENTITY FUNCTION IS ITSELF VERSIONED, and two hashes computed by different functions
#: must never be compared without both versions named — the same rule that governs the two span
#: definitions and the two band-split versions.
#:
#: · **1** — revisions 1-3. `span_start`/`span_end`/`boundary_method` did not exist, so the tuple
#:   degenerated to (accession, band, tier, rule, definition). ⚠ **A span change that moved neither
#:   band nor tier would still collide.** r1 and r3 differ only because both changed spans also
#:   moved band and tier.
#: · **2** — revision 4. Coordinates present.
#: · **3** — revision 5 onward. `boundary_method` present.
#:
#: ⚠ Without this, r3→r4→r5 hashes differ for two reasons at once — the content changed AND the
#: function changed — and nobody downstream can separate them.
IDENTITY_FN_VERSION = 3


def sha256_of(path: Path) -> str:
    """⚠ LF-normalised, so a checkout's line endings cannot change an artifact's identity."""
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def fold_order_key(rows: list[dict[str, Any]]) -> str:
    """⚠ MEMBERSHIP ONLY, deliberately. The fold order must stay reproducible across span
    revisions, so this must NOT move when a span moves. `manifest_content_hash` is what moves."""
    payload = "\n".join(sorted(r["census_accession"] for r in rows))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def manifest_content_hash(rows: list[dict[str, Any]]) -> str:
    """⚠ WHAT THE MANIFEST SAYS, not who is in it. Moves when any coordinate, band, tier, rule or
    definition version moves — including when membership is untouched."""
    payload = "\n".join(
        "\t".join(str(r.get(f, "")) for f in CONTENT_FIELDS)
        for r in sorted(rows, key=lambda x: x["census_accession"]))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def band_of(span: Optional[int]) -> str:
    """⚠ A ROUTING BAND, not an eligibility test. Every one of these folds."""
    if span is None:
        return "not_foldable"
    if span <= LOCAL_CEILING.known_good:
        return "local"
    if span < LOCAL_CEILING.known_bad:
        return "untested_band"      # (440, 630) — unmeasured, routed to rental, still ranked
    return "above_local"


def manifest_rows(census_class: str) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    src = CENSUS / SOURCES[census_class]
    with src.open(encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))

    foldable, skipped = [], Counter()
    for r in rows:
        raw = str(r.get("span_aa", "")).strip()
        if not raw:
            # ⚠ NAMED, never a silent drop. A row with no span is not foldable, and the REASON is
            # what distinguishes "measured and absent" from "never asked".
            skipped[r.get("span_category") or f"fetch_ineligible:{r.get('no_span_reason','')[:40]}"] += 1
            continue
        span = int(raw)
        tier, reason = tier_for_span(span)
        foldable.append({
            "census_accession": r["census_accession"],
            "census_class": r["census_class"],
            "span_aa": span,
            "span_start": r.get("span_start", ""),
            "span_end": r.get("span_end", ""),
            "boundary_method": BOUNDARY_METHOD,
            "span_rule": r["span_rule"],
            "band": band_of(span),
            "tier": tier,
            "tier_reason": reason or "",
            "dtype": TIER_RECIPE[tier]["dtype"],
            "chunk_size": TIER_RECIPE[tier]["chunk_size"],
            "fold_order": None,                       # ⚠ filled after the seeded shuffle
            "span_definition": V2_RULED_VOCABULARY,
            "guards": r.get("guards", ""),
        })

    meta = {
        "source_file": src.name,
        "source_sha256": sha256_of(src),
        "source_rows": len(rows),
        "foldable": len(foldable),
        "not_foldable_by_reason": dict(sorted(skipped.items())),
        "span_definition": V2_RULED_VOCABULARY,
    }
    return foldable, meta


def run(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(prog="python scripts/census_manifest.py", description=__doc__)
    # ⚠ REQUIRED. There is no default seed, because a default is a seed nobody chose and everybody
    # inherits — and it would make "the seed was recorded before the shuffle" vacuously true.
    ap.add_argument("--seed", type=int, required=True,
                    help="⚠ recorded BEFORE the shuffle; a fold order must be reproducible from it")
    ap.add_argument("--class", dest="classes", action="append", required=True,
                    choices=["surface", "non_surface"],
                    help="⚠ `unclassified` is deliberately absent — F-016")
    ap.add_argument("--out", default=str(CENSUS / "census_manifest.csv"))
    ap.add_argument("--revision", type=int, default=1,
                    help="⚠ manifest revision. Earlier revisions are RETAINED, never overwritten")
    ap.add_argument("--rebuild-reason", default="",
                    help="⚠ required for revision > 1 — a rebuild with no stated reason is "
                         "indistinguishable from a rerun that liked its answer better")
    args = ap.parse_args(argv)

    out = Path(args.out)
    prov_path = out.parent / f"{out.stem}.provenance.json"

    # ⚠⚠ THE SEED IS WRITTEN TO DISK BEFORE ANY SHUFFLE HAPPENS. If the run dies after this line,
    # the record of what seed was intended survives — which is the point. A seed reported after a
    # successful run is a seed that could have been retried until the order looked good.
    per_class = {c: manifest_rows(c) for c in args.classes}
    if args.revision > 1 and not args.rebuild_reason:
        raise SystemExit("⚠ --rebuild-reason is required for revision > 1")
    provenance: dict[str, Any] = {
        "seed": args.seed,
        "manifest_revision": args.revision,
        "rebuild_reason": args.rebuild_reason,
        # ⚠ THE SEED IS PRESERVED ACROSS THE REBUILD and the order still differs, because the
        # POPULATION differs. Stated here so a later reader does not read a changed order as a
        # broken seed. What the pre-registration protects is that the seed was fixed before any
        # order was seen — and that survives a rebuild it did not choose.
        "seed_preserved_across_rebuild": args.revision > 1,
        "order_differs_because_population_differs": args.revision > 1,
        "seed_recorded_before_shuffle": True,
        "span_definition": V2_RULED_VOCABULARY,
        "span_definition_note": (
            "D-081: the 82-target cohort is frozen under v1-extracellular-substring-2026-07-21. "
            "Counts under the two definitions are not comparable unless both are named."),
        "attention_tilt_limitation": ATTENTION_TILT,
        "largest_contiguous_disclosure": LARGEST_CONTIGUOUS_DISCLOSURE,
        "span_length_disclosure_note": SPAN_LENGTH_DISCLOSURE_NOTE,
        # ⚠ The determinism control (4a) runs with the worker IDLE and nothing enqueued, so any
        # ceiling it measures is SINGLE-PROCESS headroom. Under concurrent operation the effective
        # ceiling is lower by the worker's model footprint, which is unknown until its first claim.
        "ceiling_is_single_process": True,
        "concurrency_caveat": (
            "Any measured fold ceiling reflects single-process headroom: the probe ran with the "
            "worker idle and holding no model. The worker's _MODEL_CACHE is module-level and "
            "therefore PER-PROCESS, so a probe and a worker folding concurrently hold two copies "
            "of the weights on one card. ⚠ Operating rule: do not enqueue a protein within "
            "800 MiB of the measured ceiling until one fold has completed with the worker actively "
            "holding its model."),
        "ceiling_recipe": {
            "hardware": LOCAL_CEILING.hardware, "dtype": LOCAL_CEILING.dtype,
            "chunk_size": LOCAL_CEILING.chunk_size, "known_good": LOCAL_CEILING.known_good,
            "known_bad": LOCAL_CEILING.known_bad, "provenance": LOCAL_CEILING.provenance,
        },
        "classes": {c: meta for c, (_, meta) in per_class.items()},
        "shuffled": False,
    }
    prov_path.parent.mkdir(parents=True, exist_ok=True)
    prov_path.write_text(json.dumps(provenance, indent=2), encoding="utf-8")
    print(f"⚠ seed {args.seed} recorded to {prov_path.name} BEFORE the shuffle")

    rows: list[dict[str, Any]] = []
    for c in args.classes:
        rows.extend(per_class[c][0])

    # ⚠ Sorted to a canonical order FIRST, so the shuffle is the only source of order and the
    # result depends on the seed alone rather than on dict iteration or file order.
    rows.sort(key=lambda r: (r["census_class"], r["census_accession"]))
    random.Random(args.seed).shuffle(rows)
    for i, r in enumerate(rows, 1):
        r["fold_order"] = i

    with out.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(OUT_COLUMNS))
        w.writeheader()
        w.writerows(rows)

    bands = Counter(r["band"] for r in rows)
    tiers = Counter(r["tier"] for r in rows)
    by_class = Counter(r["census_class"] for r in rows)
    lengths = sorted(int(r["span_aa"]) for r in rows)
    import statistics as _st
    _q = _st.quantiles(lengths, n=4)
    provenance.update(shuffled=True, manifest_rows=len(rows),
                      span_length_distribution={
                          "n": len(lengths), "min": lengths[0], "q1": round(_q[0]),
                          "median": round(_q[1]), "q3": round(_q[2]), "max": lengths[-1],
                          "mean": round(_st.mean(lengths), 1),
                          "below_50": sum(1 for x in lengths if x < 50),
                          "below_100": sum(1 for x in lengths if x < 100),
                          "below_150": sum(1 for x in lengths if x < 150),
                      },
                      manifest_sha256=sha256_of(out),
                      # ⚠ BOTH, LABELLED DISTINCTLY. Never one number standing for both.
                      fold_order_key=fold_order_key(rows),
                      fold_order_key_covers="membership only: the census_accession set — stable across span "
                                            "revisions BY DESIGN",
                      manifest_content_hash=manifest_content_hash(rows),
                      manifest_content_hash_covers=list(CONTENT_FIELDS),
                      # ⚠ Two hashes computed by different functions are not comparable without
                      # both versions named.
                      identity_fn_version=IDENTITY_FN_VERSION,
                      identity_fn_version_note=(
                          "1 = revisions 1-3, no coordinates and no boundary_method (the tuple "
                          "degenerates to accession/band/tier/rule/definition and a span change "
                          "that moved neither band nor tier would still collide); "
                          "2 = revision 4, coordinates present; "
                          "3 = revision 5 onward, boundary_method present"),
                      bands=dict(sorted(bands.items())), tiers=dict(sorted(tiers.items())),
                      rows_by_class=dict(sorted(by_class.items())),
                      first_10_fold_order=[(r["fold_order"], r["census_accession"], r["tier"])
                                           for r in rows[:10]])
    prov_path.write_text(json.dumps(provenance, indent=2), encoding="utf-8")

    print(f"wrote {out} | {len(rows)} foldable rows")
    for c in args.classes:
        m = per_class[c][1]
        print(f"{c} | source {m['source_file']} sha256 {m['source_sha256'][:16]}… | "
              f"rows {m['source_rows']} | foldable {m['foldable']}")
        print(f"{c} | not foldable, by reason | {json.dumps(m['not_foldable_by_reason'])}")
    print(f"bands (routing, NOT eligibility) | {json.dumps(dict(sorted(bands.items())))}")
    print(f"tiers | {json.dumps(dict(sorted(tiers.items())))}")
    print(f"⚠ every band folds; sum of bands {sum(bands.values())} == manifest rows {len(rows)}")
    print(f"first 10 of the seeded fold order | {provenance['first_10_fold_order']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
