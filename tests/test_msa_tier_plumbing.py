"""D-107 amendment 1 — `msa` is a claimable `jobs.tier`; `TIER_RECIPE` stays ESMFold-only.

Four ATs that must be able to go red (UnlockedFakeJobQueue / SQLite; no live Postgres job):

1. rental claim returns the rental job only, when an msa job is also pending
2. msa claim returns the msa job only, when a rental job is also pending
3. `build_fold_spec` for an msa job raises — it does not return an ESMFold FoldSpec
4. local/rental `TIER_RECIPE` is unchanged (`msa` is not a key)
"""

from __future__ import annotations

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.artifacts import build_fold_spec
from core.contracts import KNOWN_TIERS, TIER_RECIPE
from core.enqueue import FetchedSequence, enqueue_cohort
from core.manifest import ManifestRow
from core.queue import PENDING
from db.models import Base, JobRecord, ProteinAnalysis
from doubles import UnlockedFakeJobQueue

REV = "75a3841ee059df2bf4d56688166c8fb459ddd97a"


def _settings():
    return {"model_revision": REV, "dtype": "fp16", "chunk_size": 64,
            "source": "whole", "ecd_start": None, "ecd_end": None}


def _seed_rental_and_msa():
    """The same seed both cross-claim ATs use."""
    q = UnlockedFakeJobQueue()
    rental_id = q.enqueue(1, tier="rental")
    msa_id = q.enqueue(2, tier="msa")
    return q, rental_id, msa_id


def test_rental_claim_returns_the_rental_job_only_when_msa_is_also_pending():
    """AT 1. A rental-tier worker cannot take an msa pending job."""
    q, rental_id, msa_id = _seed_rental_and_msa()
    claimed = q.claim("rental-box", tier="rental")
    assert claimed is not None
    assert claimed.id == rental_id
    assert claimed.tier == "rental"
    assert q.get(msa_id).status == PENDING


def test_msa_claim_returns_the_msa_job_only_when_rental_is_also_pending():
    """AT 2. An msa-tier worker cannot take a rental pending job."""
    q, rental_id, msa_id = _seed_rental_and_msa()
    claimed = q.claim("msa-box", tier="msa")
    assert claimed is not None
    assert claimed.id == msa_id
    assert claimed.tier == "msa"
    assert q.get(rental_id).status == PENDING


def test_build_fold_spec_for_an_msa_job_raises_not_an_esmfold_foldspec():
    """AT 3. Same shape as D-047 unknown-tier: ValueError, not a silent ESMFold FoldSpec."""
    eng = create_engine("sqlite://")
    Base.metadata.create_all(eng)
    with Session(eng) as s:
        a = ProteinAnalysis(
            input_type="uniprot", input_value="P00000",
            meta={"sequence": "MKT", "tier": "msa", "source": "whole"},
        )
        s.add(a)
        s.flush()
        analysis_id = a.id
        s.commit()
    queue = UnlockedFakeJobQueue()
    queue.enqueue(analysis_id, inference_settings=_settings(), tier="msa")
    with pytest.raises(ValueError, match="msa"):
        build_fold_spec(queue, eng, "w1", tier="msa")


def test_local_and_rental_tier_recipe_unchanged():
    """AT 4. `msa` must not resolve to fp16/chunk-64 by living in TIER_RECIPE."""
    assert TIER_RECIPE == {
        "local": {"dtype": "int8", "chunk_size": 64},
        "rental": {"dtype": "fp16", "chunk_size": 64},
    }
    assert "msa" not in TIER_RECIPE
    assert KNOWN_TIERS == frozenset({"local", "rental", "msa"})


def _fake_fetch(accession: str) -> FetchedSequence:
    return FetchedSequence(sequence="A" * 2500, uniprot_release="2024_06")


def _msa_row(**kw) -> ManifestRow:
    fields = dict(
        accession="P00000", gene="MSA1", label="msa-plumbing",
        boundary_method="whole", span=None, ecd_start=None, ecd_end=None,
        tier="msa", tier_reason="d107-plumbing",
        held_out=False, excluded=False, exclusion_reason=None, primary_match=False,
    )
    fields.update(kw)
    return ManifestRow(**fields)


def test_enqueue_accepts_msa_without_stamping_an_esmfold_recipe():
    """Known-tier list includes msa so enqueue does not KeyError or copy rental's recipe."""
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with Session(engine) as s:
        enqueue_cohort(s, [_msa_row()], _fake_fetch)
        a = s.execute(select(ProteinAnalysis)).scalar_one()
        job = s.execute(select(JobRecord)).scalar_one()
        assert a.meta["tier"] == "msa"
        assert job.tier == "msa"
        assert "dtype" not in job.inference_settings
        assert "chunk_size" not in job.inference_settings


def test_enqueue_refuses_an_unknown_tier():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with Session(engine) as s:
        with pytest.raises(ValueError, match="unknown tier"):
            enqueue_cohort(s, [_msa_row(tier="galaxy-brain")], _fake_fetch)
