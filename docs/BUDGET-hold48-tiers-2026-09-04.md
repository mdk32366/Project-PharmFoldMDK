# Hold-48 budget and tier waves — 2026-09-04 (measured)

**Decision:** `D-113`. **Cite:** D-111 · D-112 · issue **#210**.
**Companion runbook:** [`GUIDE-renting-hold48.md`](GUIDE-renting-hold48.md).

⚠ **Measured, not vibes.** Every dollar figure below is either (a) arithmetic on a named
measurement or (b) an extrapolation whose formula and `n` are stated.

**Card rate for this pilot: $2.19/hr** (Matt/Trinity pin — **not $2.00**). Every `$` column
uses that pin.

**RunPod balance remaining after Terminate: $14.17.** That is a **measured remaining-balance
reading**, not a forecast, not a budget cap invented here, and not "what the 44 will cost."

This document does not enqueue jobs and does not touch Fly.

---

## Named unknown — Peak VRAM

**Peak VRAM is UNKNOWN.** That is the name of the quantity. It is not a gap to fill from
context.

- **Not in provenance.** The IGF2R pilot recorded claim→complete wall, mean_plddt, and
  artifact sizes. It did **not** record `nvidia-smi` `memory.used` (or any other peak) against
  job 3589 or 3590.
- **Do not invent a number.** Not a GiB, not a % of the card, not "it fitted so headroom is
  fine," not F-059's law applied to L=1608, not the card's advertised capacity as a peak.
  A successful L=1608 fold is **not** a VRAM measurement.
- **Closes only by capture on the next cold run.** [`GUIDE-renting-hold48.md`](GUIDE-renting-hold48.md)
  Step 5: start `nvidia-smi --query-gpu=… -l 10` **before** the first fold on the clean card,
  leave it running, copy the CSV off the box with PAE. Until that file exists, this cell stays
  **UNKNOWN**.

---

## 0. Two money piles (do not add them)

| Pile | What it is | What it is not |
|---|---|---|
| **Fold-only** | Claim→complete GPU-h × **$2.19/hr** | Not the invoice. Not pip. Not idle. |
| **Setup scars** | Pip thrash, torchvision/torchaudio ABI, SQLAlchemy/D-111 import hot-fix, idle time on the scarred pod | **Not** in the length-weighted other-44 forecast |

The other-44 projection in §4 is **fold-only**. Scar wall-clock from this pilot is **not
baked into** `t(L)`. Do not infer scar hours by subtracting $0.31 from the invoice — that
split is **not in provenance**.

---

## 1. What was measured (IGF2R pilot, claim → complete wall)

Card: **NVIDIA RTX PRO 6000 Blackwell Workstation Edition**.
Stack: **torch 2.11.0+cu128**, **transformers 5.14.1**, recipe **fp16 / chunk 64** (D-047 / D-111).
Rate: **$2.19/hr**.

| Job | Tile | L (aa) | Wall (s) | Wall (min) | mean_plddt | structure.pdb (B) | pae.json.gz (B) | plddt.json (B) |
|---|---|---|---|---|---|---|---|---|
| **3589** | tile0 | **1608** | **452.4** | **7.54** | **62.25** | **1,006,224** (~1.0 MB) | **18,908,543** (~18.9 MB) | **30,618** |
| **3590** | tile1 | **797** | **59.9** | **1.00** | **76.58** | **498,678** (~0.50 MB) | **4,939,852** (~4.9 MB) | **15,061** |

Fold-only GPU-h: `(452.4 + 59.9) / 3600 = 0.1423 h` (stated **0.142 GPU-h**).
Fold-only IGF2R cost: `0.142 GPU-h × $2.19/hr ≈` **$0.31**.

**Peak VRAM: UNKNOWN.** Named unknown — not in provenance. Do not invent a GiB. Closes only
when the next cold run's `nvidia-smi` log exists (runbook Step 5). A fitted L=1608 fold is
not that log.

**Stitch (laptop, `hold48_stitch.write_stitched`): PASS — Trinity accepted.** Off-block PAE
is **null, not 0** — **2,131,551** null cells, **0** literal zeros. Parent job **3356** still
`jobs.tier` NULL. Local stitch only; no prod write of the parent in this wave.

Domain-snap vs unsnapped planner: IGF2R `span_aa=2264` unsnapped windows are **1656 + 736**
(`tests/test_hold48_tiles.py`). The live tiles were **1608 + 797**. Snap moved an internal
edge (within `DOMAIN_SNAP_AA=64` plus last-tile clamp). **n_tiles stayed 2.**

---

## 1b. Setup scars (priced separately; not in §4)

Billed on the **same** scarred pod, **not** in the $0.31 fold-only figure, **not** projected
onto the other 44:

- pip thrash (`+cu128` torch on plain PyPI; incomplete `worker/requirements` → missing
  `transformers`)
- torchvision ABI / `nms` when not from the cu128 index
- torchaudio `c10_cuda_check` when not matched to `torch 2.11.0+cu128`
- SQLAlchemy / D-111 `core.hold48` import hot-fix (D-112 is the durable shape; do not add
  SQLAlchemy to `worker/requirements.txt`)
- idle time (browser-tab drop, waiting on a broken import, empty-queue poll)

**Scar wall-clock as a split is not in provenance.** The process rule is: Terminate this
pod, cold-start the runbook on a **clean** card (Wave 0), so the next invoice is not another
copy of this pile.

---

## 2. Remaining work (tile count)

Population: `data/census/census_manifest.v7.csv`, `tranche=5`, `span_aa > 1656` → **48** rows;
**3** mucins never tiled (`Q8WXI7` / `Q9UKN1` / `Q685J3`); **45** tileable.

How known: `plan_tiles(row, domain_ends=())` — empty domain ends because
`data/census/spancache/` is gitignored (CI has no cache; `domain_ends_span_relative` returns
`()`). Unsnapped geometry is window **1656** / stride **1528** (`n_tiles(L) = 1 if L≤1656 else
ceil((L-1656)/1528)+1`).

| Quantity | N | How known |
|---|---|---|
| Tileable proteins | 45 | census v7 minus 3 mucins |
| Unsnapped tiles on those 45 | **106** | `sum(n_tiles(span_aa))` — 31 proteins ×2, 12 ×3, 2 ×4 |
| IGF2R tiles (pilot) | 2 | measured jobs 3589 / 3590 |
| **Remaining tiles** | **104** | 106 − 2 |

⚠ Domain-snap **does not change n_tiles** (function of `span_aa` only). It **does** change
last-tile / snapped-edge lengths by up to 64 aa. Length-weighted hours below use **unsnapped**
lengths. Label: **predicted, unsnapped mix, fold-only**. Live mix will differ the way IGF2R
1656/736 became 1608/797.

Remaining unsnapped length mix:

| Band | n tiles | of which L=1656 | sum L (aa) |
|---|---|---|---|
| L ≤ 800 | 17 | 0 | 6,864 |
| 801–1200 | 16 | 0 | 15,344 |
| 1201–1655 | 11 | 0 | 15,303 |
| L = 1656 (full window) | 60 | 60 | 99,360 |
| **All remaining** | **104** | **60** | **136,871** |

Min / mean / max remaining L: **177 / 1316.1 / 1656**.

---

## 3. Length → wall model (n=2, thin)

Two points only: `(L=1608, t=452.4 s)` and `(L=797, t=59.9 s)`.
⚠ These are **claim→complete fold walls**, not pod-lifetime hours. Setup scars are §1b.

**Fit used for the tables below — power law through both points:**

```
ln(t1/t0) / ln(L1/L0) = p
p = ln(452.4/59.9) / ln(1608/797) = 2.88063
k = 452.4 / 1608^p = 2.62664e-07
t(L) = k · L^p = 2.62664e-07 · L^2.88063   (seconds)
```

This recovers both measured points by construction. The exponent sits near the ESMFold trunk's
**O(L³)** triangular attention (D-042), with chunk-64 so it is not a pure cube
(`t/L³` at 1608 vs 797 = `1.088e-07` / `1.183e-07`, ratio **0.92** — closer than `t/L²`,
ratio **1.86**).

**Linear through the same two points (shown as a check, not used for short tiles):**

```
t(L) = −325.824 + 0.483970 · L    (seconds)
```

Intercept is **negative**. Linear is unusable below ~673 aa (predicts t<0). It happens to
agree with the power law on the L=1656 cluster (most of the dollars) and must **not** be used
for Wave A.

**n=2 is thin.** A third measured point at L=1656 (or a short L≈400 last-tile) could falsify
the exponent. The kill switches exist so a bad extrapolation stops the wave, rather than
being believed.

Worked predictions from the power law at **$2.19/hr**:

| L | t (s) | t (min) | $ fold-only |
|---|---|---|---|
| 797 (measured) | 59.9 | 1.00 | 0.036 |
| 1608 (measured) | 452.4 | 7.54 | 0.275 |
| 1656 (predicted) | 492.4 | 8.21 | 0.300 |
| 1200 (predicted) | 194.7 | 3.25 | 0.118 |
| 800 (predicted) | 60.6 | 1.01 | 0.037 |

---

## 4. Remaining **fold-only** estimate (power law × unsnapped lengths)

`sum_i k · L_i^p` over the 104 remaining unsnapped tiles.
**Does not include** §1b scars, cold-start, PAE retrieve, stitch I/O, or idle.

| Wave | Length band | n | Predicted wall (h) | $ fold-only at $2.19/hr |
|---|---|---|---|---|
| **A** | L ≤ 800 | 17 | **0.058** | **0.13** |
| **B** | 801–1200 | 16 | **0.472** | **1.03** |
| **C1** | 1201–1655 | 11 | **0.923** | **2.02** |
| **C2** | L = 1656 | 60 | **8.207** | **17.97** |
| **All remaining** | — | **104** | **9.660** | **21.16** |

Linear-on-remaining (clamped at t≥0) totals **9.618 h / $21.06** — same dollars on C2,
different short-tile story. **C2 is the money** (60 full windows, 85% of predicted fold-only
spend).

---

## 4b. Remaining balance vs fold-only forecast

**Measured remaining after Terminate: $14.17.**

| Compare | $ | Note |
|---|---|---|
| Balance remaining (measured) | **14.17** | After Terminate of the scarred pod |
| Fold-only remaining forecast (§4) | **21.16** | 104 tiles, unsnapped, n=2 model |
| A+B+C1 fold-only | **3.18** | 44 tiles; fits inside $14.17 with headroom **if** Wave 0 is cheap |
| C2 fold-only | **17.97** | 60 × L=1656; **does not fit** on $14.17 even with **zero** cold-start |

⚠ **$14.17 is not a forecast of C2.** It is cash on the account. C2 at this model needs a
top-up **or** a cheaper card **or** a kill after the first three L=1656 tiles update `t(L)`.
Wave 0 (clean-card re-test) spends against the same $14.17 and is **not** in the $21.16.

---

## 5. Proposed waves, concurrency, caps, kill switches

**Concurrency: 1 pod** until peak VRAM at L=1656 is a measured number. One GPU, one
`python -m worker.main`. A second pod is not licensed by this appendix.

`$` caps use **$2.19/hr × hours cap**, rounded up, and include a **setup allowance** on top
of fold-only. Caps are **stop-and-call**, not a promise the invoice will match. They are
**not** the $14.17 remaining balance.

| Wave | What | Concurrency | Fold-only (pred.) | $ cap (incl. setup @ $2.19/hr) | Hours cap | Kill switch (any one fires → stop the wave, Terminate after PAE retrieve) |
|---|---|---|---|---|---|---|
| **0** | Cold-start **re-test of the runbook** on a **clean** card. **No emit.** Empty-queue `claim→204` is success. **Start the Step 5 `nvidia-smi` logger anyway** so the first later fold is captured | 1 | $0 | **$7** | **3 h** | Any pip/ABI/import scar that is not cured by following the runbook as written. Do not hot-fix and then emit |
| **A** | Remaining L ≤ 800 (17 last-tiles) | 1 | $0.13 | **$9** | **4 h** | Any tile wall **> 180 s** (3 min), or first tile **> 3×** `t(L)` |
| **B** | 801–1200 (16) | 1 | $1.03 | **$11** | **5 h** | Any tile wall **> 10 min**, or mean of first 3 **> 1.5×** `t(L)` |
| **C1** | 1201–1655 (11) | 1 | $2.02 | **$14** | **6 h** | Any tile wall **> 15 min**, or first tile **> 1.5×** `t(L)` |
| **C2** | L = 1656 (60) | 1 | $17.97 | **$33** | **15 h** | After **3** full-window tiles: mean wall **> 1.5 × 492 s (12.3 min)**; **or** any single tile **> 20 min**; **or** OOM on a card that already folded L=1608 |

**Do not start Wave A until Wave 0 exits clean** (process rule in the runbook).
**Do not start C2 until A/B/C1 have updated the model** — three more (L, t) points make n>2
— **and** until the account covers C2 fold-only plus Wave 0, which **$14.17 does not**.

Suggested emit order inside a wave: **shortest remaining tile in that band first**, so a
kill switch fires cheap.

---

## 6. Named unknowns

| Unknown | Why it moves the bill | What would close it |
|---|---|---|
| **Peak VRAM** | **NAMED UNKNOWN.** Not in provenance. Do not invent a GiB. L=1608 fitted is not a peak. | Next cold run: runbook Step 5 `nvidia-smi` logger **before** the first fold; CSV off the box with PAE |
| **Setup-scar wall-clock split** | This pilot's invoice is fold-only $0.31 **plus** scars; the split was not logged | Wave 0 on a clean card following the runbook as written — that wall **is** cold-start, and is named as such |
| **Cold-start overhead (next pod)** | Weight download + first `fold()` load can dwarf a Wave A tile | Wall from `python -m worker.main` start to first `complete → 204` on a clean card |
| **Domain-snap length mix** | Last-tile L shifts ±64 aa; n_tiles does not | Compare `emit_tile_jobs` lengths to the unsnapped table before folding a wave |
| **PAE retrieve time** | tile0 gzip was **18.9 MB**; 60 full windows will be larger in aggregate; D-036 POST is on the clock | Time `python -m scripts.retrieve_rental_pae` on the next pod |
| **Stitch I/O** | Parent PAE is L² JSON with nulls; IGF2R L=2264 is already large; Q8WXG9 span=5879 is worse | Time `write_stitched` per parent on the laptop (not on the paid GPU) |

True **$/hr is pinned at $2.19** for this card class on this pilot. A later invoice that
disagrees is a new measurement, not a license to keep $2.00 in the tables.

---

## 7. What this document is not

- Not a GO to emit the 44.
- Not a VRAM number. Peak VRAM is a **named unknown** — do not invent one.
- Not a claim that stitched multi-tile structures are commensurable with single-pass folds
  (D-109 ruling 7 / `F-015` reserved).
- Not an invoice. **$14.17 remaining** is a balance reading after Terminate.
- Not a projection of setup scars onto the other 44.

Provenance for the 106 / 104 counts: the Python reduction in D-113 (census v7, empty
`domain_ends`, geometry from `core.contracts`). Provenance for the two walls and artifact
sizes: the IGF2R pilot claim→complete records named in §1, not re-queried from Fly in the
docs PR. Provenance for **$2.19/hr** and **$14.17 remaining**: Matt/Trinity pin, this
session, after Terminate.
