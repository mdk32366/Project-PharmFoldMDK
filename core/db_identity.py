"""D-159 — every campaign write asks the database which database it is, BEFORE it writes.

⚠⚠ **WHY THIS EXISTS, AND WHY IT IS NOT `D-158` AGAIN.** `D-158` stops the *test suite* truncating a
database it should not touch. It does nothing whatever for the *campaign scripts*: each of
`task4_slice1.py`, `task4_slice2.py`, `task4_slice3.py` and `task3_run2_folds.py` builds its own
engine from `DATABASE_URL` and **writes without ever asking what it is holding.**

⚠ Conflating the two hazards is not a hypothetical failure — it is the recorded one. This check was
*called for twice and endorsed twice* across 2026-08-17 and 2026-09-13 and **never landed**, because
every time it came up it looked like a duplicate of the guard that was already being written. Two
hazards, two vectors, two guards.

## ⚠⚠ The population floor answers the wrong question on its own

A count of census rows asks *"is this a real database?"*. It cannot ask *"is this the RIGHT one?"* —
and the incident turned on the second question:

**The old cluster `zp2wjrej9lwodn4q` is a production database holding the same population.** It was
kept deliberately, as the forensic record of 2026-09-13, and it satisfies **any** population floor
and contains **every** anchor row, because the live cluster was restored *from its backup*. A
check built only on population would wave an enqueue straight into the forensic record.

⚠ **And this was not theoretical: until 2026-09-15 `.env` set `MPG_CLUSTER=zp2wjrej9lwodn4q`** —
corrected to `kyzl60xz9zyrpj9g` that day, and verified: `.env` now holds **zero** references to the
forensic cluster. ⚠ The hazard is recorded in the past tense ON PURPOSE rather than deleted: it is
why this check exists, and a guard whose stated reason has been edited away is a guard someone
later argues is redundant. The single
artefact most likely to point a tunnel at the wrong cluster is the one a population check cannot
see. So identity is asked **first**, and the floor second.

## The two assertions

1. **Cluster identity** — the target carries `keel_live_cluster` naming `LIVE_CLUSTER_ID`. Written
   **once, by the owner, to the live cluster only**, by `scripts/keel_mark_live_cluster.py`. The
   forensic cluster's backup predates that write, so the forensic cluster cannot have it.
2. **Population floor** — `count(protein_analyses WHERE cohort_tranche > 0) >= 3400`, plus a named
   anchor row. ⚠ **A floor, never an equality.** The campaign moves these numbers by design, and a
   stale equality is a check that gets commented out the first time it is wrong — which is how a
   guard becomes a comment.

⚠ **`verify()` is pure**, so every property below is asserted without owning a database. A guard
nobody can test is a guard nobody can trust.
"""

from __future__ import annotations

from dataclasses import dataclass

#: ⚠ The live cluster, restored 2026-09-14 from `backup_1789312967_d0f89bdd9e16aed5`.
LIVE_CLUSTER_ID = "kyzl60xz9zyrpj9g"

#: ⚠⚠ The forensic record of the 2026-09-13 truncation. **DO NOT DESTROY. DO NOT CONNECT FOR
#: CONVENIENCE.** Named here so the refusal can say *which* wrong database it is looking at, which
#: is the difference between a developer fixing `.env` and a developer retrying.
FORENSIC_CLUSTER_ID = "zp2wjrej9lwodn4q"

#: The table the owner writes to the live cluster. ⚠ Created by NO migration, for the reason
#: `A-031` records of its sibling: a migration would place it in every database the chain touches.
LIVE_MARKER_TABLE = "keel_live_cluster"

#: ⚠ A FLOOR, not a count. The census stood at 3,467 manifest rows / 3,463 folded when this landed;
#: 3,400 clears a truncated, empty or freshly created database by a wide margin and does not have to
#: be revised every time the campaign writes a row.
CENSUS_FLOOR = 3400

#: ⚠ A named anchor predating the campaign: GABBR2, rank 1 of the live structural order (0.8443,
#: read live 2026-09-09, `D-146`/`D-147`). A `run: 1` census row, and the row a reader trusts most.
ANCHOR_ACCESSION = "O75899"


class WrongDatabase(RuntimeError):
    """Raised BEFORE any write when the target is not the live campaign database."""


@dataclass(frozen=True)
class Identity:
    """What the target says about itself. ⚠ `live_cluster is None` means the marker table is
    absent, which is what a fresh, restored, or forensic database looks like."""

    live_cluster: str | None
    census_rows: int
    anchor_present: bool


def verify(identity: Identity) -> None:
    """Raise `WrongDatabase` unless `identity` is the live campaign database. Pure.

    ⚠ **Identity is checked FIRST, deliberately.** The forensic cluster passes the population
    clauses, so asking the population first would mean the most dangerous wrong target is the one
    you are told about last — and a refusal that leads with *"3,467 rows found"* reads like success.
    """
    if identity.live_cluster is None:
        raise WrongDatabase(
            f"REFUSING TO WRITE: the target carries no {LIVE_MARKER_TABLE!r} marker, so it is not "
            f"the live campaign database.\n"
            f"  This is what a restored, a fresh, or the FORENSIC cluster looks like. The forensic "
            f"cluster {FORENSIC_CLUSTER_ID!r} holds the same census population and would satisfy "
            f"every other check on this page.\n"
            f"  Check MPG_CLUSTER in your environment before retrying - it pointed at "
            f"{FORENSIC_CLUSTER_ID!r} for the whole of the 2026-09-13 incident and after it.\n"
            f"  The live cluster is marked once, by the owner, with "
            f"`python scripts/keel_mark_live_cluster.py`."
        )
    if identity.live_cluster != LIVE_CLUSTER_ID:
        extra = (" - that is the FORENSIC cluster, kept as the record of the 2026-09-13 truncation."
                 " Do not write to it and do not destroy it."
                 if identity.live_cluster == FORENSIC_CLUSTER_ID else "")
        raise WrongDatabase(
            f"REFUSING TO WRITE: the target names itself {identity.live_cluster!r}, not "
            f"{LIVE_CLUSTER_ID!r}{extra}"
        )
    if identity.census_rows < CENSUS_FLOOR:
        raise WrongDatabase(
            f"REFUSING TO WRITE: {identity.census_rows} census rows, below the floor of "
            f"{CENSUS_FLOOR}.\n"
            f"  A truncated or partially restored database looks exactly like this. On 2026-09-13 "
            f"this count went to 1.\n"
            f"  ⚠ The marker says this IS the live cluster, so a low count here is not a wrong "
            f"target - it is a DAMAGED one. Do not write. Reconcile first."
        )
    if not identity.anchor_present:
        raise WrongDatabase(
            f"REFUSING TO WRITE: the anchor row {ANCHOR_ACCESSION!r} is absent. The population "
            f"clears the floor without the one row that is supposed to predate the whole campaign, "
            f"so the target holds a different population than this campaign was enumerated against."
        )


def read_identity(conn) -> Identity:
    """Read `Identity` off a live connection. ⚠ Reads only — no DDL, no DML, no transaction."""
    from sqlalchemy import text                                   # noqa: PLC0415

    marker = conn.execute(
        text("SELECT to_regclass(:t)"), {"t": LIVE_MARKER_TABLE}).scalar()
    cluster = None
    if marker is not None:
        cluster = conn.execute(
            text(f"SELECT cluster_id FROM {LIVE_MARKER_TABLE} LIMIT 1")).scalar()

    rows = conn.execute(text(
        "SELECT count(*) FROM protein_analyses WHERE cohort_tranche > 0")).scalar() or 0
    # ⚠ The accession lives in `input_value` (`input_type = 'uniprot'`), NOT in a column called
    # `accession` — `protein_analyses` has no such column, and `scripts/task3_run2_folds.py`'s
    # `_existing_run2` matches on `input_value` for the same reason. A guard that queried the
    # obvious-sounding name would have raised on every call and been "fixed" by deleting it.
    anchor = conn.execute(
        text("SELECT 1 FROM protein_analyses WHERE input_value = :a LIMIT 1"),
        {"a": ANCHOR_ACCESSION}).scalar() is not None
    return Identity(live_cluster=cluster, census_rows=int(rows), anchor_present=anchor)


def assert_campaign_target(conn) -> None:
    """⚠⚠ **Call this before the first write of any campaign script.** Reads, then verifies, then
    returns — or raises `WrongDatabase` having written nothing."""
    verify(read_identity(conn))
