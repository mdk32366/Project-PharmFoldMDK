# RULINGS — 2026-08-07 — The fold path: chain selection, guards, manifest identity, and span validity

> **OWNER RULINGS, made 2026-08-07 during the fold-path arc, and binding.** Where this file and the
> log differ, **THE LOG GOVERNS.** ⚠ This file is provenance for decisions that live in the log; **it
> is not itself authority.** Cited by the log, not restated in it.
>
> ⚠ **WHY THIS FILE EXISTS.** Every ruling below was made in pasted chat, on a day when that channel
> corrupted **thirteen consecutive reports** and dropped mid-turn in both directions. `### F-025` and
> `### D-081` are committed; **these were not.** That is F-011's shape — **a ruling living only in a
> scrollback is one session-death away from being reconstructed from memory**, which this project
> refuses. **Written before the crank, not after.**

> **Planner provenance (D-016).** Every count is **Code's reading**, reported 2026-08-06/07. The
> Planner independently reproduced the selector arithmetic, the band and denominator sums, the
> coordinate/length reconciliations, and the CCR4 largest-contiguous result. **No connector, no
> `.git`, no database.**

---

## R6 — GPI chain selection: the anchor selects the chain

**Supersedes the Planner's first selector, which was wrong.**

> **Select the `Chain` features that CONTAIN the anchor position. Among them, take the LATEST start.
> Span = that start → (anchor − 1).**
> **Zero chains contain the anchor → `absent_with_reason: gpi_no_chain_spans_anchor`.**

⚠ **Latest start is conservative, not arbitrary.** Where UniProt annotates both `37-598` and
`296-598`, it is asserting **residues 37–295 can be removed** — so they are not reliably on the
surface. **The rule can only under-read, and over-reading is what folds things that are not there.**

⚠ **The anchored residue is the attachment point, not part of the folded ectodomain — hence
`anchor − 1`.**

**Verified against every observed case:** MSLN `296-597` = **302 aa**, the mature cleaved form the
ADCs bind · CEACAM5 `35-675` = **641 aa** · GPC3 `359-553` = **195 aa**, anchor on the beta subunit ·
CD160 identical bounds, no ambiguity.

### ⚠ R6.1 — The Planner's first selector excluded a validated ADC target on annotation form

The first ruling was *"the chain whose END coincides with the anchor,"* which **conflated
disambiguating among chains with testing whether a chain is valid at all.** CEACAM5 has one chain and
was excluded on a **9-residue** end mismatch that rule A never reads. ⚠ **Written by the Planner and
corrected by the Planner; recorded openly, never patched.**

### R6.2 — Rule B is BARRED, not a fallback

**`Chain` start → `Chain` end is withdrawn from `SPAN_RULES` entirely.** ⚠ **`Chain` is not the mature
protein for every entry:** it runs through the cleaved C-terminal GPI signal in **6 of 130** —
`Q96GW7` by **266 aa**, and three of the six have that segment annotated nowhere. **B fired zero
times, but a fallback that is unsafe when it fires is a latent defect waiting for an annotation to
go missing.**

### R6.3 — The chain-choice guard is threshold-free, by measurement

**Across all 128 GPI-anchored census proteins, 127 have a single candidate (ratio 1.000); exactly one
differs, MSLN at 0.538.** ⚠ **There is nothing to calibrate a constant against — any threshold below
0.538 flags nothing, any above flags only MSLN, and the number would be a dial wearing the costume of
a constant.** ⚠ **A threshold could only ever suppress flags, which is the wrong direction for a
guard.** **It fires wherever the selector had a choice at all, and the ratio travels on the row.**

**Related, measured and not inferred:** ⚠ **`len(candidates) > 1` would have lost CD160**, which
carries two chains with identical bounds. **The test is on the distinct span, not the record count.**

---

## ⚠⚠ R7 — No `assert` in a guard path. Binding beyond this instance.

> **Any check whose failure would produce a wrong artifact raises an explicit exception. Never
> `assert`.** `assert` is for internal invariants whose violation is a crash — **not for guards
> standing between a claim and a result.**

⚠ **Asserts vanish under `python -O`. A guard that disappears under an optimisation flag is not a
guard; it is a comment that occasionally runs** — and the failure is silent.

**Fold and enqueue paths are assert-free.** ⚠ **Four remain in scripts, all doing guard work, all
ruled for conversion — scripts only, no production path, D-081 not engaged, latent not live:**

- `build_heldout_set.py:238` — ⚠ **guards the held-out set against cohort contamination. A train/test
  leak, and the paper rests on that separation.**
- `build_heldout_set.py:236` — accession uniqueness
- `intersection_check.py:94-95` — ⚠ **a checker whose checks are asserts.** Its own comment says *"if
  it stops reconciling, the reports below are unsafe"* — **under `-O` the check evaluates to nothing
  and the unsafe reports print anyway. The file's entire purpose is to claim that verification
  happened.**

---

## R8 — The fold-length guards: two of them, at two ends, for two failure modes

### R8.1 — Enqueue-time, **both branches**

`check_sliced_length` beside `_fold_input`, raising `FoldLengthMismatch`. ⚠ **The checked length is
what lands in `meta['fold_length']` — the record carries the verified number rather than a second
measurement of the same string.**

⚠ **`whole` is checked too (`len == full_length`), so a `whole` row that was silently sliced now
reds.** **A guard that only runs on the path already believed correct guards nothing.**

### R8.2 — Post-fold reconciliation: the only end-to-end check

`reconcile_fold`. ⚠ **The residue count is read out of the PDB, not from a field recorded beside it —
a count taken from the same record as the claim cannot disagree with it.** **Three numbers must
agree: enqueue-time `len(fold_seq)` · manifest `span_aa` · the PDB's residue count. A disagreement
halts the crank.** No worker change.

⚠ **An absent claim is not a satisfied claim: nothing to compare RAISES rather than returning
`agrees=True`.** *An absent value is a CATEGORY*, applied to a comparison rather than to a field.

### ⚠⚠ R8.3 — The defect these exist because of

**`core/enqueue.py:81` branched on `boundary_method`, not on the presence of coordinates.** A census
row with `span_aa` and no coordinates folded **2,000 residues, `source='whole'`, nothing red.**
**Safe branch = an exact literal; unsafe branch = the default, reached by omission.** ⚠ **The census
manifest had no `boundary_method` column at all**, so ingest would have invented one — **and anything
but that single literal yields whole-sequence folds.**

⚠ **`whole` is a legitimate recorded outcome, so every artifact would have been internally
consistent — fold succeeds, recipe recorded, provenance intact, `source='whole'` — describing the
wrong molecule 3,468 times.**

**RULED and landed:** unrecognised, empty or absent `boundary_method` raises
`UnrecognisedBoundaryMethod`; **`whole` is an explicit opt-in; there is no `else` that folds
anything.** ⚠ **Authorised under a D-081 amendment block — D-081 freezes measured results and forbids
re-running them; it does not preserve a defect that fires only on inputs the cohort does not
contain.** **No-op proved on three separately-read sources: manifest 82 = `sliced_ecd` 69 + `whole`
13, unrecognised 0 · live 80, unrecognised 0 · `meta[boundary_method]` vs `meta[source]`
disagreements 0. 69 → 67 reconciles exactly on the two never-enqueued rows (D-026).**

⚠ **Found because a specified hash tuple named two fields that did not exist. A specification acting
as an audit.**

---

## R9 — Manifest identity: two keys, never one

> **The fold order stays keyed on the accession set** — reproducible across span revisions, so a
> re-parse does not scramble the queue.
> **Manifest identity is a CONTENT HASH** over sorted
> `(accession, span_start, span_end, band, tier, rule_that_produced_the_span, boundary_method,
> source_definition_version)`.
> **Both appear in provenance, labelled distinctly: `fold_order_key` and `manifest_content_hash`.**
> ⚠ **Never one number standing for both.**

⚠⚠ **The trap this closes: r1 and r3 had identical membership (3,468) and an identical fold order —
3,468 of 3,468 — while two spans differed.** **A reader diffing r1 against r3 by row count,
membership or order would have concluded nothing moved, on the revision where the whole day's work
moved.** **Not a bug in the shuffle — identity had been inherited from the shuffle key, and those are
different jobs.**

**Discriminating test: change exactly one span; the content hash MOVES and the fold order DOES NOT.**
⚠ **A membership-only test passes under the defect.** Revert proof red at
`tests/test_census_manifest.py:207`, `:235`, `:244` — **three failure-reds, with the assertion text
naming the defect it prevents.**

### ⚠ R9.1 — `identity_fn_version`, because the hashes are not one function

**r1–r3 pre-date `span_start`/`span_end`, so their content hash was computed with the coordinate
fields empty and the identity degenerates.** ⚠ **A span change moving neither band nor tier would
still collide.** **r1–r3 are `identity_fn_version: 1`, r4 is `2`, r5 is `3` — stamped
retrospectively, never recomputed.** ⚠ **Two hashes computed by different functions are never
compared without both versions named** — the same rule that governs the two span definitions and the
two `band_split` versions.

⚠ **And a rebuild states its reason. A rebuild with no stated reason is indistinguishable from a
rerun that liked its answer better.** *(Code's rule, adopted, and it applies to every regenerated
artifact in this project.)*

---

## R10 — `span_contains_transmembrane`: excluded and named, two clauses

**`Q9BQT9` — UniProt annotates `Extracellular 20-847` overlapping its own `Transmembrane 256-276`,
a `Lumenal 277-364`, and three `Cytoplasmic` domains, all inside the chosen span.** ⚠ **The record
asserts contradictory things and the largest-contiguous rule picks the inconsistent one. We would
have folded 828 residues containing a transmembrane helix, in water — and it would have succeeded.**

⚠ **Exclusion, not truncation. Truncating at 256 would invent a boundary from an entry that cannot be
trusted about boundaries** — the fifth time today that reasoning has applied.

**Two clauses:** ⚠ **any overlap of ≥1 residue with a `Transmembrane` feature** — not only full
containment, since a half-overlap is the same contradiction — **and any containment of a topological
domain in the REJECTED set**, since an extracellular span containing a `Cytoplasmic` domain asserts
both faces at once.

**Measured before implementation: both clauses catch exactly `Q9BQT9`, 1 of 3,468.** ⚠ **The narrow
version would have sufficed; the widened one costs nothing and is kept. And clause 2 independently
corroborates that the entry is internally inconsistent — two contradictions, one record.**

---

## R11 — No length floor. And what the census actually discards.

⚠ **`PLDDT_FLOOR = 50.0` is a mean-pLDDT floor applied AFTER folding, not a span-length floor.**
**There is no length floor in the cohort or the census, so the two-definitions concern dissolves —
they agree.** ⚠ **NO FLOOR IS RULED. None is added.**

**A short span folds and then stands or falls on its own confidence**, which is the right mechanism:
a fragment with no tertiary context should return low pLDDT if it returns nothing meaningful.

**MEASURED AND RECORDED, NOT ACTED ON** — so a future scoring ruling has the number: **the
span-length distribution across the 3,468 — min, quartiles, max, and counts below 50 / 100 / 150 aa.**

### ⚠ R11.1 — The largest-contiguous disclosure

**1,650 of 3,343 vocabulary rows — 49.4% — carry more than one accepted span.** **The census inherits
the cohort's rule: band on the largest contiguous segment, discard the rest.** ⚠ **Verified: rows
where `span_aa` ≠ largest contiguous = 0, across 3,343.** CCR4 folds a **39 aa** N-terminus and
discards 61 residues across three other segments; ⚠ **the manifest correctly did not sum them to
100.**

**This is a stated property of the census, not an implementation detail, and it belongs in the
manifest provenance and the paper:** *for multi-pass membrane proteins the census folds the largest
contiguous extracellular segment and discards the remainder; 49.4% of vocabulary rows are affected.*

---

## R12 — The determinism control: what it covers, and what it does not

**4a runs through `ceiling_probe --repeat 2` per arm, not through the job queue** — ⚠ **nothing is
ingested, so there is no enqueued job to fold twice.**

⚠ **It must fold the census SPAN, not the whole sequence. If the probe cannot take explicit
coordinates, that is REPORTED, never substituted.**

⚠⚠ **RECORDED LIMIT: the determinism control covers the FOLD KERNEL, not the enqueue path. Nobody may
later cite it as end-to-end determinism.** **The three-number check (R8) guards slicing and begins at
ingest — a different failure mode, a different guard, and both are required.**

**Ordering unchanged and binding:** ⚠ **two folds at one recipe, each arm, before any comparison is
computed.** **Without it, *"int8 differs from fp16"* and *"folding is nondeterministic"* are the same
observation.** ⚠ **Sample size and seed recorded BEFORE the first overlap fold. Fold the arms; do not
read the comparison — `D-078` is unwritten.**

---

## R13 — Standing, carried forward unchanged

- ⚠ **A Planner chat message cannot ratify what a committed document reserved.**
- ⚠ **The 82 are frozen** under the original span definition, permanently. **Every artifact naming a
  span states which definition produced it. Two definitions, both named, never compared without
  naming which.**
- ⚠ **No census row is scored.** Folding is not scoring; the gate is on scoring.
- ⚠ **A number carries its source; a status claim carries a PID or an mtime.** **Three fabrications
  today — a checker output, a running process, and a 352 aa span — all self-reported, all caught only
  because something downstream refused to reconcile.**

---

## ⚠ Six findings remain unnumbered, and the numbering ruling is overdue

**`F-025` was free by luck, not procedure — nothing reserved it in three places.** Queued: the KEEL
absence · *a verification sharing an implementation with its subject will agree with it* ·
*derive from source, not from context* · *an order asking for confirmation invites confirmation,
where one stating an expected value invites comparison* · *a guard placed downstream of the filter it
guards watches nothing* · *a metric answering a narrower question than its name suggests*.
