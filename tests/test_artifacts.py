"""D-047 — the fold recipe is resolved at fold-time, not frozen at enqueue.

`build_fold_spec` (app/artifacts.py) is the one authoritative site: it resolves
`dtype`/`chunk_size` from the current `TIER_RECIPE[tier]`, NOT from the job's stored
`inference_settings`. These tests pin that — including the exact bug the 2026-07-24 rerun
hit, where a requeue replayed a pre-D-042 frozen `chunk_size=None` and re-OOM'd unchunked.

build_fold_spec's inputs, faked at the seam: a queue whose `claim()` yields a `Job` (with a
stored `inference_settings`), and a real SQLite engine holding the analysis whose `meta`
carries the `tier` and the folded `sequence`.
"""

from __future__ import annotations

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.artifacts import build_fold_spec
from core.contracts import TIER_RECIPE
from db.models import Base, ProteinAnalysis
from doubles import UnlockedFakeJobQueue

REV = "75a3841ee059df2bf4d56688166c8fb459ddd97a"


def _queue_and_engine(*, tier, stored_settings, sequence="MKT"):
    """A fake queue holding one claimable job + a real engine holding its analysis.
    ``meta`` carries the tier (recipe key) and the folded sequence, as enqueue writes it."""
    eng = create_engine("sqlite://")
    Base.metadata.create_all(eng)
    meta = {"sequence": sequence, "source": stored_settings.get("source", "whole")}
    if tier is not None:
        meta["tier"] = tier
    with Session(eng) as s:
        a = ProteinAnalysis(input_type="uniprot", input_value="P00000", meta=meta)
        s.add(a)
        s.flush()
        analysis_id = a.id
        s.commit()
    queue = UnlockedFakeJobQueue()
    queue.enqueue(analysis_id, inference_settings=stored_settings)
    return queue, eng


def _stale_rental_settings():
    """What a pre-D-042 rental job froze: chunk_size=None (unchunked) — the recipe that OOM'd."""
    return {"model_revision": REV, "dtype": "fp16", "chunk_size": None,
            "source": "whole", "ecd_start": None, "ecd_end": None}


# ── THE regression that names 2026-07-24 (red before the fix, green after) ─────

def test_fold_time_recipe_overrides_stale_stored_chunk_size():
    # A rental job whose FROZEN inference_settings says chunk_size=None (the pre-D-042 recipe
    # that re-OOM'd on requeue) must fold at the CURRENT rental recipe's chunk_size=64.
    queue, eng = _queue_and_engine(tier="rental", stored_settings=_stale_rental_settings())
    spec = build_fold_spec(queue, eng, "w1")
    assert spec.chunk_size == 64, "fold-time recipe must win over the stale stored None (D-047)"
    assert spec.chunk_size == TIER_RECIPE["rental"]["chunk_size"]
    assert spec.dtype == TIER_RECIPE["rental"]["dtype"]


# ── each tier resolves its current recipe, regardless of what was stored ───────

def test_rental_tier_resolves_current_rental_recipe():
    queue, eng = _queue_and_engine(tier="rental", stored_settings=_stale_rental_settings())
    spec = build_fold_spec(queue, eng, "w1")
    assert (spec.dtype, spec.chunk_size) == ("fp16", 64)


def test_local_tier_resolves_current_local_recipe():
    # Even if the stored hint disagreed, local resolves to int8/64.
    stored = {"model_revision": REV, "dtype": "fp16", "chunk_size": None,
              "source": "sliced_ecd", "ecd_start": 20, "ecd_end": 69}
    queue, eng = _queue_and_engine(tier="local", stored_settings=stored)
    spec = build_fold_spec(queue, eng, "w1")
    assert (spec.dtype, spec.chunk_size) == ("int8", 64)


# ── a job with no/unknown tier fails LOUD, never a silent None default ─────────

def test_unknown_tier_raises_not_silently_defaults():
    queue, eng = _queue_and_engine(tier="galaxy-brain", stored_settings=_stale_rental_settings())
    with pytest.raises(ValueError, match="tier"):
        build_fold_spec(queue, eng, "w1")


def test_missing_tier_raises():
    queue, eng = _queue_and_engine(tier=None, stored_settings=_stale_rental_settings())
    with pytest.raises(ValueError, match="tier"):
        build_fold_spec(queue, eng, "w1")


# ── the non-recipe fields stay authoritative from inference_settings ───────────

def test_slicing_identity_still_comes_from_inference_settings():
    # D-047 moves ONLY dtype/chunk_size to fold-time; model_revision + source + ECD bounds are
    # the target's slicing identity and remain authoritative from the stored settings.
    stored = {"model_revision": REV, "dtype": "int8", "chunk_size": 64,
              "source": "sliced_ecd", "ecd_start": 20, "ecd_end": 69}
    queue, eng = _queue_and_engine(tier="local", stored_settings=stored, sequence="MKTAYIAK")
    spec = build_fold_spec(queue, eng, "w1")
    assert spec.model_revision == REV
    assert spec.source == "sliced_ecd"
    assert (spec.ecd_start, spec.ecd_end) == (20, 69)
    assert spec.sequence == "MKTAYIAK"


# ── empty queue still returns None (unchanged) ─────────────────────────────────

def test_empty_queue_returns_none():
    eng = create_engine("sqlite://")
    Base.metadata.create_all(eng)
    assert build_fold_spec(UnlockedFakeJobQueue(), eng, "w1") is None
