"""KEEL V8-a — the properties of the guard that OUTLIVED its mechanism.

⚠⚠ **This file used to test a hostname allowlist. `D-158` deleted that mechanism**, because a
`fly mpg proxy` tunnel presents production at `127.0.0.1` and loopback could not be removed from the
list — the genuinely disposable databases are on loopback too. The positive-identity guard that
replaced it, and the full regression, live in `tests/test_d158_positive_identity_guard.py`.

⚠ **What was removed, recorded rather than left to a diff.** Four assertions went with the
mechanism: that a named production host is refused *because it is not on the list*; that every
entry on the list is allowed; that `CI=true` is permitted unconditionally; and that the override is
the bare sentence `i-know-this-truncates`. ⚠⚠ **The third and fourth were not merely superseded —
they were asserting the two bypasses that sat IN FRONT of the host check**, and `D-158` deletes the
first and binds the second to a named target. A test that pins a hole open is not a test worth
carrying forward.

⚠ **What stays here is what is mechanism-independent**, and each earned its place by catching
something real.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tests"))

from _db_safety import db_host, refusal_reason  # noqa: E402


def _no_marker(url):              # noqa: ARG001
    return False


# ── the parser, which still has a caller ────────────────────────────────────────────────────────

def test_the_host_parser_is_not_fooled_by_a_password_containing_an_at_sign():
    """⚠ A password with `@` in it would otherwise shift the parsed host.

    ⚠⚠ **This survives `D-158` for a stated reason rather than by inertia** (§B.7): the host no
    longer decides anything, but the refusal must still NAME the target it refused, so `db_host`
    has a real caller. Had the rewrite left it callerless, the function and this test would have
    gone together — a test guarding code nothing calls is the defect this project catalogues.
    """
    assert db_host("postgresql://user:p@ss@prod.example.net/db") == "prod.example.net"
    reason = refusal_reason({"DATABASE_URL": "postgresql://user:p@ss@prod.example.net/db"},
                            probe=_no_marker)
    assert reason is not None
    assert "prod.example.net" in reason, "the refusal did not name the host it refused"


def test_an_ipv6_loopback_is_parsed_and_named_rather_than_mangled():
    """⚠ IPv6 arrives bracketed. The bracketed branch is first because alternation is ordered —
    the bare branch matches a lone `[` and yields an empty host."""
    assert db_host("postgresql://u:p@[::1]:5432/db") == "::1"


# ── the secret-hygiene guard, wholly independent of any mechanism ───────────────────────────────

def test_every_env_variant_is_gitignored_not_just_dot_env():
    """⚠⚠ On 2026-08-17 a backup named `.env.env.bak-precluster-swap` was created during a cluster
    swap. It held the OLD production database password and was **not ignored** — one unscoped
    `git add -A` from a public repository.

    The pattern was `.env`, which matches the file called `.env` and nothing else: the narrowest
    possible reading of an intent that was obviously broader. ⚠ `.env.example` must stay tracked,
    so the negation is asserted too — a fix that ignores the template breaks every fresh clone."""
    ignore = (REPO / ".gitignore").read_text(encoding="utf-8")
    assert ".env*" in ignore, "a .env backup or variant would not be ignored"
    assert "!.env.example" in ignore, "the template must stay tracked or a fresh clone has no example"
