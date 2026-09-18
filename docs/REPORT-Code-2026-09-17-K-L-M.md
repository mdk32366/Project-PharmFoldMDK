# REPORT — Code → Planner — 2026-09-17 · TASK K (coherence), TASK L (the eighth outcome), TASK M (the folded-flag provenance)

**Owner:** Matt Kelly · **Planner:** Claude Opus 5 · **Builder:** Code
**Written:** 2026-09-17, late afternoon PDT. **Governs:**
`ORDERS-Code-2026-09-17-offline-coherence-eighth-outcome-and-folded-flag.md`.
**Branch:** `d167-r1r4-population-read`, PR #332, head **`95d6c21`**.

> ⚠ **All three tasks were offline.** No database, no tunnel, no network. **Nothing was changed by
> TASK M** — no label, no flag, no copy. **All three completed; none stopped.**
> **No integer was spent.** Pointers unchanged: `D-169` · `F-083` · `A-032`.

---

## 1. TASK K — the coherence check, computed from the artifacts

⚠ **Read from the four committed JSON artifacts on disk, not from any restated number.**

| # | claim | measured | from |
|---|---|---|---|
| **K1** | representatives **3,466**, of which **776** hold no feature row ⇒ **2,690** hold one | **3,466 − 776 = 2,690** ✅ | `c1_read.json` + diagnostics |
| **K2** | `C5` found **2,690** v1 ids in `protein_features`, 50/50 equal | **v1 ids 2,690 · in table 2,690 · sample 50 checked, 50 equal, 0 differing** ✅ | `c5_read.json` |
| **K3** | `C2 = 0` — no representative's features hang off a stale `analysis_id` | **0, with an empty id list** ✅ | `c2_c3_c4_read.json` |
| **K4** | ⇒ the covered set IS v1's set, with nothing from an unaccounted source | ⚠ **SUPPORTED** — see §1.1 | K1 ∧ K2 ∧ K3 |

**The three numbers interlock exactly.** There is no near-miss and no rounding: `3,466 − 776`,
`2,690` and `2,690` are the same integer, and `C2 = 0` closes the route by which a representative's
features could belong to a different row.

⚠ **Recorded as a COHERENCE CHECK ACROSS THREE INDEPENDENT READINGS — corroboration, not a new
finding, and not a new integer.** It answers the concern behind the floor: *a smaller `C1a` would
mean features from an unaccounted source.* **There is no such source.**

### 1.1 ⚠ One boundary on K4, stated because the claim is easy to over-read

**K4 holds for the CENSUS REPRESENTATIVE population.** It is **not** a statement that
`protein_features` contains exactly 2,690 rows.

**`C3 = 0` proves the opposite for the other population:** every cohort tranche-0 analysis **has** a
feature row, so the table also holds cohort rows. ⚠ **Two populations, two accountings** — the same
distinction `SPEC v2` §1.1 exists to protect, applied here to the table rather than to the accession
sets. **The total row count of `protein_features` was not measured today** and is not claimed.

### 1.2 K5 — consistent, and stated as consistent

**`C1b` = 45 and `C4`'s assembled branch = 45**, which is the entire `assembled_served` population
recorded at `decisions.md:2860`. ⇒ **Not one assembled representative holds a feature row.**

⚠ **This is consistent, not surprising:** the assembled parents are exactly the rows the profile
short-circuits on, so nothing ever extracted features for them. **It is also the number that sizes
`D-168` §4's claim** — extraction over those 45 would change nothing any page displays.

### 1.3 K6 — a footnote, and deliberately not a calculation

**`C1a` = 776.** The void file-based figure was **777**. ⚠⚠ **Nothing reconciles against it, and the
difference is not computed here** — the source CSV is gone (`RECONSTRUCTION` §1) and the figure
survives only as a historical quotation. **It is recorded as a footnote and chased no further.**

### 1.4 The rest of the interlock, since it was on disk anyway

`C1c = C1a − C1b` → **731 = 776 − 45** ✅ · `C4` sums to **776** = `C1a` ✅ ·
representatives **3,466** + accessions with no representative **1** = **3,467**, the census
population exactly ✅.

---

## 2. TASK L — the eighth outcome, pinned harder (`95d6c21`)

The outcome itself shipped at `06aea65`, raised as a **reported addition** rather than a silent fold.
Now that it is **ruled in**, the tests pin what the ruling requires:

1. ⚠⚠ **An identity failure and a length failure are TOLD APART.** Two fixtures, each differing in
   one dimension: a **long** overlap (301 residues) at **71% identity** → `overlap_identity_below_minimum`;
   a **short** overlap (21 residues) at **99% identity** → `overlap_below_minimum`. The first is
   asserted to **clear** the 50-residue minimum and the second to fall **below** it, so the two
   cannot be confused by an assertion that happens to pass.
2. **It is never `no_pdb_entry`** — that would report our filter as nature's absence.
3. **Both sum checks are against eight**, each naming its population: a pass whose rows all land in
   the new outcome still reconciles against **82** and against **3,467** separately. ⚠ The sum walk
   is asserted to iterate `OUTCOMES` **itself**, so no outcome can be invisible to it.
4. **The new outcome prints even when zero** (`D-027` at the reporting surface).
5. **Offline still enforced by test**; the CLI still refuses a non-local `--source`. ⚠ **No live
   client came into existence.**

**Local: 39 in the T0 suite, full suite 2,811 passed.** CI running on `95d6c21`.

---

## 3. ⚠⚠ TASK M — the folded-flag provenance. **A reading. Nothing was changed.**

### 3.1 Where the flag comes from

| step | source |
|---|---|
| the picker returns a **kind** | `app/reads.py:947` `choose_census_representative` → `"assembled"` · `"tiles_only"` · `"mucin"` · `"single-pass"` |
| the kind sets **`folded`** | `app/reads.py:1001` `apply_structure_kind`: `True` for `assembled` / `single-pass`; **`False` for `tiles_only` and `mucin`**, which also set `mean_plddt = None`, `not_folded_reason`, `not_folded_copy` and `profile_status = "not_folded"` |
| the same rule, named once for consumers | `app/reads.py:141` `STRUCTURE_KINDS_WITH_A_FOLD = {"assembled", "single-pass"}`, used for the bridge payload at `:685` |
| the surface decides the axis | `ui/src/structureStatus.js:63` `structureServed`: `tiles_only` first, then **`r.folded === false` → `STRUCTURE_NONE`** |
| the copy | `ui/src/structureStatus.js:83` `NOT_FOLDED_COPY = 'NOT FOLDED'` (and `:84` `NOT FOLDED HERE` for the cohort-fold case), chosen in `structureServedLabel` |

### 3.2 ⚠⚠ Can a `pending` row produce `NOT FOLDED`? **Yes — and job status is never consulted.**

The path, in source:

1. `choose_census_representative` (`app/reads.py:985–991`) builds `mucin_rows` from rows whose
   `hold48_kind == "mucin"` **or** whose accession is in `MUCIN_ACCESSIONS`, and `non_tile_folded`
   from rows **with a `pdb_path`**.
2. **If there are mucin rows and no row carries a `pdb_path`, the kind is `"mucin"`.**
3. `apply_structure_kind` sets **`folded: False`**.
4. The surface reads `folded === false` and prints **`NOT FOLDED`**.

⚠⚠ **The decision turns on the ABSENCE OF A `pdb_path`, never on `jobs.status`.** MUC16's single
row is `pending` with no artifact, so it is invisible to the label either way: **a `pending` row and
a `failed` row and no row at all all produce the same `NOT FOLDED`.**

### 3.3 Does `structure_kind: mucin` participate? **Yes, and it is decided by accession identity**

`MUCIN_ACCESSIONS` is a hard-coded frozenset at **`core/hold48.py:51`** — `Q8WXI7`, `Q9UKN1`,
`Q685J3` — *"Named by the GO. The category is the molecule, not the length (D-109 ruling 3)."*
⚠ So the mucin branch is reached **because of which protein it is**, independent of any row, any
status, and any artifact.

### 3.4 ⚠ Which of the orders' two readings the source supports

**The source supports reading 1: the label is the honest permanent state, and the `pending` rows are
the stale artifact.**

- The label is a claim about **what structure exists** (no `pdb_path`) plus a **standing class
  ruling** (`MUCIN_ACCESSIONS`, `decisions.md:6883`'s `out_of_class`). **Both are true today.**
- It is **not** a claim about the queue, and it cannot become one: no branch in the path reads
  `jobs.status`.

⚠⚠ **But one string does make a queue claim, and it is the one that contradicts the rows:**
`app/reads.py` sets, for the mucin branch,

> *"mucin — out of class; never ESMFold (D-111). **Rental is closed (pod Terminated)**"*

**The enqueued `pending` rows are precisely what "rental is closed" implies does not exist.**
⚠ So the tension the Planner identified is real, and it lives in the **copy's second clause**, not in
the `folded` flag. **Code changed nothing, and does not rule which side is wrong** — the owner
decides whether the three pending rows should be retired or the sentence should stop describing the
queue.

⚠ **One consequence worth having on the record either way:** because the label never reads
`jobs.status`, **retiring those rows would change no surface**. The two candidate fixes are not
symmetric in cost.

---

## 4. What Code asks the Planner for

1. **Accept K4 as corroboration** with §1.1's boundary — the interlock is over census
   representatives, and `protein_features` also holds cohort rows (`C3 = 0` proves it).
2. **Note §3.4's asymmetry:** retiring the three pending mucin rows would change **no** surface,
   because the label never consults job status. That may make the owner's decision cheaper than it
   looked.
3. **Confirm nothing further is offline-doable today**, or issue the next orders. ⚠ The cohort-account
   query (what the three missing accessions hold **instead**) is already ordered for the next tunnel
   and was **not** attempted.
