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


def test_the_ingest_payload_supplies_every_key_claim_subscripts():
    """⚠⚠ THE GUARD. Prove it bites by deleting `model_revision` from the ingest payload — the
    exact defect that stranded ten jobs — and this names the missing key."""
    import scripts.census_ingest as ing
    row = next(r for r in ing.manifest_rows(1))
    payload = ing.build_row(row)
    s_keys, meta_keys = _keys_read_by_build_fold_spec()
    missing_s = s_keys - set(payload["inference_settings"])
    missing_meta = meta_keys - set(payload["meta"])
    assert not missing_s, (
        f"inference_settings is missing {sorted(missing_s)} — /claim would raise KeyError AFTER "
        f"marking the job claimed, stranding it with attempts=0 and no error")
    assert not missing_meta, f"meta is missing {sorted(missing_meta)}"


def test_a_payload_missing_model_revision_is_refused_before_any_write():
    """⚠ The refusal itself, not just the key check — `assert_claimable` must RAISE, because the
    dry run's job is to fail here rather than let the route fail after a write."""
    import scripts.census_ingest as ing
    payload = ing.build_row(next(r for r in ing.manifest_rows(1)))
    del payload["inference_settings"]["model_revision"]
    with pytest.raises(SystemExit, match="stranding it"):
        ing.assert_claimable(payload)


def test_a_payload_with_an_unresolvable_tier_is_refused():
    """⚠ D-047: `/claim` raises when `meta['tier']` resolves no recipe. Same failure shape — after
    the claim — so the ingest must refuse first."""
    import scripts.census_ingest as ing
    payload = ing.build_row(next(r for r in ing.manifest_rows(1)))
    payload["meta"]["tier"] = "gpu-go-brrr"
    with pytest.raises(SystemExit, match="resolves no recipe"):
        ing.assert_claimable(payload)


def test_a_valid_payload_builds_a_foldspec_with_the_recipe_from_the_tier_table():
    """⚠ A-017 clause (c) control: without this, the refusals above would pass under an
    implementation that refuses everything.

    ⚠ And it pins D-047: dtype/chunk_size come from TIER_RECIPE, NOT from inference_settings —
    which deliberately does not carry them."""
    import scripts.census_ingest as ing
    from core.contracts import TIER_RECIPE
    payload = ing.build_row(next(r for r in ing.manifest_rows(1)))
    spec = ing.assert_claimable(payload)
    assert spec.dtype == TIER_RECIPE["local"]["dtype"]
    assert spec.chunk_size == TIER_RECIPE["local"]["chunk_size"]
    assert "dtype" not in payload["inference_settings"]
    assert "chunk_size" not in payload["inference_settings"]
    assert len(spec.sequence) == payload["meta"]["span_aa"]
