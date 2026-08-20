"""HPA attribution — the four elements, and the per-datum link they hang on.

⚠⚠ THE LICENCE WORDS IT AS A PRECONDITION, NOT A FOOTNOTE: *"be sure that our content is never
displayed in the absence of such citation."* That is `D-094`'s shape, written by HPA. So this is a
MOUNT PRECONDITION on every surface that renders an HPA-derived value — not a page footer.

⚠⚠ AND "HPA-DERIVED" IS ABOUT THE SOURCE, NOT THE ROUTE. `CancerAssociations` reads Kathad's S3, and
`D-100` established S3 is a **verbatim extract of `pathology.tsv` — 1,640 / 1,640 rows, all four
count columns identical.** **CITING THE PAPER IS NOT CITING HPA.** The obligation attaches to the
underlying source however the numbers arrived, and `D-053` predates the clinical layer entirely — so
the gap is older than the entry that found it.

⚠ THE PRIMARY PUBLICATION IS THE IHC PAPER, AND THE OBVIOUS GUESS IS WRONG. `pathology.tsv` is
immunohistochemistry, so the citation is Uhlén 2015 *Tissue-based map of the human proteome*. It is
**NOT** the 2017 *pathology atlas of the human cancer transcriptome*, despite that paper's title
matching our filename. A filename is not a modality.
"""
from __future__ import annotations

import csv
import functools
import pathlib
from typing import Optional

#: ⚠ Element 1 — the primary publication. IHC, not transcriptome.
PRIMARY_PUBLICATION = {
    "citation": ("Uhlén M et al., Tissue-based map of the human proteome, "
                 "Science (2015)"),
    "doi": "10.1126/science.1260419",
    "url": "https://doi.org/10.1126/science.1260419",
}

#: ⚠ Element 2 — the website reference.
WEBSITE_REFERENCE = {"name": "Human Protein Atlas", "url": "https://www.proteinatlas.org"}

#: ⚠⚠ Element 3 — the image/data credit, AS ITS OWN ELEMENT. Amendment 1 clause 3 dropped it and
#: `NC` confirmed it was never built. It is not the same string as element 2 doing double duty.
DATA_CREDIT = "Human Protein Atlas"

#: ⚠⚠ Element 4's host. THE VERSION IS THE POINT. `D-093 amendment 8`: v22 states BY-SA 3.0 and www
#: states BY 4.0 — two different licences on two live pages. A link to the current release beside
#: v22 data cites a source that is not the source AND points at different terms.
V22_HOST = "https://v22.proteinatlas.org"

#: The verified EG1 pattern — derived by navigating the site, not constructed.
#: `SPEC-2026-08-19-hpa-deep-link-pattern.md`: canonical is `<ENSG>-<GENE>`, with `/pathology` for
#: the tumour view and `/tissue` for the normal-tissue view.
VIEWS = {"pathology": "pathology", "normal_tissue": "tissue", "protein": ""}


def deep_link(ensg: Optional[str], gene: Optional[str], view: str = "protein") -> Optional[str]:
    """The per-datum link, or None when it cannot be built.

    ⚠⚠ None IS A CATEGORY, NOT A FAILURE. 89 of 2,688 census rows resolve no ENSG, and a link built
    without one would either 404 or — worse — resolve to something else. The surface renders the
    absence with its cause rather than a broken anchor.
    """
    if not ensg or not gene:
        return None
    if view not in VIEWS:
        raise ValueError("unknown view %r — the view must be named, never defaulted" % view)
    suffix = VIEWS[view]
    base = "%s/%s-%s" % (V22_HOST, ensg, gene)
    return "%s/%s" % (base, suffix) if suffix else base


@functools.lru_cache(maxsize=1)
def ensg_map(path: str | None = None) -> dict[str, str]:
    """gene symbol -> ENSG, from data ALREADY INGESTED.

    ⚠ Not a new supplier and not a data-model change: both clinical tables carry `gene` (the ENSG)
    beside `gene_name`, so the mapping is a lookup over rows we already hold. Measured coverage:
    **82 of 82** cohort symbols and **2,599 of 2,688** folded census symbols resolve.
    """
    p = pathlib.Path(path) if path else pathlib.Path("data/census/hpa_ensg_map.csv")
    if not p.exists():
        return {}
    with p.open(encoding="utf-8") as fh:
        return {r["gene_name"]: r["ensg"] for r in csv.DictReader(fh) if r.get("ensg")}


def attribution_block(gene: Optional[str], view: str = "protein",
                      ensg: Optional[str] = None) -> dict:
    """Every element a surface needs to satisfy the precondition, in one payload.

    ⚠ All four travel together. A surface that received three of them could render three and look
    attributed, which is the shape this whole order exists to close.
    """
    resolved = ensg or (ensg_map().get(gene) if gene else None)
    return {
        "primary_publication": dict(PRIMARY_PUBLICATION),
        "website": dict(WEBSITE_REFERENCE),
        "data_credit": DATA_CREDIT,
        "deep_link": deep_link(resolved, gene, view),
        # ⚠ stated so the surface can say WHY a link is absent rather than omitting it silently
        "deep_link_absent_reason": (
            None if deep_link(resolved, gene, view)
            else ("no gene symbol on this record" if not gene
                  else "no Ensembl gene id resolves for %s in the ingested HPA files" % gene)),
        "ensg": resolved,
    }
