# DRAFT — `D-102 amendment 2` — for the Planner to rule on

> ⚠⚠ **THIS IS A DRAFT AND IS NOT IN THE LOG.** Code drafts, the Planner rules — the `D-075`
> proposal split, per `ORDERS-Code-default-sort-and-the-3dmol-debt.md` §2 `TB1`. It carries no
> integer, and `‹N›` is deliberately left unresolved in the title below so the amendment checker
> does not count it as a citation.
>
> ⚠ **The placement of the unranked (`TA2`) is reported here as a PROPOSAL and has not been built.**
> §4 of the orders: *placement of the unranked is a decision, not a default.*

---

## Proposed entry

### `#### D-102 amendment ‹N›` — The default sort is itself a lens, and a page that arrives pre-ordered has chosen one; `/targets` defaults to the scorer rank, and the unranked are partitioned rather than positioned

- **Date:** 2026-08-21 · **Status:** ⚠ **PROPOSED — Planner to rule** · **Author:** Code (draft)

**THE TWO SURFACES DISAGREED, AND THE DISAGREEMENT WAS THE FINDING.** `CensusTable.jsx` refuses a
pLDDT default in its own source — *"a self-reported confidence into a de facto ranking"* — and pins
the census default to `accession`. `/targets` defaulted to **mean pLDDT descending**. ⚠ **Same
reasoning, opposite behaviour, on two surfaces**, and neither file mentioned the other.

**THE OWNER'S RULING (2026-08-21):** default to the **scorer rank** where one exists; **pLDDT becomes
an explicit sort the reader chooses.**

**⚠⚠ THE FIGURE THAT MAKES THIS A RULING AND NOT A PREFERENCE.** `F-051` measures
`membrane_proximal_plddt` at **32.2%** of the scorer's attribution (against `mean_plddt_ecd` at
6.4%). **So ordering the cohort by pLDDT is a de facto ranking by roughly a third of the real
ranking, presented as though it were the ranking.** ⚠ That is *worse* here than on the census, not
better: on the census nothing else is competing to be the order, while here a real scorer ordering
exists and the page was showing a proxy for it. ⚠ `F-051`'s own caveat travels too — a 32.2%
attribution share is a share of *predictor* weight, not a causal role — and it does not weaken the
point, because the defect is that a **fraction** was standing in for the **whole**.

**WHAT `D-102` ALREADY SETTLED, AND WHAT THIS ADDS.** `D-102` ruled that **a stated lens is neither a
judgement nor a measurement** — a reader choosing to sort by stained fraction is looking at data
another way. ⚠ **This amendment names the boundary of that permission: the reader choosing a lens is
licensed; the SYSTEM choosing one and presenting it as the order is not.** A default sort is a lens
applied before anybody asked, and it is the one lens the page does not label.

**RULING 1 — `/targets` defaults to the scorer rank**, taken from the pre-registered run.
⚠ **`F-049` applies and the conjunction is load-bearing:** `run_kind='preregistered'` alone does not
identify the run, because `id=1` carries that value with **zero scored rows**. The predicate is
`valid ∧ run_kind='preregistered'`. ⚠⚠ **It must not be re-derived.** `app/reads.py`'s
`_latest_valid_result` already implements exactly this conjunction (`D-064` decision 3 for *valid*,
`D-065` decision 4 for *pre-registered*), and `/api/ranking` already serves its 56 rows. **A second
way to identify the run is `F-052`'s shape, and this project has spent the week paying for it.**

**RULING 2 — pLDDT remains an explicit sort**, and when the reader chooses it, it carries the same
sentence the census uses. ⚠ **The lens is stated where the lens is applied** — nothing is removed,
and the reader keeps every ordering they had.

**⚠⚠ RULING 3 — THE 26 UNRANKED ROWS ARE PARTITIONED, NOT POSITIONED. This is the clause needing the
ruling.** **56 of the 82 are scored.** The other 26 **have no position in a scorer ordering at all.**

⚠ **Measured at v99 against `/api/ranking` ∩ `/api/coverage` ∩ `/api/analyses`, not taken from the
orders' vocabulary — and one of the four named causes is empty:**

| cause | n | how it is known |
| --- | --- | --- |
| `below_floor` | **11** | `disposition: ranked`, folded, `mean_plddt` **30.68 – 49.46** — every one under `D-060` decision 5's floor of 50 |
| `held_out` | **13** | `disposition: held_out` (12 folded, 1 failed) |
| `not_folded` | **2** | `disposition: excluded` — `FAT2` and `MUC16`, oversize, never attempted |
| `unranked_unexplained` | **0** | ⚠ **empty at v99. Every one of the 26 has a stated cause.** |

⚠⚠ **That the fourth bucket is empty is load-bearing for clause 3:** showing the cause in place of a
rank is only honest if a cause always exists, and today it does. **If a row ever lands in
`unranked_unexplained`, the group must say *"no cause recorded"* and not fall back to a dash** —
that is the state `F-044`'s shape hides in.

⚠ **Sorting them to the bottom would rank them 57th through 82nd. They are not last; they are
unranked, and a sort that sinks them is a ranking of scoreability** — the same defect in a new coat,
which is precisely what this amendment exists to stop.

**Proposed placement:**
1. The **56 ranked rows** render in rank order, each showing its **actual rank integer**.
2. The **26 unranked** render in a **visually separate group beneath**, under a heading that states
   *these have no scorer rank* — ⚠ **not** as rows 57–82, and with **no position number of any kind**.
3. In that group the rank column shows **the cause** (`below_floor` / `held_out` / `not_folded` /
   `unranked_unexplained`), never a dash and never a number. ⚠ Every absence is a category with a
   cause.
4. Within the group, rows are ordered by **accession ascending**, and **the arbitrariness is
   stated** — accession is the census's own default precisely because it encodes no judgement.
5. ⚠ They are **not hidden** behind a control. 26 of 82 removed from the default view would be a
   silent exclusion, which is worse than a wrong order.

⚠ **What is derived and what is chosen.** Clauses 1–3 follow from the owner's stated reasoning: if
the unranked have no position, they cannot be given one. **Clauses 4 and 5 are choices** — the
internal ordering of the group, and its visibility by default — **and those are what the Planner is
asked to rule on.**

**WHAT THIS DOES NOT DO.** It does not score the census (`D-079` decision 1 stands: a fold is a
measurement, a score is an interpretation). It does not make the two populations reachable through
one another (`D-081`). And it does not change what the scorer computes — **only which ordering the
page arrives in, and what it says about it.**

---

## ⚠ Open questions for the ruling

**1. A row with two causes needs a precedence, and `IGF2R` is that row.** It is `held_out`
**and** its fold failed (CUDA OOM at 2,491 aa). Both are true; the group can show only one.
⚠ Code's proposal is **disposition first** — `held_out` is a decision made *before* the fold was
attempted, so it is why the row was never going to be ranked regardless of how the fold went. **The
fold failure is the second fact, not the first.** ⚠ This is a choice and it is not derivable.

**2. Do clauses 4 and 5 stand?** The internal ordering of the unranked group (accession ascending,
stated as arbitrary) and its visibility by default (shown, not hidden behind a control).

**3. ⚠ Is `below_floor` at 11 rows a finding rather than a category?** Eleven of the 82 are excluded
by a pLDDT floor of 50, and the highest of them is **49.46** — `ATP2B2`, short of the floor by
**0.54**. ⚠⚠ **`F-053`'s lesson is exactly this shape: a threshold on a scalar that is standing in
for something else.** Code is **not** proposing the floor move — `D-060` decision 5 pre-registered
it, and moving a pre-registered threshold after seeing the data is the defect that pre-registration
exists to prevent. **It is flagged because a reader who sorts by rank will see eleven rows outside
the ordering and one of them missed by half a point**, and the page should probably say so.
