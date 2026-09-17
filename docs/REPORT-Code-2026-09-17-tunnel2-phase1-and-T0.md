# REPORT — Code → Planner — 2026-09-17 · Tunnel 2, E1–E3, Phase 1 C1–C5, and T0

**Owner:** Matt Kelly · **Planner:** Claude Opus 5 · **Builder:** Code
**Written:** 2026-09-17, **16:10 PDT**. The `09-17` label is the real calendar date.
**Governs:** `ORDERS-Code-2026-09-17-tunnel2-phase1-and-T0.md` · `AMENDMENT 2` · `SPEC v2`.
**Branch:** `d167-r1r4-population-read`, PR **#332**, head **`06aea65`** — 23 commits, 62 files,
+8,327 / −58 from `1e67954`.
**CI:** run **35285299955** — `test` **pass** (2,796 passed, 85 skipped, 1 xfailed) ·
`postgres` **pass** (76 passed, 1 skipped) · `deploy` skipped.
**Pointers:** `D-169` · `F-083` · `A-032`. **No integer was spent by this work.**

> ⚠ **Tunnel 2 is CLOSED.** Two tunnels exist for 2026-09-17 and **a third is not authorised.**
> **No expectation was missed.** Nothing was re-run to improve a number; no artifact was deleted or
> rewritten.

---

## 1. TASK H — the four governing documents are landed

`AMENDMENT 2`, `SPEC v2` and the tunnel-2 orders are committed to `docs/` (`6702ed3`) with landing
headers above their bodies; **no body text edited**. ⚠ **The delivery class now has no open
instance.**

**Three things `AMENDMENT 2` orders were already done before it arrived**, and are not redone:
`D-168` written (`8005f27`), `F-081`+`F-082` written with the `F-` pointer moved (`222bcdb`), and
`feature_coverage_report.py` built and CI-green (`2cd1c16`).

**Its two corrections are applied:** §4's *"tunnel 2 declared"* is void for the morning (case (i)
stands), and §3's three-branch `C4` is superseded by the four-branch form.

---

## 2. TASK I — tunnel 2, with its own evidence

Opened **22:56:48Z**, closed **22:58:32Z**. Own open paste · own Direct-IP corroboration
(`fdaa:62:76d9:0:1::9`, **MATCH**) · own single-listener count (**1**, pid 23488) · own close paste
(**0 listeners**, pid gone). ⚠ **Never merged into tunnel 1's account**, which stays *one tunnel, one
read*. Step-0 probe **`10003`**, exit 0. `$url` shape `127.0.0.1:16391/pharmfoldmdk`,
`placeholder=False`, **16391 named explicitly**.

⚠ **The departure is recorded, not smoothed:** the orders say *owner at the keyboard*; the owner
directed Code to run it, as this morning, and `t2-tunnel-open.txt` says so in its header.

**Both instruments were CI-green BEFORE the tunnel opened** (run 35284284426, postgres 76).

---

## 3. ⏸ Pause 1 — E1, E2, E3

### 3.1 E3 — the stop condition did NOT fire

**Exactly `P11717`, `Q8WXI7`, `Q9NYQ8`** lack a complete tranche-0 row, from 82 roster accessions
read. ⚠ **The cohort account is now proven rather than consistent**, which is what `AMENDMENT 2` §5
asked for. Phase 1 was allowed to start.

### 3.2 ⚠⚠ E2 — the three pending accessions are the three mucins

**`Q685J3`, `Q8WXI7`, `Q9UKN1` — and no one else.** The two failed are confirmed as **`P11717`**
and **`P55073`**. `F-078`'s five non-complete run-1 rows are enumerated for the first time.

⚠ **This is evidence toward `F-082` sub-question (b) — whether the never-folded state is a CLASS
property of mucins — and it is not an answer to it.** All three mucins sitting in the same status,
alone, is consistent with `decisions.md:6883`'s standing `out_of_class` ruling. **Code does not
close (b): the question asks about a class, and this reads one status column.**

### 3.3 E1 — MUC16 holds exactly one row in the database

**`Q8WXI7`: 1 row in total** — `pending` · whole-protein · run `1` · tranche 5. **No cohort-side row
at all**, no tile rows, nothing complete. ⚠ **`F-082` sub-question (a) is CLOSED**, and it confirms
`F-082`'s reading from the other side: the miss was never about which rows were complete.

⚠ **A detail worth the Planner's eye:** `Q9NYQ8` (FAT2) appears in E3's missing set but in **neither**
E2 list — so it has **no non-complete run-1 row either.** Like MUC16, it appears to hold no
cohort-side row at all. **Measured, not interpreted**; the enumeration was of the cohort's *complete*
rows, so what a cohort accession holds *instead* is not established for FAT2.

---

## 4. ⏸ Pause 2 — C5, read ALONE, before C1 was computed

| | measured |
|---|---|
| v1 artifact `analysis_id`s | **2,690** |
| of those, present in `protein_features` | ⚠ **2,690 — all of them** |
| equality sample | **50 checked, 50 equal, 0 differing** |

**v1 DID reach the table.** ⚠ The v1 manifest's `wrote_database_rows: false` describes the
extraction, not the ingest — the rows arrived by the ingest path afterwards.

**Therefore `C1a`'s floor keeps the meaning it was registered with**, and the pause resolved in favour
of proceeding. ⚠ **The pause was real, not nominal:** `c5_read.json` contains **no `C1` reading at
all**, because none was computed — the `--sections` split makes a C5-only run compute nothing else,
and its keys are absent rather than present as zeros.

---

## 5. ⏸ Pauses 3 and 4 — the coverage readings, each with its key

| reading | measured | key |
|---|---|---|
| **C1a** | **776** | census representatives with no `protein_features` row |
| **C1b** | **45** | of those, already refusing as assembled — extraction changes nothing visible |
| **C1c** | ⚠⚠ **731** | **the ONLY true coverage gap** |
| **C1a verdict** | **ok** | at or above the pre-registered floor of 773 |
| **C2** | **0** | no stale representative anywhere |
| **C3** | **0** | no cohort row lacks a feature row |
| **C4** | assembled **45** · **mucin 3** · single-pass **728** · tiles_only **0** | sums to **776** = C1a |

**Diagnostics:** 3,466 representatives + 1 accession with no representative = **3,467**, the census
population exactly.

### 5.1 ⚠⚠ `P2` is RESOLVED: it stays OUT

`C3 = 0`. The owner's ruling made P2 conditional on `C3` showing a gap; **there is no gap**, so the
condition never fires. ⚠ **P1 in, P2 OUT, P3 a ≤100 tagged instrument sample, P4 out** — the
population question that has been open all day is closed by a measurement.

### 5.2 What C1c means, stated so the next sitting cannot misread it

**731 representatives would gain a rendered profile from extraction.** The other **45** would not:
their page short-circuits before the feature row is read. ⚠ **`C1a` alone (776) is NOT the coverage
gap**, and reporting it as one is the Planner's CSV error in a new coat.

⚠ **`C4`'s `mucin 3` is the same three accessions as E2's pending list.** Two independent readings,
same three proteins.

---

## 6. TASK J — T0 delivered, offline, CI green

`scripts/pdb_coverage_census.py` + 35 tests (`06aea65`), built from the committed **SPEC v2**.

**Offline by construction and by test:** a test fails if `requests`, `urllib`, `httpx`,
`http.client` or `socket` appears in the module, and the CLI **refuses** a `--source` that is not a
local directory. ⚠ **T1 was not run and no live client exists to be called by accident.**

**Pinned:** the pre-registered policy numbers · every outcome at zero, none able to vanish · **two
sum checks, never one** (82 and 3,467, each naming its population; the union is asserted *not* to be
an expected total, and a test fails if SPEC v1's void figure appears anywhere) · the populations read
from committed files with their **75-accession overlap asserted rather than hidden** · spans from our
record, each row naming its file · the 50-residue minimum inclusive at 50 and exclusive at 49 ·
method and resolution **recorded not filtered** (a 7.4 Å EM entry still qualifies at step 1) ·
deterministic best-entry choice · a rate limit as a **recorded outcome** · cache hits labelled · a
partial pass reported **as partial** · resume that skips held records **and still tallies them** · a
re-read **marked as a re-read** · write-once artifact with sha256, `PYTHONHASHSEED` and the source
release in the manifest · **printed output asserted ASCII on the printed bytes.**

### 6.1 ⚠⚠ Reported, not decided — the spec's seven outcomes have no home for an identity failure

An entry can overlap the ECD span **well** and still fail the **95% identity** floor (an isoform or
ortholog mismatch). Under SPEC v2 §1 there is nowhere to put it:

- `overlap_below_minimum` would report an **identity** problem as a **length** problem;
- `no_pdb_entry` would report **our filter** as **nature's absence** — the exact conflation §1's
  last line forbids for `accession_unresolved` and `span_unknown`.

**So an eighth outcome is ADDED and NAMED: `overlap_identity_below_minimum`** — which §5 item 2
permits by name (*"an outcome the code produces that is not in the list is ADDED, never folded"*).
⚠ **Same shape as `C4`'s `mucin` branch**, and raised the same way: **the Planner rules, Code does
not fold.**

⚠ **Consequence for T4:** the report will carry **eight** outcomes, and the sum checks are against
eight, not seven.

---

## 7. State, and what is not done

| item | state |
|---|---|
| Tunnel account | **two tunnels, two sittings, both fully evidenced.** A third is not authorised |
| E1 / E2 / E3 | reported; **E3's stop did not fire** |
| `C5` | **v1 reached the table**; reported before `C1` ran |
| `C1a`/`C1b`/`C1c`, `C2`, `C3`, `C4` | reported with keys; **`C1a` above its floor** |
| **`P2`** | ⚠ **RESOLVED — out**, by `C3 = 0` |
| T0 | delivered, **CI green**, offline |
| **T1 / T2 / T3** | ⚠ **not authorised, not run** |
| `A-032` step 1 | still deferred |
| Phase 2 / Phase 3 | unblocked / still barred, per their own conditions |
| **The close-out** | ⚠ **not written** — the orders defer it until the owner calls the day |

**Evidence:** `t2-tunnel-open.txt` · `t2-tunnel-closed.txt` · `e1_e3_read.json` · `c5_read.json` ·
`c1_read.json` · `c2_c3_c4_read.json` + their console logs. **All four artifacts re-hash on disk
after the tunnel closed**, and each is EOL-protected **by name** in `.gitattributes`.
**Credential scan clean on every file.** Explicit paths on every `git add`; the untracked
`_tmp_c1_*` / `_tmp_c2_*` helpers remain **not read, not touched, not ruled on.**

---

## 8. What Code asks the Planner for

1. **Rule on §6.1's eighth outcome** — accept `overlap_identity_below_minimum`, or say where an
   identity failure belongs. ⚠ It changes T4's sum checks, so it is better ruled before T1 reads.
2. **Note §3.3's FAT2 detail** — it has no complete cohort row *and* no non-complete run-1 row. If
   the cohort account should enumerate what each missing accession holds *instead*, that is a
   one-query addition next sitting.
3. **Confirm `P2` is closed** on `C3 = 0`, so the close-out can state it as resolved rather than
   carried.
4. **Say where PR #332 lands.** It now carries the whole day: R1–R4 and its read, `D-168`, `F-081`,
   `F-082`, the coverage report, tunnel 2's four readings, and T0. ⚠ **Nothing in it deploys.**
