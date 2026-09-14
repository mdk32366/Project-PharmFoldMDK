# §D — Slice 4 enumeration. READ-ONLY. No database, no tunnel, no `.env`.

**Source:** `data/census/census_manifest.v7.csv` (committed), the on-disk slice enumerations, and
`core/foldability`. **Nothing was written.** ⚠ `scripts/task4_slice4.py` is deliberately NOT created
— §C and §I had to merge first so the identity check and the shell split are in it from commit one.

---

## 1. ⚠ The Planner's figure is contradicted, as ordered

**Roughly 735 rows** was arithmetic on two committed numbers (D-137's `local` total of 2,691 minus
slices 1–3), not an enumeration.

**The enumeration says 600.**

## 2. Every band, measured against D-157's table

| band | counted | D-157 | delta | span range | mean |
|---|---|---|---|---|---|
| 1–10 | 130 | 130 | **0** | 1–10 | 5.3 |
| 11–30 | 395 | 395 | **0** | 11–30 | 21.8 |
| 31–100 | 1,101 | 1,101 | **0** | 31–100 | 47.3 |
| **101–250** | **600** | **600** | **0** | **101–250** | **174.6** |
| 251–384 | 346 | 346 | **0** | 253–384 | 317.3 |
| **TOTAL** | **2,572** | **2,572** | **0** | | |

⚠ Tranche 1–4 rows carrying a span: **2,691**. Above the 384 aa campaign envelope: **119** —
D-157's named remainder, and **not local** for this campaign.

## 3. ⚠⚠ The "1–10 remainder" does not exist

The orders name *"bands 101–250 and the 1–10 remainder"*. **There is no remainder.**

Band 1–10 holds 130 rows. Slice 2's band was (1, 30) and it enumerated all 525 = 130 + 395.
Of the 130, **four** are absent from slice 2's enqueued set — and all four are Task 3 twenty rows:

    Q8WXF7  span=1    Q9Y3E0  span=2    Q86Y82  span=7    Q8TB68  span=9

Slice 2 enumerated 525 and enqueued 517. **All eight of the difference are in the Task 3 twenty**
(`A6ND48`, `Q0VDE8`, `Q86Y82`, `Q8TB68`, `Q8WXF7`, `Q9BRY0`, `Q9ULK5`, `Q9Y3E0`) — already folded
under Run 2, correctly excluded to avoid two Run 2 rows on one accession.

**So slice 4's population is band 101–250 and nothing else: 600 rows.**

## 4. Band 101–250 detail

- **600 rows**, span range 101–250, mean **174.6**, median **178**
- By tranche: **t2 = 216, t3 = 384**. ⚠ No tranche 1 or tranche 4 rows fall in this band.
- **Rows whose envelope is not `local` under `core/foldability`: ZERO.**

## 5. ⚠ A finding worth a number, raised rather than taken

`core/manifest.LOCAL_CEILING.local_bound = 440`, but the campaign caps at `CAP_AA = 384`.

So `core.foldability.envelope()` calls spans **385–440 `local`** while D-157 rules them out as
card-bound. Two notions of "local" differ by 56 aa, and **119 rows sit above the campaign cap**.
Nothing is wrong today — the campaign scripts use `CAP_AA`, not `envelope()` — but this is the
two-paths-to-one-quantity class (`F-046`, `F-014`) in a quantity that decides what gets folded.

⚠ **No integer is claimed for this.** It is reported for an owner ruling.

## 6. Overlap arithmetic

    band size:                    600
    already carrying a Run 2 row: REQUIRES THE DATABASE — behind §C, not computed here
    to enqueue:                   pending the above

⚠ **Slice 4 still requires the owner's ruling (`D-161`), its own enqueue behind `D-159`, and its
runner written with `D-160`'s split from the first commit.**
