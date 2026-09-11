# ORDERS-Code — D-130-B + D-131 Phase 4 named refuse

**Date:** 2026-09-06
**Repo:** C:\\Projects\\Project-PharmFoldMDK
**Branch:** already on `d130-b-d131-phase4-named-refuse` tracking `origin/main` @ `932292d` — stay here; do not switch away
**Authority:** Matt GO via Emma Builder-Orders pipe (D-0047-C). Tip `932292d` = D-130-A (#253). Phase 5 template: `cbcb47d` (#250).

## Goal
Ship D-130-B Method/UI Phase 4 residual-RMSD OPS disclosure (as recorded) and D-131 labels for parents **3272** and **3394** as **named refuse / accept-refuse**. One docs+UI PR is fine. Measurement voice only. Open PR to `main`; do not merge.

## Spec / acceptance
- [ ] Edit `docs/method-hold48-tiles.md`: add addendum D-130-B / D-131 with tip `932292d`, out_root `residual_rmsd_ops_2026-09-05`, rollup PASS 0 / REFUSE 2 / recovered_of_two=0; 3272 `rmsd_irreducible` floor≈12.63 Å; 3394 `rmsd_gt_10` floor≈4.77 Å rmsd≈13.77 Å offset=0
- [ ] Replace any “Two joins are still open / Phase 4 must-hunt” prose for 3272/3394 with named refuse / accept-refuse
- [ ] Scrub “What this file is not” bullets that keep 3272/3394 as must-hunt
- [ ] Mirror in `ui/src/components/MethodNote.jsx`
- [ ] Flip fate in `ui/src/components/AssemblyReview.jsx` (+ tests): phase-4-must-hunt → accept-refuse / named refuse / is_accept_refuse true; attach Phase 4 0/2 rollup (not D-128 seven)
- [ ] Inventory = 17 PASS + 10 accept-refuse (Phase 5 eight + 3272 + 3394). Never 27/27 PASS / “solved”
- [ ] Commit on this branch; `gh pr create` to main; do not merge

### 17 PASS
2817, 2917, 2929, 3027, 3097, 3153, 3188, 3217, 3320, 3379, 3404, 3454, 3469, 3516, 3541, 3569, 3575

### 10 accept-refuse
2938, 2939, 3179, 3190, 3321, 3368, 3566, 3432, **3272**, **3394**

## Freeze
served=assembler; gate 10.0 Å; D-126 best experimental; no residual-RMSD re-run; no RMSD-v2; no F-004; no Fly POST from this order.

## Out of scope
Merging; Phase 6/7; touching unrelated untracked census/tmp files; inventing new decision numbers beyond D-130-B/D-131.

## Catch-up
After PR URL exists, Emma files `Sessions/Kaylee/CATCHUP-FROM-COPILOT.md`.
