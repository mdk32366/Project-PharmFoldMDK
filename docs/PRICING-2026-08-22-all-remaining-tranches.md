# PRICING — ALL REMAINING TRANCHES — 2026-08-22

**AUTHORED-SHA256** (range: **first `## §` header → EOF**, anchored to line starts, **SECOND
occurrence of the marker**) = `db121bb6aaeb11fa8341a67091a278812959d96916a928ce71f6ab736101b605`
**bytes** = `9961`

> Written by the Planner on the owner's ruling *"Rental, scoped. All remaining tranches priced."*
> ⚠ **Priced from committed surfaces, not from a live database read** — the MPG proxy on 16380 was
> closed and raising it is the owner's. Every key is stated so each number can be re-derived.

---

## §0 — ⚠ What this prices, and what it CANNOT prove

**It prices the rows that remain unfolded across every tranche, at the recipe the local ceiling was
measured under (int8, `chunk_size=64`).**

⚠ **It cannot prove a row is unfolded.** Fold state lives in the database; this reads
`census_manifest.v7.csv` (3,467 rows) against the **last live read** recorded in
`CLOSEOUT-Code-2026-08-21.md` §1 — *2,690 folded of 3,467*. **A stale fold count moves the
local-straggler line and nothing else**; the rental population is defined by `tier`, not by fold
state, so the money is unaffected.

⚠ **It is not a suitability axis** (`census_cost.py`'s standing caveat, D-077 dec 1). Nothing here
says a target is a good ADC target, and no row is filtered by affordability.

## §1 — The population, by tranche

| tranche | rows | tier | span band | remaining | rental cost |
|---|---|---|---|---|---|
| 1 | 1,307 | local | 1–50 aa | — | **$0** |
| 2 | 535 | local | 51–149 aa | — | **$0** |
| 3 | 517 | local | 152–300 aa | — | **$0** |
| 4 | 332 | local | 301–439 aa | — | **$0** |
| **5** | **776** | **rental** | **441–14,451 aa** | **776** | **§4** |
| 6 | — | — | — | — | ⚠ **not priceable** |

**Local tier totals 2,691; the last live read folded 2,690. So ONE local-tier row is unfolded, and
it costs nothing** — it is under the ceiling by construction. ⚠ Its identity needs a database read;
it does not need money.

⚠⚠ **Tranche 6 has NO ROWS and cannot be priced.** It is a *design* — `D-091` ruling 3's gate,
discharged by `D-095`'s tiling amendment. `census_manifest.v7.csv` carries tranches 1–5 only.
**Tranche 6 is a re-tiling of tranche-5 rows, not a new population**, so pricing it separately would
double-count rows already priced in §4. *An absence with a cause, not a zero.*

## §2 — ⚠⚠ The memory law, MEASURED — and it replaces a guess

`data/control/sb_timing/timings.json` holds ten folds (2026-08-20 02:40–02:43 UTC, driver 610.88).
Subtracting the resident model at `span_aa = 1`:

| span | peak GiB | incremental GiB |
|---|---|---|
| 1 | 5.24 | 0.00 — the resident model |
| 134 | 5.36 | 0.12 |
| 218 | 5.55 | 0.31 |
| 315 | 5.89 | 0.65 |
| 439 | 6.50 | 1.26 |

**Consecutive fitted exponents: 1.95 · 2.01 · 1.99.**

> **`incremental_GiB = 7.215e-06 · L^1.983`**, with a **5.24 GiB** resident model and **1.43 GiB** of
> CUDA context / workspace / fragmentation overhead, calibrated from `free_after = 0.03` at 439 aa.

⚠ **This is the pair representation, and that is why the exponent is 2.** Chunking at 64 stops the
trunk materialising its O(L³) triangular attention; what stays resident is the O(L²) pair tensor.
**The law is mechanistic, not merely fitted** — which is the reason to trust it further out than a
bare curve fit would earn.

**Two paths to one quantity, compared ON THE NUMBERS:**

| check | law says | measured | source |
|---|---|---|---|
| peak at 456 aa | 6.59 GiB | **6.60 GiB** | `ceiling_climb.int8.uncapped.jsonl`, `Q8WXD0` |
| max span, local 8 GB | 431 aa | **432 aa** | `ceiling_climb.int8.release.jsonl` |

**A different protein, a different script, a different day — agreement to 0.01 GiB and to 1 aa.**

### What that does to the card table

| card | VRAM | **measured-law max span** | the 2026-08-16 proposal's guess |
|---|---|---|---|
| local | 8 GB | **431 aa** (measured: 432) | ~440, measured |
| A6000 / L40S | 48 GB | **~2,528 aa** | ~850 |
| A100 / H100 | 80 GB | **~3,379 aa** | ~1,100 |
| RTX PRO 6000 | 96 GB | **~3,702 aa** | — |

⚠⚠ **The proposal's estimates were ~3× too pessimistic** — it assumed fp16 (doubling the model) and
declined to extrapolate, correctly, *because it had no law.* It has one now. ⚠ **The 48 GB figure is
a 5.8× extrapolation beyond the fitted range and must be confirmed by a `ceiling_climb` on the rented
card before anything is queued** — `preflight()` returns `REFUSED_NO_MEASUREMENT` for unmeasured
lengths by design, and this table is **planning, not permission.**

## §3 — ⚠⚠ Three constraint classes. Only one of them is money

1. **MEMORY — no longer binding.** On a 48 GB card the law clears **2,528 aa**; only **25** of 776
   rows exceed it. *Renting solves this class outright.*
2. **TRAINED CONTEXT — binding, and money does not touch it.** `facebook/esmfold_v1` carries
   `max_position_embeddings = 1026`. Rotary embeddings extrapolate, so **nothing refuses a long
   sequence** — it returns a structure, and **there is no evidence it means anything.**
   **141 of 776 rows are past it.** ⚠ *A bigger card buys nothing here.*
3. **BIOLOGY — binding, and nothing touches it.** MUC16 / MUC12 / MUC17: tandem-repeat, heavily
   O-glycosylated, largely disordered. A structure is **producible and uninformative** (D-085,
   D-076 Tier 3). ⚠ *Neither compute nor domain assembly helps.*

**So the split that matters is 1,026 aa — the trained context — NOT the card's capacity.** The
2026-08-16 proposal split at 850 / 2,000 / 4,000 aa, which are memory boundaries. **Memory stopped
being the boundary the moment the law was fitted.**

## §4 — THE PRICE

**635 of 776 rows sit at or inside the trained context. That is the purchase.**

Time model: `t = 2.74 s + c · L^k`, floor and anchor from the **2,436 real per-fold durations**
across tranches 1–4 (anchor: tranche-4 median, 368 aa → 49.39 s). ⚠ The floor is subtracted first; a
naive log-log fit returns `k = 1.52` because the low-L points are mostly fixed overhead.

| `k` | GPU-h, this card | @2× rental | @4× rental |
|---|---|---|---|
| 2.45 (tranche 4 only — the near band) | 34.6 h | **17.3 h** | 8.6 h |
| 2.69 (tranches 3–4) | 40.3 h | 20.2 h | 10.1 h |
| 3.22 (tranches 2–4 — conservative) | 57.3 h | **28.6 h** | 14.3 h |

> ### **635 rows · 17–29 GPU-hours · $9 – $23** at A6000 $0.50–0.80/h, 2× speedup.

⚠ **The 2–4× rental speedup is an ASSUMPTION, not a measurement.** ⚠ **Market rates are not quotes.**
⚠⚠ **And the GPU is not the cost — the setup is:** the D-036 out-of-band artifact path, claim-time
tier filtering (or rental jobs are visible to the local worker the moment they exist), and a
`ceiling_climb` on the rented card. **Precondition, not follow-up.**

**Cross-check against the record:** `BATON-code-next-session.md` priced *566 rental rows at about
$12–20*. This prices **635 rows at $9–23** — more rows, same order, arrived at independently. **The
two agree.**

## §5 — ⚠⚠ What is NOT a purchase

**The 141 rows past the trained context — 136 of them `census_class = surface`:**

| band | rows |
|---|---|
| 1,027–2,000 aa | 102 |
| 2,001–4,000 aa | 26 |
| 4,001–14,451 aa | 13 |

**Folding all 141 costs ~$65–104** and buys 141 structures with **no evidence that any of them means
anything.** ⚠⚠ **That is not a cheap purchase. It is an expensive one, because the output is
unevaluable.**

**And for the ten that matter most, the remedy is FREE.** FAT1–4, LRP1 / LRP1B / LRP2, USH2A,
ADGRV1, PKHD1L1 are stacks of independently-folding domains, **each comfortably inside 1,026 aa —
most inside 440 aa, which is to say inside the LOCAL ceiling.** ⚠⚠ **Domain assembly is not a
workaround for these; it is arguably the correct model, and it runs on the local card at $0 rental.**
A single 4,400-residue pass would be the questionable choice *on infinite VRAM.* ⚠ Assembly changes
`boundary_method`, so the artifacts are **not comparable to single-pass folds** without saying so.

**⚠⚠ The largest line item in the naive budget should not be bought at all.**

## §6 — ⚠⚠ THE REFIT, PRE-REGISTERED HERE, BEFORE ANY FOLD

**`FC3` measured that nothing anywhere pre-commits a refit at a larger `n`. A refit chosen after the
folds are visible is post-hoc by construction — ten minutes before, unsalvageable after.**

Folding the 635 moves the census from **2,690** folded rows toward **3,325**. Pre-registered:

1. **The refit runs at `n = 3,325`, or at whatever `n` actually lands — stated before it is seen.**
2. **It is a NEW `ranking_run_id`. Runs are never mixed.** Runs 3 and 4 already share a
   `scorer_version` and three parameters, and mixing rows across runs *"would produce a clean,
   stable, meaningless slope."*
3. **Pre-registered branches, and the sentence permitting a third:** the six coefficients either
   **(a)** hold their signs and rank order, or **(b)** at least one flips sign. ⚠⚠ **A THIRD OUTCOME
   IS PERMITTED AND NAMED IN ADVANCE — the refit is UNDERPOWERED or degenerate at the new `n`.**
   `P-001` amendment 2 returned exactly that at n = 4, and a two-branch pre-registration meeting a
   three-answer question has already happened twice this week.
4. **`D-089` still holds: no census row is scored.** ⚠ If the refit is to score census rows, **that
   is a separate owner ruling and it is not made here.**

## §7 — Recommendation

1. **Buy the 635.** $9–23, 17–29 GPU-h, inside the trained context, memory no longer binding.
2. **Do not buy the 141.** Not on cost — on unevaluability.
3. **Assemble Group A's ten locally, for free.** That is the correct model, not a workaround.
4. **`ceiling_climb` on the rented card before one row is queued.** The 2,528 aa figure is an
   extrapolation, and `preflight` refuses unmeasured lengths by design.
5. **Ship claim-time tier filtering first**, or rental rows are visible to the local worker on sight.
6. **The three mucins stay excluded**, on the biology, as already ruled.

⚠ **Two findings this pricing produced, proposed and NOT written:** the `L^1.983` memory law, which
closes `D-077`'s unmeasured band by calculation and extends `F-053`'s *"the guard measures the wrong
axis"* with the right axis; and the fact that **the binding constraint on tranche 5 was never memory
at all — it was the trained context**, which no purchase relieves. `F-050` stays reserved.
