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
    # ── ruled 2026-08-07 after the CSPA check, promoted from HELD ──
    "Lumenal, melanosome",  # 3/3 CSPA category 1 — experimentally surface-detected, 449-458 aa
    "Vacuolar",             # ⚠ accepted on COMPARTMENT BIOLOGY, not on the two instances seen
})

#: ⚠ HELD — ruled AFTER a check, not before. **They are not accepted and gain nothing.**
#: The check is deliberately orthogonal to the vocabulary: do the proteins carrying these terms
#: appear in an EXPERIMENTAL cell-surface dataset? Topology vocabulary is a curator's word choice;
#: surface proteomics is a measurement. ⚠ That they sit in SURFY's positive class is supporting but
#: WEAKER evidence — A-014 holds that a model's positive class is a prediction, not a fact.
#: ⚠ EMPTY, AND THE CONSTANT STAYS. Both terms were ruled ACCEPTED on 2026-08-07 after the check.
#: An empty frozenset is a finding — "the held list was worked through" — where a deleted constant
#: would read as "there was never a holding pen." Same rule as an empty band key versus an omitted
#: one, which is the distinction this whole vocabulary exists to keep.
HELD_TERMS: frozenset[str] = frozenset()

#: REJECTED — cannot reach the plasma membrane on any mechanism.
REJECTED_TERMS: frozenset[str] = frozenset({
    "Mitochondrial intermembrane", "Mitochondrial matrix",
    "Nuclear", "Peroxisomal matrix", "Peroxisomal",
    "Cytoplasmic",
    # ⚠ Ruled 2026-08-07, hypothesis 1: yeast ortholog annotation transfer. `P0DKB6` MPC1L is
    # Homo sapiens 9606, reviewed — the organism check closed the serious branch. It is a
    # CYTOPLASMIC term wearing sporulation vocabulary, so it is rejected for the same reason
    # `Cytoplasmic` is, and it is REJECTED rather than deleted so the ruling stays visible.
    "Mother cell cytoplasmic",
})

#: The band and category vocabulary. ⚠ Every one of these is an ABSENCE WITH A CAUSE, never a zero
#: and never a bare null. `no_topology` is retired: it made a claim its filter could not support.
NO_EXTRACELLULAR_SPAN = "no_extracellular_span"

#: ⚠ The reason a GPI protein takes when rule A cannot run. Named, excluded, NEVER defaulted into a
#: span — the withdrawn rule B is what defaulting would have looked like.
REASON_GPI_POSITION_UNANNOTATED = "gpi_anchor_position_unannotated"
REASON_GPI_NO_CHAIN = "gpi_chain_unannotated"

#: ⚠⚠ THE MATURE-CHAIN SELECTOR, ruled 2026-08-07 after a live defect on MSLN.
#:
#: A GPI-anchored mature chain is **by definition the one terminating at the anchor** — the
#: anchor position selects the chain, not the other way round. `min(start)`, `Chain[0]` and
#: "the longest" are all wrong, and `min(start)` was wrong LIVE: on `Q13421` MSLN it took 37,
#: carrying ~250 residues of the megakaryocyte-potentiating factor — a fragment that is
#: cleaved off and **secreted**, so an antibody never meets it — fused to the ectodomain that
#: matters. ⚠ On the one protein `### F-025` is named after, and it would have folded,
#: scored, banded and looked entirely normal.
#:
#: ⚠ `P51654`'s −195 and MSLN's +250 are the SAME defect at opposite ends of the molecule.
#: Rule B was barred for over-reading the C-terminus; this is the N-terminal twin, and it was
#: live while B never fired.
#:
#: ⚠ **No chain ends at the anchor, OR the candidates disagree → named and excluded, never
#: guessed.** The disagreeing case is not the owner's ruling and is not invented here: MSLN
#: carries BOTH `Mesothelin` 37-598 and `Mesothelin, cleaved form` 296-598, both terminating at
#: the anchor, giving 561 and 302. Choosing between them is a ruling, so it lands here instead.
REASON_GPI_MATURE_CHAIN_AMBIGUOUS = "gpi_mature_chain_ambiguous"

#: ⚠ LIVE GUARDS, not one-off checks. Both of these found a real defect once; a check that runs only
#: when someone remembers to run it will not find the second one.
GUARD_CHAIN_OVERRUNS_ANCHOR = "chain_end_exceeds_anchor"
GUARD_CHAIN_START_AMBIGUOUS = "chain_start_ambiguous"
SPAN_BOUNDARY_UNKNOWN = "span_boundary_unknown"
TERM_UNRULED = "term_unruled"
ABSENT_WITH_REASON = "absent_with_reason"

#: How a span was produced. ⚠ Recorded on every row — a span whose rule is unknown is a span whose
#: meaning is unknown.
RULE_VOCABULARY = "vocabulary"
RULE_GPI_A = "gpi_rule_A"

#: ⚠⚠ RULE B IS WITHDRAWN, 2026-08-07, and it is not a deprecation — it is a bar.
#:
#: B was `Chain` start → `Chain` end. The divergence check that was supposed to VALIDATE it killed
#: it instead: on all six proteins where A and B disagree, `Chain` runs straight through the
#: C-terminal GPI signal that is cleaved and replaced by the anchor — by **266 residues** on
#: `Q96GW7` — and on three of those six that removed segment is annotated nowhere at all.
#: **`Chain` is not the mature protein for those entries.** B would have folded a chimera of the
#: real ectodomain and a signal peptide that does not exist in the mature protein.
#:
#: ⚠ **B fired zero times, so nothing produced was ever wrong.** That is exactly why it is barred
#: rather than left in place: **a fallback that is unsafe when it fires is not a fallback, it is a
#: latent defect waiting for a `Lipidation` annotation to go missing.**
RULE_GPI_B_WITHDRAWN = "gpi_rule_B"

SPAN_RULES: tuple[str, ...] = (RULE_VOCABULARY, RULE_GPI_A)

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
