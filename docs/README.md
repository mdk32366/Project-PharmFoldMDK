# PharmFoldMDK — Design Decision Log

> **This file is mandatory reading and mandatory writing.**
>
> **THE RULE:** *Every design decision we make gets written in this file **before** the
> work it describes is finished.* The log leads the code. If you are about to build,
> change, or discard something and the reasoning is not yet here, stop and record it
> first. A PR whose work is not reflected in a decision entry is incomplete.
>
> **THE SECOND RULE (provenance, D-016):** *Every claim names how it is known.* A written
> record fixes a claim in place; it does not make it true. Before a number or a status enters
> this log, ARCHITECTURE, or a PR, name the artefact it came from — the raw log line, the query
> output, the run URL. If you cannot name it, you are recording a belief, not a finding. A
> summary is not knowing: prefer the breakdown to the total, and **prefer the query whose answer
> could disqualify you** (`pg_available_extensions` tells you a thing *exists*; `pg_extension`
> only that it is *on* — a zero from the second cannot distinguish *absent* from *off*).
>
> Companion documents:
> - [`../ARCHITECTURE.md`](../ARCHITECTURE.md) — the current-state architecture (must be
>   updated in the same PR as any architectural change, and before any PR is filed).
> - [`GUIDE-renting-hold48.md`](GUIDE-renting-hold48.md) — RunPod hold-48 rental runbook
>   (D-113, D-114; RTX PRO 6000 Blackwell). ⚠ **D-118:** rental E2E **CLOSED** 2026-09-05 PT
>   (pod Terminated). The file opens with a CLOSED banner; Deploy / emit steps are
>   **historical** and must not be presented as the live path. Not a rewrite of the A6000 guide.
> - [`BUDGET-hold48-tiers-2026-09-04.md`](BUDGET-hold48-tiers-2026-09-04.md) — measured
>   budget / tier waves from the IGF2R pilot (D-113). **D-114** amends the cash envelope
>   only; measured forecasts stand. ⚠ **D-120:** stamped historical forecast (2026-09-05
>   closeout superseded it as a live plan).
> - [`PLAN-ui-post-wave2-endstate.md`](PLAN-ui-post-wave2-endstate.md) — post-Wave2 UI
>   evaluation and phased honesty plan (**D-117**). ⚠ **D-117 remains the plan/stance, not a
>   Kabsch GO.** Phase 1 P0 honesty is **D-118**. Phase 2 review UI is **D-120**.
>   **D-121** is the follow-on 8th-grade Method explainer (`method-hold48-tiles.md` +
>   `/method` addendum). The stitcher is a pLDDT assembler; seams are not scientifically
>   solved. **D-125** is the Kabsch restitch Spec
>   ([`SPEC-kabsch-restitch.md`](SPEC-kabsch-restitch.md)). **D-125-A** already
>   shipped the core BUILD on `main` (`26a40a8` / #237): overlap Cα Kabsch →
>   transform tile → existing `winning_tile`. **D-125-B** already shipped
>   UI dual-path honesty on `main` (`aa8d3f1` / #238). **D-126** is the
>   overlap-confidence Kabsch Spec
>   ([`SPEC-overlap-confidence-kabsch.md`](SPEC-overlap-confidence-kabsch.md))
>   (docs on `main` at `d59be6b` / #239 + amendment 1 `b32f9db` / #240).
>   **D-126-A** already shipped the core BUILD on `main` (`aa8aa02` /
>   #241): trimmed + pLDDT-weighted Kabsch → existing `winning_tile`;
>   sibling `confidence_kabsch/` tree. **D-126-B** already shipped UI
>   triple-path honesty on `main` (`abbcd00` / #242). **D-127** is the
>   piecewise / domain-aware Kabsch Spec
>   ([`SPEC-piecewise-domain-kabsch.md`](SPEC-piecewise-domain-kabsch.md))
>   (already on `main`, `00fa76d` / #243). **D-127-A** already shipped
>   the core BUILD on `main` (`e49bf34` / #244): per-domain weighted
>   Kabsch (no trim) → existing `winning_tile`; sibling
>   `piecewise_kabsch/` tree. **D-127-B** already shipped UI four-path
>   honesty **and** the Spec §7 Method addendum on `main` (`de9a80e` /
>   #245), discharging the mandatory Method obligation and disclosing
>   the D-127 OPS result. **D-128** is the linker / seam honesty Spec
>   ([`SPEC-linker-seam-honesty.md`](SPEC-linker-seam-honesty.md))
>   (already on `main`, `2004c5a` / #246). **D-128-A** already shipped
>   the core BUILD on `main` (`9e65cbf` / #247): sibling
>   `core/hold48_linker_seam.py` + `linker_seam/` tree; §1a honesty rows
>   for every path (null ≠ 0, unknown ≠ honest, prior trees read-only);
>   optional ±32 aa window fit → existing `winning_tile`. **D-128-B**
>   already shipped UI five-path honesty for that tree **and** the Spec
>   §7 Method addendum on `main` (`cd071d7` / #248), discharging the
>   mandatory Method obligation. **D-129** is the Phase 5 named-refuse
>   Spec ([`SPEC-phase5-named-refuse.md`](SPEC-phase5-named-refuse.md))
>   (**this PR**) — **labelling authority only**: the **eight** parents
>   (the linker seven **+ 3432**) are **`accept-refuse`**, that OPS
>   disclosure becomes **standing**, **3272 / 3394** stay **Phase 4
>   must-hunt** on a **separate Matt GO**, and there is **no linker-v2**.
>   Production paths (assembler / D-125
>   Kabsch / D-126 confidence / D-127 piecewise) stay callable and the
>   **assembler** stays the served path. ⚠ **Neither A nor B ran ops.**
>   A **D-128 OPS restitch of the must-hunt seven** (⚠ **`must-hunt` is
>   what they were called when that run was chosen; the Phase 5 sign has
>   since superseded that name — see D-129 / D-129-B**; tip `9e65cbf`,
>   out_root `linker_seam_ops_2026-09-05`) was handed to D-128-B **as
>   recorded** and is disclosed on the Method surface: **PASS 0 /
>   REFUSE 7 / FAIL 0**, `repaired_of_seven` = **0** (the pre-registered
>   allowed outcome), with the named give-back
>   `n_d125_pass_d128_refuse` = **5** and `n_d126_pass_d128_refuse` =
>   **6**. ⚠ **Not re-measured in that PR.**
>   ⚠ **Seams are not scientifically solved.** ⚠ **10.0 Å gate
>   STAYS.** ⚠ **No trim loop.** ⚠ **D-126 remains the best
>   experimental path until proven otherwise; the D-127 failed
>   experiment stays disclosed.**
> - [`SPEC-kabsch-restitch.md`](SPEC-kabsch-restitch.md) — Kabsch on overlap Cα →
>   transform tile → existing `winning_tile` stitch. D-125-A implements
>   that Spec; it does not replace the assembler. D-125-B names both
>   paths when A's sibling tree is on disk. ⚠ **Not F-004 ingest.**
> - [`SPEC-overlap-confidence-kabsch.md`](SPEC-overlap-confidence-kabsch.md) —
>   overlap-confidence Kabsch (trimmed + pLDDT-weighted) → existing
>   `winning_tile`. Spec + amendment 1 already on `main`. **D-126-A**
>   implements it as a sibling module (`core/hold48_confidence_kabsch.py`);
>   does not overwrite assembler or D-125 `kabsch/{id}/` /
>   `hold48_kabsch.py`. ⚠ **10.0 Å gate stays.**
> - [`SPEC-piecewise-domain-kabsch.md`](SPEC-piecewise-domain-kabsch.md) —
>   piecewise / domain-aware Kabsch (multi-rigid; no trim) → existing
>   `winning_tile`. Spec already on `main` (`00fa76d` / #243).
>   **D-127-A** implements it as a sibling module
>   (`core/hold48_piecewise_kabsch.py`); does not overwrite assembler
>   or D-125 `kabsch/{id}/` or D-126 `confidence_kabsch/{id}/` /
>   `hold48_kabsch.py` / `hold48_confidence_kabsch.py`.
>   **D-127-B** reads that tree for four-path review-card honesty and
>   shipped the **mandatory** Spec §7 Method addendum (`de9a80e` /
>   #245).
>   ⚠ **10.0 Å gate stays.** ⚠ **Another weight / trim knob is
>   forbidden.**
> - [`SPEC-linker-seam-honesty.md`](SPEC-linker-seam-honesty.md) —
>   linker / seam honesty (**D-128**, already on `main`). §1a makes a
>   per-path / per-seam `max_ca_jump_angstrom` **required**: a path that
>   ends over **10.0 Å** at a seam is **dishonest** for that seam and no
>   success PDB may be presented as honest. §1b's optional repair is
>   **linker-local rigid only** — one weighted Kabsch in a **±32 aa**
>   window (**W = 32**, ε = 1e-3, **no trim loop**, no pieces, no
>   linker-inherit) → existing `winning_tile`. Primary inventory is the
>   **seven** signed must-hunt linker parents (2938, 2939, 3179, 3190,
>   3321, 3368, 3566 — ⚠ **`must-hunt` is what they were called when
>   D-128 was written; the Phase 5 sign has since superseded that name
>   and they are `accept-refuse`, D-129 / D-129-B**).
>   ⚠ **Not piecewise-v2. Not an RMSD Spec
>   (3272 / 3394 out of primary). Not a domain Spec. 3432 stays
>   accept-refuse.** ⚠ **10.0 Å stays — no loosen without Matt.**
>   ⚠ **Never says solved.** **D-128-A** implements it as a fifth
>   sibling module (`core/hold48_linker_seam.py` +
>   `scripts/linker_seam_restitch.py`); it does not overwrite the
>   assembler or `kabsch/` / `confidence_kabsch/` / `piecewise_kabsch/`,
>   and it runs no ops. **D-128-B** already shipped on `main`
>   (`cd071d7` / #248): it **reads** that tree for five-path
>   review-card honesty — one row per `(path, seam)`, never an
>   average — and ships the **mandatory** Spec §7 Method addendum,
>   including the **D-128 OPS result as recorded** (PASS 0 / REFUSE 7 /
>   FAIL 0; `repaired_of_seven` = 0; `seam_jump_gt_10` ×6 / `rmsd_gt_10`
>   ×1; give-back 5 vs D-125 and 6 vs D-126). ⚠ **That PR ran no ops and
>   re-measured nothing.** ⚠ **§3 / §9 now carry the D-129 Phase 5
>   cross-link:** after the SIGNED Phase 5 sign the **seven are
>   `accept-refuse`, no longer must-hunt** — a **label** change only;
>   §1a / §1b / §2 / §5 / §11 stand exactly as shipped and the seams are
>   still **not solved**.
> - [`SPEC-phase5-named-refuse.md`](SPEC-phase5-named-refuse.md) —
>   Phase 5 named-refuse (**D-129**, **this PR**). ⚠ **Authority over
>   LABELS, not algorithms** — it changes no geometry, no threshold, no
>   artifact tree, and no served byte. **Eight** parents are
>   **`accept-refuse`** (the recorded honest outcome of a refusal,
>   closed to further hunting): **2938, 2939, 3179, 3190, 3321, 3368,
>   3566** (the D-128 linker seven) **+ 3432** (already accept-refuse,
>   **unchanged**). A surface labels them **named refuse** and **never**
>   **open must-hunt**, **solved / fixed / repaired**, or **a D-128
>   miss** — **0-of-7 was pre-registered** as allowed. ⚠ **`accept-refuse`
>   ≠ Method silence:** the D-128 OPS **0 of 7** and its named give-back
>   (**5** vs D-125, **6** vs D-126) — already disclosed by D-128-B —
>   become a **standing** obligation and may never be softened, dropped,
>   or split apart. ⚠ **The Method D-128-B shipped still calls the seven
>   `must-hunt`**; that re-label is owed to a later Method / UI PR, not
>   to this docs Spec PR. ⚠ **3272 / 3394 stay Phase 4 must-hunt** —
>   **separate Matt GO**, no RMSD Spec bleed. ⚠ **No linker-v2**; the
>   stitch family **freezes** (served = **assembler**, **no auto-flip**,
>   **no F-004**, **10.0 Å** / W = 32 / ε = 1e-3 stay, **D-126 remains
>   best experimental until proven otherwise**, **both** failed rescues
>   stay disclosed). ⚠ **Never says solved.** ⚠ **§6 now carries the
>   D-130 Phase 4 cross-link:** the **separate Matt GO** that section
>   required has **arrived**, so 3272 / 3394 are still **Phase 4
>   must-hunt** but the hunt is now **Spec-governed** — they are still
>   **not** `accept-refuse`, the eight are unchanged, §4's disclosure
>   stays standing, and §7's freeze is **not repealed**.
> - [`SPEC-residual-rmsd-hunt.md`](SPEC-residual-rmsd-hunt.md) —
>   Phase 4 residual-RMSD hunt (**D-130**, already on `main`, `854c2ab` /
>   #252). **Algorithm authority** for **D-130-A**, which is **this PR**
>   and implements §1a / §1b / §2 / §3 / §5 / §11 as a sixth sibling
>   module (`core/hold48_residual_rmsd.py` +
>   `scripts/residual_rmsd_restitch.py`); it overwrites none of the five
>   earlier trees, edits no `hold48_*.py`, ships no UI and no Method
>   edit, and **runs no ops**. ⚠ **Single failure mode:
>   residual RMSD** (the `rmsd_gt_10` whole-overlap class). ⚠ **Two
>   parents only: 3272** `Q6V0I7` **/ 3394** `Q8TDW7` — both **Phase 4
>   must-hunt**, both out of the D-128 OPS seven. ⚠ **NOT a linker
>   Spec, NOT a domain-partition Spec, NOT both, NOT a kitchen sink.**
>   §1a's **required** half decomposes the residual: per `(path, seam)`
>   it records the achieved full-overlap RMSD beside the
>   rigid-invariant internal **dRMSD** and the **proved floor**
>   `dRMSD / 2` under *every* rigid transform, classing the row
>   `irreducible` / `placement` / `unknown`. ⚠ **The floor is
>   one-directional:** over **10.0 Å** it *certifies* that no rigid
>   move can pass; under it, it **proves nothing** and is never a
>   recovery forecast or an argument to loosen a gate. §1b's optional
>   recovery is a **residue-identity correspondence audit** followed by
>   **D-125's fit unchanged** (unweighted, untrimmed, full overlap) —
>   **no trim** (the D-126 lie surface, which hid a 28–68 Å gap on
>   **3272**), **no weights, no pieces, no window, no linker-inherit**.
>   ⚠ **`recovered_of_two` = 0 is PRE-REGISTERED as allowed**, and a
>   **named refuse after a failed hunt** is a complete outcome.
>   Sixth sibling tree `residual_rmsd/{parent}/` +
>   `core/hold48_residual_rmsd.py` — colliding with no earlier tree or
>   module. ⚠ **The eight stay `accept-refuse`; Phase 5 is not
>   reopened.** ⚠ **10.0 Å stays. Served stays assembler. No F-004, no
>   auto-flip. D-126 remains best experimental and callable. Never
>   solved — and never solved without measurement.** ⚠ **D-130-A ships
>   the code and NOT the claim:** the §1a decomposition is written for
>   every seam and every path, `recovered_of_two` = 0 stays an allowed
>   outcome, and **D-130-B** (UI + Method §7) is still owed before D-130
>   is "done".
> - [`method-hold48-tiles.md`](method-hold48-tiles.md) — owner-facing 8th-grade write-up
>   of hold-48 tiles / overlap-as-glue / winner-tile assembler (**D-121**) plus a
>   D-125-B addendum (what Kabsch does / does not), a D-126-B addendum
>   (what weighted / trimmed Kabsch does / does not vs assembler vs
>   D-125), a **D-127-B** addendum (the four-step stitch-path train
>   assembler → D-125 → D-126 → D-127; per-domain pieces; linker
>   inherit; the refuse table; **10.0 Å stays**), and a **D-128-B**
>   addendum (the **five**-step train with linker / seam honesty; what
>   **dishonest** means about a structure file; the refuse table;
>   **never solved**; **3432 accept-refuse**; and the **D-128 OPS
>   result as recorded** — PASS 0 / REFUSE 7 / FAIL 0 with its named
>   give-back). Additive MethodNote
>   sections on `/method`. ⚠ **Assembler remains the default served
>   PDB. #229 stays merged.** ⚠ **D-129 does NOT edit this file** — its
>   §5 carries the required 8th-grade copy as **authority** only. That
>   addendum still calls the seven **must-hunt**; after the Phase 5 sign
>   they are **`accept-refuse` / named refuse**, so a later Method / UI
>   PR owes that re-label. ⚠ **The D-128 OPS disclosure already here
>   must stay** — D-129 makes it **standing**, never softened or
>   dropped.
> - [`decisions.md`](decisions.md) — thin **ship index** (which id ships which work).
>   **D-124 ships** ADC-C: **A** (pipeline catalog + access/RTT payload +
>   thin read API) already on `main` (`b71bade` / #235); **B** already on
>   `main` (`57f429d` / #236). **D-125 ships** the Kabsch restitch Spec
>   (already on `main`, `fbe8978` / #234) **and D-125-A** (already on
>   `main`, `26a40a8` / #237: core Kabsch + refuse + feed `winning_tile`;
>   sibling `kabsch/{parent}/` tree). **D-125-B** already shipped UI
>   dual-path honesty on `main` (`aa8d3f1` / #238). **D-126 ships** the
>   overlap-confidence Kabsch Spec (already on `main`, `d59be6b` / #239
>   + amendment 1 `b32f9db` / #240). **D-126-A** already shipped the
>   core BUILD on `main` (`aa8aa02` / #241). **D-126-B** already
>   shipped UI triple-path honesty on `main` (`abbcd00` / #242).
>   **D-127 ships** the piecewise / domain-aware Kabsch Spec
>   (already on `main`, `00fa76d` / #243). **D-127-A** already
>   shipped the core BUILD on `main` (`e49bf34` / #244).
>   **D-127-B** already shipped UI four-path honesty **and** the
>   mandatory Spec §7 Method addendum on `main` (`de9a80e` / #245).
>   **D-128 ships** the linker / seam honesty Spec (already on `main`,
>   `2004c5a` / #246) —
>   [`SPEC-linker-seam-honesty.md`](SPEC-linker-seam-honesty.md).
>   **D-128-A** already shipped the core BUILD on `main` (`9e65cbf` /
>   #247); **D-128-B** already shipped UI five-path honesty **and** the
>   mandatory Spec §7 Method addendum on `main` (`cd071d7` / #248).
>   **D-129 ships** the Phase 5 named-refuse Spec (already on `main`,
>   `1baf4c0` / #249) —
>   [`SPEC-phase5-named-refuse.md`](SPEC-phase5-named-refuse.md): the
>   **eight** parents are **`accept-refuse`**, the D-128 OPS **0 of 7**
>   disclosure is **standing**, **3272 / 3394** stay **Phase 4
>   must-hunt**, and there is **no linker-v2**. **D-129-B** shipped
>   those labels on `main` (`cbcb47d` / #250) and **D-129-C** the hygiene
>   patch that stops the eight's retired name standing bare (`544e821` /
>   #251). **D-130 ships** the
>   Phase 4 residual-RMSD Spec (already on `main`, `854c2ab` / #252);
>   **D-130-A** ships its core BUILD — **this PR** — and **D-130-B**
>   (UI + Method §7) is still owed. **D-121 ships** the
>   Method hold-48 8th-grade explainer. **D-123 ships** the Nectin-4/ADC
>   Doc follow-on on `/about` (already on `main`, `2ffd4f8` / #231).
>   **D-122 ships** ADC-B (`/adcs` UI) on `main` (`86f8a10` / #232).
>   **D-119 ships** ADC-A. **D-120 ships** Phase 2 review UI; parent PLAN
>   is **D-117**; parent honesty GO is **D-118**. Not a second living log
>   — authoritative `### D-NNN` entries stay in this file.
> - [`../data/adcs/README.md`](../data/adcs/README.md) — ADC-A v1 catalog hook
>   (**D-119**). ADC-B pages consume it (**D-122**). **D-124 / ADC-C-A** adds
>   sibling files `adcs.pipeline.v1.json` + `access.v1.json` — not merged into
>   `adcs.v1.json`. **D-124 / ADC-C-B** consumes those siblings on `/adcs`.
>   **D-136** fills the Approved **Cancer type** column from openFDA
>   `label.json` §1 INDICATIONS AND USAGE (a `reviewed` tumour-type list beside
>   the `official` verbatim text it was reduced from, audited by substring; a
>   third date `indications_reviewed_as_of`; ⚠ never an HPA / staining join,
>   D-093). Weekly Drugs@FDA watch is Emma's ops lane; not built here.
> - The planning docs in this folder (TDD, DB plan, UI plan, test plan, checklist) — the
>   *original* intent. Where a decision below diverges from them, **this log wins**.

## How to add a decision

> **Numbering note: there is no D-010.** The sequence runs D-001…D-009 then D-011. Nothing was
> deleted — the number was simply skipped. Not renumbered, because commit `c07b95b` already
> references D-011 by name. Spike entries use `S-NNN` and instrument/method findings use `F-NNN`.

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
5. **Before using a metric as a *leading indicator*, verify its events actually PRECEDE the thing
   it predicts.** (Added 2026-07-19 after **F-001**.) WHEA corrected-error rate was used for hours
   as an early-warning signal for host crashes; per-second timestamps then showed the fatal is
   logged *in the same second* as the corrected errors, and that six burst days with 65/40/31
   corrected errors produced **zero** crashes. The metric was **anti-correlated** with its target.
   A metric can be real, well-defined, correctly queried — and still measure the *aftermath* of the
   event you meant to predict. **Check the time-ordering, not just the correlation.**
6. **Prefer the instrument-free comparison when one exists.** The strongest result in this whole
   investigation needs no event log at all: *4 crashes in 4 HER2 attempts, 0 in ~93 Trop-2 folds.*
   When a raw outcome count is available, it outranks any derived telemetry.

7. **⚠ A POINTER IS NOT PROOF OF ITS TARGET — and the sharpest case is the record pointing at itself.**
   (Added 2026-08-03 after **D-062**.) This project keeps re-learning one shape in different clothes:
   a *reference* to a thing is taken as evidence the thing exists and is sound.
   - **A green check is not a working system** — the gate proves the tests it has, not the behaviour.
   - **A summary is not the records** — `params_all_on_cuda=True` was true and missed spill;
     *"217 WHEA events"* was true and missed severity (S-001/S-002).
   - **A hash from an hour ago is not the file now** — re-verify immediately before a destructive act.
   - **A filename is not an identity** — a basename match nearly overwrote the 605 KB decision log with
     an unrelated project's `README.md`.
   - **A cited path is not a tracked file** — `intersection_check.py` was cited as provenance from a
     path that did not exist (D-073/D-074).
   - **⚠ AND: a commit message naming a decision is NOT evidence the decision was logged.** PR #90 was
     titled *"F-004 + D-062: … the scorer surface that renders it"*, and its diff added `### F-004` and
     **no `### D-062`**. Thirteen later citations then referred to D-062 as settled authority. **The
     record referred to itself into a false sense of completeness** — the most dangerous member of this
     family, because every other item is a pointer from outside the log into the world, where reality
     eventually pushes back, while this one is a pointer from the log into the log, where nothing does.
   - **The general rule: to confirm a thing exists, look at the thing — never at a reference to it.**
     For log entries that is one command: every cited `D-NNN`/`F-NNN` must have a matching `### ` entry.

   **⚠ STATE OF THE INVARIANT — do not assume it has always held.** As of **2026-08-04** every cited
   `D-NNN`/`F-NNN`/`S-NNN`/`DEP-NNN` in this log and in `ARCHITECTURE.md` either resolves to a real
   `### ` entry **or is listed in [`RESERVED.md`](RESERVED.md)**.

   **The distinction the register exists to hold.** A *forward* reference to an entry that announces
   its own absence is not the D-062 defect — D-062's harm was that thirteen citations treated a missing
   entry as **settled authority**, and nothing in the text suggested it was missing. A reference that
   says *"this is not written yet"* cannot do that. **But it is indistinguishable from the defect to a
   checker.**

   **That is why the exceptions are a file and not a paragraph.** This note first carried them as prose
   — one exception (`D-010`), then two (`D-078`), and within a day the set was five. Prose kept the
   property *"an undocumented miss is a real finding"* true only while the set was small enough to
   remember; `RESERVED.md` keeps it true as the set grows. **The checker whitelists that file and
   nothing else, and an unresolved reference not listed there is a finding immediately** — same class
   as D-062, found early. The command is in the register; **read its output, not its exit code.**

   **This closed state was RESTORED on that date; it did not hold before it.** Two holes were repaired
   the same day: **D-062**, cited **13 times** as the authority for a shipped surface with no entry
   (back-filled from artefacts and permanently marked as such), and **F-009**, cited by shipped UI and
   by `ARCHITECTURE.md` while existing only as a staged document (landed from that document, so sourced
   rather than reconstructed). **Both had accumulated citations for days without anything objecting** —
   which is the asymmetry above in practice.

   **What a future session should take from this:** the invariant is *maintained*, not *guaranteed*.
   Nothing in the gate enforces it — the check is deliberately **named, not built** (D-074 dec 3: do
   not answer a finding with a framework that becomes a second thing to drift). So **re-run it rather
   than trusting this paragraph** — which is itself only a pointer, and therefore not proof of its own
   target. Running it is one command; it found two holes the first time it was run.

---

## Method note: a guard that is already red reports nothing, and a baseline diff over failure NAMES cannot see it

Learned on 2026-09-11, from **four instances in one session — three found in the code by READING,
one caught in the WRITING, and none by running.** ⚠ The common property is not that the guards were
wrong. It is that **each could not fail in the direction it claimed to protect**, so each was
structurally incapable of reporting the defect it existed for.

**⚠⚠ THE METHOD DEFECT, STATED FIRST, BECAUSE IT IS THE REUSABLE PART.**

A regression check of the shape *"run the suite on this branch, diff the failing test NAMES against
a baseline, treat the difference as my regressions"* is **not a regression check.**

> **It cannot distinguish *fails for the same reason* from *fails for a NEW reason*.** A test that
> was already red absorbs a new defect silently, and the diff comes back empty.

That is how instance 1 below reached CI: the guard was **red on the developer's platform and green
on CI's**, so it sat in the "pre-existing failures" bucket of exactly such a diff, and a real
regression hid inside it. ⚠ **It is `F-034`'s shape turned on the harness** — *the verification would
have triggered the failure it was built to verify against.*

**The three instances.**

1. **`tests/test_d143_track_b_structural_only.py` — platform-divergent, always.** It pinned the exact
   list of files permitted to carry a retired string, building that list with
   `str(path.relative_to(ROOT))`. On Windows that yields `docs\decisions.md`; the expected values
   are `/`-separated. ⚠ **The assertion could never pass on one platform and never fail on the other.**
   When `D-156` moved the entries out of `docs/README.md`, the carrier changed — and **only CI saw
   it.** Fixed by `as_posix()` **and** by correcting the carrier; both landed at `ffea42e`.

2. **`tests/test_census_accession_route.py` — every assertion textual.** The file exists for exactly
   one behaviour: an accession present in **both** populations must resolve to its **census** row
   (`D-081`), and a cohort-only accession must be refused rather than served. Every assertion read
   source text — `'"cohort"' in src`, `"D-081" in src`, and `callable(resolve_census_accession)`,
   which asserts the function **exists** and never what it **returns**. ⚠ **Not one called the
   resolver.** `F-054` verbatim, sitting on top of behaviour that happens to be correct.
   ⚠⚠ **Proven, not argued:** removing the population filter from `resolve_census_accession` — the
   realistic mistake — makes it serve the **cohort** row (id 4 where census id 2027 is correct), and
   **all seven string assertions stay GREEN.**

3. **A `@pytest.mark.parametrize` whose parameters are never used.** In the same file,
   `test_the_resolver_normalises_what_a_person_actually_pastes` is parametrised over two accessions
   and **uses neither** — both cases run identical source-text assertions. ⚠ **The parametrisation is
   decorative**, and a reader counting cases would credit it with coverage it does not have.

4. ⚠⚠ **A FOURTH, AND IT IS THE ONLY ONE THAT NEVER SHIPPED — because this note already existed.**
   Task 2's repair added `pae_post_fn` to the local fold path, and the danger was not the unit but
   the **wiring**: every unit test passes while `run()` never hands the route to the fold path,
   leaving a correct function production never calls — `F-054`'s shape exactly. The first guard
   written for it asserted
   `"pae_post_fn=client.persist_pae" in inspect.getsource(worker_main.run)`.
   ⚠ **That is instance 2's defect, hours after instance 2 was written up here.** It was replaced
   before commit with a behavioural guard that captures the callable `run()` hands the loop and
   invokes it, and the replacement was **proven by revert**: removing the wiring reddens it at the
   assertion.

   > ⚠ **Recorded as an instance rather than quietly fixed, because it is the only evidence here
   > about whether writing this down changes anything.** Three were found in code by reading.
   > **This one was caught in the writing, by a author who had just written the note** — which is
   > the weakest possible test of the note and still the only one available. ⚠ **It says nothing
   > about whether the habit survives the week.**

**⚠ What follows, and what deliberately does not.**

- **Prefer the check that can fail.** Before trusting a guard, ask what change would make it red —
  and if the honest answer is *"none that matter"*, it is documentation with an `assert` in it.
- **A baseline diff must compare failure CAUSES, not names** — or be treated as what it is: a
  smoke test that a branch did not make things obviously worse.
- ⚠ **`A-017` clause (c) is the same rule one level down:** *the fixture must contain a case where
  correct and incorrect differ.* Instances 2 and 3 are that clause failing at file scope rather than
  at fixture scope.
- ⚠⚠ **NO FRAMEWORK IS BUILT FOR THIS, AND THAT IS A DECISION** (`D-074` decision 3 — *do not answer
  a finding with a framework that becomes a second thing to drift*). This note is the remedy.

**⚠ `F-050`'s status, stated because these three bear on it.** **`F-050` is RESERVED for the
guard-direction sweep — the audit of whether each guard fails in the direction it claims to protect
— and it is STILL UNWRITTEN.** It has been reserved since 2026-08-06 and deliberately not taken.

> ⚠⚠ **Four unbidden instances in one session is evidence FOR that sweep.** None was found by
> looking for it; each surfaced while doing something else. **That is the argument for a sweep and
> also the reason to distrust the count** — an unbidden sample is drawn from what happened to be
> read, so **four is a floor, never a rate, and the denominator is unknown.**
>
> ⚠ **And the four are not one population.** Instances 1–3 are guards that **shipped and ran red
> or vacuous for weeks**; instance 4 **never shipped**. A sweep would find the first kind and can
> never find the second. **Counting them together overstates what a sweep would recover** — the
> sweep's real target is three.

⚠ **The sweep is NOT started here**, and this note does not authorise it. It records the count, the
three instances, and the fact that the reserved integer still resolves to nothing.

## Log (newest first)

> ⚠⚠ **THE ENTRIES HAVE MOVED (`D-156`, 2026-09-11).** This README keeps the **rules**, the
> **method notes**, the **template** and the **open questions**. The entries themselves now live
> in the five KEEL documents:
>
> | document | holds | question it answers |
> |---|---|---|
> | [`decisions.md`](decisions.md) | `### D-NNN` | *Why is it like this?* |
> | [`findings.md`](findings.md) | `### F-NNN` | *How do we know?* |
> | [`assumptions.md`](assumptions.md) | `### A-NNN` | *What are we taking for granted?* |
> | [`../ARCHITECTURE.md`](../ARCHITECTURE.md) | the current-state shape | *What am I looking at?* |
> | [`Test_Plan.md`](Test_Plan.md) | the guards | *What would catch it if it broke?* |
>
> **The allocator is [`RESERVED.md`](RESERVED.md)** — it holds the next free `D-`, `F-` and `A-`
> integer, and **the pointer moves in the SAME commit that spends one.**
>
> ⚠ **Residual, stated rather than hidden:** the `S-` (spike) and `DEP-` (deprecation) entries
> are **not** part of the KEEL five and did not move. They remain below.


### DEP-006 — The serving image gains a build stage and a static-serve path

- **Date:** 2026-07-23
- **Status:** Proposed → Accepted on merge with the bundle.
- **Amends:** DEP-001 (*"what the Fly image contains, and what it must never contain"*), whose
  own consequence named this: *"When Streamlit lands, both this entry and the image change
  together"* — now React per D-033, which said the same: *"A React UI adds a build step (bundle)
  and a static-serve path, which is a DEP-001 amendment at that time."*
- **Context:** The image today is single-stage: `python:3.11-slim`, `requirements.lock` with
  `--require-hashes`, then `COPY app/ core/ db/`. A React bundle needs Node at **build** time and
  nothing at **run** time — a distinction the image must express, or the CUDA-free serving tier
  acquires a JS toolchain it never executes.

- **Decision — a two-stage build; the runtime stage stays exactly as ruled.**
  1. **Stage 1 (`node:20-slim`, build only):** `COPY ui/package.json ui/package-lock.json`,
     `npm ci`, `COPY ui/`, `npm run build` → static assets.
  2. **Stage 2 (`python:3.11-slim`, the runtime):** unchanged in every respect DEP-001 ruled —
     runtime lock with `--require-hashes`, `app/` + `core/` + `db/`, **no `worker/`, no torch** —
     plus `COPY --from=0` of the built assets only.

  **Node never enters the runtime image.** The built assets are static files; the serving tier
  remains Python + the hash-locked runtime lock.

- **Serving the bundle:** FastAPI mounts the static directory and serves `index.html` as the
  SPA fallback. **`/api` and `/jobs` are matched first** — a catch-all that swallowed `/api`
  would break the read API silently, so route ordering is the thing to assert, not eyeball.

- **⚠ Three constraints in the existing tree that this must not break** (verified, not assumed):
  - **`tests/test_image_contents.py` forbids the literal strings** `torch`, `transformers`,
    `bitsandbytes`, **and `streamlit`** anywhere in the Dockerfile's non-comment lines. React is
    none of these, so the test passes unchanged — **and it must keep passing unchanged.** Do not
    weaken it to accommodate the build stage.
  - **`test_copies_the_serving_packages`** asserts `copy app`, `copy core`, `copy db` are
    present. The two-stage rewrite must keep all three in the runtime stage.
  - **`.dockerignore` excludes `tests/`, `docs/`, `scripts/`, `worker/`.** A new `ui/` directory
    must **not** be added to it (stage 1 needs it), but `ui/node_modules/` and `ui/dist/`
    **must** be, or the build context balloons.

- **Test surface:** extend `test_image_contents.py` — the runtime stage still copies
  `app`/`core`/`db`; **no `npm` or `node` instruction appears after the runtime `FROM`**; the
  forbidden-string set is unchanged and still passes. Plus a route-ordering test: `GET /api/analyses`
  returns the API's JSON, **not** `index.html`.

- **Deep-learning justification:** indirect — the same separation-of-worlds DEP-001 exists to
  enforce, one tier out. A serving image that acquired a JS runtime it never executes is the
  same invisible-bloat failure as one that acquired CUDA.

- **Consequences:** DEP-004's meaning changes on this merge — **a green deploy will finally mean
  a UI is reachable**, which it has never meant before. That is DEP-004's own stated trigger
  (*"the first UI to ship amends what a green deploy means"*) and it is amended in the same PR.

---

### DEP-005 — Applying the production schema: supervised first, automated after
- **Date:** 2026-07-22
- **Status:** **Accepted (2026-07-22)** — owner-ruled via the deployment-arc orders (the Planner's
  draft was Proposed; these orders enact it: the corrections below, the phase-1/phase-2 split, and
  the verification surface).
- **Context — the gap the Builder surfaced rather than guessed past.** DEP-004 rules that a
  green deploy means *"the transport API is up and the queue is accepting work."* **That is
  false until the schema exists on the Fly database.** Nothing in DEP-001…004 says how
  `alembic upgrade head` runs against production, and the Builder deliberately did **not** add a
  `fly.toml` `release_command` for it, on the grounds that it touches the prod database and
  belongs in a decision. Correct call: this entry exists because of it.

  **Provenance (D-016):** ruled against `db/migrations/env.py`, `db/migrations/versions/`, and
  D-012 §5a / D-017 / D-019, read from the tree at `6792c21`. The Planner has **not** seen the
  `Dockerfile`, `fly.toml`, or deploy-job body built in PR #48 — those are Builder-reported, and
  the `release_command` wiring below must be checked against the actual `fly.toml` before it
  lands.

---

- **Why this is not a routine migration, stated before the ruling.** The chain is two
  migrations, and `0002` is not ordinary DDL:

  ```
  0001_create_jobs.py
  0002_protein_analyses.py   ← creates the extensions schema, the vector extension,
                                and analysis_embeddings (embedding vector(384))
  ```

  `0002` runs `CREATE SCHEMA IF NOT EXISTS extensions`, `CREATE EXTENSION IF NOT EXISTS vector
  SCHEMA extensions`, and then a **bare `vector(384)`** column that resolves only through
  `env.py`'s `SET search_path TO public, extensions` (D-012 §5a). So the first production
  migration is simultaneously:

  1. the first time the **migration chain** runs against the Fly MPG cluster (D-014);
  2. the first time `CREATE EXTENSION vector` is issued **on production**, where the role's
     privileges are the Fly cluster's, not CI's;
  3. the first time the `search_path` seam resolves a bare `vector` type **outside CI**.

  **Correction to a claim carried in this project's own hazard notes:** the `postgres` CI job
  uses a **pgvector image** (D-019), not stock `postgres:16` as
  `docs/HAZARD-search-path-seams.md` and D-032 both state. Seam 2 is therefore *better* covered
  than those documents say — the extension path is exercised in CI. **What CI still cannot
  prove is production role privileges on a managed cluster.** `CREATE EXTENSION` commonly
  requires elevated rights; if the Fly database role lacks them, this migration fails on the
  first run and only on production. That is the specific reason to watch it. *(Both documents are
  corrected in this same change.)*

---

- **Decision — two phases, and they compose:**

  **Phase 1 — the initial migration is run BY HAND, supervised, BEFORE the first deploy.**
  Not by `release_command`, not by the deploy job. The owner runs `alembic upgrade head`
  against the Fly database once, watches it, and confirms the schema exists.

  **Why supervised for the first run, specifically:** every item in the list above is
  first-time-on-prod, and a `release_command` failure surfaces as a deploy log to parse after
  the fact. A hand-run surfaces as an error message in front of a person who can act on it. The
  asymmetry is stark and one-directional — supervising costs five minutes; debugging a failed
  automated migration against a half-applied prod schema costs an evening, and it happens with
  the deploy already in flight.

  **Phase 2 — a `release_command` in `fly.toml` for steady state, ruled but wired AFTER
  phase 1 succeeds.** Once the schema is known-good and the app has come up clean, migrations
  become automatic and versioned with the deploy: Fly runs the release command in a one-off
  machine before the new version goes live, so **a failed migration aborts the release rather
  than shipping code against a schema that never applied.** That property is worth having, and
  it is why phase 2 is ruled now rather than left open.

  **The order is the substance of this entry.** Automating first would mean the riskiest
  migration in the project's history runs unattended; hand-running forever would mean "did prod
  get migrated" is a question rather than a guarantee. Supervised-then-automated gets both.

- **⚠ The merge that lands the deploy job must NOT precede phase 1.** DEP-004's promise —
  a green deploy means the queue accepts work — is only true once the tables exist. Merging
  first produces a green deploy over an empty database: **the transport would be up and every
  write would fail**, which is exactly the over-read DEP-004 was written to prevent, arriving by
  a different route.

---

- **Test surface / verification (what "phase 1 succeeded" means, so it is checkable rather
  than felt):**
  - `alembic current` against the Fly database reports **head** (`0002`).
  - The `extensions` schema exists and the `vector` extension is installed in it.
  - `analysis_embeddings` exists with an `embedding vector(384)` column — i.e. the bare
    `vector(384)` resolved, which is the seam actually being tested.
  - `jobs`, `protein_analyses`, and `ranking_runs` exist with the FK closure D-019 ruled.
  - **If `CREATE EXTENSION` fails on privileges**, that is a result, not a blocker to work
    around: it means the Fly role needs elevation or the extension needs pre-installing by the
    cluster owner, and that fact belongs in this entry as an amendment rather than in a
    workaround.

- **Deep-learning justification:** indirect. `analysis_embeddings` is the vector store the
  scorer's outputs (D-027) will land in. A schema that half-applied, or a `vector` type that
  silently failed to resolve, would surface later as missing data rather than as an error —
  the same invisible-corruption class D-017 and D-032 exist to guard against, one layer out.

- **Consequences / follow-ups:**
  - **`docs/HAZARD-search-path-seams.md` and D-032 both need correcting** on the stock-image
    claim: the `postgres` job uses a pgvector image per D-019. Seam 2's remaining exposure is
    **production role privileges**, not CI coverage. Its named trigger (the first
    `analysis_embeddings` write, downstream of D-027) is unchanged. *(Done in this change.)*
  - **Phase 2's `release_command` is a change to the deploy path**, which sits downstream of two
    required checks — so per D-008 it is proven, not merged on the strength of a passing run.
  - **The provisioning checklist is owner action and precedes everything here:** the app-scoped
    token as the `FLY_API_TOKEN` GitHub secret (DEP-003), `primary_region` matching the MPG
    cluster's region, `DATABASE_URL`, `WORKER_AUTH_TOKEN` matching the worker's, and the
    artifacts volume.

---

### DEP-004 — What a green deploy means, and what it does not
- **Date:** 2026-07-22
- **Status:** **Accepted (2026-07-22)**
- **Series note:** first entries under the `DEP-NNN` prefix — deployment/operations, same log,
  appended at top, monotonic within series (D-002's single-log discipline unchanged). The
  precedent is `S-NNN` for spikes: a prefix that says which arc an entry belongs to, so a reader
  tracing the graded scientific claim can skip `DEP-*` and a reader debugging a deploy can find
  them together. **No deployment TDD** — considered and rejected as disproportionate; the
  coherent picture is D-004 plus these entries.
- **Context:** Deployment is about to produce a green "deploy succeeded" signal on every
  main-push. That signal is easy to over-read, and two facts make the honest reading narrower
  than the word "deployed" implies:
  - **The worker is not deployed** (D-004): `worker/` runs on the local GPU box and is started
    **by hand**. Nothing in the deploy pipeline starts it.
  - **There is no UI yet.** D-004 plans Streamlit as the serving tier's front end, but **it does
    not exist** — verified against the tree at `6792c21`: no `streamlit` dependency, no Streamlit
    code. `app/` is the FastAPI transport only (the four worker→Fly routes from D-031).
- **Decision — a green deploy means exactly this: the transport API is up on Fly and the queue
  is accepting work.** It does **not** mean:
  - that any fold has run, or can run without the owner starting the worker;
  - that a user-facing UI is reachable — there is none to reach;
  - that the full system is "live" in any sense a reader might assume from a green checkmark.

  Stated so the signal is not over-read — by the owner, or by a grader seeing a passing deploy.
- **Deep-learning justification:** neutral — operational honesty, not a model decision. Recorded
  because an over-read green is the deployment-arc version of the failure the whole log guards
  against: a signal that claims more than it demonstrates.
- **Consequences:**
  - When Streamlit is built, it is its own entry and it changes what a green deploy means — at
    which point this entry is amended, not silently outgrown. *(Superseded in part by D-033: the
    UI is React, not Streamlit — but the shape of this consequence is unchanged: the first UI to
    ship amends what a green deploy means.)*

    > **⚠ Amended by DEP-006 (2026-07-23) — this is that merge.** The React bundle now ships in the
    > two-stage image and is served under `/` (`/api` and `/jobs` matched first). **A green deploy
    > therefore now means a UI is reachable** at `pharmfoldmdk.fly.dev`, which it never did before.
    > DEP-004's own stated trigger — *"the first UI to ship amends what a green deploy means"* —
    > fired. A green deploy still does **not** mean any fold has run (that remains an owner action).
  - **Starting the worker on the GPU box is an owner action**, and it is the precondition for the
    first end-to-end fold (the measurement that retires D-030's provisional lease and D-031's PAE
    ratio).

---

### DEP-003 — `FLY_API_TOKEN`: an app-scoped deploy token, not an account token
- **Date:** 2026-07-22
- **Status:** **Accepted (2026-07-22)**
- **Context:** The deploy job authenticates to Fly with a token held as a GitHub Actions secret.
  A GitHub Actions secret is readable by any workflow run on the repo, so its blast radius on
  compromise is the question, not merely its convenience.
- **Decision — an app-scoped deploy token (`fly tokens create deploy`), scoped to
  `pharmfoldmdk` alone.** Not an account/org-wide token.
  - **Rationale, owner's ruling:** there are **four other apps on the account**. An account-wide
    token in CI means a compromised workflow could redeploy or disrupt all five; an app-scoped
    token can touch only this one. The scope cost is nil — the deploy job only ever deploys this
    app — so there is no reason to hold more authority than the job uses.
  - **Rotation is an owner action, not automated.** If the token is rotated or revoked, the
    GitHub secret is updated by hand. No rotation automation is built; naming it here is what
    keeps "who can redeploy prod" an answerable question rather than an assumed one.
- **Deep-learning justification:** neutral — least-privilege on a deploy credential.
- **Consequences:**
  - The token grants deploy on `pharmfoldmdk` only; a second app would need its own.
  - Stored as the `FLY_API_TOKEN` GitHub Actions secret; referenced by the deploy job, never
    echoed.
  - **Owner action, precondition for the first green deploy:** create the token
    (`fly tokens create deploy -a pharmfoldmdk`) and set it as the `FLY_API_TOKEN` repo secret.
    Until it exists, the deploy step authenticates to nothing — the Builder cannot create it
    (it is a credential), and says so rather than stubbing around it.

---

### DEP-002 — The deploy guard lives on the job, never on the trigger
- **Date:** 2026-07-22
- **Status:** **Accepted (2026-07-22)** — forced by D-008; ruled explicitly so the shape is not
  gotten backwards.
- **Context:** `gate.yml`'s own header carries the instruction:
  > *"When real Fly deploy is wired, guard the DEPLOY JOB (not the trigger) against doc-only
  > changes so docs still run tests but don't redeploy."*

  Without a guard, every docs-only PR merged to main would trigger a production deploy. The
  tempting fix — a `paths-ignore` on the workflow — is **the exact thing D-008 removed**, because
  a required status check that does not report on every PR leaves that PR unmergeable forever.
  `test` and `postgres` are both required (D-032); they must run on docs PRs too.
- **Decision — the deploy JOB is conditional on the change not being docs-only; the workflow
  TRIGGER is untouched.** `test` and `postgres` run on every PR and push, as now. The `deploy`
  job additionally checks whether the push changed anything outside `docs/**` and `*.md`, and
  **skips the Fly deploy step when it did not.** Docs still run the full required suite; they
  just do not redeploy.
- **Why this exact split, restated because it is easy to invert:** guarding the *trigger* would
  make the required checks stop reporting on docs PRs → deadlock (D-008). Guarding the *job*
  keeps the checks universal and makes only the *deploy* conditional. The first is a
  reintroduced bug; the second is the fix.
- **Deep-learning justification:** neutral — CI topology.
- **Consequences / test surface:**
  - **Testable, and tested first (project rule):** a docs-only change must not run the deploy
    step; a code change must. The doc-only detection (diff of changed paths against the previous
    main commit, matched against `docs/**` / `*.md`) is the unit under test.
  - The deploy job stays `needs: [test, postgres]` — it cannot run until both required checks are
    green, unchanged from the placeholder.

---

### DEP-001 — What the Fly image contains, and what it must never contain
- **Date:** 2026-07-22
- **Status:** **Accepted (2026-07-22)**
- **Context:** The Fly image serves the transport tier. What goes into it is a decision because
  the failure mode of getting it wrong is silent: an image that includes the worker's CUDA stack
  would be multi-gigabyte, slow to build and deploy, and **would still work** — so nothing would
  flag it. D-004 (worker not deployed) and D-018 (the CUDA stack is a separate, unlocked
  dependency world) both bear on it, and neither is self-enforcing in a Dockerfile.
- **Decision — the image contains the runtime tier and nothing GPU:**
  - **Installs `requirements.lock`** — the hash-locked runtime file (D-013), which as of #47
    carries FastAPI/uvicorn/python-multipart. **Not** `requirements-dev.lock`, **not**
    `worker/requirements.txt`.
  - **Copies `app/` and `core/`.** `app/` is the FastAPI transport; `core/` because the `/claim`
    route calls `core.queue.PostgresJobQueue` (verified in `app/main.py`) and the routes import
    the queue/manifest primitives.
  - **Does NOT copy `worker/`** and **does NOT install any `torch`/`transformers` stack.** The
    worker runs on the GPU box (D-004); its `torch==2.11.0+cu128` build is a CUDA dependency world
    D-018 deliberately keeps out of the locked environment.
  - **No Streamlit** — it does not exist yet (verified against the tree). When it is built, this
    entry is amended to add it and its dependency.
- **Why explicit rather than left to whoever writes the `COPY` lines:** the image-bloat failure
  is invisible (it works), and the correct contents are dictated by two prior entries a Dockerfile
  author might not have in view. Ruling it makes the Dockerfile a transcription of a decision
  rather than a judgement call.
- **Deep-learning justification:** indirect — keeping the CUDA stack out of the serving image is
  the deployment face of D-018's separation, which is what makes the runtime environment a
  function of a committed lock file (D-013) rather than of an unpinned GPU toolchain.
- **Consequences / test surface:**
  - **Assertable and tested first:** the built image (or the Dockerfile's install/copy set) must
    contain no `torch` and no `worker/`. A test/CI check that greps the image or the Dockerfile
    for `torch` guards the invisible failure.
  - When Streamlit lands, both this entry and the image change together. *(Now React, per D-033 —
    a build step + static-serve path, a DEP-001 amendment when the UI is built, not before.)*
  - **Builder note (verified against the import graph at `6792c21`, 2026-07-22):** the COPY list
    above is corrected in two ways the ruling did not trace, **both preserving its intent** (no
    CUDA/worker world in the serving image):
    1. **The image also copies `db/`** (the SQLAlchemy ORM models). `app/artifacts.py` imports
       `db.models`; `db/` is serving-tier with no GPU dependency. DEP-001 under-listed it — an
       image of `app/` + `core/` alone would fail at import.
    2. **`FoldSpec` was relocated to `core/contracts.py`.** `app/artifacts.py` imported it from
       `worker/orchestrator.py`, which would have forced `worker/` into the image **against this
       very ruling**. `FoldSpec` is the claim contract — the route produces it, the loop consumes
       it — tier-neutral by nature; it now lives in `core/` and `worker.orchestrator` **re-exports**
       it, so the loop's tests are unchanged (D-031 rule) and the image ships `app/` + `core/` +
       `db/`, no `worker/`. The image-contents test enforces the "no `worker/`, no torch"
       property, so this correction is self-guarding rather than a promise.

---

### S-005 — bisect the length ceiling at 440 aa
- **Date:** 2026-07-19
- **Status:** **CLOSED 2026-07-19 — 440 aa FOLDED CLEAN (reading 1).** 28.6 s at `chunk 64`,
  peak 6665 MiB (no spill), pLDDT 84.27, 440/440 CA, zero WHEA events, zero bugchecks.
  **⇒ the ceiling is in (440, 630).** Most of the curated ADC set is locally foldable; only
  HER2-class targets (>440 aa) need external compute.
- **Type:** Spike — a single bisection step. **One run, then stop.**

**The bracket.** Length is the discriminator (S-004). The evidence, instrument-free:
- **248 aa (Trop-2): 0 crashes in ~93 folds** — both precisions, spilling and not.
- **630 aa (HER2): 4 crashes in 4 attempts.**

The ceiling lies somewhere in **(248, 630)**. **440 aa is the closest integer to the true midpoint**
(439), so a single run halves the remaining bracket **whichever way it goes** — maximum information
per crash, which matters when each observation costs a host.

**Sequence — hold everything constant except length.** Take the **HER2 ECD (`P04626`, 23–652) and
truncate to its first 440 residues**. Same protein, same amino-acid composition, same code path,
same UniProt-derived source. **Deliberately NOT a different protein at ~440 aa** — that would
reintroduce composition and fold-difficulty as confounds, and this run only has budget for one
variable.

**Configuration:** int8 (S-003 recipe), `chunk_size` 64 descending on OOM, driver 596.72,
GPU process list verified empty, WHEA window recorded from a noted T0.

**Expect JSON corruption on a crash.** S-004's results file was truncated to NUL bytes by the
unflushed mid-write. **That is now the known signature of a host loss, not a surprise or a bug** —
stdout is the surviving record, so read it first.

**THE THREE READINGS — fixed in advance:**

| # | Observation | Reading |
|---|---|---|
| **1** | **Completes clean** | Ceiling is in **(440, 630)**. Most of the curated ADC set is **locally foldable**; only HER2-class targets need external compute. |
| **2** | **Crashes** | Ceiling is in **(248, 440)**. The constraint is **broad**, and external compute does **most** of the cache work. |
| **3** | **Completes, with corrected errors but no fatal** | The **burst-without-crash** pattern seen on six historical days (F-001). **Treat as a PASS.** Interesting, but **uninformative about the ceiling** — corrected errors do not predict crashes. |

**Reading 3 exists because of F-001:** without it, corrected errors during a successful fold would
have been misread as a near-miss or a partial failure. They are neither.

- **Deep-learning justification:** the ceiling determines how much of the curated ADC target
  database the local tier can fold, and therefore how much of the graded DL pipeline runs on
  owned hardware versus rented compute.
- **Stop condition:** **one run.** Do not bisect further tonight regardless of outcome.

---

#### RESULTS (2026-07-19) — **CLOSED. Completed clean. READING 1 fired.**

**HER2 ECD truncated to 440 aa folded successfully on the first attempt.** Host alive; last reboot
remains 19:02:08 (the S-004 crash), i.e. **no new reboot**.

| Measure | Value |
|---|---|
| Chunk | **64** — first attempt, no descent needed |
| Wall time | **28.6 s** |
| Peak VRAM | **6665 MiB**, `spilled = False` (free was 7043 MiB) |
| mean pLDDT | **84.27** *(rescaled ×100 per the scale trap)* |
| CA count | **440 / 440** — exact |
| NaN/inf coords | **0** |
| Radius of gyration | **24.64 Å** (compact-globular reference for N=440 ≈ 22.2 Å) |
| **WHEA in window** | **0 corrected, 0 fatal** (window 19:22:23→19:24:50 contains folds 19:23:49→19:24:17) |
| **Bugchecks** | **0** |

Null verified against a same-day control (78 WHEA events today, last at 19:02:29 — the S-004 crash).
This is **reading 1, not reading 3**: there were no corrected errors at all.

**⇒ THE CEILING IS IN (440, 630).** The bracket is halved. Structure is sane (exact residue count,
no NaN, Rg slightly above the compact-globular estimate as expected for a multi-domain elongated
ECD), and pLDDT 84.27 is **notably higher** than Trop-2's 74.68.

**Product consequence:** **most of the curated ADC target set is locally foldable.** Typical ADC
target ECDs — Trop-2 ~250 aa, Nectin-4 ~350 aa, and now anything up to at least 440 aa — run on this
machine. **Only HER2-class targets (>440 aa) need external compute.** That is a far narrower
constraint than S-004 alone implied.

**⚠ Observation, labelled as inference not measurement — a memory-adjacent reading of the 630 aa
crash.** Peak at 440 aa was **6665 MiB against 7043 MiB free — only 378 MiB of headroom** at
`chunk 64`. Activation memory grows steeply with length, so **630 aa at `chunk 64` would very
plausibly have exceeded free VRAM and spilled during the fold**, even though it did *not* spill at
rest (`resident 5351 MiB`). S-004's peak was **destroyed with the corrupted JSON**, so this cannot
be confirmed. If it is right, **HER2 might still fold at `chunk 16/32`** — the descent existed but
S-004 crashed at `chunk 64` before reaching it. **Not tested; one run was the budget.** This does
not resurrect the spill mechanism generally (the fp16 control showed sustained spill at 248 aa
causes no crash), but it is a live possibility specifically for the 630 aa case.

**Next bisection step if resumed:** ~535 aa, same truncation method.

### S-004 — int8 + HER2 (630 aa), the untested crash condition
- **Date:** 2026-07-19
- **Status:** **CLOSED 2026-07-19 — HOST CRASHED (4th bugcheck, `0x00020001`, 19:02:28).
  Pre-registered READING 4 fired: escalation is not gradual and the corrected-error instrument is
  invalid as a leading indicator.** Duration eliminated as the trigger; **sequence length** is the
  discriminator. See RESULTS and **F-001** below.
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

---

#### RESULTS (2026-07-19) — **CLOSED. The host crashed. Pre-registered READING 4 fired.**

**Outcome: reading 4, not reading 3.** Reading 3 required errors to *"appear but stay corrected"* —
i.e. **no fatal**. A fatal occurred, and the corrected errors arrived **in the same second as the
fatal, not before it**. That is reading 4 verbatim: *"host crashes with no prior corrected errors →
neither story is complete; escalation is not gradual."* **The reading that neither hypothesis
anticipated is the one that fired** — which is precisely what pre-registering it was for.

**Fourth crash of the day, same signature:**

| # | Bugcheck | Code |
|---|---|---|
| 1 | 16:32:32 | `0x00020001` |
| 2 | 16:44:44 | `0x00020001` |
| 3 | 16:48:15 | `0x00020001` |
| **4** | **19:02:28** | **`0x00020001`** |

**What S-004 got before it died** (stdout survived; the results JSON was **corrupted to NUL bytes** —
an unflushed mid-write file, itself a signature of abrupt power loss rather than clean exit):

| | Value |
|---|---|
| Run start | 19:01:17 |
| Config | **int8**, `resident 5351 MiB`, **`spills_at_rest = False`** |
| Target | HER2 ECD `(23, 652)`, **630 aa** |
| **Chunk size** | **64** — the *first* attempt; it never reached the descent to 32/16/8 |
| **Peak VRAM** | **UNKNOWN — the record was destroyed by the crash.** No `OK` line was ever printed. |
| **Time into the fold** | **≈56 s** (fold began ≈19:01:32 after load; bugcheck 19:02:28) |
| PDB saved | none — no fold completed |

**Driver 596.72 and LM Studio are ELIMINATED as explanations** — the crash reproduced with the new
driver installed and with the GPU compute-process list verified empty at T0.

**⭐ Duration is NOT the trigger — sequence length is.** This is the one open mechanism question, and
the data now answers it:
- The **fp16 Trop-2 control** ran **five individual folds of 73.4–74.1 s each** — and **did not crash**.
- **S-004 crashed ≈56 s into a single fold** — *shorter* than folds the machine had just tolerated
  five times in a row.

**A shorter fold killed it while longer folds survived.** Single-fold duration up to ~74 s is
tolerated, so duration is eliminated. What differs is **sequence length / activation geometry**
(630 aa vs 248 aa). Spill is eliminated too: int8 does not spill at rest, and it crashed anyway.

**Cache-path verdict:** **FAIL** — but *not* on the two-cap latency criterion. It never produced a
structure at any chunk size, because the host died mid-fold. The two-cap amendment (which would have
scored a slow `chunk 16` fold as a PASS) never got the chance to apply.

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

> ⚠ **Restated by F-001: true, but largely irrelevant.** This is **not** a steadily degrading link.
> It is a fault that **fires in bursts and usually recovers** — six of those seven days produced
> **zero** fatals (including 65 corrected on 06-09 with no crash). Corrected-error history says
> almost nothing about crash risk. The **18:04 / 18:06** events attributed above to the driver
> install **may equally have been a spontaneous burst — now unknowable, recorded as unknowable.**

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

> ⛔ **VOID — see F-001 (instrument correction).** The corrected-error comparison below measures
> **crash debris, not precursors**: the fatal is logged in the *same second* as the corrected errors
> in all four crashes, and six historical burst days produced 65/40/31 corrected errors with **zero**
> fatals. *"65 corrected in the crashing window vs 0 in clean runs"* is **three crash events versus
> zero, double-counted.* **The valid measure was always the fatal count: 4 vs 0.** Text retained
> for provenance.

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

> ⚠ **Restated by F-001:** this arm's "zero corrected errors" reduces to **"no crash"**, which host
> survival already established independently. **The refutation below still stands — but on the
> fatal count, not the corrected count.** S-004 later strengthened it: HER2 crashed at int8 with
> **no spill at rest**, eliminating spill again by a different route.

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

## Open questions awaiting a decision entry

These are known forks in the road. Each becomes a `D-NNN` entry **before** we act on it.

- ~~**DL core for Iteration 1**~~ — **resolved in D-003: run ESMFold ourselves.**
- ~~**Where inference runs + Fly compute**~~ — **resolved in D-004: local GPU worker,
  pull-based; Fly serving tier has no GPU.**
- ~~**Sequence-length cap / domain selection**~~ and ~~**pre-compute & cache pipeline**~~ —
  **resolved in D-006** (fp16 + `chunk_size` + extracellular-domain fold + 400-residue live
  cap + OOM degradation + offline pre-compute). Caps still need empirical validation.
- **Worker ↔ app contract:** job schema, claim/lease semantics, artifact upload, auth token.
- ~~**Prod DB choice**~~ — **resolved in D-012: Postgres-first**, from the first migration;
  the SQLite-on-Volume prototype path is closed, not deferred. The **test** DB remains SQLite
  per D-005, which D-012 §3–§5 turns from a footnote into a named, structural exposure.
- **Embedding model** for semantic search (which encoder, `vector(384)` assumed).
- ~~**Postgres integration test job**~~ — **BUILT in D-017.** The `postgres` CI job stands up a
  real Postgres 16 service container, applies migrations with `alembic upgrade head` (not
  `create_all`), and exercises `claim`'s `FOR UPDATE SKIP LOCKED` atomicity for the first time.
  What was "the single largest coverage hole" is closed. **Residual, narrower:** the job is not
  *yet* a branch-protection required check (owner action, deferred until proven stable — D-017),
  and pgvector **type resolution** through the `extensions` schema is still unexercised (no vector
  column yet; the job switches to a pgvector image when the first vector-column migration lands).
- **pgvector `extensions`-schema resolution** — a `vector(384)` column actually resolving via
  env.py's `search_path` seam, against a populated `extensions` schema, on real PG. Deferred to
  the first vector-column migration (D-017 residual; env.py seam already in place, D-012 §5a).
