"""KC1 — F-048's 58, recomputed from the cache, and placed against the cohort's ecd_length range.

⚠ The order asks whether ruling 6 (span-floor refusal) and ruling 3 (out-of-range refusal) catch the
same rows. That is answerable WITHOUT census features, because ecd_length IS the span length and the
span is in the committed manifest.
"""
import csv
import json
import pathlib
import sys
from collections import Counter

REPO = pathlib.Path(r"C:\Projects\Project-PharmFoldMDK")
sys.path.insert(0, str(REPO))
from scripts.tranche6_domain_census import (  # noqa: E402
    UNIPROT_CACHE, domain_like_features, _coords, span_relation)

MANIFEST = REPO / "data" / "census" / "census_manifest.v7.csv"

rows = list(csv.DictReader(MANIFEST.open(encoding="utf-8")))
print(f"  manifest rows (census_manifest.v7.csv): {len(rows)}")

engulfing = []
checked = missing_cache = no_span = 0
for r in rows:
    acc = r["census_accession"]
    s0, s1 = r.get("span_start"), r.get("span_end")
    if not s0 or not s1:
        no_span += 1
        continue
    p = UNIPROT_CACHE / f"{acc}.json"
    if not p.exists():
        missing_cache += 1
        continue
    checked += 1
    doc = json.loads(p.read_text(encoding="utf-8"))
    s0, s1 = int(s0), int(s1)
    for feat in domain_like_features(doc):
        a, b = _coords(feat)
        if a is None or b is None:
            continue
        if span_relation(a, b, s0, s1) == "engulfing":
            engulfing.append({"acc": acc, "span": int(r["span_aa"]), "s0": s0, "s1": s1,
                              "a": a, "b": b, "type": feat.get("type"),
                              "desc": (feat.get("description") or "")[:38]})
            break

accs = sorted({e["acc"] for e in engulfing})
print(f"  rows with a numeric span      : {len(rows)-no_span}")
print(f"  rows with a cached UniProt doc: {checked}   (no cached doc: {missing_cache})")
print(f"\n  ⚠⚠ ENGULFING (F-048) accessions recomputed: {len(accs)}   [entry records 58]")

spans = [e["span"] for e in engulfing]
print(f"\n  their span_aa: min {min(spans)} · median {sorted(spans)[len(spans)//2]} · max {max(spans)}")

# the cohort's observed ecd_length range, from KA1
COH_MIN, COH_MAX = 13, 1652
COH_P05, COH_P95 = 21, 896.75
print(f"\n  the cohort's ecd_length range (KA1): strict [{COH_MIN}, {COH_MAX}] · p05-p95 [{COH_P05}, {COH_P95}]")
c = Counter()
for e in engulfing:
    s = e["span"]
    c["BELOW the cohort strict min (out of range on ecd_length alone)" if s < COH_MIN
      else ("inside strict, but below p05" if s < COH_P05 else "inside p05-p95" if s <= COH_P95
            else "above p95")] += 1
print("\n  ⚠⚠ KC1 — where the 58 fall on ecd_length, the ONE feature available without extraction:")
for k, v in c.most_common():
    print(f"    {k:62s} {v:3d}")
print(f"    {'TOTAL':62s} {len(engulfing):3d}")

print("\n  the shortest, the ones ruling 6 is written for:")
print(f"  {'acc':9s} {'span':>5s} {'span range':>13s}  engulfing feature")
print("  " + "-" * 92)
for e in sorted(engulfing, key=lambda e: e["span"])[:12]:
    # ⚠ NOT a nested same-quote f-string. That is PEP 701 (Python 3.12+) and this project runs
    # 3.11 in the venv AND in CI — the file could not even be PARSED here. Authored and run under
    # a 3.14 interpreter by mistake, which is the same "verified in a richer environment than
    # production" defect F-052 records. The span range is built first, then formatted.
    span_range = "%d-%d" % (e['s0'], e['s1'])
    print(f"  {e['acc']:9s} {e['span']:>5d} {span_range:>13s}  "
          f"{e['a']}-{e['b']} {e['type']}: {e['desc']}")

print("\n  ⚠ and are they FOLDED / in the census DB population at all?")
import csv as _csv
SP = pathlib.Path(__file__).resolve().parent
_rows=[r for r in _csv.reader((SP/"census.csv").open(encoding="utf-8")) if len(r)>=11]
census_accs = {r[1] for r in _rows if r[3]=="t"}
inn = [a for a in accs if a in census_accs]
print(f"    of the {len(accs)}, folded in protein_analyses: {len(inn)}")
print(f"    ⚠ every one of them carries NO protein_features row (KC3), so ruling 3 cannot")
print(f"      evaluate them on any feature and ruling 6 is the ONLY refusal that can fire today.")
