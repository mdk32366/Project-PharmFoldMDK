"""The V2 span definition: the ruled vocabulary, the GPI rule, and the two named absences.

⚠ **A-017, THREE CLAUSES, EACH ASSERTED SEPARATELY.** (a) the fixture reaches the code under test;
(b) one property, one test; (c) **the fixture contains a case where correct and incorrect differ.**
On 2026-08-06 three revert proofs proved nothing because the fixture's world was too small to
contain the bug, so clause (c) gets its own positive controls here rather than being assumed.

⚠ **AND THE FROZEN DEFINITION IS ASSERTED, NOT HOPED FOR.** `### D-081` freezes the 82 under V1
permanently. If `scripts/ecd_lengths.py:parse()` ever learns the V2 vocabulary, the cohort stops
being reproducible under the definition that measured it — so that is a test, not a comment.
"""

from __future__ import annotations

import pytest

from core.span_definition import (
    ACCEPTED_TERMS, HELD_TERMS, NO_EXTRACELLULAR_SPAN, REJECTED_TERMS, RULE_GPI_A, RULE_GPI_B,
    RULE_VOCABULARY, SPAN_BOUNDARY_UNKNOWN, TERM_UNRULED, UnknownSpanDefinition,
    V1_EXTRACELLULAR_SUBSTRING, V2_RULED_VOCABULARY, classify_term, require_definition,
)
from core.span_extract import SpanResult, divergence, extract, mature_chain_bounds


# ── fixture builders ────────────────────────────────────────────────────────
def _loc(start, end, *, smod="EXACT", emod="EXACT"):
    return {"start": {"value": start, "modifier": smod}, "end": {"value": end, "modifier": emod}}


def td(desc, start, end, **kw):
    return {"type": "Topological domain", "description": desc, "location": _loc(start, end, **kw)}


def entry(*feats):
    return {"features": list(feats), "sequence": {"length": 1000}}


def chain(start, end):
    return {"type": "Chain", "description": "", "location": _loc(start, end)}


def lipid(pos, desc="GPI-anchor amidated serine"):
    return {"type": "Lipidation", "description": desc, "location": _loc(pos, pos)}


# ── (c) THE DISCRIMINATING FIXTURES — one per mechanism ─────────────────────
def test_a_protein_whose_only_face_is_lumenal_gains_a_span():
    """⚠ THE CORE CASE. Under V1 this protein has NO span at all — `Lumenal` does not contain the
    substring `extracellular`. Prove it bites by removing `Lumenal` from `ACCEPTED_TERMS`: the
    result becomes `no_extracellular_span` and this reds at the span assertion."""
    r = extract(entry(td("Lumenal", 24, 704), td("Cytoplasmic", 726, 904)))
    assert r.span_aa == 681, r
    assert r.rule == RULE_VOCABULARY
    assert not r.category, "a protein that gained a span also carries an absence category"


def test_a_protein_whose_only_face_is_mitochondrial_matrix_gains_nothing():
    """⚠ THE REJECTION MUST BITE. Mitochondria do not fuse with the plasma membrane, and a widening
    to *"anything not cytoplasmic"* would have recruited ~418 annex domains that cannot be ADC
    targets on any mechanism — in the direction that makes the atlas look bigger.

    Prove it bites by moving `Mitochondrial matrix` into `ACCEPTED_TERMS`: a span appears and this
    reds naming it."""
    r = extract(entry(td("Mitochondrial matrix", 2, 19), td("Mitochondrial matrix", 75, 136)))
    assert r.span_aa is None, f"an unreachable face produced a span: {r}"
    assert r.category == NO_EXTRACELLULAR_SPAN


def test_perinuclear_space_is_accepted_although_its_name_contains_nuclear():
    """⚠ THE TRAP, AND IT HAS ITS OWN TEST. `Perinuclear space` is continuous with the ER lumen and
    is ACCEPTED — while `Nuclear` is rejected. A widening written as *"not cytoplasmic and not
    nuclear"* silently drops all 16 of them.

    Prove it bites by reimplementing `classify_term` as a substring test: `Perinuclear space` starts
    matching `Nuclear`, and this reds."""
    assert classify_term("Perinuclear space") == "accepted"
    assert classify_term("Nuclear") == "rejected"
    r = extract(entry(td("Perinuclear space", 10, 110)))
    assert r.span_aa == 101, r


def test_a_gpi_protein_with_lipidation_uses_rule_A():
    """⚠ Rule A: `Chain` start → (`Lipidation` − 1). Prove it bites by swapping the precedence so B
    runs first: the span becomes the full chain and this reds on the number."""
    r = extract(entry(chain(37, 598), lipid(598)))
    assert r.rule == RULE_GPI_A, r
    assert r.span_aa == 598 - 37, r


def test_a_gpi_protein_without_lipidation_falls_back_to_rule_B():
    """⚠ B recovers a protein A would otherwise drop. Fixture: a `Chain` and a GPI anchor recorded
    only as a `Region` — i.e. the anchor is known but not annotated as `Lipidation`.

    ⚠ But a `Region` mentioning GPI is a MENTION, not an annotation, so this protein has no
    authoritative anchor at all and must NOT be treated as GPI-anchored."""
    r = extract(entry(chain(20, 300),
                      {"type": "Region", "description": "GPI-anchor attachment region",
                       "location": _loc(295, 300)}))
    assert r.rule != RULE_GPI_A
    assert r.category == NO_EXTRACELLULAR_SPAN, (
        f"a Region merely MENTIONING a GPI anchor was treated as an annotation of one: {r}")


def test_rule_B_produces_the_full_mature_chain_when_lipidation_is_unusable():
    """The genuine rule-B path: a GPI `Lipidation` whose position sits before the chain start, so A
    cannot be computed. Prove it bites by deleting the B branch: the row becomes
    `absent_with_reason` and this reds."""
    r = extract(entry(chain(100, 400), lipid(50)))
    assert r.rule == RULE_GPI_B, r
    assert r.span_aa == 400 - 100 + 1


def test_a_gpi_protein_with_no_chain_is_absent_with_reason_not_dropped():
    """⚠ Missing a required feature is a NAMED CATEGORY, never a silent drop from a denominator.
    Two real proteins are in this state — `P25063` and `P31358`.

    Prove it bites by returning `None` and letting the caller skip the row: the denominator loses
    two rows and nothing says so."""
    r = extract(entry(lipid(300)))
    assert r.span_aa is None
    assert r.category == "absent_with_reason"
    assert "Chain" in r.reason, r.reason


def test_an_sdk1_shaped_null_coordinate_is_its_own_category_and_invents_nothing():
    """⚠ THE F-020 SHAPE. The term MATCHED — `Extracellular` is accepted — and the coordinate is
    `UNKNOWN`. It is neither *no reachable domain* nor a usable span.

    Prove it bites by defaulting the null start to `1`: a 2,009 aa span appears from a coordinate
    nobody measured, and this reds at the category."""
    r = extract(entry(td("Extracellular", None, 2009, smod="UNKNOWN")))
    assert r.span_aa is None, f"a coordinate was invented: {r}"
    assert r.category == SPAN_BOUNDARY_UNKNOWN
    assert "2009" in r.boundary_coordinate, (
        f"the category must RECORD the coordinate it does have: {r.boundary_coordinate!r}")
    assert "UNKNOWN" in r.boundary_coordinate


def test_an_unrecognised_term_is_named_never_silently_dropped_or_accepted():
    """⚠ THE DEFECT THIS WHOLE ARC CAME FROM. A term outside accept/held/reject must land loudly.

    Prove it bites by making `classify_term` return `rejected` for unknowns: the row becomes
    `no_extracellular_span`, the term vanishes, and this reds."""
    r = extract(entry(td("Mother cell cytoplasmic", 43, 51)))
    assert r.category == TERM_UNRULED, r
    assert "Mother cell cytoplasmic" in r.reason
    assert r.terms_unruled == ["Mother cell cytoplasmic"]


def test_a_held_term_gains_nothing_and_is_reported():
    """⚠ HELD IS NOT ACCEPTED. `Lumenal, melanosome` and `Vacuolar` are ruled after a check, and
    until then they produce no span. Prove it bites by folding `HELD_TERMS` into `ACCEPTED_TERMS`:
    five surface proteins gain spans that no ruling authorised, and this reds."""
    r = extract(entry(td("Vacuolar", 10, 200)))
    assert r.span_aa is None, f"a HELD term produced a span before it was ruled: {r}"
    assert r.category == NO_EXTRACELLULAR_SPAN
    assert r.terms_held == ["Vacuolar"]


def test_vocabulary_wins_over_gpi_when_both_are_present():
    """Precedence is load-bearing: an accepted domain with real coordinates beats the GPI rule."""
    r = extract(entry(td("Lumenal", 30, 530), chain(20, 600), lipid(590)))
    assert r.rule == RULE_VOCABULARY and r.span_aa == 501, r


# ── (a) the fixtures reach the code at all ──────────────────────────────────
def test_the_extractor_returns_a_span_for_a_plainly_extracellular_protein():
    """⚠ A-017 clause (a) positive control. If the extractor were broken outright, every refusal
    above would pass for the wrong reason."""
    r = extract(entry(td("Extracellular", 1, 100)))
    assert r.span_aa == 100 and r.rule == RULE_VOCABULARY


def test_the_multi_chain_fixture_actually_contains_two_chains():
    """⚠ A-017 clause (c) for `mature_chain_bounds`. With one `Chain` the min/max and the `[0]` pick
    are indistinguishable — and taking `[0]` produced a NEGATIVE rule-A-minus-rule-B divergence on
    `P51654` during the pre-registration. That is the bug this fixture must be able to hold."""
    e = entry(chain(20, 200), chain(210, 500))
    assert len(e["features"]) == 2
    assert mature_chain_bounds(e) == (20, 500), (
        "mature chain bounds took one Chain record instead of spanning them all")


# ── (b) one property, one test ──────────────────────────────────────────────
def test_the_ruled_vocabularies_do_not_overlap():
    assert not (ACCEPTED_TERMS & REJECTED_TERMS)
    assert not (ACCEPTED_TERMS & HELD_TERMS)
    assert not (HELD_TERMS & REJECTED_TERMS)


def test_a_span_result_cannot_carry_both_a_span_and_an_absence():
    """⚠ The invariant that keeps an absence from being read as a low number."""
    with pytest.raises(ValueError):
        SpanResult(span_aa=100, category=NO_EXTRACELLULAR_SPAN)
    with pytest.raises(ValueError):
        SpanResult()


def test_an_unnamed_span_definition_raises_rather_than_defaulting():
    """⚠ D-081: every artifact naming a span states which definition produced it. Prove it bites by
    adding an `or V2_RULED_VOCABULARY` fallback."""
    assert require_definition(V1_EXTRACELLULAR_SUBSTRING) == V1_EXTRACELLULAR_SUBSTRING
    with pytest.raises(UnknownSpanDefinition):
        require_definition("v2")
    with pytest.raises(UnknownSpanDefinition):
        require_definition(None)


def test_the_divergence_check_reports_both_rules_and_never_feeds_the_span():
    """⚠ A check on the rule, not an input to it. `Q96GW7`'s real shape: `Chain` runs 266 residues
    past the anchor because the C-terminal GPI signal is cleaved and not annotated."""
    e = entry(chain(23, 911), lipid(646))
    assert divergence(e) == (623, 889)
    assert extract(e).span_aa == 623, "the divergence check leaked into the produced span"


# ── ⚠ D-081: the frozen path must stay frozen ───────────────────────────────
def test_the_v1_extractor_does_not_know_the_v2_vocabulary():
    """⚠⚠ THE FREEZE, ASSERTED. `### D-081` freezes the 82 under V1 permanently, and the cohort
    stays reproducible only while `scripts/ecd_lengths.py:parse()` keeps ignoring `Lumenal`.

    Prove it bites by teaching `parse()` the accepted term list: this reds, and it reds *before*
    anyone re-runs the cohort and quietly gets different numbers."""
    from scripts.ecd_lengths import parse
    rec = parse("TEST", "", entry(td("Lumenal", 24, 704)))
    assert rec.largest_span is None, (
        "scripts/ecd_lengths.py:parse() now admits a V2 term. D-081 freezes the 82 under V1; the "
        "cohort's committed spans are no longer reproducible from its own extractor.")
    rec2 = parse("TEST", "", entry(td("Extracellular", 1, 100)))
    assert rec2.largest_span == 100, "the V1 positive control failed — parse() is broken outright"
