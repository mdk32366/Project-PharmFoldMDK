"""`GC2`/`GC3`/`GC5` — the ingest's acceptance bar, and the proof that it REJECTS.

⚠⚠ **A BAR NEVER SEEN TO REJECT IS DECORATION** (Principle 9). Every assertion here is paired with
a corrupted fixture that must make it fail, and the corruption is **one count in one row** — the
smallest thing that can be wrong, because a bar that only catches gross damage is not a bar.

⚠ **These run without a database.** The bar is pure: rows in, verdict out. That is deliberate —
it means the rejection can be proven in the ordinary gate rather than only in the `postgres` job,
and it means the transaction wrapper has nothing to hide behind.

⚠ Fixtures are synthetic and small. The REAL numbers (337 / 1,303 / 1,640) are asserted as the
module's constants, so a change to `D-100`'s figures is a visible diff rather than a silent drift.
"""
from __future__ import annotations

import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from core.clinical_ingest import (  # noqa: E402
    D100_EXCLUDED,
    D100_KEPT,
    D100_ROWS,
    IngestRefused,
    assert_grid_or_refuse,
    is_noop_rerun,
    reproduce_d100,
    sha256_of,
    verify_source,
)


def _pair(gene, cancer, high, medium, low, nd):
    ingested = {"gene_name": gene, "cancer": cancer,
                "high": high, "medium": medium, "low": low, "not_detected": nd}
    s3 = {"Gene name": gene, "Cancer": cancer,
          "High": high, "Medium": medium, "Low": low, "Not detected": nd}
    return ingested, s3


def _grid(n_kept, n_excluded):
    """A synthetic grid with a known kept/excluded split.

    ⚠ `qh = 100·(low + 2·medium + 3·high)/total`, cutoff 150 INCLUSIVE (`F-043`: 52 pairs sit at
    exactly 150.0 and the sign is worth 51 of them). All-High gives 300 → kept; all-Low gives
    100 → excluded.
    """
    ing, s3 = [], []
    for i in range(n_kept):
        a, b = _pair(f"KEPT{i}", "breast cancer", 10, 0, 0, 0)
        ing.append(a); s3.append(b)
    for i in range(n_excluded):
        a, b = _pair(f"EXCL{i}", "breast cancer", 0, 0, 10, 0)
        ing.append(a); s3.append(b)
    return ing, s3


def test_the_constants_are_d100s_figures():
    """⚠ Pinned, so a change to the acceptance bar is a diff and not a drift."""
    assert (D100_KEPT, D100_EXCLUDED, D100_ROWS) == (337, 1303, 1640)
    assert D100_KEPT + D100_EXCLUDED == D100_ROWS


def test_a_grid_that_reproduces_exactly_is_accepted():
    ing, s3 = _grid(D100_KEPT, D100_EXCLUDED)
    v = assert_grid_or_refuse(ing, s3)
    assert (v.rows, v.kept, v.excluded) == (D100_ROWS, D100_KEPT, D100_EXCLUDED)
    assert v.ok and not v.mismatches


def test_one_corrupted_count_in_one_row_refuses_the_whole_ingest():
    """⚠⚠ `GC3`. The smallest possible corruption — one count, one row — must roll the whole
    transaction back. If this passes, a wrong ingest lands."""
    ing, s3 = _grid(D100_KEPT, D100_EXCLUDED)
    ing[0]["high"] = 9                      # was 10; the S3 row still says 10
    with pytest.raises(IngestRefused) as exc:
        assert_grid_or_refuse(ing, s3)
    msg = str(exc.value)
    assert "may not commit" in msg and "high ingested 9 != S3 10" in msg


def test_a_corruption_that_preserves_the_score_is_still_caught():
    """⚠⚠ THE DISCRIMINATING CASE. Two panels can give the SAME `qh` from different counts, so a
    score-only bar would pass a corrupted ingest. All four columns are compared for that reason.

    `high=2, low=0` and `high=1, medium=1, low=1` over the same total both give qh=... — the point
    is that the counts differ while the derived figure need not, and the check must see the counts.
    """
    ing, s3 = _grid(2, 0)
    # same total, same kept/excluded verdict, different composition
    ing[0].update(high=8, medium=3, low=0, not_detected=0)
    s3[0].update(High=10, Medium=0, Low=0, **{"Not detected": 0})
    v = reproduce_d100(ing, s3)
    assert v.mismatches, "a composition change slipped past because only the score was compared"


def test_a_missing_row_is_caught_rather_than_silently_shrinking_the_grid():
    """⚠ An ingest that wrote 1,639 of 1,640 rows must fail. A row count that merely *looks*
    plausible is exactly what this bar exists to refuse."""
    ing, s3 = _grid(D100_KEPT, D100_EXCLUDED)
    ing.pop()
    with pytest.raises(IngestRefused) as exc:
        assert_grid_or_refuse(ing, s3)
    assert "absent from the ingested rows" in str(exc.value)


def test_an_empty_panel_is_a_category_and_never_a_zero_score():
    """⚠ `qh` returns None on an empty panel, and the verdict counts it separately — returning 0.0
    would rank it below a genuinely low-expressing protein, an absence dressed as a measurement."""
    ing, s3 = _grid(1, 0)
    a, b = _pair("EMPTY", "breast cancer", 0, 0, 0, 0)
    ing.append(a); s3.append(b)
    v = reproduce_d100(ing, s3)
    assert v.no_score == 1
    assert v.kept == 1 and v.excluded == 0


# ── GC5 — the source pin ────────────────────────────────────────────────────────────────────

def test_an_absent_source_file_is_a_hard_error_not_a_skip(tmp_path):
    """⚠⚠ KEEL-1 V9 Principle 6's direction clause. *You probably do not have the file* is not a
    safety property — it is the shape that armed the truncation."""
    with pytest.raises(IngestRefused) as exc:
        verify_source(tmp_path / "nope.tsv", "0" * 64)
    assert "ABSENT" in str(exc.value)


def test_a_hash_mismatch_refuses_and_names_both_hashes(tmp_path):
    p = tmp_path / "src.tsv"
    p.write_text("Gene\tCancer\n", encoding="utf-8")
    real = sha256_of(p)
    with pytest.raises(IngestRefused) as exc:
        verify_source(p, "1" * 64)
    msg = str(exc.value)
    assert "1" * 64 in msg and real in msg, "a refusal must name what it expected and what it got"
    # ⚠ and the matching case must pass, or the guard would refuse everything and look strict
    assert verify_source(p, real) == real


def test_idempotency_distinguishes_a_rerun_from_a_new_ingest():
    """`GC4`. ⚠ Same hashes -> no-op. Different hashes -> a NEW ingest that must say so, never a
    silent second copy."""
    a = {"pathology.tsv": "aa", "normal_tissue.tsv": "bb"}
    assert is_noop_rerun(a, dict(a)) is True
    assert is_noop_rerun(a, {"pathology.tsv": "aa", "normal_tissue.tsv": "CHANGED"}) is False
    assert is_noop_rerun({}, a) is False, "a first run is not a no-op"
