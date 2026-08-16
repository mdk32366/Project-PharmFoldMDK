"""⚠⚠ The ingest must satisfy the contract `/claim` enforces — checked BEFORE any row is written.

**Why this file exists, and it cost ten stranded jobs:** the first tranche-1 ingest wrote
`inference_settings` without `model_revision`. The dry run passed — it validated slices, spans and
DB invariants, **but never called the consumer it was writing for.** `/claim` then raised
`KeyError('model_revision')` **after** marking each job `claimed`, so ten jobs became permanently
stuck: `attempts=0`, no error recorded, nothing retryable.

⚠ **A failure that leaves no trace in the row is worse than one that fails loudly**, and at 1,307
rows it would have been 1,307 silently stuck jobs.
"""

from __future__ import annotations

import pathlib
import re

import pytest

REPO = pathlib.Path(__file__).resolve().parent.parent


# ⚠⚠ THE SPANCACHE IS GITIGNORED (`.gitignore:234`) — 5,009 UniProt entries, deliberately not in
# the repo. The first version of this file called `ing.manifest_rows(1)` and let `build_row` read
# the real cache, so **it passed only on the author's machine and turned CI red on every run**:
# `SystemExit: no cache entry for P51677`. A test that depends on an artifact not in the repo is a
# test only one person can run, and a green local gate that CI cannot reproduce is not a gate.
#
# ⚠ The fix is a SYNTHETIC row, not a skip. What is under test is the CLAIM CONTRACT — which keys
# the payload must carry — and that needs no real UniProt entry. Skipping would have left the
# ten-stranded-jobs regression unguarded everywhere except one laptop.
@pytest.fixture
def census_row(monkeypatch):
    """One manifest row + its sequence, entirely in-memory. ⚠ No cache, no network, no DB."""
    import scripts.census_ingest as ing
    row = {
        "census_accession": "TEST0001", "tranche": "1", "tier": "local",
        "span_aa": "12", "span_start": "5", "span_end": "16",
        "boundary_method": "sliced_ecd", "census_class": "surface", "band": "local",
        "tier_reason": "", "span_rule": "vocabulary", "guards": "", "fold_order": "1",
        "span_definition": "v2-ruled-vocabulary-2026-08-07",
    }
    # ⚠ 20 residues so the 5..16 slice is real; the slice check must still be exercised.
    monkeypatch.setattr(ing, "sequence_from_cache", lambda acc: "MKTAYIAKQRQISFVKSHF")
    return row


def _keys_read_by_build_fold_spec() -> tuple[set[str], set[str]]:
    """The `s[...]` and `meta[...]` keys `app/artifacts.py:build_fold_spec` actually subscripts.

    ⚠ Read from the SOURCE, not from a list someone maintains alongside it — a hand-kept list is
    the thing that drifts, and this whole file exists because two shapes drifted apart.
    """
    src = (REPO / "app" / "artifacts.py").read_text(encoding="utf-8")
    start = src.index("def build_fold_spec")
    body = src[start: src.index("\ndef ", start + 10)]
    return (set(re.findall(r"\bs\[\"(\w+)\"\]", body)),
            set(re.findall(r"\bmeta\[\"(\w+)\"\]", body)))


def test_the_scan_finds_the_keys_rather_than_passing_on_an_empty_set():
    """⚠ A-017 clause (a). An empty set is a subset of everything — a scan that matches nothing
    would make every assertion below pass while guarding nothing."""
    s_keys, meta_keys = _keys_read_by_build_fold_spec()
    assert "model_revision" in s_keys, s_keys
    assert s_keys >= {"model_revision", "source", "ecd_start", "ecd_end"}, s_keys
    assert "sequence" in meta_keys, meta_keys


def test_the_ingest_payload_supplies_every_key_claim_subscripts(census_row):
    """⚠⚠ THE GUARD. Prove it bites by deleting `model_revision` from the ingest payload — the
    exact defect that stranded ten jobs — and this names the missing key."""
    import scripts.census_ingest as ing
    row = census_row
    payload = ing.build_row(row)
    s_keys, meta_keys = _keys_read_by_build_fold_spec()
    missing_s = s_keys - set(payload["inference_settings"])
    missing_meta = meta_keys - set(payload["meta"])
    assert not missing_s, (
        f"inference_settings is missing {sorted(missing_s)} — /claim would raise KeyError AFTER "
        f"marking the job claimed, stranding it with attempts=0 and no error")
    assert not missing_meta, f"meta is missing {sorted(missing_meta)}"


def test_a_payload_missing_model_revision_is_refused_before_any_write(census_row):
    """⚠ The refusal itself, not just the key check — `assert_claimable` must RAISE, because the
    dry run's job is to fail here rather than let the route fail after a write."""
    import scripts.census_ingest as ing
    payload = ing.build_row(census_row)
    del payload["inference_settings"]["model_revision"]
    with pytest.raises(SystemExit, match="stranding it"):
        ing.assert_claimable(payload)


def test_a_payload_with_an_unresolvable_tier_is_refused(census_row):
    """⚠ D-047: `/claim` raises when `meta['tier']` resolves no recipe. Same failure shape — after
    the claim — so the ingest must refuse first."""
    import scripts.census_ingest as ing
    payload = ing.build_row(census_row)
    payload["meta"]["tier"] = "gpu-go-brrr"
    with pytest.raises(SystemExit, match="resolves no recipe"):
        ing.assert_claimable(payload)


def test_a_valid_payload_builds_a_foldspec_with_the_recipe_from_the_tier_table(census_row):
    """⚠ A-017 clause (c) control: without this, the refusals above would pass under an
    implementation that refuses everything.

    ⚠ And it pins D-047: dtype/chunk_size come from TIER_RECIPE, NOT from inference_settings —
    which deliberately does not carry them."""
    import scripts.census_ingest as ing
    from core.contracts import TIER_RECIPE
    payload = ing.build_row(census_row)
    spec = ing.assert_claimable(payload)
    assert spec.dtype == TIER_RECIPE["local"]["dtype"]
    assert spec.chunk_size == TIER_RECIPE["local"]["chunk_size"]
    assert "dtype" not in payload["inference_settings"]
    assert "chunk_size" not in payload["inference_settings"]
    assert len(spec.sequence) == payload["meta"]["span_aa"]
