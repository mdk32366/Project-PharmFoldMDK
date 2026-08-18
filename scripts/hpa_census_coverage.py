"""`CB`/`CD`/`CE1` — the pinned census↔HPA mapping, both directions, and coverage by CATEGORY.

⚠⚠ **THIS INGESTS NOTHING.** No table is created, no row is written, no schema is final. `D-093` is
a pre-registration and is **void if code precedes it**; this reports what a supplier can serve so
that `D-093 amendment 2` can be written against measurements instead of assumptions.

⚠ **THE PINNED MAPPING, and decision 6 question (3) is not answered by "we join on gene symbol".**
The census keys on **UniProt accession**; HPA keys on **Ensembl gene id**. The mapping is taken from
the UniProt entries already cached in `data/census/spancache/` — pinned by that cache, not fetched
live — and it is read **two independent ways from the same record**:

  - the `HPA` cross-reference, whose `id` is the unversioned `ENSG…`;
  - the `Ensembl` cross-reference's `GeneId` property, versioned (`ENSG….10`), stripped.

**Both are reported and compared.** ⚠ *Two paths to one quantity, compared on the numbers* — if they
ever disagree the disagreement is the finding, and a single path would never show it.

⚠⚠ **`accession_ambiguous` IS A CATEGORY, NOT A RESOLUTION RULE** (`P2`). An accession mapping to
more than one gene is **reported as ambiguous and never silently resolved** — no first-match, no
longest-match, no alphabetical. *A tie-break invented at ingest is a dial nobody recorded.*

⚠ **Every count states its key** (`P4`): `3,467` is the census manifest, `2,690` is the folded set,
`15,313` is HPA IHC's gene-name count. **A figure that does not name its denominator is not a
measurement.**

READ-ONLY. Cache-only apart from the HPA files, which are referenced BY PATH and never vendored.

Usage:
    python scripts/hpa_census_coverage.py \
        --normal-tissue <path>/normal_tissue.tsv \
        --pathology     <path>/pathology.tsv \
        [--census-api   <path>/census_api.json]
"""
from __future__ import annotations

import argparse
import csv
import json
import pathlib
import sys
from collections import Counter, defaultdict

REPO = pathlib.Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from scripts.tranche6_domain_census import MANIFEST, UNIPROT_CACHE  # noqa: E402

LABELS = REPO / "data" / "census" / "census_labels.csv"
ADC_REF = REPO / "data" / "adc_reference_mapping.csv"
W = 92


def ensg_from_entry(doc: dict) -> tuple[set[str], set[str]]:
    """(from the HPA xref, from the Ensembl xref) — both unversioned, both as SETS.

    ⚠ Sets, not scalars, because *more than one* is the `accession_ambiguous` category and a
    scalar return would have to invent a tie-break to exist at all.
    """
    hpa: set[str] = set()
    ens: set[str] = set()
    for x in doc.get("uniProtKBCrossReferences", []):
        db = x.get("database")
        if db == "HPA":
            gid = (x.get("id") or "").split(".")[0]
            if gid.startswith("ENSG"):
                hpa.add(gid)
        elif db == "Ensembl":
            for q in x.get("properties", []):
                if q.get("key") == "GeneId" and (q.get("value") or "").startswith("ENSG"):
                    ens.add(q["value"].split(".")[0])
    return hpa, ens


def norm(s: str) -> str:
    """⚠ The join key is normalised ONCE, here, and the normalisation is the thing `CB4` tests.
    A case-mismatched join returning a clean zero three times is a catalogued `F-047` member."""
    return (s or "").strip().upper()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--normal-tissue", required=True)
    ap.add_argument("--pathology", required=True)
    ap.add_argument("--census-api", help="JSON from GET /api/census; the folded set")
    args = ap.parse_args(argv)

    manifest = list(csv.DictReader(MANIFEST.open(encoding="utf-8")))
    genes = {r["census_accession"]: r["gene"]
             for r in csv.DictReader(LABELS.open(encoding="utf-8"))}

    # ── the pinned mapping, read two ways ───────────────────────────────────────────────────
    hpa_map: dict[str, set[str]] = {}
    ens_map: dict[str, set[str]] = {}
    for r in manifest:
        acc = r["census_accession"]
        doc = json.loads((UNIPROT_CACHE / f"{acc}.json").read_bytes().decode("utf-8"))
        h, e = ensg_from_entry(doc)
        hpa_map[acc], ens_map[acc] = h, e

    print("=" * W)
    print("CB1 — THE PINNED MAPPING, AND IT IS READ TWO INDEPENDENT WAYS FROM ONE RECORD")
    print("=" * W)
    print(f"  instrument : UniProt entries cached in data/census/spancache/ (pinned by the cache,")
    print(f"               not fetched live). Path A = the `HPA` cross-reference id.")
    print(f"               Path B = the `Ensembl` cross-reference `GeneId`, version stripped.")
    agree = sum(1 for a in hpa_map if hpa_map[a] == ens_map[a])
    both = sum(1 for a in hpa_map if hpa_map[a] and ens_map[a])
    disagree = [a for a in hpa_map if hpa_map[a] and ens_map[a] and hpa_map[a] != ens_map[a]]
    print(f"\n  key: one row per census_accession in census_manifest.v7.csv")
    print(f"  accessions                                    : {len(manifest):,}")
    print(f"  both paths present                            : {both:,}")
    print(f"  the two paths AGREE exactly                    : {agree:,}")
    print(f"  ⚠ the two paths DISAGREE                       : {len(disagree):,}"
          f"  {sorted(disagree)[:5] if disagree else ''}")

    # ── CB3 cardinality ─────────────────────────────────────────────────────────────────────
    print("\n" + "=" * W)
    print("CB3 — CARDINALITY OF THE HOP (counts must sum to the manifest, key stated)")
    print("=" * W)
    card = Counter()
    ambiguous: list[str] = []
    unmapped: list[str] = []
    resolved: dict[str, str] = {}
    for acc in (r["census_accession"] for r in manifest):
        ids = hpa_map[acc] or ens_map[acc]
        if len(ids) == 1:
            card["exactly_one_gene"] += 1
            resolved[acc] = next(iter(ids))
        elif len(ids) > 1:
            card["accession_ambiguous"] += 1
            ambiguous.append(acc)
        else:
            card["hpa_absent"] += 1
            unmapped.append(acc)
    for k in ("exactly_one_gene", "accession_ambiguous", "hpa_absent"):
        print(f"  {k:24s} {card.get(k, 0):6,d}")
    print(f"  {'TOTAL':24s} {sum(card.values()):6,d}   sums to the manifest: "
          f"{sum(card.values()) == len(manifest)}")
    if ambiguous:
        print(f"  ⚠⚠ ambiguous, REPORTED AND NOT RESOLVED (P2): {len(ambiguous)}")
        for a in ambiguous[:8]:
            print(f"       {a}  {genes.get(a, ''):10s} -> {sorted(hpa_map[a] or ens_map[a])}")

    # ── the HPA files ───────────────────────────────────────────────────────────────────────
    nt_by_ensg: dict[str, list[tuple[str, str, str]]] = defaultdict(list)
    nt_names: set[str] = set()
    with pathlib.Path(args.normal_tissue).expanduser().open(encoding="utf-8") as fh:
        for r in csv.DictReader(fh, delimiter="\t"):
            nt_by_ensg[norm(r["Gene"])].append(
                (r["Tissue"], r["Cell type"], (r["Level"] or "").strip()))
            nt_names.add(norm(r["Gene name"]))

    pa_by_ensg: dict[str, list[dict]] = defaultdict(list)
    with pathlib.Path(args.pathology).expanduser().open(encoding="utf-8") as fh:
        for r in csv.DictReader(fh, delimiter="\t"):
            pa_by_ensg[norm(r["Gene"])].append(r)

    # ── CB2 both directions ─────────────────────────────────────────────────────────────────
    print("\n" + "=" * W)
    print("CB2 — BOTH DIRECTIONS (Part C Step 19: a one-directional check cannot see orphans)")
    print("=" * W)
    census_ensg = {norm(g) for g in resolved.values()}
    for label, hpa_keys in (("normal_tissue.tsv", set(nt_by_ensg)),
                            ("pathology.tsv", set(pa_by_ensg))):
        print(f"\n  {label}")
        print(f"    HPA gene ids in the file                        : {len(hpa_keys):,}")
        print(f"    census ENSGs NOT present in the file            : "
              f"{len(census_ensg - hpa_keys):,}")
        print(f"    ⚠ file gene ids reached by NO census accession   : "
              f"{len(hpa_keys - census_ensg):,}")
        print(f"      (the census is a surfaceome subset, so this is expected to be large —"
              f" it is reported because an orphan count nobody states is an orphan count nobody"
              f" checks)")

    # ── CD coverage, categories BEFORE any figure ───────────────────────────────────────────
    def coverage(accs: list[str], by_ensg: dict, empty_test) -> Counter:
        c = Counter()
        for acc in accs:
            ids = hpa_map[acc] or ens_map[acc]
            if len(ids) > 1:
                c["accession_ambiguous"] += 1
            elif not ids:
                c["hpa_absent"] += 1
            else:
                rows = by_ensg.get(norm(next(iter(ids))), [])
                if not rows:
                    c["ihc_gene_absent"] += 1
                elif empty_test(rows):
                    c["ihc_panel_empty"] += 1
                else:
                    c["ihc_present"] += 1
        return c

    def nt_empty(rows):
        return all(lv in ("", "N/A", "Not representative") for _, _, lv in rows)

    def pa_empty(rows):
        return all(sum(int(float(r[c] or 0)) for c in
                       ("High", "Medium", "Low", "Not detected")) == 0 for r in rows)

    populations = [("the census manifest (3,467)", [r["census_accession"] for r in manifest])]
    if args.census_api:
        folded = [r["accession"] for r in
                  json.loads(pathlib.Path(args.census_api).read_text(encoding="utf-8"))]
        populations.append((f"the folded set ({len(folded):,})", folded))
    else:
        print("\n  ⚠ folded set: NOT SUPPLIED — a named absence, not a silent omission."
              " Pass --census-api to include it.")

    print("\n" + "=" * W)
    print("CD — COVERAGE, CATEGORIES FIRST. ⚠ NO PERCENTAGE MAY ABSORB THEM (P1)")
    print("=" * W)
    ORDER = ("ihc_present", "ihc_gene_absent", "ihc_panel_empty", "hpa_absent",
             "accession_ambiguous")
    for pop_label, accs in populations:
        for file_label, by_ensg, empty in (("normal_tissue.tsv", nt_by_ensg, nt_empty),
                                           ("pathology.tsv", pa_by_ensg, pa_empty)):
            c = coverage(accs, by_ensg, empty)
            print(f"\n  {pop_label}  ×  {file_label}")
            for k in ORDER:
                print(f"    {k:24s} {c.get(k, 0):6,d}")
            print(f"    {'TOTAL':24s} {sum(c.values()):6,d}   sums to the population: "
                  f"{sum(c.values()) == len(accs)}")

    # ── CD3 the distribution that tests §0's warning ────────────────────────────────────────
    print("\n" + "=" * W)
    print("CD3 — ⚠⚠ THE EMPIRICAL TEST OF THE 'EVERY PROTEIN IS EXPRESSED SOMEWHERE' WARNING")
    print("=" * W)
    n_cancers = Counter()
    for acc, ensg in resolved.items():
        rows = pa_by_ensg.get(norm(ensg), [])
        hit = {r["Cancer"] for r in rows
               if sum(int(float(r[c] or 0)) for c in ("High", "Medium", "Low")) > 0}
        n_cancers[len(hit)] += 1
    total_res = sum(n_cancers.values())
    print(f"  key: census accessions resolving to exactly one gene ({total_res:,}), against"
          f" pathology.tsv's 20 cancer types")
    print(f"  reaching ALL 20 cancer types with a detected level : {n_cancers.get(20, 0):,}"
          f"  ({100*n_cancers.get(20,0)/max(total_res,1):.1f}%)")
    print(f"  reaching EXACTLY ONE                               : {n_cancers.get(1, 0):,}")
    print(f"  reaching NONE                                      : {n_cancers.get(0, 0):,}")
    print(f"\n  full distribution, cancers reached -> proteins:")
    for k in sorted(n_cancers):
        bar = "#" * min(60, n_cancers[k] // 25)
        print(f"    {k:3d} : {n_cancers[k]:6,d}  {bar}")

    # ── CE1 therapeutic_precedent coverage ──────────────────────────────────────────────────
    print("\n" + "=" * W)
    print("CE1 — `therapeutic_precedent` COVERAGE (a LABEL; never a scoring feature)")
    print("=" * W)
    if not ADC_REF.exists():
        print("  ⚠ data/adc_reference_mapping.csv ABSENT — a named absence.")
    else:
        # ⚠ The file opens with a  provenance line, so a naive DictReader takes THAT as the
        # header and every column name becomes prose. Skipped explicitly rather than by
        # -style luck.
        lines = [l for l in ADC_REF.read_text(encoding="utf-8").splitlines()
                 if l.strip() and not l.lstrip().startswith("#")]
        ref = list(csv.DictReader(lines))
        print(f"  rows: {len(ref):,}   columns: {list(ref[0].keys())}")
        by_key = {k: {norm(r.get(k, "")) for r in ref if r.get(k)} for k in ref[0]}
        for pop_label, accs in populations:
            acc_set = {norm(a) for a in accs}
            gene_set = {norm(genes.get(a, "")) for a in accs} - {""}
            best = max(by_key, key=lambda k: len(by_key[k] & (acc_set | gene_set)))
            hit = by_key[best] & (acc_set | gene_set)
            print(f"    {pop_label:32s} joins best on column {best!r}: {len(hit):,} matched")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
