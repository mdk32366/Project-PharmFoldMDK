"""The census COST supplier — what a row costs to FOLD, and nothing else.

⚠⚠ **THIS IS A COST / TRACTABILITY AXIS. IT IS NOT A SUITABILITY AXIS.** It reads
`core.foldability.envelope` against `core.manifest.LOCAL_CEILING` and reports where a
span of this length can be folded at the measured recipe. It says **nothing whatsoever**
about whether the protein is a good ADC target, and `D-077` decision 1 refusal 2 requires
any surface that puts the two side by side to say so **in the same visual frame**. That is
why `cost_axis` and `cost_recipe` ride on **every row** rather than living in a tooltip or
a doc a reader has to go and find — the same reason `scored: false` rides on every row.

⚠⚠ **AND IT MUST NOT FILTER THE CENSUS** — `D-077` decision 1 refusal 3, quoted because
it is the one this module is nearest to breaking: *"A comprehensive census that silently
drops the targets it cannot afford to fold is a census of our budget, not of the
surfaceome — and it would bias the census by length, i.e. by feature 1."* So this module
**stamps and returns every row it is given**, in the order it was given them. There is no
`only_local`, no `affordable`, no threshold argument, and `tests/test_d137_census_cost_column.py`
asserts there is none — including on the **UI** side, where the temptation is concrete: the
census already has fold-type chips (D-133 am. 1) and a cost chip would look like the next
one. **A sortable column and a legend are the whole licensed surface.**

⚠ **It must not become a feature.** Local-foldability is a monotone step function of ECD
length, which is **feature 1** of the pre-registered six (D-027) — the F-008 confound.
`tests/test_foldability.py` already asserts `core/scorer.py` and `core/features.py` import
neither `core.foldability` nor `core.census`; this module joins that guard, so a scorer that
reaches for a compute budget reddens rather than being caught in review.

═══════════════════════════════════════════════════════════════════════════════
WHY THE MISSING-SPAN CASE IS ITS OWN WORD, AND WHY IT IS NOT `no_topology`
═══════════════════════════════════════════════════════════════════════════════

`envelope()` **raises** on a missing span rather than guessing, because "quietly bucketing
an unmeasured target as affordable is how a cost estimate becomes a fiction" (D-024). A read
route may not raise on 3,467 rows, so the absence needs a name — and the name is
`span_unrecorded`, **never** `local`.

⚠ It is deliberately **not** `core.census.NO_TOPOLOGY`. That word means *fetched
successfully, and the protein has no numeric ECD span* — a claim about the **protein**, and
that module says in terms that it "REQUIRES A SUCCESSFUL FETCH". Here we are reading a row
out of the database whose `meta` carries no `span_aa`; nothing on the read path attests that
a topology fetch ever happened, so borrowing that word would assert a fact we do not have.
Two different ignorances, two different words — which is the same rule `core/census.py`
applies when it keeps `unresolved` apart from `fetch_failed`.

═══════════════════════════════════════════════════════════════════════════════
PROVENANCE (D-016)
═══════════════════════════════════════════════════════════════════════════════

Over `data/census/census_manifest.v7.csv` (3,467 rows, read 2026-09-08):
`local` **2,691** · `rental` **349** · `over_ceiling` **427** · blank `span_aa` **0**.

⚠⚠ **Split by whether the protein was actually folded, because the total hides the finding**
(method-note item 2). Against `census_features.v1.jsonl` (**2,690** accessions):

* **all 2,690 folded census proteins are `local`** — every census fold in the artifact sits
  inside the measured local envelope, which is what makes D-077's ✅ *Reproducibility* claim
  sayable at all; and
* the **777** never-folded rows are `over_ceiling` **427** · `rental` **349** · `local` **1**.

⚠ **The cross-check against `core/census_unfolded.py`'s reasons is EXACT for `rental` and is
NOT exact for `over_ceiling`, and the difference is the interesting part.** Measured:
`ceiling_unmeasured` **349** = `rental` **349**; `above_local_ceiling` **424** ≠
`over_ceiling` **427**. The gap is the **3 mucins**, whose recorded reason is
`mucin_out_of_class` (D-111 — never ESMFold) while their spans are over-ceiling anyway: a row
can be refused for a reason that is not its cost. And `reason_unrecorded` **1**
(`P55073`/`DIO3`, 237 aa) is costed **`local`** — it should have folded, it did not, and
nothing records why. ⚠ *"349 and 427 reconcile exactly"* was the first form of this note and
it was **wrong on the second half**; the reconciliation test caught it. Two instruments over
one span agreeing is the check — where they disagree, the disagreement has to be named rather
than rounded off.

⚠ Rows served from the database can still carry no `span_aa` in `meta`, which the manifest
cannot show — that is why `span_unrecorded` exists rather than being asserted impossible.

⚠⚠ **WHAT THE PER-ROW CAVEATS COST, MEASURED RATHER THAN WAVED THROUGH.** `cost_axis`,
`cost_recipe` and `cost_note` are identical on thousands of rows, and `app/reads.py`
records that the census list is already **7.1 MB uncompressed / 825 KB gzipped / ~4.8 s**.
Encoding all five fields for the 3,467 manifest spans adds **2,732,206 bytes (2.67 MB,
788 B/row) uncompressed and 18,064 bytes (17.6 KB) gzipped at level 9** — a ~37% rise in
bytes the reader never sees and a ~2.1% rise in bytes that actually travel, because gzip
collapses a string repeated 3,467 times to almost nothing.

⚠ The alternative — the axis statement and the meanings typed into `CensusTable.jsx` —
was considered and rejected, and not for weight: it would put a **second copy** of D-077's
refusal in the one file where someone adding a cost chip would be working, and it would put
the measured ceiling (440 / 630 / int8 / chunk 64) in a file that `core/manifest.py` keeps
one constant precisely to keep it out of. The page-level-declaration-on-every-row shape is
the one `census_staining_read.py` already uses for HPA attribution, which the census table
picks up with `rows.find((r) => r.staining)`.
"""
from __future__ import annotations

from typing import Any, Iterable

from core.foldability import LOCAL, OVER_CEILING, RENTAL, describe
from core.foldability import envelope as _envelope
from core.manifest import LOCAL_CEILING, FoldCeiling

#: ⚠ The span was never recorded on the row, so it has **no** envelope. Fourth outcome,
#: never a fourth price — see the module docstring for why this is not `no_topology`.
SPAN_UNRECORDED = "span_unrecorded"

#: The vocabulary, in the order a **cost** runs — cheapest first. ⚠ `SPAN_UNRECORDED` is
#: deliberately absent: it has no position in a cost order, and giving it one would make it
#: the dearest row on one header click. The surface sorts it last in BOTH directions, the
#: same rule a null pLDDT already gets.
COST_ORDER = (LOCAL, RENTAL, OVER_CEILING)

#: Every outcome this supplier can stamp. Exhaustive by construction.
COST_VERDICTS = COST_ORDER + (SPAN_UNRECORDED,)

#: ⚠ The displayed TERM is the vocabulary itself (`core.foldability`), not a second spelling.
#: D-133's rule: the API owns the term, the legend owns the meaning. `over ceiling` loses only
#: the underscore, exactly as `tiles_only` renders `tiles only`.
COST_LABEL = {
    LOCAL: "local",
    RENTAL: "rental",
    OVER_CEILING: "over ceiling",
    SPAN_UNRECORDED: "span not recorded",
}

#: ⚠⚠ THE STATEMENT D-077 DEC 1 REFUSAL 2 REQUIRES, and it travels with the datum rather
#: than sitting in a doc. A cost class beside a census of ADC targets, unlabelled, is an
#: invitation to read cheap as good.
COST_AXIS = (
    "COMPUTE COST, NOT SUITABILITY. This column says where this protein's extracellular "
    "span can be folded at the measured recipe — what it costs to compute. It says nothing "
    "about whether the protein is a good ADC target, and nothing here is a score or a rank. "
    "It also filters nothing: every census row stays in the census, whatever it costs "
    "(D-077 dec 1)."
)

#: ⚠⚠ ONE MEANING PER CATEGORY, SERVED. The legend renders these off the rows, so the page
#: cannot come to define a word differently from the module that assigns it.
#: ⚠⚠ `rental` CARRIES ITS CLOSURE. "rental" on a row must never read as a queue position:
#: `core/census_unfolded.py` already refuses the words *"waiting on rented capacity"* because
#: rental for the hold-48 remainder **closed 2026-09-05 PT (pod Terminated)** (D-118). A cost
#: CLASS is not a plan to spend, and the label says which.
COST_MEANING = {
    LOCAL: (
        "its extracellular span is inside the measured local envelope, so this fold costs "
        "no rented compute — it is reproducible by any reader with the same consumer card "
        "and no cloud spend."
    ),
    RENTAL: (
        "its span is above the measured local bound but below the point where a single card "
        "definitively fails, so folding it would need rented compute. ⚠ A COST CLASS, NOT A "
        "QUEUE POSITION: rental for the hold-48 remainder closed 2026-09-05 (pod Terminated), "
        "so this is what the fold would have cost, never a fold that is being waited on."
    ),
    OVER_CEILING: (
        "its span is at or above the length that is measured to fail, so it folds on no single "
        "card as one sequence. ⚠ Deliberately NOT the same class as rental: \"costs money\" and "
        "\"cannot be bought at any price on one card\" are different facts, and pooling them "
        "would let a census quote a price for something that cannot be bought. ⚠ It is also not "
        "a statement about tiles or assembly — how a structure was MADE is the Structure "
        "column, and a protein assembled from tiles is still over the single-pass ceiling."
    ),
    SPAN_UNRECORDED: (
        "no extracellular span is recorded on this row, so it has no envelope and no cost. "
        "⚠ A named absence, never counted as affordable — an unmeasured target bucketed as "
        "cheap is how a cost estimate becomes a fiction (D-024)."
    ),
}


def cost_recipe(ceiling: FoldCeiling = LOCAL_CEILING) -> str:
    """The ceiling AND the recipe it was measured under, from the one constant that holds it.

    ⚠ D-077 dec 3 / D-050: a cost claim without its recipe is not checkable — the same span
    is affordable at int8 and not at fp16. No length literal is written here; this reads
    `core.foldability.describe`, which reads `LOCAL_CEILING`.
    """
    return describe(ceiling)


def cost_for_span(span_aa: Any, ceiling: FoldCeiling = LOCAL_CEILING) -> str:
    """The cost category for one row's span. ⚠ Never raises, and never guesses `local`.

    `envelope()` raises on an absent span by design, which is right for a batch tool and
    wrong for a route serving thousands of rows — so the absence is *named here* and the
    raise is left intact for every caller that should still get it.

    ⚠ Anything that is not a positive whole number of residues is `span_unrecorded`: a
    zero-length span is not a free fold, it is a measurement that did not happen, which is
    the reading `core/census.py::categorise` already gives it.
    """
    span = _whole_residues(span_aa)
    if span is None:
        return SPAN_UNRECORDED
    return _envelope(span, ceiling=ceiling)


def cost_block(span_aa: Any, ceiling: FoldCeiling = LOCAL_CEILING) -> dict[str, str]:
    """The five fields a census row carries for cost. Every one of them is load-bearing.

    `cost` is the CATEGORY — the thing a column sorts on, so a copy edit to a label can
    never re-order the table (D-133's rule, learnt on `structure_kind_label`).
    `cost_label` is the displayed term, owned here so the surface never re-spells it.
    `cost_note` is that category's meaning, including `rental`'s closure.
    `cost_axis` is D-077 dec 1 refusal 2's statement, and `cost_recipe` is D-016's provenance.
    """
    verdict = cost_for_span(span_aa, ceiling)
    return {
        "cost": verdict,
        "cost_label": COST_LABEL[verdict],
        "cost_note": COST_MEANING[verdict],
        "cost_axis": COST_AXIS,
        "cost_recipe": cost_recipe(ceiling),
    }


def apply_cost(rows: Iterable[dict], ceiling: FoldCeiling = LOCAL_CEILING) -> list[dict]:
    """Stamp the cost block onto **every** row, and return **every** row.

    ⚠⚠ THE REFUSAL IS THE SIGNATURE. There is no predicate argument, no threshold, and no
    branch that can drop a row — `D-077` dec 1 refusal 3 is enforced by there being nothing
    here to enforce it with. A caller who wants an affordable-only census has to write the
    comprehension themselves, in the open, where a reviewer can see it.

    ⚠ Reads `span_aa`, which both halves of the list already carry: the projected rows from
    `census_projection` (`meta["span_aa"]`) and the never-folded manifest rows from
    `core.census_unfolded` (`int(r["span_aa"])`). A row missing it takes `span_unrecorded`
    rather than being skipped, so the two populations stay the same length as they arrived.
    """
    out = list(rows)
    for row in out:
        row.update(cost_block(row.get("span_aa"), ceiling))
    return out


def _whole_residues(value: Any) -> int | None:
    """A positive whole number of residues, or `None` — the only two answers a span has here.

    ⚠ `bool` is rejected explicitly. `isinstance(True, int)` is `True` in Python, so a
    truthiness flag that reached this field would otherwise be costed as a 1 aa protein
    folding locally for free.
    """
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, int):
        return value if value > 0 else None
    # ⚠ a JSON `meta` can hold `"630"` or `630.0`; both are the measurement, and refusing
    # them would report an absence where a span exists. A fraction of a residue is not a
    # span, so it is refused rather than rounded.
    if isinstance(value, float):
        return int(value) if value > 0 and value.is_integer() else None
    if isinstance(value, str) and value.strip().isdigit():
        n = int(value.strip())
        return n if n > 0 else None
    return None
