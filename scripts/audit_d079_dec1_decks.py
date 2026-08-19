"""Extract slide text from .pptx with the stdlib only (no python-pptx here), and audit it against
`D-079` decision 1: *no census statistic presented as evidence about ADC suitability in any
artifact, DECK, or briefing.*"""
import pathlib, re, zipfile

REPO = pathlib.Path(r"C:\Projects\Project-PharmFoldMDK")
CENSUS_FIG = re.compile(r"\b(2,?690|2,?807|3,?467|2,?209|1,?397|2,?632|1,?293|2,?581|2,?641)\b")
SUITABLE = re.compile(r"\b(suitab\w*|good target|promising|candidate|shortlist|best|prioriti[sz]\w*|"
                      r"rank\w*|score[sd]?|recommend\w*|top \d+)\b", re.I)

for deck in sorted(REPO.glob("docs/*.pptx")):
    z = zipfile.ZipFile(deck)
    slides = sorted((n for n in z.namelist()
                     if re.fullmatch(r"ppt/slides/slide\d+\.xml", n)),
                    key=lambda n: int(re.search(r"\d+", n.split("/")[-1]).group()))
    print("=" * 92)
    print(f"{deck.name} — {len(slides)} slides")
    print("=" * 92)
    for n in slides:
        xml = z.read(n).decode("utf-8", "replace")
        runs = re.findall(r"<a:t>(.*?)</a:t>", xml, re.S)
        text = re.sub(r"\s+", " ", " ".join(runs)).strip()
        if not text:
            continue
        idx = int(re.search(r"\d+", n.split("/")[-1]).group())
        fig = bool(CENSUS_FIG.search(text))
        suit = bool(SUITABLE.search(text))
        flag = "  ⚠⚠ CENSUS FIGURE + SUITABILITY LANGUAGE" if (fig and suit) else \
               ("  ⚠ census figure" if fig else ("  · suitability language" if suit else ""))
        print(f"\n[slide {idx}]{flag}\n  {text[:600]}")
