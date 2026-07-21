"""REAL coverage — the reaping *decision* is a pure predicate that ships in prod.

``is_stale`` runs no SQL and holds no concurrency, so these assertions are genuine
coverage of production code, not shape. The boundary is DECIDED, not incidental:
strict ``age > timeout``. Exactly-at-threshold is not yet stale.
"""

from datetime import datetime, timedelta, timezone

from core.queue import DEFAULT_STALE_SECONDS, is_stale

BASE = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)


def _now(**kw):
    return BASE + timedelta(**kw)


def test_default_threshold_is_thirty_minutes():
    # 30 min is stated in D-009 §1, so this constant is faithful, not invented.
    assert DEFAULT_STALE_SECONDS == 1800


def test_below_threshold_is_not_stale():
    assert is_stale(BASE, _now(minutes=29, seconds=59)) is False


def test_exactly_at_threshold_is_not_stale():
    # 30:00.000 — the decided edge. "Older than 30 minutes" means age must EXCEED
    # the threshold, so the exact boundary is not yet stale. Strict `>`.
    assert is_stale(BASE, _now(minutes=30)) is False


def test_just_over_threshold_is_stale():
    assert is_stale(BASE, _now(minutes=30, seconds=1)) is True


def test_never_claimed_is_not_stale():
    assert is_stale(None, _now(hours=99)) is False


def test_custom_threshold_is_honored():
    assert is_stale(BASE, _now(seconds=61), timeout_seconds=60) is True
    assert is_stale(BASE, _now(seconds=60), timeout_seconds=60) is False
