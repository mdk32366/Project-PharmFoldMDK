### F-063 — ⚠⚠ Allocator-cap + child + Layer-1 attestation did not prevent a host bugcheck: climb reached highest_ok=384 with free_before collapsed to 1513 MiB, then the host died before 392 was written

- **Date:** 2026-08-31 · **Status:** ⚠ **OPEN.** It closes when folds on this host are either (a) proven safe under a gate that refuses before free/reserved collapse of this shape, or (b) ruled off this host with the residual named and accepted. ⚠ **No further folds on this host by any recipe until Matt clears it** (D-082 / climb docstring).
- ⚠ **Do not take `F-050`.** The guard-direction sweep stays RESERVED and unwritten.
- **How known (`D-016`):** Blackwell ceiling climb on MDKDevLaptop after Matt Layer-1 attestation. Card: NVIDIA RTX PRO 2000 Blackwell, ~8151 MiB, driver 610.88, WDDM. Command class: `ceiling_climb` / Q8WXD0 / tier local / int8 / chunk 64 / `--start 248 --stop 456 --step 8` / `--memory-fraction 0.85` / `--empty-cache` / `--fold-in-child` / `--layer1-attested`. Artifact: `data/census/ceiling_climb.blackwell.int8.20260831.jsonl` (8889 bytes, **0 NUL bytes** — fsync held). Companion: `data/census/ceiling_climb.blackwell.int8.20260831.runlog.err.txt` (and empty `.runlog.txt`). Control copies: `data/control/blackwell-climb-20260831/`. Matt reported OOM + **system crash**. Climb processes killed after. No `oom_caught` / stop / summary line in the jsonl. Note: `LastBootUpTime` still showed 2026-08-27 after the event — may have been a GPU/driver hard fault without a full OS reboot; either way the host was not safe to continue.

**THE NUMBERS.**

| fact | value |
|---|---|
| OK ladder | 248,256,…,384 — **18** ok steps |
| highest_ok | **384 aa** |
| last OK peak_alloc | **6357 MiB** |
| last OK peak_reserved | **6902 MiB** |
| last OK free_before | **1513 MiB** |
| last OK f059_peak_mib | 6350.37 |
| last OK pct_depart_f059 | 0.001044 |
| last OK wall | 54.16 s |
| next planned | 392…456 — **not recorded** |

F-059 agreement on every OK step was tight (pct_depart ≤ ~0.0014). The law tracked demand. The host still died.

**THE SUBSTANCE.**

1. ⚠⚠ **D-082’s three layers did not keep the host alive on this climb.** Allocator cap (0.85), persistent child (`fold-in-child`), and owner-attested Prefer No Sysmem Fallback were all in force. The failure was a **host crash / hard fault**, not a catchable `oom_caught` in the jsonl.
2. ⚠ **Headroom had already collapsed while steps were still `ok`.** At L=384, `free_before_mib=1513` with reserved 6902 near the cap. Empty-cache did not restore free. The climb continued. The next step was never fsynced.
3. ⚠ **`highest_ok=384` / peak_alloc 6357 is a recorded last OK, not a license.** It is a **candidate** `MEASURED_SUCCESS_PEAK_MIB` for a future RB re-gate on this card only after Matt clears the host. ⚠ **Do not run `--continue-after-rb4` or any local tile fold from it tonight.**

**WHAT IT DOES NOT ESTABLISH.**

- Not that Layer-1 was unset (Matt attested; flag was passed).
- Not a refutation of F-059 (departures were small on OK steps).
- Not a rewrite of D-104 / `route_at`.
- Not permission to rent, resume climb, or fold on this host tonight.

- **Relied on by:** host clear; any future Blackwell RB re-gate; F-062 (card-bound envelopes).
- **Assumptions refused:** that cap + child + Layer-1 attestation is sufficient to make over-allocation fail as a job rather than as a bugcheck / hard fault on this WDDM laptop.
- **Amended by:** —
