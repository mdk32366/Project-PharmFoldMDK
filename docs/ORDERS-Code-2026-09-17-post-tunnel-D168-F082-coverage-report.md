# ORDERS — Code — 2026-09-17 · Post-tunnel: the tunnel 2 account, `F-082`, `D-168`, the coverage report, and `A-032` step 1

> ⚠⚠ **Where this file and the log differ, THE LOG GOVERNS.**
> ⚠ Landing header added by Code at landing, 2026-09-17. **The body below is the document as
> delivered, byte-for-byte**; no AUTHORED-SHA256 range is declared over it.

**Owner:** Matt Kelly · **Planner:** Claude Opus 5 · **Builder:** Code
**Issued:** 2026-09-17, America/Los_Angeles. The `09-17` label is the real calendar date.
**Grounded on:** branch `d167-r1r4-population-read`, PR **#332**, head **`f0be03a`**.
**Follows:** `ORDERS-Code-2026-09-17-AMENDMENT-2-phase1-and-enumerations.md`.
**Owner report:** the tunnel is **closed.**

> ⚠⚠ **NO DATABASE CONTACT IS AUTHORISED BY THIS DOCUMENT.** Every task below runs with no tunnel, no
> production access, and no GPU. ⚠ **A third tunnel is NOT authorised** (AMENDMENT 2 §4). If any task
> below appears to need one, **stop and report** — it has been mis-scoped.

---

## 1. What carries forward unexecuted, and does not expire

AMENDMENT 2 §5 and §6 were **authorised and did not run.** No report came back.

| carried | state |
|---|---|
| **E1** MUC16 rows by status | authorised, unexecuted |
| **E2** the three `pending` run-1 accessions named | authorised, unexecuted |
| **E3** which of the 82 lack a complete tranche-0 row ⚠ **with its stop condition intact** | authorised, unexecuted |
| **Phase 1 `C5` → C1a/C1b/C1c → C2 → C3 → C4** | authorised, unexecuted |
| **`P2`** | ⚠ **undecidable until `C3` is read.** `P1`, `P3`, `P4` remain settled. |

**These carry to the next sitting unchanged.** ⚠ **They are not re-planned, not re-scoped, and not
re-pre-registered.** AMENDMENT 2 remains their governing document.

---

## 2. ⚠⚠ TASK A — the tunnel 2 account. First, and it is not optional.

Tunnel 2 was reported open and is now reported closed, **with no read taken.** ⚠ **A tunnel that existed
with no open paste, no Direct-IP corroboration and no close paste leaves a GAP in the day's tunnel
account** — and the day's whole evidentiary claim is *one fully evidenced tunnel.*

**Code states, with evidence, which case holds:**

- **(ii) a second tunnel was genuinely opened** → paste its **own** open line, its **own** Direct-IP
  corroboration against `fly mpg status` (`fdaa:62:76d9:0:1::9`), its **own** single-listener
  confirmation, and its **own** close line. Recorded as **tunnel 2 of 2026-09-17, opened and closed with
  no read taken.**
- **(i) what looked open was tunnel 1's session**, and `r3-tunnel-closed.txt` is accurate → state that
  plainly. **The day then has exactly one tunnel** and the account is whole.

⚠ **Either answer is acceptable. An unrecorded tunnel is not.** If neither can be established from
evidence on hand, **that is itself a finding** and it is reported as one rather than resolved by
recollection.

---

## 3. TASK B — write `F-082`

**Subject:** R4's expectation was mis-specified for MUC16. **The database is sound; the wording was not.**

**Must contain:**

1. **The measurement:** `Q8WXI7` — tranche0 complete **0** · census whole complete **0** · census tile
   complete **0** · untagged complete **0**. **No complete run-1 row of any kind.** It appears in **none**
   of the 72 R1 groups, checked against the **complete, uncapped** list.
2. **The cause, named as the Planner's error:** A9.2's *"three named overlap exceptions"* conflated **a
   planned tiled rental span** with **a protein actually folded as tiles.** `P11717` and `Q9NYQ8` are
   both (2 and 3 complete tile rows); `Q8WXI7` is only the first — tranche 5, **14,451 aa**, rental
   planned, **never folded.** ⚠ **Same shape as Phase E's expectation 3.**
3. **Citations:** `docs/decisions.md:2860` (the 4 `none` rows are the 3 mucins — `structure_kind: mucin`,
   `folded: false` — plus `P55073`/DIO3, partitioning 3,418 + 45 + 4 + 0 = **3,467**) · `:3041` (`Q8WXI7`
   wears **`NOT FOLDED`** live, while `Q9NYQ8` renders *assembled (provisional)*) · `:6883` (the 3 mucins
   **stay `out_of_class`** — a standing ruling, not a pending state) · `data/census/census_manifest.v7.csv`
   (`Q8WXI7`, tranche 5, rental, 14,451 aa).
4. ⚠ **That `R1 = 72` STANDS** — a direct measurement with its own `count(*)`, a complete uncapped list at
   72 shown, `{2: 72}`, no group above 2. It **does not inherit** the Phase E derivation's reasoning. The
   `75 − 3` subtraction was **arithmetically right for the wrong reason:** MUC16 should have been excluded
   as *never folded, therefore incapable of forming a pair*, not as *an exception holding exactly one
   census row.*
5. ⚠ **That the "75 overlap" figure rests on the same conflation. Nothing cites 75 as a measured overlap
   without re-deriving it.**
6. **Two sub-questions, recorded OPEN and unmeasured:**
   - **(a)** MUC16's rows **by status** — E1, carried.
   - **(b)** ⚠ **whether this is a CLASS property of mucins** rather than a fact about one protein.
     `Q685J3` and `Q9UKN1` were **untouched today**; `:6883` suggests all three share the state. **Wider
     than R4.** ⚠ **Code declined to answer this and was right to.**
7. **What `F-082` is NOT:** not a data defect, not a reason to re-read R1–R4, and **not a reason to delete
   or rewrite `r1r4_read.json`** — which is never deleted or rewritten.

**Then:** move `RESERVED.md`'s **inline** `F-` pointer (line 327) to **`F-083`**. ⚠⚠ **That is the ONLY
edit to that file.** The four stale row-table entries (`F-073`, `A-031`, `D-158`, `D-156`) are **NOT
struck** — `tests/_f062_pointer_invariant.py` parses the inline pointer with `re.search`, and
`tests/test_d129_phase5_named_refuse_spec.py` cites reserved integers **by number.** Recorded in the
close-out, not repaired today.

---

## 4. ⚠⚠ TASK C — write `D-168`. **The highest-value task remaining today.**

It needs no tunnel, its content is settled, and **writing it is what unblocks Phase 2 next sitting.**

**Content, per `RULING-2026-09-16` §1.2 and the owner's ruling of 2026-09-17:**

1. **Creates NO new refusal category.** Cites **`D-120` / `D-109` ruling 7** and reuses
   **`refused_assembled_incommensurable`**. ⚠ Records that the feature-coverage orders' §2.2 proposed a
   second name for one thing and is **superseded** on that point — **Planner error 9, found by Code
   reading source.** `no_protein_level_structure` is **superseded as a profile category**; if the
   distinction is still wanted it belongs to the **extraction** artifact's outcome vocabulary, never as a
   second profile refusal.
2. ⚠⚠ **States plainly that extracting features for assembled parents changes NOTHING any page
   displays.** `census_profile_statuses` (`app/census_profile_read.py:127–129`) tests
   `_incommensurable_assembly` **first and `continue`s**, so the feature row is never consulted for those
   rows. **Without this sentence the work will look like it failed.** It is a **measurement for the v2
   comparison**, not a coverage fix.
3. **The ruling:** features measured on an assembled chain are **stored, tagged**, and **NEVER pooled**
   into a fit or a support range with single-pass vectors.
4. **One general sentence:** commensurability is a property of the **instrument and the object
   together**, and any feature vector must carry enough provenance to establish **both** before it may
   enter a fit. ⚠ **General on purpose — this is what stops `D-168` needing a re-rule per model.**
5. ⚠ **`D-168` does NOT specify the v2 artifact's schema.** The `model` / `structure_kind` tag keys are
   named and pinned by the **v2 pre-registration.** *(Code's catch — the two "never mix" rules are one
   principle on two axes. Credited.)*
6. **Records that the `structure_kind` tag in the v2 artifact stands and is not a refusal.** It records
   what the extractor measured; the refusal is decided **at profile time, from the row.**

**Then:** move `RESERVED.md`'s inline `D-` pointer to **`D-169`**. Same constraint as §3 — inline only.

⚠ **Extraction may proceed after `D-168` is written. Ingest may not.**

---

## 5. TASK D — `scripts/feature_coverage_report.py`, tests first. **NOW AUTHORISED.**

Previously deferred; **authorised here** because it **reads and reports only** — no tunnel, and **nothing
in it deploys.**

⚠ **Build from the COMMITTED `docs/ORDERS-RECONSTRUCTION-2026-09-17-feature-coverage.md`**, never from a
chat restatement (`RULINGS-2026-08-07` **R5**). ⚠ **If Code's source reading turns up an architecture
constraint that document does not state, that constraint is REAL and the document is incomplete** —
**report it**; §2.4.2 and §2.4.5 are unrecovered and were not reconstructed.

**Tests pin, at minimum:**

1. ⚠⚠ It **models the `_incommensurable_assembly` short-circuit.** An **assembled parent with no feature
   row → C1b**, **not** C1c. A **single-pass row with no feature row → C1c.** Without this it reproduces
   the Planner's CSV error.
2. **C1c is computed as C1a − C1b** and is **labelled the only true coverage gap.**
3. **Every count is its own `count(*)`.** ⚠ A test **fails** if any count derives from a list length —
   the session's shared defect class, which the R1–R4 instrument already caught **inside its own draft**
   (`len(R4_ACCESSIONS)`).
4. **Every capped list says it is capped**, carrying a count it did not derive from its own length.
5. **Printed output is ASCII**, asserted on the **printed bytes.** ⚠ **A source-only ASCII check is not an
   output ASCII check** — only the printed-byte assertion caught `core.db_role.format_preamble`'s section
   sign, and **only in CI.**
6. `choose_census_representative` is **imported from `app/reads.py`** — one home, never re-implemented.
7. **Each reading states its key.** A bare number is not a C-reading.
8. **A-017 discrimination:** every assertion is shown capable of failing, on a fixture that makes it fail.

⚠ **There is no §1 table for it to reproduce or to differ from** — the source CSV is gone
(`RECONSTRUCTION` §1). **Its output is the measurement.** The **777** figure is a **historical quotation,
not a live number**, and this script does not reconcile against it.

**CI green — `test` and `postgres` both — before anything is called done.** ⚠ **No deploy. This is not a
deployable change.**

---

## 6. TASK E — `A-032` step 1: the UniProt topology feasibility read

**Authorised.** Public API read over the **3,467** census accessions. No tunnel, no database, no GPU.

⚠ **It is a GATE, not a build.** Its result **sizes Axis B or kills it** (`SPEC-A-032` §1.1, §4). **Nothing
downstream of the gate is authorised** — not Axis B, not Axis A, not `D-169` / `D-170`, which wait on
`D-168`.

**Conditions:**

1. **Pre-register the pass/fail criterion BEFORE the pull.** ⚠ What coverage of topology annotation counts
   as feasible is written down first, not chosen after seeing the numbers.
2. **Report coverage with its own `count(*)`:** how many accessions carry a usable cytoplasmic-tail
   annotation, how many do not, and **how many fail to resolve at all** — three numbers, each keyed.
3. ⚠ **Rate-limit and cache politely.** A partial pull is reported **as partial**, with how far it got. **A
   truncated pull presented as a complete one is the session's shared defect class.**
4. **The raw pull is committed as evidence** with its sha256.
5. ⚠ **This is a descriptive feasibility reading. It scores nothing** (`D-079` dec 1) **and ranks
   nothing.**

⚠ **If TASK E crowds TASK C, TASK C wins.** `D-168` unblocks Phase 2; `A-032` step 1 sizes a November
decision.

---

## 7. Priority, if the day is short

**C** (`D-168`) → **A** (the tunnel account) → **B** (`F-082`) → **D** (the coverage report) → **E**
(`A-032` step 1).

⚠ **A and B are cheap and both are record-keeping the day's evidentiary claim depends on. Do not let D or
E displace them.**

---

## 8. Hygiene, unchanged and binding

`.\.venv\Scripts\python.exe` everywhere, `-m alembic` included · **explicit paths on every `git add`** ·
literal secrets **stop** a commit, bare words are **listed** (A10.3) · evidence LF and ASCII ·
**`r1r4_read.json` is never deleted or rewritten**, and stays protected **by name** in `.gitattributes` ·
⚠ the untracked `_tmp_c1_*` / `_tmp_c2_*` helpers stay **not read, not touched, not ruled on**, and must
not land · `.env` still carries a credential on the dead **16380**, consistent with rotation being
**deferred deliberately.**

---

## 9. The close-out carries all of this

1. **Today's result, stated plainly:** **R1, R2, R3 MET** against pre-registration (72 · 72 of 72 · 0);
   **R4 NOT MET at 2 of 3**, ruled a **mis-specified expectation**, recorded as **`F-082`**. The delivery
   block **cleared** — all governing documents committed to `docs/`.
2. **`F-081`** — the run-label blind spot: **real in source, ZERO instances in the database today**
   (`(absent)` whole_protein 0 · tile 0 · partial_tile_keys 0), **latent for the next tile emission.**
   ⚠ `app.reads.keep_run_1` shares it.
3. **`F-082`** and its two open sub-questions.
4. ⚠ **The "75 overlap" figure** — re-derive before citing.
5. ⚠ **The reusable method note:** *a source-only ASCII check is not an output ASCII check.* A **lesson**,
   not a changelog line.
6. **`core/db_role.py`'s section sign** — stays on the existing "make printed output ASCII" item. ⚠ A
   shared module is not a read-day edit.
7. ⚠ **The tunnel account**, per §2, with the case Code establishes.
8. ⚠ **The owner-at-the-keyboard departure** on tunnel 1's read — recorded in `r1-tunnel-open.txt`, **not
   smoothed.** Authorisation was given, so the gate held in substance; recorded as a departure anyway.
9. **`E1`, `E2`, `E3` and Phase 1 `C1`–`C5`** — **authorised, unexecuted, carried.** ⚠ **`P2` undecidable
   until `C3`.**
10. **Planner errors 11 and 12**; Planner count **12**, Code count **7**.
11. `F-079`'s three open exceptions · the citation-invariant residual · the four stale `RESERVED.md` rows
    (`F-073`, `A-031`, `D-158`, `D-156`) — **recorded, not repaired.**
12. **Owner decisions still open:** the paper's **§4.3 loss statement** (now zero rows, owner's wording) ·
    the **v2 timeline class dates** · **`D-169` / `D-170`** (after `D-168`) · **credential rotation**
    (deferred deliberately).
13. **The true calendar date: 2026-09-17.**
