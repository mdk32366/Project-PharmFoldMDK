"""D-166 — enqueue idempotency is a DATABASE constraint, not something the application remembers.

⚠⚠ **`F-077`'s three duplicates were written with the guard present, type-correct and five hours
old.** `core.hold48._emitted_tile_idents` reads, decides, then writes, with no lock between — and
two enqueue transactions overlapped. Proven from `jobs.id`, a non-transactional sequence:
transaction A took 3673-3692, B took **3693**, then A took **3694** and **3697**.

⚠ **The tests below are STRUCTURAL and they say so.** A concurrency defect cannot be reproduced on
SQLite in-process, and asserting the Postgres constraint's behaviour against a substrate that does
not carry it is `F-056`'s class — the mistake this file exists to stop repeating. What is asserted
here is that the constraint is DECLARED, that the migration refuses rather than crashes when it
cannot build, and that the entry does not claim more than it landed.
"""

from __future__ import annotations

import ast
import pathlib
import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
MIGRATION = REPO / "db" / "migrations" / "versions" / "0014_enqueue_identity_unique.py"
DECISIONS = (REPO / "docs" / "decisions.md").read_text(encoding="utf-8")
FINDINGS = (REPO / "docs" / "findings.md").read_text(encoding="utf-8")
RESERVED = (REPO / "docs" / "RESERVED.md").read_text(encoding="utf-8")


def test_the_migration_exists_and_chains_onto_the_current_head():
    """⚠ A migration that does not chain is a migration that never runs."""
    assert MIGRATION.is_file(), "D-166's constraint has no migration"
    src = MIGRATION.read_text(encoding="utf-8")
    assert 'revision: str = "0014_enqueue_identity_unique"' in src
    assert 'down_revision: Union[str, None] = "0013_cancer_burden"' in src


def test_the_index_is_UNIQUE_and_PARTIAL_over_the_tile_identity():
    """⚠⚠ Unique is the whole point; partial is what keeps it off every non-tile job.

    A non-partial index would collapse every job whose settings lack the keys into one NULL/NULL
    identity and refuse the second ordinary enqueue in the project.
    """
    src = MIGRATION.read_text(encoding="utf-8")
    assert "unique=True" in src, "the index is not UNIQUE, which is the entire mechanism"
    assert "postgresql_where" in src, (
        "the index is not PARTIAL — it would constrain every job that carries no tile keys")
    assert "inference_settings->>'parent_job_id'" in src
    assert "inference_settings->>'tile_index'" in src


def test_the_migration_REFUSES_with_the_offending_rows_named():
    """⚠⚠ `F-077`'s duplicates are still in production, so this migration CANNOT build there yet.

    Postgres would refuse it anyway with `duplicate key value violates unique constraint` — which
    names the constraint and not the rows. `D-162` rule 7: a probe states what it would return if
    the thing were not so. Here that means naming what to collapse.
    """
    src = MIGRATION.read_text(encoding="utf-8")
    assert "HAVING COUNT(*) > 1" in src, "the migration does not look before it builds"
    assert "REFUSING to build" in src
    assert "OWNER AT THE KEYBOARD" in src, (
        "the refusal does not say who is allowed to fix it — F-075 gates the collapse")
    tree = ast.parse(src)
    fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "upgrade")
    raises = [n for n in ast.walk(fn) if isinstance(n, ast.Raise)]
    assert raises, "upgrade() does not refuse; it would emit a bare integrity error instead"


def test_the_entry_does_NOT_claim_the_run2_path_is_constrained():
    """⚠⚠ THE OVER-CLAIM GUARD, and it is the one most likely to rot.

    The Run-2 identity is `(protein_analyses.input_value, jobs.inference_settings->>'run')` — two
    tables. No single-table index expresses it, `0014` does not constrain it, and an entry that
    implied otherwise would leave a live read-then-write behind a claim of safety.
    """
    src = MIGRATION.read_text(encoding="utf-8")
    assert "Run-2 identity is NOT constrained here" in src
    body = DECISIONS.split("### D-166", 1)[1].split("\n### D-165", 1)[0]
    assert "NOT expressible as a single-table constraint" in body
    assert "pg_advisory_xact_lock" in body, (
        "the interim mitigation for the unconstrained path is not named")


def test_the_entry_records_that_CI_cannot_certify_this_migration():
    """⚠ `F-056`'s class: `alembic upgrade head` runs against a FRESH container in CI, which has no
    duplicates, so the index builds there whether or not production could take it."""
    body = DECISIONS.split("### D-166", 1)[1].split("\n### D-165", 1)[0]
    assert "F-056" in body, "the entry does not name the class of its own green gate"
    assert "release_command" in body, (
        "the entry does not establish that no deploy applies this silently")
    gate = (REPO / ".github" / "workflows" / "gate.yml").read_text(encoding="utf-8")
    assert "alembic upgrade head" in gate, (
        "the premise of the F-056 note is stale — CI no longer migrates")


def test_F077_amendment_1_corrects_the_cause_and_keeps_the_superseded_text():
    """⚠⚠ `F-077` §3 read a FOLD-QUEUE separation as an EMITTER separation.

    The pairs completed ~2 h 57 m apart because one GPU drained 20 folds between the batches. The
    enqueues were 2 m 26 s apart. `D-129-C`: the superseded text is recorded, not overwritten.
    """
    body = FINDINGS.split("### F-077", 1)[1].split("\n### F-078", 1)[0]
    assert "amendment 1" in body, "F-077 carries no amendment"
    assert "a re-run of a wave, not three independent retries" in body, (
        "the superseded claim was overwritten rather than recorded — D-129-C")
    assert "2 m 26 s" in body, "the corrected separation is not stated"
    assert "3694" in body and "3697" in body, (
        "the id interleaving is the proof and it is not in the amendment")


def test_the_headline_leads_with_determinism_not_with_the_duplicates():
    """⚠ The duplicates are how it was learned; the determinism is what was learned."""
    head = FINDINGS.split("### F-077 — ", 1)[1].split("\n", 1)[0]
    assert head.index("deterministic") < head.index("duplicated"), (
        "F-077's headline still leads with the defect rather than the finding")


def test_the_pointer_moved_in_this_commit_and_166_is_named_not_barred():
    """⚠⚠ The allocator discipline: the pointer moves in the SAME commit that spends the integer,
    and every next-free guard names the spent integer rather than relaxing to a `>=`."""
    assert "Next free `D-` integer: **`D-167`**" in RESERVED
    assert "it read **`D-166`**" in RESERVED, (
        "the superseded pointer value was overwritten in silence — D-129-C")
    assert "| **D-166** |" in RESERVED, "D-166 has no row in the allocator"
    assert re.search(r"^### D-166 — ", DECISIONS, re.M), "D-166 is pointed at but unwritten"

    # ⚠⚠ The needles are SPLIT and this file EXCLUDES ITSELF. A guard whose own source
    # satisfies the thing it bars passes for the wrong reason — `D-145`'s class, and it has
    # already been caught three times in this repository on exactly this shape.
    bar = "166 not in" + " ids"
    relaxed = (">" + "= 166", ">" + "=166")
    named = 0
    for p in sorted((REPO / "tests").glob("test_*.py")):
        if p.name == pathlib.Path(__file__).name:
            continue
        text = p.read_text(encoding="utf-8")
        if "not in ids" not in text:
            continue
        assert bar not in text, f"{p.name} still bars 166, which D-166 has spent"
        for r in relaxed:
            assert r not in text, (
                f"{p.name} relaxed a next-free bar to a `>=` — never do this")
        named += 1
    # ⚠ MEASURED, not guessed: 9 test files carry an id-set guard (7 D-numbered plus
    # `test_adc_catalog` and `test_f021_fill_feature_7`, whose `not in ids` is unrelated).
    # A floor below the measured count would let a file silently drop out of the sweep.
    assert named == 9, f"{named} files carry an id-set guard, expected 9 — the sweep moved"

    # ⚠⚠ The pointer assertion is the one that actually fails a stale widening: every file
    # that names the next-free integer must name the SAME one, or two guards disagree about
    # what is free and the disagreement is invisible until an entry lands on it.
    # ⚠ EXCLUDES ITSELF, for the second time in this function — this file names the pointer
    # in its own assertion text, so an unfiltered scan counts the guard as one of the guarded.
    needle = "Next free `D-`" + " integer"
    pointer = [q for q in sorted((REPO / "tests").glob("test_*.py"))
               if q.name != pathlib.Path(__file__).name
               and needle in q.read_text(encoding="utf-8")]
    assert len(pointer) == 9, f"{len(pointer)} files pin the D- pointer, expected 9"
    for q in pointer:
        text = q.read_text(encoding="utf-8")
        assert needle + ": **`D-167`**" in text, (
            f"{q.name} still pins the pointer at a spent integer")
