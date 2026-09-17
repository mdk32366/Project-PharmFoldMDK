# OWNER RULING — 2026-09-17 · The feature-extraction population: P1 in · P2 conditional · P3 as a sample · P4 out

> ⚠⚠ **Where this file and the log differ, THE LOG GOVERNS.**
> ⚠ Landing header added by Code at landing, 2026-09-17. **The body below is the document as
> delivered, byte-for-byte**; no AUTHORED-SHA256 range is declared over it, so nothing is pinned
> by these lines.

**Owner:** Matt Kelly · **Planner:** Claude Opus 5 · **Builder:** Code
**Issued:** 2026-09-17, America/Los_Angeles. The `09-17` label is the real calendar date.
**Grounded on:** `origin/main` @ **`1e67954`** (the #331 merge).
**Answers:** `ORDERS-RECONSTRUCTION-2026-09-17-feature-coverage.md` §2.1 — the last owner decision gating
Phase 2.
**Gates:** Phase 2 extraction v2. ⚠ **Authorises nothing today.**

---

## 1. The ruling

**Owner ruling, 2026-09-17: the Planner's recommendation is ACCEPTED as written.**

| population | size | **RULED** |
|---|---|---|
| **P1** — every current census representative with a structure (`/api/census`) | **3,463 folded** | **IN** — unscoped. See §2. |
| **P2** — the cohort 82 (tranche 0) | 82 | **IN IF `C3` SHOWS A GAP.** ⚠ Conditional on a measurement, not on an assumption. If `C3` reads 0, P2 is out and no extraction runs against the cohort. |
| **P3** — Run-2 rows | thousands | **OUT as a population.** **IN as a stratified sample of ≤ 100**, labelled an instrument check. |
| **P4** — hold-48 tile windows | — | **OUT.** Tiles are not proteins and are never a profile subject. |

---

## 2. ⚠ What accepting P1 unscoped means, stated before the work rather than after

P1 as ruled **includes** the assembled parents and tile-window rows.

Because `census_profile_statuses` (`app/census_profile_read.py:127–129`) tests
`_incommensurable_assembly` **first and `continue`s**, those rows display
`refused_assembled_incommensurable` **whether or not they have features.**

**Therefore, for that portion of P1:**

1. ⚠⚠ **Extraction changes nothing any page displays.** It is **not** a coverage fix.
2. It **is** a measurement required by the v2 model comparison, which is why it is still worth paying for.
3. ⚠ **`D-168` must state this in plain words**, or the work will look like it failed. This is carried from
   `RULING-2026-09-16` §1.1 and is not a new condition.
4. **`C1b` is the number that sizes it.** It is reported with its key, never as a bare figure.

**Reopening is allowed and is not a reversal.** If `C1b` comes back materially larger than the working
expectation, the owner may narrow P1 to exclude the assembled portion **before Phase 2 runs**. This ruling
does not lock that in. ⚠ Narrowing **after** Phase 2 has run is a different matter and needs its own
ruling, because the artifact would then hold vectors the population no longer claims.

---

## 3. P3 — the conditions that make it an instrument check rather than a second population

The sample is **≤ 100**, **stratified**, and exists to answer one question: do the same six features come
out the same when the same protein is re-folded? That tests `A10.2`'s `mean_plddt` equality **at the
feature level** rather than at the fold level.

⚠⚠ **Conditions, all of them binding:**

1. **Never pooled with P1** in any count, fit, support range, or coverage figure.
2. **Tagged in the artifact** as the instrument sample, distinguishable without reference to this
   document.
3. **A difference is a finding, not a correction.** Two paths to one quantity disagreeing is the finding;
   it is reported and the work stops on it. Nothing is reconciled and nothing is averaged.
4. The stratification basis is **stated before the sample is drawn**, not chosen after seeing it.

---

## 4. P2 — the condition

P2 enters **only** if `C3` — cohort tranche-0 analyses with no `protein_features` row — reads **greater
than zero**.

⚠ `C3` is measured in Phase 1, **in the same read-only tunnel as R1–R4**. P2 is therefore not decidable
today and is not decided today. **Code does not assume the cohort is complete, and does not assume it is
incomplete.**

---

## 5. What this does not authorise

- **Nothing runs today.** `ORDERS-Code-2026-09-17-R1-R4.md` governs the current work: R1–R4 only,
  owner-gated, and still owing Code's statement of R4's run-label predicate.
- **Phase 1 is not opened by this ruling.** It opens when R1–R4 have been reported and the owner says so.
- **Phase 2 is not opened by this ruling.** It additionally requires `D-168` written, and P2's condition
  resolved by `C3`.
- **Phase 3 ingest remains barred** until `D-168` is ruled *and written*, the §2.3 citation list is
  produced, and `census_ingest_features.py` carries `D-159` plus the role preamble.

---

## 6. Owner decisions now closed, and what remains

**Closed as of this ruling:**

| decision | ruled |
|---|---|
| Fresh-session confirmation | given |
| Credential rotation | ⚠ **deferred deliberately** — recorded as a choice, not an omission. The literal-secret scan is the only guard and the repo is public. |
| `D-168` commensurability | **store tagged, never pool** |
| R4's key (whole-protein identity, tiles as a diagnostic) | **Code's choice ruled correct** — it is the only key under which `3 of 3` is satisfiable |
| **P1–P4 population** | **this document** |

**Still open:**

1. The paper's **§4.3 loss statement**, now narrowing to zero rows — owner's wording.
2. The **v2 timeline months** — owner supplies the class dates; the proposal PDF is rebuilt around them.
3. **`D-169` / `D-170`** (`SPEC-A-032` §2.6, §3.7) — **not today**, after `D-168`.
4. Whether the feature-coverage orders are **re-issued from the recovered verbatim chat text** or the
   current reconstruction stands with the recovered sections appended. ⚠ Related finding, owed under
   **`F-081`**: the document is cited by filename in the ruling, both preworks and the close-out, and
   appears **never to have been committed to `docs/` at all** — a name in the citation chain that never
   resolved.

**Planner error count, carried: 10.**
