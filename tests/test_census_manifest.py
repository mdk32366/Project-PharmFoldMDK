"""The census manifest: the seed, and the fact that a band routes rather than excludes.

⚠ **A SEED CHOSEN AFTER SEEING THE ORDER IS NOT A SEED, IT IS A SELECTION.** The whole value of a
recorded seed is that it was fixed before anyone could see what it produced — so the assertion is
not *"a seed is reported"* but *"the seed reached disk before `shuffle` was called."*

⚠ **AND A BAND MUST NOT DECIDE WHETHER A TARGET FOLDS.** `above_local` is a routing fact: it sends a
protein to the rented GPU. A manifest that dropped those rows would report a foldable population it
had quietly shrunk, which is F-009's shape with a new column name.
"""

from __future__ import annotations

import csv
import json

import pytest

from core.manifest import LOCAL_CEILING
from core.span_definition import V2_RULED_VOCABULARY
from scripts.census_manifest import band_of, run


@pytest.fixture()
def built(tmp_path):
    out = tmp_path / "m.csv"
    assert run(["--seed", "4242", "--class", "surface", "--out", str(out)]) == 0
    rows = list(csv.DictReader(out.open(encoding="utf-8", newline="")))
    prov = json.loads((tmp_path / "m.provenance.json").read_text(encoding="utf-8"))
    return rows, prov, out


# ── the seed ────────────────────────────────────────────────────────────────
def test_the_seed_reaches_disk_before_the_shuffle_runs(tmp_path, monkeypatch):
    """⚠⚠ THE ASSERTION THAT MATTERS, and it is about ORDER OF OPERATIONS, not about a field being
    present. The provenance file is read at the moment `shuffle` is called: the seed must already
    be in it, and `shuffled` must still be false.

    Prove it bites by moving the provenance write to after the shuffle — the file does not exist
    when `shuffle` runs and this reds there, not on a missing key at the end."""
    import scripts.census_manifest as m
    out = tmp_path / "m.csv"
    prov_at_shuffle = {}

    real = m.random.Random

    class Spy(real):                       # type: ignore[misc,valid-type]
        def shuffle(self, seq):            # noqa: D102
            p = out.parent / "m.provenance.json"
            prov_at_shuffle["exists"] = p.exists()
            if p.exists():
                prov_at_shuffle.update(json.loads(p.read_text(encoding="utf-8")))
            return real.shuffle(self, seq)

    monkeypatch.setattr(m.random, "Random", Spy)
    assert m.run(["--seed", "99", "--class", "surface", "--out", str(out)]) == 0

    assert prov_at_shuffle.get("exists") is True, (
        "the provenance file did not exist when shuffle() was called — the seed was recorded "
        "AFTER the order was produced, which is a seed nobody committed to in advance")
    assert prov_at_shuffle["seed"] == 99
    assert prov_at_shuffle["shuffled"] is False


def test_the_same_seed_reproduces_the_same_fold_order(tmp_path):
    """⚠ A fold order that cannot be reproduced from its seed is a fold order somebody chose."""
    import scripts.census_manifest as m
    a, b = tmp_path / "a.csv", tmp_path / "b.csv"
    m.run(["--seed", "7", "--class", "surface", "--out", str(a)])
    m.run(["--seed", "7", "--class", "surface", "--out", str(b)])
    assert a.read_text(encoding="utf-8") == b.read_text(encoding="utf-8")


def test_a_different_seed_produces_a_different_order(tmp_path):
    """⚠ A-017 clause (c): without this, an implementation that ignored the seed entirely would
    pass the reproducibility test above perfectly."""
    import scripts.census_manifest as m
    a, b = tmp_path / "a.csv", tmp_path / "b.csv"
    m.run(["--seed", "7", "--class", "surface", "--out", str(a)])
    m.run(["--seed", "8", "--class", "surface", "--out", str(b)])
    assert a.read_text(encoding="utf-8") != b.read_text(encoding="utf-8"), (
        "two different seeds produced identical fold orders — the seed is not reaching shuffle")


def test_there_is_no_default_seed(tmp_path):
    """⚠ A default seed is a seed nobody chose and everybody inherits, and it would make
    "recorded before the shuffle" vacuously true."""
    import scripts.census_manifest as m
    with pytest.raises(SystemExit):
        m.run(["--class", "surface", "--out", str(tmp_path / "x.csv")])


# ── bands route, they do not exclude ────────────────────────────────────────
def test_every_band_including_above_local_is_present_in_the_manifest(built):
    """⚠ BANDS CHOOSE THE TIER, NEVER WHETHER A TARGET FOLDS. Prove it bites by filtering
    `above_local` out of the manifest: the band vanishes and this reds naming it."""
    rows, _, _ = built
    bands = {r["band"] for r in rows}
    assert "above_local" in bands, (
        "the above_local band is absent from the manifest — a routing fact was used as an "
        "exclusion, and the foldable population was silently shrunk")
    assert "local" in bands and "untested_band" in bands


def test_the_fixture_actually_contains_above_local_rows(built):
    """⚠ A-017 clause (c). With no over-ceiling protein the assertion above passes under an
    implementation that drops them."""
    rows, _, _ = built
    assert sum(1 for r in rows if r["band"] == "above_local") > 0


def test_above_local_routes_to_rental_rather_than_being_dropped(built):
    rows, _, _ = built
    for r in rows:
        if r["band"] == "above_local":
            assert r["tier"] == "rental", r
            assert r["tier_reason"], "a rental routing carries no reason"


def test_the_untested_band_is_its_own_band_and_is_not_folded_into_local(built):
    """⚠ (440, 630) is UNMEASURED. Calling it local would guess a host crash; calling it
    above_local would guess a needless rental. It is neither, and it says so."""
    rows, _, _ = built
    for r in rows:
        span = int(r["span_aa"])
        if LOCAL_CEILING.known_good < span < LOCAL_CEILING.known_bad:
            assert r["band"] == "untested_band", r


def test_bands_sum_to_the_manifest_and_lose_no_rows(built):
    rows, prov, _ = built
    assert sum(prov["bands"].values()) == len(rows) == prov["manifest_rows"]


# ── provenance ──────────────────────────────────────────────────────────────
def test_the_span_definition_is_named_on_every_row_and_in_the_provenance(built):
    """⚠ D-081. A span whose definition is unknown is a span whose meaning is unknown, and a
    foldable count under V2 is not comparable to one under V1 unless both are named."""
    rows, prov, _ = built
    assert prov["span_definition"] == V2_RULED_VOCABULARY
    assert {r["span_definition"] for r in rows} == {V2_RULED_VOCABULARY}
    assert "v1-extracellular-substring-2026-07-21" in prov["span_definition_note"]


def test_the_attention_tilt_limitation_travels_with_the_manifest(built):
    """⚠ Not a correction, and nothing is adjusted for it — but a fold order drawn from a
    population with a known tilt should say so where the order is, not three documents away."""
    _, prov, _ = built
    t = prov["attention_tilt_limitation"]
    assert "-0.142" in t and "+0.120" in t
    assert "Nothing is adjusted for it" in t


def test_the_source_is_identified_by_hash_not_by_filename(built):
    """⚠ A filename is not an identity."""
    _, prov, _ = built
    meta = prov["classes"]["surface"]
    assert len(meta["source_sha256"]) == 64
    assert meta["foldable"] < meta["source_rows"]


def test_the_not_foldable_rows_are_counted_by_reason_never_just_dropped(built):
    """⚠ An absence is a category with a cause. `source_rows` must reconcile."""
    _, prov, _ = built
    meta = prov["classes"]["surface"]
    assert meta["foldable"] + sum(meta["not_foldable_by_reason"].values()) == meta["source_rows"]
    assert "span_boundary_unknown" in meta["not_foldable_by_reason"]


def test_the_ceiling_recipe_is_a_triple_not_a_bare_integer(built):
    """⚠ D-077 dec 3. A band split read under a recipe it was not measured under is a different
    measurement wearing the same name."""
    _, prov, _ = built
    r = prov["ceiling_recipe"]
    for k in ("dtype", "chunk_size", "known_good", "known_bad", "hardware"):
        assert r[k] not in (None, ""), k


def test_band_of_refuses_to_call_a_missing_span_foldable():
    assert band_of(None) == "not_foldable"
    assert band_of(LOCAL_CEILING.known_good) == "local"
    assert band_of(LOCAL_CEILING.known_bad) == "above_local"


# ── ⚠ two identities, and neither may stand for the other ───────────────────
def _mrow(acc, start, end, band="local", tier="local", rule="vocabulary", defn="v2"):
    return {"census_accession": acc, "span_start": start, "span_end": end, "band": band,
            "tier": tier, "span_rule": rule, "span_definition": defn}


def test_changing_exactly_one_span_moves_the_content_hash_and_not_the_fold_order():
    """⚠⚠ THE DISCRIMINATING TEST, and a membership-only check passes under the defect.

    Revisions 1 and 3 had identical membership (3,468) and an identical fold order — 3,468 of
    3,468 — while `P51654` went 529→195 and `Q13421` went 561→302. **An unchanged fold order is
    not evidence of an unchanged manifest.**

    Prove it bites by defining `manifest_content_hash` over accessions only — exactly the
    membership-only identity that hid the change — and the content assertion reds."""
    from scripts.census_manifest import fold_order_key, manifest_content_hash
    before = [_mrow("A", 1, 100), _mrow("B", 200, 400)]
    after = [_mrow("A", 1, 100), _mrow("B", 200, 300)]      # ⚠ exactly one span changed

    assert fold_order_key(before) == fold_order_key(after), (
        "the fold order key moved when only a SPAN changed — fold orders must stay reproducible "
        "across span revisions, which is the whole reason it is keyed on membership")
    assert manifest_content_hash(before) != manifest_content_hash(after), (
        "the content hash did NOT move when a span changed — this is the r1-vs-r3 defect: a "
        "manifest whose contents differ reporting the same identity")


def test_the_fixture_actually_changes_exactly_one_span():
    """⚠ A-017 clause (c). With no changed span, both assertions above pass trivially."""
    before = [_mrow("A", 1, 100), _mrow("B", 200, 400)]
    after = [_mrow("A", 1, 100), _mrow("B", 200, 300)]
    diff = [(x, y) for x, y in zip(before, after) if x != y]
    assert len(diff) == 1 and diff[0][0]["span_end"] != diff[0][1]["span_end"]


def test_a_membership_change_moves_both():
    """⚠ The converse control: adding a protein must move BOTH, or the fold-order key would be
    stable against the one thing it is supposed to track."""
    from scripts.census_manifest import fold_order_key, manifest_content_hash
    before = [_mrow("A", 1, 100)]
    after = [_mrow("A", 1, 100), _mrow("B", 5, 50)]
    assert fold_order_key(before) != fold_order_key(after)
    assert manifest_content_hash(before) != manifest_content_hash(after)


def test_the_content_hash_covers_the_band_tier_rule_and_definition_not_only_coordinates():
    """⚠ A band or tier moving is a routing change; a rule or definition moving is a meaning
    change. Both must move the identity."""
    from scripts.census_manifest import manifest_content_hash as h
    base = [_mrow("A", 1, 100)]
    assert h(base) != h([_mrow("A", 1, 100, band="above_local")])
    assert h(base) != h([_mrow("A", 1, 100, tier="rental")])
    assert h(base) != h([_mrow("A", 1, 100, rule="gpi_rule_A")])
    assert h(base) != h([_mrow("A", 1, 100, defn="v1")])


def test_both_identities_are_emitted_and_labelled_distinctly(built):
    """⚠ One number standing for both is the defect this exists to prevent."""
    _, prov, _ = built
    assert prov["fold_order_key"] != prov["manifest_content_hash"]
    assert "membership" in prov["fold_order_key_covers"].lower()
    assert "span_start" in prov["manifest_content_hash_covers"]


def test_a_span_without_coordinates_is_refused_outright():
    """⚠ A LENGTH CANNOT SLICE A SEQUENCE. The census manifest carried only `span_aa` until now,
    so nothing downstream could have cut anything from it. Prove it bites by dropping the check."""
    from core.span_extract import SpanResult
    with pytest.raises(ValueError, match="cannot be sliced"):
        SpanResult(span_aa=100, rule="vocabulary")
    with pytest.raises(ValueError, match="do not reconcile"):
        SpanResult(span_aa=100, span_start=1, span_end=50, rule="vocabulary")


# ── ⚠ D-083: a tranche is a PARTITION, not an ordering ──────────────────────
def test_the_tranche_bands_are_exhaustive_and_mutually_exclusive(built):
    """⚠ Every foldable row lands in exactly one tranche, and they sum to the declared total.
    Prove it bites by overlapping two bands or leaving a gap between them."""
    from scripts.census_manifest import tranche_for_span
    rows, prov, _ = built
    assert sum(prov["tranches"].values()) == len(rows) == prov["manifest_rows"]
    for r in rows:
        assert int(r["tranche"]) == tranche_for_span(int(r["span_aa"]))


def test_a_span_outside_every_band_raises_rather_than_defaulting():
    """⚠ An unbanded row would fold under a tranche label nobody assigned it."""
    from scripts.census_manifest import tranche_for_span
    with pytest.raises(ValueError, match="refusing to guess"):
        tranche_for_span(0)


def test_the_bands_ascend_and_tranche_one_is_the_smallest(built):
    """⚠⚠ THE BOUNDARIES ARE CHOSEN FOR RISK, NOT BALANCE. D-082 leaves the crank uncapped with
    layer 2 off and layer 1 never observed to fire, so a memory problem must surface on a 40 aa
    fold rather than a 430 aa one.

    Prove it bites by reordering the bands descending: tranche 1 becomes the most expensive batch
    and the derisking is inverted."""
    from scripts.census_manifest import TRANCHE_BANDS
    los = [lo for _, lo, _ in TRANCHE_BANDS]
    assert los == sorted(los), "the tranche bands do not ascend"
    rows, _, _ = built
    by_t = {}
    for r in rows:
        by_t.setdefault(int(r["tranche"]), []).append(int(r["span_aa"]))
    for t in sorted(by_t)[:-1]:
        assert max(by_t[t]) < min(by_t[t + 1]), f"tranche {t} overlaps tranche {t+1}"


def test_no_census_row_is_ever_labelled_tranche_zero(built):
    """⚠⚠ TRANCHE 0 IS THE 82-TARGET COHORT. A census row carrying it would appear on the
    tranche-zero surface the app serves — a named stop condition.

    Prove it bites by starting TRANCHE_BANDS at 0."""
    rows, _, _ = built
    assert not [r for r in rows if int(r["tranche"]) == 0]


def test_the_seed_still_governs_inside_each_tranche(built):
    """⚠⚠ THE RECONCILIATION, AND IT IS THE WHOLE POINT OF D-083. Batching touches the PARTITION;
    the seeded order is untouched. Within a tranche, fold_order must still be the shuffled order —
    NOT sorted by span, which is what "smallest first" would mean if taken naively.

    Prove it bites by sorting rows by span_aa before assigning fold_order: within a tranche the
    order becomes monotone in span and this reds."""
    rows, _, _ = built
    t1 = [r for r in rows if int(r["tranche"]) == 1]
    t1.sort(key=lambda r: int(r["fold_order"]))
    spans = [int(r["span_aa"]) for r in t1]
    assert spans != sorted(spans), (
        "within tranche 1 the fold order is monotone in span — the seeded order was replaced by a "
        "size sort, which is choosing the order the seed exists to avoid choosing")


def test_the_tranche_is_derived_from_the_span_so_it_is_not_in_the_content_hash(built):
    """⚠ `tranche` is a PURE FUNCTION of `span_aa`, and `span_start`/`span_end` are already in
    CONTENT_FIELDS — so hashing it would add nothing a span change does not already move. Stated
    rather than left as an apparent oversight: r6 and r7 hash identically ON PURPOSE.

    Prove it bites by making the tranche depend on anything other than the span."""
    from scripts.census_manifest import CONTENT_FIELDS, tranche_for_span
    rows, _, _ = built
    assert "tranche" not in CONTENT_FIELDS
    assert all(int(r["tranche"]) == tranche_for_span(int(r["span_aa"])) for r in rows)
