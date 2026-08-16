# PRE-REGISTRATION — 2026-08-16 — Re-measuring the local ceiling under driver 610.88

> **Written BEFORE the measurement and before the instrument that performs it.** Governed by
> `### D-082`, `### D-077` dec 3, and `docs/FINDING-2026-08-16-fp16-bugchecks-the-host.md`.
> Where this file and the log differ, **THE LOG GOVERNS.** ⚠ This file is provenance, not authority.
>
> ⚠ **VOID IF CODE PRECEDES IT** (D-075 / D-077 / D-079 precedent). At this commit no measurement
> instrument exists beyond `core/vram_guard.py`, which measures nothing on its own.

**Provenance (D-016):** the prior stack is pinned in `data/census/stack_before_driver_upgrade.json`
(driver **596.72**, torch 2.11.0+cu128, transformers 5.14.1, RTX PRO 2000 Blackwell, 8,151 MiB). The
target is **610.88**, released 2026-07-30, reported by the owner. ⚠ **Every number below that
predates 610.88 is a 596.72 number and is labelled as such.**

---

## §1 — ⚠ The instrument cannot run behind its own guard, and this is how it is bounded instead

`vram_guard.preflight` refuses any length with no measured requirement. **The re-measurement is what
builds those requirements, so it cannot be gated by them** — it would refuse everything, forever.

⚠ **It is bounded by three other things, and none of them is an assumption about what fits:**

1. **The allocator cap is the ceiling of the experiment.** With
   `set_per_process_memory_fraction(f)` PyTorch raises `torch.cuda.OutOfMemoryError` **in Python**
   at the cap. **The measurement climbs until that raise.** ⚠ The refusal is the result, and it is
   catchable rather than fatal.
2. ⚠⚠ **IT CLIMBS. IT DOES NOT BISECT — and that is the lesson of the crash, not a preference.**
   The old probe jumped **209 → 313 aa**, a 50% increase with nothing measured in between, and the
   host died on that jump. **Bisection's entire value is large jumps into unmeasured territory,
   which is precisely what cannot be afforded here.** A climb costs more folds; every step is
   bounded by the one before it.
3. **Every step is durable before the next begins.** ⚠ `fsync`, because the last probe's
   append-only file came back as **55 bytes of `\0`** — a hard reset does not flush the page cache,
   and the record that was written *before* each fold specifically to survive a halt did not
   survive it.

## §2 — What is measured

**Only `int8`, chunk_size 64 — the `local` tier recipe, resolved from `TIER_RECIPE`.**
⚠ **fp16 is NOT probed on this host.** A bugcheck is not a data point worth buying twice, and n=1
is not a ceiling.

**Source:** `Q8WXD0` RXFP2, from `data/census/spancache`, truncated from residue 1 — the same
protein and the same construction as the int8 determinism control, so the two are comparable.

**At each length, recorded per fold:**

| Field | Why |
|---|---|
| `max_memory_allocated` | ⚠ **the actual demand** |
| `max_memory_reserved` | the allocator's retained pool |
| `nvidia-smi used` | ⚠ **what we mistook for demand on 596.72** |
| `mem_get_info` free/total | the real budget, which is not the card's label |
| `nvidia_driver_version` | D-082 — a ceiling is valid only under the stack that produced it |
| wall-clock | cost |

⚠ **Three memory numbers, none standing for the other.** On 596.72 we recorded **7,658 MiB** from
`nvidia-smi` for a 416 aa int8 fold and called it the peak. **It is `reserved`, inflated by the
caching allocator's retained pool, and the true demand is still unknown.** Establishing the gap
between allocated and reserved is the **first** thing this measurement produces, and it decides the
cap.

## §3 — ⚠ THE FORECAST, as a composition. Stated before the first fold.

**Step 0 — the determinism re-run doubles as the first curve point.** `Q8WXD0` at **416 aa** under
610.88, two folds.

```
PREDICTED
  determinism    IDENTICAL across both folds, as under 596.72
  max_allocated  ⚠ NOT PREDICTED — unknown, and it is the point of the exercise
  max_reserved   ~7,658 MiB, i.e. close to the 596.72 nvidia-smi figure
```

⚠ **`max_allocated` is deliberately left unforecast.** A forecast here would be a guess dressed as a
prediction, and the number decides the cap.

**⚠ Three outcomes, and the reading is fixed now:**

| If `max_allocated` at 416 aa is | Then |
|---|---|
| **well below** `max_reserved` (say < 5.5 GiB) | the 94% figure was cache, real headroom is larger than feared, cap **0.85** |
| **close to** `max_reserved` (> 7 GiB) | ⚠ **the card is genuinely near its limit at 416 aa**, cap drops to **0.70** and much of the local band routes to rental |
| **above the 0.85 cap** | ⚠ **the fold that "succeeded" on 596.72 cannot run inside a safe cap at all** — `known_good = 440` is refuted and the local tier is far smaller than the manifest assumes |

**Step 1 — the climb.** From **416 aa** upward in **+8 aa** steps to **456 aa** (past `known_good`
440), one fold per step, stopping at the **first** `OutOfMemoryError`.

```
PREDICTED COMPOSITION
  folds attempted        6 at most (416, 424, 432, 440, 448, 456)
  first refusal          ⚠ NOT PREDICTED — this is the measurement
  outcome vocabulary     ok | oom_caught | refused_by_cap
  ⚠ host bugchecks       0.  ANY host death falsifies the whole design and stops everything.
```

⚠ **+8 aa is `REPEAT_STEP`, the D-077 dec 4 stopping granularity** — reused so the resolution
matches the bound it is testing, rather than being chosen here.

## §4 — What would falsify this, and what halts it

- ⚠⚠ **A host bugcheck.** The three layers exist to make this impossible; one occurrence means they
  do not work and **no further fold happens on this host, by any recipe.**
- ⚠ **An `OutOfMemoryError` that is NOT caught** — i.e. the process dies rather than raising. That
  is layer 2 failing and layer 1 absent or ineffective.
- **A fold at 416 aa that fails under 610.88 having succeeded under 596.72** — a driver regression,
  and a finding rather than a nuisance.
- ⚠ **A determinism divergence between 596.72 and 610.88.** *ESMFold's output is not
  driver-invariant* is a methods note nobody publishes, and it would mean **every fold must record
  its driver** — which, as of `f0f5196`, it now does.

## §5 — ⚠ What must NOT move

**Zero database writes. No census row. No enqueue. No fold of any of the 82** — `### D-081` is
absolute. **No cross-recipe comparison is read; `### D-078` is unwritten.** The manifest is not
rebuilt by this: ⚠ **a ceiling changes ROUTING, and routing changes are a manifest revision with a
stated reason — not a silent edit.**

⚠ **And the sysmem fallback policy cannot be confirmed from code.** `sysmem_fallback_state()`
returns `unknown`, never `ok`. **If the owner has not set it, layer 1 is absent and every result
here is obtained without the only protection that addresses the mechanism that killed the host.**
That fact is recorded on the artifact, not assumed away.
