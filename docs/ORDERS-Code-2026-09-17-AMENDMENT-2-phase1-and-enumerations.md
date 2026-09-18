# ORDERS (AMENDMENT 2) — Code — 2026-09-17 · The stop is lifted · tunnel 2 declared · `F-082` · Phase 1 C1–C5 and the three enumerations

> ⚠⚠ **Where this file and the log differ, THE LOG GOVERNS.**
> ⚠ Landing header added by Code at landing, 2026-09-17. **The body below is the document as
> delivered, byte-for-byte**; no AUTHORED-SHA256 range is declared over it.

**Owner:** Matt Kelly · **Planner:** Claude Opus 5 · **Builder:** Code
**Issued:** 2026-09-17, America/Los_Angeles. The `09-17` label is the real calendar date.
**Grounded on:** branch `d167-r1r4-population-read`, PR **#332**, head **`f0be03a`**; read script at
`00badb9`.
**Amends:** `ORDERS-Code-2026-09-17-R1-R4.md` §5.2 and §9, and `AMENDMENT 1` §7.
**Answers:** `FINDING-Code-2026-09-17-R4-MUC16.md` §7 items 1–4.

---

## 1. ⚠⚠ RULED — the stop is LIFTED. R4's expectation was mis-specified; the database is sound.

**`FINDING` §7 item 1: option (a). Decidable from the committed record. No second read for this purpose,
and (c) is NOT ordered.**

Verified against the three citations Code named:

| source | establishes |
|---|---|
| `docs/decisions.md:2860` | the census partitions `oneshot` 3,418 · `assembled_served` 45 · `none` 4 · `tiles_only` 0 = **3,467**; the four `none` rows are the **3 mucins** (`Q685J3`, `Q8WXI7`, `Q9UKN1` — `structure_kind: mucin`, **`folded: false`**) plus `P55073`/DIO3 |
| `docs/decisions.md:3041` | live, **`Q8WXI7` wears `NOT FOLDED`**; `Q9NYQ8` renders *assembled (provisional)* |
| `docs/decisions.md:6883` | the 3 mucins **stay `out_of_class`** — a standing ruling, not a pending state |

**MUC16 has no complete census row BY DESIGN. The pre-registration required one.**

⚠ **Where the error came from, and it is the Planner's:** A9.2's phrase *"the three named overlap
exceptions"* conflated **a planned tiled rental span** with **a protein actually folded as tiles.**
`P11717` and `Q9NYQ8` are both — 2 and 3 complete tile rows. **`Q8WXI7` is only the first:** tranche 5,
14,451 aa, rental planned, **0 tile rows and 0 whole-protein rows.** The set was built from the manifest
without checking each element's fold state, which the committed record had already recorded as false.
**Same shape as Phase E's expectation 3.**

**Planner error count, carried: 12.**

⚠ **(c) is not ordered because it cannot change R4's verdict:** a `pending` or `failed` row is **not a
complete census row**, so the second clause fails either way. The question is real but it is **census
accounting**, not R4 — and it is folded into §5 below at no extra tunnel cost.

---

## 2. ⚠ RULED — `R1 = 72` STANDS, and it now rests on measurement rather than derivation

**`FINDING` §7 item 2.**

The Phase E derivation reached 72 as `75 overlap − 3 named exceptions`, and §1 falsifies the **premise**
for one of those three terms. **R1's 72 does not inherit that reasoning.** It is a direct measurement:
its own `count(*)`, a **complete uncapped list at 72 shown**, and `{2: 72}` with no group holding 3 or
more. ⚠ **This is the reading the Phase E report could not take**, and it is what now carries the 72.

**Recorded:** the subtraction was **arithmetically right for the wrong reason.** MUC16 was excluded as
*"an exception holding exactly one census row"*; it should have been excluded as *"never folded, therefore
incapable of forming a pair."* Same term, different justification. **The derivation is no longer
load-bearing.**

⚠ **Consequence carried, not resolved today:** the **"75 overlap"** figure rests on the same conflation.
**Nothing cites 75 as a measured overlap without re-deriving it.**

---

## 3. RULED — the numbers · `FINDING` §7 item 3

| integer | subject |
|---|---|
| **`F-081`** | **stays with the run-label blind spot** (claimed in `AMENDMENT 1` §8 item 1). ⚠ Its finding is now **sharper** than when claimed: `core/hold48.py` `emit_tile_jobs` writes no `run` key, so the defect is **real in source with ZERO instances in the database today** — `(absent)` whole_protein **0** · tile **0** · partial_tile_keys **0**. **Latent, not active. It fires on the next tile emission.** |
| **`F-082`** | **ASSIGNED to the R4 miss:** the expectation was mis-specified for MUC16, with the never-folded mucin state as its substance. Cites `decisions.md:2860`, `:3041`, `:6883` and `census_manifest.v7.csv`. |

**`RESERVED.md`'s `F-` pointer moves to `F-083`.** ⚠ Inline pointer only (line 327). **The four stale row-table
entries are NOT touched** — see §8.

**`F-082` carries two open sub-questions, neither a stop:**
1. MUC16's rows **by status** — §5 measures it.
2. ⚠ **Whether this is a CLASS property of mucins** rather than a fact about one protein. The other two
   mucins were untouched today; `decisions.md:6883` suggests all three share the state. **This is wider
   than R4 and Code correctly declined to answer it.** §5 takes the cheap part; the rest stays open.

---

## 4. ⚠⚠ Tunnel 2 — declared, because the evidence says tunnel 1 is closed

`FINDING` §8 records `r3-tunnel-closed.txt` and **0 listeners after.** The owner reports a tunnel **open
now**. ⚠ **The standing condition is one tunnel per day. It is AMENDED here, deliberately and on the
record — not broken quietly.**

**Before the first read of this amendment, Code states which case holds:**

- **(i)** tunnel 1 was never actually closed and `r3-tunnel-closed.txt` is wrong — ⚠ **that is a finding
  about the evidence** and it stops this amendment until ruled; or
- **(ii)** a **new tunnel** was opened after the close — **this is tunnel 2 of 2026-09-17**, and it gets
  its **own** open paste, its **own** Direct-IP corroboration against `fly mpg status`
  (`fdaa:62:76d9:0:1::9`), its **own** single-listener confirmation, and its **own** close paste.

⚠ **Two tunnels in one day is now authorised. A third is not.** Everything in this amendment runs inside
tunnel 2.

**Unchanged and binding inside it:** `SET TRANSACTION READ ONLY` · role preamble · `D-159` · every count
its own `count(*)` · every capped list labelled capped · write-once output with its own sha256 · ASCII
printed output · `.\.venv\Scripts\python.exe` · `$url` built with **16391 named explicitly**, never
trusted from `.env` (which still carries a credential on the dead **16380**) · literal secrets stop a
commit, bare words are listed (A10.3) · **explicit paths on every `git add`.**

---

## 5. ORDERED — the three enumerations. Read-only. Tests first.

These rectify what §1, §2 and `FINDING` §4/§6 left unmeasured. **They are cheap, they are in the tunnel
already, and none of them is a pass/fail gate.** Each reports with **its own `count(*)`** and its key
stated.

| # | reading | why |
|---|---|---|
| **E1** | **MUC16 (`Q8WXI7`) rows BY STATUS**, all statuses, whole-protein **and** tile identity, run label named including `(absent)` | closes `F-082` sub-question 1. ⚠ **It does not reopen R4** — R4's verdict is ruled in §1 and is not contingent on this. |
| **E2** | **The three `pending` run-1 accessions named**, and the 2 `failed` confirmed as `P11717` / `P55073` | `F-078` recorded 5 non-complete run-1 rows and never enumerated them. ⚠ **MUC16 may or may not be among the pending. Code asserts nothing until measured.** |
| **E3** | **Which of the 82 cohort accessions lack a complete tranche-0 row** — named, not counted | today's **79 of 82** is *consistent* with the Phase E account (`P11717` failed; `Q8WXI7`, `Q9NYQ8` not folded) but ⚠ **consistent is not proven.** E3 proves or refutes it. |

⚠ **E3 has a stop condition.** If the three named are **not** `P11717`, `Q8WXI7`, `Q9NYQ8`, that is a
**finding** and Phase 1 does not start in this tunnel. The cohort account would then be wrong in a way
that bears on `C3`, and `C3` gates **P2**.

**Not ordered, and not in scope here:** the other two mucins (`Q685J3`, `Q9UKN1`) beyond whatever E1's
by-status shape reveals about MUC16 alone. **`F-082` sub-question 2 stays open and unmeasured.**

---

## 6. AUTHORISED — Phase 1, C1–C5, in tunnel 2

The delivery block is cleared: **all four governing documents are committed to `docs/`**, including
`ORDERS-RECONSTRUCTION-2026-09-17-feature-coverage.md`. ⚠ **Code builds from the COMMITTED file, not from
any chat restatement** (`RULINGS-2026-08-07` **R5**).

**Population, per `RULING-Owner-2026-09-17`:** **P1 in, unscoped** · **P2 only if `C3` > 0** · **P3 a ≤100
stratified instrument sample, tagged, never pooled** · **P4 out.**

**Order within Phase 1 — do not reorder:**

1. ⚠⚠ **`C5` FIRST, and reported before anything else.** It decides whether v1's **2,690** rows ever
   reached `protein_features`. The panel reads the **table**; the v1 manifest says
   `wrote_database_rows: false`. **If they never arrived, the whole coverage picture changes and that is
   reported immediately.** ⚠ Before `C5`, Code restates **from source** where the panel's features come
   from.
2. **`C1`, as THREE keyed readings, never one number:** **C1a** no `protein_features` row · **C1b** of
   those, how many already refuse as assembled · **C1c = C1a − C1b**, ⚠⚠ **the ONLY true coverage gap.**
   Original expectation on C1a was **≥ 773**; ⚠ **a SMALLER number is a finding** — it would mean features
   arrived from some other source.
3. **`C2`** — representatives whose `protein_features.analysis_id` ≠ the representative's id. A **named
   category** (stale representative), **count and ids.** No pre-set expectation; the count is the
   measurement.
4. **`C3`** — cohort tranche-0 analyses with no feature row. **This resolves `P2`**, and it is read
   alongside E3.
5. **`C4`** — **C1a** broken down by `structure_kind`: assembled parent / tiles-only / single-pass.

**Binding on the instrument:** `choose_census_representative` is **imported from `app/reads.py`** — one
home, never re-implemented. ⚠ **Each C-reading states its key.** A bare number is not a C-reading.

⚠ **There is no §1 table to reproduce or to differ from** — the source CSV is gone
(`RECONSTRUCTION` §1). **Phase 1's live readings are the authoritative coverage numbers from today
forward. The 777 figure is a historical quotation, not a live measurement.**

---

## 7. What is NOT authorised by this amendment

| not authorised | why |
|---|---|
| `scripts/feature_coverage_report.py` | Next sitting. ⚠ It must model the `_incommensurable_assembly` short-circuit; tests first. Nothing in it deploys. |
| **Phase 2 extraction** | Requires **`D-168` WRITTEN**, not merely ruled. §9. |
| **Phase 3 ingest** | Additionally requires the §2.3 citation list and `census_ingest_features.py` carrying `D-159` + the role preamble. |
| **A third tunnel** | Two are authorised. §4. |
| Re-reading R1–R4 | ⚠ **Ruled and closed.** R1/R2/R3 **MET**; R4 **mis-specified**, recorded as `F-082`. **`r1r4_read.json` is never deleted or rewritten.** |
| `RESERVED.md`'s four stale rows | §8. |
| The other two mucins | §5. |
| `A-032` beyond its step-1 feasibility read | Standing. |

---

## 8. `RESERVED.md` — the `F-` pointer moves; the stale rows do NOT

**Move the inline `F-` pointer to `F-083`** (line 327). That is the only edit.

⚠⚠ **DO NOT STRIKE** the four stale row-table entries (`F-073`, `A-031`, `D-158`, `D-156`), which all read
*"Nothing yet — the next free integer"* while their entries exist.
`tests/_f062_pointer_invariant.py` parses the inline pointer with `re.search`, and
`tests/test_d129_phase5_named_refuse_spec.py` cites specific reserved integers **by number.** **Recorded
in the close-out, not repaired today.** This is the `F-044` shape — a pointer that exists to prevent
drift, itself drifted.

---

## 9. `D-168` — written after the readings, this sitting if the readings allow

Content is settled (`RULING-Owner-2026-09-17`, owner ruling accepted):

1. **No new refusal category.** Cites `D-120` / `D-109` ruling 7; reuses
   **`refused_assembled_incommensurable`**.
2. ⚠⚠ **States plainly that extracting features for assembled parents changes NOTHING any page
   displays** — the short-circuit at `app/census_profile_read.py:127–129`. **Without this sentence the
   work will look like it failed.**
3. **The ruling: store tagged, NEVER pool** assembled vectors into a fit or a support range with
   single-pass vectors.
4. **One general sentence:** commensurability is a property of the **instrument and the object together**,
   and any feature vector must carry enough provenance to establish both before it may enter a fit.
5. ⚠ **`D-168` does NOT specify the v2 artifact's schema.** The `model` / `structure_kind` tag keys are
   named and pinned by the **v2 pre-registration**, not here. (Code's catch, credited in `AMENDMENT 1`.)

**Extraction may proceed after `D-168` is written. Ingest may not.**

---

## 10. Carried to the close-out

1. **`F-081`** — the run-label blind spot: real in source, **zero instances today**, latent for the next
   tile emission. ⚠ Including that `app.reads.keep_run_1` shares the blind spot.
2. **`F-082`** — R4 mis-specified; MUC16 never folded; **both sub-questions**, with E1's result and the
   mucin class question left open.
3. ⚠ **The "75 overlap" figure rests on the same conflation as R4's set** (§2) — re-derive before citing.
4. ⚠ **The reusable method note:** *a source-only ASCII check is not an output ASCII check.* Only the
   assertion on **printed bytes** caught the section sign in `core.db_role.format_preamble`, and **only in
   CI.** A **lesson**, not a changelog line.
5. **`core/db_role.py`'s section sign** — stays on the existing "make printed output ASCII" item. ⚠ A
   shared module is not a read-day edit.
6. **Planner errors 11 and 12**; error count **12**. Code's count **7**, unchanged.
7. ⚠ **Tunnel 2 declared and authorised** (§4), with the case Code states under §4(i)/(ii).
8. ⚠ **The owner-at-the-keyboard departure** on tunnel 1's read — recorded in `r1-tunnel-open.txt`, **not
   smoothed.** Authorisation was given, so the gate held in substance. **Recorded as a departure anyway.**
9. `F-079`'s three open exceptions · the citation-invariant residual · the four stale `RESERVED.md` rows.
10. ⚠ **Untouched, unread, unruled:** the untracked `_tmp_c1_*` / `_tmp_c2_*` helpers.

---

## 11. What "done" looks like for this amendment

- §4's tunnel case stated, tunnel 2's open evidence pasted.
- **E1, E2, E3** reported, each with its key and its own `count(*)`. ⚠ **E3's stop condition checked
  before Phase 1 starts.**
- **`C5` reported first**, then **C1a/C1b/C1c**, C2, C3, C4 — **each with its key stated.**
- **`P2` resolved** by `C3`, or explicitly left open with the reason.
- **`F-082`** written; `RESERVED.md`'s `F-` pointer moved to `F-083`.
- **`D-168`** written, or deferred with the reason stated.
- **Tunnel 2 closed**, with both pastes.
- The close-out states the **true calendar date** and carries §10 in full.

⚠ **Any miss against a pre-registered expectation is a finding and stops the work. Nothing is re-run and
nothing is reconciled.**
