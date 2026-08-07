#!/usr/bin/env python3
"""THE §3 GATE. Read-only, cache only, no network, no write to the repo.

Does the vocabulary defect touch the 82? If any of the 82 carry a Topological domain outside the
"extracellular" substring match, the committed F-004/F-017 features were measured under a definition
about to change and the two stop being comparable.

Also reports the per-PROTEIN reachable/unreachable split the owner's §2 ruling asks for.
"""
from __future__ import annotations

import csv
import json
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CACHE = REPO / "data" / "census" / "spancache"

# ⚠ The owner's §2 ruling: BIOLOGICAL, not lexical. Secretory-pathway faces reach the plasma
# membrane. Mitochondrial, peroxisomal and nuclear faces do not.
REACHABLE = ("lumenal", "vesicular", "vacuolar", "perinuclear space", "intragranular",
             "exoplasmic loop", "extracellular")
UNREACHABLE = ("mitochondrial", "nuclear", "peroxisomal", "mother cell")
CYTO = ("cytoplasmic",)


def klass(d: str) -> str:
    dl = d.lower()
    if "extracellular" in dl:
        return "extracellular"          # already caught by the current filter
    # ⚠ "Mother cell cytoplasmic" and "Perinuclear space" both contain a trap substring; the
    # unreachable check runs FIRST only for terms that are unambiguous, so order matters.
    if "perinuclear space" in dl:
        return "reachable"
    if any(t in dl for t in CYTO):
        return "cytoplasmic"
    if any(t in dl for t in UNREACHABLE):
        return "unreachable"
    if any(t in dl for t in REACHABLE):
        return "reachable"
    return "unclassified_term:" + d


def tds(data):
    for f in data.get("features") or []:
        if f.get("type") != "Topological domain":
            continue
        loc = f.get("location") or {}
        s = (loc.get("start") or {}).get("value")
        e = (loc.get("end") or {}).get("value")
        yield (f.get("description", "") or ""), s, e


def has_tm(data):
    return any(f.get("type") == "Transmembrane" for f in (data.get("features") or []))


def load(acc):
    p = CACHE / f"{acc}.json"
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except ValueError:
        return None


# ── the 82 ──────────────────────────────────────────────────────────────────
accs, labels = [], {}
for line in (REPO / "data" / "cohort_82_accessions.txt").read_text(encoding="utf-8").splitlines():
    line = line.strip()
    if not line or line.startswith("#"):
        continue
    parts = [p for p in line.replace(",", " ").split() if p]
    accs.append(parts[0])
    labels[parts[0]] = parts[1] if len(parts) > 1 else ""

committed = {}
with (REPO / "data" / "cohort_82_ecd.csv").open(encoding="utf-8", newline="") as fh:
    for r in csv.DictReader(fh):
        committed[r["accession"]] = r

print(f"the 82 | accessions read = {len(accs)} | committed ECD rows = {len(committed)}")
missing_cache = [a for a in accs if not (CACHE / f"{a}.json").exists()]
print(f"the 82 | in spancache = {len(accs) - len(missing_cache)} | NOT cached = {len(missing_cache)}")
if missing_cache:
    print(f"  ⚠ NOT CACHED (cannot be answered offline): {missing_cache}")

affected, clean, unread = [], [], []
for a in accs:
    d = load(a)
    if d is None:
        unread.append(a)
        continue
    rows = list(tds(d))
    outside = [(desc, s, e, klass(desc)) for desc, s, e in rows if "extracellular" not in desc.lower()]
    noncyto = [o for o in outside if o[3] in ("reachable", "unreachable")
               or o[3].startswith("unclassified_term")]
    cur = committed.get(a, {})
    cur_largest = cur.get("largest_span_aa", "")
    if noncyto:
        # what the span WOULD become if the reachable terms were admitted
        widened = [(s, e) for desc, s, e in rows
                   if klass(desc) in ("extracellular", "reachable") and s and e]
        new_largest = max((e - s + 1 for s, e in widened), default=None)
        affected.append((a, labels.get(a, ""), cur_largest, new_largest, noncyto))
    else:
        clean.append(a)

print()
print(f"§3 GATE | of {len(accs) - len(unread)} readable: AFFECTED = {len(affected)} | clean = {len(clean)}"
      f" | unreadable = {len(unread)}")
print()
for a, lab, cur, new, noncyto in affected:
    terms = Counter(f"{d} [{k}]" for d, _, _, k in noncyto)
    print(f"  {a:<8} {lab:<10} committed largest_span_aa={cur:<6} widened→{new}")
    for t, n in terms.most_common():
        print(f"      {n} x {t}")

# ── the per-PROTEIN reachable/unreachable split over the no_topology bands ──
print()
print("PER-PROTEIN split of the no_topology rows (the §2 ruling applied to the census)")
for cls, path in (("surface", "spans_surface.csv"), ("annex", "spans_annex.csv")):
    with (REPO / "data" / "census" / path).open(encoding="utf-8", newline="") as fh:
        rows = [r for r in csv.DictReader(fh)
                if r["no_topology_reason"] and r["fetched_on"] and r["fetch_failed"] != "true"]
    c = Counter()
    terms = Counter()
    for r in rows:
        d = load(r["census_accession"])
        if d is None:
            c["cache_miss"] += 1
            continue
        ks = {klass(desc) for desc, _, _ in tds(d)}
        for desc, _, _ in tds(d):
            terms[f"{desc} [{klass(desc)}]"] += 1
        if "reachable" in ks or any(k.startswith("unclassified_term") for k in ks):
            c["RECOVERABLE (a reachable face)"] += 1
        elif "unreachable" in ks:
            c["unreachable face only (mito/perox/nuclear)"] += 1
        elif "cytoplasmic" in ks:
            c["cytoplasmic-only TD"] += 1
        elif has_tm(d):
            c["TM but no TD at all"] += 1
        else:
            c["no membrane evidence at all"] += 1
    print(f"\n  {cls} | no_topology rows = {len(rows)}")
    for k, n in c.most_common():
        print(f"      {k:<46} {n}")
    print(f"      {'':<46} ---- sum {sum(c.values())}")
    unk = [t for t in terms if "[unclassified_term" in t]
    if unk:
        print(f"      ⚠ TERMS NOT IN THE RULING: {sorted(unk)}")
