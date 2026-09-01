"""D-082 — the guard refuses rather than attempts, and never reports safety it cannot see.

⚠⚠ **THE PREMISE.** On 2026-08-16 an over-VRAM fp16 fold bugchecked the host: there was no process
left to catch anything. **Any assertion here that a failure is "caught" would be testing the wrong
property.** What is tested is that the fold is REFUSED BEFORE the allocation.
"""

from __future__ import annotations

import pytest

from core.vram_guard import (
    DEFAULT_MARGIN_MIB, FIT, HOST_DOWN, REFUSED_INSUFFICIENT_HEADROOM, REFUSED_NO_MEASUREMENT,
    Preflight, apply_allocator_cap, f059_peak_gib, infer_host_down, preflight,
    sysmem_fallback_state,
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


def test_f059_peak_gib_is_the_published_law_not_a_requirement():
    """F-059 §1 / F-061: the helper records the law. It is not preflight's measurement."""
    assert abs(f059_peak_gib(1) - 5.24) < 1e-4
    # F-059 table: 439 aa → 6.50 GiB peak
    assert abs(f059_peak_gib(439) - 6.50) < 0.05
    import inspect
    assert "requirement_mib" in inspect.signature(preflight).parameters


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


# ── ⚠ D-082: the stack must name the driver, or a fold cannot be attributed ──
def test_the_fold_provenance_captures_the_nvidia_driver_version():
    """⚠⚠ THE GAP THE 2026-08-16 CRASH EXPOSED. The fold record captured torch, transformers, CUDA
    and the device name — and NOT the driver, which is the one component that turned an
    over-allocation into a HOST BUGCHECK rather than an exception.

    D-082: a ceiling, and a determinism verdict, are valid only under the recipe AND the stack that
    produced them. Without this field a fold cannot be attributed to a driver at all, and a result
    measured under 596.72 would silently read as applying to whatever is installed later.

    Prove it bites by removing the field or the probe."""
    import dataclasses
    from worker.runner import FoldProvenance, _capture_environment
    assert "nvidia_driver_version" in [f.name for f in dataclasses.fields(FoldProvenance)]
    env = _capture_environment()
    assert "nvidia_driver_version" in env


def test_an_absent_nvidia_smi_yields_none_rather_than_failing_the_fold(monkeypatch):
    """⚠ A diagnostic that can fail the fold is worse than the gap it fills. `None` is a CATEGORY —
    'the driver was not readable' — never a zero and never a guess.

    Prove it bites by removing the try/except: the CI gate, which has no nvidia-smi, dies."""
    import subprocess
    from worker.runner import _capture_environment

    def boom(*a, **k):
        raise FileNotFoundError("nvidia-smi")

    monkeypatch.setattr(subprocess, "run", boom)
    env = _capture_environment()
    assert env["nvidia_driver_version"] is None


def test_every_captured_environment_key_has_a_provenance_field():
    """⚠⚠ THE DRIFT GUARD, and it exists because the drift already happened.

    `fold()` assigned the environment onto the provenance with FOUR HAND-WRITTEN LINES. A fifth key
    — `nvidia_driver_version` — was added to `_capture_environment` and to the dataclass, and the
    assignment list was not updated. Every fold then recorded `None` for the one field `### D-082`
    required, **one commit after the entry demanding it.** Two paths to one quantity, nothing
    comparing them.

    ⚠ The assignment is now a loop over the dict, so the two cannot disagree — and this asserts the
    key set matches the fields, so a key added to one side and not the other reds here rather than
    silently writing `None` into every record.

    Prove it bites by adding a key to `_capture_environment`'s dict with no matching field."""
    import dataclasses
    from worker.runner import FoldProvenance, _capture_environment
    fields = {f.name for f in dataclasses.fields(FoldProvenance)}
    missing = set(_capture_environment()) - fields
    assert not missing, (
        f"captured environment key(s) with no FoldProvenance field: {sorted(missing)} — they would "
        f"be silently dropped from every fold record")


def test_fold_assigns_the_environment_from_the_dict_not_by_hand():
    """⚠⚠ ASSERTED STATICALLY OVER THE SOURCE, because the behavioural version proved NOTHING.

    My first attempt performed the `setattr` loop inside the TEST, so it exercised the loop in
    the test and not the one in `fold()` — reverting `fold()` to the hand-written four-line
    assignment left it GREEN. **A-017 clause (a): the fixture never reached the code under
    test**, the same class as the three revert proofs that proved nothing on 2026-08-06.

    `fold()` needs a GPU, so the assignment cannot be exercised on the CI gate. It is pinned
    over the source instead — the precedent is `test_comparator_is_exact_not_tolerant`, which
    asserts the absence of tolerance "behaviourally and statically over this source".

    Prove it bites by restoring `prov.torch_version = env["torch_version"]` and its siblings:
    the hand-written list reappears and this reds."""
    import pathlib as _pl
    import re
    src = (_pl.Path(__file__).resolve().parent.parent / "worker" / "runner.py").read_text(
        encoding="utf-8")
    assert "for _key, _value in env.items():" in src, (
        "fold() no longer assigns the environment from the dict")
    assert "setattr(prov, _key, _value)" in src, (
        "the environment assignment loop is gone from fold()")
    hand = re.findall(
        r"^\s*prov\.(torch_version|transformers_version|device_name|cuda_version|"
        r"nvidia_driver_version)\s*=", src, re.M)
    assert not hand, (
        f"fold() assigns environment field(s) by hand: {hand}. A hand-written list must track "
        f"a dict, and it already drifted once — nvidia_driver_version was captured and never "
        f"assigned, so every fold recorded None for the field D-082 required.")

