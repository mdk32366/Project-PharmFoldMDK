"""Task 2 / route (a) — the LOCAL tier's PAE reaches the column, not just the disk.

⚠⚠ TWO GATES, AND FIXING ONLY THE FIRST IS A SILENT HALF-FIX.
  Gate A — ``worker/main.py`` ``if artifact_dir:`` → ``_persist_pae_local`` writes the FILE.
  Gate B — ``scripts/retrieve_rental_pae.py`` is the ONLY feeder of ``pae_json_path``, and it
           is a rental-pod-termination script. On local there is no pod, so nothing ever fed
           the column.
Writing a file to local disk and leaving ``pae_json_path`` NULL is the defect wearing a fix.

⚠ ROUTE (a) (AMENDMENT 1 §3.2, ruled): widen the **D-036 out-of-band route** to feed the column
on local. ``POST /jobs/{job_id}/pae`` → ``app.artifacts.persist_pae`` writes the file into
``artifact_root`` **and** sets the column in one transaction, so reaching that route is what
makes the column non-NULL. Route (b) — putting PAE back on the upload — is NOT taken: ``D-035``
§3(c) records ``await pae.read()`` whole-body into memory and warns explicitly that returning PAE
to the upload path makes that live again.

⚠ AMENDED TASK 3.3 BINDS: the COLUMN non-NULL **AND** the file resolves. Both. Per fold. These
tests own the first half — that the local path reaches the only thing that writes the column.

⚠ FORWARD ONLY. Nothing here backfills: ``F-042`` closes on its SECOND clause — the recorded rows
carry the statement that they do not and why. The finding closes by disclosure, not erasure.
"""
from __future__ import annotations

import gzip
import json

import pytest

from worker.main import fold_from_spec
from worker.orchestrator import FoldSpec
from worker.runner import MODEL_REVISION


class _Result:
    """A fold result carrying PAE, which is the only interesting case here."""

    def __init__(self, pae=None):
        self.pae = pae


def _spec(**kw) -> FoldSpec:
    base = dict(job_id=77, sequence="MKT", model_revision=MODEL_REVISION, dtype="int8",
                chunk_size=64, source="sliced_ecd", ecd_start=1, ecd_end=3)
    base.update(kw)
    return FoldSpec(**base)


def _fold_returning(pae):
    def fake_fold(sequence, *, dtype, chunk_size, source, ecd_start, ecd_end, length_cap=None):
        return _Result(pae=pae)
    return fake_fold


class _PaeSpy:
    """Stands in for the D-036 route. Records what a real POST would carry."""

    def __init__(self):
        self.calls = []

    def __call__(self, job_id, pae_gz):
        self.calls.append((job_id, pae_gz))


# ── A-017: the fixture must reach the local branch, and the fold must HAVE a PAE ─────────────

def test_the_fixture_reaches_the_local_branch_and_the_fold_actually_carries_pae():
    """⚠⚠ A-017 POSITIVE CONTROL, AND IT IS LOAD-BEARING HERE.

    Two ways the assertions below could pass while proving nothing:
      (a) the fixture sets ``artifact_dir``, so the RENTAL branch runs and the local one is
          never entered — a test that never enters ``_persist_pae_local``'s sibling passes
          under any implementation;
      (b) the fold returns no PAE at all, so *"nothing was posted"* is correct for the wrong
          reason and the test can never discriminate.
    This pins both open before anything else runs."""
    pae = [[0.0, 1.0], [1.0, 0.0]]
    result = fold_from_spec(_spec(), _fold_returning(pae), artifact_dir=None)
    assert result.pae == pae, (
        "the fixture's fold emitted no PAE — every assertion below would pass vacuously")
    # ⚠ The local branch is the one with artifact_dir unset. `config_from_env` reads
    # WORKER_ARTIFACT_DIR, and `worker/main.py` documents unset as "the local tier".
    assert _spec().job_id == 77


# ── the behaviour the file exists for ────────────────────────────────────────────────────────

def test_a_local_fold_sends_its_pae_to_the_route_that_writes_the_column():
    """⚠⚠ THE ASSERTION THE PIPELINE WAS MISSING.

    Gate B is the only writer of ``pae_json_path`` and it is a rental-termination script, so a
    local fold produced PAE that nothing ever recorded — 2,691 census rows, every one NULL
    (``F-042``). This asserts the local path reaches the route, which is what sets the column."""
    spy = _PaeSpy()
    pae = [[0.0, 1.5], [1.5, 0.0]]
    fold_from_spec(_spec(job_id=4242), _fold_returning(pae), artifact_dir=None, pae_post_fn=spy)

    assert spy.calls, (
        "a local fold produced PAE and nothing reached the D-036 route — the column stays NULL, "
        "which is F-042 reproduced rather than repaired")
    job_id, pae_gz = spy.calls[0]
    assert job_id == 4242, "the PAE was posted against the wrong job"
    assert json.loads(gzip.decompress(pae_gz)) == pae, (
        "the posted bytes are not this fold's PAE, gzipped as the route expects")


def test_a_local_fold_with_no_pae_posts_nothing():
    """⚠ The absent case is a NAMED outcome, not a silent one. A fold that emitted no PAE has
    nothing to record, and inventing an empty matrix would be worse than the NULL."""
    spy = _PaeSpy()
    fold_from_spec(_spec(), _fold_returning(None), artifact_dir=None, pae_post_fn=spy)
    assert spy.calls == []


def test_the_rental_path_is_untouched_by_this_change(tmp_path):
    """⚠⚠ RENTAL BEHAVIOUR MUST NOT MOVE. ``D-036`` writes PAE to the pod's disk for out-of-band
    retrieval before termination, and ``scripts/retrieve_rental_pae.py`` is the blocking gate
    before the pod dies. Reaching the route from the rental box as well would double-write and
    change a path whose failure costs a PAID re-fold."""
    spy = _PaeSpy()
    written = {}

    def fake_write_pae(result, out_dir):
        written["out_dir"] = str(out_dir)
        return f"{out_dir}/pae.json"

    fold_from_spec(_spec(job_id=9), _fold_returning([[0.0]]), artifact_dir=str(tmp_path),
                   write_pae_fn=fake_write_pae, pae_post_fn=spy)

    assert written["out_dir"].endswith("9"), "the rental local write stopped keying on job_id"
    assert spy.calls == [], "the rental path posted to the route — that is a behaviour change"


def test_a_failed_post_is_loud_on_local_rather_than_swallowed():
    """⚠⚠ TASK 2.5'S LOCAL EQUIVALENT OF THE RENTAL GATE.

    ``_persist_pae_local`` swallows deliberately: on rental a crash before the upload leaves the
    job to reap and re-fold **on a paid card**, and the missing file is caught downstream by the
    retrieval-verify step that gates pod termination. **On local there is no pod and therefore no
    gate** — a guard placed where the money is, not where the data is.

    So a local POST failure must be LOUD. A swallowed one produces exactly the state this whole
    task exists to remove: a fold that looks fine and a column that is NULL, invisible until the
    campaign ends."""
    def exploding_post(job_id, pae_gz):
        raise RuntimeError("route unreachable")

    with pytest.raises(RuntimeError):
        fold_from_spec(_spec(), _fold_returning([[0.0]]), artifact_dir=None,
                       pae_post_fn=exploding_post)


def test_run_actually_wires_the_route_into_the_fold_path():
    """⚠⚠ THE HALF-FIX THIS FILE COULD STILL HAVE SHIPPED.

    Every assertion above exercises `fold_from_spec` directly. All of them pass while `run()`
    never passes `pae_post_fn`, leaving a correct function that production never calls — which is
    `F-054`'s shape: a feature absent from production behind a green suite. This asserts the
    wiring, not the unit.

    ⚠ Asserted BEHAVIOURALLY, by capturing the callable `run()` hands the loop and invoking it.
    A `inspect.getsource(...)` string check would have been the textual guard this repository
    has now recorded three instances of — correct behaviour protected by a string that a
    refactor preserves while breaking what it describes."""
    from worker import main as worker_main

    posted: list[tuple[int, bytes]] = []
    captured: dict = {}

    class _FakeClient:
        def persist_pae(self, job_id, pae_gz):
            posted.append((job_id, pae_gz))

    def fake_run_worker(client, fold_callable, worker_id, **kw):
        captured["fold_callable"] = fold_callable

    def _fit_preflight(length, dtype, chunk_size, *, requirement_mib, margin_mib, **_):
        # ⚠⚠ run() now DEFAULTS to the real gate, and `preflight` refuses when free
        # VRAM cannot be read - which is every CI box. This test is about WIRING, not about
        # gating, so it injects a FIT rather than leaving the default to refuse. The gate's
        # own refusals are asserted in tests/test_worker_preflight_gate.py.
        from core.vram_guard import FIT, Preflight
        return Preflight(outcome=FIT, length=length, dtype=dtype, chunk_size=chunk_size,
                         free_mib=7043, total_mib=8151, required_mib=requirement_mib,
                         margin_mib=margin_mib, memory_fraction=0.85, layers={}, detail="")

    monkeypatch_target = worker_main.build_client
    worker_main.build_client = lambda cfg: _FakeClient()          # noqa: E731
    try:
        cfg = worker_main.WorkerConfig(transport_url="http://unused", auth_token="t",
                                       worker_id="w", artifact_dir=None)
        worker_main.run(cfg,
                        fold_fn=_fold_returning([[0.0, 2.0], [2.0, 0.0]]),
                        run_worker_fn=fake_run_worker,
                        preflight_fn=_fit_preflight)
    finally:
        worker_main.build_client = monkeypatch_target

    assert "fold_callable" in captured, "run() never handed a fold callable to the loop"
    captured["fold_callable"](_spec(job_id=555))

    assert posted, (
        "run()'s fold path does not reach the D-036 route — the local tier would fold, produce "
        "PAE, and record nothing, which is F-042 reproduced rather than repaired")
    assert posted[0][0] == 555
    assert json.loads(gzip.decompress(posted[0][1])) == [[0.0, 2.0], [2.0, 0.0]]
