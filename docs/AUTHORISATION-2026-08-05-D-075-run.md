# AUTHORISATION — 2026-08-05 — Execute `ORDERS-Code-2026-08-05-D-075-run.md`

> **This is an authorisation, not an order.** ⚠ **It restates nothing from the run order or from
> `docs/README.md` §D-075.** The order governs the run; the log governs the reading. This document
> does three things only: records the state that makes the run possible, discharges the §0
> confirmations already answered today, and names what changed since the order was written.
>
> **Owner authorisation, 2026-08-05.** Merge PR #123 first.

---

## §1 — Sequence

```
1.  Owner merges PR #123 (docs-only, c40967b)
2.  Confirm F-017 is reserved in RESERVED.md ON MAIN        ← #2's precondition, the reason for the resequence
3.  Execute ORDERS-Code-2026-08-05-D-075-run.md
```

⚠ **Step 2 is not ceremony.** `CORRECTION-2026-08-05-sequence.md` exists because the run order's §5
requires that reservation before the run, and it lands in #123. **Confirm it by reading the row, not
by trusting the merge.**

---

## §2 — §0 confirmations: three discharged today, two still Code's to make

**⚠ Do not re-run the discharged ones.** They were answered once, on the record, and a second run
risks two reports that disagree — the discipline from the 2026-08-05 meta-order.

| §0 item | State |
|---|---|
| **0.2 — migration state** | ✅ **Answered 2026-08-05 against the live tunnel.** `alembic_version = 0006_run_kind`; `membrane_proximal_sasa` **ABSENT** from `protein_features`. Read as two independent facts. **They agree.** ⚠ **Corroborated by an independent second reading** — `CLOSEOUT-2026-08-04.md` reported the same from a different session. **0007 is genuinely unapplied.** |
| **branch state** | ✅ `main` at `d6622f9` (#122 merged), `084517a` unsquashed in history. |
| **`RESERVED.md` checker** | ✅ Clean **on main**, output read not exit code. |
| **0.1 — Decision 4 reads as merged** | ⬜ **Code's, before anything else.** Quote it back from `docs/README.md`. |
| **0.3 / 0.4 — id=2 and id=3 intact** | ⬜ **Code's**, now that the tunnel is live. First time these are checkable this session. |
| **0.5 — the fixture's contaminated arm still reds** | ⬜ **Code's.** ⚠ If it will not red, **STOP** — the order says why. |

---

## §3 — What changed since the order was written

1. **⚠ Task 1a is real work, not a formality.** The order anticipated 0007 might already be applied.
   It is not. **The run begins with a write to production**, and that write is
   **owner-at-the-keyboard**. Verify after by column inspection, then separately by
   `alembic_version` — the same two-independent-facts method that produced the finding.
2. **`F-017` is reserved as of #123**, so §5's numbering is settled before the result exists rather
   than contested after it.
3. **The tunnel is live and it is fragile.** ⚠ **The proxy window must stay open for the whole run.**
   If it drops mid-run, that is **stop-and-report** — a partially-written result is worse than none,
   and the run guide records that the tunnel drops silently.

---

## §4 — The one thing that must not be compressed

**Report the fired Decision 4 row, quoted from `docs/README.md`, before writing any prose about what
it means.**

⚠ This is the whole asset. It has survived four deferrals, an adversarial review, and a Planner
correction that had dropped one of its rows. **A Pfizer date nine days out is exactly the pressure
the frozen interpretation exists to resist**, and the row most likely to fire is the one a reader in
a hurry will want to talk past.

**Nothing else in this document overrides anything in the order or the log.** Where this and either
of them differ, **they govern.**
