"""F-035 — the manifest computes the tier; the claim must ENFORCE it.

⚠⚠ Before this, `claim()` was `WHERE status = 'pending' ORDER BY created_at` — no tier, no length.
The only thing keeping rental work off the local card was that no rental row had ever been ingested:
**an operational convention doing a guard's job.** Tranche 5 is 776 rental rows at 441–14,451 aa
resolving `fp16`, against a card measured at 8,150 MiB with `known_good = 440` at int8 — and an
fp16 overrun is what bugchecked this host on 2026-08-12.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from doubles import UnlockedFakeJobQueue  # noqa: E402

from core.queue import DEFAULT_TIER  # noqa: E402


def test_a_local_worker_cannot_claim_a_rental_job():
    """⚠⚠ THE WHOLE FINDING, in one assertion."""
    q = UnlockedFakeJobQueue()
    q.enqueue(1, tier="rental")
    assert q.claim("local-gpu", tier="local") is None


def test_a_rental_worker_cannot_claim_a_local_job_either():
    """⚠ The filter is symmetric. A rental box quietly draining the local queue would waste rented
    hours on folds the local card already handles — cheaper than a bugcheck, still wrong."""
    q = UnlockedFakeJobQueue()
    q.enqueue(1, tier="local")
    assert q.claim("rental-box", tier="rental") is None


def test_each_worker_gets_its_own_tier():
    q = UnlockedFakeJobQueue()
    local_job = q.enqueue(1, tier="local")
    rental_job = q.enqueue(2, tier="rental")
    assert q.claim("w-local", tier="local").id == local_job
    assert q.claim("w-rental", tier="rental").id == rental_job


def test_an_untagged_job_is_claimable_by_NOBODY():
    """⚠⚠ NOT claimable-by-anyone. `NULL = 'local'` is unknown in SQL, hence false, and that is the
    behaviour we want: `OR tier IS NULL` would look friendly and restore the exact hole — an
    untagged rental job taken by the local worker."""
    q = UnlockedFakeJobQueue()
    q.enqueue(1, tier=None)
    for t in ("local", "rental", "msa", "anything"):
        assert q.claim("w", tier=t) is None


def test_the_default_tier_is_local_because_that_is_the_CHEAP_failure():
    """⚠ Direction matters. Wrongly refusing work costs an idle GPU; wrongly accepting it means
    fp16 at 441+ aa on a card measured to hold 440."""
    assert DEFAULT_TIER == "local"
    q = UnlockedFakeJobQueue()
    q.enqueue(1, tier="rental")
    assert q.claim("w") is None          # no tier given → local → refuses the rental job


def test_fifo_still_holds_within_a_tier():
    """⚠ The filter must not disturb the ordering contract (D-009 §1 Amendment 3)."""
    from datetime import datetime, timezone
    q = UnlockedFakeJobQueue()
    older = q.enqueue(1, tier="local", created_at=datetime(2026, 1, 1, tzinfo=timezone.utc))
    q.enqueue(2, tier="local", created_at=datetime(2026, 1, 2, tzinfo=timezone.utc))
    assert q.claim("w", tier="local").id == older


def test_the_filter_is_in_the_SQL_not_after_the_claim():
    """⚠⚠ A post-claim check marks the job `claimed` and then declines it — the shape that left ten
    jobs permanently stuck with attempts=0, no error and nothing retryable. Asserted over the
    SOURCE, so the guard survives the implementation being rewritten."""
    src = (REPO / "core" / "queue.py").read_text(encoding="utf-8")
    claim_sql = src[src.index("UPDATE jobs SET status = 'claimed'"):]
    claim_sql = claim_sql[: claim_sql.index("RETURNING")]
    # ⚠ Comments stripped first. The first version matched the word "tier IS NULL" in the SQL's own
    # warning comment and failed on correct code — a guard that reads prose is checking the wrong
    # artifact.
    code = " ".join(line.split("--")[0] for line in claim_sql.splitlines())
    assert "tier = :tier" in code, "the tier is not filtered inside the claim statement"
    assert "IS NULL" not in code.upper(), (
        "`OR tier IS NULL` restores F-035 — an untagged rental job becomes claimable by the local "
        "worker")


def test_the_double_enforces_the_same_rule_as_the_sql():
    """⚠ A double that accepted `tier` and ignored it would let every claim test pass while
    production filtered differently — two paths to one behaviour, never compared."""
    src = (REPO / "tests" / "doubles.py").read_text(encoding="utf-8")
    assert "j.tier == tier" in src, "the double does not filter by tier"


@pytest.mark.parametrize("path,needle", [
    ("worker/http_client.py", '"tier": tier'),
    ("worker/main.py", 'WORKER_TIER'),
    ("scripts/census_ingest.py", 'tier=p["tier"]'),
    ("core/enqueue.py", 'tier=row.tier'),
])
def test_the_tier_is_declared_and_written_end_to_end(path, needle):
    """⚠ A filter with nothing writing the column would refuse every job. Both enqueue paths must
    tag, and the worker must declare."""
    assert needle in (REPO / path).read_text(encoding="utf-8"), f"{path} is missing {needle!r}"
