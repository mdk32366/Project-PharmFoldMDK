# ORDERS — Code — the ingest goes through the GATE, not through anyone's hands

**AUTHORED-SHA256** (range: **first `## §` header → EOF**, no newline normalisation) = `1da904fd593709a51e0a24122414b8400929756992ec2104ffc397d0e7c5dfc3`
**bytes** = `8711`

> ⚠ **DOWNLOAD AND COMMIT. DO NOT RETYPE. No landing header** — provenance goes in
> `SPEC-2026-08-19-landed-artifact-provenance.md`.
>
> ⚠ **Hash the range by ANCHORING TO LINE STARTS.** `F-047` member 18: the header describing a range
> contains the range markers, and a plain `index()` hashed zero bytes — **a valid hash of nothing,
> which would have matched itself forever.**
>
> ⚠ Planner grounding `7011e24`. **No GPU, no rental, no fold. Tranche 5 HELD** (`D-091` r2).

---

## §0 — ⚠⚠ The Planner's previous recommendation was wrong and is withdrawn here

**The Planner told the owner to hand-run an Alembic migration and a production ingest.**

⚠⚠ **KEEL-2/3 step 16: *hand-deploy dies. Merging is the only way to ship. Manual = emergencies
only.*** **A migration typed at a production terminal is exactly the operation the gate exists to
prevent a human performing** — *a tired person at a terminal at 11pm* is what branch protection was
built against, **and the Planner proposed making the owner that person.**

⚠ **The rule the Planner was actually bound by is narrower:** *never infer flag syntax for a
production command — say what is needed, and let the owner **or Code** supply the syntax.* **That
governs who WRITES commands, not who presses enter.** **`F-047` member 19.**

**The correct split, and it is what this order implements:**
**writes go through the GATE · reads go through a READ-ONLY ROLE · the owner holds credentials and
the decision to stop · Code executes both.** ⚠ **The control is the gate and the grant — not hands on
a keyboard.**

---

## §1 — Task GA — does a release command already exist?

⚠ **Never assert absence.** **Report, from `HEAD`:**

**GA1 — Does `fly.toml` carry a `[deploy] release_command`?** Quote it, or report its absence **as of
the revision you checked.**
**GA2 — How have migrations reached production until now?** ⚠ **If the honest answer is *by hand*,
say so** — that is a finding about the deployment path, not an embarrassment, and it is `D-092`'s
neighbourhood.
**GA3 — Do migrations currently run anywhere in the gate workflow?** Quote the step or report none.

⚠ **Answer GA before building anything in §2.** If a release command exists, this is configuration;
if it does not, it is a new deployment step and **that is a decision with an entry.**

## §2 — Task GB — the migration becomes a consequence of merging

**On GA's answer:** the Alembic upgrade runs as a **release command**, so schema changes land
**because a merge passed the gate**, not because anyone ran anything.

**GB1 — ⚠ The release command must FAIL the deploy on a failed migration.** A migration that errors
and lets the deploy proceed is worse than no migration — **the code would then run against a schema
it does not expect.** **Prove it: point a migration at a deliberate error and watch the deploy stop.**
**GB2 — ⚠⚠ Report what happens to an in-flight request during the migration**, and whether the
migration is backward-compatible with the currently-running image. **A release command runs BEFORE
the new image is live** — additive columns are safe, drops and renames are not. **Say which this is.**
**GB3 — Report the rollback path**, and ⚠ **whether it has ever been exercised.** *Accept by
reproduction, not by label* — a rollback nobody has run is `F-045`'s shape.

## §3 — ⚠⚠ Task GC — THE INGEST CARRIES ITS OWN ACCEPTANCE BAR, INSIDE THE TRANSACTION

**This is the part worth building carefully.**

**GC1 — One idempotent command, shipped in the image**, invoked by the release path or as a one-shot
job. ⚠ **Not a script anyone runs locally against production.**

**GC2 — ⚠⚠ THE `D-100` REPRODUCTION RUNS INSIDE THE TRANSACTION, AGAINST WHAT WAS JUST WRITTEN:**

```
BEGIN
  load pathology.tsv + normal_tissue.tsv   (column-scoped; prognostic columns excluded and asserted)
  run the D-100 reproduction ON THE INGESTED ROWS
      337 / 337   kept pairs
    1,303 / 1,303 correctly excluded
    1,640 / 1,640 rows, all four count columns identical
  if any figure differs  ->  ROLLBACK, exit non-zero, print the mismatch
COMMIT
```

⚠⚠ **A wrong ingest then CANNOT LAND.** **Not *we check afterwards and repair it* — the database
refuses to keep data that fails Kathad's grid.** **Honesty made structural rather than documentary.**

**GC3 — ⚠ Prove the rollback fires. Corrupt one count in a fixture, run it, and watch the transaction
roll back and the exit code go non-zero.** **A bar never seen to reject is decoration** —
Principle 9. **Restore byte-identical afterwards.**

**GC4 — Idempotency marker**: the ingest records its own completion with the **source `sha256`** of
each file. ⚠ **A second run against the same hashes is a no-op, not a duplicate.** **A run against
different hashes is a NEW ingest and says so.**

**GC5 — ⚠ Report what the ingest does if a source file is ABSENT or its hash does not match the
pinned value.** **Hard error, never a skip** — KEEL-1 V9 Principle 6's direction clause, and the
third guard audited under it this week.

## §4 — Task GD — the read-only role, which is what makes a tunnel safe

⚠⚠ **`AC1` measured the residual: *loopback tunnel to production — PASSES*.** `D-092` refuses
production **by hostname**, and through a tunnel the hostname is `localhost`. **The guard does not
fire.** ⚠ **And 14 tests `TRUNCATE` per test.**

**GD1 — Specify a Postgres role with `SELECT` only** — no `INSERT`, `UPDATE`, `DELETE`, `TRUNCATE`,
no DDL, and ⚠ **no ownership of any table**, since an owner can truncate regardless of grants.
**GD2 — ⚠⚠ Prove the refusal at the DATABASE, not at the guard: connect as that role and attempt a
`TRUNCATE`. It must fail with a permission error.** **Report the error text.** **That is the
difference between *we checked* and *it cannot happen*.**
**GD3 — ⚠ Say what the owner needs to create it.** **Do not infer the syntax; state the requirement
and let the owner or your own authorised path supply it.** **The credential is the owner's.**
**GD4 — With that role, `FA2` · `FB1` · `FB2` are read-only SQL and are yours to run.** ⚠ **Report
`FA2` as the SET DIFFERENCE — which accessions — not as the arithmetic.**

⚠ **Sequence, and it matters: the backup verification is rank 2 on the owner's queue and this is when
it earns its keep.** **Opening any tunnel to production before a COMPLETED backup is confirmed
recreates the conditions of the original truncation with the recovery path unverified.** **Say so in
your reply; do not proceed past `GD1`/`GD2` without it.**

## §5 — ⚠⚠ Task GE — `FD1` may be arithmetic, not a refit. Test the hypothesis

**`core/scorer.py` line ~200 returns `coefficients[k] * std[k]` — the attribution IS
`coefficient × standardized feature`.**

⚠ **So if per-target attributions are persisted, then across the scored set `attribution_k(i)` is an
exact linear function of the raw feature `x_k(i)`, slope `coef_k / sd_k`.** **Two rows determine it;
56 over-determine it 28-fold.**

**GE1 — ⚠ Confirm or refute the premise first: are per-feature attributions persisted per target, or
only a total?** **If only a total, say so and stop — the hypothesis dies there.**
**GE2 — If they are, recover the slope per feature and ⚠⚠ REPORT WHETHER ALL ROWS AGREE.** **Any
deviation is a finding** — about determinism, about drift, or about attributions not being what they
are documented as. **The self-check is the point, not the coefficients.**
**GE3 — If the standardizer's mean and sd are persisted, recover `coef_k` exactly. If not, report the
RAW-SCALE coefficient** and say which you have. ⚠ **Do not reconstruct a standardizer to get the
other one — that is fitting.**
**GE4 — ⚠⚠ This is a REPRODUCTION FROM PERSISTED VALUES, NOT A FIT.** **`§6` of the scoring order
stands: if closing this needs anything fitted, STOP AND REPORT.**

⚠ **The Planner is reading a stale snapshot and this is a HYPOTHESIS, not a claim.** **Refuting it is
as useful as confirming it.**

## §6 — ⚠ Task GF — the finding that stands whichever way `GE` goes

***"No fitted-model coefficients are persisted — only the per-target score/rank/attributions and the
LOO distribution."***

⚠⚠ **`D-041` claims the fit is reproducible and nothing stored makes that checkable.** **A
pre-registered run's parameters cannot be recovered from the record** — `F-045`'s shape: *the record
says what was done and not enough to redo it.*

**Report, for the Planner to write up:** what IS persisted per run · what would have to be stored for
`FB3` to be answerable without fitting · ⚠ **and whether `scorer_version` alone is sufficient to
establish that two runs used the same parameters, or only that they used the same CODE.**

## §7 — Report

Branch and tip · ⚠ **number and title of any entry landed, in the message that lands it** · the
invariant with its keys, tested before any merge · the gate without `.env` · ⚠⚠ **and `GA`'s answer
FIRST, because §2 and §3 are configuration if a release command exists and a new decision if it does
not.**
