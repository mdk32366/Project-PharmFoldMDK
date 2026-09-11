### F-064 — ⚠⚠ After a successful Blackwell RB fold, in-process release does not restore free for the next preflight: free collapsed 7043→1649 MiB while reserved stayed ~6900; after process exit the GPU was free again

- **Date:** 2026-08-31 · **Status:** ⚠ **OPEN.** It closes when successive local tiles on this card either (a) each start from a cold process (or equivalent teardown that restores free before the next preflight), or (b) the residual is named and accepted. ⚠ Process-per-tile is the prescribed next gate; do not lower operational max below 380 on this evidence alone.
- ⚠ **Do not take `F-050`.** The guard-direction sweep stays RESERVED and unwritten.
- **How known (`D-016`):** RB re-gate after Matt host clear (F-063). Card: NVIDIA RTX PRO 2000 Blackwell, ~8151 MiB, driver 610.88, WDDM. Harness on main via PR #199 (`fb3826cb`): `route=local` AND `length≤384`, `MEASURED_SUCCESS_PEAK_MIB=6357`, climb exact-L preferred else hard envelope, `WORKER_FOLD_IN_CHILD=1`, `--limit 10`, no `--continue-after-rb4`. Artifact: `data/control/rb_local/rb_local_summary.regate384.csv` (PR #201).

**THE NUMBERS.**

| fact | value |
|---|---|
| tile 1 | O75445 USH2A t17 **L=380** |
| tile 1 requirement | 6357 / `hard_envelope_6357` |
| tile 1 preflight | FIT (`free_before=7043`) |
| tile 1 peak_alloc / reserved | **6336** / **6900** |
| tile 1 pct_depart_f059 | 0.000926 |
| tile 1 folded | yes |
| tile 2 | O75445 USH2A t18 **L=374** |
| tile 2 preflight | **refused_insufficient_headroom** (`free=1649`, need 6357) |
| folded | **1/10**; tiles 3–10 not attempted |
| after process exit | nvidia-smi ~0 used / ~7899 free |

**THE SUBSTANCE.**

1. ⚠⚠ **The F-063 envelope licensed the first fold.** L=380 succeeded under 6357 with peak_alloc 6336. This is not a too-long-tile finding and does not authorize dropping operational max below 380.
2. ⚠ **In-process release did not restore free.** After tile 1, reserved stayed ~6900 and free fell to 1649 — same collapse shape as F-063’s climb `free_before`. `release_resident_model` / empty-cache inside one long-lived process is insufficient on this WDDM card.
3. ⚠ **Exit restores the device.** After the batch process ended, the GPU reported free again. The failure is residency across tiles in one process, not a stuck driver after exit. Process-per-tile (fresh OS process that exits before the next preflight) is the prescribed next gate.

**WHAT IT DOES NOT ESTABLISH.**

- Not a refutation of F-059 (tile 1 departure was tiny).
- Not a rewrite of D-104 / `route_at`.
- Not permission to `--continue-after-rb4`, climb, or rent.
- Not that Layer-1 / fold-in-child were unset for the successful tile.

- **Relied on by:** process-per-tile RB re-run; any claim that empty_cache alone serializes folds on this card.
- **Assumptions refused:** that clearing the model cache in-process restores cold-start free between successive RB tiles on this Blackwell laptop.
- **Amended by:** —

