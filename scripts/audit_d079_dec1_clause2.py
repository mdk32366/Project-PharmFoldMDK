"""Clause 2 audit: is any CENSUS statistic presented as evidence about ADC SUITABILITY?

⚠ The method, stated: find sentences that contain BOTH a census figure AND suitability language,
then read every hit. A co-occurrence is a CANDIDATE, never a verdict — most will be prohibitions.
"""
import pathlib, re

REPO = pathlib.Path(r"C:\Projects\Project-PharmFoldMDK")
TARGETS = ["docs/PAPERS-v2.md", "ARCHITECTURE.md", "README.md", "docs/README.md"]
TARGETS += [str(p.relative_to(REPO)).replace("\\", "/") for p in (REPO / "ui" / "src").rglob("*.jsx")
            if ".test." not in p.name]

CENSUS_FIG = re.compile(r"\b(2,?690|2,?807|3,?467|2,?209|1,?397|2,?632|1,?293|2,?581)\b")
SUITABLE = re.compile(r"\b(suitab\w*|good target|promising|candidate|shortlist|best|prioriti[sz]\w*|"
                      r"rank\w*|score[sd]?|recommend\w*)\b", re.I)
NEGATED = re.compile(r"\b(not|no|never|bars?|barred|forbid\w*|must not|cannot|refus\w*|deliberately|"
                     r"neither|without|unscored)\b", re.I)

hits = []
for rel in TARGETS:
    p = REPO / rel
    if not p.is_file():
        continue
    text = p.read_text(encoding="utf-8", errors="replace")
    for sent in re.split(r"(?<=[.!?])\s+|\n\n", text):
        if CENSUS_FIG.search(sent) and SUITABLE.search(sent):
            hits.append((rel, sent.strip()))

print(f"  files scanned            : {len([t for t in TARGETS if (REPO/t).is_file()])}")
print(f"  candidate co-occurrences : {len(hits)}")
neg = [h for h in hits if NEGATED.search(h[1])]
bare = [h for h in hits if not NEGATED.search(h[1])]
print(f"    carrying a negation    : {len(neg)}   (prohibitions, not claims)")
print(f"  ⚠ WITHOUT a negation     : {len(bare)}   <- these need reading")
print()
for rel, sent in bare:
    s = re.sub(r"\s+", " ", sent)[:400]
    print(f"  --- {rel}\n      {s}\n")
