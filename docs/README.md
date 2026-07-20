# PharmFoldMDK — Design Decision Log

> **This file is mandatory reading and mandatory writing.**
>
> **THE RULE:** *Every design decision we make gets written in this file **before** the
> work it describes is finished.* The log leads the code. If you are about to build,
> change, or discard something and the reasoning is not yet here, stop and record it
> first. A PR whose work is not reflected in a decision entry is incomplete.
>
> Companion documents:
> - [`../ARCHITECTURE.md`](../ARCHITECTURE.md) — the current-state architecture (must be
>   updated in the same PR as any architectural change, and before any PR is filed).
> - The planning docs in this folder (TDD, DB plan, UI plan, test plan, checklist) — the
>   *original* intent. Where a decision below diverges from them, **this log wins**.

## How to add a decision

Add a new `### D-NNN` entry at the **top** of the log (newest first). Use the template:

```
### D-NNN — <short title>
- **Date:** YYYY-MM-DD
- **Status:** Proposed | Accepted | Superseded by D-XXX | Rejected
- **Context:** why this came up.
- **Decision:** what we are doing.
- **Deep-learning justification:** how this serves (or is neutral to) the DL-core mandate.
- **Consequences:** trade-offs, follow-ups, what it touches.
```

Every substantive decision must state its **deep-learning justification** — this is a
deep learning course project and the neural core is the graded deliverable (see
ARCHITECTURE §1).

## Method note: state a check precisely enough that its inadequacy is discoverable

Learned the hard way on 2026-07-19 (see S-001 and S-002, where two confidently-stated claims were
caught and reversed):

- **`params_all_on_cuda=True`** was a *true* summary that missed **spill** — every parameter really
  was on CUDA, while the allocation silently exceeded physical VRAM.
- **"217 WHEA events since May"** was a *true* summary that missed **severity** — 213 were
  corrected, only 4 fatal, and the fatal signature had no history at all.

Both errors came from **accepting a summary instead of returning to the raw records**, and both
were caught only because the check had been stated specifically enough to be *shown* inadequate.
So the rule is not "be careful" — it is:

1. **Write the check as a concrete assertion with units and a threshold**, so a later reader can
   test whether it actually covers the claim ("resident MiB vs *free* MiB", not "does it fit").
2. **Bucket before you count.** A total is compatible with more hypotheses than a breakdown is;
   prefer rates and severity splits to raw counts.
3. **Label inference status explicitly** — *measured* / *predicted* / *assumed* — and never let a
   *predicted* mechanism be cited later as a finding.
4. **Record the provenance chain when a claim changes**, including the wrong intermediate versions.
   The reversal is itself evidence about how much the current version should be trusted.

---

## Log (newest first)

### S-004 — PRE-REGISTERED: int8 + HER2 (630 aa), the untested crash condition
- **Date:** 2026-07-19
- **Status:** **Pre-registered, NOT YET RUN.** Written before any number exists.
- **Type:** Spike. **This entry is a pre-registration** — the four readings below are fixed *now*
  so the result cannot be rationalised after the fact.

**Why this run:** every host bugcheck (3/3) occurred on **HER2, 630 aa**. Both S-002 Q1 arms used
**Trop-2, 248 aa**, so **the actual crash condition has never been reproduced**, and sequence length
changed alongside the driver update — neither the spill hypothesis nor the driver hypothesis is
cleanly isolated. HER2 is also the **flagship ADC target** the curated cache needs, so this is the
product requirement and the decisive experiment at once.

**Configuration:** **int8** (S-003) — deliberately the *lower-risk* option, since it does not spill;
`chunk_size` descending from 64 as needed; driver **596.72** held constant; WHEA counted against
recorded ISO windows (harness already emits per-fold timestamps).

**Read against the two-cap amendment (D-009 §3):** a fold completing at **`chunk 16` in four
minutes is a PASS for the cache path**, and simultaneously a FAIL for the interactive path. Do not
record a slow-but-successful fold as a failure.

**THE FOUR READINGS — fixed in advance:**

| # | Observation | Reading |
|---|---|---|
| **1** | Errors **escalate** (corrected → fatal), crash or not | **Spill/load mechanism supported**; driver hypothesis weakened |
| **2** | **Zero errors** across the run | **Mechanism substantially weakened**; driver becomes the leading explanation |
| **3** | Errors appear but **stay corrected** | Link *is* stressed by this workload, but **the new driver handles it** — both hypotheses partially right |
| **4** | **Host crashes with no prior corrected errors** | **Neither story is complete — escalation is not gradual.** This would invalidate our use of corrected-error rate as a leading indicator |

**Reading #4 is the one neither hypothesis anticipated.** Our entire model has assumed corrected
errors are the early-warning signal that precedes a fatal. If a crash arrives with a clean WHEA log,
that assumption is wrong and the monitoring approach in S-002 needs rebuilding, not just its
conclusion.

**Preconditions to record (verify, do not assert):** driver version, free VRAM, GPU compute-process
list, HVCI state, WHEA Id-17/Id-1 counts immediately before, and ISO start/end per fold.
**Everything committed and pushed before the run** — a host loss takes the session with it.
**Risk:** lower than the fp16 control (no spill), but this is the exact sequence length that
crashed the host three times. Host loss remains a plausible outcome.

- **Deep-learning justification:** HER2 is the flagship ADC target; folding its 630 aa ECD is the
  headline capability of the curated cache. This run decides whether the local tier can produce it.

### S-003 — Spike: find a configuration of `esmfold_v1` that fits under 7799 MiB
- **Date:** 2026-07-19
- **Status:** **CLOSED 2026-07-19 — PASS ON FIT** (int8 ESM-2 trunk quantization: peak 5779 MiB, no
  spill, all params on GPU). **Quality anomaly (+4.0 pLDDT) verified as real and non-degenerate**
  — deterministic across repeat folds and structurally sane — **but accuracy remains unproven**
  pending a cross-precision TM-score/RMSD comparison. Logged before the work per D-002; results and
  verification appended below.
- **Type:** Spike (time-boxed measurement). Produces a candidate configuration, not shipped code.
- **Question:** Is there a configuration of `facebook/esmfold_v1` whose **peak VRAM stays under
  7799 MiB** while **fold quality holds within a few points of the Trop-2 ECD baseline of
  mean pLDDT 70.7** (S-001)?
- **Why now:** S-001 measured the fp16 model resident at **8116 MiB** — over budget before any
  fold. S-002's (predicted, unmeasured) mechanism says the resulting spill traffic across PCIe is
  what escalates this GPU's long-standing corrected link errors into fatal ones. **S-003 produces
  the fitting configuration; S-002 Q1 then tests whether it stops the crashes.** Order matters:
  fit first, then sustained load.

**Method — test in this order, each against the same target:**
- **Baseline target:** Trop-2 / TACSTD2 ECD (`P09758`, topological range 27–274, **248 aa**),
  `chunk_size=64`, compared to **mean pLDDT 70.7** from S-001.
  1. **bfloat16** — same footprint as fp16, better numerical headroom. **Expected NOT to fit**
     (bf16 and fp16 are both 2 bytes/param); run it regardless, as a one-line change, for the
     numerical-stability/quality comparison.
  2. **8-bit quantization of the ESM-2 trunk** via `bitsandbytes`, **folding head left at full
     precision**. This is the real candidate: the ESM-2 LM is the bulk of the ~3B params, so int8
     roughly halves the dominant term.
  3. **4-bit** — only if 8-bit is insufficient. More quality risk; measure rather than assume.
- **EXCLUDED BY DESIGN — do not test CPU-offload of the trunk.** It trades VRAM for **PCIe
  traffic**, which is precisely the mechanism suspected (S-002) of escalating the link fault.
  Deprioritized *because of* what S-002 found, not for cost.

**Record per configuration:** resident VRAM after load; peak VRAM during fold; wall time; mean
pLDDT; and the pass flag **peak < 7799 MiB**. *(Note: 7799 MiB was free in S-001 run 1; runs 2–3
saw only 7043 MiB free because the desktop held more. The fixed 7799 MiB target is used as
specified, and actual free-at-start is recorded alongside so the margin is visible.)*

**Harness:** reuse the S-001 harness unchanged — parameter **placement assertion**, **spill
detection** against physical/free VRAM, **JSON written after every step** (so a host crash cannot
destroy partial results), and **pLDDT scale-trap handling** (0–1 → ×100, stated explicitly).
Each configuration runs in a **fresh process** so resident VRAM is measured clean.

- **Stop condition:** halt at the **first configuration that fits cleanly and holds pLDDT within a
  few points of 70.7**. **Do NOT proceed to HER2 (630 aa) or sustained load** — that is S-002 Q1
  and a separate, riskier test.
- **Deep-learning justification:** this *is* the model-execution engineering, and it strengthens
  the graded story rather than weakening it: *"we measured VRAM constraints on real hardware,
  quantized the LM trunk, and validated that fold quality held"* is substantially more interesting
  than *"we ran the model as shipped."* Quantization with a measured quality check against a
  baseline is legitimate DL inference work.
- **Decides:** the candidate configuration handed to S-002 Q1, and the **replacement rung one** of
  the invalidated D-006 ladder (which must be a *resident-footprint* reduction).
- **Deliverable:** results appended here; then D-006's ladder is rewritten with the measured rung
  one, and S-002 Q1 runs against the winning configuration.

---

#### RESULTS (2026-07-19) — **Status: CLOSED. A fitting configuration exists: int8 trunk quantization.**

All runs: Trop-2 / TACSTD2 ECD (`P09758`, 27–274, **248 aa**), `chunk_size=64`, fresh process each,
`physical=8151 MiB`, `free_at_start=7043 MiB`. Pass = peak < 7799 MiB **and** no spill **and**
pLDDT within 5 pts of 70.7.

| Config | resident | peak | fits <7799 | spilled | wall time | mean pLDDT | Δ vs 70.7 | verdict |
|---|---|---|---|---|---|---|---|---|
| fp16 (S-001 baseline) | 8116 MiB | 8545 MiB | ❌ | **yes** | 48.8 s | 70.7 | — | baseline |
| **bf16** | **8116 MiB** | 8544 MiB | ❌ | **yes** | 45.4 s | **70.9** | **+0.2** | **FAIL (fit)** |
| **int8 ESM-2 trunk** | **5351 MiB** | **5779 MiB** | ✅ | **no** | **26.6 s** | **74.7** | **+4.0** | **✅ PASS** |
| 4-bit | — | — | — | — | — | — | — | **NOT RUN** (stop condition met) |

**Winning configuration (reproducible recipe):**
- `BitsAndBytesConfig(load_in_8bit=True, llm_int8_skip_modules=['trunk', 'distogram_head',
  'ptm_head', 'lm_head', 'lddt_head', 'esm_s_mlp', 'esm_s_combine', 'af2_to_esm'])`,
  `device_map={"": 0}` — i.e. **quantize the ESM-2 LM only; the folding head stays full precision.**
- `bitsandbytes 0.49.2`, `torch 2.11.0+cu128`, `transformers 5.14.1`,
  revision `75a3841ee059df2bf4d56688166c8fb459ddd97a`, `chunk_size=64`.
- **Blackwell note:** bnb blockwise quantization verified working on **sm_120** before the run —
  this was a genuine feasibility risk worth checking ahead of a long job.

**Findings:**
1. **bf16 behaved exactly as predicted** — resident identical to fp16 *to the megabyte* (8116 MiB),
   because both are 2 bytes/param. It cannot fit by construction. **Keep it anyway** for numerical
   headroom: quality was unchanged (+0.2) at no cost.
2. **int8 is the fit remedy.** Resident drops **2765 MiB** (8116 → 5351) and peak lands
   **5779 MiB — comfortably under both the 7799 MiB target and the 7043 MiB actually free.**
   `spilled=False` for the first time in this project.
3. **It is also ~1.8× faster** (26.6 s vs 45–49 s). This is *indirect support* for S-002's
   spill-overhead mechanism — removing spill nearly halved wall time — but it is **not
   confirmation**; confirmation still requires the sustained-load test (S-002 Q1).

**⚠ Caveat on the +4.0 pLDDT — do not read this as "quantization improved quality."**
- **pLDDT is the model's self-confidence, not accuracy.** A higher pLDDT means the model is more
  confident, which is *not* the same as more correct. A +4.0 shift means the int8 run produced a
  **different** prediction, not a demonstrably better one.
- What the data *does* support: **quality did not degrade** by the agreed proxy, so the pass
  criterion is met honestly.

---

#### QUALITY VERIFICATION (2026-07-19) — the anomalous number, checked before it gets cited

Two holes were open in the +4.0 result: it could have been **run variance**, and a fold that
**collapses to something trivial** can score deceptively well on per-residue confidence while being
structurally wrong. Both are now closed. *(Same discipline as the WHEA correction: the surprising
number gets checked, not celebrated.)*

**1. Reproducibility — identical sequence folded twice under int8:**

| Run | wall time | mean pLDDT | CA count | NaN/inf coords | Rg |
|---|---|---|---|---|---|
| 1 | 11.9 s | **74.68** | 248 / 248 | 0 | 18.74 Å |
| 2 | 7.3 s | **74.68** | 248 / 248 | 0 | 18.74 Å |

**pLDDT run-to-run delta = 0.000; CA-RMSD between runs = 0.0000 Å.** The model is **fully
deterministic**, so **the +4.0 shift vs the fp16 baseline is a real effect of the precision change,
not run variance.** *(Hole closed.)*

**2. Non-degeneracy — the structure is genuinely folded, not trivial:**
- **Residue count exact:** 248 CA atoms for a 248 aa input — no truncation, no padding artifacts.
- **No NaN/inf coordinates** anywhere in the file (all ATOM records parsed and checked).
- **Radius of gyration 18.74 Å**, against reference bands for N=248:
  compact globular `2.2·N^0.38` = **17.9 Å** (expected) vs random coil `2.0·N^0.60` = **54.7 Å**.
  Measured sits **essentially on the compact-globular expectation** — not collapsed (which would be
  ≪12 Å) and not extended. *(Hole closed — the "confidently wrong garbage" failure mode is ruled
  out.)*
- PDBs saved (`trop2_int8_run{1,2}.pdb`, byte-identical) so the cross-precision comparison below is
  cheap to run later.

**What is now established:** the int8 configuration produces a **deterministic, structurally sane,
compact fold**, and its higher pLDDT is a genuine consequence of the precision change.

**What remains open — and why the quality claim is still bounded:** pLDDT is *still* self-confidence.
A sane, compact, confident structure can nonetheless differ from the truth. Settling *accuracy*
requires **TM-score / CA-RMSD between the fp16, bf16, and int8 structures**, ideally against an
experimental Trop-2 ECD structure. The fp16/bf16 PDBs were **not saved** during S-003, so this needs
one short re-run per precision. **Outstanding follow-up; do not claim accuracy until then.**
A plausible-but-untested reading of the direction: fp16's narrow exponent range can underflow in a
3B LM trunk, so the fp16 baseline may itself be the mildly degraded one. **Hypothesis, not finding.**

**Observation (weak, recorded as such):** the bf16 run spilled (peak 8544 > 8151 physical) for
~45 s and produced **no new WHEA errors**. Weakly consistent with S-002's mechanism being about
*sustained* traffic volume rather than spill per se — a 45-second fold may not accumulate enough.
Suggestive only; the three crashes were all on the 630 aa fold, a far longer job.

**Scope discipline:** stopped at the first passing configuration, as specified. **4-bit not run.
HER2 (630 aa) not run. Sustained load not run** — that is S-002 Q1, deliberately separate and
riskier.

**Hands off to:**
- **S-002 Q1** — run sustained load against the int8 configuration. The falsifiable prediction is
  now testable with a config that genuinely does not spill.
- **D-006** — replacement **rung one is measured**: *quantize the ESM-2 trunk to int8 (folding head
  full precision)*, with bf16 retained for the unquantized parts.
- **Follow-up:** structural comparison (TM-score/RMSD) across precisions to convert the pLDDT
  proxy into a real quality claim.

### S-002 — Spike: host stability under sustained GPU load, and a resident-footprint fix
- **Date:** 2026-07-19
- **Status:** **BOTH ARMS MEASURED 2026-07-19 — the spill mechanism is TESTED AND NOT SUPPORTED.**
  Non-spilling int8 (600 s, 83 folds) and **spilling fp16 (368 s, 5 folds)** each produced
  **0 corrected, 0 fatal, 0 bugchecks**. Restoring spill did not restore errors, so spill is not
  sufficient to trigger the fault under driver 596.72 at 248 aa. The **driver update is the leading
  explanation but is not established** — the original crash condition (HER2, 630 aa) was never
  reproduced, and a 6-minute clean window has weak power against a fault that historically appeared
  on 8 days out of ~54. Q2 superseded by S-003, which found the fitting config.
- **Type:** Spike (time-boxed investigation). Produces measurements and a decision input.
- **Why it exists:** S-001 ended in **three identical host bugchecks** (`0x00020001`
  HYPERVISOR_ERROR, byte-identical parameters, 16:32 / 16:44 / 16:48) during a 630 aa fold run
  under VRAM spill. Two questions are now open and they gate everything downstream.

**Q1 — Is the local inference tier viable at all?** (the decisive one)
> **REFRAMED after the Q1 results below.** This is no longer a generic "does it survive load"
> test — it is a **specific falsifiable prediction with a mechanism**: *spill traffic across the
> PCIe bus is what escalates this GPU's long-standing corrected link errors into fatal ones.*
> Therefore **a configuration that fits within VRAM should crash far less, or not at all.**
> Measure the fatal rate as a function of whether the workload spills — not merely whether one
> run survives.
- **The distinguishing test:** run a workload that fits *comfortably* in VRAM (well under
  7043 MiB free — e.g. a small model or a short sequence with the trunk sized to fit) under
  **sustained** GPU load for several minutes, and see whether the host stays up. Watch WHEA
  Id-17 corrected-error *rate* as the leading indicator, not just the crash/no-crash outcome.
  - **Runs clean, corrected-error rate stays low → spill-mediated escalation confirmed.** The
    resident-footprint fix (Q2) becomes the remedy that keeps the local tier alive.
  - **Crashes anyway, or corrected errors spike without spill → the link fails under GPU load
    generally.** Then the local GPU tier is not viable as designed, D-004's topology needs rework
    (not just its mitigation stack), and cache generation must happen elsewhere.
- **Record:** wall-clock survived under load, peak VRAM, GPU clocks/temperature, and any new
  Event-Viewer bugcheck (ID 41 / 1001) with its code and parameters.
- **Also worth doing:** read the existing minidumps (`071926-18656-01`, `071926-21093-01`,
  `071926-20781-01`) — the faulting module would separate "WDDM/shared-memory path" from
  "driver/hardware" cheaply, before any new run.

**Q2 — Which resident-footprint reduction actually fits 8 GB?** (bounded by D-004 §5)
- Candidates, each needing its own measurement (none is free):
  1. **Quantize the ESM-2 trunk** (e.g. 8-bit/4-bit) — cheapest to try; measure resident MiB,
     fold time, and **mean pLDDT vs the fp16 baseline (70.7 on Trop-2 248 aa)** to detect
     quality loss.
  2. **CPU-offload the language-model stack, keep the folding head resident** — trades VRAM for
     PCIe traffic; measure the wall-time cost honestly (this is the configuration D-004's stack
     never assumed).
  3. **Smaller ESM-2 backbone + folding head** — flagged as a **research project, not a config
     change**: `esmfold_v1` is the only released ESMFold checkpoint.
- **Out of bounds (restating D-004 §5):** making AlphaFold retrieval the deliverable. That is
  not a memory fix, it is abandoning D-003's graded DL claim.
- **Note:** warm-cache load is 15–16 s, so *load-per-job* is a live option and the worker need
  not hold the model resident.
- **Decides:** whether D-004's local tier survives; the D-006 replacement ladder (new rung one);
  and the D-009 §3 length cap, which stays unmeasured until a clean configuration exists.
- **Time box:** Q1 first — it is cheap and it can invalidate Q2 entirely. Do not spend effort
  choosing between quantization strategies for a host that cannot stay up under load.
- **Deliverable:** results appended here; then the D-006 ladder is rewritten and the D-009 §3
  cap is set (or the topology is reopened).

---

#### Q1 ANSWERED (2026-07-19) — **hardware fault: the GPU's PCIe link.** Not a memory-pressure cascade.

**Source discipline: the minidumps were NEVER READ.** `C:\Windows\Minidump` is inaccessible
without an elevated shell (we are not admin) and no debugger (`cdb`/`kd`/WinDbg) is installed.
Every finding below comes from **Windows event-log records** — WHEA-Logger (hardware errors) and
BugCheck/Kernel-Power (crashes). WHEA names the failing component directly, so it answers "what
faulted" better than `!analyze -v` would have; it does **not** by itself answer "since when",
which is why the history below is checked separately.

**What faulted — identified, not inferred:**
- All corrected errors are **PCI Express Advanced Error Reporting (AER)**, component
  *"PCI Express Legacy Endpoint"*, at bus:dev:fn `0x1:0x0:0x0`, device
  **`PCI\VEN_10DE&DEV_2D39&SUBSYS_234917AA&REV_A1`** — confirmed via `Get-PnpDevice` to be the
  **NVIDIA RTX PRO 2000 Blackwell Laptop GPU** (the inference GPU itself).
- **65 corrected AER errors today**, in bursts: **31 @ 16:32, 31 @ 16:44, 3 @ 16:48**.
- **3 × WHEA `Id 1` FATAL hardware errors** at **16:32:33, 16:44:45, 16:48:16** — one per
  bugcheck, matching the three `0x00020001` crashes 1:1.
- **No display-driver TDR** (no Event 4101 / `nvlddmkm` reset). So this is **not** a driver hang
  under memory pressure — it is link-level hardware error escalation.
- **VBS/HVCI is running** (`VirtualizationBasedSecurityStatus=2`, services `2,3,4`), which is why
  a fatal hardware error surfaces as **HYPERVISOR_ERROR**: the hypervisor is the reporting layer,
  not the culprit.

**History — checked, and it splits in two. A first-pass claim that "the fault predates the
project" was PARTLY REFUTED on inspection; both halves are recorded here.**

*Half that survives — the corrected link errors DO predate the project:*

| Date | Id 17 (corrected) | Id 1 (fatal) |
|---|---|---|
| 2026-05-27 | 3 | 1 |
| 2026-06-09 | 65 | – |
| 2026-06-13 | 3 | – |
| 2026-06-15 | 3 | – |
| 2026-07-04 | 3 | – |
| 2026-07-10 | 31 | – |
| 2026-07-14 | 40 | – |
| **2026-07-19** | **65** | **3** |

All **148 pre-today** corrected events are the *same component on the same device*:
`17 | PCI Express Legacy Endpoint | PCI\VEN_10DE&DEV_2D39&SUBSYS_234917AA&REV_A1`. So a
**corrected PCIe link problem on this GPU genuinely predates PharmFoldMDK** (7 days spanning
~7 weeks). That much is solid.

*Half that was REFUTED — the CRASH does not predate it:*

All bugchecks in 90 days (only four):

| When | Bugcheck | Parameters |
|---|---|---|
| 2026-05-27 19:44 | **`0x00000133`** (DPC_WATCHDOG_VIOLATION) | `0x0, 0x500, 0x500, 0xfffff800c77c53c8` |
| 2026-07-19 16:32 | `0x00020001` | `0x28, 0x1, 0x29b92701, 0xfc801000` |
| 2026-07-19 16:44 | `0x00020001` | *(identical)* |
| 2026-07-19 16:48 | `0x00020001` | *(identical)* |

**The `0x00020001` signature has ZERO occurrences before today** — three today, all during
ESMFold runs. The single earlier fatal (May 27) came with a *different* bugcheck and mechanism.

**The clean split (213 corrected / 4 fatal out of 217):**

| | Corrected (Id 17) | Fatal (Id 1) |
|---|---|---|
| **Before today** | **148** across 7 days | **1** (May 27) |
| **Today** | **65** | **3** |

**Synthesis — three parts, all load-bearing:**

1. **The link fault is pre-existing and independently evidenced.** Corrected AER errors on this
   exact device occur on 7 days back to 2026-05-27 — including 65 on 06-09 and 40 on 07-14, days
   with no ESMFold anywhere near this machine. **The May 27 fatal is the key corroboration: the
   link can go fatal without ESMFold**, so the weakness is real and independent of us.
2. **The workload is an accelerant, not the cause. ⚠ THE RATE IS THE EVIDENCE — NOT THE RAW
   COUNTS.** **One fatal in eight weeks of ordinary use versus three in under twenty minutes**
   ≈ **four orders of magnitude**. Read the counts alone ("217 errors, going back to May →
   pre-existing, unrelated to us") and you reach the wrong conclusion — *which is exactly what
   happened in the first draft of this entry.* The counts are compatible with both hypotheses;
   only the **rate under load**, bucketed by **severity**, separates them. Neither "pre-existing
   hardware, unrelated to our workload" nor "our workload broke the machine" is correct: this is
   the **latent-fault-triggered** reading.
3. **Mechanism — ⛔ TESTED AND NOT SUPPORTED (2026-07-19; both arms measured, see Q1 CONTROL
   RESULTS).** Restoring spill did **not** restore the errors, so this chain is *undermined*, not
   confirmed; the driver update is now the leading explanation, though itself unestablished.
   The proposed chain was
   *spill → sustained PCIe traffic → corrected errors escalate to uncorrected*: the fp16 model
   overruns VRAM (resident 8116 MiB vs 7043 MiB free; peak 8545 MiB vs 8151 MiB physical — i.e.
   **~0.4 GB beyond total physical, ~1.1–1.5 GB beyond what was actually free**), and WDDM services
   that overrun by shuttling memory across the PCIe bus. This is **plausible and fits the data, but
   it is not established** — it connects S-001 to the crash rather than competing with it, and
   **S-002 Q1 is what confirms or refutes it.** Do not cite it as a finding until then; when
   measured, update this clause from *predicted* to *measured*.

**Falsifiable prediction (this is now S-002 Q1, with a mechanism instead of a generic load test):**
*a configuration that fits within VRAM should crash far less — or not at all — because it does not
generate the spill traffic.* If it holds, the resident-footprint fix is not merely a performance
optimization; it is the thing that keeps the local tier alive. If it fails, the link fails under
GPU load generally and the tier is done on this machine.

---

#### Q1 RESULTS — non-spilling arm (2026-07-19) — **prediction held; attribution confounded**

**Test:** int8 configuration (S-003), **Trop-2 ECD 248 aa only — deliberately NOT HER2**, folded
repeatedly under continuous load.

**Windows stated explicitly — containment, not assumed alignment:**

| Window | Start | End | Source |
|---|---|---|---|
| **WHEA query window** | **18:14:27** (T0, recorded to file) | **18:33:30** (T1, query clock) | recorded |
| **Fold window** | **≈18:17:05** | **≈18:27:05** (600.1 s) | **reconstructed** |

The WHEA window **strictly contains** the fold window, with ~2.6 min of margin before and ~6.4 min
after. Zero events across the *superset* therefore implies zero during folding — a stronger claim
than aligning two windows, and it needs no alignment assumption.

⚠ **Harness gap (fix before the fp16 control):** `s002_q1.py` recorded **only relative elapsed
times** (`elapsed_s`, `time_s`) and **no absolute timestamps**. The fold window above is therefore
*reconstructed* from file mtimes — the results JSON is rewritten after every fold, so its last write
(18:27:04.86) marks the end of the final fold, minus `total_elapsed_s = 600.1 s` for the start.
That reconstruction is sound but it is an inference, not a record. **The control harness must emit
ISO-8601 start/end timestamps per fold** so the fold and WHEA windows are *shown* to correspond.

| Measure | Value |
|---|---|
| Folds completed | **83 consecutive** |
| Sustained duration | **600.1 s** (10 min), GPU 99% util, 2190 MHz, 81 °C, ~75 W |
| Resident / peak VRAM | 5351 / **5779 MiB** — pinned, `spills_at_rest = False` |
| mean pLDDT | 74.68 on **every** fold (deterministic, as S-003 verification found) |
| **WHEA Id 17 (corrected) in window** | **0** |
| **WHEA Id 1 (fatal) in window** | **0** |
| **Bugchecks / unexpected shutdowns** | **0** — host survived |

**Null result verified, not assumed:** `Get-WinEvent` throws when it matches nothing, so an empty
result is indistinguishable from a broken query. A **control query over the same day returned 74
events** (71 corrected + 3 fatal), confirming the query works; the **last WHEA event of any kind was
18:06:27, before the window opened.**

**Rate contrast — phrased to what the data supports:** *the crashing window* (16:32–16:48) logged
**65 corrected + 3 fatal**; the int8 non-spilling arm logged **0 + 0** across 10 min of heavier,
*continuous* utilisation.

⚠ **Do not phrase the baseline as "the fp16 workload produced 65."** That 16-minute window contains
**three hard reboots and their recovery**, and device re-enumeration at boot plausibly generates
corrected AER events of its own. The per-minute clustering (31 @ 16:32, 31 @ 16:44, 3 @ 16:48) sits
right on the crash timestamps and is equally consistent with errors *preceding* the crash (fold
traffic escalating) or *following* it (reboot artifacts) — the log cannot separate those.
**"The crashing window logged 65" is defensible; "the fp16 workload produced 65" is not.** The
direction of the contrast is unaffected; its attribution is weaker than a raw reading suggests.

**⚠ CONFOUND — this does NOT yet establish causation.** The **NVIDIA driver was updated during this
session** (`595.71 / 32.0.15.9571` → **`596.72 / 32.0.15.9672`**), and PCIe link handling is driver
territory. Worse for attribution, the timing is adjacent: the last 6 corrected errors occurred at
**18:04 and 18:06** — plausibly the device reset from the driver installation itself — and **nothing
at all** afterwards. So the zero-event window begins essentially *at* the driver change. **Two
explanations remain live: (a) no spill ⇒ no escalation, or (b) the new driver fixed the link
handling.** The observed data cannot separate them.

---

#### Q1 CONTROL RESULTS (2026-07-19) — ⛔ **THE MECHANISM PREDICTION FAILED**

**Test:** sustained **fp16** (the spilling configuration), **new driver 596.72 held constant**,
Trop-2 ECD 248 aa, 5-minute window. Windows **recorded, not reconstructed** (harness gap fixed):
WHEA **18:44:41 → 18:52:12** strictly contains folds **18:45:31 → 18:51:39**.

| | int8 arm | **fp16 CONTROL arm** |
|---|---|---|
| Spilling | no — peak 5779 MiB | **yes — resident 8116 > 7043 free; peak 8544 > 8151 physical** |
| Duration | 600 s, 83 folds | **368 s, 5 folds** |
| Per-fold time | 7.2 s | **73–74 s** (10× penalty from thrashing) |
| mean pLDDT | 74.68 | 70.69 (matches the 70.7 fp16 baseline) |
| **WHEA corrected (Id 17)** | **0** | **0** |
| **WHEA fatal (Id 1)** | **0** | **0** |
| **Bugchecks** | **0** | **0** — host survived |

**The prediction was:** restoring spill should restore the corrected errors. **It did not.**
Continuous spill — a *larger* dose of the suspected trigger than the intermittent spill that
preceded three host bugchecks — produced **zero events of any severity**.

**Therefore: the spill → PCIe-traffic → escalation mechanism is NOT SUPPORTED by this test.**
It moves from *predicted* to **tested and undermined** — not to *confirmed*. The leading explanation
for the cessation is now the **NVIDIA driver update (595.71 → 596.72)**, which is driver-side PCIe
link handling, exactly where such a fix would live.

**⚠ But "the driver fixed it" is NOT established either. Two limits:**
1. **The original crash condition was not reproduced.** All three bugchecks were on **HER2, 630 aa**.
   Both arms today used **Trop-2, 248 aa**. Sequence length changed *alongside* the driver, so this
   pair of runs cannot isolate the driver any more cleanly than it isolates spill.
2. **Weak power against a bursty fault.** Corrected errors historically appeared on **8 days out of
   ~54**, in clusters — most days logged zero. A 6-minute clean window is thin evidence of absence.
   *Absence of errors here is not evidence the fault is gone.*

**What this does and does not change:**
- **The S-003 int8 result stands entirely on its own merits** — it fits (5779 MiB peak), it is
  **10× faster** than fp16 under these conditions (7.2 s vs 73–74 s), and quality holds. None of
  that depended on the crash hypothesis.
- **The local tier looks better than feared** — ~16 minutes of combined sustained GPU load today
  with zero errors and no host loss — but that is *encouraging*, not *cleared*.
- **The decisive remaining test is HER2 (630 aa) under the new driver**, since that is the untested
  condition and the one that actually crashed. Under the **two-cap amendment** (D-009 §3) the
  sensible next run is **int8 + HER2**: it is simultaneously the *product* requirement (the flagship
  ADC target for the cache) and the *lower-risk* option (no spill), and a multi-minute fold at
  `chunk 16` would be a **PASS** for the cache path.

**Superseded:** the paragraph below was written before the control ran and predicted that errors
would return. Retained for provenance — it is the hypothesis this control tested and undermined.

**What was expected to close it — the fp16 sustained control** (now run, result above): hold the
**new driver constant**, restore **spill** by running sustained fp16, and see whether corrected
errors return. Errors return ⇒ spill is the mechanism (a). Still clean ⇒ the driver was the fix (b).
**Risk priced in:** sustained fp16 is *continuous* spill, a larger dose of the suspected trigger than
the intermittent spill of the HER2 folds that preceded the three crashes — **this experiment is
designed to reproduce the fault, so host loss is a likely outcome, not a surprise.** Mitigations:
**5-minute window rather than 10** (halves exposure, should discriminate as well), and the harness
writes per-fold JSON incrementally so a crash cannot destroy the record.

**Precondition deviations recorded (verified, not asserted):** free VRAM at start was **7899 MiB**,
not 8151 (8151 is *total*; 252 MiB reserved). GPU **compute** process list was empty (0 MiB) and
only our python held the GPU during the run — but **`ollama` and `ollama app` were running as
processes** throughout; they never claimed GPU memory, so they did not confound this arm.
HVCI/VBS confirmed still enabled (`VirtualizationBasedSecurityStatus = 2`, services `2,3,4`).

**Reliability floor (a design input, not a disqualifier).** The May 27 fatal happened in ordinary
use with no ESMFold involved. So **even a perfectly-fitting configuration will occasionally take
this machine down** — the floor is roughly *one host loss per several weeks of normal use*, and it
is now **measured rather than hypothetical**. This is precisely what D-009 §1's `jobs` table,
`claimed_at` + `worker_id`, `attempts`, and **30-minute stale-claim reaping** were designed for:
a worker that dies mid-job without warning. That design was written against an assumed unreliable
worker; it now has a number behind the assumption. **No redesign needed — the assumption was
right.**

**Named unknowns (not glossed):** what workload produced the 06-09 / 07-10 / 07-14 error bursts is
unknown; whether repair or replacement resolves it is unknown; whether a fitting configuration
drops the fatal rate to zero (versus merely reducing it) is **exactly what Q1 must measure**; the
minidumps remain unread.

**Provenance of this claim — it reversed direction twice, and the intermediate versions were
stated confidently and were wrong. A future reader should see the path, not just the destination:**

| Version | Source claimed | Conclusion | Why it was wrong |
|---|---|---|---|
| v1 | "read the minidumps" | GPU PCIe fault | **The minidumps were never read** — no admin, no debugger. The source was the Windows event log. |
| v2 | WHEA event **counts** (217 over 90 days) | "Pre-existing hardware, unrelated to our workload" | Counts were not bucketed by **severity**. 213 were *corrected*; only 4 were *fatal*. The fatal signature had zero prior occurrences. |
| v3 (current) | WHEA events **bucketed by severity**, plus all 4 bugcheck codes/params | Latent fault + workload accelerant; mechanism predicted, not measured | — |

**The failure mode both times was accepting a summary instead of returning to the raw data.**
`params_all_on_cuda=True` was a true summary that missed spill; "217 WHEA events since May" was a
true summary that missed severity. Each was caught only by re-deriving from the underlying records.

**⚠ Git history carries a superseded claim that cannot be rewritten.** PR #5 squash-merged as
commit **`5ad4c9b`** with the title:

> `docs: S-002 Q1 answered — GPU PCIe link fault (pre-existing hardware) (#5)`

That title was written **before** the correction, and its parenthetical **"(pre-existing hardware)"
is superseded by this entry** — the accurate reading is *latent pre-existing link weakness that this
workload accelerates*, per the provenance table above.

Two details matter for anyone auditing history:
- The squash **body** does contain all four constituent commit messages *including* the retractions,
  so a reader who opens the full commit sees the correction sequence. But **`git log --oneline`
  shows only the title**, and the body's *first* message also states the superseded
  "the fault predates the project / our load did not cause it" framing before later messages walk
  it back. History read top-down is therefore misleading in isolation.
- It **cannot be corrected in place**: `main` is branch-protected (D-008 — required `test` check,
  PR-only, `enforce_admins`), so rewriting history would require a force-push that protection
  forbids, and rewriting merged history would be the wrong remedy regardless.

**Authority rule: where commit metadata and this log disagree, THIS ENTRY WINS.** Commit titles are
not decision records; `docs/README.md` is.

**Adjacent audit (2026-07-19):** `git log -p --all -- .vscode/settings.json` confirms the file
existed in exactly two commits — added in `5ad4c9b`, removed in `a317a73` — and only ever contained
a 10-line `files.exclude` block (`.git`, `.svn`, `.hg`, `.DS_Store`, `Thumbs.db`, `.mule`).
**No credentials, tokens, or sensitive paths entered history.** No remediation required.

**Suggestive but NOT conclusive:** at idle the link reports `pcie.link.gen.current=1` (max 5) and
`width=8` (max 16). Consistent with AER-driven downtraining — **but confounded**, because NVIDIA
GPUs idle at low link speed for power management and some laptops are wired x8. Not offered as
proof; the 217 AER records are the solid evidence.

**Conclusions:**
1. **The local tier is NOT killed outright — it is conditional.** The mechanism in §3 above is what
   keeps it alive: if spill traffic mediates the escalation, then a configuration that fits in VRAM
   may not trigger the fault at all. **A resident-footprint fix is therefore not just an
   optimization — it is the candidate remedy**, and it must be measured before writing the tier
   off. (An earlier draft of this entry concluded "not viable regardless of the memory fix"; that
   inference was wrong — "a memory fix cannot repair a link" does not imply "a memory fix cannot
   avoid triggering it.")
2. **This is still also a platform problem.** Owner actions worth taking in parallel: update NVIDIA
   driver (595.71 current) and BIOS/EC firmware, and open a vendor support conversation — 148
   corrected PCIe AER errors over seven weeks plus a fatal on a machine this new is warranty
   territory. **Whether repair/replacement resolves it is UNKNOWN**; do not plan the project around
   that outcome either way.
3. **Project consequence — de-risk without abandoning.** Cache generation (D-009 §3 (A)) can move
   to **different compute** (cloud GPU / Colab / cluster) to remove the schedule dependency on
   both the hardware outcome *and* the Q1 result; a rented ≥16 GB GPU additionally makes the S-001
   fp16 non-fit stop binding, collapsing two problems into one. But this is **de-risking, not a
   verdict on the local tier** — Q1 may well restore it. Either way this stays **inside the
   D-004 §5 boundary** and is **not** a retreat to AlphaFold retrieval; D-003's graded DL claim is
   unaffected, since ESMFold still runs.
4. **Q2 (resident-footprint fix) is deferred, not cancelled** — whatever compute hosts the cache
   build still needs a configuration that fits, and the fp16-does-not-fit finding (S-001) travels
   with us to any 8 GB-class device. On a ≥16 GB device it may simply not bind.
5. **Minidumps remain unread** (need an elevated shell). Now low value — WHEA already identified
   the component. Only worth revisiting if the vendor asks for them.

### D-009 — Iteration 1 scope, job queue shape, and ECD boundary selection
- **Date:** 2026-07-19
- **Status:** **Accepted (2026-07-19)** — §1 and §2 accepted as originally logged; **§3 resolved
  by S-001 to (A) cache-first**, with the length cap explicitly left unmeasured. Note that
  Iteration-1 application work remains blocked, now on **S-002** rather than on §3: (A) is
  chosen but not executable until a folding configuration exists that fits and does not crash
  the host.
- **Context:** D-004 ratified the two-tier topology and carried three items forward: the
  job queue schema and claim mechanism, extracellular-domain boundary selection, and the
  Iteration-1 scope question (cache-first vs. live-first). The first two are resolvable
  from known constraints. The third depends on measured ESMFold performance on 8 GB VRAM,
  which does not yet exist. Per the log-leads-the-code rule, the resolvable parts are
  ratified here and the unresolved part is stubbed explicitly rather than guessed.

---

#### §1 — Job queue: dedicated `jobs` table (Accepted)

- **Decision:** Fold jobs live in a **dedicated `jobs` table**, not as additional columns
  on `protein_analyses`.
- **Rationale:** `protein_analyses` rows are durable scientific records; job state is
  transient operational state with retries, failures, and worker ownership. Merging them
  would (a) attach permanently-dead queue columns to every historical analysis, (b) make
  retry semantics awkward, since a retry is a new attempt against the same analysis, and
  (c) conflate "this analysis exists" with "this fold is in flight."
- **Shape (initial):**

  | Column | Type | Notes |
  |---|---|---|
  | `id` | SERIAL PK | |
  | `analysis_id` | INTEGER FK → `protein_analyses(id)` | the record this fold produces |
  | `status` | VARCHAR(20) | `pending` \| `claimed` \| `complete` \| `failed` |
  | `claimed_at` | TIMESTAMPTZ NULL | set at claim; used for stale-claim reaping |
  | `completed_at` | TIMESTAMPTZ NULL | |
  | `worker_id` | VARCHAR(64) NULL | which worker holds it |
  | `attempts` | INTEGER DEFAULT 0 | retry budget |
  | `error` | TEXT NULL | last failure message |
  | `inference_settings` | JSONB | dtype, `chunk_size`, model revision, sequence length — the reproducibility record (D-004) |
  | `created_at` | TIMESTAMPTZ | |

- **Claim mechanism:** `SELECT ... FOR UPDATE SKIP LOCKED` — the standard Postgres
  queue-claim pattern. Correct with a single worker and remains correct without change if
  a second worker is ever added.
- **Indexes:** `jobs(status, created_at)` for the claim query; `jobs(analysis_id)`.
- **Stale claims:** a `claimed` job older than a threshold (initially 30 min) is returned
  to `pending` and `attempts` incremented. Covers the laptop-sleeps-mid-fold case, which
  D-004 accepted as a normal operating condition rather than an error.
- **Deep-learning justification:** indirect but load-bearing — this is the mechanism that
  lets neural inference run on hardware that can actually hold the model. Without a
  durable queue, the local-GPU tier from D-004 is not viable and the graded DL work has
  nowhere to execute.

---

#### §2 — ECD boundary selection from UniProt topology (Accepted)

- **Decision:** For each target protein, fold **only the extracellular domain**, with
  boundaries taken from **UniProt's `Topological domain` feature annotations** where the
  description is `Extracellular`.
- **Method:** Query the UniProt REST API for the accession, read `features` of type
  `Topological domain`, select extracellular spans, slice the canonical sequence to that
  residue range, and submit only the slice to ESMFold.
- **Persistence:** store the selected range and its provenance on the analysis row
  (`metadata` JSONB: `ecd_start`, `ecd_end`, `ecd_source`) so the 3D viewer can label
  precisely what is being displayed, and so results are reproducible.
- **Fallback:** when no extracellular topological annotation exists, fall back to the full
  canonical sequence **and surface a visible warning in the UI** — the user should know
  they are looking at a whole-protein fold, which for a long target may fail the
  length cap. Absence of annotation is scientifically informative, not merely an error.
- **Multiple extracellular spans:** where a target has more than one, select the longest
  by default and record the choice; per-span selection is a later enhancement.
- **Deep-learning justification:** this is what makes the D-003 model choice tractable on
  D-004 hardware, and it is *scientifically* correct rather than merely convenient — ADC
  antibody binding occurs at the ECD, so the domain we fold is the domain that matters.
  Reference sizes: HER2 ECD ~630 aa, Trop-2 ECD ~250 aa, Nectin-4 ECD ~350 aa, against
  full lengths of 1255 / 323 / 510 aa respectively.

---

#### §3 — Iteration 1 scope — **RESOLVED 2026-07-19: (A) cache-first**

- **Status:** **Accepted.** Resolved by S-001. The pre-registered branch that fired was
  *"600 aa OOMs / won't load cleanly in fp16 → **(A) cache-first**, and escalate."*
- **Decision:** **(A) cache-first.** Iteration 1 ships the Mission Briefing plus the curated
  ADC target database served from cached PDB/pLDDT/PAE artifacts. User-submitted live folding
  is deferred. The demo does not depend on the laptop being awake — which, given three host
  bugchecks under load, is now a hard requirement rather than a convenience.
- **The length cap is deliberately NOT set.** D-009 §3 originally expected the cap to fall out
  of the bisection. It cannot: **no configuration ran clean**, and the 630 aa fold was never
  measured (3/3 host crashes). A cap derived from a spilling, crashing configuration would be
  fiction. **The cap stays unmeasured until a working configuration exists (S-002).**

---

##### STRUCTURAL AMENDMENT (2026-07-19): there are **TWO caps**, not one

**The problem this fixes:** D-006 and S-001 used a single sequence-length cap, and treated
**`chunk ≤16` as a FAIL** (*"severe chunking ⇒ ceiling below this length"*), alongside a
**`time < 120 s`** criterion. Those encoded an **interactive-latency assumption** — a user waiting
on a live fold cannot tolerate minutes, and heavy chunking means slow. **Cache-first (this section)
makes that assumption irrelevant for Iteration 1.** An offline cache build does not care whether a
fold takes four minutes; it runs unattended.

**Decision — split the cap into two numbers with two different criteria:**

| | **Interactive cap** | **Cache-build cap** |
|---|---|---|
| **Applies to** | live user-submitted folding (deferred to Iteration 1.5+) | offline pre-fold of the curated ADC target DB (**Iteration 1**) |
| **Bounded by** | **latency** — the user is waiting | **memory fit + host stability** only |
| **Criteria** | `chunk ≥ 32` **and** wall time `< 120 s` **and** no spill | **no spill** **and** host survives. Wall time is **not** a criterion. `chunk = 16` or `8` is **acceptable**. |
| **Status** | unmeasured | unmeasured |

**Consequence — read HER2 correctly when it is finally folded:** a HER2 ECD (630 aa) fold that
completes at `chunk 16` in four minutes without spilling is a **PASS for the cache path**, and
simultaneously a **FAIL for the interactive path**. Under the old single-cap criteria it would have
been recorded as a plain failure. **This is logged before HER2 runs precisely so the result is not
misread when it arrives.**

**Why this changes the product, not just the diagnosis:** it means the curated target database can
include **large ECDs that would never be viable interactively** — HER2 (630 aa) is the flagship ADC
target, and cache-first is what makes it reachable. The two-cap split converts a latency constraint
into a *scope* decision instead of an exclusion.

**Scoping note for D-006/S-001 criteria:** their `chunk ∈ {64,32}` and `time < 120 s` conditions are
hereby scoped to the **interactive** cap only. They were never valid criteria for the cache path.
- **The binding condition on (A) still applies** (from the original stub): cache-first does not
  weaken the graded DL content **only if the folding pipeline is real, committed, reproducible
  code in this repo** that produces the cache — not a one-off script. That condition is now
  *doubly* binding, because the cache is the only path to a demo.
- **Blocked downstream:** the cache cannot be built until S-002 yields a configuration that both
  fits and does not crash the host. **(A) is chosen, but not yet executable.**

*(Original stub text retained below for the record.)*

- **Status (superseded):** UNRESOLVED. This clause is deliberately incomplete. Iteration-1
  application work MUST NOT begin until it is filled in.
- **The fork:**
  - **(A) Cache-first.** Iteration 1 ships the Mission Briefing plus the curated ADC
    target database, folded offline by the real pipeline and served from cached
    PDB/pLDDT/PAE artifacts. The worker and `jobs` table exist and are exercised by the
    offline folding run, but user-submitted live folding is deferred to Iteration 1.5.
    Demo is independent of the laptop being awake.
  - **(B) Live-first.** Iteration 1 ships the full loop: user submits a sequence → job
    queues → local worker folds → result renders. More moving parts; demo depends on the
    inference tier being online at presentation time.
- **What decides it:** spike **S-001** (below). The threshold, set in advance so the
  result is not rationalized after the fact:
  - 600 aa fold completes in **under ~2 minutes** at acceptable peak VRAM → **(B) viable**
  - 600 aa fold takes materially longer, or OOMs at `chunk_size=32` in fp16 → **(A)**,
    and the length cap is revised downward to whatever 8 GB actually sustains.
- **Note on the DL claim under (A):** cache-first does not weaken the graded deep-learning
  content **provided the folding pipeline is real, committed, reproducible code in this
  repo** — invoked to produce the cache — and not a one-off script run once by hand. If
  (A) is chosen, that condition is binding.

---

#### Follow-ups
- Alembic migration for `jobs` (blocked on §3 only in timing, not in content).
- Worker credential handling — Fly secrets, referenced by name (Principle 4).
- Authenticated artifact-upload endpoint (D-004 consequence, still open).
- ARCHITECTURE.md §4 (data model) gains `jobs`; §6 Iteration-1 row updates once §3 resolves.

### S-001 — Spike: measure ESMFold fp16 performance on 8 GB Blackwell
- **Date:** 2026-07-19
- **Status:** **CLOSED 2026-07-19** — answer: **no, not in this configuration** (see RESULTS).
- **Type:** Spike (time-boxed investigation, not a feature). Produces a measurement and a
  decision input, not shipped functionality.
- **Question:** Does `facebook/esmfold_v1` in fp16 fold ADC-relevant extracellular domains
  on an 8 GB Blackwell laptop GPU, and how fast?
- **Method:**
  1. Load `esmfold_v1` with `torch_dtype=torch.float16` on the local GPU.
  2. Set `chunk_size=64`. Fold a ~300 aa sequence (Trop-2 ECD scale). Record peak VRAM
     (`torch.cuda.max_memory_allocated`) and wall time.
  3. Fold a ~600 aa sequence (HER2 ECD scale). Same measurements.
  4. If either OOMs, retry at `chunk_size=32` and record.
  5. If 600 aa OOMs at 32, bisect downward to find the actual sustainable ceiling.
- **Record:** peak VRAM and wall time per sequence length and chunk size; mean pLDDT of
  each output as a sanity check that fp16 has not degraded quality; model revision hash
  and torch version.
- **Decides:** D-009 §3 (cache-first vs. live-first) and the final API sequence-length cap
  in D-004.
- **Time box:** one afternoon. If the model will not load at all in fp16, stop and
  escalate — that invalidates the D-004 mitigation stack and D-003 needs revisiting.
- **Deliverable:** results appended to this entry, then D-009 §3 filled in and promoted
  to Accepted.

---

#### RESULTS (2026-07-19) — **Status: CLOSED.** Escalation branch fired.

**Reproducer pin (what actually ran):**

| Item | Value |
|---|---|
| torch | `2.11.0+cu128` (CUDA build 12.8) |
| transformers | `5.14.1` |
| model | `facebook/esmfold_v1`, revision **`75a3841ee059df2bf4d56688166c8fb459ddd97a`** |
| precision | `esm.half()` → fp16 LM trunk + fp32 folding trunk |
| GPU | NVIDIA RTX PRO 2000 Blackwell Laptop, capability sm_120 |
| **on-disk weights** | **9,581,481,414 B ≈ 9.58 GB** (`du`); the in-run tree walk reported 9.78 GB — Windows lacks symlink support so HF duplicates blobs into `snapshots/`. **Not the ~2.5 GB originally assumed.** Disk ≠ VRAM, but it is the worker's deployment footprint. |

**Unit correction (load-bearing, applies to every figure below):** `nvidia-smi` reports
**MiB**; torch reports **decimal GB**. `8151 MiB` = 8.55 GB decimal (≠ "8.15 GB").
All memory figures below are normalized to **MiB**.

**Memory — the model does not fit at rest:**

| Quantity | MiB |
|---|---|
| Physical VRAM | **8151** |
| Free at start (desktop using the rest) | 7043 (run 2/3); 7799 (run 1) |
| **Resident after fp16 load** | **8116** |
| Peak during 248 aa fold | **8545** |

`params_all_on_cuda = True` (all 4498 params on CUDA — no accelerate/`device_map` offload),
**but resident (8116) exceeds free VRAM (7043)**, so Windows WDDM silently spilled to shared
system RAM rather than raising OOM. Peak (8545) exceeds even *total* physical (8151).
**Conclusion: fp16 alone does not fit `esmfold_v1` in 8 GB.** The absence of an OOM is a
Windows artifact, not evidence of a fit; on Linux this would have raised `CUDA out of memory`.

**Load time — run 1's 631 s was WRONG as a load figure.** It was download-dominated. From a
warm cache, **load = 15–16 s** (runs 2 and 3, consistent). Relevant to D-004 worker design:
loading per job is cheap; holding resident is what does not fit.

**Folds actually measured:**

| Target | Len | Chunk | Time | Peak | mean pLDDT | Verdict |
|---|---|---|---|---|---|---|
| Trop-2/TACSTD2 ECD (23–274→27–274) | 248 | 64 | 48.8 s | 8545 MiB | 70.7 | **NOT-CLEAN — `vram-spill`** (run 1 logged `CLEAN` *before* spill detection existed; superseded) |
| **HER2/ERBB2 ECD (23–652)** | **630** | — | — | — | — | **NEVER MEASURED — host bugchecked, 3/3 attempts** |

**pLDDT scale trap fired for real:** raw B-factors came back on the **0–1 scale** and were
rescaled ×100 (`rescaled-x100(raw was 0-1 scale)`) to 70.7. Unrescaled, the guard would have
read 0.707 and wrongly flagged it as suspect/zero. The check is honest only because the
rescale is explicit.

**Host instability — the run never completed:** three attempts at the 630 aa fold, three
hard crashes, all with the **identical bugcheck `0x00020001` (HYPERVISOR_ERROR)**, byte-identical
parameters `(0x28, 0x1, 0x29b92701, 0xfc801000)`:

| # | Kernel-Power 41 (crash) | BugCheck 1001 (reboot) | Minidump |
|---|---|---|---|
| 1 | 2026-07-19 16:32:19 | 16:32:32 | `071926-18656-01.dmp` |
| 2 | 2026-07-19 16:44:28 | 16:44:44 | `071926-21093-01.dmp` |
| 3 | 2026-07-19 16:48:00 | 16:48:15 | `071926-20781-01.dmp` |

Identical signatures across three independent runs indicate a **reproducible fault**, not random
corruption. Whether it is a memory-pressure cascade (VRAM spill thrashing the WDDM/shared-memory
path) or an underlying hardware/driver problem is **not determined by this spike** → **S-002**.

**Decides:** D-009 §3 → **(A) cache-first** (the pre-registered "won't load cleanly in fp16 →
cache-first + escalate" branch). Length cap **remains unmeasured** — a cap cannot be set from a
configuration that never ran clean. D-004's mitigation stack is invalidated at rung one (amended
below). **The local inference tier's viability is now itself unproven** pending S-002.

### D-008 — Gate proven; branch protection required; paths-ignore removed
- **Date:** 2026-07-19
- **Status:** Accepted (supersedes the "doc-only commits bypass the test gate" clause of
  D-005 and the `paths-ignore` choice in D-007)
- **Context:** The CI gate (D-005/D-007) was only half a gate. `push: branches: [main]`
  makes the main-push run a **post-hoc check** — it runs on a commit *already on main*, so
  nothing is physically blocked; the keel run went green because the code was clean, not
  because a gate stood in the way. **The PR path is the real gate**, and it only blocks if
  `main` is *protected* and merging is the only route in. Proven empirically below.
- **Evidence (all on 2026-07-19):**
  - **Red gate on a PR:** PR #1 (`break-it`, deliberately broken assert) → gate run
    **`test` = failure, `deploy` = skipped** (`deploy: needs: test` did its job):
    https://github.com/mdk32366/Project-PharmFoldMDK/actions/runs/29706935765
  - **Advisory-only before protection:** PR #1 read `MERGEABLE / UNSTABLE` — a failing
    check did **not** block merge on its own.
  - **Blocking after protection:** same PR flipped to `MERGEABLE / BLOCKED` once `test`
    was required.
  - **Direct push refused:** `git push origin main` (empty commit) →
    `GH006: Protected branch update failed ... Changes must be made through a pull
    request ... Required status check "test" is expected.`
- **Decision:**
  1. **Branch protection on `main` is a hard prerequisite** and is now set: require a pull
     request (0 approvals), require the **`test`** status check, **`enforce_admins: true`**
     (no bypass — including the owner), no direct pushes. Direct pushes to `main` (like the
     keel commit `d656b63`, which predated protection) are no longer possible.
  2. **Remove `paths-ignore` from `gate.yml`.** With `test` now a *required* check, a
     doc-only PR that never triggered the workflow would leave the required check
     unreported and the PR **unmergeable forever**. Dropping `paths-ignore` makes the ~20s
     suite run on every PR, so the check always reports; docs pay a trivial always-green
     cost instead of deadlocking.
- **Deep-learning justification:** Neutral (process), but this is the difference between a
  gate that *looks* enforced and one that actually is — the guarantee that no untested
  inference code can reach prod now holds against a tired 11pm `git push origin main`.
- **Consequences / follow-ups:**
  - Doc-only commits now run the test suite (they pass trivially and are never blocked) —
    this is the accepted reversal of the earlier doc-bypass intent.
  - When the real Fly deploy replaces the placeholder, **guard the `deploy` job** (not the
    workflow trigger) against doc-only changes, so docs still run tests but don't redeploy.
  - `enforce_admins: true` means even the owner merges via PR with `test` green — by design.

### D-007 — Lay the keel: `tests/` + CI deploy gate scaffold
- **Date:** 2026-07-19
- **Status:** Accepted
- **Context:** Realize the D-005 deploy gate as actual repo scaffolding **before** any
  application code exists, so the "no untested code to prod" discipline is in place from
  the first line of real code.
- **Decision:**
  - **`tests/`** with `conftest.py` exposing an **in-memory SQLite fixture** and one trivial
    passing smoke test. The fixture uses the **stdlib `sqlite3`** module (zero extra deps →
    CI green with only `pytest`); it will graduate to SQLAlchemy/SQLModel sessions when
    models land.
  - **`.github/workflows/gate.yml`**: `deploy` job `needs: test`; **native `paths-ignore`
    filter** (`**.md`, `docs/**`) so doc-only commits never trigger the workflow (that is
    how they "bypass the gate" per D-005). CI pins **Python 3.11**, `actions/checkout@v5`,
    `actions/setup-python@v6`.
  - The **`deploy` job is a placeholder** (echo) — real Fly deploy (flyctl + `FLY_API_TOKEN`)
    is wired in a later decision once the app exists. **No application code written.**
- **Deep-learning justification:** Neutral (scaffolding), but it stands up the gate that
  will protect the DL pipeline's correctness before any inference code can reach prod.
- **Consequences:** The SQLite fixture is stdlib-only for now; pgvector/Postgres paths still
  need the separate integration job flagged in D-005. Deploy is inert until wired.

### D-006 — ESMFold fold-path strategy for the 8 GB VRAM budget
- **Date:** 2026-07-19
- **Status:** ⚠ **INVALIDATED AT RUNG ONE (2026-07-19) by S-001 — REPLACEMENT RUNG ONE NOW MEASURED
  (S-003).** The ladder below assumes fp16 makes the model *fit at rest*; it does not
  (resident 8116 MiB vs 7043 MiB free). Rungs 2–6 reduce **activation** memory and cannot fix a
  **resident-weight** overrun. Do not implement this ladder as written.
  **New rung one (measured, S-003): quantize the ESM-2 LM trunk to int8 via `bitsandbytes`, leaving
  the folding head at full precision** → resident 5351 MiB, peak 5779 MiB, **no spill**, ~1.8×
  faster, pLDDT 74.7 vs 70.7 baseline. **Rung two: bf16** for the unquantized parts (same footprint
  as fp16, better numerical headroom, quality unchanged at +0.2). Chunking / length caps / ECD
  scoping remain valid as *activation*-memory rungs **below** these. Ladder retained verbatim below
  for the record; rewrite pending S-002 Q1 confirmation under sustained load.
  **⚠ ALSO RE-SCOPED (D-009 §3 two-cap amendment, 2026-07-19): this entry's `chunk ≥ 32` and
  `time < 120 s` conditions are INTERACTIVE-path criteria only.** They encoded a latency assumption
  that cache-first makes irrelevant. For the **offline cache build**, `chunk = 16` or `8` and a
  multi-minute fold are **acceptable**; the only criteria there are *no spill* and *host survives*.
- **Context:** The local inference GPU has **8 GB VRAM** (D-004). Full `esmfold_v1`
  (ESM-2 3B) wants ~16 GB+ for long sequences, so it will OOM on large proteins without a
  deliberate memory strategy. ADC targets are often large, but ADCs bind **cell-surface
  epitopes**, so the extracellular region is the scientifically relevant part to fold.
- **Decision — a layered strategy, applied in order:**
  1. **Half precision:** run the ESM-2 language-model trunk in fp16 on the GPU to roughly
     halve activation memory.
  2. **Axial-attention chunking:** set a `chunk_size` (start **128**, step down to 64/32 on
     OOM) to cap peak attention memory at a modest speed cost.
  3. **Extracellular-domain folding:** for a UniProt input, parse topology
     (`TRANSMEM` / `TOPO_DOM` features), extract the **extracellular domain(s)**, and fold
     those rather than the full chain — both ADC-appropriate and VRAM-friendly. If topology
     is unavailable, fall back to a length-capped full fold.
  4. **Interactive length cap:** the live "bring-your-own-sequence" path caps at
     **~400 residues** (starting value); longer inputs are routed to the offline pipeline
     or folded domain-only.
  5. **Graceful OOM degradation on the worker:** catch CUDA OOM → retry smaller
     `chunk_size` → **CPU-offload** the trunk (using the 31.5 GB system RAM, slow but
     completes) → else mark the job `needs_offline`.
  6. **Offline pre-compute pipeline:** a non-interactive worker mode folds the **curated
     ADC target database** ahead of time (CPU-offload allowed, no time pressure); results
     are cached as Volume artifacts + DB rows so the class demo path is always instant.
- **Deep-learning justification:** These are the model-execution decisions themselves —
  precision, attention chunking, and input truncation are standard neural-inference
  engineering, and folding the extracellular domain aligns the model's compute with the ADC
  biology. This is exactly the "how we actually run the deep model" reasoning the course
  expects, not an API wrapper.
- **Consequences / follow-ups:**
  - The 400-residue cap and `chunk_size=128` are **estimates**; measure real peak memory vs.
    sequence length on the 8 GB card and update this entry with the validated numbers.
  - Domain extraction needs a UniProt topology parser; proteins lacking topology annotation
    fall back to length-capped full folding.
  - fp16 may slightly reduce coordinate accuracy vs. fp32 — acceptable for exploration;
    note it in output caveats.
  - Adds an **offline pre-compute worker mode** to the `worker/` component (D-004).

### D-005 — CI/CD deploy gate + testing strategy (no untested code to prod)
- **Date:** 2026-07-19
- **Status:** Accepted
- **Context:** Deployment to Fly.io must be rock-solid — **no untested code reaches prod.**
- **Decision:**
  - **GitHub Actions gate:** on PRs and pushes to `main`, run a `test` job; the Fly
    **deploy job runs only if tests pass** (`deploy: needs: [test]`).
  - **All tests live in `tests/`** (plural — matches the existing Test Plan and pytest
    convention; if you want the literal singular `test/`, say so and I'll rename).
  - **Two kinds of tests:** (1) **functional** — `pytest`, `*.py`, covering data layer,
    inference logic, API contracts (per Test Plan §A); (2) **user-based** — structured
    human scenarios (per Test Plan §B), run at iteration boundaries, gating iteration
    sign-off rather than each push.
  - **Test database is SQLite** (in-memory / temp file): fast, deterministic, no external
    DB in CI. All external calls — ESMFold inference, AlphaFold DB, UniProt — are mocked.
  - **Doc-only commits bypass the test gate:** a path filter treats changes limited to
    `docs/**`, `**/*.md`, `ARCHITECTURE.md`, `LICENSE`, etc. as non-code and skips the
    `test` job. Any change touching code runs the full gate.
- **Deep-learning justification:** Neutral (process), but it guards the DL pipeline's
  correctness — pLDDT/PAE parsing, fallback behavior, and the job-queue contract get
  tested before they can reach prod.
- **Consequences / known gaps:**
  - **SQLite ≠ Postgres/pgvector.** Vector search and Postgres-specific SQL cannot run on
    SQLite, so those paths must be mocked or covered by a **separate Postgres integration
    job** later (flag for Iteration 3). *(Same class of gap JARVIS hit: SQLite `create_all`
    never exercises real Postgres/migration behavior.)*
  - Deploy needs `FLY_API_TOKEN` in GitHub Actions secrets.
  - The local GPU worker (D-004) is out of the prod deploy path but its contract with the
    app (job schema, artifact upload) must be covered by functional tests.

### D-004 — Deployment & inference topology: Fly serving tier + local GPU worker (pull-based)
- **Date:** 2026-07-19
- **Status:** Accepted
- **Context:** ESMFold (D-003) is GPU-heavy and Fly.io GPU is uncertain/expensive. The
  developer has a local machine with an **NVIDIA RTX PRO 2000 Blackwell Laptop GPU (8 GB
  VRAM)** and **31.5 GB system RAM**, and wants the app web-accessible but the model on
  local hardware.
- **Decision:** Split into two tiers.
  - **Serving tier — Fly.io:** Streamlit + FastAPI + Postgres/pgvector + Volume. Always-on,
    **no GPU**. Accepts analyses, stores data/artifacts, serves the UI.
  - **Inference tier — local machine:** a worker process running **ESMFold on the local
    NVIDIA GPU**.
  - **Coupling = pull-based job queue.** The web app enqueues an analysis job (a Postgres
    row, `status=pending`). The local worker **polls Fly over an authenticated outbound
    HTTPS connection**, claims pending jobs, folds, uploads artifacts (PDB / pLDDT / PAE)
    back to the Fly Volume, and sets `status=done|error`. **No inbound exposure of the home
    machine; no tunnel required.**
- **Deep-learning justification:** This is what makes running our own ESMFold feasible on a
  student budget — the neural inference runs on capable local hardware while the app stays
  web-accessible. The deep learning is still *ours*, executed by our worker.
- **Why pull-based over a tunnel (the ratified recommendation):** a laptop GPU sleeps,
  changes networks, and a fold takes seconds–minutes; pull-based tolerates intermittent
  connectivity, requeues on worker death/OOM, needs no open inbound port, and matches the
  async nature of folding. A synchronous tunnel (Tailscale/Cloudflare) would require the
  machine to be reachable and hold long HTTP requests open — kept only as a fallback.
- **Consequences / follow-ups (each becomes its own entry before we act):**
  - **8 GB VRAM is the binding constraint.** Full `esmfold_v1` (ESM-2 3B) wants ~16 GB+ for
    long sequences → OOM risk on large proteins. Mitigations to design: axial-attention
    `chunk_size`, a **live sequence-length cap**, folding only the **ADC-relevant
    extracellular domain**, and **pre-computing the curated ADC target DB offline** (can
    CPU-offload using the 31.5 GB system RAM and be patient).
  - **Availability:** if the local worker is offline, live jobs **queue** (no loss) but
    don't complete; pre-computed curated targets keep the class demo always-live.
  - **Worker plumbing needed:** an API token for the worker, job claim/lease semantics to
    avoid double-processing, and stale-job requeue on worker death (cf. JARVIS
    `recover_stale_jobs`).
  - **New repo component `worker/`** — runs locally, **not** deployed to Fly.

---

#### ⚠ AMENDMENT (2026-07-19, on S-001 results) — the mitigation stack is invalid at rung one

- **What broke.** The stack above (and its expansion in D-006) was ordered **fp16 → chunking →
  length cap → ECD scoping → caching**. Every rung *after the first* assumed the model **fits at
  rest** and that the remaining problem is activations. S-001 measured the opposite: the fp16
  model is resident at **8116 MiB against 7043 MiB free / 8151 MiB physical** — it spills to
  shared system RAM *before a single fold begins*. **fp16 alone does not get `esmfold_v1` into
  8 GB.** Chunking, caps, and ECD scoping all reduce *activation* memory; none of them reduce
  the *resident weight* footprint that is already over budget. The stack therefore needs
  **restructuring, not tuning**: the first rung must become a *resident-footprint* reduction.
- **Consequence for the topology.** D-004's two-tier design is not refuted, but the **local
  inference tier's viability is now unproven** — three attempts at a 630 aa fold ended in an
  identical host bugcheck (`0x00020001`). Whether the local GPU can sustain this work at all is
  **S-002**, and it gates the tier.
- **Bounded option space (restating §5 so the boundary is visible when the fix is picked).** A
  non-fit points to a **smaller/lighter folding configuration or narrower targets** — explicitly
  **NOT** a retreat to AlphaFold retrieval. Inside the boundary: **(a)** quantize the ESM-2
  trunk, **(b)** CPU-offload the language-model stack while keeping the folding head resident,
  **(c)** pair a smaller ESM-2 backbone with a folding head. Outside the boundary: making
  retrieval the deliverable (that would gut D-003's graded DL claim).
- **Reality check on (c):** `esmfold_v1` is the **only released ESMFold checkpoint**, so
  "just use a smaller variant" mostly is not a thing — (c) is a research project, not a config
  change. None of (a)/(b)/(c) is free and each needs its own measurement → **S-002**, not a
  guess made here.
- **Corrected worker input:** warm-cache load is **15–16 s**, not the 631 s recorded in run 1
  (that figure was download-dominated). Cheap loads make *load-per-job* viable, which matters
  precisely because *holding resident* is what does not fit.

### D-003 — Run ESMFold ourselves as the Iteration-1 deep-learning core
- **Date:** 2026-07-19
- **Status:** Accepted
- **Context:** The course grade depends on a neural network doing load-bearing work
  (ARCHITECTURE §1). Structure prediction is the tool's foundational output, so it is the
  natural home for the graded DL. The two candidates were (a) run a protein-folding model
  ourselves vs. (b) retrieve pre-computed structures from AlphaFold DB with a smaller
  neural component elsewhere. Option (b) risks reading as "just an API wrapper."
- **Decision:** PharmFoldMDK will **run ESMFold in-project** to predict 3D structure
  directly from an amino-acid sequence. ESMFold (Meta AI) is a transformer stack: the
  ESM-2 protein language model produces residue representations that a folding head turns
  into 3D coordinates, **from a single sequence with no MSA required**. We load it via
  Hugging Face (`facebook/esmfold_v1`, `EsmForProteinFolding`) / PyTorch. It emits
  per-residue **pLDDT** and **PAE**, which map straight onto our data model
  (`protein_analyses.mean_plddt`, `pae_json_path`). AlphaFold DB / UniProt retrieval is
  demoted to an **optional fast path for already-solved canonical proteins and a
  fallback**, not the deliverable — ESMFold is what we run and defend.
- **Deep-learning justification:** This is the strongest available DL story: our system
  performs neural inference (a ~3B-parameter transformer language model + folding head) to
  produce the primary output. It gives us genuine DL substance to present and analyze —
  the ESM-2/transformer architecture, single-sequence inference vs. MSA-based AlphaFold2,
  pLDDT confidence calibration, and behavior on cancer-target variants that may not exist
  in AlphaFold DB. It also uniquely enables Iteration 2's **mutation impact** (fold the
  wild-type and the mutant and compare) — retrieval alone cannot fold an arbitrary mutant.
- **Consequences / follow-ups (each becomes its own decision entry before we act):**
  - **Compute & memory is the primary risk.** Full `esmfold_v1` is GPU-hungry
    (multi-GB weights; long sequences can exceed ~16 GB GPU RAM). Fly.io GPU availability
    is uncertain and the TDD flagged GPU deprecation. **Open D-00X:** where inference runs
    (in-process vs. dedicated worker/queue) and on what Fly compute (CPU-only tolerated for
    short sequences vs. GPU). Mitigations to evaluate: axial-attention `chunk_size`,
    sequence-length caps for the demo, and **pre-computing + caching** structures for the
    curated ADC target database so the live demo path is fast.
  - **Sequence-length limit** for the graded demo (ADC targets are often large; may fold
    only the extracellular domain relevant to ADC binding) — to be set in a later entry.
  - **Dockerfile / dependency weight** grows (torch, transformers, model weights); cold
    start includes model load — plan a warm-load path.
  - **Reproducibility:** pin the model revision and torch version; record device and any
    `chunk_size`/length settings with each analysis (course reproducibility expectation).
  - Updates `ARCHITECTURE.md` §3 (DL core ratified), §5 (compute now an active concern),
    and §6 (Iter-1 DL content confirmed).

### D-002 — Governance: living architecture doc + this decision log
- **Date:** 2026-07-19
- **Status:** Accepted
- **Context:** The project must be maintainable and sustainable long-term, and its design
  rationale must be traceable for grading and for future work.
- **Decision:** Maintain `ARCHITECTURE.md` (repo root) as the single source of truth for
  system shape, updated in the same PR as any architectural change and brought current
  before any PR is filed. Maintain this `docs/README.md` as an append-at-top decision log
  where every design decision is written **before** its implementing work is finished.
  Both rules are encoded in `CLAUDE.md` so every working session is bound by them.
- **Deep-learning justification:** Neutral (process). Indirectly protects the DL mandate
  by forcing each decision to state where the deep learning is before code lands.
- **Consequences:** Slight up-front writing overhead per change; in exchange the project
  stays auditable and the DL story stays front-and-center.

### D-001 — Planning docs live in the repo under `docs/`
- **Date:** 2026-07-19
- **Status:** Accepted
- **Context:** Planning docs (TDD v3, DB plan, UI plan, test plan, checklist, proposal)
  were sitting in a non-git sibling folder, unversioned.
- **Decision:** Moved all six into `docs/` with flattened filenames and committed
  (`6ea1e7e`). They are the reference intent; ratified changes are logged here.
- **Deep-learning justification:** Neutral (housekeeping).
- **Consequences:** Single versioned home for project intent; the `.docx` proposal is
  tracked as binary.

---

## Open questions awaiting a decision entry

These are known forks in the road. Each becomes a `D-NNN` entry **before** we act on it.

- ~~**DL core for Iteration 1**~~ — **resolved in D-003: run ESMFold ourselves.**
- ~~**Where inference runs + Fly compute**~~ — **resolved in D-004: local GPU worker,
  pull-based; Fly serving tier has no GPU.**
- ~~**Sequence-length cap / domain selection**~~ and ~~**pre-compute & cache pipeline**~~ —
  **resolved in D-006** (fp16 + `chunk_size` + extracellular-domain fold + 400-residue live
  cap + OOM degradation + offline pre-compute). Caps still need empirical validation.
- **Worker ↔ app contract:** job schema, claim/lease semantics, artifact upload, auth token.
- **Prod DB choice:** Postgres-first vs. SQLite-on-Volume prototype (Database Plan §5).
  *(Note: this is the **prod** DB; the **test** DB is SQLite per D-005 regardless.)*
- **Embedding model** for semantic search (which encoder, `vector(384)` assumed).
- **Postgres integration test job** for pgvector/Postgres-specific paths (D-005 gap).
