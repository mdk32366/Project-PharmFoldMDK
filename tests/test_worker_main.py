"""Worker entry point (worker/main.py) — wiring the D-030 loop to the D-031 transport.

Tested WITHOUT a GPU: the real fold (`worker.runner.fold`) is GPU-bound and is the owner's to
run on the box — this suite stops before it. Everything up to the fold is hermetic: config from
the environment, the `FoldSpec`→`fold(...)` adapter (with its model-revision guard), client
construction, and the `run()` wiring, all exercised with an injected fold so no ESMFold call is
ever made here.

`FoldSpec` is imported from `worker.orchestrator` — its stable public location before and after
the DEP-001 relocation (re-export), so this entry point does not depend on #48's merge order.
"""

from __future__ import annotations

import pytest

from worker.http_client import HttpQueueClient
from worker.main import (
    DEFAULT_TRANSPORT_URL,
    WorkerConfig,
    build_client,
    config_from_env,
    fold_from_spec,
    run,
)
from worker.orchestrator import FoldError, FoldSpec
from worker.runner import MODEL_REVISION


def _spec(**kw) -> FoldSpec:
    base = dict(job_id=1, sequence="MKT", model_revision=MODEL_REVISION, dtype="int8",
                chunk_size=64, source="sliced_ecd", ecd_start=1, ecd_end=3)
    base.update(kw)
    return FoldSpec(**base)


# ── config from the environment ───────────────────────────────────────────────

def test_config_defaults(monkeypatch):
    monkeypatch.setenv("WORKER_AUTH_TOKEN", "tok")
    monkeypatch.delenv("TRANSPORT_URL", raising=False)
    monkeypatch.delenv("WORKER_ID", raising=False)
    monkeypatch.delenv("WORKER_POLL_INTERVAL", raising=False)
    c = config_from_env()
    assert c.auth_token == "tok"
    assert c.transport_url == DEFAULT_TRANSPORT_URL
    assert c.worker_id == "local-gpu"
    assert c.poll_interval == 5.0


def test_config_overrides_and_strips_trailing_slash(monkeypatch):
    monkeypatch.setenv("WORKER_AUTH_TOKEN", "tok")
    monkeypatch.setenv("TRANSPORT_URL", "https://pharmfoldmdk.fly.dev/")
    monkeypatch.setenv("WORKER_ID", "gpu-box-1")
    monkeypatch.setenv("WORKER_POLL_INTERVAL", "2.5")
    c = config_from_env()
    assert c.transport_url == "https://pharmfoldmdk.fly.dev"   # no trailing slash
    assert c.worker_id == "gpu-box-1"
    assert c.poll_interval == 2.5


def test_config_requires_token(monkeypatch):
    monkeypatch.delenv("WORKER_AUTH_TOKEN", raising=False)
    with pytest.raises(KeyError):                              # loud failure, no silent default
        config_from_env()


# ── the FoldSpec → fold adapter (stops before the real GPU fold) ──────────────

def test_fold_from_spec_maps_every_input():
    captured = {}

    def fake_fold(sequence, *, dtype, chunk_size, source, ecd_start, ecd_end, length_cap=None):
        captured.update(sequence=sequence, dtype=dtype, chunk_size=chunk_size,
                        source=source, ecd_start=ecd_start, ecd_end=ecd_end)
        return "RESULT"

    out = fold_from_spec(
        _spec(sequence="MKTMKT", dtype="fp16", chunk_size=None,
              source="whole", ecd_start=None, ecd_end=None),
        fold_fn=fake_fold,
    )
    assert out == "RESULT"
    assert captured == dict(sequence="MKTMKT", dtype="fp16", chunk_size=None,
                            source="whole", ecd_start=None, ecd_end=None)


def test_fold_from_spec_rejects_model_revision_mismatch():
    def fake_fold(*a, **k):
        raise AssertionError("must NOT fold when the job pins a different model revision")

    with pytest.raises(FoldError):
        fold_from_spec(_spec(model_revision="deadbeef"), fold_fn=fake_fold)


# ── client construction carries the bearer token (D-031 §4) ───────────────────

def test_build_client_is_http_client_with_bearer_token():
    c = build_client(WorkerConfig(transport_url="http://x", auth_token="sekret", worker_id="w"))
    assert isinstance(c, HttpQueueClient)
    assert c._headers == {"Authorization": "Bearer sekret"}


# ── run() wires the loop with the adapter (fold never actually runs) ──────────

def test_run_wires_client_adapter_and_config():
    calls = {}

    def fake_run_worker(client, fold, worker_id, **kw):
        calls.update(client=client, worker_id=worker_id,
                     poll_interval=kw.get("poll_interval"))
        # prove `fold` is the adapter over our injected fold_fn, without a GPU
        calls["folded"] = fold(_spec(sequence="AAA"))

    def fake_fold(sequence, **k):
        return f"folded:{sequence}"

    cfg = WorkerConfig(transport_url="http://x", auth_token="t", worker_id="wid",
                       poll_interval=2.0)
    run(cfg, fold_fn=fake_fold, run_worker_fn=fake_run_worker)

    assert isinstance(calls["client"], HttpQueueClient)
    assert calls["worker_id"] == "wid"
    assert calls["poll_interval"] == 2.0
    assert calls["folded"] == "folded:AAA"
