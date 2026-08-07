"""The span definition — TWO of them, both named, from 2026-08-07 onward.

⚠ **`### D-081`. There are two definitions in this repository and neither is "the" definition.**
The 82-target cohort is frozen under `V1` **permanently**; the census uses `V2`. **Every artifact
naming a span states which definition produced it, and no artifact compares a span under one to a
span under the other without saying which.** A number that moves because a definition moved is not
a new measurement.

⚠ **`V1` IS NOT LEGACY AND IS NOT DEPRECATED.** It is the definition `### F-004` and `### F-017`
were measured under, and re-running the cohort under `V2` would spend `### D-075`'s pre-registration
— which is the apparatus that makes those results mean anything. `V1` must keep reproducing the old
file byte for byte, which is why `V2` is opt-in at every call site rather than a new default.

## What `V1` actually measured, and why it was renamed

`V1` is a **substring match on `"extracellular"`** over `Topological domain` descriptions. The band
it produced was called `no_topology`, and `### F-025` establishes that the band reported **five**
different things, only one of which is *"this protein has no reachable domain"*:

  1. a reachable face under other vocabulary (`Lumenal`, `Vesicular`, `Exoplasmic loop`, …)
  2. `Transmembrane` present, faces never labelled — ⚠ a genuine annotation gap that no widening fixes
  3. GPI-anchored — no topology **by design**, and it needs a different extraction rule entirely
  4. only an unreachable or cytoplasmic face — correctly excluded
  5. ⚠ the term matched and the **coordinate** was `UNKNOWN`

So the band is renamed to `no_extracellular_span`, which is what it measures, and mechanisms 3 and 5
get categories of their own rather than being absorbed into an absence.

## The vocabulary ruling is BIOLOGICAL, not lexical

⚠ **Do not widen to "anything not cytoplasmic."** The test is one question: **can this face ever
reach the outside of the cell?** Secretory-pathway faces — ER, Golgi, endosome, lysosome, secretory
vesicle — do: vesicle fusion puts them outside. **Mitochondrial, peroxisomal and nuclear faces do
not, on any mechanism**, because those organelles do not fuse with the plasma membrane. A careless
widening would recruit ~418 annex domains that cannot be ADC targets on any mechanism — **in the
direction that makes the atlas look bigger.** That is the failure mode this module exists to prevent.

⚠ **`Perinuclear space` is the trap.** It is continuous with the ER lumen and therefore ACCEPTED —
and it contains the substring `nuclear`, so a widening written as *"not cytoplasmic and not nuclear"*
silently drops all 16. **The membership test is a set, not a substring, for exactly this reason.**

⚠ **Compartment reasoning is Planner-supplied general knowledge and is NOT sourced at first hand**
(D-016). It is ruled on that basis and the glossary says so.
"""

from __future__ import annotations

#: ⚠ The frozen definition. `### D-081` — the 82 are measured under this permanently.
V1_EXTRACELLULAR_SUBSTRING = "v1-extracellular-substring-2026-07-21"

#: The ruled definition. Census only.
V2_RULED_VOCABULARY = "v2-ruled-vocabulary-2026-08-07"

SPAN_DEFINITIONS: tuple[str, ...] = (V1_EXTRACELLULAR_SUBSTRING, V2_RULED_VOCABULARY)

#: ⚠ ACCEPTED — the face can reach the outside of the cell. Acceptance places a protein in the
#: FOLDABLE population, not on a shortlist; the ranking still happens downstream.
ACCEPTED_TERMS: frozenset[str] = frozenset({
    "Extracellular",        # unchanged — the original definition
    "Lumenal",              # ER / Golgi / endosome / lysosome. The core case
    "Lumenal, vesicle",     # secretory-vesicle lumen — fuses with the membrane by definition
    "Vesicular",            # the same, generic
    "Intragranular",        # secretory-granule lumen — exocytosis exposes it
    "Exoplasmic loop",      # ⚠ *exoplasmic* MEANS the non-cytoplasmic face. A third word for it
    "Perinuclear space",    # ⚠ continuous with the ER lumen. Same compartment, different name
})

#: ⚠ HELD — ruled AFTER a check, not before. **They are not accepted and gain nothing.**
#: The check is deliberately orthogonal to the vocabulary: do the proteins carrying these terms
#: appear in an EXPERIMENTAL cell-surface dataset? Topology vocabulary is a curator's word choice;
#: surface proteomics is a measurement. ⚠ That they sit in SURFY's positive class is supporting but
#: WEAKER evidence — A-014 holds that a model's positive class is a prediction, not a fact.
HELD_TERMS: frozenset[str] = frozenset({
    "Lumenal, melanosome",  # melanosomes are lysosome-related organelles; a specialised lineage
    "Vacuolar",             # usually lysosome-like in human annotation; lysosomal exocytosis is real
})

#: REJECTED — cannot reach the plasma membrane on any mechanism.
REJECTED_TERMS: frozenset[str] = frozenset({
    "Mitochondrial intermembrane", "Mitochondrial matrix",
    "Nuclear", "Peroxisomal matrix", "Peroxisomal",
    "Cytoplasmic",
})

#: The band and category vocabulary. ⚠ Every one of these is an ABSENCE WITH A CAUSE, never a zero
#: and never a bare null. `no_topology` is retired: it made a claim its filter could not support.
NO_EXTRACELLULAR_SPAN = "no_extracellular_span"
SPAN_BOUNDARY_UNKNOWN = "span_boundary_unknown"
TERM_UNRULED = "term_unruled"
ABSENT_WITH_REASON = "absent_with_reason"

#: How a span was produced. ⚠ Recorded on every row — a span whose rule is unknown is a span whose
#: meaning is unknown.
RULE_VOCABULARY = "vocabulary"
RULE_GPI_A = "gpi_rule_A"
RULE_GPI_B = "gpi_rule_B"

SPAN_RULES: tuple[str, ...] = (RULE_VOCABULARY, RULE_GPI_A, RULE_GPI_B)

SPAN_CATEGORIES: tuple[str, ...] = (
    NO_EXTRACELLULAR_SPAN, SPAN_BOUNDARY_UNKNOWN, TERM_UNRULED, ABSENT_WITH_REASON,
)


class UnknownSpanDefinition(ValueError):
    """A span definition outside `SPAN_DEFINITIONS`. ⚠ Raised, never defaulted — the whole point of
    D-081 is that no artifact carries an unnamed definition."""


def require_definition(value: object) -> str:
    if value in SPAN_DEFINITIONS:
        return str(value)
    raise UnknownSpanDefinition(
        f"unknown span definition {value!r}; expected one of {SPAN_DEFINITIONS}. "
        f"⚠ D-081: every artifact naming a span states which definition produced it."
    )


def classify_term(description: str) -> str:
    """`accepted` | `held` | `rejected` | `term_unruled`.

    ⚠ **Set membership on the EXACT description, never a substring.** A substring test is the defect
    this whole arc came from, and `Perinuclear space` — accepted, containing `nuclear` — would be
    dropped by the obvious rewrite of it.

    ⚠ **An unrecognised term is `term_unruled`: named and reported, never silently dropped and never
    silently accepted.** The census contains exactly one today (`Mother cell cytoplasmic`, n=1), and
    the register is where it gets ruled.
    """
    d = (description or "").strip()
    if d in ACCEPTED_TERMS:
        return "accepted"
    if d in HELD_TERMS:
        return "held"
    if d in REJECTED_TERMS:
        return "rejected"
    return TERM_UNRULED
