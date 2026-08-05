# PRE-WORK — next session (baton from 2026-08-04)

> **Read this, `CLOSEOUT-2026-08-04.md`, and `ARCHITECTURE.md` first.** Per KEEL v6 pre-flight:
> new chat, upload nothing, let the Planner read the connected repository.
>
> ⚠ **v6 pre-flight assumes the Planner can see the repo. On 2026-08-04 it could not** — no GitHub
> connector, a zip only. **Confirm the connection by quotation of a specific named file before
> trusting anything the Planner says about repository state.** Green status is not proof.

---

## §0 — Confirm before doing anything

1. **`git log --oneline -1`** on `main` and on `d077-local-fold-envelope`. Is PR #122 merged?
2. **Numbers, checked in the log file itself, not in a reference to it.** `RESERVED.md` is the
   whitelist; the checker must report zero unresolved-and-unreserved. *A commit message naming an
   entry does not discharge it — the header must exist.*
3. **Migration 0007: still unapplied.** `alembic_version = 0006_run_kind`, `membrane_proximal_sasa`
   absent, both agreeing. ⚠ **If 0008 has since been authored, prod is two behind — verification
   must check each column separately, not just the head revision.**

---

## §1 — The spine, unchanged: run D-075

**It has been deferred twice and is still the gate on everything.** Phase B, the census, P-001's
branch, and the entire roadmap past Tier 2 hang on which row fires.

**It needs an unhurried session.** Apply 0007 (verify by column inspection, **not** alembic's exit
code) · confirm sealed Decision 4 reads exactly as merged (#109) · authorise the geom_proxy refit
and the attention control · **read the result against the frozen six-row table and only against it.**

⚠ **Decision 4 has a pre-registered *ambiguous* row.** A reader in a hurry will want to talk past it.
That row is a legitimate outcome, not a failed run.

**Land it as its own F-entry citing D-075, amending nothing.** Branch A or Branch B follows from the
row that fired, not from the hope.

---

## §2 — Then unblock the census (one delivery, not a decision)

**`ORDERS-Code-2026-08-04-b-scale-readiness.md` never reached the Builder.** Nothing is blocked on
thinking. Deliver it — **by paste** — and Tasks A and B run:

- **Task A** — fetch the real `table_S3_surfaceome.xlsx`; **verify against `2f1b8262…` / `6864772`
  before anything reads it.** A mismatch is stop-and-report. ⚠ The reconstruction Code built is a
  **scrape**, deliberately *not* under the upstream name, and it does not discharge Task A.
- **Task B** — 2,886 entry names → accessions, four buckets, `multi` reported not resolved.
  ⚠ **0 of 2,886 are accession-shaped.** The mapping is a hard prerequisite, not a cleanup pass.
- **Task C** — cohort tag + route filtering. **Ships before any census row can exist**, not
  alongside. `list_analyses` is unfiltered and unpaginated today.
- **Task D** — F-010. ⚠ **Owner ruling still outstanding.** Planner recommendation: rename to
  `folded_analysis_id` so the name states its own population rule (D-074's own remedy). Free now,
  impossible once anything consumes the field. Test names **IGF2R** — a test over the folded
  majority passes under both the bug and the fix.
- **Task F** — chunked-vs-unchunked (`None` vs `64`). Pre-register before running; **determinism
  control first**; fixture named from what exists in the repo. **Not Trop-2.**

---

## §3 — Three owner rulings carried forward

1. **KEEL Principle 7 divergence.** `docs/README.md` is a 652 KB container where v6 specifies four
   named documents — and v6's Principle 7 blood line *describes this repository by name*. The
   migration is mechanical; the timing is a judgement. **Not mid-branch with an open PR.**
2. **The assumption register** (`KEEL-Assumption-Register-v6.md`) — proposed as a fifth named
   document answering *"what are we taking for granted?"*, with seventeen seeded rows and the
   survivorship warning on the score. Unruled.
3. **P-002's gate is unset.** It is currently one good question and four unverified protein names.
   ⚠ **Its first work is curation and sourcing, not drafting** — the argument is compelling enough
   to write before the evidence exists, and that would make it an opinion piece.

---

## §4 — Standing constraints, unchanged

- **No census row enters the database before Task C ships.**
- **Scoring is inference, never refitting.** No census path may import the fitter. The
  pre-registered run (id=2, 56 / 12) is read from its row, never recomputed.
- **Two denominators, never summed.** The 82 is tranche zero, frozen. ⚠ **The surface class is
  2,807 distinct accessions, not 2,886 identifiers** — every count states its key.
- **Three classes, always named.** `surface` · `non_surface` · `unclassified`. ⚠ **The 2,801
  unclassified are not evidence for F-011's thesis** — a different exclusion mechanism. Do not
  recruit them; a larger excluded set makes a better story and that is the tell.
- **Local-foldability is a cost axis, never a suitability axis, and never a census filter.**
- **Red-then-green, corrected form:** a realistic mistake, failing at the assertion, not at
  collection.

---

## §5 — The through-line

**Nothing measured today changed a result. Several things changed what a result would have meant.**
The census denominator was wrong twice — once by 79 proteins, once by 126% — and both were found by
opening a file and counting, not by a test. The cohort turns out to span three fold recipes under an
invariance assumption that has now measured false in one regime and remains untested in the one that
matters. **The proof mechanism this project leans on hardest was itself resting on something nobody
had stated.**

**None of it moves without D-075.** That run has been deferred twice for good reasons and should not
be deferred a third time for a convenient one.
