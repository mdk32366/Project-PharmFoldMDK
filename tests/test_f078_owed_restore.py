"""F-078 amendment 1 — the owed restore of slice 2's 37 cannot be silently dropped.

⚠⚠ **WHY THIS IS A TEST AND NOT A NOTE.** Order B set jobs 4869–4905 to tier `NULL` so slice 3's
1,097 could be the only claimable population. That is the cheap ordering — 74 writes against 2,194 —
and it buys that saving with **an asymmetric failure mode**:

| ordering | if the restore is forgotten |
|---|---|
| A (repair first) | the campaign visibly stalls — 1,097 rows unclaimable, impossible to miss |
| **B (slice 3 first)** | **silent.** A NULL-tier job is claimable by nobody, `refuse_on_strangers` deliberately does not count one, and slice 2 stays 480/517 for ever |

⚠ **Nothing else in this system will ever raise its hand about those rows.** That is precisely the
shape `F-078` exists to record — a loss no check is looking at — so the mitigation cannot itself be
a thing someone has to remember to look at.

⚠ The notice is printed by `--report`, the command run at the moment the fold ends. This asserts it
is still wired in, still names the concrete steps, and still names the rows.

**Delete this test only when slice 2 reads 517/517.** Its removal is the record that the debt was
paid, and it should be removed in the same commit that pays it.
"""

from __future__ import annotations

import inspect
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def test_the_report_prints_the_owed_restore():
    """⚠ A reminder that is not on the path the operator walks is not a reminder."""
    import scripts.task4_slice3 as s3

    src = inspect.getsource(s3.report)
    assert "owed_restore_notice()" in src, (
        "`--report` no longer prints the owed restore. That notice is the ONLY thing watching "
        "slice 2's 37 NULL-tiered rows — the stranger guard does not count them by design.")


def test_the_notice_names_the_rows_and_what_NOT_to_do():
    """⚠ 'Something is owed' is not actionable at 2 a.m. after a ten-hour fold. The row range and
    what done looks like have to be in the text itself.

    ⚠⚠ `F-078` amendment 2 changed WHAT the notice must say. It used to be pinned to the restore
    and re-fold steps — and following them would have overwritten 37 verified artifacts. It is
    now pinned to the prohibition, so a later edit cannot quietly restore the old steps."""
    import scripts.task4_slice3 as s3

    text = "\n".join(s3.OWED_RESTORE)
    assert "4869" in text and "4905" in text, "the notice does not name the rows"
    assert "517/517" in text, "the notice does not say what done looks like"
    assert "F-078 amendments 1 and 2" in text, "the notice does not cite the amendment that governs"
    assert "DO NOT RE-FOLD" in text, "the notice no longer forbids the re-fold"
    assert "--restore" in text, "the notice does not name the command that must not run"
    assert "f078_identity_check.py" in text, "the notice does not name the evidence"
    assert "tier NULL -> 'local'" not in text, (
        "the superseded restore step is back in the notice — following it destroys the evidence")


def test_restore_refuses_even_for_the_owner():
    """⚠⚠ `F-078` amendment 2 §4. `--restore` leads to a re-fold, and a re-fold overwrites the 37
    artifacts in place. The script refuses BEFORE it builds an engine, so the refusal cannot depend
    on a tunnel being up. ⚠ The URL below points at nothing: if the refusal moved after the connect,
    this would raise instead of returning 1."""
    import scripts.f078_null_tier_the_37 as f

    url = "postgresql://nobody@127.0.0.1:1/nothing"
    assert f.main(["--url", url, "--restore"]) == 1
    assert f.main(["--url", url, "--restore", "--i-am-the-owner"]) == 1


def test_the_notice_explains_why_nothing_else_will_catch_it():
    """⚠⚠ The load-bearing sentence. Without it a later reader deletes the notice as noise,
    because a NULL-tier row looks like a deliberate hold rather than a debt."""
    import scripts.task4_slice3 as s3

    text = " ".join(s3.OWED_RESTORE).lower()
    assert "claimed by nobody" in text
    assert "stranger guard does not count" in text
