"""The clinical edges as a renderable block — `D-093`, edges 1 and 2.

⚠⚠ WHAT THIS IS FOR, IN ONE SENTENCE: it ties a protein to something a human being can understand
— *"of 12 ovarian tumours tested, 10 stained positive"* — rather than to a score. Patient counts,
from immunohistochemistry, with the normal-tissue half beside them.

⚠ BOTH EDGES OR NEITHER. `D-093` decision 5 makes the normal-tissue differential **co-equal, not an
appendix**, and amendment 2 ruling 2 ships them together. A tumour panel alone is the flattering
half: MSLN stains in 83% of ovarian tumours **and** stains High in bronchus and fallopian tube, and
a card that showed the first without the second would be selling rather than describing.

⚠⚠ THE BURDEN SLOT IS RENDERED EMPTY ON PURPOSE. Decision 4 mandates a burden tuple — incidence,
lethality, survival — and amendment 1 clause 2 removed the only redistributable source. Ruling 1:
`burden_supplier_unlicensed` renders **wherever a burden would have appeared — never a blank, never
a zero, never an omission.** SEER, GLOBOCAN/IARC, TCGA/GDC and CPTAC are **UNATTEMPTED, not
failed**: a category with a cause.

⚠⚠ AND THIS PAYLOAD CARRIES NO BURDEN FIELD AT ALL — a guard caught me putting one here.
`D-093` decision 1: **clinical burden is a property of the DISEASE**; it attaches by traversal and
may never be a protein-level column. My first version returned `burden` and `burden_note` on the
protein block, which asserts that a PROTEIN has an incidence and a lethality. It does not; a
disease does. `test_no_protein_level_model_or_payload_carries_a_burden_field` reddened on it.

⚠ Ruling 1 is satisfied by the SURFACE, which is where it belongs: `ClinicalEdges.jsx` renders
"How common, how deadly — not shown, no licensed source" wherever tumours are listed. The refusal
is identical for every protein and every disease, so carrying it per-protein in a payload was
duplicating a constant AND miscategorising it. Fixing the shape beat renaming around the check.

⚠ NO RATIO IS COMPUTED. `core.clinical_layer.tumour_normal_ratio()` raises by design (ruling 4: the
two edges are not commensurable). This module returns both sides and divides nothing.

⚠ Deliberately NOT in `app/reads.py`: the route layer composes suppliers, and keeping each one in
its own module is what makes the walls checkable at file granularity.
"""
from __future__ import annotations

from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from core.hpa_attribution import attribution_block
from core.clinical_layer import LEVEL_ORDINAL, CATEGORY_LAYERS, layers_of
from db.models import ClinicalNormalTissue, ClinicalPathology


#: The coverage categories this module can report, from the layer's own five.
assert "ihc_present" in CATEGORY_LAYERS and "ihc_gene_absent" in CATEGORY_LAYERS


#: ⚠⚠ THE LICENCE STATEMENT THE SURFACE QUOTES — owner ruling R1, `D-093 amendment 3` item 5.
#: A module constant so a test can compare it to the PINNED as-read region byte for byte, rather
#: than a reviewer comparing it by eye.
HPA_LICENCE_STATEMENT = {
    # ⚠⚠ REPORTED SPEECH, NEVER ADOPTION. "…states…" — never "this data is licensed under…",
    # which would adopt one side of a dispute. Adoption is what the ruling refuses.
    "attributive": "The Human Protein Atlas states, on its Licence & Citation page",
    # ⚠⚠ VERBATIM, INCLUDING "3.0 International" — a licence version that does not exist. The
    # surface does NOT say so: correcting someone else's page on our page is worse than quoting it,
    # and that observation lives in the log where it belongs.
    # ⚠ The trailing quote is unbalanced in the source itself and is reproduced exactly, because
    # verbatim means verbatim even where the page is untidy.
    "quotation": (
        "The Human Protein Atlas is licensed under the Creative Commons Attribution-ShareAlike "
        "3.0 International License for all copyrightable parts of our database, specifically "
        "indicated in the downloadable XML format with 'source=\"HPA\"."
    ),
    # ⚠⚠ THE v22 HOST, AND WHICH PAGE IS NOT A DETAIL. Both were fetched on 2026-08-20 and diffed:
    # v22 says **Attribution-ShareAlike 3.0 International**; www says **Attribution 4.0
    # International**. They are DIFFERENT LICENCES. v22 governs because v22 is what was ingested,
    # and it does NOT redirect — so the version really is retrievable from the host name.
    "url": "https://v22.proteinatlas.org/about/licence",
    "date_read": "2026-08-20",
}


def _tumour_rows(session, gene_name: str) -> list[dict]:
    rows = session.execute(
        select(ClinicalPathology).where(ClinicalPathology.gene_name == gene_name)
    ).scalars().all()
    out = []
    for r in rows:
        tested = r.high + r.medium + r.low + r.not_detected
        positive = r.high + r.medium + r.low
        out.append({
            "cancer": r.cancer,
            "patients_tested": tested,
            "patients_positive": positive,
            # ⚠ the counts travel with the fraction. A percentage over 4 patients and one over 40
            # are different facts, and a bare percentage hides which you are reading.
            "high": r.high, "medium": r.medium, "low": r.low, "not_detected": r.not_detected,
        })
    # ⚠ ordered by how much of the panel stained, NOT presented as a ranking of targets:
    # this is one protein's own tumours ordered for legibility, never proteins ordered against
    # each other. D-079 dec 1 bars the latter and this is not it.
    out.sort(key=lambda d: (-(d["patients_positive"] / d["patients_tested"])
                            if d["patients_tested"] else 0, d["cancer"]))
    return out


def _normal_rows(session, gene_name: str) -> list[dict]:
    rows = session.execute(
        select(ClinicalNormalTissue).where(ClinicalNormalTissue.gene_name == gene_name)
    ).scalars().all()
    by_tissue: dict[str, dict] = {}
    for r in rows:
        t = by_tissue.setdefault(r.tissue, {"tissue": r.tissue, "highest": None, "cell_types": 0,
                                            "detected_in": 0})
        t["cell_types"] += 1
        if r.level in LEVEL_ORDINAL:
            if r.level != "Not detected":
                t["detected_in"] += 1
            cur = t["highest"]
            if cur is None or LEVEL_ORDINAL.index(r.level) > LEVEL_ORDINAL.index(cur):
                t["highest"] = r.level
        # ⚠ a NON-ordinal level (N/A, Ascending, Descending, Not representative) never becomes
        # `highest`: comparing it against the ordinal scale is what IncomparableEdges forbids.
    out = [t for t in by_tissue.values() if t["detected_in"] > 0]
    out.sort(key=lambda d: (-LEVEL_ORDINAL.index(d["highest"] or "Not detected"),
                            -d["detected_in"], d["tissue"]))
    return out


def clinical_block(engine: Any, gene_name: Optional[str]) -> dict:
    """Both edges for one gene, plus the burden slot that stays empty with its reason.

    ⚠⚠ AN ABSENT GENE IS A CATEGORY, NOT AN EMPTY PANEL. `ihc_gene_absent` means HPA's IHC does not
    cover this protein — **not** that it was tested and found negative. Measured on the census:
    960 of 2,687 folded genes are absent, so this is the common case and not an edge case.
    """
    if not gene_name:
        return {"status": "not_determinable", "reason": "no gene symbol on this record",
                "tumours": [], "normal_tissues": [],
                "layers": layers_of("accession_ambiguous")}

    with Session(engine) as s:
        tumours = _tumour_rows(s, gene_name)
        normals = _normal_rows(s, gene_name)
        any_row = bool(tumours) or bool(
            s.execute(select(ClinicalNormalTissue.id)
                      .where(ClinicalNormalTissue.gene_name == gene_name).limit(1)).first())

    if not any_row:
        category = "ihc_gene_absent"
    elif not tumours and not normals:
        category = "ihc_panel_empty"
    else:
        category = "ihc_present"

    return {
        "status": category,
        "layers": layers_of(category),          # (mapping outcome, supplier encoding, derived fact)
        "gene": gene_name,
        "tumours": tumours,
        "normal_tissues": normals,
        # ⚠⚠ THE SURFACE QUOTES THE PAGE — owner ruling R1, `D-093 amendment 3` item 5.
        # The first version asserted `CC BY-SA 3.0`, which adopted one side of a dispute. Amendment 4
        # removed the assertion and left SILENCE. ⚠ Silence leaves a reader unable to verify anything;
        # an attributed quotation with a resolvable link and a date read is verifiable and claims
        # nothing. This is a CHANGE from amendment 4's fix, in the direction of more information.
        #
        # ⚠⚠ REPORTED SPEECH, NEVER ADOPTION. "The Human Protein Atlas states…" — never "this data is
        # licensed under…". Adoption is exactly what the ruling refuses.
        # ⚠⚠ VERBATIM, INCLUDING "3.0 International" — a licence version that does not exist. The
        # surface does NOT say so. Correcting someone else's page on our page is worse than quoting
        # it; that observation lives in the log, where it belongs.
        # ⚠ THE URL IS THE v22 HOST, determined by fetching BOTH pages on 2026-08-20 and diffing:
        # v22 says Attribution-ShareAlike 3.0 International, www says Attribution 4.0 International.
        # They are DIFFERENT LICENCES. v22 governs, because v22 is what was ingested.
        "licence_statement": dict(HPA_LICENCE_STATEMENT),
        # ⚠⚠ THE FOUR ELEMENTS, PER VIEW. The licence makes citation a PRECONDITION of
        # display, so each edge carries its own deep link — the tumour panel to /pathology and
        # the normal-tissue panel to /tissue. A single block per page does not discharge it.
        "attribution_tumour": attribution_block(gene_name, "pathology"),
        "attribution_normal": attribution_block(gene_name, "normal_tissue"),
        "source": ("Human Protein Atlas v22 — pathology.tsv (protein → tumour, IHC) and "
                   "normal_tissue.tsv (protein → normal tissue)."),
        "boundary": ("Immunohistochemistry: how many patient samples stained for this protein. "
                     "An EXPRESSION observation — not causation, not a claim the protein drives "
                     "the disease, and not a clinical indication."),
        # ⚠⚠ no ratio, no combined figure, no score. The two edges are not commensurable
        # (ruling 4), and `tumour_normal_ratio()` raises rather than returning one.
    }
