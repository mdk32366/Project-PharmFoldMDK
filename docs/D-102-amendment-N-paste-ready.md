# PASTE-READY — `D-102 amendment ‹N›` — for `docs/README.md`

**AUTHORED-SHA256** (range: **first `####` header → EOF**, anchored to line starts, **SECOND
occurrence of the marker**) = `fe94cbeb613efea4351a37c32f025f487a0447abc59b3aed854b318528ea7e77`
**bytes** = `5755`

> ⚠ **DOWNLOAD AND COMMIT. DO NOT RETYPE.** Landing header **above** the marker, outside the range.
> ⚠⚠ **`####` — this IS an amendment.** *(`F-053` was sent at `####` and was not one; this one is.)*
> ⚠ **Confirm the number against the live log. Three greps.**
> **Built from `docs/DRAFT-D-102-amendment-2.md`; the draft's three questions are kept with their
> answers recorded against them** — *a question deleted looks like one never asked.*

---

#### D-102 amendment ‹N› — ⚠⚠ The default sort promoted the rows the scorer had DELIBERATELY EXCLUDED to the head of the ranking

- **Date:** 2026-08-21 · **Status:** ruled and **SHIPPED** (`main @ ad1a8b7`, verified against
  production at v100, not against the gate).
- **Owner ruling:** default `/targets` to the **scorer rank**; pLDDT becomes an **explicit** sort.

---

**1 — ⚠⚠ THE MEASUREMENT, AND IT IS WORSE THAN THE RULING THAT PRECEDED IT.**

**The Planner ruled this as *"a de facto ranking by a third of the real ranking"* — `F-051` measures
`membrane_proximal_plddt` at 32.2% of attribution.** ⚠⚠ **The verification found something neither
of us had measured:**

| old default's top 3 | pLDDT | scorer rank |
|---|---|---|
| **UGT8** | 84.23 | ⚠⚠ **none — `held_out`** |
| **ENPP5** | 83.20 | ⚠⚠ **none — `held_out`** |
| **TLR3** | 81.41 | ⚠⚠ **none — `held_out`** |

**Six of the old default's top ten were not in the ordering at all. `FAM171A1`, the actual rank 1,
sat FOURTH.**

⚠⚠ **So the page's first screen was substantially filled with proteins the scorer NEVER RANKED,
presented above the real head of the ranking — and the rows it promoted were the ones DELIBERATELY
EXCLUDED from the thing the page appeared to be showing.** **A reader taking the top of that list as
*the best targets* was reading held-out rows.**

⚠ **`D-016`, key stated:** `/api/analyses` sorted `mean_plddt desc`, **intersected with
`/api/ranking`'s 56**, measured at **v100.**

**2 — ⚠ THE RULING, AND ITS REASON, WHICH IS THE PART THAT BINDS.**

**`CensusTable.jsx` already refused a pLDDT default as *"turning self-reported confidence into a de
facto ranking."*** **`/targets` did it anyway — same reasoning, opposite behaviour, two surfaces.**

⚠⚠ **The cohort IS ranked — by the SCORER, not by pLDDT.** **`D-102`'s own distinction holds: a
reader CHOOSING a lens is neither judgement nor measurement; the SYSTEM choosing it and calling it
the order is.**

⚠ **`F-051`'s caveat travels with the 32.2%: it is PREDICTOR WEIGHT, not causal share** — *and the
defect being corrected is a fraction standing in for the whole, so the correction must not repeat the
error in its own justification.*

**3 — PLACEMENT OF THE 26 UNRANKED. Five clauses, all owner-ruled.**

**Measured rather than assumed** — ⚠ **one of the four named causes is EMPTY:**

| cause | n | |
|---|---|---|
| `below_floor` | **11** | ranked, folded, pLDDT 30.68–49.46, under the `D-060` floor of 50 |
| `held_out` | **13** | 12 folded, 1 failed |
| `not_folded` | **2** | FAT2, MUC16 — oversize, never attempted |
| ⚠ `unranked_unexplained` | **0** | **empty** |

1. ⚠⚠ **PARTITION, NOT POSITION.** The 56 render in rank order with their integer; the 26 render in a
   **separate group beneath, with no position number of any kind.** **Not rows 57–82.**
2. ⚠⚠ **THE PARTITION BINDS TO THE RANK AXIS ONLY.** **Choose another column and all 82 order
   together** — *permanently quarantining them would claim they are outside EVERY ordering, which is
   a different false claim.* ⚠ **This scoping exists because the ruling was stated as REASONING —
   *"they have no position in a scorer ordering"* carries its own boundary; *"put them at the bottom
   of a separate group"* would not have.** *(Code's observation, and it is the durable lesson.)*
3. ⚠ **`IGF2R` renders BOTH causes, `held_out` leading** — *held-out was decided before a card was
   involved; the OOM is what happened afterwards.* ⚠⚠ **A row with two causes showing one is an
   absence with a cause hiding an absence with a cause.**
4. **Accession ascending, and the arbitrariness stated.** ⚠ **Accession is the only available order
   that is not a ranking of something** — any quality-adjacent key smuggles an order back in.
   **Visible, not collapsed:** *a collapsed group is a filtered default wearing a disclosure control.*
5. ⚠⚠ **THE EMPTY BUCKET IS WHAT MAKES SHOWING A CAUSE HONEST.** **If a row ever lands in
   `unranked_unexplained` the group says *"no cause recorded"* — never a dash.** *(Code's clause.)*

**4 — ⚠ THE FLOOR HOLDS, AND THE PAGE SAYS SO.**
`D-060` pre-registered the pLDDT floor at 50. **The highest excluded row is `ATP2B2` at 49.46 — short
by 0.54.** ⚠⚠ **Moving a threshold after seeing which rows fall outside it is exactly what
pre-registration prevents. THE FLOOR STAYS.** **The group states the pre-registered floor and renders
`49.46`, so a reader can judge the cutoff without us moving it.** ⚠ **What it costs is recorded
separately as a finding, not as a proposal.**

**5 — What shipped, and how it was proven.**
**`TA1` consumes `/api/ranking`; `_latest_valid_result` already carries `valid ∧
run_kind='preregistered'` (`D-064` dec 3 + `D-065` dec 4).** ⚠⚠ **Nothing re-derived** — *re-deriving
the predicate would be `F-052` again in the exact place the order warned about it.*
**`TA4`: 14 new tests, 10 reddening at the assertion under the old default.** ⚠ **The property is that
`FAM171A1` ranks 1 with a LOWER pLDDT than `NECTIN4`, so the ordering is IMPOSSIBLE under the old
default** — **a property that cannot hold both ways, not a snapshot of the new order.**

**⚠ Two defects found during the build are recorded in `F-047`, not here** — an invented `below_floor`
cause, and a test whose title argued for the behaviour it pinned.

**6 — ⚠ What this does NOT do.**
- **It does not change `D-060`'s floor** · **does not rank the 26** · ⚠ **does not remove pLDDT as a
  sort** — *`D-102` protects the reader's lens and this ruling narrows only the DEFAULT.*
- ⚠⚠ **It does not extend the partition beyond the rank axis.**
