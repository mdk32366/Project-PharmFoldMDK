"""D-036 retrieval-script tests (`scripts/retrieve_rental_pae.py`), written before the code.

The transfer POSTs each local `pae.json` gzipped to the new route. Committed, reproducible code
(D-009 §3), not a shell one-liner. The `post` callable is injected so the walk/gzip/report logic
is hermetic — no network, no real Fly. Idempotency is the script's re-run converging (the route
is idempotent server-side, D-036); the script simply re-POSTs.
"""

from __future__ import annotations

import gzip
import json
from pathlib import Path

from scripts.retrieve_rental_pae import transfer_all


def _seed_pae(root, job_id, pae):
    d = Path(root) / str(job_id)
    d.mkdir(parents=True)
    (d / "pae.json").write_text(json.dumps(pae), encoding="utf-8")


def test_transfer_all_posts_each_pae_gzipped(tmp_path):
    _seed_pae(tmp_path, 1, [[1.0]])
    _seed_pae(tmp_path, 37, [[2.0, 3.0]])
    posted = {}

    def fake_post(job_id, gz):
        posted[job_id] = json.loads(gzip.decompress(gz))     # the body is the gzipped PAE
        return True

    results = transfer_all(str(tmp_path), post=fake_post)
    assert results == {1: True, 37: True}
    assert posted == {1: [[1.0]], 37: [[2.0, 3.0]]}


def test_transfer_all_skips_dirs_without_pae(tmp_path):
    (Path(tmp_path) / "5").mkdir()                            # a job dir with no pae.json
    _seed_pae(tmp_path, 6, [[9.0]])
    seen = []
    transfer_all(str(tmp_path), post=lambda j, g: seen.append(j) or True)
    assert seen == [6]


def test_transfer_all_reports_failures(tmp_path):
    _seed_pae(tmp_path, 1, [[1.0]])
    _seed_pae(tmp_path, 2, [[2.0]])
    results = transfer_all(str(tmp_path), post=lambda j, g: j == 1)   # job 2 "fails"
    assert results == {1: True, 2: False}


def test_transfer_all_is_idempotent_on_rerun(tmp_path):
    _seed_pae(tmp_path, 1, [[1.0]])
    calls = []

    def fake_post(job_id, gz):
        calls.append(job_id)
        return True

    transfer_all(str(tmp_path), post=fake_post)
    transfer_all(str(tmp_path), post=fake_post)               # re-run: files still there, re-POST
    assert calls == [1, 1]                                    # converges server-side (route idempotent)
