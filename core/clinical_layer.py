"""`D-093 amendment 2` made structural: the vocabulary and the category layering, before any ingest.

⚠⚠ **THIS CREATES NO TABLE AND WRITES NO ROW.** It is the constraint half of `EC` — the vocabulary a
schema must obey and the layering ruling 5 requires — expressed as pure code so it can be tested
before anything is stored. **Nothing here touches a database.**

⚠ **`EC1` asked whether ruling 5's TWO layers are enough. They are not. THREE are needed**, and the
reason is not stylistic:

  `hpa_absent` and `accession_ambiguous` are **outcomes of the MAPPING**. They happen before any
  supplier is consulted, and there is **no supplier encoding to record** — the supplier was never
  asked. Filing them under `supplier_encoding` would assert that HPA returned something for a
  protein HPA was never queried about.

  ⚠⚠ And the **derived fact is UNDEFINED** for them. *"Is IHC available for this protein?"* has no
  answer when we do not know which gene the protein is. **`not_determinable` is a third value, not a
  synonym for `no_ihc_available`** — one says the supplier has nothing, the other says we cannot ask.

So: **mapping outcome → supplier encoding → derived fact**, with the second and third only defined
when the first resolved. `EC1`'s partition assertion is over the FIRST layer, because that is the one
every row lands in exactly once.
"""
from __future__ import annotations

# ── ruling 7: `Level` is NOT a four-value ordinal ────────────────────────────────────────────

#: The four values that ARE positions on a scale, weakest first.
LEVEL_ORDINAL = ("Not detected", "Low", "Medium", "High")

#: ⚠⚠ The four that are NOT. `Ascending` and `Descending` are **gradients** — they describe how
#: staining varies across a structure, not how much of it there is. **No weighting can place them**,
#: and a `qh`-style score that silently treats them as a level is inventing a position on a scale
#: the annotation deliberately declined to give.
LEVEL_NON_ORDINAL = ("N/A", "Ascending", "Descending", "Not representative")

#: Measured over HPA v22 `normal_tissue.tsv`, 1,194,479 rows:
#:   Not detected 565,839 · Medium 302,651 · Low 183,677 · High 140,198
#:   N/A 1,860 · Ascending 172 · Descending 73 · Not representative 9   (2,114 non-ordinal)
LEVEL_VALUES = LEVEL_ORDINAL + LEVEL_NON_ORDINAL


class UnhandledLevel(ValueError):
    """⚠ A `Level` value outside the measured set RAISES.

    HPA may add a value in a later release, and **a silent fallthrough would file it as whichever
    branch happened to be last.** `D-093` amendment 2 ruling 7 requires the full set asserted and a
    red on anything unhandled — this is that red, at the point of use rather than at review time.
    """


def is_ordinal(level: str) -> bool:
    """Can this `Level` be placed on a scale at all? ⚠ Raises on an unknown value."""
    v = (level or "").strip()
    if v not in LEVEL_VALUES:
        raise UnhandledLevel(
            f"Level {level!r} is not one of the {len(LEVEL_VALUES)} measured HPA v22 values "
            f"{LEVEL_VALUES}. A new value is a supplier change, not a parsing detail — "
            f"re-derive ruling 7 rather than widening this list silently.")
    return v in LEVEL_ORDINAL


# ── ruling 5, widened to three layers ────────────────────────────────────────────────────────

#: LAYER 1 — what the MAPPING did. Every census row lands in exactly one of these.
MAPPING_OUTCOME = ("mapped_one_gene", "accession_ambiguous", "hpa_absent")

#: LAYER 2 — what the SUPPLIER did. ⚠ Defined ONLY when layer 1 is `mapped_one_gene`.
#: The same underlying fact arrives differently in the two files, and the record keeps which:
#:   `row_absent`             — `normal_tissue.tsv` omits the gene entirely   (1,023 on the manifest)
#:   `row_present_panel_empty`— `pathology.tsv` lists it with all counts zero (1,008 on the manifest)
SUPPLIER_ENCODING = ("row_present_with_data", "row_present_panel_empty", "row_absent")

#: LAYER 3 — what is TRUE OF THE PROTEIN, which is what the surface renders.
#: ⚠⚠ `not_determinable` is NOT a synonym for `no_ihc_available`: one is *the supplier has nothing*,
#: the other is *we cannot ask*. Collapsing them is the laundering ruling 5 exists to prevent.
DERIVED_FACT = ("ihc_available", "no_ihc_available", "not_determinable")

#: The five measured categories, mapped onto the three layers. ⚠ This IS the table `EC1` asked for.
CATEGORY_LAYERS: dict[str, tuple[str, str | None, str]] = {
    "ihc_present":         ("mapped_one_gene",      "row_present_with_data",    "ihc_available"),
    "ihc_panel_empty":     ("mapped_one_gene",      "row_present_panel_empty",  "no_ihc_available"),
    "ihc_gene_absent":     ("mapped_one_gene",      "row_absent",               "no_ihc_available"),
    "accession_ambiguous": ("accession_ambiguous",  None,                       "not_determinable"),
    "hpa_absent":          ("hpa_absent",           None,                       "not_determinable"),
}

MEASURED_CATEGORIES = tuple(CATEGORY_LAYERS)


def layers_of(category: str) -> tuple[str, str | None, str]:
    """(mapping outcome, supplier encoding or None, derived fact). ⚠ Raises on an unknown category —
    a sixth category is a measurement that changed, not a lookup miss."""
    if category not in CATEGORY_LAYERS:
        raise ValueError(
            f"unknown coverage category {category!r}; the measured five are {MEASURED_CATEGORIES}")
    return CATEGORY_LAYERS[category]


# ── ruling 6: an absent row is NOT `Not detected` ────────────────────────────────────────────

#: ⚠ Two states, never one. `Not detected` is an explicit Level (565,839 rows); a MISSING
#: (gene, tissue, cell) row means the pair was **not tested**. Measured: **0 of 15,313 genes cover
#: all 266 (tissue, cell) pairs**, so the grid is ragged and the distinction is load-bearing.
TESTED_STATE = ("tested_not_detected", "not_tested")


# ── ruling 4: the two edges are NOT commensurable ────────────────────────────────────────────

class IncomparableEdges(TypeError):
    """⚠⚠ Raised by any attempt to combine a tumour count with a normal-tissue level.

    `pathology.tsv` serves four patient COUNTS per (gene × cancer). `normal_tissue.tsv` serves one
    ordinal LEVEL per (gene × tissue × cell) and **carries no patient counts at all** — so a
    quasi-H-score cannot be computed on the normal side, and **a ratio, difference, contrast or
    index would put two incomparable quantities either side of one operator.**

    ⚠ Decision 5 is satisfied by **co-equal display**, not by arithmetic. This exception is the
    structural form of that ruling: the operation does not exist rather than being discouraged.
    """


def tumour_normal_ratio(*_args, **_kwargs):
    """⚠⚠ Deliberately unimplemented, and it raises rather than returning `None`.

    A function returning `None` invites a caller to treat the absence as a missing value and fill
    it. **The ratio is pre-registered as NOT COMPUTABLE FROM THIS SUPPLIER** — an absence with a
    cause, not an unfilled intention — so the call itself is the error.
    """
    raise IncomparableEdges(
        "no tumour-normal ratio, difference, contrast or index is computed from these two "
        "suppliers (D-093 amendment 2 ruling 4). pathology.tsv has patient counts; "
        "normal_tissue.tsv has none. Render both edges side by side, each in its own units, "
        "with the incomparability stated.")
