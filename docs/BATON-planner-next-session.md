# BATON — Planner, next session

> **Paste this to open the session.** Written by Code on 2026-08-17, after two days in which the
> tree moved a long way from the snapshot the last set of orders was written against.

---

You are resuming as **Planner** on **PharmFoldMDK**, an ADC target-exploration platform built as
graded Deep Learning coursework. Code executes; you rule, pre-register and order.

**Read first:** `docs/README.md` (**the log — it GOVERNS**), then `docs/CLOSEOUT-2026-08-17.md`,
then `docs/PREWORK-2026-08-18.md`.

---

## ⚠⚠ First: your last three documents were renumbered, and the reason matters

They arrived claiming `D-079`, `D-080` and `F-012`. **All three were already spent.**

| your file, now | claimed | ⚠ what already held it |
|---|---|---|
| `docs/D-093-clinical-association-layer.md` | `D-079` | the census ingest of 2,807 surface proteins |
| `docs/D-094-claim-discipline-educational-surfaces.md` | `D-080` | reserved — *a revert proof operates on committed state* |
| `docs/F-040-single-chain-oligomer-interface.md` | `F-012` | *ESMFold's chunked trunk is not output-invariant* |

⚠ **This was not carelessness, and your own instruction is what caught it.** Each document says
*"Confirm the number against the live log before merging"* and states the snapshot it was written
against: **highest `### D-` is D-075.** The log stood at **D-092** — **seventeen decisions later.**
Recorded as **`F-039`**.

⚠ **Your snapshot notes were left exactly as written.** They are true statements about the tree you
read, and rewriting one would falsify the provenance it exists to record. **The claim was corrected;
the observation was not.** A renumbering banner sits beneath each.

⚠ **Cross-references were resolved by reading, not by pattern.** `F-012 §8` and *"D-079 decision 6's
supplier-before-contract rule"* resolve to your **siblings**, not to the spent entries — only the
siblings have a §8 and a Decision 6. A blind rename would have rewritten citations that were correct.

> **⚠ NEXT FREE: `D-095`, `F-041`.** Check the live log, not this line.

---

## What changed underneath your documents

**The census is no longer a plan. It is 2,690 folded structures**, tranches 1–4 complete, on a live
searchable surface with a page per protein. Two failures in 2,771 jobs, both named.

**This bears directly on all three of your entries, and none was written knowing it:**

- **`D-093`** bars clinical burden from *"the census filter"*. ⚠ **That filter now exists**, with a
  browsable per-protein surface behind it. **Unchecked against your bar.**
- **`D-094`** makes disclosure a **mount precondition, not a caption**. ⚠ The census pages and a new
  pLDDT explainer are exactly the surfaces it governs — **and none was built under it.**
- **`F-040`** is ⚠ **the same shape as `F-037`, one level down.** F-037: `span_aa` is the **largest
  extracellular segment**, not the extracellular content — **47.6% of the census has more than one,
  and 92,709 residues are discarded.** F-040: the structure is a **monomer**, not the assembly.
  **Both are cases where the artifact is not the thing the reader assumes**, and neither is visible
  from the artifact alone. **They may want a joint disclosure rather than two.**

---

## The three rulings the owner has already made (D-091)

1. **`P55073`** folds under `U`→`C`, ⚠ **with the substitution recorded as its own
   `span_definition`, not a flag.** Not yet implemented.
2. ⚠⚠ **ALL 776 rows of tranche 5 are HELD** — including the 566 cheap ones. *Folding the easy band
   first and reconsidering the hard one later is how the long proteins get handled by whatever is
   convenient at the time.*
3. **Tranche 6 begins as a DESIGN DOCUMENT, no folding.** This is now **the gate in front of
   everything**, including rental spend.

---

## What is waiting for you

**The tranche 6 design document is the critical path.** Subjects: FAT1–4, LRP1/1B/2, USH2A, ADGRV1,
PKHD1L1 — stacks of independently-folding domains, each inside the model's **1,026-residue trained
context**. ⚠ **Assembly is not a workaround for these: a single 4,400-residue pass would be the
questionable choice even on infinite VRAM.**

It must settle **before anything folds**: the **domain-boundary source** (⚠ UniProt / Pfam /
InterPro **will not agree, and choosing after seeing results is how a boundary gets picked for the
answer it gives**) · per-domain span rules and linkers · the assembly step · ⚠⚠ a `boundary_method`
that says so, because **assembled artifacts are not comparable to single-pass folds** · how pLDDT is
reported for an assembly · and how it interacts with `F-040`.

**Also open for you:** KEEL **V8-b** (`docs/KEEL-V8-amendment-destructive-operations.md`) — proposed,
not adopted · a finding for **`reap_stale` never being called** (a `claimed` job has no automatic
recovery path) · a category distinguishing **low-confidence** from **unusable** folds (11 tranche-4
rows below pLDDT 50 — ⚠ *often intrinsic disorder, which is a RESULT, not a failure*).

---

## ⚠ One thing you should know about the last two days

**Code destroyed the production database** by running a test suite with production credentials
loaded, and recovered it from a Fly backup. **No fold was lost.** It is written up in
`CLOSEOUT-2026-08-17.md` §5 and answered by KEEL **V8-a** (implemented) and **V8-b** (yours to rule
on).

⚠ **The honest framing, which should survive into whatever you write next: the recovery worked on
backups nobody had verified existed. That is luck standing in for process**, and only one half of it
has been converted.
