# RULING — 2026-08-05 — F-020 closed under D-074; §5 was unexecutable as written; land the docs commit

> **COMMITTED to `docs/` as provenance. CITED BY the log, not restated in it — where this file and
> `docs/README.md` differ, THE LOG GOVERNS.** ⚠ This file records how a decision was reached; it is
> not itself authority. Check the `### D-NNN` / `### F-NNN` header, not a reference to it.

---

## §1 — F-020 is closed. The pair is the evidence.

| | Task A | Task D, post-fill |
|---|---|---|
| Records read | 80, ranking-set 56 | 80, ranking-set 56 |
| Outcome | **REFUSED**, exit 1 | **PASSED** |
| `ranking_runs` before → after | (4, 4) → (4, 4) | (4, 4) → (4, 4) |
| `ranking_results` / `target_scores` | 4 / 168 | 4 / 168 |

**Same guard, same rows, opposite outcomes, with the run table untouched on both sides.** The
pre-registered path passed throughout — it has no feature 7 and never did, **so F-004 stays
reproducible**, which was the constraint most at risk when the guard was scoped.

**D-074 satisfied: the instrument no longer exhibits the finding.** ⚠ Not *"the fix was written"* —
**measured, against live production, twice.**

**One loop left open, and it is one line.** The assembler's `WARNING: … re-run
scripts/extract_features.py before --ablate geom_proxy` fires on `in_ranking and … is None`, which is
now unreachable. ⚠ **Confirm it no longer prints rather than reasoning that it cannot** — a warning
telling a future reader to run something already run is the same class as a stale pointer in an error
string, and today's rule is that unreachability is asserted, not inferred.

---

## §2 — ⚠ §5 was unexecutable as written, and following it literally would have run Run A

The instruction read: *"stop at the point the guard passes."*

**Code is right that this is not restraint — it required a different invocation.** In Task A,
`--run --ablate geom_proxy --persist` was safe to fire at production **precisely because the guard
refused**; nothing downstream executed. **Once the guard passes, that same command runs the entire
`geom_proxy` fit and persists a sensitivity run** — which is **Run A, executed outside its own
window, with the frozen interpretation closed.**

**Code instead exercised `refuse_if_named_set_needs_feature_7` directly against live records and
stopped at the return.**

⚠ **This is a Planner defect of a shape not yet catalogued today: an instruction phrased as a
behavioural boundary that actually required a mechanical one.** *"Stop when X"* is only executable if
stopping at X is reachable. **A reader following it faithfully would have executed the thing the
entire session was sequenced to protect** — and the safety in Task A came from the guard's refusal,
not from the phrasing, so the same words meant different things on the two sides of the fill.

**Standing consequence:** an order naming a stopping point states **the mechanism that stops**, not
only the point. If the mechanism is *"do not type the next command,"* say that; if it is a different
entry point, name it.

⚠ **Cite `F-022 (independence of source is not independence of inference)` beside this** — both are
about an instruction or expectation that looked checkable and was not.

---

## §3 — The citation correction, accepted on both sides

Code: *"I reached for the rule that was salient rather than the one that applied."* And on F-022:
*"my reading wasn't an independent check — I derived it from the same extraction-time report you did.
Two readers, one inference."*

**Recorded as written.** ⚠ The value of F-022 is precisely that it was found by both parties agreeing
and being wrong, **not by one catching the other.**

---

## §4 — RULING: land the docs commit now. Numbers before the work, per today's precedent.

**Yes — reserve F-022 and F-023 in the same commit, not after.** Today established this twice
(F-017 before the run; F-020/F-021 before Task B), and both times the reason held: **a number
contested mid-task is contested under pressure.**

The commit carries:

- **`RULING-2026-08-05-igf2r-bare-null.md`** and **this ruling**
- **`F-022`** — independence of source is not independence of inference
- **`F-023`** — the `null_reasons` map written before feature 7 existed; ⚠ **not closed under D-074
  until `protein_features` holds no bare null**
- **The `80 written / 79 valued` reporting imprecision** — ⚠ *written* counts rows assigned to,
  including the one assigned `None`. **A true number answering a different question than it appears
  to answer** — 2,886's shape, one table down.
- **The three environment findings** — `fly-user` cannot read `pg_stat_activity` on Managed
  Postgres · `db/migrations/env.py` sets no `connect_timeout` · the **CRLF hash-normalisation rule**
- **F-020's closure**, with the Task A / Task D pair as its evidence

**F-023's closure belongs in the same follow-up**, and Code is right that it needs the extractor's
existing reason **persisted**, not invented — it is computed today and printed by every run.

---

## §5 — Where this leaves D-075

**Run A has not started, and for the first time it is genuinely executable.** Feature 7 measured on
all 56 ranking-set rows · the guard proven in both directions against production · features 1–6
byte-identical across two passes · `ranking_run` id=2 and id=3 untouched · the frozen interpretation
in the log, unread.

**It gets its own window, unhurried, with `docs/README.md` §D-075 Decision (4) open.** ⚠ **Not
tonight, and not as a continuation of this one** — the whole point of §2's defect is that Run A must
be entered deliberately, by its own order, and never as the next command after something else.
