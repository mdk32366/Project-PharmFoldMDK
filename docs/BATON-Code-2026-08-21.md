# BATON — Code — 2026-08-21

> **Written by the outgoing Code at the end of 2026-08-20, after walking the Targets surfaces.**
> ⚠ This is a handover, not authority. **Where this file and `docs/README.md` differ, THE LOG
> GOVERNS.** Every number below is checkable and every one of them should be checked.

---

## §0 — Grounding, and what to distrust in it

**`main @ d3591d3`, deployed v95.** Gate **1,005 passed, 19 skipped**. Parent invariant
**155 defined | 15 reserved | 170 cited | 0 dangling**; amendment invariant **29 | 29 | 0**.

⚠ **Those numbers were true when written and are the first thing to re-derive, not to quote.** The
commands are in `docs/RESERVED.md` ("How to run the check") and `scripts/check_amendment_references.py`.

⚠⚠ **Standing prohibitions, carried forward and not negotiable:**
- **No hand-written SQL against production.** A committed, self-checked, bare-`SELECT` script is the
  established path (`scripts/taskb_pae_inventory.py`, `scripts/sa_pae_probe.py`).
- **A permission denial is STOP AND REPORT** — never a retry and never a workaround.
- **No rebase, squash, amend or force-push.**
- **NEVER run `pytest` in a shell where `.env` has been sourced. Print `DATABASE_URL` before every
  gate run; it must be empty.**
- ⚠ **Never round-trip a file through the shell.** Backticks in markdown get executed by
  `bash -c`; it happened three times on 2026-08-20 and once created stray files and ate a citation.
  Use the Write/Edit tools for anything containing backticks.
- **Assert that a string replacement applied.**
- **Confirm every `D-`/`F-` integer against the live log before spending it.**

---

## §1 — ⚠⚠ START HERE. A defect the outgoing Code shipped, found by walking Targets

**30 of the 777 census rows marked NOT FOLDED are already folded in the cohort, at identical span
lengths.**

| | |
| --- | --- |
| `ERBB2` / `P04626` on **Targets** | folded, mean pLDDT **73.94**, tier **rental**, `fold_length` **630** |
| `ERBB2` / `P04626` on the **census** | `folded: false`, `above_local_ceiling`, `span_aa` **630** |

⚠⚠ **The census card says *"waiting on rented capacity."* It is not waiting. The fold exists and is
one click away.** Measured: `span_aa == fold_length` in every one of the six spot-checked overlaps
(`PTPRZ1` 1612, `JAG1` 1034, `INSR` 731, `LRP6` 1351, `ITGB5` 696, `LRFN4` 502), so these are the
same spans, not merely the same proteins.

⚠ **The status is not wrong; the COPY is.** `above_local_ceiling` is true — 630 aa does exceed the
local ceiling of 440, and the cohort fold ran at **rental/fp16**. Two populations, and `D-081`
measures them under different span definitions. **But a reader is told a fold is pending when it
has already happened.**

**What is owed:** the census card and row must distinguish *"never folded anywhere"* from *"not
folded in THIS population, and here is the cohort fold."* ⚠⚠ **Do not simply link the two** — `D-081`
bars making one population reachable through the other's route, and the census route already 404s a
cohort-only accession *by design*. **The fix is copy plus a stated cross-reference, and the wording
is a ruling, not a rendering choice.** Report before building.

⚠ Reproduce it in one command before touching anything:
`/api/census` where `folded === false`, intersected with `/api/analyses` by accession.

---

## §2 — Two more from the same walk, both smaller

1. ⚠ **`/targets` says "80 folded targets" and lists 80 rows — but only 79 folded.** `IGF2R`
   (`P11717`) is among them and never folded. **The ROW is honest** — it renders `—` and *"fold
   failed — CUDA OOM folding 2491 aa at chunk_size=32"* — **so the header contradicts the row
   beneath it.** The census surface was fixed for the inverse defect on 2026-08-20; this one is
   still open.
2. ⚠ **`/targets` has NO search box.** The alias index (`D-101`) reaches the census only, so `HER2`
   finds nothing here even though `ERBB2` is present and folded. ⚠ Also: the default sort is
   **mean pLDDT descending**, which `CensusTable.jsx` explicitly refuses on the census as *"a
   self-reported confidence into a de facto ranking."* **Same reasoning, opposite behaviour, on two
   surfaces.** Whether the 82 may be ordered that way is a ruling — the cohort IS ranked, but not
   by pLDDT.

⚠⚠ **And a gift for `F-053`:** `IGF2R`'s failure is *"CUDA OOM folding 2491 aa at chunk_size=32"* —
**a MEMORY failure quoted against a LENGTH, rendered on the surface since long before `F-053` was
written.** The finding's own evidence was already on the page.

---

## §3 — The four documents landed today, and what each is for

All four moved to `docs/` with **AUTHORED-SHA256 verified**:

| file | what it is |
| --- | --- |
| `BOOT-Planner-2026-08-21.md` | ⚠ **the Planner's**, not yours. Do not execute it |
| `PREWORK-2026-08-21.md` | ⚠ intent, not state. **Rental, and only rental** |
| `CLOSEOUT-2026-08-20.md` | what happened. ⚠ *"that any of it is still true"* is what it cannot prove |
| `F-052-amendment-2-and-F-053-amendment-1.md` | ⚠⚠ **NOT YET LANDED IN THE LOG** — see below |

**⚠⚠ ONE CORRECTION TO `PREWORK` §4, MADE BEFORE YOU READ IT.** It says *"Merge
`fix/pae-squeeze-and-read-route` @ `692e805`"*. **That is already merged** — `main @ d3591d3`, PR
#173, deployed v95. ⚠ **Do not merge it again and do not treat `SA4`/`SA6` as unblocked by it:** the
route now exists, but the 79 matrices were never fetched, so `SA4`/`SA6` are still **unanswered**.
*A document that is intent rather than state will go stale exactly here.*

**Two entries in that paste are NOT in `docs/README.md`:** `F-052 amendment 2` (the squeeze sibling)
and `F-053 amendment 1` (§5's memory-scaling hole). ⚠ They are cited by `CLOSEOUT-2026-08-20.md`,
which is outside the primary invariant's corpus — **so the check is green and the entries are still
missing.** That is `F-044`'s shape and the reason the amendment checker exists. **Land them, verify
each pin, and confirm the header level: `####` for an amendment, `###` for a top-level entry.**
⚠ On 2026-08-20 an `F-` finding arrived with an amendment-level header; landing it as sent would
have made it **cited but not defined**.

---

## §4 — ⚠ The cheapest measurement on the board, and it may remove the reason to spend

**One fold at ~500 aa with the model RELEASED. Two minutes.** `PREWORK` §2 makes it the first
measurement, and it is the first datum on the memory-versus-length curve that nobody has.

**Why it matters:** ESMFold sits resident at **~5.24 GiB**; the *incremental* cost of the census's
longest fold (439 aa) is only **~1.26 GiB**. Releasing the model frees roughly five times the
incremental cost, so part of the **441–629 band may fold locally** — and 3 of 6 recoverable
positives sit in exactly that band.

**⚠⚠ Two things that weaken it, both measured and both in `F-053 amendment 1`:**
- **Reload is ~11.7 s per invocation, not amortised.** Confirmed twice: the 1-aa fold took 13.9 s
  against 2.0 s for the 21-aa fold. Trivial across a handful of 75–101 s folds; **~8.7 h across 2,690.**
- ⚠⚠ **The memory scaling is UNMEASURED.** `span^1.26` is a **TIME** law and says nothing about VRAM.
  Trunk attention is O(L²) at minimum, so there is **no reason to expect 629 aa to cost 1.26 GiB.**

⚠ **Practical note the two-minute estimate hides:** `scripts/sb_census_fold_timing.py` holds the
model across its loop **by construction**. Measuring release-and-reload needs a fresh process per
fold or an explicit teardown the script does not have. **That is a change, not a flag.**

---

## §5 — Open, with holders

| item | holder |
| --- | --- |
| `QC1` — re-key `JA`, then price | ⚠ **the owner**; it is the wall and nothing prices before it |
| `SA1`/`SA3`/`SA4`/`SA5` — the 79 PAE matrices | Code. ⚠ The route exists; **nothing has been fetched** |
| `F-042` path (c) — the ~7–8 h local refold | owner ruling |
| `F-052 amendment 2`, `F-053 amendment 1` | ⚠ **land them** (§3) |
| The 30-overlap copy defect | ⚠⚠ **§1 — report before building** |
| `/targets` count, search, default sort | §2 — the sort is a ruling |
| `preflight` wiring | ⚠ a decision, and it gates the climb. `F-049`: written, tested, called by nothing |

**⚠ Numbers that will be re-derived wrongly if you do not read them here first:**
- **~7–8 h**, NOT 7.67. Eight of ten folds agreed within 5%; the whole 6.95 → 7.67 move was the two
  longest folds shifting with thermal state. ⚠⚠ **A tighter regression on unstable measurements is
  precision theatre.**
- **`CEILING_KNOWN_GOOD = 440` is a LENGTH.** What binds is memory (`F-053`).
- **The census is 2,690 folded of 3,467 manifest.** Every count states its key or it is not a count.

---

## §6 — How this project fails, so you can watch for it

⚠⚠ **The recurring defect is not an error — it is a confident, well-formed answer about the wrong
thing.** Five instances landed in the log this week and three were found on 2026-08-20 alone: SEER's
*"Skin excluding Basal and Squamous"*, GDC survival over a convenience cohort, and HPA's cancer
column carrying two ICD-O axes at once. **None was a licensing problem and all would have survived
a licence review.**

⚠ **Three defects on 2026-08-20 were found by WALKING the surfaces, not by tests** — including two
introduced within the hour by the person writing the enumeration meant to close them. **`F-052`
amendment 1 is that finding.** Walk what you ship.

⚠ **And a guard that matches its own warning text fired three times in one day.** A check that greps
source for the thing it forbids will red on its own docstring, and its own forbidden-token list.
**Read structure — AST — not prose.** Every instance was fixed the same way and it recurred anyway.
