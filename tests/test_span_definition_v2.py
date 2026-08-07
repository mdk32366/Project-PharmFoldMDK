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
    ABSENT_WITH_REASON, ACCEPTED_TERMS, GUARD_CHAIN_OVERRUNS_ANCHOR, GUARD_CHAIN_START_AMBIGUOUS,
    HELD_TERMS, NO_EXTRACELLULAR_SPAN, REASON_GPI_NO_CHAIN, REASON_GPI_POSITION_UNANNOTATED, REJECTED_TERMS,
    RULE_GPI_A, RULE_VOCABULARY, SPAN_BOUNDARY_UNKNOWN, SPAN_RULES, TERM_UNRULED,
    UnknownSpanDefinition, V1_EXTRACELLULAR_SUBSTRING, V2_RULED_VOCABULARY, classify_term,
    require_definition,
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


def test_a_gpi_protein_without_a_lipidation_annotation_is_absent_with_reason_never_a_span():
    """⚠⚠ RULE B IS BARRED, 2026-08-07, and this is where its input now lands.

    B was `Chain` start → `Chain` end, and the divergence check meant to VALIDATE it killed it
    instead: `Chain` runs straight through the C-terminal GPI signal that is cleaved and replaced
    by the anchor — 266 residues on `Q96GW7` — and on three of six divergent proteins that segment
    is annotated nowhere. **`Chain` is not the mature protein for those entries**, so B would have
    folded a chimera of the real ectodomain and a signal that does not exist in the mature protein.

    ⚠ B fired zero times, which is exactly why it is barred rather than left in place: **a fallback
    that is unsafe when it fires is not a fallback — it is a latent defect waiting for a
    `Lipidation` annotation to go missing.**

    Prove it bites by restoring the B branch: a span appears where a named absence belongs."""
    r = extract(entry(chain(20, 300), lipid(None)))
    assert r.span_aa is None, f"the withdrawn rule B produced a span: {r}"
    assert r.category == ABSENT_WITH_REASON
    assert r.reason == REASON_GPI_POSITION_UNANNOTATED


def test_rule_B_is_not_in_the_declared_rule_vocabulary_at_all():
    """⚠ A barred rule still listed in the vocabulary is a rule someone will reach for."""
    assert SPAN_RULES == (RULE_VOCABULARY, RULE_GPI_A)
    assert "gpi_rule_B" not in SPAN_RULES


def test_a_gpi_protein_whose_anchor_precedes_the_chain_start_is_named_not_defaulted():
    """The other unusable-position shape. ⚠ Under rule B this became the full `Chain`."""
    r = extract(entry(chain(100, 400), lipid(50)))
    assert r.span_aa is None, f"an unusable anchor position produced a span: {r}"
    # ⚠ No chain CONTAINS position 50 (the only chain is 100-400), so there is no anchored species.
    assert r.reason == "gpi_no_chain_spans_anchor"
    # and a genuinely unannotated position still lands on its own reason
    assert extract(entry(chain(20, 300), lipid(None))).reason == REASON_GPI_POSITION_UNANNOTATED


def test_the_chain_overrun_guard_fires_and_is_carried_on_the_row():
    """⚠ A LIVE GUARD, not a one-off check. `Chain` running past the anchor is how rule B was
    caught, and a check that runs only when someone remembers to run it will not catch the second
    one. The fixture is `Q96GW7`'s real shape: chain 23-911, anchor 646.

    Prove it bites by deleting the guard — the row still gets the right span, and the thing that
    caught the defect quietly stops watching."""
    r = extract(entry(chain(23, 911), lipid(646)))
    # ⚠ The row keeps its span under the corrected selector AND still carries the flag. A guard
    # that only fired on exclusions would go quiet the moment the exclusion was lifted.
    assert r.span_aa == 623 and r.rule == RULE_GPI_A
    assert GUARD_CHAIN_OVERRUNS_ANCHOR in r.guards, r
    clean = extract(entry(chain(37, 598), lipid(598)))
    assert GUARD_CHAIN_OVERRUNS_ANCHOR not in clean.guards, (
        "the guard fires on a protein whose chain ends at the anchor — it would flag everything "
        "and therefore flag nothing")


def test_disagreeing_chain_starts_are_flagged_rather_than_silently_decided():
    """⚠ "THE FIRST `Chain`" IS NOT A RULE, and neither is `min` without saying so. Two census
    proteins are cleaved into subunits with different starts — `P51654` and `Q13421` MSLN — and the
    mature N-terminus used here includes a fragment that is cleaved off and secreted. **That is the
    same defect that barred rule B, at the other end of the molecule.**

    ⚠ It is FLAGGED, not decided, because deciding it is a ruling. Prove it bites by dropping the
    flag: the two ambiguous rows become indistinguishable from the eight that agree."""
    r = extract(entry(chain(37, 286), chain(296, 598), lipid(598)))
    assert GUARD_CHAIN_START_AMBIGUOUS in r.guards, r
    agree = extract(entry(chain(25, 200), chain(25, 300), lipid(299)))
    assert GUARD_CHAIN_START_AMBIGUOUS not in agree.guards, (
        "the flag fires where the chain starts agree — it would flag all ten multi-chain proteins "
        "instead of the two that are actually ambiguous")


def test_a_gpi_protein_with_no_chain_is_absent_with_reason_not_dropped():
    """⚠ Missing a required feature is a NAMED CATEGORY, never a silent drop from a denominator.
    Two real proteins are in this state — `P25063` and `P31358`.

    Prove it bites by returning `None` and letting the caller skip the row: the denominator loses
    two rows and nothing says so."""
    r = extract(entry(lipid(300)))
    assert r.span_aa is None
    assert r.category == "absent_with_reason"
    assert r.reason == REASON_GPI_NO_CHAIN, r.reason


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
    r = extract(entry(td("Periplasmic", 43, 251)))
    assert r.category == TERM_UNRULED, r
    assert "Periplasmic" in r.reason
    assert r.terms_unruled == ["Periplasmic"]
    assert classify_term("Periplasmic") == TERM_UNRULED, (
        "the fixture term is in one of the ruled lists, so this test no longer exercises the "
        "unruled path at all — A-017 clause (c)")


def test_the_two_held_terms_are_now_accepted_and_the_held_list_is_empty_not_deleted():
    """⚠ RULED 2026-08-07 after the CSPA check — and the two did NOT get the same answer.

    `Lumenal, melanosome`: 3 of 3 in CSPA category 1 — experimentally surface-detected, which is a
    measurement and not a prediction — with 449-458 aa spans. `Vacuolar`: accepted on **compartment
    biology**, explicitly NOT on its two observed instances. ⚠ Rejecting a compartment on a sample
    of two V-ATPase subunits would be the F-019 error and would bar every future `Vacuolar` protein
    on evidence about V-ATPase. The 64 aa and 74 aa loops sort themselves out downstream, on their
    own merits, which is the system working rather than a gap.

    ⚠ `HELD_TERMS` is EMPTY, not deleted — an empty holding pen is a finding ("it was worked
    through"); a missing one reads as: there was never one."""
    assert classify_term("Vacuolar") == "accepted"
    assert classify_term("Lumenal, melanosome") == "accepted"
    assert HELD_TERMS == frozenset()
    r = extract(entry(td("Vacuolar", 476, 549)))
    assert r.span_aa == 74 and r.rule == RULE_VOCABULARY, r


def test_the_yeast_term_is_ruled_rejected_rather_than_left_unruled_or_deleted():
    """⚠ RULED hypothesis 1: yeast ortholog annotation transfer. `P0DKB6` MPC1L is *Homo sapiens*
    9606, reviewed — the organism check closed the serious branch, so no denominator moves. It is a
    CYTOPLASMIC term, so it is rejected for the same reason `Cytoplasmic` is.

    ⚠ Rejected, NOT deleted: a term that vanishes reads as: nobody thought of it. Prove it bites
    by removing it from `REJECTED_TERMS` — it returns to `term_unruled` and this reds."""
    assert classify_term("Mother cell cytoplasmic") == "rejected"
    r = extract(entry(td("Mitochondrial matrix", 2, 19), td("Mother cell cytoplasmic", 43, 51)))
    assert r.category == NO_EXTRACELLULAR_SPAN, r
    assert r.terms_unruled == []


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


def test_the_divergence_check_is_kept_as_diagnosis_after_the_bar():
    """⚠ A check on the rule, not an input to it. `Q96GW7`'s real shape: `Chain` runs 266 residues
    past the anchor because the C-terminal GPI signal is cleaved and not annotated."""
    e = entry(chain(23, 911), lipid(646))
    assert divergence(e) == (623, 889)
    # ⚠ Rule A's 623 is produced; rule B's 889 is computable as diagnosis and never used.
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


# ── ⚠ the ruled mature-chain selector: the MSLN over-read ────────────────────
def test_the_anchor_selects_the_chain_not_the_lowest_start():
    """⚠⚠ THE MSLN DEFECT, and it was LIVE on the protein F-025 is named after.

    Mesothelin is made as a precursor. The N-terminal MPF fragment is cleaved and **secreted** — it
    is not on the cell. `min(start)` took 37 and produced a 561 aa span carrying ~250 residues an
    antibody will never meet, fused to the ectodomain that matters. **It would have folded, scored,
    banded and looked entirely normal.**

    Prove it bites by restoring `mature_chain_bounds` as the selector: the span becomes 561."""
    e = entry(chain(37, 598), chain(37, 286), chain(296, 598), lipid(598))
    r = extract(e)
    assert r.span_aa != 561, (
        "the mature chain was selected by lowest start — this is the MSLN over-read, and it carries "
        "~250 residues of a secreted fragment into the fold")


def test_msln_shaped_disagreeing_candidates_are_named_and_excluded_never_guessed():
    """⚠ Both `Mesothelin` 37-598 and `Mesothelin, cleaved form` 296-598 terminate at the anchor,
    giving 561 and 302. The owner ruled the ZERO-candidate case; the DISAGREEING case is not ruled,
    so it takes the same named exclusion rather than a guess.

    Prove it bites by adding a tie-break (e.g. latest start): a span appears where a ruling is
    owed, and this reds."""
    r = extract(entry(chain(37, 598), chain(37, 286), chain(296, 598), lipid(598)))
    # ⚠ CORRECTED BY THE SECOND RULING. The candidates containing the anchor are 37-598 and
    # 296-598; the LATEST start wins, landing on the mature cleaved form the ADCs bind.
    assert r.span_aa == 302, f"the mature cleaved form was not selected: {r}"
    assert r.rule == RULE_GPI_A


def test_identical_duplicate_chains_are_not_a_disagreement():
    """⚠ A-017 clause (c) for the selector. `O95971` CD160 carries `CD160 antigen` and
    `CD160 antigen, soluble form`, BOTH 25-159. Two records, one span — not ambiguous.

    Prove it bites by testing `len(candidates) > 1` instead of the number of distinct SPANS:
    CD160 becomes absent_with_reason and a correct protein is lost."""
    r = extract(entry(chain(25, 159), chain(25, 159), lipid(159)))
    assert r.span_aa == 134, f"two identical chains were read as a disagreement: {r}"
    assert r.rule == RULE_GPI_A


def test_the_selector_takes_the_anchored_subunit_of_a_cleaved_protein():
    """⚠ `P51654` GPC3: alpha 25-358, beta 359-554, anchor 554. The anchor sits on the BETA subunit,
    so the mature GPI chain is 359-554 → 195 aa, not 529. The alpha subunit is a separate chain."""
    r = extract(entry(chain(25, 358), chain(359, 554), lipid(554)))
    assert r.span_aa == 195 and r.rule == RULE_GPI_A, r


def test_a_chain_running_past_the_anchor_still_yields_a_span_and_is_flagged_not_excluded():
    """⚠ Flagged, not excluded — the posture the owner set for `P08571`. The C-terminal overrun is
    real and recorded; it is not a reason to lose the protein."""
    # ⚠⚠ THE FIRST SELECTOR EXCLUDED THIS PROTEIN AND IT WAS WRONG TO. P06731 CEACAM5 has ONE
    # chain, 35-685, and an anchor at 676 — a nine-residue end mismatch at a boundary rule A never
    # reads. It was dropped on ANNOTATION FORM rather than on biology, and it is a clinically
    # validated ADC target. Containment is the right test: the anchor sits inside the chain.
    r = extract(entry(chain(35, 685), lipid(676)))
    assert r.span_aa == 641, f"CEACAM5 was excluded on an end mismatch rule A never uses: {r}"
    assert r.rule == RULE_GPI_A


def test_the_chain_start_guard_stays_live_after_the_fix():
    """⚠ The guard is what CAUGHT the MSLN over-read. It stays on the artifact after the fix, so a
    `Chain` set the selector does not explain is still visible rather than silently handled."""
    r = extract(entry(chain(25, 358), chain(359, 554), lipid(554)))
    assert GUARD_CHAIN_START_AMBIGUOUS in r.guards, r


def test_the_shortening_guard_fires_wherever_the_selector_had_a_choice_and_carries_the_ratio():
    """⚠ THRESHOLD-FREE BY MEASUREMENT, not by preference. Across all 128 GPI-anchored census
    proteins, 127 have a single candidate start and exactly one differs — MSLN at 0.538. **There is
    nothing to calibrate a constant against**, so any threshold would be a dial wearing the costume
    of a measurement, and it could only ever SUPPRESS flags.

    Prove it bites by adding `if ratio < 0.5` — MSLN stops being flagged, and the one protein where
    a choice was actually made becomes indistinguishable from the 127 where none was."""
    r = extract(entry(chain(37, 598), chain(37, 286), chain(296, 598), lipid(598)))
    flags = [g for g in r.guards if g.startswith("chain_shorter_than_longest_candidate")]
    assert flags, f"the selector chose between candidates without flagging it: {r.guards}"
    assert flags[0].endswith(":0.538"), flags


def test_the_shortening_guard_stays_silent_where_there_was_no_choice():
    """⚠ A-017 clause (c). A guard that fires on every GPI protein flags nothing."""
    r = extract(entry(chain(37, 598), lipid(598)))
    assert not [g for g in r.guards if g.startswith("chain_shorter_than_longest_candidate")], r


def test_a_gpi_protein_with_no_chain_at_all_is_still_named_and_excluded():
    """⚠ P25063 and P31358 carry a GPI anchor and NO `Chain` feature. They stay out — but now on
    annotation absence rather than on an over-strict selector, which is the distinction that
    matters: it is a fact about the record, not about our rule."""
    r = extract(entry(lipid(59)))
    assert r.span_aa is None and r.reason == "gpi_chain_unannotated"
