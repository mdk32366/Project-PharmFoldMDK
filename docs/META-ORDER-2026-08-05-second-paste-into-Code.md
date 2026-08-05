# META-ORDER — paste into Code — 2026-08-05 (second) — the A-017 ruling, the merge, and Tasks B → D

You are receiving **one document**: `RULING-2026-08-05-A017-and-task-C-protocol.md`.
**Hash it against the copy in hand before reading; a mismatch is stop-and-report.**

⚠ **The delivery channel has failed three times today** — the STOP ruling never arrived across two of
your reports, and one of your reports arrived here twice. **If anything this meta-order names is not
in your hands, say so before building rather than reconstructing it.**

---

## §1 — Sequence

```
1.  Merge PR #124 at 8713c06                              ← owner authorisation, below
2.  Confirm on main: checker clean, F-020/F-021/A-017 rows present
3.  Task B — build, tests first, owner merges
4.  Task C — OWNER at the keyboard. Production write. Not yours.
5.  Task C verification — YOURS, independently, after the owner reports only that it ran
6.  Task D — the same command that refused now proceeds
7.  STOP. Run A does not start.
```

**Owner authorisation:** *"Merge PR #124 at `8713c06`. Owner authorisation, 2026-08-05."*

---

## §2 — The A- naming convention: forward-only. ⚠ Do NOT sweep.

The ruling §2 introduces `A-0NN (descriptive name)` citation form. **Its scope is narrow and the
narrowness is the point.**

✅ **Apply to:** every **new** A- citation, in code, docs, orders, and commit messages.
✅ **Add descriptive names to `RESERVED.md`'s A- rows** — that file is the index, so existing bare
citations resolve through it.

❌ **Do NOT rewrite existing citations** in `PAPERS-v2.md`, in today's committed rulings, or in the
log. ⚠ **Editing a sealed document to look as though it never used a bare number is the shape this
project refuses** — the same reason `RULINGS-…-task2-task3-contract.md` §3.1 got a *pointer* rather
than a corrected definition.

❌ **Do NOT renumber anything.** A-014, A-016, A-017 keep their integers. **The reconciliation
happens when KEEL-4 lands, and it must check all three** — not only A-017.

---

## §3 — Task B: three things that decide whether it is right

1. **⚠ Abort-on-drift is the whole task.** *Fix what is broken, abort on everything else.* A fill
   that writes the rows that matched and reports the ones that did not is the command that would
   have corrupted the table, wearing a report.
2. **The latest-run default is DELETED, not corrected.** `--load` requires `--ranking-run`.
   ⚠ A default that silently resolved to `plddt_only` is the `or "resolved"` class.
3. **`or 0.0` at `fit_scorer.py:111` is removed, not guarded around** (ruling §3). A measured 0.0 is
   a legitimate value; correctness must not rest on the guard alone. **Report feature 7's
   distribution after the fill and name any exact zeros.**

**And report the 1–6 comparison as a result even when it passes.** ⚠ An 80/80 byte-identical match
is a determinism finding about the instrument D-075 runs on. **A mismatch outranks D-075 and stops
Task C.**

---

## §4 — Task C is the owner's, and your part is the *second* reading

**Do not run the fill.** When the owner reports **only that it ran** — not what it showed — read the
post-state yourself: row count unchanged, non-null count on the ranking set, feature-7 distribution.

⚠ **The two readings must agree.** If they disagree, that is stop-and-report and Task D does not
start. This is the discipline that corroborated 0007 twice today, as unapplied and then as applied.

**⚠ Your Task B report must name the exact invocation** — the dry-run flag and the write flag. The
owner protocol deliberately does not guess them; the Planner does not name flags it did not write.

---

## §5 — Hard boundaries

- **No Run A.** Its own order, its own unhurried session, with the frozen interpretation open.
- **No hand-written SQL against production**, by anyone, for any part of this.
- **No touching `ranking_run` id=2, id=3, or id=4.** No refit.
- **No general-purpose updater.** `--fill-feature-7` writes one column.
- **No census work, no migration 0008, no UI.**
- **No KEEL Principle 7 migration** — still an owner-parked cleanup task, not in this handoff.
- **No document reorganisation.** If you notice something relevant you were not given, report it.

## §6 — Report-back checkpoints

1. **After the merge:** checker on main, and the three reserved rows quoted.
2. **After Task B's tests go red:** where each red fires — ⚠ **at the assertion, and having reached
   the code under test.** `A-017 (the fixture must reach the code under test)` is now a named
   requirement, not a lesson.
3. **After Task B's PR is up:** the exact dry-run and write invocations, for the owner.
4. **After the owner reports the write:** your independent post-state reading.
5. **After Task D:** the refusal and the pass, reported **as one before/after pair** — that pair is
   F-020's closure evidence under D-074.
