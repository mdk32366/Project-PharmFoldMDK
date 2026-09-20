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
    # ⚠ D-167 (the re-attach of slice 2's 37) spent 167 and moved the pointer in its own commit;
    # the pin is MOVED by name, and the superseded D-166 note stays in the chain.
    assert "Next free `D-` integer: **`D-170`**" in RESERVED
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
        assert needle + ": **`D-170`**" in text, (
            f"{q.name} still pins the pointer at a spent integer")


# ── the advisory lock: the INTERIM, and the tests say so in terms ──────────────────────────────

def test_the_lock_is_transaction_scoped_and_never_session_scoped():
    """⚠⚠ `pg_advisory_lock` survives the transaction and is released only by unlock or by the
    session ending. A process that dies holding an enqueue lock would wedge every future enqueue
    until someone went looking. `pg_advisory_xact_lock` is released by COMMIT or ROLLBACK."""
    src = (REPO / "core" / "enqueue_lock.py").read_text(encoding="utf-8")
    assert "pg_advisory_xact_lock" in src
    assert "SELECT pg_advisory_lock(" not in src, (
        "a session-scoped advisory lock can be leaked by a process that dies holding it")


def test_the_lock_reports_FALSE_rather_than_pretending_on_a_substrate_without_it():
    """⚠⚠ `F-056`'s class, which this project has already shipped once: the test substrate must
    not report a protection it does not have. SQLite has no advisory locks."""
    from core.enqueue_lock import RUN2_NAMESPACE, TILE_NAMESPACE, hold_enqueue_lock, lock_key
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session

    with Session(create_engine("sqlite://")) as s:
        assert hold_enqueue_lock(s, TILE_NAMESPACE) is False, (
            "the lock claims to have been taken on an engine that cannot take it")

    # ⚠ Keys are DERIVED from the namespace, never hand-assigned: a hand-assigned integer is a
    # second copy of a constant in the value that decides mutual exclusion (`F-014`'s class).
    assert lock_key(TILE_NAMESPACE) != lock_key(RUN2_NAMESPACE), (
        "two enqueue families collide into one lock and serialise for no reason")
    for ns in (TILE_NAMESPACE, RUN2_NAMESPACE):
        assert -(2 ** 63) <= lock_key(ns) < 2 ** 63, "key does not fit a Postgres bigint"
        assert lock_key(ns) == lock_key(ns), "key is not stable across calls"


def test_BOTH_check_then_write_paths_take_the_lock():
    """⚠ The tile path and the Run-2 path are different code with the same defect. Wiring one and
    not the other would leave the live campaign's path unguarded while reading as fixed."""
    hold48 = (REPO / "core" / "hold48.py").read_text(encoding="utf-8")
    assert "hold_enqueue_lock(session, TILE_NAMESPACE)" in hold48
    assert hold48.index("hold_enqueue_lock(session, TILE_NAMESPACE)") < \
        hold48.index("emitted_indices, emitted_windows = _emitted_tile_idents"), (
        "the lock is taken AFTER the read it is supposed to serialise")

    run2 = (REPO / "scripts" / "task3_run2_folds.py").read_text(encoding="utf-8")
    assert "hold_enqueue_lock(session, RUN2_NAMESPACE)" in run2, (
        "the Run-2 slice enqueues reach their check-then-write unserialised")


def test_the_entry_records_the_lock_as_a_PROCESS_LEVEL_interim():
    """⚠⚠ THE OVER-CLAIM GUARD FOR THE MITIGATION ITSELF.

    A lock is a convention among callers; a constraint is a property of the data. The next enqueue
    path, written by someone who has not read `D-166`, will simply not call it — which is the same
    shape as the check-then-write, one layer up. An entry that presented the lock as the fix would
    make the unconstrained Run-2 path read as safe.
    """
    body = DECISIONS.split("### D-166", 1)[1].split("\n### D-165", 1)[0]
    assert "process-level" in body.lower(), "the entry does not bound what the lock is"
    assert "will simply not call it" in body, (
        "the entry does not name the way the interim fails")
    src = (REPO / "core" / "enqueue_lock.py").read_text(encoding="utf-8")
    assert "NOT a constraint" in src, "the module does not say what it is not"


# ── the collapse: an owner-gated destructive write that re-measures rather than trusts ─────────

def test_the_collapse_REMEASURES_and_does_not_trust_F077():
    """⚠⚠ `F-077` measured byte-identity on 2026-09-15. Acting on a measurement after it stopped
    being checkable is the shape this project keeps paying for — `D-166` exists because a
    completion timestamp was read as an enqueue timestamp. The collapse hashes both artifacts in
    its own run, and a single mismatch refuses everything."""
    src = (REPO / "scripts" / "d166_collapse_duplicate_tiles.py").read_text(encoding="utf-8")
    assert "hashlib.sha256" in src, "the collapse does not hash anything"
    assert "not trusting F-077" in src or "does not trust" in src
    assert "DIFFERENT" in src and "return 1" in src, (
        "a non-identical pair does not stop the run")


def test_the_collapse_deletes_ROWS_and_never_BYTES():
    """⚠ A row can be re-derived from an artifact. An artifact deleted on a guess cannot be
    re-derived from anything."""
    src = (REPO / "scripts" / "d166_collapse_duplicate_tiles.py").read_text(encoding="utf-8")
    assert "DELETE FROM jobs" in src and "DELETE FROM protein_analyses" in src
    for forbidden in ("os.remove", "unlink", "shutil.rmtree", "_remove_files"):
        assert forbidden not in src, f"the collapse deletes bytes via {forbidden}"
    assert "LEFT IN PLACE" in src, "the surviving artifact files are not named"


def test_the_collapse_is_owner_gated_and_refuses_an_unexpected_duplicate_set():
    """⚠ `F-075`: an authenticated session is not an attestation. ⚠⚠ And a FOURTH duplicate is a
    new finding, not something to sweep up in passing — the script refuses rather than widening."""
    src = (REPO / "scripts" / "d166_collapse_duplicate_tiles.py").read_text(encoding="utf-8")
    # ⚠ F-079 moved the gate from a bare `sys.argv` membership test to argparse, so the operator can
    # also name the target (`--url`). The pin moves with it, by name; the gate is not relaxed.
    # Superseded pin, recorded (D-129-C): `'"--i-am-the-owner" in sys.argv' in src`.
    assert '"--i-am-the-owner", dest="owner"' in src
    assert "if not owner:" in src, "the dry run is no longer the default"
    assert "F-075" in src, "the gate does not name the finding that requires it"
    assert "live != EXPECTED" in src, "the script does not check WHICH duplicates it found"
    assert "again != EXPECTED" in src, (
        "the write does not re-check inside its own transaction — the very defect D-166 records")


def test_the_prework_pairs_the_two_owner_writes():
    """⚠ Both are owner writes against the same cluster. Two sittings cost more than one, and the
    second is the one that gets postponed."""
    prework = (REPO / "docs" / "PREWORK-2026-09-16.md").read_text(encoding="utf-8")
    assert "d166_collapse_duplicate_tiles.py" in prework, (
        "the duplicate collapse is not queued beside the 37")
    assert "f078_null_tier_the_37.py" in prework
