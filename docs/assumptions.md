# PharmFoldMDK — The Assumption Register (`assumptions.md`)

> **The question this document answers (KEEL-4 §2): "What are we taking for granted?"**
>
> ⚠ **This file is AUTHORED, and it is the one KEEL document a script could not have produced.**
> A register cannot be reconstructed from the log — KEEL-4 §7 is explicit that you seed it from the
> breaks you already know about and then **register forward**. Entries below were seeded by hand on
> 2026-09-11 against the log at `836a9a3`, and landed by **`D-156`**.
>
> **Companions:** [`decisions.md`](decisions.md) (*why is it like this?*) ·
> [`findings.md`](findings.md) (*how do we know?*) · [`RESERVED.md`](RESERVED.md) — the allocator,
> which holds **the next free `A-` integer** and moves it in the same commit that spends one.
>
> **Every claim names how it is known (`D-016`).** The measurements in this file were taken with
> `grep` over the working tree at `836a9a3`; each one states its command.

---

## 0. Why this file exists, and what it cost to not have it

KEEL-4 V9 opens with a PAID FOR IN BLOOD note:

> *While it sat unruled, three assumption numbers were assigned locally by a project that needed
> them and had never received this page. They are cited in shipped code and in test docstrings, and
> they resolve to nothing.*

**That project is this one, and the three numbers are `A-014`, `A-016` and `A-017`.**

**How known (`D-016`):** `grep -rnE "\bA-[0-9]{3}\b"` over `core/ app/ scripts/ tests/ worker/ db/
ui/src` and over `docs/ ARCHITECTURE.md`, working tree at `836a9a3`:

| id | code files | code citations | doc citations | in the log |
|---|---|---|---|---|
| `A-014` | 2 | 2 | 64 | 18 |
| `A-015` | 0 | 0 | 5 *(all of them declining to use it)* | 0 |
| `A-016` | 7 | 8 | 62 | 18 |
| `A-017` | **21** | **61** | 75 | 15 |
| **total** | **30** | **71** | **201** | **51** |

⚠⚠ **71 citations in shipped code and 201 in documents, every one resolving to a register that did
not exist until this file.** `docs/RESERVED.md` has held the three rows since 2026-08-04/05 with
their provenance intact — so the reasoning was never lost — but a reader following `A-017` out of a
test docstring had nowhere to arrive.

---

## 1. The reconciliation `RESERVED.md` demands — run here for the first time

`docs/RESERVED.md` lines 70–88 marks all three numbers **provisional** and blocks them on a document
the repository had never received:

> *`A-017` is the lowest integer above every `A-` number known here; it must be re-confirmed against
> KEEL-4 at merge, and `A-015` was deliberately not taken because KEEL-4 is recorded as holding items
> 15/16/17 and the mapping is unverifiable from here.*
>
> *⚠ **Nothing is renumbered.** `A-014`, `A-016`, `A-017` keep their integers. **The reconciliation
> when KEEL-4 lands must check all three**, not only `A-017`.*

**KEEL-4 has since landed** — `docs/keel/KEEL-4-assumption-register.md`, **V9**, derived from
`KEEL-4-The-Assumption-Register-V9.docx`, sha256 `5c5912…c367f`. The reconciliation is now due, and
below is its result.

**Finding 1 — KEEL-4 V9 assigns no numbers to this project, so the feared collision does not
materialise.** **How known (`D-016`):** `grep -cE "A-0[0-9][0-9]" docs/keel/KEEL-4-assumption-register.md`
returns **1 line**, and that line is §4's citation example — *"Cite an entry by number AND name —
A-007 (every feature row carries six features), never a bare A-007."* `A-007` is illustrative, and its
subject matches the seed project named in KEEL-4 §6, not anything here. **V9 contains no assignment of
15, 16 or 17.**

**Finding 2 — therefore `A-014`, `A-016` and `A-017` are CONFIRMED at their integers**, and the
provisional flag in `RESERVED.md` can be lifted. This is the outcome the 2026-08-05 session was
protecting: it *"declined `A-015` in a namespace it cannot verify, took the lowest safe integer, and
wrote the provisional reasoning into the row itself"* (`CLOSEOUT-2026-08-05.md`). The caution was
warranted and is now discharged.

⚠ **What this reconciliation cannot rule out.** It is evidence about **V9 as committed here**, which
is itself a derived Markdown of an owner-authored `.docx`. If an external master assigns 15/16/17
elsewhere, this repository cannot see it. **The check is against the received document, and that is
all it is.** Re-run it if a later KEEL-4 version lands.

**Finding 3 — the inherited three are named as *lessons*, not as *assumptions*, and the schema wants
the assumption.** `A-014` is written as *"an upstream model's negative class is a prediction, not a
fact"* — a true statement, the corrected form. KEEL-4 §4 asks for *"the assumption, as a falsifiable
proposition"*, and its own example (`A-007`, *every feature row carries six features*) is the thing
taken for granted, i.e. the **false** one. ⚠⚠ **The three are NOT renamed here.** They are cited by
name in 71 places in shipped code, and KEEL-4 §4 makes the name load-bearing precisely so a wrong
citation is wrong on sight. **New entries from `A-018` follow the schema; the inherited three keep
their cited names, and this paragraph is the reconciliation of the two conventions.**

---

## 2. The namespace

- **`A-001` – `A-013`** — **never assigned by this repository.** The namespace opened at 14 because
  the 2026-08-05 session took the lowest integer it could prove safe, not because 1–13 exist here.
- **`A-014`, `A-016`, `A-017`** — inherited, cited in shipped code, **confirmed** in §1.
- **`A-015`** — ⚠ **deliberately never taken**, and it stays empty. Skipping it was the act that made
  the other three safe; filling it now would erase the reasoning. **Do not reuse this integer.**
- **`A-018` onward** — opened by this file.

---

## 3. The register

### A-014 — an upstream model's negative class is a prediction, not a fact

- **Registered:** 2026-08-04 · **Status:** **BROKE** *(confirmed at this integer 2026-09-11)*
- **Relied on by:** `core/span_definition.py:75` · `core/structural_profile.py:60` · `F-011` ·
  `F-019` *(reserved)* · `D-075 amd 1` · `D-079 amd 6` · `D-079 amd structural-profile` ·
  `D-093 amd 2` · `D-095 amd 2` · the three `D-093` pooling-surface drafts — **named in 11 of the 25
  *"Assumptions relied on"* fields in the log**, ⚠ of which **2 name it only to record that it does
  NOT apply** (*"IHC is an assay, not a model"*). **Actual reliances: 9.**
- **What breaks if false:** the census itself. The surfaceome filter that produced it and the
  cohort's labels are both model outputs, and `D-075 amd 1` relies on it **twice, in opposite
  directions**.
- **The test:** `F-011` — ask whether the classifier's negative class means *"cannot be a target"* or
  *"was not predicted to be one"*. It is the latter, and the excluded class may hold the best
  therapeutic window.
- **Guard:** none structural — it is a claim-discipline rule enforced by review (`D-094`). ⚠
  `D-093 amd 2` records the boundary explicitly: *IHC is an assay, not a model, so `A-014` does not
  apply to those edges.*

### A-016 — any red proves the assertion bites

- **Registered:** 2026-08-04 · **Status:** **BROKE** *(confirmed at this integer 2026-09-11)*
- **Relied on by:** 7 test modules, 8 citations — `tests/test_clinical_layer_prohibitions.py:243` ·
  `tests/test_d141_land_confidence_kabsch.py:394` · `tests/test_d144_census_structural_rank.py:189` ·
  `tests/test_d146_track_b_live_api_copy.py:115,165` · `tests/test_d149_cancer_burden.py:122` ·
  `tests/test_d151_ui_polish.py:188` · `PAPERS-v2.md` P-001's methods correction.
- **What breaks if false:** every *"proven by revert"* claim in the log, including the ones carried
  into a paper's methods section.
- **The test:** revert the component and read **where** the red fired. An error-red and a failure-red
  are different objects; the revert must be a realistic mistake and it must fail **at the assertion**.
  Originates in a guard that reddened as a *collection error* (`F-012` session) and looked like proof.
- **Guard:** convention, enforced per-test by docstring. ⚠ Not structural — nothing fails if a future
  revert proof skips the check.

### A-017 — the fixture must reach the code under test

- **Registered:** 2026-08-05 · **Status:** **BROKE**, then **GUARDED** *(gate requirement; confirmed
  at this integer 2026-09-11)*
- **Relied on by:** ⚠⚠ **21 test modules, 61 citations — the most load-bearing assumption in the
  suite.** `test_census_spans_v2` · `test_census_manifest` · `test_census_ingest_claim_contract` ·
  `test_census_reparse_preserves_fetch_date` · `test_census_task2_task3_contract` ·
  `test_clinical_layer_prohibitions` · `test_d145_bake_structural_loader` ·
  `test_d146_track_b_live_api_copy` · `test_d147_ecd_intermittent_flag` · `test_d149_cancer_burden` ·
  `test_docs_landing_headers` · and 10 more · plus `D-093`, `D-094`, `F-040`, `BRIEFING-copy-about-adcs`.
- **What breaks if false:** a green suite means nothing. Five instances were caught by two agents
  across three tasks **in one day** (`CLOSEOUT-2026-08-05.md`).
- **The test:** three clauses, each earned by a dated instance —
  **(a)** the fixture must reach the code; **(b)** each property needs its own test, since a compound
  test proves only its first failing assertion; **(c)** the fixture must contain a case where correct
  and incorrect differ.
- **Guard:** ✅ **a gate requirement** — positive controls are asserted rather than assumed
  (e.g. `test_the_fixture_for_the_ordering_test_is_not_degenerate`;
  `assert checked == 1649, "the loop must actually visit every flagged row (A-017)"`).
- ⚠⚠ **And it is named by ZERO decision entries.** The assumption cited 61 times in the test suite
  appears in no *"Assumptions relied on"* field anywhere in the log (§5). **The mechanism KEEL-4 §5.1
  relies on is not carrying its heaviest entry.**

---

## 4. Seeded from known breaks — `A-018` onward

> ⚠⚠ **SURVIVORSHIP, AND IT IS THE WHOLE CAVEAT (KEEL-4 §6).** Every entry below was seeded from a
> finding that records a break. **An assumption that held quietly was never written down**, so the
> denominator is unknown and unknowable backwards. These rows calibrate nothing on their own; the
> register becomes an instrument only for assumptions registered **before** they are tested, which is
> what `A-030` onward is for.

### A-018 — a green test suite means the behaviour exists in production

- **Registered:** 2026-09-11 *(retroactive, from `F-054`, 2026-08-20)* · **Status:** **BROKE**
- **Relied on by:** every gate-green merge claim; `D-093`'s clinical layer; the `A-016`/`A-017` family.
- **What breaks if false:** `F-054` — **1,012 green tests certified a feature ENTIRELY ABSENT from
  production**, and a broad `except` converted one attribute error into **777 silently missing rows**.
- **The test:** assert that a **row comes back**, not that the code has a shape. Cost: one integration
  test per surface.
- **Guard:** partial — `A-017` clause (c) is a gate requirement, but it governs fixtures, not the
  shape-vs-behaviour distinction. ⚠ `F-054` is **OPEN**.

### A-019 — the test engine and the production engine reject the same things

- **Registered:** 2026-09-11 *(retroactive, from `F-056`, 2026-08-21)* · **Status:** **BROKE**
- **Relied on by:** the entire suite's authority over the census ingest path.
- **What breaks if false:** `F-056` — **2,690 census cards were 500 in production while the suite was
  green.** The test substrate forgives exactly the mistake production rejects.
- **The test:** run the contract tests against the production engine. Cost: a Postgres service in CI.
- **Guard:** ⚠ none at the time of the finding; `F-056` is **OPEN** and closes when no test's
  correctness depends on the substrate.

### A-020 — a measured-success VRAM envelope is a property of the recipe, not of the card

- **Registered:** 2026-09-11 *(retroactive, from `F-062`, 2026-08-31)* · **Status:** **BROKE**
- **Relied on by:** `preflight`; the local/rental routing; the rental budget in
  `BUDGET-hold48-tiers-2026-09-04.md`.
- **What breaks if false:** `F-062` — `S-005`'s 6,665 MiB envelope produced a **FIT** verdict on a
  Blackwell card with `free_before=7043` MiB, and the fold raised **CUDA OOM at ~12.9 s**. Being within
  1.45% of the `F-059` law did not certify headroom.
- **The test:** gate on a measured success recorded on the **same card / recipe / allocator fraction**
  that will fold. Cost: one measurement per card before it is trusted.
- **Guard:** `preflight` refuses an absent measurement (`F-061`). ⚠ Both findings **OPEN**.

### A-021 — releasing VRAM in-process restores free memory for the next preflight

- **Registered:** 2026-09-11 *(retroactive, from `F-064`, 2026-08-31)* · **Status:** **BROKE**
- **Relied on by:** every multi-tile local batch; the process model of the fold worker.
- **What breaks if false:** `F-064` — after a successful fold, **free collapsed 7043 → 1649 MiB while
  reserved stayed ~6900**; after process exit the card was free again. The second tile's preflight
  reads a number that describes the first tile's allocator, not the card.
- **The test:** fold two tiles in one process and read `free` before the second preflight.
- **Guard:** process-per-tile is the prescribed next gate. ⚠ `F-064` **OPEN**; do not lower
  operational max below 380 on this evidence alone.

### A-022 — sequence length is the binding constraint on whether a fold fits

- **Registered:** 2026-09-11 *(retroactive, from `F-053` 2026-08-20 and `F-059` 2026-08-22)* ·
  **Status:** **BROKE**
- **Relied on by:** `CEILING_KNOWN_GOOD = 440`; the ceiling climb; `preflight`; the tranche cost model.
- **What breaks if false:** `F-053` — the constant **is a LENGTH**, and what actually binds is
  **~1.26 GiB of headroom against a 5.24 GiB resident model**; *"the guard, the climb and the preflight
  all measure the wrong axis."* `F-060` then split a cost plan on a constraint that had stopped binding.
- **The test:** `F-059` — incremental VRAM is **O(L²)**, and the band `D-077` called UNMEASURED was
  **measurable from ten folds already committed**. ⚠ **No new fold was needed to falsify this.**
- **Guard:** ⚠ none yet — both findings close only when the fold path constrains on headroom.

### A-023 — `scorer_version` identifies the parameters a run used

- **Registered:** 2026-09-11 *(retroactive, from `F-049`, 2026-08-19)* · **Status:** **BROKE**
- **Relied on by:** `D-041`'s reproducibility claim; `D-079 amd 3`; `F-052`.
- **What breaks if false:** `F-049` — it establishes that two runs used the same **CODE**, never the
  same **PARAMETERS**, and **nothing persisted makes the reproducibility claim checkable.**
- **The test:** try to reconstruct a past run's parameters from what is stored. It cannot be done.
- **Guard:** ⚠ none. `F-049` **OPEN** on a narrowed claim.

### A-024 — a join key that was unique stays unique

- **Registered:** 2026-09-11 *(retroactive, from `F-031`, 2026-08-16)* · **Status:** **GUARDED**
- **Relied on by:** every `select(ProteinAnalysis…)`; the feature loader (`F-021`).
- **What breaks if false:** `F-031` — two populations in one table, joined on a key no longer unique,
  silently mixing rows from different runs.
- **The test:** insert a second run's row and re-run the join.
- **Guard:** ✅ `uq_protein_features_analysis_id` — the constraint closes `F-021` clause 1, and
  `F-031` is **CLOSED under `D-074`**. ⚠ **The only entry in this register with a structural guard
  and a closed finding.**

### A-025 — an absent value is distinguishable from a row that was never fetched

- **Registered:** 2026-09-11 *(retroactive; three instances)* · **Status:** **BROKE**
- **Relied on by:** the span filters; the scorer's ablation path; `/api/coverage`.
- **What breaks if false:** three separate ways —
  `F-036`: a row never fetched carries an **empty** `span_category`, so *"unknown"* and *"has a span"*
  are the same filter ·
  `F-020`: an **absent measurement coerced to zero and fit as though measured**, which would have
  returned `D-075` Decision 4's ambiguous row **for the wrong reason** ·
  `F-018` *(reserved, unwritten)*: an absent status recorded as an affirmative one — *the absent-value
  rule violated in the passing direction*.
- **The test:** ask the store for a value it was never given and see whether the answer is
  distinguishable from a real one.
- **Guard:** partial — the `geom_proxy` guard shipped for `F-020`; nothing covers the general class.
- ⚠ Closely related to `F-010`, the `analysis_id` that *"held one only on success"* — named in KEEL-4
  §6's PAID FOR IN BLOOD catalogue, drawn from this project.

### A-026 — the pipeline captures everything the model emits that we might want later

- **Registered:** 2026-09-11 *(retroactive, from `F-042`, 2026-08-17)* · **Status:** **BROKE**
- **Relied on by:** every analysis that would need per-residue error estimates; `P-001`.
- **What breaks if false:** `F-042` — **ESMFold emits PAE on every forward pass and the pipeline
  discards it: 2,690 of 2,690 census folds carry none.** Any PAE-dependent analysis now costs a
  re-fold of the entire census.
- **The test:** enumerate the model's outputs against the fields persisted. One read of the forward
  signature would have shown it.
- **Guard:** ⚠ none.

### A-027 — a folded monomer's exposed surface is antibody-accessible

- **Registered:** 2026-09-11 *(retroactive, from `F-040`)* · **Status:** **BROKE**
- **Relied on by:** ⚠⚠ **the platform's primary output.** Every structural accessibility score, and
  the ADC-target ranking built on it.
- **What breaks if false:** `F-040` — **ESMFold folds MONOMERS**, so an obligate oligomer's **subunit
  interface is indistinguishable from an antibody-accessible patch**. A buried interface scores as
  exposed surface.
- **The test:** check the oligomeric state of a scored target and ask whether the exposed patch is an
  interface. Cost: an oligomer annotation per target.
- **Guard:** claim discipline under `D-094`; the surface states the limit rather than correcting the
  score. ⚠ **Not a structural guard — the number is still computed the same way.**
- ⚠ **This is the heaviest entry in the register.** It is the assumption the Prime Directive's
  deliverable rests on, and it is registered BROKE.

### A-028 — the repository namespace is the only one assigning these integers

- **Registered:** 2026-09-11 *(retroactive, from `F-065` and from this register's own history)* ·
  **Status:** **BROKE**
- **Relied on by:** every `D-`, `F-`, `A-` and `P-` citation in code, tests and documents.
- **What breaks if false:** `F-065` — **a second decision namespace ran alongside the log for one work
  session, and three of its integers collide with live entries** (issue #210 cites `D-0027, amends
  D-0026; D-0024 no-climb remains`, canon at an Obsidian path outside the repository). ⚠ And the `A-`
  namespace hit the same failure from the other side: it was numbered **provisionally against a
  document the repository had never received** (§1).
- **The test:** `grep -n "^### D-02[467]" docs/README.md` — the collision check that closed `F-065`.
- **Guard:** ✅ `D-109` ruling 1 — **the repository namespace governs.** `F-065` is **CLOSED on
  ruling**, and no repository artifact cites a `D-00NN` integer.

### A-029 — a reserved id will be written

- **Registered:** 2026-09-11 · **Status:** **BROKE**
- **Relied on by:** ⚠ every citation of a reserved id — which is the failure mode, not a side effect.
- **What breaks if false:** a reference that resolves to nothing. **Measured at `836a9a3`:**
  **9 finding ids reserved and never written** — `F-013` `F-014` `F-015` `F-018` `F-019` `F-022`
  `F-023` `F-024` `F-050` — and **3 assumption ids cited 71 times in shipped code** before any
  register existed (§0). ⚠⚠ `F-014` is itself *"documenting a duplication is not managing it"*, and it
  is one of the nine unwritten.
- **The test:** for every reserved id, does a written entry exist? **How known (`D-016`):**
  `grep -oE "^### F-[0-9]{3}" docs/README.md` differenced against the `F-` rows of `docs/RESERVED.md`.
- **Guard:** partial — `check_amendment_references.py` exists, but `F-044` records its limit exactly:
  **the citation invariant proves that a reference RESOLVES, never that it resolves to the right
  thing — it finds holes, not mismatches.**
- ⚠⚠ **This is the assumption that made this document necessary**, and registering it is the only part
  of this file that is not retrospective.

---

---

## 4a — ⚠⚠ REGISTERED FORWARD — the survivorship caveat stops here

> **Everything above this line was seeded from a finding that already recorded a break** (§4), so
> the score above calibrates nothing. **This section holds entries registered BEFORE the thing
> they assume is tested.** KEEL-4 §6: *the register becomes calibration only forward, once
> assumptions are registered before they are tested — which is why a register starts rather than
> being reconstructed.*
>
> ⚠ **The status field below is the instrument.** `ASSUMED` here is a live position, not a
> retrospective label, and whether it becomes `HELD` or `BROKE` is the first genuine measurement
> this register has ever produced.

### A-030 — a JSONB column can take an additive key without changing any consumer

- **Registered:** 2026-09-11 · **Status:** ⚠ **ASSUMED** — *registered before the work that tests
  it, and not yet tested.* ⚠⚠ **The first entry in this register that is not retrospective.**
- **Relied on by:** the `run: 1` backfill (`AMENDMENT 2` §3.1), which writes one additive key into
  `jobs.inference_settings` on **3,656 of 3,656 rows** in order to restore `D-095` decision 4's
  property — *present and monovalued, every row declaring itself* — so that Run 1 is **positively
  declared rather than inferred from the absence of a key** (`F-018`'s class).
- **What breaks if false:** ⚠⚠ **a production write to every job row in the table.** If any
  consumer of `inference_settings` depends on its **key set** rather than on named keys, the
  backfill changes behaviour everywhere at once — and it is an **express exception to Task §4.2**
  (*no original row is updated*), granted by the owner with named bounds, so it does not get a
  second attempt on a different reasoning.
- **The test:** enumerate every reader of `inference_settings` and establish that none depends on
  the key set — no `== {...}`, no `len(...)`, no `.keys()`, no iteration over the dict.
  ⚠ **Cost: one grep and one revert proof**, which is why it is registered rather than assumed
  silently.
- **Guard:** the `AMENDMENT 2` §3.1 red test — a revert proof that the backfill changes nothing
  but the key — plus the before/after counts, and `run: 1` on **3,656 of 3,656** (⚠ a hole makes
  the partition the absence-based one the ruling exists to avoid).

**⚠ What is already measured, recorded here because it is the reason this is `ASSUMED` and not a
guess.** How known (`D-016`): `grep -rn "inference_settings"` over `app/ core/ scripts/ worker/ db/`
at `d6f12ca`. **Every reader is key-addressed** — `job.inference_settings.get(...)`,
`settings = job.inference_settings or {}` then named lookups, `is_tile_job(...)` testing for named
keys. **No `== {...}`, no `len()`, no `.keys()`, no iteration over the dict.**

⚠⚠ **AND THAT IS EXACTLY WHY IT STAYS `ASSUMED` RATHER THAN BEING PROMOTED NOW.** A grep over the
Python in this repository is **not** the population the assumption is about:

- ⚠ **The UI reads through the API, not through these modules**, and a client that renders or
  round-trips `inference_settings` would not appear in this grep at all.
- ⚠ **A database-side consumer** — a view, an index on an expression, a downstream query — is not
  Python and was not searched.
- ⚠ **`alembic` migrations and any future ORM comparison** are outside the grep's window.

**The grep narrows the risk; it does not close it.** ⚠ **The guard closes it, and the guard has not
run.** Promoting this entry on the grep alone would be the `[L]`-used-as-`[M]` error this project
recorded twice on 2026-09-11.

## 5. The feeding mechanism, measured

KEEL-4 §5.1 is the load-bearing claim of the whole design: *"Every decision entry carries an
'Assumptions relied on' field… The register is a by-product of the decision log."* **A register kept
by a form lasts as long as the form does.**

**How known (`D-016`):** `grep -c "Assumptions relied on" docs/README.md` against
`grep -cE '^### D-' docs/README.md`, working tree at `836a9a3`.

| measure | value |
|---|---|
| `### D-` headings in the log | 162 — ⚠ **161 real entries**, plus the `### D-NNN — <short title>` template stub at line 282 |
| entries carrying an *"Assumptions relied on"* field | **25** |
| **coverage** | **25 / 161 = 15.5%** |
| of those fields: recorded **"none"** | 14 |
| of those fields: named `A-014` | 11 — ⚠ **2 of them to say it does NOT apply**, so **9** real |
| of those fields: named `A-016` | 1 |
| of those fields: named `A-017` | ⚠⚠ **0** |

*(14 + 11 + 1 = 26 against 25 fields: one field both records "none new" and names `A-014` to rule it
out. **How known (`D-016`):** per-line classification of every `Assumptions relied on` line in
`docs/README.md` at `836a9a3`.)*

**Read honestly:** the form exists and is filled in **15.5% of the time**; when filled it records
*"none"* more often than it names anything, and across the whole log it produces **nine real
reliances on one assumption**. ⚠⚠ **`A-017` — 61 citations across 21 test modules, a gate
requirement — is named by no decision entry at all.** The mechanism KEEL-4 relies on to keep this
register alive is currently the weakest part of it, and that is a fact about the form, not about the
people filling it: **a field nobody is stopped for is a field that gets skipped.**

---

## 6. The score

**15 registered · 15 tested · 15 broke · 2 subsequently guarded (`A-017`, `A-024`) · 1 closed on
ruling (`A-028`).**

⚠⚠ **This is 100% and it means nothing as a rate.** Every entry here was seeded from a finding that
records a break, exactly as KEEL-4 §7 prescribes and exactly as KEEL-4 §6 warns must be labelled.
**The denominator is the assumptions nobody wrote down, and it is unknowable backwards.**

What it does establish, with no denominator — and it is the same thing KEEL-4's seed project
established: **when this project finally tested a load-bearing assumption, it broke. Fifteen times.**
Enough to justify the instrument. Not enough to justify a percentage.

**⚠⚠ AND AS OF 2026-09-11 THE FORWARD COUNT IS 1: `A-030`, REGISTERED AND NOT YET TESTED.**

> **16 registered · 15 tested · 15 broke · 1 ASSUMED and untested.**

⚠ **The two numbers must never be added into one rate.** The retrospective fifteen are survivorship
and calibrate nothing; **the forward one is the only entry whose outcome is not known in advance**,
and it is a sample of one. ⚠ **`A-030` resolving to `HELD` would be the first evidence this register
has ever produced that is not drawn from failures** — and one entry is not a rate either.

**The register becomes calibration at `A-030`** — and it has started, which is different from having
arrived.

---

## 7. What this file does NOT claim

- ⚠ **Not that the fifteen are all of them.** They are the ones a finding already caught.
- ⚠ **Not that `A-001`–`A-013` were considered and rejected.** They were never assigned here.
- ⚠ **Not that the §1 reconciliation binds an external KEEL-4 master.** It checks V9 as committed.
- ⚠ **Not that any status here supersedes the finding it was drawn from.** Where this file and
  `docs/README.md` disagree, **the log wins** (CLAUDE.md rule 3).
- ⚠⚠ **Not that this file governs itself.** Adding a fifth named document changed the shape of the
  documentation set, which is a design decision — it is logged as **`### D-156`** in
  [`decisions.md`](decisions.md), written **before** the split was made (CLAUDE.md rule 1), with the
  `ARCHITECTURE.md` delta in the same PR (rule 2).
