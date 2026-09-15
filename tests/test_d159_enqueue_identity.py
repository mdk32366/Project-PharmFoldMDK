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

# ⚠⚠ F-079. This module used to police a HAND-WRITTEN tuple of four scripts. It named the files
# written before it and nothing written after — not `task4_slice4.py`, and not the one irreversible
# DELETE in the tree, `d166_collapse_duplicate_tiles.py`, which never called the check. The subjects
# are now ENUMERATED from what git tracks: every `scripts/*.py` that carries `--i-am-the-owner` and
# mutates. A new owner-gated writer is policed by existing, not by someone remembering to list it.

from _tracked_sources import tracked_files  # noqa: E402

#: ⚠ Owner-gated writers that do NOT call the check, each with the OWNER's reason. ⚠⚠ An empty
#: reason FAILS the guard: an exception is a ruling, and Code does not invent one (F-079 §3). The
#: four below were found by the enumeration and RULED BY THE OWNER (Matt Kelly) on 2026-09-15.
#: ⚠ Three are TEMPORARY — owed the check, not excused from it.
IDENTITY_CHECK_EXCEPTIONS: dict[str, str] = {
    "scripts/backfill_run_label.py": (
        "TEMPORARY (owner, 2026-09-15): owed assert_campaign_target; exception lasts until a "
        "follow-up PR adds it (F-079 §3)."),
    "scripts/census_ingest_features.py": (
        "TEMPORARY (owner, 2026-09-15): owed assert_campaign_target. It runs on the machine, but "
        "the machine's DATABASE_URL secret is state outside the script and only the marker "
        "detects a wrong cluster; exception lasts until a follow-up PR adds it (F-079 §3)."),
    "scripts/clinical_ingest_edges.py": (
        "TEMPORARY (owner, 2026-09-15): owed assert_campaign_target; exception lasts until a "
        "follow-up PR adds it (F-079 §3)."),
    "scripts/keel_mark_live_cluster.py": (
        "BOOTSTRAP OF THE CHECK (owner, 2026-09-15): writes the keel_live_cluster marker that "
        "assert_campaign_target requires, so the check refuses it by construction until it has "
        "run. The operator's confirmation at the keyboard is the evidence (its docstring)."),
}

#: ⚠ What counts as a mutation, in CODE only (comments and docstrings are blanked first, so prose
#: that says "UPDATE" cannot move the first write). SQL verbs are matched in their statement shape
#: rather than as bare words, because printed messages say "DELETE 3 rows". ⚠ `.commit()` is here
#: on purpose: `backfill_run_label.py` writes by ORM attribute assignment and carries NO SQL verb, so
#: a verb-only detector cannot see it (F-079 §3).
_MUTATION = re.compile(
    r"\bINSERT\s+INTO\b|\bUPDATE\s+[\w.\"]+\s+SET\b|\bDELETE\s+FROM\b|\bTRUNCATE\b"
    r"|\bs\.add(?:_all)?\(|(?<![.\w])(?:insert|update|delete)\(|\.commit\(\)")
_CALL = re.compile(r"(?<!def )\bassert_campaign_target\(")


def _code_only(src: str) -> str:
    """`src` with comments and docstrings replaced by spaces, offsets preserved.

    ⚠ Blanking rather than deleting keeps every index comparable with the original source."""
    import ast
    import io
    import tokenize

    docstrings = set()
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            body = getattr(node, "body", [])
            if (body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant)
                    and isinstance(body[0].value.value, str)):
                docstrings.add((body[0].lineno, body[0].col_offset))
    lines = src.splitlines(keepends=True)
    starts = [0]
    for ln in lines:
        starts.append(starts[-1] + len(ln))
    out = list(src)
    for tok in tokenize.generate_tokens(io.StringIO(src).readline):
        if tok.type == tokenize.COMMENT or (tok.type == tokenize.STRING and tok.start in docstrings):
            a = starts[tok.start[0] - 1] + tok.start[1]
            b = starts[tok.end[0] - 1] + tok.end[1]
            out[a:b] = [ch if ch == "\n" else " " for ch in src[a:b]]
    return "".join(out)


def ordering_violation(src: str) -> str | None:
    """Why `src` fails the rule, or None. Pure, so it can be shown to fail on a synthetic source."""
    code = _code_only(src)
    first = _MUTATION.search(code)
    if first is None:
        return None
    call = _CALL.search(code)
    if call is None:
        return f"mutates ({first.group(0)!r}) and never calls assert_campaign_target"
    if call.start() > first.start():
        return f"mutates ({first.group(0)!r}) BEFORE it calls assert_campaign_target"
    return None


def owner_gated_writers() -> list[str]:
    """Every tracked `scripts/*.py` carrying `--i-am-the-owner` whose code mutates."""
    found = []
    for path in tracked_files(REPO, ["scripts"]):
        src = path.read_text(encoding="utf-8")
        if "--i-am-the-owner" in src and _MUTATION.search(_code_only(src)):
            found.append(path.relative_to(REPO).as_posix())
    return sorted(found)


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

def test_every_owner_gated_writer_calls_the_identity_check_first():
    """⚠⚠ **`F-046`'s defect class, refused in advance — and `F-079`'s, which is the same class one
    level up: the list of subjects was itself a single copy.** Every tracked owner-gated writer
    calls the check before its first mutation, or is a named exception carrying the owner's reason.

    ⚠ The ordering assertion is the substance: the call must come before the first mutation, or it
    is decoration.
    """
    failures = []
    for rel in owner_gated_writers():
        if rel in IDENTITY_CHECK_EXCEPTIONS:
            if not IDENTITY_CHECK_EXCEPTIONS[rel].strip():
                failures.append(f"{rel}: listed as an exception with NO reason - the owner rules it")
            continue
        why = ordering_violation((REPO / rel).read_text(encoding="utf-8"))
        if why:
            failures.append(f"{rel}: {why}")
    assert not failures, "owner-gated writers that do not ask which database first:\n  " + (
        "\n  ".join(failures))


def test_an_exception_names_a_script_that_still_exists_and_still_writes():
    """⚠ An exception for a file that no longer needs one is a hole kept open by habit."""
    writers = set(owner_gated_writers())
    stale = [rel for rel in IDENTITY_CHECK_EXCEPTIONS if rel not in writers]
    assert not stale, f"exceptions for scripts that are gone or no longer write: {stale}"


def test_the_ordering_detector_can_fail():
    """⚠ `F-045`: a detector that cannot be shown to fail proves nothing. Synthetic sources, one per
    outcome, including the two ways prose must NOT count."""
    check = "from core.db_identity import assert_campaign_target\n"
    assert ordering_violation(check + "assert_campaign_target(c)\nc.execute(text('DELETE FROM jobs'))\n") is None
    assert "never calls" in ordering_violation("c.execute(text('DELETE FROM jobs'))\n")
    assert "BEFORE" in ordering_violation(
        check + "s.add(row)\nassert_campaign_target(c)\n")
    assert "BEFORE" in ordering_violation(check + "job.x = 1\ns.commit()\nassert_campaign_target(c)\n")
    # prose is not a write: a docstring and a comment saying the verbs, then the check, then a write
    prose = '"""This UPDATE jobs SET nothing; DELETE FROM x."""\n# INSERT INTO y\n'
    assert ordering_violation(prose + check + "assert_campaign_target(c)\ns.add(r)\n") is None
    # a printed message is not a statement shape
    assert ordering_violation(check + "print(f'DELETE {n} rows')\n") is None


def test_enumeration_is_not_a_hand_list():
    """⚠ F-079: the enumeration reaches a file no hand list ever named, and the list is gone."""
    writers = owner_gated_writers()
    assert "scripts/d166_collapse_duplicate_tiles.py" in writers
    assert "scripts/task4_slice4.py" in writers
    src = Path(__file__).read_text(encoding="utf-8")
    assert ("ENQUEUE_" + "SCRIPTS = (") not in src, "the hand-written tuple is back"


def test_the_check_has_exactly_one_home():
    """⚠ No second copy of the floor, the anchor or the cluster id anywhere in the campaign
    scripts. Two paths to one quantity is the defect this project has catalogued ten times.

    ⚠ Scoped to the writers that CALL the check. `F-079` widened the subjects from a hand list to the
    enumeration, which brought in `keel_mark_live_cluster.py` — the bootstrap that WRITES the marker
    and names the live cluster in its operator warning. A named exception is outside this rule for
    the same reason it is outside the ordering rule: its relation to the check is the owner's ruling.
    """
    for rel in owner_gated_writers():
        if rel in IDENTITY_CHECK_EXCEPTIONS:
            continue
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
