# Claim-time tier enforcement, and what tranche 5 would cost

> **Two parts, and they are connected.** §1 is a **finding + proposal**: the local/rental routing
> decision is computed carefully and **enforced nowhere**. §2 is the **cost analysis** for the
> rental tranche. ⚠ **§2 is the reason §1 is urgent** — the moment tranche 5 is ingested, an
> unfiltered `/claim` points 776 oversize fp16 jobs at an 8 GB card.
>
> ⚠ **Nothing here has been implemented.** Tranche 4 is mid-flight and the claim path is not being
> touched while it folds.

---

# §1 — FINDING: `tier` is computed by the manifest and enforced by nobody

## What is true

`core/manifest.py` decides `local` vs `rental` per row — the whole point of the routing table, with
`tier_reason` recorded per row. `TIER_RECIPE` then resolves the recipe **at claim time** (D-047):

```python
{'local': {'dtype': 'int8', 'chunk_size': 64}, 'rental': {'dtype': 'fp16', 'chunk_size': 64}}
```

⚠ **And `core/queue.py:claim()` is:**

```sql
UPDATE jobs SET status='claimed', ... WHERE id = (
    SELECT id FROM jobs
    WHERE status = 'pending'                 -- ⚠ THE ENTIRE PREDICATE
    ORDER BY created_at, id
    FOR UPDATE SKIP LOCKED LIMIT 1)
```

**No tier. No length.** A worker takes the oldest pending job, whatever it is.

## Why it has not bitten

⚠⚠ **Because no rental row has ever been ingested.** The only thing keeping rental work off the
local card is that none exists yet. **That is an operational convention doing a guard's job**, and
it holds exactly until someone runs the obvious next command.

## What it would cost the moment tranche 5 lands

| | |
|---|---|
| tranche 5 | **776 rows, all `tier=rental`, 441–14,451 aa** |
| local card | **8,150 MiB total** (measured, `ceiling_climb` header), `known_good = 440` aa **at int8** |
| recipe a rental job resolves | **`fp16`** — roughly double the activation memory of int8 |

So an unfiltered claim folds **fp16 at 441+ aa on a card whose measured int8 ceiling is 440**.

⚠⚠ **An fp16 probe is what bugchecked this host on 2026-08-12.** On WDDM an over-allocation is
**not refused** — the driver spills to system memory and faults in kernel mode. **D-082 layer 3
does not survive that. Nothing does**; layers 1 and 2 are the only mitigations, and layer 1 is an
owner-attested driver setting that `sysmem_fallback_state()` deliberately reports as `unknown`.

⚠ **FIFO is a delay, not a safeguard.** Tranche 5 rows would queue *behind* tranche 4's remainder —
and then be claimed the instant tranche 4 drains, most likely unattended.

## Proposal

1. **The worker declares its tier; `claim()` filters on it.** `WORKER_TIER`, defaulting to
   `local`. ⚠ **Defaulting to `local` is the safe default** — the failure mode of wrongly refusing
   work is an idle GPU; the failure mode of wrongly accepting it is a host bugcheck.
2. ⚠ **The tier must be filtered in the SQL, not checked after the claim.** A post-claim check
   marks the job `claimed` and then declines it — the shape that stranded ten jobs (F-032):
   `attempts=0`, no error, nothing retryable.
3. **A second, independent length guard at fold time.** ⚠ Tier is a *label*; length is the physical
   constraint. `vram_guard.preflight()` already returns `REFUSED_NO_MEASUREMENT` for an unmeasured
   length — ⚠ **it is simply not wired into the fold path.** A mislabelled row must still be
   refused.
4. **State the composition on every claim refusal.** *"No work for tier `local`; 776 pending at
   tier `rental`"* — ⚠ an idle worker and an empty queue must never look identical.

⚠ **Not yet numbered as an `F-` entry.** Next free is `F-035`, and taking an integer under
momentum is the F-025 defect. **Owner ruling wanted** on whether this is a finding (a defect that
exists now) or a decision (a gap that only becomes a defect on ingest). **My read: a finding** — the
manifest's routing is load-bearing and is not enforced, independently of whether anyone has tripped
it yet.

---

# §2 — What running tranche 5 would cost

## The time model, measured

Fitted on **2,436 real per-fold durations** (`claimed_at` → `completed_at`) across tranches 1–4:

| tranche | n | median span | median duration |
|---|---|---|---|
| 1 | 1,307 | 35 aa | 2.74 s |
| 2 | 535 | 89 aa | 3.24 s |
| 3 | 516 | 219 aa | 14.77 s |
| 4 | 78 | 368 aa | 49.39 s |

⚠⚠ **The first fit I ran was wrong and would have understated the answer by an order of
magnitude.** A naive log-log fit gave **`k = 1.52`** — because 535 of 1,129 points are tranche 2,
where the **2.74 s fixed per-job overhead dominates the O(L³) trunk**. Low-L points are mostly
overhead, so they flatten the curve. **Subtract the floor first:**

| window | exponent |
|---|---|
| tranches 2–4 (51–439 aa) | **k = 3.22** |
| tranches 3–4 (152–439 aa) | **k = 2.69** |
| tranche 4 only (301–439 aa) | **k = 2.45** |
| median check t2→t3 | k = 3.52 |
| median check t3→t4 | k = 2.62 |

Consistent with the trunk's O(L³) triangular attention, ⚠ **and the exponent DECREASES with
length** — chunking (`chunk_size=64`) is doing its job. So the high-`k` column below is
conservative and the low-`k` column is the better guess in the near band.

## ⚠ Time is NOT the binding constraint. Memory is.

**A protein that does not fit does not fold slowly — it does not fold.** Measured anchor:
**440 aa at int8 ≈ 6.5–6.7 GB.** fp16 roughly doubles it, and the pair representation grows ~O(L²).
Rough capacity, **estimate not measurement**:

| card | VRAM | est. max single-sequence span, fp16 + chunk 64 |
|---|---|---|
| local (current) | 8 GB | ~440 aa **measured**, int8 |
| A6000 / L40S | 48 GB | **~850 aa** |
| A100 / H100 80GB | 80 GB | **~1,100 aa** |

⚠⚠ **These are extrapolations and the project's own instrument refuses to make them.**
`vram_guard.preflight()` returns **`REFUSED_NO_MEASUREMENT`** for a length with no measured
requirement — *"a length with no measured requirement is a category, not a green light."* **A cost
plan built on the table above is planning, not permission.** Each card class needs its own
`ceiling_climb` before anything is queued to it.

## The split, and where the money actually goes

GPU-hours are **this 8 GB card's seconds**; a rented A6000/A100 is faster per fold — ⚠ assume
**2–4×, an assumption, not a measurement** — so divide.

| span band | rows | k=2.45 (low) | k=3.22 (high) | verdict |
|---|---|---|---|---|
| 441–850 aa | **566** (73%) | **26 GPU-h** | **48 GPU-h** | plausible on 48 GB |
| 851–2,000 aa | 171 (22%) | 41 GPU-h | 130 GPU-h | needs 80 GB class |
| 2,001–4,000 aa | 26 (3.4%) | 48 GPU-h | 284 GPU-h | beyond single-card estimate |
| **4,001–14,451 aa** | **13 (1.7%)** | **182 GPU-h** | **2,827 GPU-h** | ⚠ **infeasible as one sequence** |

⚠⚠ **The headline: 73% of the rows are ~26–48 GPU-hours. The last 1.7% is 182–2,827.** Thirteen
proteins dominate a budget of 776 — and they are the ones **least likely to fold at all**, because
they exceed every card in the table. **The tail is not expensive; it is impossible, and its
"cost" is an extrapolation of a curve 30× past where it was measured.**

⚠ `Q8WXI7` MUC16 at **14,451 aa** is in that tail — already a D-085 named exclusion whose stated
conditions say a structure is **producible but not meaningful** (intrinsically disordered,
D-076 Tier 3). ⚠ **Spending the largest single line item in this budget on it would buy a
structure the project has already ruled uninformative.**

## Rough money

⚠ **Market rates, not quotes — check before committing.** Approx. spot/on-demand:
A6000 ≈ **$0.50–0.80/h**, A100 80GB ≈ **$1.50–2.50/h**, H100 ≈ **$2–4/h**.

**The 566-row band on a rented A6000**, taking the high-k estimate (48 GPU-h) and a conservative
2× speedup → **~24 h → roughly $12–20 of GPU time.**

⚠⚠ **The GPU is not the cost. The setup is.** A rental worker needs the D-036 out-of-band artifact
path, a `ceiling_climb` on the new card before anything is queued, and — per §1 — **claim-time tier
filtering, or the rental jobs are visible to the local worker the moment they exist.**

## Recommendation

1. **Hold tranche 5.** Finish tranche 4; that completes the entire local-tier census — **2,691 of
   3,467 rows**, everything foldable on this hardware.
2. **Implement §1 before ingesting any rental row.** It is the precondition, not a follow-up.
3. **Run a `ceiling_climb` on whatever card is rented, before queueing to it.** ⚠ The 850/1,100 aa
   figures above are estimates, and `preflight()` refuses unmeasured lengths by design.
4. **Split tranche 5 by feasibility rather than treating it as one unit.** The 566-row band is
   cheap and routine. ⚠ **The 39 rows above 2,000 aa are a separate decision** — they need domain
   assembly (which changes `boundary_method`, so the artifacts are not comparable to single-pass
   folds), and that is a modelling decision, not a purchase.


---

# §3 — CORRECTION: "infeasible" / "impossible" was wrong, and the 13 are not what I called them

> **Added 2026-08-16 after the owner challenged the word.** ⚠ **The table in §2 says "infeasible as
> one sequence" and my summary said "impossible." Both were wrong, and the second was wrong in the
> exact way `D-085` had just ruled against** — *excluded* did not mean *unfoldable*, and neither
> does this. ⚠ **The original wording is left standing above and corrected here, not edited away.**

## What is actually true — a hard limit, and it is not the one I cited

`facebook/esmfold_v1`: **`max_position_embeddings = 1026`**, **`position_embedding_type = rotary`**.

⚠ **Rotary embeddings extrapolate — there is NO mechanical cutoff.** So nothing refuses a long
sequence on model grounds. But **~1,026 is the trained context**, and beyond it the model is
running outside the distribution it was fitted on. **It will return a structure. There is no
evidence it means anything.**

⚠⚠ **That implicates far more than 13 rows:**

| tranche-5 spans | rows |
|---|---|
| > 850 aa (past the 48 GB estimate) | **210** |
| **> 1,026 aa (past the TRAINED CONTEXT)** | **141** |
| > 2,000 aa | 39 |
| > 4,000 aa | 13 |

⚠ **This is not a hardware question and renting a bigger card does not touch it.** §2 framed the
rental tranche as a memory-and-money problem; **for 141 rows the binding constraint is the model,
not the GPU.**

## The 13, named — and they are not a junk tail

| accession | symbol | span | what it is |
|---|---|---|---|
| Q14517 | **FAT1** | 4,160 | protocadherin — cadherin repeat stack |
| Q9NYQ8 | **FAT2** | 4,030 | protocadherin |
| Q8TDW7 | **FAT3** | 4,122 | protocadherin |
| Q6V0I7 | **FAT4** | 4,466 | protocadherin |
| Q07954 | **LRP1** | 4,400 | LDLR-related — LDLa/EGF/β-propeller modules |
| Q9NZR2 | **LRP1B** | 4,420 | LDLR-related |
| P98164 | **LRP2** | 4,398 | LDLR-related (megalin) |
| O75445 | **USH2A** | 5,011 | usherin — laminin/fibronectin domains |
| Q8WXG9 | **ADGRV1** | 5,879 | adhesion GPCR — Calx-β repeats |
| Q86WI1 | **PKHD1L1** | 4,190 | fibrocystin-L — IPT/TIG domains |
| Q685J3 | **MUC17** | 4,368 | mucin — tandem repeats |
| Q9UKN1 | **MUC12** | 5,364 | mucin — tandem repeats |
| Q8WXI7 | **MUC16** | 14,451 | mucin (CA-125) |

⚠⚠ **All thirteen are `census_class = surface`.** On an ADC target platform that is the class that
matters — **these are not the rows to discard, they are among the rows most worth having.**

## They split into TWO groups, and neither is "impossible"

**Group A — modular ordered repeat proteins (10):** FAT1–4, LRP1/1B/2, USH2A, ADGRV1, PKHD1L1.
⚠ **These are stacks of independently-folding domains, each comfortably inside the 1,026 trained
context.** Domain assembly is not a workaround for them — **it is arguably the correct way to model
them**, and a single 4,400-residue pass would be the questionable choice even on infinite VRAM.
**Verdict: a METHOD limit with a known remedy, not a limit at all.** ⚠ Assembly changes
`boundary_method`, so the artifacts are **not comparable to single-pass folds** without saying so
(D-076 Tier 2 already says this for FAT2).

**Group B — mucins (3):** MUC16, MUC12, MUC17. Tandem repeats, heavily O-glycosylated, largely
intrinsically disordered. ⚠ **A structure is PRODUCIBLE and uninformative** — exactly the D-085
condition already recorded for MUC16. **Verdict: a BIOLOGY limit. More compute does not help, and
neither does domain assembly.**

⚠ **Nothing in the 13 is impossible.** Ten have a clear method; three have a clear reason the
question is malformed. **"Impossible" collapsed those into one word and pointed at the wrong
remedy for both.**

## The owner's read was right: this is a tranche 6, not a bigger tranche 5

⚠ **Domain assembly is a different KIND of work**, not more of the same: it needs a domain-boundary
source, a per-domain span definition, an assembly step, and a `boundary_method` that says so.
**Its artifacts do not belong in the same population as single-pass folds** — which is precisely
why it is a separate arc and not a longer queue.

**Revised recommendation:**
1. Tranche 5 becomes **the 566 rows at 441–850 aa** — measurable, cheap, single-pass, inside the
   trained context.
2. ⚠ **The 141 rows above 1,026 aa do not belong in ANY single-pass tranche**, at any budget, on any
   card. Renting hardware for them buys extrapolation.
3. **Tranche 6 is the domain-assembly arc** for Group A. It is a modelling design task, not a
   purchase — and it is where several of the most interesting surface targets live.
4. **Group B stays excluded**, with the D-085 conditions already stated.
