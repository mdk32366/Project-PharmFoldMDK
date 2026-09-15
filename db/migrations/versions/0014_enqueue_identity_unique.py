"""Enqueue idempotency becomes a DATABASE constraint — `D-166`.

⚠⚠ **A read-then-write guard cannot survive concurrency, and `F-077` is the proof.**
`core.hold48._emitted_tile_idents` reads the emitted tile identities, decides, then writes, with no
lock in between. On 2026-09-04 two enqueue transactions **overlapped** — proven by `jobs.id`, a
non-transactional sequence: transaction A took 3673-3692, B took **3693**, then A took **3694** and
**3697**. Under `READ COMMITTED` neither could see the other's uncommitted rows, the guard returned
*"not yet emitted"* in both, and both wrote. The guard was present, type-correct and **five hours
old** (`52ecb61`, 2026-09-04T16:36:54Z).

⚠ **The precedent is `0013`**, which put a `UNIQUE (run_id, statistic, seer_site_id, sex)` on the
burden figures *"so the loader physically cannot do what `F-021` recorded"*. `F-077` is `F-021` in a
different table.

⚠⚠ **THIS MIGRATION CAN GO GREEN IN CI AND STILL FAIL AGAINST PRODUCTION.**
`.github/workflows/gate.yml` runs `alembic upgrade head` against a **fresh** service container,
which has no duplicate rows, so the index builds there unconditionally. That is `F-056`'s class —
the test substrate forgives what production rejects — and it is why `upgrade()` below **looks
first** and raises a message naming the offending rows rather than letting Postgres emit a bare
`duplicate key value violates unique constraint`.

⚠ **Production duplicates must be collapsed by the OWNER first** (`F-075`, `D-166` §5). `F-077`
established every pair is byte-identical, so the collapse destroys no evidence — but it is a
production write and this migration does not perform it.

⚠ **The Run-2 identity is NOT constrained here.** It is
`(protein_analyses.input_value, jobs.inference_settings->>'run')` — two tables — and no
single-table index expresses it. `D-166` §4b records it as owed and undesigned rather than
pretending this migration covers it.

Revision ID: 0014_enqueue_identity_unique
Revises: 0013_cancer_burden
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0014_enqueue_identity_unique"
down_revision: Union[str, None] = "0013_cancer_burden"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

INDEX_NAME = "uq_jobs_hold48_tile_identity"

# ⚠ The pre-check. Postgres would refuse the index anyway; this refuses it with the row ids, so the
# operator is told WHAT to collapse rather than that something is wrong.
_DUPLICATES = sa.text("""
    SELECT inference_settings->>'parent_job_id' AS parent,
           inference_settings->>'tile_index'    AS tile_index,
           array_agg(id ORDER BY id)            AS ids
    FROM jobs
    WHERE inference_settings ? 'tile_index'
      AND inference_settings ? 'parent_job_id'
    GROUP BY 1, 2
    HAVING COUNT(*) > 1
    ORDER BY 1
""")


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        # ⚠ SQLite has no JSONB `?` operator and its JSON1 predicates are not the same predicate
        # (`F-056`). The constraint is a Postgres property and the SQLite substrate does not get a
        # weaker imitation of it — it gets nothing, and the tests name the engine they run on.
        return

    dupes = bind.execute(_DUPLICATES).mappings().all()
    if dupes:
        listed = "; ".join(
            f"parent {d['parent']} tile {d['tile_index']} -> jobs {list(d['ids'])}" for d in dupes)
        raise RuntimeError(
            f"REFUSING to build {INDEX_NAME}: {len(dupes)} duplicate tile identities exist and the "
            f"index cannot be created over them. Collapse them first — OWNER AT THE KEYBOARD "
            f"(F-075, D-166 §5). F-077 measured every pair byte-identical, so either copy is the "
            f"tile and the collapse destroys no evidence. Offending rows: {listed}")

    op.create_index(
        INDEX_NAME, "jobs",
        [sa.text("(inference_settings->>'parent_job_id')"),
         sa.text("(inference_settings->>'tile_index')")],
        unique=True,
        postgresql_where=sa.text("inference_settings ? 'tile_index' "
                                 "AND inference_settings ? 'parent_job_id'"))


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return
    op.drop_index(INDEX_NAME, table_name="jobs")
