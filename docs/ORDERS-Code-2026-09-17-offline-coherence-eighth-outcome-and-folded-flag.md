# ORDERS — Code — 2026-09-17 · Three offline tasks: the coherence check, SPEC v2's eighth outcome, and the folded-flag provenance read

> ⚠⚠ **Where this file and the log differ, THE LOG GOVERNS.**
> ⚠ Landing header added by Code at landing, 2026-09-17. **The body below is the document as
> delivered, byte-for-byte**; no AUTHORED-SHA256 range is declared over it.

**Owner:** Matt Kelly · **Planner:** Claude Opus 5 · **Builder:** Code
**Issued:** 2026-09-17, America/Los_Angeles, late afternoon. The `09-17` label is the real calendar date.
**Grounded on:** branch `d167-r1r4-population-read`, PR **#332**, head **`06aea65`**, CI green (run
35285299955).
**Owner instruction:** *"Go"* — the offline half now; the cohort-account query waits for the next tunnel.

> ⚠⚠ **NO DATABASE. NO TUNNEL. NO NETWORK.** All three tasks read **committed artifacts and source
> only.** ⚠ **A third tunnel is NOT authorised.** If any task below appears to need one, **stop and
> report** — it has been mis-scoped.

---

## 1. Rulings carried into these orders

| item | ruled |
|---|---|
| **SPEC v2's eighth outcome** | ⚠ **`overlap_identity_below_minimum` ACCEPTED.** §1 is amended to **eight** outcomes; T4's sum checks are against **eight**. The amendment is **recorded in the close-out**, not edited into the committed spec's body. |
| **`P2`** | ⚠⚠ **CLOSED — OUT**, on `C3 = 0`. The population ruling now reads **P1 in · P2 out on measurement · P3 a ≤100 tagged instrument sample · P4 out.** The close-out states it **resolved**, not carried. **The last owner decision from this morning's list, closed by a reading rather than a judgment.** |
| **`F-082` (a)** | **CLOSED** by E1. |
| **`F-082` (b)** | ⚠ **STAYS OPEN.** E2's result — the three pending accessions being exactly the three mucins — is **evidence toward it, not an answer.** Code's refusal to close it (*"the question asks about a class and this reads one status column"*) is **ruled correct.** |
| **FAT2's missing-row detail** | noted; the one-query cohort-account reading is **ordered for the next tunnel**, not today. |

---

## 2. ⚠⚠ TASK K — the coherence check, from the ARTIFACTS, not from the Planner's arithmetic

**The Planner derived an interlock from Code's restated numbers and will not have it asserted on that
basis.** ⚠ **Population arithmetic is exactly where the Planner went wrong twice today — errors 13 and
15.** So it is measured from the committed artifacts, by Code, or it does not go in the close-out.

**Read from `c5_read.json`, `c1_read.json`, `c2_c3_c4_read.json` and the E-reads — offline, they are on
disk:**

| # | the claim to check | from |
|---|---|---|
| **K1** | representatives **3,466**, of which **776** hold no feature row ⇒ **2,690** hold one | `c1_read.json` + its diagnostics |
| **K2** | `C5` found **2,690** v1 `analysis_id`s present in `protein_features`, 50/50 equal | `c5_read.json` |
| **K3** | `C2 = 0` — no representative's feature row hangs off a stale `analysis_id` | `c2_c3_c4_read.json` |
| **K4** | ⇒ **the covered set IS v1's set, exactly, with nothing arriving from an unaccounted source** | K1 ∧ K2 ∧ K3 |

⚠⚠ **K4 is the one that matters, and it is a CONCLUSION, not a reading.** State plainly whether the
artifacts support it. **If the three numbers do not interlock exactly, say so and stop** — a near-miss is
a finding, not a rounding.

⚠ **If it holds, record it as a COHERENCE CHECK ACROSS THREE INDEPENDENT READINGS — corroboration, NOT a
new finding, and NOT a new integer.** It answers the concern behind the floor: *"a smaller `C1a` is a
finding because it would mean features from an unaccounted source."* **There is no such source.**

**Two smaller cross-checks in the same family:**

- **K5** — `C1b = 45` and `C4`'s assembled branch **= 45**, which is the whole `assembled_served`
  population from `decisions.md:2860`. ⇒ ⚠ **not one assembled representative holds features.** State it
  as **consistent**, not as a surprise.
- **K6** — `C1a = 776` against the void file-based **777**. They differ by one. ⚠⚠ **Nothing reconciles
  against 777** — it is a historical quotation (`RECONSTRUCTION` §1, `F-082`'s warning class).
  **A FOOTNOTE, not a discrepancy to chase.** ⚠ **Do not compute the difference as though it explained
  something.**

**No new integer. No new artifact if the existing ones answer it — a short written check is the
deliverable.**

---

## 3. TASK L — SPEC v2's eighth outcome into T0, tests first

`overlap_identity_below_minimum` is ruled in (§1). ⚠ **Fold it into T0 NOW**, so **T1 cannot start next
sitting against a stale instrument.**

**Pinned:**

1. **Eight outcomes**, all initialised to **`0`**, ⚠ **none able to vanish when empty** — `D-027` at the
   reporting surface, the rule the coverage report **failed CI on** today.
2. ⚠⚠ **Both sum checks are against EIGHT**: the outcomes sum to **82** for the cohort pass and to
   **3,467** for the census pass, each naming its population. ⚠ **Never to 3,474**, and the union stays
   asserted as **NOT** an expected total.
3. **A fixture that lands in the new outcome:** an entry with a **long, qualifying overlap** that
   **fails the 95% identity floor.** ⚠ It must be provably distinguishable from
   `overlap_below_minimum` — **an identity failure reported as a length failure is the defect this
   outcome exists to prevent**, and a test that cannot tell them apart has measured nothing (`A-017`).
4. ⚠ **It is never folded into `no_pdb_entry`.** That would report **our filter as nature's absence** —
   the conflation §1's last line forbids for `accession_unresolved` and `span_unknown`.
5. **Offline still enforced by test** — the module may not reference `requests`, `urllib`, `httpx`,
   `http.client` or `socket`, and the CLI still refuses a non-local `--source`. ⚠ **No live client comes
   into existence in this task.**

**CI green — `test` and `postgres` both.** ⚠ **T1 remains NOT authorised.**

---

## 4. ⚠ TASK M — the folded-flag provenance read. A READING, not a change.

**The question, stated as measurable:** `decisions.md:3041` records MUC16 displaying **`NOT FOLDED`**.
**E1 measured MUC16 holding exactly one row: `pending`, whole-protein, run 1, tranche 5.** ⚠ *"Not
folded"* reads as a **settled state**; `pending` is a **queued job.** Before today the label was not
checkable. **It is now, for all three mucins.**

**Read from source only — no database, no tunnel:**

1. **Where the census payload's folded / not-folded flag comes from** — the field, the function, the file
   and the line.
2. ⚠⚠ **Whether a `pending` row can produce `NOT FOLDED`** on the surface, and by what path.
3. **What the UI copy is** for that state, and where it is defined.
4. **Whether `structure_kind: mucin` participates** in that decision or is independent of it.

⚠⚠ **DO NOT CHANGE ANY LABEL, ANY FLAG, OR ANY COPY.** The Planner has **not** ruled this a defect, and
the two readings of it point at **opposite fixes:**

| reading | the fix would be |
|---|---|
| the mucins will **never** be folded — `decisions.md:6883` holds them `out_of_class` as a **standing ruling** | *"not folded"* is the **honest permanent state**, and the **`pending` rows are the stale artifact** |
| the `pending` rows are live and the queue is real | the **label** is wrong, not the rows |

⚠ **Code reports which the source supports. The OWNER decides which side is wrong.** A change made
before that decision would pick one by accident.

⚠ **This spends no integer.** If it turns out to be a defect, it gets one **when the owner rules**, and
Code confirms next-free from `RESERVED.md` **in the commit that spends it** — ⚠ **a pointer moved past an
unwritten integer is the `D-062` shape**, which is why `F-081` was written today.

---

## 5. Not authorised

| not authorised | why |
|---|---|
| **A third tunnel** | Two exist for 2026-09-17, both fully evidenced. ⚠ The cohort-account query (what the three missing accessions hold **instead**) is **ordered for the NEXT tunnel**, not today. |
| **T1 / T2 / T3** | T0 only. ⚠ T1's stop condition needs a fresh head. |
| **Any label, flag or copy change** | §4. |
| **`A-032` step 1** | Still deferred; its pass criterion is pre-registered **before** the pull. |
| **Phase 2 extraction** | Unblocked by `D-168`, but needs owner presence and its own orders. |
| **Phase 3 ingest** | Additionally needs the §2.3 citation list and `census_ingest_features.py` carrying `D-159` + the role preamble. |
| **`D-169` / `D-170`** | Owed to `SPEC-A-032` §2.6 / §3.7. |
| Re-reading R1–R4, or any of today's four artifacts | ⚠ **Never deleted, never rewritten.** They are read, not re-run. |
| `RESERVED.md`'s four stale rows | Recorded, not repaired. ⚠ **Not struck** without checking the `re.search` pins. |
| **Any deploy** | Nothing today is deployable. |
| **The close-out** | ⚠ Still deferred — **written when the owner calls the day.** |

---

## 6. Hygiene

**Explicit paths on every `git add`** · literal secrets **stop** a commit, bare words **listed**
(A10.3) · evidence LF and ASCII · printed output ASCII **on the printed bytes** · ⚠ the untracked
`_tmp_c1_*` / `_tmp_c2_*` helpers stay **not read, not touched, not ruled on** · any new artifact added
to `.gitattributes` **by name** — the glob is not enough for a byte-for-byte guard.

---

## 7. What "done" looks like

- **K1–K6 stated**, from the artifacts. ⚠ **K4 answered plainly — supported or not** — and if supported,
  recorded as **corroboration**, not a finding, not an integer.
- **T0 carrying eight outcomes**, both sum checks against eight, the identity fixture discriminating,
  **CI green**, still offline, **T1 not run.**
- **TASK M reported**: the flag's provenance, whether `pending` can yield `NOT FOLDED`, and which of §4's
  two readings the source supports. ⚠ **Nothing changed.**
- **The three tasks are independent.** ⚠ **If one stops, the other two still stand** — say which
  stopped and why.
