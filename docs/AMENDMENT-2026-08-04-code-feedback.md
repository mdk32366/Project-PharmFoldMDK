# AMENDMENT — 2026-08-04 — Code's D-077 report, reconciled against the four staged documents

Covers: `KEEL-4-The-Assumption-Register-v1.md`, `F-011-surfaceome-negative-class.md`, `PAPERS.md`,
`ORDERS-Code-2026-08-04-surfaceome-spans.md`. Ends with the pre-noon runbook and the answer to
Code's closing question.

---

## §1 — ⚠ Numbering collision: two claimants on F-011. Owner rules.

Code reports *"next free is F-011"* for the two probe results. The Planner staged **F-011** as the
surfaceome negative-class finding an hour earlier. **Neither is merged, so nothing is broken yet —
but this is exactly the condition that produced D-062.**

Also: Task 1 and Task 3 Arm A are **two** F-entries, not one. Three claimants, one number.

**Planner recommendation (not a ruling):** the surfaceome finding is **complete and mergeable now**;
the probe entries **cannot exist until the GPU runs**. Assign by readiness, not by intent:

| Entry | Assignment | State |
|---|---|---|
| **F-011** | Surfaceome negative class | Staged, complete, mergeable today |
| **F-012** | Task 1 — chunk-invariance verdict | Reserved, blocked on the run |
| **F-013** | Task 3 Arm A — local ceiling | Reserved, blocked on the run |

⚠ **If the owner assigns differently, the staged file is renamed before merge, not after.** D-075's
precedent: untracked drafts sweep freely; a merged citation cannot be renumbered (D-011).

**Consequence for the register:** F-011's closing line cites **A-014**, which does not exist until
KEEL-4 lands. That is a **third** forward reference, joining D-010 and D-078.

---

## §2 — The forward-reference set is now a list, and it needs to be one place

Code's handling was right: *a reference announcing its own absence is not the D-062 defect, but is
indistinguishable from it to a checker.* That distinction is correct and it does not scale as prose
scattered across a method note.

**Recommended:** a single `RESERVED.md` — every announced-but-unwritten `D-`/`F-`/`A-` number, who
reserved it, and what unblocks it. The checker whitelists that file and nothing else. **An
unresolved reference not in `RESERVED.md` is a finding, immediately.** Currently: **D-010**
(historical skip), **D-078** (precision A/B, unblocked by a raised ceiling), **A-014** (unblocked by
KEEL-4), and **F-012/F-013** if §1 is accepted.

This keeps Code's stated property — *"an undocumented third miss is a real finding"* — true as the
set grows, instead of true only while the set is small enough to remember.

---

## §3 — KEEL-4 additions. All three of Code's flagged items are register entries.

Add to §2's evidence table. **Revised score: twelve tested, twelve broke.** The survivorship
warning in KEEL-4 §2 is unchanged and still governs how that number is read.

| # | The assumption | How it surfaced | Outcome |
|---|---|---|---|
| **15** | *`git checkout --` is safe on a file whose work is committed* — i.e. that the work **was** committed | Revert-proof loop wiped uncommitted `core/manifest.py` and `worker/ceiling_probe.py` | **BROKE** — and this is the **second occurrence** (D-075's process note is the first) |
| **16** | *A test that goes red proves its assertion bites* | `test_probe_module_imports_no_database_session` reddened on `from db.session import …` as a **collection error**; the assertion never ran | **BROKE** |
| **17** | *Documenting a duplication manages it* | `core/manifest.py`'s comment read *"mirrors `scripts/ecd_lengths.py:46-52`"* — the drift was **written down and left live** | **BROKE** |

### ⚠ Item 16 is the most important thing in Code's report, and it is bigger than one test.

**Red-then-green is this project's primary proof mechanism**, cited in nearly every order. It
rested, unstated, on *any red proves the assertion bites.* It does not. **An error-red and a
failure-red are different objects**, and only a failure-red proves the assertion executed. A
non-importable module produces a collection error that looks exactly like a passing proof in a
terminal.

**Ruled into the method, effective now:**
- **A revert proof must fail at the assertion, not at collection or import.** Read the failure
  line, do not read the colour.
- **The revert must be a realistic mistake.** `from db.session import SessionLocal` proves nothing
  because `db.session` does not exist; `from db import models` proves it because that is the import
  a careless author would actually write. Code found this by reading output rather than trusting it
  — the exact behaviour §5 of KEEL-4 says to reward.
- **The docstring records which revert proves the guard and which does not.** Code did this
  unprompted; it becomes the standard.

### Item 15 is now a pattern (n=2) and needs a rule, not a note.

**Twice now, proving a guard has endangered the thing it guards.** Recommended as **D-080** (D-078
reserved, D-079 staged): *a revert proof operates on committed state or on a copy — never on a
working tree holding uncommitted work.* Commit first, then break, then restore by `git checkout` of
a **known commit**. The current method makes the destructive act indistinguishable from the safe
one.

⚠ **And note what saved it both times: someone was watching.** That is not a guard.

---

## §4 — Patches to the surfaceome-spans orders

1. **Constant renamed.** Code's implementation uses **`LOCAL_CEILING`** (a structure carrying its
   recipe), not `CEILING_KNOWN_GOOD`. Every reference in `ORDERS-Code-2026-08-04-surfaceome-spans.md`
   §2 and §3 reads `LOCAL_CEILING`. **Read the shipped name off the merged code, not off this
   amendment.**
2. **§3's `ecd_lengths.py` note is superseded — in the project's favour.** The order said to extend
   it; Code has already bound it to the shared structure and added a test that fails if a bare
   literal reappears under `core/`, `scripts/`, `worker/`, or `app/`. **The census span pull
   therefore inherits the guard rather than needing one.** Nothing to add.
3. **The full-scope ingest and Downloads-by-name instructions stand unchanged.**
4. **Sequencing note kept:** the split artifact must name the ceiling that produced it. With
   `LOCAL_CEILING` still at 440 and **zero targets moved tier**, a split computed now is valid and
   will simply be recomputed when the bisection lands. Cheap either way.

---

## §5 — PAPERS.md: one addition

**P-001 gains an open item.** Item 16 above is a defect in the *evidence-generation method* the
paper's credibility rests on — the honesty apparatus is a stated strength of both branches. **It
does not weaken any result** (no F-004/F-005 guard was proven by a fake red, and Code re-proved the
one that was). But the methods section, if it claims red-then-green, must claim the corrected
version. **Found by us, before review, and recorded.**

---

## §6 — The pre-noon runbook, and ⚠ a Planner reversal

**I have argued all morning that the D-075 run comes first. I am reversing that for today only, and
the reason is new information, not a change of mind about priority.**

Code confirms **migration 0007 is still unapplied to prod.** So the run is not a short CPU refit —
it opens with **a schema migration against live production**, carrying a known silent-rollback
hazard that must be verified by column inspection rather than by exit code. Then it requires reading
a **sealed six-row interpretation table** whose entire validity rests on being read carefully.

**A prod migration and a one-shot sealed reading, executed against a departure clock, is the worst
available combination.** The pressure to accept an ambiguous result as a clean one is highest
exactly when someone is watching the time — and Decision 4 has a pre-registered *ambiguous* row that
a rushed reader will want to talk past. **D-075 keeps its priority; it loses today's slot.**

### Do before noon — safe, reversible, high value per minute

| Order | Task | Why it qualifies | ~Time |
|---|---|---|---|
| **1** | **Read-only 0007 check** — does `membrane_proximal_sasa` exist in prod? | **Read-only.** Answers Code's question with a yes. It is information, not mutation, and it removes a standing unknown from the baton. **Do not apply.** | 2 min |
| **2** | **Open the PR** for `d077-local-fold-envelope` | `main` is protected with `enforce_admins` (D-008), so nothing merges by accident. CI runs while you fly; you review from the air. | 5 min |
| **3** | **Task 1c** — three Trop-2 folds, int8, chunk 64/32/16, then read decision 2's **two-row** frozen table | Local, no DB writes, fully reversible, ~250 aa so nowhere near the wall. **Two rows, not six** — a safe reading under time pressure in a way D-075's is not. Gates Arm B. | ~15 min |

### Do NOT start before noon

- **Task 3 Arm A.** Bisection at k=4 in (440, 630) is roughly twenty folds **deliberately driven
  into an OOM boundary**, on a card with 378 MiB of headroom, on the machine whose S-004 precedent
  is *a host bugcheck*. It wants someone at the keyboard. Tonight or on landing.
- **The D-075 run**, per above.
- **Applying 0007.** Read-only check yes; migration no.

---

## §7 — Answer to Code's closing question

**Both, in this order: read-only 0007 check first, then open the PR.** The check is two minutes and
its answer changes what the next session opens with; the PR is a container, not a commitment, and
protected `main` means it cannot become one without the owner.

**Then Task 1c if the clock allows, and stop there.**

**One request back to Code:** the §3 finding — that `ecd_lengths.py` carried a hand-duplicated copy
of both constants while `core/manifest.py`'s own comment *documented* the duplication — is the
**tenth** instance of the two-paths-to-one-quantity class, and it has a feature the other nine did
not: **the drift was known, written down, and the writing-down substituted for the fix.** That
belongs in the log as its own short finding, not only in a session report. **Reserve it a number in
`RESERVED.md` and write it when the branch merges.**
