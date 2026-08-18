"""Task I — reproduce Kathad's stage ladder: 20,090 → 5,543 → 4,875 → 1,731 → 763.

⚠⚠ THE 13 CRITICAL TISSUES ARE READ, NOT INFERRED, AND NOT FROM FIG 2A. The order said to take
them from Fig 2A; **Fig 2A is a heatmap of 44 normal tissues for the 82 survivors** and does not
carry them. They are stated verbatim in the Methods, which is machine-readable:

    "considered the removal of genes with high expression levels in 13 critical normal tissues as
     used in [14]; lung, oral mucosa, esophagus, stomach, duodenum, small intestine, colon,
     rectum, liver, kidney, heart muscle, skin, bone marrow. This step resulted in 1731 genes"
    — journal.pone.0308604, Methods

⚠ THE TARGETS ARE PRE-REGISTERED AND NOT NEGOTIABLE. If a stage misses, the miss is reported and
neither the tissue list nor the rule is adjusted to reach the number. *A boundary moved to land on
a target is a boundary chosen for the answer it gives.*

⚠ THE TISSUE VOCABULARY IS AMBIGUOUS, and that is a property of the source, not a choice made
here. `stomach` appears only as `stomach 1` / `stomach 2`; `skin` appears as a bare tissue AND as
`skin 1` / `skin 2`. Every defensible mapping is reported side by side and none is privileged —
the same discipline A3 applies to its type sets and k values.

    python scripts/kathad_stage3.py --atlas ~/Downloads/v22/proteinatlas.tsv \
                                    --normal ~/Downloads/v22/normal_tissue.tsv
"""
from __future__ import annotations

import argparse
import csv
import pathlib
import sys
from typing import Optional

REPO = pathlib.Path(__file__).resolve().parents[1]

#: Verbatim from the Methods. ⚠ Do not edit to make a stage land.
CRITICAL_13 = ("lung", "oral mucosa", "esophagus", "stomach", "duodenum", "small intestine",
               "colon", "rectum", "liver", "kidney", "heart muscle", "skin", "bone marrow")

#: The paper's own ladder, transcribed for comparison only.
TARGETS = {"total": 20090, "membrane": 5543, "protein_evidence": 4875, "after_tissues": 1731}

MEMBRANE_CLASS = "Predicted membrane proteins"
PROTEIN_EVIDENCE = "Evidence at protein level"

#: ⚠ "high expression levels" — the rule under test. `High` is the only HPA level that means it.
HIGH = "High"


def tissue_variants(vocab: set[str]) -> dict[str, set[str]]:
    """Every defensible mapping of the 13 names onto the file's vocabulary.

    ⚠ Reported side by side. Picking the one that lands on 1,731 would be fitting the boundary to
    the answer; reporting all of them is a measurement of how much the ambiguity is worth.
    """
    def resolve(name: str, numbered: bool, bare: bool) -> set[str]:
        out = set()
        if bare and name in vocab:
            out.add(name)
        if numbered:
            out |= {t for t in vocab if t.startswith(name + " ")}
        return out

    variants: dict[str, set[str]] = {}
    for label, numbered, bare in (
        ("bare-only (exact names only)", False, True),
        ("numbered-only (stomach 1/2, skin 1/2)", True, False),
        ("bare + numbered (widest)", True, True),
    ):
        s: set[str] = set()
        for n in CRITICAL_13:
            s |= resolve(n, numbered, bare)
        variants[label] = s
    return variants


def load_atlas(path: pathlib.Path) -> list[dict]:
    """⚠⚠ THE COLUMN NAMED `Gene` MEANS DIFFERENT THINGS IN DIFFERENT HPA FILES, in the same
    version and the same download:

        proteinatlas.tsv   Gene = TSPAN6           (the SYMBOL);  Ensembl = ENSG00000000003
        pathology.tsv      Gene = ENSG00000000003  (the ID);      Gene name = TSPAN6
        normal_tissue.tsv  Gene = ENSG00000000003  (the ID);      Gene name = TSPAN6

    Joining `proteinatlas.Gene` to `pathology.Gene` gives a clean, plausible, entirely EMPTY
    intersection — the `D-100` defect one file over, and it raises nothing. **So the join key here
    is the Ensembl id**, which is unambiguous in all three.
    """
    with path.open(encoding="utf-8") as fh:
        return [{"symbol": r["Gene"].strip(), "ensembl": r["Ensembl"].strip(),
                 "Protein class": r["Protein class"], "Evidence": r["Evidence"]}
                for r in csv.DictReader(fh, delimiter="\t")]


def high_in(path: pathlib.Path, tissues: set[str]) -> set[str]:
    """ENSEMBL IDS with `Level == High` in ANY of `tissues`. ⚠ Keyed on `Gene` because in
    normal_tissue.tsv that column is the Ensembl id — see `load_atlas`."""
    out: set[str] = set()
    with path.open(encoding="utf-8") as fh:
        for r in csv.DictReader(fh, delimiter="\t"):
            if r["Level"].strip() == HIGH and r["Tissue"].strip() in tissues:
                out.add(r["Gene"].strip())
    return out


def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--atlas", required=True)
    ap.add_argument("--normal", required=True)
    args = ap.parse_args(argv)

    atlas = load_atlas(pathlib.Path(args.atlas).expanduser())
    normal_path = pathlib.Path(args.normal).expanduser()

    print("=" * 88)
    print("TASK I — Kathad's stage ladder, re-derived")
    print("⚠ targets are pre-registered; a miss is REPORTED, never engineered away")
    print("=" * 88)

    def line(name, mine, target):
        ok = mine == target
        print(f"  {name:34s} {mine:8,d} {target:8,d}   {'MATCH' if ok else '⚠ MISS'}")
        return ok

    print(f"  {'stage':34s} {'mine':>8s} {'paper':>8s}")
    print("  " + "-" * 62)
    line("total genes", len(atlas), TARGETS["total"])

    membrane = [r for r in atlas if MEMBRANE_CLASS in r["Protein class"]]
    line("membrane protein coding", len(membrane), TARGETS["membrane"])

    stage2 = [r for r in membrane if r["Evidence"].strip() == PROTEIN_EVIDENCE]
    line("+ evidence at protein level", len(stage2), TARGETS["protein_evidence"])
    pool = {r["ensembl"] for r in stage2}   # join on Ensembl (see load_atlas)

    with normal_path.open(encoding="utf-8") as fh:
        vocab = {r["Tissue"].strip() for r in csv.DictReader(fh, delimiter="\t")}

    print("\n" + "=" * 88)
    print("STAGE 3 — remove genes HIGH in any of the 13 critical tissues")
    print("⚠ `stomach` exists only as `stomach 1`/`stomach 2`; `skin` exists bare AND numbered.")
    print("  Every mapping is shown. None is privileged.")
    print("=" * 88)
    print(f"  {'tissue mapping':40s} {'tissues':>8s} {'removed':>8s} {'remaining':>10s}  vs 1,731")
    print("  " + "-" * 78)

    hit = None
    for label, tissues in tissue_variants(vocab).items():
        removed_genes = high_in(normal_path, tissues)
        remaining = pool - removed_genes
        n = len(remaining)
        delta = n - TARGETS["after_tissues"]
        mark = "MATCH" if delta == 0 else f"⚠ {delta:+,d}"
        print(f"  {label:40s} {len(tissues):8d} {len(pool & removed_genes):8,d} "
              f"{n:10,d}  {mark}")
        if delta == 0:
            hit = label

    print()
    if hit:
        print(f"  ✓ stage 3 reproduces under: {hit}")
        print("  ⚠ One mapping landing and the others not is EVIDENCE for that mapping — but it")
        print("    is evidence, not proof: the paper does not state which it used.")
    else:
        print("  ⚠⚠ STAGE 3 DOES NOT REPRODUCE UNDER ANY MAPPING.")
        print("     Per the pre-registration the miss is reported and nothing is adjusted.")
        print("     Either the 'high expression' rule is not `Level == High`, or the tissue")
        print("     resolution differs, or the gene pool entering stage 3 is not the 4,875.")
    return 0 if hit else 1


if __name__ == "__main__":
    raise SystemExit(main())
