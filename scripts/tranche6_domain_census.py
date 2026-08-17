"""Task A of ORDERS-Code-2026-08-18 — the boundary-source domain census over the 141.

Scope is **D-098**: the 141 past-context rows (`tranche=5`, `span_aa > 1026`), NOT the ten proteins
that motivated the ruling. `boundary_method` is a column and a column applies to every row that
carries it.

    python scripts/tranche6_domain_census.py --source uniprot          # cache-only, no network
    python scripts/tranche6_domain_census.py --preflight               # the F-041 coordinate check
    python scripts/tranche6_domain_census.py --source interpro --probe Q14517   # one accession
    python scripts/tranche6_domain_census.py --source interpro         # the 141-accession pull

⚠⚠ TWO NUMBERS, NEITHER ALLOWED TO STAND ALONE (order §1). `n_domain` over the CHAIN and the number
of domains inside the V2 SPAN are different quantities, and the naive count is the chain. A
cytoplasmic-tail domain is a domain; it is not a domain we would fold. Both are emitted on every
row. This is F-037 one level down and it must not be rediscovered after a fold.

⚠ EVERY ABSENCE IS A CATEGORY. A domain whose coordinates cannot be resolved becomes
`unknown_coordinates`, never a silent drop; the bucket-sum invariant is what proves it.

⚠ A PERMISSION DENIAL OR RATE-LIMIT REFUSAL IS STOP-AND-REPORT — never a retry, never a
per-accession re-query. Per-accession retry is where shopping hides once the endpoint and the
accession set are fixed (order §1 A2). The disk cache makes a resumed run free.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any, Iterable, Optional

REPO = Path(__file__).resolve().parents[1]

MANIFEST = REPO / "data" / "census" / "census_manifest.v7.csv"
UNIPROT_CACHE = REPO / "data" / "census" / "spancache"
INTERPRO_CACHE = REPO / "data" / "census" / "interprocache"

#: ⚠ The endpoint is a COMMITTED CONSTANT, not a literal in a call (order §1 A2). Changing where
#: the boundaries come from is a change to the record, and it should show up in a diff.
INTERPRO_ENDPOINT = (
    "https://www.ebi.ac.uk/interpro/api/entry/InterPro/protein/UniProt/{accession}/"
    "?page_size=200"
)

#: UniProt splits a tandem array across two feature types. ⚠ `Repeat` is NOT optional: dropping it
#: loses 34 LDL-receptor class B repeats from LRP1 alone and the survivor still looks plausible.
DOMAIN_LIKE = ("Domain", "Repeat")

TRAINED_CONTEXT = 1026

UNKNOWN_COORDINATE = "unknown_coordinates"

#: Databases whose UniProtKB cross-reference was checked for coordinates by F-041.
MEMBER_DBS = ("Pfam", "InterPro", "SMART", "PROSITE", "CDD", "Gene3D",
              "SUPFAM", "PANTHER", "FunFam")


# ────────────────────────────────────────────────────────────────────────────── bucketing ──

@dataclass
class DomainCounts:
    """⚠ Chain counts and span counts are SEPARATE FIELDS on purpose. A caller that wants "how
    many domains" must choose which question it is asking, in writing."""

    n_domain_chain: int = 0
    n_repeat_chain: int = 0
    n_domainlike_chain: int = 0

    n_wholly_inside_span: int = 0
    n_straddling_span: int = 0
    n_wholly_outside_span: int = 0
    n_unknown_coordinates: int = 0

    residues_in_domains_span: int = 0
    residues_in_span_not_in_any_domain: int = 0

    categories: dict = field(default_factory=dict)

    def buckets_account_for_every_feature(self) -> bool:
        """The invariant that makes the unknown-coordinate branch provable by revert: delete the
        branch and a real domain vanishes from every bucket while the chain count is unchanged."""
        return (
            self.n_wholly_inside_span
            + self.n_straddling_span
            + self.n_wholly_outside_span
            + self.n_unknown_coordinates
        ) == self.n_domainlike_chain


def domain_like_features(doc: dict) -> list[dict]:
    """`Domain` and `Repeat` features, in file order. Non-domain features are excluded."""
    return [f for f in doc.get("features", []) if f.get("type") in DOMAIN_LIKE]


def _coords(feature: dict) -> tuple[Optional[int], Optional[int]]:
    """(start, end), or (None, None) when either endpoint is unresolvable.

    ⚠ An `UNKNOWN` modifier is unresolvable even when a number is present — the number is a
    guess the annotation itself declines to stand behind.
    """
    loc = feature.get("location") or {}
    out = []
    for key in ("start", "end"):
        node = loc.get(key) or {}
        value = node.get("value")
        if value is None or node.get("modifier") == "UNKNOWN":
            return (None, None)
        out.append(int(value))
    return (out[0], out[1])


def bucket_domains(features: Iterable[dict], *, span_start: int, span_end: int) -> DomainCounts:
    """Bucket domain-like features against the V2 span, and account for the span's residues.

    ⚠ Residue coverage is CLIPPED to the span and de-overlapped, so
    `residues_in_domains_span + residues_in_span_not_in_any_domain == len(span)` always. Summing
    raw feature lengths instead lets the second number go negative, and nothing notices.
    """
    counts = DomainCounts()
    covered: set[int] = set()

    for f in features:
        counts.n_domainlike_chain += 1
        if f.get("type") == "Domain":
            counts.n_domain_chain += 1
        elif f.get("type") == "Repeat":
            counts.n_repeat_chain += 1

        a, b = _coords(f)
        if a is None or b is None:
            counts.n_unknown_coordinates += 1
            counts.categories[UNKNOWN_COORDINATE] = counts.categories.get(UNKNOWN_COORDINATE, 0) + 1
            continue

        if b < span_start or a > span_end:
            counts.n_wholly_outside_span += 1
            continue
        if a >= span_start and b <= span_end:
            counts.n_wholly_inside_span += 1
        else:
            counts.n_straddling_span += 1

        covered.update(range(max(a, span_start), min(b, span_end) + 1))

    span_len = span_end - span_start + 1
    counts.residues_in_domains_span = len(covered)
    counts.residues_in_span_not_in_any_domain = span_len - len(covered)
    return counts


# ─────────────────────────────────────────────────────────────────────────────── the 141 ──

def past_context_rows(manifest: Path = MANIFEST) -> list[dict[str, str]]:
    """The D-098 population: `tranche=5` and `span_aa > 1026`. ⚠ Strictly greater — 1,026 is the
    last in-context length, and a `<=` here would silently add rows the ruling did not scope."""
    with manifest.open(encoding="utf-8") as fh:
        rows = [r for r in csv.DictReader(fh)
                if r.get("tranche") == "5" and int(r["span_aa"]) > TRAINED_CONTEXT]
    return rows


# ───────────────────────────────────────────────────────────────────────── F-041 preflight ──

def crossref_coordinate_report(cache: Path = UNIPROT_CACHE, limit: Optional[int] = None) -> dict:
    """⚠ The order's A1 gate: do Pfam/InterPro cross-references carry coordinates?

    If they do, A2 is unnecessary and the order is wrong — say so and stop. F-041 already answered
    this cache-wide (they do not), and this reproduces it rather than citing it.
    """
    files = sorted(cache.glob("*.json"))
    if limit:
        files = files[:limit]
    declares: dict[str, int] = {}
    total: dict[str, int] = {}
    with_coords: dict[str, int] = {}

    for p in files:
        doc = json.loads(p.read_bytes().decode("utf-8"))
        for x in doc.get("uniProtKBCrossReferences", []):
            db = x.get("database")
            if db not in MEMBER_DBS:
                continue
            total[db] = total.get(db, 0) + 1
            keys = {q.get("key") for q in x.get("properties", [])}
            if "MatchStatus" in keys:
                declares[db] = declares.get(db, 0) + 1
            if {"location", "start", "end", "begin", "fragments"} & set(x.keys()):
                with_coords[db] = with_coords.get(db, 0) + 1

    return {
        "n_entries_scanned": len(files),
        "xrefs_total": total,
        "xrefs_declaring_matchstatus": declares,
        "xrefs_carrying_coordinates": with_coords,
        "any_coordinates": bool(with_coords),
    }


# ────────────────────────────────────────────────────────────────────────── interpro pull ──

class StopAndReport(RuntimeError):
    """⚠ Raised on a refusal. NEVER caught and retried — the order forbids it by name."""


def _interpro_fetch(accession: str, *, timeout: int = 60) -> tuple[dict, str]:
    """One request. Returns (payload, release). ⚠ A 403/429 raises StopAndReport."""
    url = INTERPRO_ENDPOINT.format(accession=accession)
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            release = resp.headers.get("InterPro-Version") or "release_not_reported"
            return json.loads(resp.read().decode("utf-8")), release
    except urllib.error.HTTPError as e:
        if e.code in (401, 403, 429):
            raise StopAndReport(
                f"⚠ HTTP {e.code} on {accession} — STOP AND REPORT. "
                "The order forbids a retry or a per-accession re-query."
            ) from e
        if e.code == 404:
            return {"results": [], "_status": "not_found"}, "release_not_reported"
        raise


def interpro_cached(accession: str, cache: Path = INTERPRO_CACHE) -> tuple[dict, str, str]:
    """Disk-cached fetch. Returns (payload, release, fetched_on).

    ⚠ The cache stores the raw payload AND the date/release it was read under, because a cached
    record is still a record measured on some date — a table that cannot say when its inputs were
    fetched is not checkable (census_spans_v2's rule, inherited verbatim).
    """
    cache.mkdir(parents=True, exist_ok=True)
    path = cache / f"{accession}.json"
    if path.is_file():
        blob = json.loads(path.read_bytes().decode("utf-8"))
        return blob["payload"], blob["interpro_release"], blob["fetched_on"]

    payload, release = _interpro_fetch(accession)
    stamp = date.today().isoformat()
    path.write_text(
        json.dumps({"payload": payload, "interpro_release": release, "fetched_on": stamp}),
        encoding="utf-8",
    )
    return payload, release, stamp


def interpro_intervals(payload: dict) -> list[dict]:
    """Flatten InterPro match locations into {accession, name, type, start, end} intervals.

    ⚠ A match may have MULTIPLE fragments (discontinuous domains). Each fragment is its own
    interval; collapsing them to (min, max) would invent residues the match does not claim.
    """
    out: list[dict] = []
    for result in payload.get("results", []):
        meta = result.get("metadata", {}) or {}
        for prot in result.get("proteins", []) or []:
            for loc in prot.get("entry_protein_locations", []) or []:
                for frag in loc.get("fragments", []) or []:
                    if frag.get("start") is None or frag.get("end") is None:
                        continue
                    out.append({
                        "entry": meta.get("accession", ""),
                        "name": meta.get("name", ""),
                        "type": meta.get("type", ""),
                        "start": int(frag["start"]),
                        "end": int(frag["end"]),
                    })
    return out


#: ⚠⚠ PRE-REGISTERED, on the Q14517 probe alone, BEFORE any of the 141 was pulled (order §0 P1:
#: picking a source after seeing results is how a boundary gets chosen for the answer it gives).
#:
#: InterPro returns overlapping annotations of several `type`s over the same residues. On FAT1,
#: `IPR000742` (EGF-like domain) and `IPR001881` (EGF-like calcium-binding) cover 4013-4050 and
#: 4016-4050 — the same region, twice — and `IPR000152` is a `ptm` SITE, not a domain.
#:
#: Only `domain` and `repeat` denote a bounded structural unit comparable to UniProt's
#: `Domain`/`Repeat`. `family` and `homologous_superfamily` typically span the whole chain;
#: `ptm`, `site`, `conserved_site`, `binding_site` and `active_site` are point features.
#: ⚠ Counting all types would compare a different object and the agreement table would be
#: meaningless — F-038's shape, a true number about the wrong population.
INTERPRO_BOUNDARY_TYPES = ("domain", "repeat")


def as_features(intervals: list[dict], *, types: Optional[tuple[str, ...]] = INTERPRO_BOUNDARY_TYPES
                ) -> list[dict]:
    """Adapt InterPro intervals to the same shape `bucket_domains` consumes, so ONE bucketing
    implementation serves every source. ⚠ Two bucketers would be two paths to one quantity.

    `types=None` keeps every type — used only to report what the filter excluded, never to
    produce the comparison.
    """
    kept = [i for i in intervals if types is None or (i.get("type") or "").lower() in types]
    return [{
        "type": "Repeat" if (i.get("type") or "").lower() == "repeat" else "Domain",
        "description": f"{i['entry']} {i['name']}".strip(),
        "location": {"start": {"value": i["start"], "modifier": "EXACT"},
                     "end": {"value": i["end"], "modifier": "EXACT"}},
    } for i in kept]


# ───────────────────────────────────────────────────────────────────── A3 agreement table ──

#: ⚠⚠ REPORTED AT EVERY VALUE, NEVER ONE (order §1 A3). A single tolerance is a dial wearing the
#: costume of a measurement: whichever k makes the sources agree is the k that gets quoted.
AGREEMENT_K = (0, 5, 10, 25, 50)


def boundaries_of(features: Iterable[dict]) -> list[int]:
    """Every start and every end, in order. ⚠ A domain contributes TWO boundaries — a rule that
    matched starts only would call two sources agreeing while their domains had different lengths."""
    out: list[int] = []
    for f in features:
        a, b = _coords(f)
        if a is None or b is None:
            continue
        out.extend((a, b))
    return out


def matched_within(source: Iterable[int], other: Iterable[int], k: int) -> int:
    """How many of `source`'s boundaries have SOME counterpart in `other` within ±k.

    ⚠⚠ DIRECTIONAL, and both directions must be reported. If `other` has four boundaries clustered
    near one of `source`'s, then source→other is 1 and other→source is 4. Quoting either alone is a
    claim about the wrong denominator.
    """
    others = sorted(other)
    if not others:
        return 0
    import bisect
    n = 0
    for x in source:
        i = bisect.bisect_left(others, x - k)
        if i < len(others) and others[i] <= x + k:
            n += 1
    return n


# ─────────────────────────────────────────────────────────────────────────────────── CLI ──

FIELDS = [
    "census_accession", "span_aa", "span_start", "span_end", "source",
    "n_domain_chain", "n_repeat_chain", "n_domainlike_chain",
    "n_domains_wholly_inside_the_V2_span", "n_domains_straddling_the_span_boundary",
    "n_domains_wholly_outside_the_span", "n_unknown_coordinates",
    "residues_in_domains", "residues_in_span_not_in_any_domain",
    "buckets_sum_ok", "fetched_on", "source_release", "status",
]


def row_for(entry: dict[str, str], counts: DomainCounts, *, source: str,
            fetched_on: str, release: str, status: str) -> dict[str, Any]:
    return {
        "census_accession": entry["census_accession"],
        "span_aa": entry["span_aa"],
        "span_start": entry["span_start"],
        "span_end": entry["span_end"],
        "source": source,
        "n_domain_chain": counts.n_domain_chain,
        "n_repeat_chain": counts.n_repeat_chain,
        "n_domainlike_chain": counts.n_domainlike_chain,
        "n_domains_wholly_inside_the_V2_span": counts.n_wholly_inside_span,
        "n_domains_straddling_the_span_boundary": counts.n_straddling_span,
        "n_domains_wholly_outside_the_span": counts.n_wholly_outside_span,
        "n_unknown_coordinates": counts.n_unknown_coordinates,
        "residues_in_domains": counts.residues_in_domains_span,
        "residues_in_span_not_in_any_domain": counts.residues_in_span_not_in_any_domain,
        "buckets_sum_ok": counts.buckets_account_for_every_feature(),
        "fetched_on": fetched_on,
        "source_release": release,
        "status": status,
    }


def _span_features(entry: dict[str, str]) -> tuple[list[dict], list[dict]]:
    """(uniprot_features, interpro_features) for one row, both clipped to nothing — the span
    filter happens in bucketing, and boundaries are compared over the whole chain deliberately:
    a boundary just outside the span is still evidence about whether the sources agree."""
    acc = entry["census_accession"]
    doc = json.loads((UNIPROT_CACHE / f"{acc}.json").read_bytes().decode("utf-8"))
    up = domain_like_features(doc)
    payload, _, _ = interpro_cached(acc)
    ip = as_features(interpro_intervals(payload))
    return up, ip


def _agreement_report() -> int:
    """Task A3 — pairwise boundary agreement at every k, both directions, never one number."""
    rows = past_context_rows()
    print(f"population: {len(rows)} rows (D-098)\n")

    tot_up = tot_ip = 0
    hits_up = {k: 0 for k in AGREEMENT_K}
    hits_ip = {k: 0 for k in AGREEMENT_K}
    per_row = []

    for entry in rows:
        try:
            up, ip = _span_features(entry)
        except FileNotFoundError:
            continue
        bu, bi = boundaries_of(up), boundaries_of(ip)
        tot_up += len(bu)
        tot_ip += len(bi)
        row = {"acc": entry["census_accession"], "n_up": len(bu), "n_ip": len(bi)}
        for k in AGREEMENT_K:
            mu = matched_within(bu, bi, k)
            mi = matched_within(bi, bu, k)
            hits_up[k] += mu
            hits_ip[k] += mi
            row[f"up_in_ip_{k}"] = mu
            row[f"ip_in_up_{k}"] = mi
        per_row.append(row)

    print("=" * 92)
    print("A3 — BOUNDARY AGREEMENT, UniProt vs InterPro, over the 141")
    print("⚠ Both directions. A single figure hides which source is the denominator.")
    print("=" * 92)
    print(f"  UniProt boundaries  : {tot_up:,}")
    print(f"  InterPro boundaries : {tot_ip:,}\n")
    print(f"  {'k':>4s}  {'UniProt->InterPro':>22s}  {'InterPro->UniProt':>22s}")
    print("  " + "-" * 52)
    for k in AGREEMENT_K:
        a = f"{hits_up[k]:,}/{tot_up:,} ({100*hits_up[k]/tot_up:.1f}%)" if tot_up else "-"
        b = f"{hits_ip[k]:,}/{tot_ip:,} ({100*hits_ip[k]/tot_ip:.1f}%)" if tot_ip else "-"
        print(f"  {k:>4d}  {a:>22s}  {b:>22s}")

    print("\n  ⚠ rows where NEITHER source annotates anything (a category, not a zero):")
    none = [r for r in per_row if r["n_up"] == 0 and r["n_ip"] == 0]
    print(f"    {len(none)} rows" + (": " + ", ".join(r["acc"] for r in none) if none else ""))
    only_ip = [r for r in per_row if r["n_up"] == 0 and r["n_ip"] > 0]
    print(f"  ⚠ rows InterPro annotates and UniProt does NOT: {len(only_ip)}")
    for r in only_ip:
        print(f"    {r['acc']:8s} uniprot=0  interpro={r['n_ip']//2} domains")
    only_up = [r for r in per_row if r["n_ip"] == 0 and r["n_up"] > 0]
    print(f"  ⚠ rows UniProt annotates and InterPro does NOT: {len(only_up)}")
    for r in only_up:
        print(f"    {r['acc']:8s} interpro=0  uniprot={r['n_up']//2} domains")
    return 0


def run(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--source", choices=("uniprot", "interpro"))
    ap.add_argument("--preflight", action="store_true",
                    help="F-041: do cross-references carry coordinates? If yes, STOP.")
    ap.add_argument("--probe", metavar="ACC",
                    help="fetch ONE accession and print the response shape, before spending 141")
    ap.add_argument("--agreement", action="store_true",
                    help="A3: pairwise boundary agreement at k=0,5,10,25,50, both directions")
    ap.add_argument("--out", help="write rows to this CSV")
    ap.add_argument("--sleep", type=float, default=0.34, help="seconds between network calls")
    args = ap.parse_args(argv)

    if args.preflight:
        rep = crossref_coordinate_report()
        print(json.dumps(rep, indent=2))
        if rep["any_coordinates"]:
            print("\n⚠⚠ Cross-references DO carry coordinates. A2 is unnecessary and the order "
                  "is wrong. STOPPING, per order §1 A1.")
            return 2
        print("\n✓ No cross-reference carries coordinates — A2 (the network pull) IS required.")
        return 0

    if args.probe:
        payload, release, stamp = interpro_cached(args.probe)
        ivs = interpro_intervals(payload)
        print(f"accession        : {args.probe}")
        print(f"interpro_release : {release}")
        print(f"fetched_on       : {stamp}")
        print(f"results          : {len(payload.get('results', []))}")
        print(f"intervals (all)  : {len(ivs)}")
        kept = as_features(ivs)
        print(f"intervals (kept) : {len(kept)}  [types {INTERPRO_BOUNDARY_TYPES}]")
        by_type: dict[str, int] = {}
        for iv in ivs:
            t = (iv.get("type") or "?").lower()
            by_type[t] = by_type.get(t, 0) + 1
        print("by type          :")
        for t, n in sorted(by_type.items(), key=lambda kv: -kv[1]):
            mark = "  <- kept" if t in INTERPRO_BOUNDARY_TYPES else "  (excluded)"
            print(f"    {t:26s} {n:4d}{mark}")
        for iv in ivs[:8]:
            print(f"  {iv['entry']:12s} {iv['start']:6d}-{iv['end']:<6d} {iv['type']:12s} {iv['name']}")
        return 0

    if args.agreement:
        return _agreement_report()

    if not args.source:
        ap.error("one of --source, --preflight, --probe or --agreement is required")

    rows = past_context_rows()
    print(f"population: {len(rows)} rows (D-098: tranche=5, span_aa > {TRAINED_CONTEXT})",
          file=sys.stderr)

    out_rows: list[dict[str, Any]] = []
    for i, entry in enumerate(rows, 1):
        acc = entry["census_accession"]
        s0, s1 = int(entry["span_start"]), int(entry["span_end"])
        try:
            if args.source == "uniprot":
                blob = (UNIPROT_CACHE / f"{acc}.json").read_bytes()
                doc = json.loads(blob.decode("utf-8"))
                feats = domain_like_features(doc)
                release = str((doc.get("entryAudit") or {}).get("entryVersion", "")) or \
                    "release_not_reported"
                stamp = "cache"
            else:
                payload, release, stamp = interpro_cached(acc)
                feats = as_features(interpro_intervals(payload))
                if args.sleep:
                    time.sleep(args.sleep)
            counts = bucket_domains(feats, span_start=s0, span_end=s1)
            out_rows.append(row_for(entry, counts, source=args.source,
                                    fetched_on=stamp, release=release, status="ok"))
        except StopAndReport:
            raise
        except FileNotFoundError:
            out_rows.append(row_for(entry, DomainCounts(), source=args.source,
                                    fetched_on="", release="", status="not_in_cache"))
        except Exception as e:  # noqa: BLE001
            out_rows.append(row_for(entry, DomainCounts(), source=args.source,
                                    fetched_on="", release="",
                                    status=f"{type(e).__name__}: {e}"[:120]))
        if i % 25 == 0:
            print(f"  ... {i}/{len(rows)}", file=sys.stderr)

    bad = [r for r in out_rows if not r["buckets_sum_ok"]]
    if bad:
        print(f"⚠⚠ {len(bad)} rows fail the bucket-sum invariant — a domain vanished. STOP.",
              file=sys.stderr)

    if args.out:
        path = Path(args.out)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=FIELDS)
            w.writeheader()
            w.writerows(out_rows)
        print(f"wrote {len(out_rows)} rows -> {path}", file=sys.stderr)
    else:
        w = csv.DictWriter(sys.stdout, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(out_rows)

    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(run())
