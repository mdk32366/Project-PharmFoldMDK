# ORDERS (RECONSTRUCTION) — Code — 2026-09-17 · Feature coverage, Phases 1–3

## ⚠⚠ THIS DOCUMENT IS NOT THE ORIGINAL

**This document reconstructs a lost original and is not the original.**

`ORDERS-Code-2026-09-16-feature-coverage.md` is gone. Code searched the repository, `Downloads`
(recursive) and `Documents` and found neither it nor the CSV it was built on
(`feature_coverage_census_v7_file_based.csv`, sha256 `f9104d4e…d50c4`). **Owner ruling, 2026-09-17: if it
is not in `Downloads` and not in `docs/`, it does not exist.**

This document is issued **today, 2026-09-17**, by the Planner, and reconstructs that original from the
Planner's own drafting record, the `RULING-2026-09-16`, both preworks, and the close-out.

**What that means, precisely:**

1. **This document is the authority from now on.** The lost original is not cited by anything written
   after today. Documents that already cite it keep their citations; they are historical.
2. ⚠ **It is a reconstruction, and it says so in its own title.** Any future reader who finds a
   discrepancy between this and a quotation of the original in an older document should treat the older
   quotation as the better evidence of what the original said, and **report the discrepancy** rather than
   resolve it.
3. ⚠⚠ **§1 of the original is NOT recovered, and is not reconstructed.** See §1 below.
4. **Code confirms these definitions against its own source reading before building Phase 1.** If Code
   disagrees on any key, **that stops the work** — a reconstruction is exactly the kind of document that
   must be checked, not trusted.

**Owner:** Matt Kelly · **Planner:** Claude Opus 5 · **Builder:** Code
**Grounded on:** `origin/main` @ **`1e67954`** (the #331 merge).
**Supersedes:** the lost original, in full.
**Superseded in part, on the day it was written, by:** `RULING-2026-09-16-D-168-and-session-open.md` §1 —
recorded inline below at §2.2 and §3.

---

## 1. ⚠⚠ The file-based coverage table — NOT RECOVERED

The original's §1 carried a coverage table derived from
`feature_coverage_census_v7_file_based.csv` (sha256 `f9104d4e…d50c4`), which produced the widely-quoted
**777** gap and the **141 spans over 1,026 aa**.

**The CSV is also gone.** The table therefore **cannot be re-derived, cannot be re-hashed, and is not
reconstructed here.**

⚠⚠ **Consequence, and it is a real one:**

- **Nothing written after today cites the lost §1 table as authority.** The 777 figure survives only as
  *a quotation in older documents*, not as a live measurement.
- The **only** authoritative coverage numbers from today forward are the ones Phase 1 measures against
  the live database: **C1a / C1b / C1c**, C2, C3, C4, C5.
- ⚠ The `RULING-2026-09-16` §1.1 already established that the Planner's CSV **did not model the
  `_incommensurable_assembly` short-circuit**, so its 777 **overstates the display gap**. The loss of the
  CSV removes the ability to quantify by how much from the file side. **Phase 1 measures it directly
  instead.** This is a smaller loss than it looks: the live reading was always going to be the better
  measurement.
- **`scripts/feature_coverage_report.py` therefore has no §1 table to reproduce or to differ from.** Its
  output is the measurement. ⚠ This moots the original's requirement that its output equal §1 — a
  requirement the ruling had already superseded for a different reason (§4 of the Planner prework).

**Nothing is reconstructed in this section. The gap is the record.**

---

## 2. Decisions before anything is extracted

### 2.1 Owner — the population (scope) · RECOVERED

| population | Planner recommendation |
|---|---|
| **P1** — every current census **representative** with a structure (`/api/census`, **3,463 folded**) | **in** |
| **P2** — the cohort 82 (tranche 0), coverage **measured** in §3 before assuming it is complete | **in, if C3 shows a gap** |
| **P3** — Run-2 rows | **out as a population.** A **stratified sample of ≤ 100** only, as an instrument check: Run-1 vs Run-2 features for the same accession. That tests `A10.2`'s `mean_plddt` equality at the feature level. |
| **P4** — tile windows | **out** |

⚠ **Still an open owner decision.** Not ruled as of this issue.

### 2.2 Features on ASSEMBLED structures · RECOVERED, THEN SUPERSEDED IN PART

**What the original said:** for proteins over the trained window the representative structure may be
**assembled from tiles**, and four of the six features are confidence or geometry statistics that, on a
stitched structure, mix tiles folded as separate inferences with boundary effects at the seams:

- `mean_plddt_ecd`
- `membrane_proximal_plddt`
- `radius_of_gyration`
- `largest_patch_fraction`

Whether such a vector is **commensurable** with a single-inference vector is not an engineering question.
It is a scientific ruling, on the `D-094` pattern, and it is `D-168`.

⚠⚠ **SUPERSEDED, per `RULING-2026-09-16` §1 — Planner error 9:**

| the original proposed | the ruling |
|---|---|
| a new profile category `refused_assembled_structure` | ⚠ **SUPERSEDED. Reuse `refused_assembled_incommensurable`**, which the tree has shipped since `D-120`. Code found this by reading source. **Credited.** |
| tiles-only parents get `no_protein_level_structure` | ⚠ **SUPERSEDED as a profile category.** `_incommensurable_assembly` already returns true for a tile row. If the distinction is still wanted it belongs to the **extraction** artifact's outcome vocabulary, never as a second profile refusal. |
| the `structure_kind: assembled` tag in the artifact | **STANDS.** It records what the extractor measured, and it is **not** a refusal. |
| "extract tagged, ingest tagged, profile refuses" | **STANDS in shape**, but the refusal is decided at profile time from the row, by `_incommensurable_assembly` — not by anything the extractor writes. |

**`D-168`'s actual subject, per the ruling §1.2:** not a category. The **commensurability** question — may
features measured on an assembled chain be compared with, pooled with, or fitted alongside features from a
single-pass fold?

**OWNER RULING, 2026-09-17: store tagged, NEVER pool** into a fit or a support range with single-pass
vectors. Accepted.

⚠ **`D-168` must also state plainly that extracting features for assembled parents changes nothing any
page displays**, or the work will look like it failed. **Extraction may proceed after `D-168`; ingest may
not.**

### 2.3 Owner — the paper's pins · RECOVERED

- Anything sealed or cited that was computed from `census_features.v1` **keeps citing v1 by sha256**
  (`c08f9f1d…1863`).
- **v2 is additive.** Replacing v1 in any sealed analysis requires a ruling.
- ⚠ Code greps `docs/` for every citation of `census_features.v1` and of `c08f9f1d` and **lists them
  before ingest.** Seven such documents are known to exist.

### 2.4 Planner rulings — architecture

**2.4.1 · RECOVERED — same instrument, proven, not assumed.**
- v2 must report `feature_version == e67a8cf30c1c`.
- ⚠ If `core/features.py` has changed since `8db7345` and the version differs, **STOP**: that is a second
  instrument and it gets its own D-entry.
- **Calibration:** v2 re-extracts **every** v1 row, not a sample. It is cheap — v1's 2,690 rows took 38
  minutes. It requires **exact equality** of all features, extended ones included, wherever the
  representative `analysis_id` is unchanged.
- Any difference is a **finding**: two paths to one quantity.
- ✅ **Already measured and accepted** (`RULING-2026-09-16` §2): `feature_version()` reads `e67a8cf30c1c`
  and `git log` over `core/features.py` since `8db7345` is empty. **The stop condition does not fire.**
  This is what makes the v1-equality calibration meaningful rather than circular.

**2.4.2 · ⚠ NOT RECOVERED.** No reconstruction attempted.

**2.4.3 · RECOVERED IN SUBSTANCE — categories are never folded together.** Each named outcome keeps its
own name; a second name for one thing is a defect. ⚠ This is the clause the original's own §2.2 violated,
which is Planner error 9.

**2.4.4 · RECOVERED — the bracketing run.** Phase 2 runs the **10 largest** first and **reports before the
full pass.**

**2.4.5 · ⚠ NOT RECOVERED.** No reconstruction attempted.

**2.4.6 · RECOVERED — `census_ingest_features.py` carries `D-159` and the role preamble** before Phase 3.

⚠ **Two of six clauses are unrecovered. If Code's source reading turns up an architecture constraint that
this document does not state, that constraint is real and this document is incomplete — report it, do not
assume it was dropped deliberately.**

---

## 3. Phase 1 — one read-only tunnel: the live coverage · RECOVERED, WITH THE RULING FOLDED IN

Extend the R1–R4 instrument. **Tests first**, `SET TRANSACTION READ ONLY`, role preamble, `D-159`.
**Every count reads its own `count(*)`; every list is labelled capped if capped (A9.3).**

⚠ **Phase 1 runs in the SAME tunnel as R1–R4.** Not a second tunnel.

### 3.1 Pre-registered readings

| reading | key | expectation |
|---|---|---|
| **C1** | census representatives — via `choose_census_representative` **imported from `app/reads.py`** (one home, never re-implemented) — with **no `protein_features` row** | ⚠ See §3.2: **split into C1a / C1b / C1c.** Original expectation **≥ 773**, close to the file gap minus never-folded rows. ⚠ A **smaller** number means features were ingested from some other source: **finding.** |
| **C2** | representatives **with** a `protein_features` row whose `analysis_id` ≠ the representative's id | a **named category** — stale representative — with count **and ids**. Expectation not pre-set; **the count is the measurement.** |
| **C3** | cohort tranche-0 analyses with no `protein_features` row | measured. **Decides P2.** |
| **C4** | **C1a** broken down by `structure_kind`: assembled parent / tiles-only / single-pass | measured. Sizes §2.2's ruling. |
| **C5** | was `census_features.v1` ever **ingested**? — `protein_features` rows whose `analysis_id` ∈ v1, with **feature equality on a 50-row sample** | confirms which artifact the profile panel is actually reading |

⚠ **Before C5, Code states from source where the profile panel's features come from.** The original's §1
*assumed* the table via `census_ingest_features.py`; the v1 manifest records
`wrote_database_rows: false`, because that write happens at ingest.
✅ **Already established** (`RULING-2026-09-16` §2): the panel reads the **`protein_features` table**, not
the artifact. **C5 is therefore the load-bearing reading of Phase 1** — it decides whether v1's **2,690**
rows ever reached the table. **C5 is reported first, before anything else in Phase 1.** If they never
arrived, the whole coverage picture changes.

### 3.2 ⚠⚠ C1 and C4 report THREE numbers, not one — `RULING-2026-09-16` §1.1

`census_profile_statuses` (`app/census_profile_read.py:127–129`) tests `_incommensurable_assembly(row)`
**first and `continue`s.** The feature row is never consulted for assembled parents or tile windows.
Verified in source by Code, 2026-09-17.

**Consequence: such a row displays `refused_assembled_incommensurable` whether or not it has features.**
So "has no feature row" and "would gain a rendered profile" are **different quantities.**

| key | counts |
|---|---|
| **C1a** | census representatives with **no `protein_features` row** |
| **C1b** | **of those**, how many **already refuse as assembled** — extraction changes nothing visible for them |
| **C1c** | **C1a − C1b** — rows that would actually gain a rendered profile. ⚠⚠ **ONLY THIS IS THE COVERAGE GAP.** |

**Code states each key with its reading.** A bare number is not a C1.

### 3.3 `scripts/feature_coverage_report.py`

**Tests first.** It does not exist yet. It **models the `_incommensurable_assembly` short-circuit**, or it
reproduces the Planner's CSV error.

**Its tests pin:** an assembled parent with **no** feature row is counted under **C1b**, not C1c; a
single-pass row with no feature row is counted under **C1c**.

⚠ Per §1, there is **no §1 table for it to reproduce or to differ from.** Its output is the measurement.
It **reads and reports only** — there is nothing in it to deploy.

---

## 4. Phase 2 — extraction v2 (no production access) · RECOVERED

1. **Tests first:**
   - the `--out` / `--manifest` override;
   - ⚠ **refusal to write to any path whose basename is `census_features.v1*`**;
   - the new outcome categories, and the `structure_kind` tag;
   - the per-protein timeout producing `extraction_timeout`;
   - `PYTHONHASHSEED` pinned in the manifest;
   - the v1/v2 equality comparator — equality passes; a one-float change **fails on exactly that
     accession and feature**; a changed `analysis_id` goes to **its category, not to a difference**.
2. **The bracketing run on the 10 largest (§2.4.4). Report before the full pass.**
3. The full pass, **owner's go-ahead**, locally.
   - ⚠ Run with `PYTHONUTF8=1` if the console is piped (A6/A7's lesson). Better: **the extractor writes
     its own log file.**
4. **Pre-registered outcome table, all four at equal prominence:**
   - (a) v1 rows reproduce **exactly**;
   - (b) v1 rows **differ** — ⚠ **STOP**, finding;
   - (c) the category sums equal `/api/census` rows **exactly**;
   - (d) the gap resolves into `ok` **plus named categories only** — no blank, no skip.
5. The comparator report and the v2 artifact are committed, **with sha256 in the manifest.**

---

## 5. Phase 3 — ingest (a later sitting; owner at the keyboard) · RECOVERED

Only after **all three**:

1. **`D-168` is ruled** (§2.2) — ✅ owner ruling given 2026-09-17: store tagged, never pool. The entry
   itself is still to be **written.**
2. The **§2.3 citation list** is produced and reviewed.
3. **`census_ingest_features.py` carries `D-159` and the role preamble** (§2.4.6).

---

## 6. What this document does not authorise

It authorises **nothing today.** `ORDERS-Code-2026-09-17-R1-R4.md` governs the current work, and Phase 1
opens only when R1–R4 have been reported and the owner says so.

⚠ Phase 1 also requires the still-open owner decision on the **P1–P4 population** (§2.1).

**Planner error count, carried: 10.**
