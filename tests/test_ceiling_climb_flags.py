# -*- coding: utf-8 -*-
"""F-062 climb flags: refuse without layer1 attestation; honor fold-in-child; refuse append."""
from __future__ import annotations

import json
import os

import pytest

from scripts import ceiling_climb as cc


def test_refuses_without_layer1_attested(tmp_path, monkeypatch):
    cache = tmp_path / "spancache"
    cache.mkdir()
    (cache / "Q8WXD0.json").write_text(
        json.dumps({"sequence": {"value": "A" * 500}}), encoding="utf-8"
    )
    monkeypatch.setattr(cc, "CACHE", cache)
    monkeypatch.setattr(cc, "CENSUS", tmp_path)
    monkeypatch.delenv("WORKER_FOLD_IN_CHILD", raising=False)
    out = tmp_path / "climb.jsonl"
    with pytest.raises(SystemExit) as ei:
        cc.run([
            "--accession", "Q8WXD0", "--tier", "local",
            "--start", "248", "--stop", "256", "--step", "8",
            "--memory-fraction", "0.85",
            "--out", str(out),
        ])
    assert "layer1-attested" in str(ei.value).lower() or "REFUSING TO CLIMB" in str(ei.value)


def test_refuses_append_to_existing_out(tmp_path, monkeypatch):
    cache = tmp_path / "spancache"
    cache.mkdir()
    (cache / "Q8WXD0.json").write_text(
        json.dumps({"sequence": {"value": "A" * 500}}), encoding="utf-8"
    )
    monkeypatch.setattr(cc, "CACHE", cache)
    monkeypatch.setattr(cc, "CENSUS", tmp_path)
    out = tmp_path / "climb.jsonl"
    out.write_text("{}\n", encoding="utf-8")
    with pytest.raises(SystemExit) as ei:
        cc.run([
            "--accession", "Q8WXD0", "--tier", "local",
            "--start", "248", "--stop", "256", "--step", "8",
            "--memory-fraction", "0.85", "--layer1-attested",
            "--out", str(out),
        ])
    assert "already exists" in str(ei.value)


def test_cache_miss_stops_without_fetch(tmp_path, monkeypatch):
    cache = tmp_path / "spancache"
    cache.mkdir()
    monkeypatch.setattr(cc, "CACHE", cache)
    monkeypatch.setattr(cc, "CENSUS", tmp_path)
    out = tmp_path / "climb.jsonl"
    with pytest.raises(SystemExit) as ei:
        cc.run([
            "--accession", "MISSING", "--tier", "local",
            "--start", "248", "--stop", "256", "--step", "8",
            "--memory-fraction", "0.85", "--layer1-attested",
            "--out", str(out),
        ])
    assert "NOT fetched" in str(ei.value) or "no cache" in str(ei.value).lower()


def test_fold_in_child_flag_sets_env(tmp_path, monkeypatch):
    cache = tmp_path / "spancache"
    cache.mkdir()
    (cache / "Q8WXD0.json").write_text(
        json.dumps({"sequence": {"value": "A" * 100}}), encoding="utf-8"
    )
    monkeypatch.setattr(cc, "CACHE", cache)
    monkeypatch.setattr(cc, "CENSUS", tmp_path)
    monkeypatch.delenv("WORKER_FOLD_IN_CHILD", raising=False)
    out = tmp_path / "climb.jsonl"
    with pytest.raises(SystemExit) as ei:
        cc.run([
            "--accession", "Q8WXD0", "--tier", "local",
            "--start", "248", "--stop", "456", "--step", "8",
            "--memory-fraction", "0.85", "--layer1-attested", "--fold-in-child",
            "--out", str(out),
        ])
    assert "shorter than" in str(ei.value)
    assert os.environ.get("WORKER_FOLD_IN_CHILD") == "1"
