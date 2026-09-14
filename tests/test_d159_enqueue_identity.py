"""D-159 — every campaign write asks the database which database it is, before it writes.

⚠⚠ **THIS IS NOT `D-158` AGAIN, AND THE PROJECT HAS ALREADY PAID FOR TREATING IT AS THOUGH IT WERE.**
`D-158` guards the *test suite*. The campaign scripts never consult it: each builds its own engine
from `DATABASE_URL` and writes. This check was **called for twice and endorsed twice** across
2026-08-17 and 2026-09-13 and **never landed**, because every time it came up it looked like a
duplicate of the guard already being written. Two hazards, two vectors, two guards.

⚠⚠ **THE ASSERTION THAT CARRIES THIS FILE IS `test_the_forensic_cluster_passes_every_population_
check_and_is_still_refused`.** The old cluster `zp2wjrej9lwodn4q` holds the same census population —
the live cluster was restored *from its backup* — so it satisfies **any** floor and contains **every**
anchor row. A check built only on population would wave an enqueue straight into the forensic
record. ⚠ And until 2026-09-15 `.env` set `MPG_CLUSTER=zp2wjrej9lwodn4q`, so the artefact most likely to point
a tunnel at the wrong cluster is the one a population check cannot see.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from core.db_identity import (
    ANCHOR_ACCESSION,
    CENSUS_FLOOR,
    FORENSIC_CLUSTER_ID,
    LIVE_CLUSTER_ID,
    LIVE_MARKER_TABLE,
    Identity,
    WrongDatabase,
    assert_campaign_target,
    verify,
)

REPO = Path(__file__).resolve().parent.parent

#: The live campaign database, as it should answer.
GOOD = Identity(live_cluster=LIVE_CLUSTER_ID, census_rows=3467, anchor_present=True)

#: ⚠ Every script that builds an engine and writes. A fourth copy in a fourth script is `F-046`.
ENQUEUE_SCRIPTS = (
    "scripts/task4_slice1.py",
    "scripts/task4_slice2.py",
    "scripts/task4_slice3.py",
    "scripts/task3_run2_folds.py",
)


def test_the_live_database_is_accepted():
    verify(GOOD)  # must not raise


# ── ⚠⚠ the assertion this entry exists for ──────────────────────────────────────────────────────

def test_the_forensic_cluster_passes_every_population_check_and_is_still_refused():
    """⚠⚠ **THE CASE A POPULATION FLOOR CANNOT SEE.** `zp2wjrej9lwodn4q` is a production database
    of the same population, kept deliberately as the forensic record of 2026-09-13.

    ⚠ Note what this fixture asserts: **the floor passes and the anchor is present.** Only identity
    fails. A guard built on the floor alone would return *permitted* here, and the enqueue would
    land in the forensic record — destroying the evidence of the incident that produced the guard.
    """
    forensic = Identity(live_cluster=FORENSIC_CLUSTER_ID, census_rows=4535, anchor_present=True)
    with pytest.raises(WrongDatabase) as e:
        verify(forensic)
    assert FORENSIC_CLUSTER_ID in str(e.value)
    assert "forensic" in str(e.value).lower(), (
        "the refusal must say WHICH wrong database this is — that is the difference between a "
        "developer fixing MPG_CLUSTER and a developer retrying")


def test_identity_is_asked_BEFORE_the_population():
    """⚠ Order is not cosmetic. A database with no marker and a healthy population must be refused
    ON IDENTITY: a refusal that leads with *3,467 rows found* reads like success, and the most
    dangerous wrong target would be the one reported last."""
    unmarked_but_full = Identity(live_cluster=None, census_rows=99999, anchor_present=True)
    with pytest.raises(WrongDatabase) as e:
        verify(unmarked_but_full)
    assert LIVE_MARKER_TABLE in str(e.value)
    assert "below the floor" not in str(e.value)


def test_an_unmarked_database_names_MPG_CLUSTER_as_the_thing_to_check():
    """⚠ The refusal points at the artefact that is actually wrong. `.env` carried the forensic
    cluster id through the whole incident and still does."""
    with pytest.raises(WrongDatabase) as e:
        verify(Identity(live_cluster=None, census_rows=3467, anchor_present=True))
    assert "MPG_CLUSTER" in str(e.value)


# ── the population clauses ──────────────────────────────────────────────────────────────────────

def test_a_truncated_database_is_refused_even_though_it_IS_the_live_cluster():
    """⚠⚠ The 2026-09-13 shape: the right cluster, holding one row. The marker says this really is
    the live database, so a low count is not a wrong target — it is a DAMAGED one, and the refusal
    has to say so rather than sending the operator to fix their environment."""
    with pytest.raises(WrongDatabase) as e:
        verify(Identity(live_cluster=LIVE_CLUSTER_ID, census_rows=1, anchor_present=False))
    assert "below the floor" in str(e.value)
    assert "DAMAGED" in str(e.value)


def test_the_floor_is_a_floor_and_not_an_equality():
    """⚠ The campaign moves these numbers by design. A stale equality is a check that gets
    commented out the first time it is wrong — which is how a guard becomes a comment."""
    verify(Identity(LIVE_CLUSTER_ID, CENSUS_FLOOR, True))
    verify(Identity(LIVE_CLUSTER_ID, CENSUS_FLOOR + 50_000, True))
    with pytest.raises(WrongDatabase):
        verify(Identity(LIVE_CLUSTER_ID, CENSUS_FLOOR - 1, True))


def test_a_populated_database_missing_the_anchor_is_a_different_population():
    with pytest.raises(WrongDatabase) as e:
        verify(Identity(LIVE_CLUSTER_ID, 9000, anchor_present=False))
    assert ANCHOR_ACCESSION in str(e.value)


# ── ⚠⚠ the raise happens BEFORE any write ───────────────────────────────────────────────────────

class RecordingConn:
    """A connection double that records every statement and can answer the identity probe.

    ⚠ It is deliberately not a mock library object: the assertion below is *nothing was written*,
    and that is worth reading literally in the test rather than through a framework's API.
    """

    def __init__(self, marker, rows, anchor):
        self.marker, self.rows, self.anchor = marker, rows, anchor
        self.statements: list[str] = []

    def execute(self, stmt, params=None):
        sql = str(stmt)
        self.statements.append(sql)
        if "to_regclass" in sql:
            return _Scalar(LIVE_MARKER_TABLE if self.marker else None)
        if "cluster_id" in sql:
            return _Scalar(self.marker)
        if "count(*)" in sql:
            return _Scalar(self.rows)
        return _Scalar(1 if self.anchor else None)


class _Scalar:
    def __init__(self, v):
        self._v = v

    def scalar(self):
        return self._v


def test_nothing_is_written_before_the_refusal():
    """⚠⚠ **A test proving only the raise does not discharge this.** The whole point is that the
    refusal arrives before the first `INSERT`, so the assertion is over what the connection was
    ASKED, not merely over the exception."""
    conn = RecordingConn(marker=None, rows=1, anchor=False)
    with pytest.raises(WrongDatabase):
        assert_campaign_target(conn)
    written = [s for s in conn.statements
               if re.search(r"\b(insert|update|delete|truncate|drop|alter)\b", s, re.I)]
    assert not written, f"the guard wrote before it refused: {written}"
    assert conn.statements, "the guard refused without asking the database anything"


def test_the_happy_path_also_writes_nothing():
    conn = RecordingConn(marker=LIVE_CLUSTER_ID, rows=3467, anchor=True)
    assert_campaign_target(conn)
    assert not [s for s in conn.statements if re.search(r"\binsert\b", s, re.I)]


def test_the_anchor_is_read_from_input_value_and_not_from_a_column_that_does_not_exist():
    """⚠ `protein_analyses` has NO `accession` column — the UniProt accession lives in
    `input_value`, which is how `_existing_run2` matches it. A guard that queried the
    obvious-sounding name would have raised on every call and been 'fixed' by deletion."""
    conn = RecordingConn(marker=LIVE_CLUSTER_ID, rows=3467, anchor=True)
    assert_campaign_target(conn)
    anchor_sql = [s for s in conn.statements if ANCHOR_ACCESSION in s or "input_value" in s]
    assert anchor_sql, "the anchor was never queried"
    assert not any("census_accession" in s for s in conn.statements)


# ── ⚠ one home, every caller (F-046) ────────────────────────────────────────────────────────────

def test_every_enqueue_script_calls_the_check_before_it_writes():
    """⚠⚠ **`F-046`'s defect class, refused in advance.** Four scripts each build an engine and
    write. The check lives in ONE module and each script calls it; a fourth copy in a fourth script
    is how three straddle predicates ended up under one name.

    ⚠ The ordering assertion is the substance: the call must come before the first mutation in the
    same function, or it is decoration.
    """
    for rel in ENQUEUE_SCRIPTS:
        text = (REPO / rel).read_text(encoding="utf-8")
        assert "from core.db_identity import" in text, f"{rel} does not import the check"
        assert "assert_campaign_target" in text, f"{rel} never calls the check"
        call = text.index("assert_campaign_target(")
        # the first thing any of these scripts does to write is `s.add(` / `s.add_all(`
        adds = [m.start() for m in re.finditer(r"\bs\.add(_all)?\(", text)]
        assert adds, f"{rel} has no write site — the wiring assumption is wrong, re-read it"
        assert call < min(adds), (
            f"{rel} calls the identity check AFTER its first write — the check must refuse before "
            f"anything lands, not report afterwards")


def test_the_check_has_exactly_one_home():
    """⚠ No second copy of the floor, the anchor or the cluster id anywhere in the campaign
    scripts. Two paths to one quantity is the defect this project has catalogued ten times."""
    for rel in ENQUEUE_SCRIPTS:
        text = (REPO / rel).read_text(encoding="utf-8")
        assert str(CENSUS_FLOOR) not in text, f"{rel} restates the census floor"
        assert LIVE_CLUSTER_ID not in text, f"{rel} restates the live cluster id"


def test_no_migration_creates_the_live_marker():
    """⚠ Same condition as `A-031`'s, for the same reason and with the opposite polarity: this
    marker must exist ONLY on the live cluster, so the schema chain must never place it."""
    versions = sorted((REPO / "db" / "migrations" / "versions").glob("*.py"))
    assert versions
    offenders = [p.name for p in versions if LIVE_MARKER_TABLE in p.read_text(encoding="utf-8")]
    assert not offenders, f"{offenders} would put the live marker into every database it upgrades"


def test_the_live_marker_has_an_owner_run_bootstrap():
    """⚠⚠ The marker has to be WRITTEN to the live cluster, and that is a production write — so it
    is an owner step with the owner at the keyboard, not something a script does on the way past.
    ⚠ Until it runs, this guard fails closed and every enqueue is refused. That is the correct
    direction, and it is why the bootstrap is part of this entry rather than an afterthought."""
    boot = REPO / "scripts" / "keel_mark_live_cluster.py"
    assert boot.is_file(), "nothing can mark the live cluster, so every enqueue would be refused"
    text = boot.read_text(encoding="utf-8")
    assert "from core.db_identity import" in text, "the bootstrap restates the marker name"
    assert "i-am-the-owner" in text, "a production write with no owner gate"
