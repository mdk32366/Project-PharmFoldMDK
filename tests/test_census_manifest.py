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
