"""D-082 — the guard refuses rather than attempts, and never reports safety it cannot see.

⚠⚠ **THE PREMISE.** On 2026-08-16 an over-VRAM fp16 fold bugchecked the host: there was no process
left to catch anything. **Any assertion here that a failure is "caught" would be testing the wrong
property.** What is tested is that the fold is REFUSED BEFORE the allocation.
"""

from __future__ import annotations

import pytest

from core.vram_guard import (
    DEFAULT_MARGIN_MIB, FIT, HOST_DOWN, REFUSED_INSUFFICIENT_HEADROOM, REFUSED_NO_MEASUREMENT,
    Preflight, apply_allocator_cap, infer_host_down, preflight, sysmem_fallback_state,
)


def _pf(**kw):
    """Preflight with CUDA reads stubbed, so the decision logic is tested without a GPU."""
    import core.vram_guard as g
    return kw


# ── ⚠ the refusal, which is the whole point ─────────────────────────────────
def test_a_length_with_no_measured_requirement_is_refused_not_attempted(monkeypatch):
    """⚠⚠ AN ABSENT MEASUREMENT IS A CATEGORY, NOT A GREEN LIGHT. Guessing a requirement is how a
    host gets rebooted — the failure is a bugcheck, not an exception.

    Prove it bites by defaulting `requirement_mib` to 0 or to a guess: the outcome becomes `fits`
    and an unmeasured length is folded."""
    import core.vram_guard as g
    monkeypatch.setattr(g, "cuda_memory", lambda: (7000, 8150))
    monkeypatch.setattr(g, "apply_allocator_cap", lambda f: {"applied": False})
    r = g.preflight(416, "int8", 64, requirement_mib=None)
    assert r.outcome == REFUSED_NO_MEASUREMENT
    assert r.may_fold is False
    assert "not a green light" in r.detail


def test_unreadable_free_vram_is_refused_rather_than_assumed_to_fit(monkeypatch):
    """⚠ The same rule one level down: if we cannot read the budget, we do not spend it."""
    import core.vram_guard as g
    monkeypatch.setattr(g, "cuda_memory", lambda: None)
    monkeypatch.setattr(g, "apply_allocator_cap", lambda f: {"applied": False})
    r = g.preflight(416, "int8", 64, requirement_mib=1000)
    assert r.outcome == REFUSED_NO_MEASUREMENT and r.may_fold is False


def test_insufficient_headroom_is_refused_with_the_arithmetic_stated(monkeypatch):
    """⚠ The real shape: int8 at 416 aa peaked at 7,658 MiB while only 7,043 was free.

    Prove it bites by dropping the margin from the comparison: 7,000 + 0 <= 7,043 passes, and the
    fold that may already have been spilling is attempted again."""
    import core.vram_guard as g
    monkeypatch.setattr(g, "cuda_memory", lambda: (7043, 8150))
    monkeypatch.setattr(g, "apply_allocator_cap", lambda f: {"applied": False})
    r = g.preflight(416, "int8", 64, requirement_mib=7000)
    assert r.outcome == REFUSED_INSUFFICIENT_HEADROOM
    assert "7512 MiB" in r.detail and "7043 MiB is free" in r.detail


def test_a_fold_that_fits_with_margin_is_allowed(monkeypatch):
    """⚠ A-017 clause (c): without this the refusals above pass under a guard that refuses
    everything, which would be indistinguishable from a guard that works."""
    import core.vram_guard as g
    monkeypatch.setattr(g, "cuda_memory", lambda: (7043, 8150))
    monkeypatch.setattr(g, "apply_allocator_cap", lambda f: {"applied": False})
    r = g.preflight(200, "int8", 64, requirement_mib=4000)
    assert r.outcome == FIT and r.may_fold is True


def test_the_margin_is_applied_and_is_not_zero_by_default():
    """⚠ The requirement curve is measured on ONE protein per length; a different sequence at the
    same length is not guaranteed to demand the same memory."""
    assert DEFAULT_MARGIN_MIB > 0


# ── ⚠ layer 1 is not ours, and the guard says so rather than guessing ───────
def test_layer_one_reports_unknown_never_ok():
    """⚠⚠ REPORTING THE DRIVER SETTING AS `ok` BECAUSE WE COULD NOT FIND A PROBLEM WOULD BE AN
    ABSENT MEASUREMENT COERCED INTO AN AFFIRMATIVE — the F-018 shape, one layer down.

    Prove it bites by returning `{"state": "ok"}`: the crank would read a driver setting nobody
    verified as a safety guarantee."""
    s = sysmem_fallback_state()
    assert s["state"] == "unknown"
    assert s["state"] != "ok"
    assert "owner_action" in s and "Sysmem Fallback" in s["owner_action"]
    assert "bugcheck" in s["why_it_matters"]


def test_layer_two_declares_what_it_does_not_cover():
    """⚠ A strong guard, not a proof. A cap reported without its gaps reads as total coverage."""
    out = apply_allocator_cap(0.85)
    if out.get("applied"):
        assert "does_not_cover" in out
        assert "cuBLAS" in out["does_not_cover"] or "context" in out["does_not_cover"]
    else:
        assert "why" in out


def test_an_out_of_range_fraction_raises_rather_than_clamping():
    with pytest.raises(ValueError):
        apply_allocator_cap(0)
    with pytest.raises(ValueError):
        apply_allocator_cap(1.5)


# ── ⚠ HOST_DOWN is inferred, and its absence proves nothing ─────────────────
def test_a_job_left_running_across_a_restart_is_evidence_of_a_host_death():
    r = infer_host_down(1)
    assert r["verdict"] == HOST_DOWN
    assert "STOP" in r["action"]


def test_no_such_job_is_reported_as_no_evidence_not_as_healthy():
    """⚠⚠ THE ASYMMETRY, AND IT IS THE POINT. A boolean would let "no evidence" read as "fine".

    Prove it bites by returning `False`/`healthy`: a host that died before claiming anything reads
    as a clean run."""
    r = infer_host_down(0)
    assert r["verdict"] != HOST_DOWN
    assert r["verdict"] == "no_evidence_of_host_death"
    assert "NOT a clean bill of health" in r["caveat"]


def test_preflight_carries_every_layer_onto_the_record(monkeypatch):
    """⚠ The decision travels on the artifact, so nobody has to re-derive why a fold was skipped."""
    import core.vram_guard as g
    monkeypatch.setattr(g, "cuda_memory", lambda: (7043, 8150))
    r = g.preflight(200, "int8", 64, requirement_mib=4000)
    assert set(r.layers) == {"layer1_sysmem_fallback", "layer2_allocator_cap"}
    assert r.layers["layer1_sysmem_fallback"]["state"] == "unknown"
