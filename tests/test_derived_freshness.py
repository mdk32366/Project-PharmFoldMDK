"""A derived artifact must not quietly describe a manifest that is no longer there.

⚠ `span_segments.csv` and `census_labels.csv` are derived from the census manifest. A revision does
not make them fail, warn or change — **they keep answering**. A wrong topology is worse than a
missing one, because a missing one is visible.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from core.derived_freshness import (  # noqa: E402
    ABSENT, FRESH, SOURCE_HASH_KEY, STALE, UNSTAMPED, check, file_sha256, stamp,
)

CENSUS = REPO / "data" / "census"
MANIFEST = CENSUS / "census_manifest.v7.csv"


def test_a_matching_hash_is_fresh_and_a_changed_one_is_stale(tmp_path):
    m = tmp_path / "manifest.csv"
    m.write_text("a,b\n1,2\n", encoding="utf-8")
    prov = tmp_path / "d.provenance.json"
    prov.write_text(json.dumps(stamp(m)), encoding="utf-8")
    assert check(prov, m)[0] == FRESH

    m.write_text("a,b\n1,3\n", encoding="utf-8")   # ⚠ one byte
    verdict, note = check(prov, m)
    assert verdict == STALE
    assert "RE-RUN" in note


def test_the_four_verdicts_are_distinct_because_they_need_different_actions(tmp_path):
    """⚠ `unstamped` is NOT `stale` and NOT `fresh` — it is 'this predates the check'. Collapsing
    it into either would recommend the wrong action."""
    m = tmp_path / "m.csv"
    m.write_text("x", encoding="utf-8")
    assert check(tmp_path / "nope.json", m)[0] == ABSENT
    p = tmp_path / "p.json"
    p.write_text(json.dumps({"derived_on": "whenever"}), encoding="utf-8")
    assert check(p, m)[0] == UNSTAMPED
    assert len({FRESH, STALE, UNSTAMPED, ABSENT}) == 4


def test_an_unreadable_provenance_is_stale_not_fresh(tmp_path):
    """⚠ Treating a file we cannot parse as fresh would trust it precisely when we cannot."""
    m = tmp_path / "m.csv"
    m.write_text("x", encoding="utf-8")
    p = tmp_path / "p.json"
    p.write_text("{not json", encoding="utf-8")
    assert check(p, m)[0] == STALE


def test_freshness_is_content_not_mtime(tmp_path):
    """⚠ A file copied or checked out has a new mtime and identical content. mtime would cry stale
    on a `git checkout` and stay quiet on an in-place edit that preserved it — wrong both ways."""
    a, b = tmp_path / "a", tmp_path / "b"
    a.write_bytes(b"same"); b.write_bytes(b"same")
    assert file_sha256(a) == file_sha256(b)
    assert file_sha256(tmp_path / "missing") is None      # ⚠ None, never a crash


@pytest.mark.parametrize("name", ["span_segments", "census_labels"])
def test_the_shipped_derivations_are_stamped_and_fresh(name):
    """⚠ Both are checked in. If this reds, the artifact was re-derived without the manifest, or
    the manifest moved without the artifact — either way, re-run the script."""
    prov = CENSUS / f"{name}.provenance.json"
    if not prov.is_file() or not MANIFEST.is_file():
        pytest.skip(f"{name} or the manifest is absent")
    assert SOURCE_HASH_KEY in json.loads(prov.read_text(encoding="utf-8"))
    verdict, note = check(prov, MANIFEST)
    assert verdict == FRESH, note


def test_the_census_surface_drops_a_stale_derivation_rather_than_serving_it():
    """⚠⚠ The consumer must REFUSE, not degrade to the old numbers. Asserted over the source, so
    the guard survives the implementation being rewritten."""
    src = (REPO / "app" / "reads.py").read_text(encoding="utf-8")
    assert "from core.derived_freshness import FRESH, check" in src
    assert "seg_verdict == FRESH" in src, "segments are loaded without checking freshness"
    assert "lab_verdict == FRESH" in src, "labels are loaded without checking freshness"
    assert "derivation_status" in src, "the verdict is not carried to the consumer"
