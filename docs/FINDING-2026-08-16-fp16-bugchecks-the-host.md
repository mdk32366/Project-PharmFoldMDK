# FINDING — 2026-08-16 — Exceeding VRAM at fp16 does not raise a catchable OOM; it bugchecks the host

> ⚠ **No number is taken. Six findings are already queued behind one free integer and the numbering
> ruling is overdue.** Where this file and the log differ, **THE LOG GOVERNS.** This is provenance.

**Provenance (D-016):** every value is Code's reading — the probe's stderr log, the Windows System
event log, `nvidia-smi`, and `data/census/determinism_control.int8.json`. The crash was reported by
the owner at the keyboard and independently confirmed in the event log.

---

## §1 — What happened

Task 4a's fp16 ceiling probe was running untiered at `--dtype fp16 --chunk-size 64`, bisecting
`(good=1, bad=417)` over RXFP2's cached sequence.

```
  probing length 209 (1/1) (good=1, bad=417)...
    -> ok
  probing length 313 (1/1) (good=209, bad=417)...
                                    ← the host died here
```

**Windows System event log:**

```
04:38:37  volmgr        161  Dump file creation FAILED, BugCheckProgress 0x00000053
04:38:37  volmgr        162  Dump file generation succeeded
04:38:38  Kernel-Power   41  rebooted without cleanly shutting down
04:38:50  WER-SystemErrorReporting 1001
          bugcheck 0x0000001e (0xffffffffc0000005, 0xfffff8039b5d3d…)
```

⚠ **`0x1E` is `KMODE_EXCEPTION_NOT_HANDLED`; `0xC0000005` is `STATUS_ACCESS_VIOLATION`.** That is a
**kernel-mode fault**, not a user-space allocation failure. **Host RAM was not the constraint** —
the machine has 31.5 GB and reports 22 GB free at rest. **It is a display-driver fault under VRAM
pressure** (WDDM, driver 596.72, RTX PRO 2000 Blackwell, 8,151 MiB).

## §2 — ⚠⚠ Why this is worse than a failed measurement

**`worker/ceiling_probe.py:_attempt` is built on the assumption that exceeding VRAM raises a Python
exception it can catch:**

```python
try:
    result = runner.fold(source[:length], ...)
except Exception as e:
    outcome = OOM if "out of memory" in str(e).lower() else ERROR
```

⚠ **On this platform that assumption is false.** The process never reaches the `except`. **The whole
machine goes down**, and with it every unflushed write. **A probe designed to survive its own
failure mode does not survive it.**

### ⚠ The append-only resume file was defeated by exactly the crash it exists for

`ceiling_probe` persists each attempt **before** the next fold, specifically so a halted run can
resume. After the reset, `data/census/fp16_ceiling.jsonl` is **55 bytes of `\0`** — the record was in
the OS page cache and never reached disk. **The `209 → ok` result survives only in the stderr log,
not in the append-only file that was supposed to guarantee it.**

⚠ **`fsync` is the difference between "written" and "durable", and the probe does not call it.**

## §3 — What was measured before the host died

```
fp16, chunk_size 64, RXFP2 truncated from residue 1
  209 aa   ok        ← folded; VRAM 7,874 MiB / 8,151 with weights resident
  313 aa   HOST BUGCHECK 0x1E during this attempt
```

⚠ **The 313 aa attempt is *when* the host died, not proof that 313 aa *caused* it.** A kernel fault
is not a controlled experiment and this one is `n=1`. **Recorded as a coincidence in time until it
reproduces, which it must not be asked to do casually.**

⚠ **`--good 1` was never tested** — the probe asserts its lower bound rather than measuring it, so
"fp16 folds at 209" is measured and "fp16 folds below 209" is assumed.

**For comparison, int8 on the same protein and card, which completed and is intact:**

```
Q8WXD0 416 aa int8/chunk 64 — IDENTICAL across both folds, kernel deterministic
peak VRAM 7,658 MiB / 8,151 = 94.0%      headroom 493 MiB
```

## §4 — ⚠ What this puts in doubt, none of it acted on

1. ⚠⚠ **The crank is unsafe as designed.** A census fold that exceeds VRAM does not fail its job —
   **it takes the host down mid-crank.** The manifest holds **2,691 rows in the `local` band** (up to
   440 aa) and **349 in `untested_band` (440–630)**.
2. ⚠ **`known_good = 440` is now in question on this driver.** int8 at **416 aa already sits at 94%**
   of the card. The bound came from S-004/S-005; **whether it was measured under this driver version
   is not recorded**, and a ceiling is only valid under the recipe *and the stack* that measured it.
3. ⚠ **The fp16 arm of 4a cannot be completed on this host by this method.** Any further probing
   risks another bugcheck, and a bugcheck is not a data point worth buying twice.
4. ⚠ **`ceiling_probe`'s OOM taxonomy is unsound here.** `OOM` vs `ERROR` presumes a catchable
   exception; the real third outcome is **`HOST_DOWN`**, which the instrument cannot record because
   it is not running when it happens.

## §5 — What is NOT concluded

⚠ **No fp16 ceiling is reported. One `ok` and one crash is not a ceiling**, and calling 209 a
ceiling would be an assertion dressed as a measurement.

⚠ **`### D-078` is untouched. No cross-recipe comparison has been read.** The int8 arm is complete
and the fp16 arm is not, so there is nothing to compare and no temptation to.

**Nothing was folded into any artifact, no census row exists, no database was written, and the repo
is intact at `f488e3b` with everything through it pushed.**
