"""JA — re-key the rental population against the DATABASE, not against D-041.

⚠ D-041's "29 rental-tier unfolded" predates FA2's finding that 26 rental-tier targets are already
folded AND scored. FC's bands were computed against that stale 29. This measures the CURRENT set.
"""
import csv
import pathlib
import sys
from collections import Counter

REPO = pathlib.Path(r"C:\Projects\Project-PharmFoldMDK")
sys.path.insert(0, str(REPO))
from core.adc_reference import cohort_accessions, group_b_accessions, load_mapping  # noqa: E402
from core.manifest import tier_for_span  # noqa: E402

SP = pathlib.Path(__file__).resolve().parent

# ── the database's fold state, one row per protein_analyses row ─────────────────────────────
analyses = {}
for line in (SP / "analyses.tsv").read_text(encoding="utf-8").splitlines():
    p = line.split("\t")
    if len(p) < 6 or p[0].startswith("Field separator"):
        continue
    analyses[p[0].strip()] = {
        "tranche": p[1].strip(),
        "has_pdb": p[2].strip() == "t",
        "has_plddt": p[3].strip() == "t",
        "source": p[4].strip(),
        "has_features": p[5].strip() == "t",
    }

cohort = {r["accession"]: r for r in
          csv.DictReader((REPO / "data/cohort_82_ecd.csv").open(encoding="utf-8"))}
positives = group_b_accessions(load_mapping(), cohort_accessions())
scored56 = {l.split("|")[1].strip() for l in
            (SP / "scored56.txt").read_text(encoding="utf-8").splitlines() if "|" in l}

print("=" * 94)
print("JA1 — THE CURRENT UNFOLDED SET, MEASURED AGAINST THE DATABASE")
print("=" * 94)
print("  key   : the 82 cohort accessions in data/cohort_82_ecd.csv")
print("  joined: protein_analyses.input_value (input_type='uniprot')")
print("  FOLDED means: a protein_analyses row EXISTS and pdb_path IS NOT NULL")
print("          ⚠ reported beside mean_plddt and protein_features so the definition is visible")

rows = []
for acc, c in cohort.items():
    a = analyses.get(acc)
    span = c["largest_span_aa"]
    rows.append({
        "acc": acc, "gene": c["gene"],
        "span": int(span) if span else None,
        "tier": (tier_for_span(int(span))[0] if span else "no_span_measured"),
        "in_db": a is not None,
        "folded": bool(a and a["has_pdb"]),
        "plddt": bool(a and a["has_plddt"]),
        "feats": bool(a and a["has_features"]),
        "pos": acc in positives,
        "scored": acc in scored56,
    })

c = Counter()
for r in rows:
    c["no protein_analyses row" if not r["in_db"] else
      ("folded (pdb_path present)" if r["folded"] else "row exists, NOT folded")] += 1
for k, v in c.most_common():
    print(f"    {k:34s} {v:3d}")
print(f"    {'TOTAL':34s} {sum(c.values()):3d}")

unfolded = [r for r in rows if not r["folded"]]
print(f"\n  ⚠⚠ COHORT TARGETS UNFOLDED TODAY: {len(unfolded)}   (D-041 recorded 29 rental-tier unfolded)")

print("\n" + "=" * 94)
print("JA2 — LABELLED AND POSITIVE AMONG THE UNFOLDED, against BOTH denominators")
print("=" * 94)
npos = sum(1 for r in unfolded if r["pos"])
print(f"  unfolded cohort targets                          : {len(unfolded)}")
print(f"  ⚠ of those, Group B POSITIVES                     : {npos}")
print(f"  denominator A — positives scored at run 2         : {len(positives & scored56)}")
print(f"  denominator B — Group B positives across the 82   : {len(positives)}")
print(f"  ⚠ D-040's '~22 positives across the 82' is a THIRD figure and is not this one.")

print("\n" + "=" * 94)
print("JA3 — THE UNFOLDED, BUCKETED BY THE LOCAL CEILING. ROWS, NOT COUNTS")
print("=" * 94)


def band(n):
    if n is None:
        return "no_span_measured"
    return "<=440" if n <= 440 else ("441-629" if n <= 629 else ">=630")


print(f"  {'acc':9s} {'gene':10s} {'span_aa':>8s} {'band':>17s}  {'positive?':>9s}  {'in db?':>6s}")
print("  " + "-" * 88)
for r in sorted(unfolded, key=lambda r: (r["span"] is None, r["span"] or 0)):
    print(f"  {r['acc']:9s} {r['gene']:10s} "
          f"{(str(r['span']) if r['span'] else '-'):>8s} {band(r['span']):>17s}  "
          f"{('YES' if r['pos'] else '-'):>9s}  {('yes' if r['in_db'] else 'NO'):>6s}")

print("\n" + "=" * 94)
print("JA4 — FC's ANSWER RE-STATED AGAINST THE CURRENT SET. DID IT MOVE?")
print("=" * 94)
bc = Counter(band(r["span"]) for r in unfolded)
bp = Counter(band(r["span"]) for r in unfolded if r["pos"])
print(f"  {'band':>17s} {'FC (stale, n=29)':>18s} {'CURRENT':>9s} {'positives now':>14s}")
print("  " + "-" * 66)
stale = {"<=440": (0, 0), "441-629": (13, 3), ">=630": (16, 3)}
for k in ("<=440", "441-629", ">=630", "no_span_measured"):
    s = stale.get(k)
    print(f"  {k:>17s} {(f'{s[0]} ({s[1]} pos)' if s else 'n/a'):>18s} "
          f"{bc.get(k, 0):>9d} {bp.get(k, 0):>14d}")
print(f"\n  ⚠⚠ THE CEILING-CLIMB QUESTION: positives recoverable in 441-629 by climbing 440 -> ~630")
print(f"     FC said 3.  Current: {bp.get('441-629', 0)}.")

print("\n" + "=" * 94)
print("JA5 — THE 13 no_span_measured. ARE THEY STILL UNMEASURED, AND WHY?")
print("=" * 94)
nsm = [r for r in rows if r["tier"] == "no_span_measured"]
print(f"  cohort rows with no largest_span_aa in cohort_82_ecd.csv : {len(nsm)}")
cc = Counter()
for r in nsm:
    cc["folded anyway" if r["folded"] else ("row in db, unfolded" if r["in_db"] else "no db row")] += 1
for k, v in cc.most_common():
    print(f"    {k:28s} {v:3d}")
print(f"\n  {'acc':9s} {'gene':10s} {'folded?':>8s} {'plddt?':>7s} {'features?':>10s}  error (from the CSV)")
print("  " + "-" * 88)
for r in sorted(nsm, key=lambda r: r["acc"]):
    err = (cohort[r["acc"]].get("error") or "").strip()[:34]
    print(f"  {r['acc']:9s} {r['gene']:10s} {('yes' if r['folded'] else 'NO'):>8s} "
          f"{('yes' if r['plddt'] else 'no'):>7s} {('yes' if r['feats'] else 'no'):>10s}  {err}")

print("\n" + "=" * 94)
print("JA6 — THE 10 LOCAL-TIER TARGETS NOT SCORED AT RUN 2: WHICH PREDICATE DO THEY FAIL?")
print("=" * 94)
local_unscored = [r for r in rows if r["tier"] == "local" and not r["scored"]]
print(f"  local-tier and NOT scored at run 2: {len(local_unscored)}")
print(f"\n  {'acc':9s} {'gene':10s} {'span':>6s} {'in db?':>7s} {'folded?':>8s} {'plddt?':>7s} "
      f"{'features?':>10s} {'positive?':>10s}")
print("  " + "-" * 88)
for r in sorted(local_unscored, key=lambda r: r["acc"]):
    print(f"  {r['acc']:9s} {r['gene']:10s} {r['span']:>6d} "
          f"{('yes' if r['in_db'] else 'NO'):>7s} {('yes' if r['folded'] else 'NO'):>8s} "
          f"{('yes' if r['plddt'] else 'no'):>7s} {('yes' if r['feats'] else 'NO'):>10s} "
          f"{('YES' if r['pos'] else '-'):>10s}")
reasons = Counter()
for r in local_unscored:
    if not r["in_db"]:
        reasons["no protein_analyses row at all"] += 1
    elif not r["folded"]:
        reasons["row exists but not folded"] += 1
    elif not r["feats"]:
        reasons["folded but NO protein_features row"] += 1
    else:
        reasons["folded WITH features — unexplained by this measurement"] += 1
print(f"\n  ⚠ why they are not in the ranking set, by cause:")
for k, v in reasons.most_common():
    mark = "  ⚠⚠ needs D-064's predicate read" if "unexplained" in k else ""
    print(f"    {k:52s} {v:3d}{mark}")
print(f"    {'TOTAL':52s} {sum(reasons.values()):3d}")
