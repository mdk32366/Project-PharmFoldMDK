# Orders for Code — D-075: the confidence-blind proxy ablation + popularity-matched control (extends D-065)

> **⚠ PRIORITY: this is TIER 0. It is the fork the roadmap turns on.** But it does **not** start
> until its prerequisites are confirmed (§0). **Scope:** `core/scorer.py`, `core/features.py`
> (proxy only), `scripts/fit_scorer.py`, `scripts/attention_control.py` (new), `tests/`,
> `docs/README.md`, `ARCHITECTURE.md`.
> **NOT in this PR:** `app/`, `ui/`, the label file, migrations beyond an additive `run_kind`/proxy
> column verified by `information_schema`, the pre-registered fit (id=2, never recomputed).
>
> **⚠ F-004 IS THE RESULT. Nothing here replaces it. No run in this PR. The interpretation (§Decision 4)
> is committed BEFORE any run.**

---

## 0. ⚠ Prerequisites — confirm before writing a line

> **✅ ALL THREE DISCHARGED 2026-08-01, before any code** (recorded in the order itself so a later
> reader is not left to re-derive them — D-074):
> 1. **D-065 merged AND run** → the *proceed* branch. `e309545` (PR #91); results F-005 `42a74ad`
>    (PR #92), `no_plddt` = `ranking_run` **id=3**, `plddt_only` = **id=4**, `scorer_version=a927dc4532b7`.
>    The `no_plddt` baseline is **measured** — median **0.5625** / mean **0.5893** / **6-of-12** — and is
>    **not "≈ chance"**; only the count is even. Anchored in D-075 Decision 0.
> 2. **Number renumbered: `F-008` → `D-075`.** F-008 was taken (two-precision confound, `754e58f`);
>    re-typed as a decision. All six staged docs swept in the landing commit (all were untracked, so no
>    published citation broke — contrast D-011).
> 3. **F-004 (id=2) persisted and read-only** — confirmed live via `/api/ranking` and by SELECT:
>    `run_kind='preregistered'`, `scorer_version=91e646e4a289`, 56 rows, 12 positives. Read-only holds
>    because `fit_scorer.py` always mints a *new* run and no CLI path targets an existing id; ⚠
>    `persist_results()` itself is unguarded, so it is a property of the **call path**, not the function.
>
> **Two amendments to this order were ruled on the same date and are reflected in the landed entry, not
> here:** Decision 4 anchors on the explicit **triple** (median, mean, count) with every "≈ chance" cell
> replaced (D-041 dec 4), and Decision 2's fixture gains a **second arm** (differing-length pLDDT array)
> because feature 7 derives `n_res` from coordinate residues only. **Where this order and
> `docs/README.md` §D-075 differ, the log governs.**

This order **extends D-065**, it does not duplicate it. D-065 already specified two feature-drop
ablations (`no_plddt`, `plddt_only`). D-075 adds what D-065 lacked: a **confidence-blind replacement
feature** (so the axis is tested with its information restored, not merely amputated) and a
**popularity-matched control** (so "attention" is tested directly, not only via feature removal).

1. **Confirm D-065's status.** Read `docs/README.md`.
   - If D-065 **merged and its ablations have run** (F-005 exists): D-075 builds on those results —
     the `no_plddt` result is the amputated baseline this order restores information to. Cite it.
   - If D-065 **merged but not yet run**: run D-065's two ablations first (they are the cheaper,
     already-ruled pair), then D-075. Do not skip them — they triangulate with D-075.
   - If D-065 **not merged**: STOP and surface it. D-075 cannot precede its own prerequisite.
2. **Confirm the D-075 number** against `docs/README.md`. Renumber if taken.
3. **Confirm F-004 (id=2) is persisted and read-only** in the run table. Its numbers are read from
   the row, never recomputed.

---

## 1. The entry

### D-075 — A confidence-blind structural axis: does the signal survive when pLDDT information is *replaced* rather than removed, and when attention is matched?

- **Date:** 2026-08-01
- **Status:** Proposed → Accepted on merge. **Ruled before any run.**
- **Relates:** **D-065** (the two feature-drop ablations D-075 extends); **F-004** caveat (b) (the
  confound); D-058 decision 2 (sensitivity permitted after the pre-registered result, never replaces
  it); D-041 (the model, unchanged); D-060 (leakage guards, RNG discipline).
- **Provenance:** the Grok adversarial second opinion (2026-08-01) escalated the pLDDT-attention
  confound from open caveat to potentially load-bearing, and named the exact tests D-065 did not run:
  a confidence-blind *replacement* and a popularity-matched control. This entry runs them.

**Context — why D-065 alone is not enough.** D-065's `no_plddt` drops features 3 and 4 and asks *does
the shift survive their removal?* But dropping them also removes the **information** they carried
(membrane-proximal accessibility), so a null `no_plddt` result is ambiguous: signal gone because
pLDDT was confounded, or because real geometric information was amputated? D-075 resolves the
ambiguity by **replacing** that information with a confidence-blind measure, and by testing attention
directly.

---

#### Decision (1) — the confidence-blind feature set (frozen before any run)

| Set | Features | Parameters |
|---|---|---|
| **`no_plddt`** (from D-065) | 1 (ECD length), 2 (Rg), 5 (SASA), 6 (patch fraction) | 5 |
| **`geom_proxy`** (D-075, new) | 1, 2, 5, 6, **+ 7 (membrane-proximal SASA, coordinate-only)** | 6 |

`geom_proxy` restores the *membrane-proximal accessibility information* that feature 4 carried, but
measured from **geometry alone, with zero pLDDT input.** If the signal is real geometric structure,
`geom_proxy` recovers what `no_plddt` lost. If the signal was pLDDT-as-attention, `geom_proxy` does
not recover it — because the proxy carries no confidence information.

#### Decision (2) — ⚠ the proxy MUST be confidence-blind (its own red-then-green test)

Feature 7, membrane-proximal SASA:
- computed on the **raw atomic coordinates** over the **same membrane-proximal residue window**
  feature 4 uses (same window rule — reuse it, do not redefine it);
- **must not read the pLDDT / B-factor column at any point** — no confidence weighting, no
  pLDDT-based residue filtering, no confidence-derived window adjustment.

**⚠ Test that MUST go red first:** a fixture of two structures with **identical backbone coordinates
but different pLDDT/B-factor columns** must yield **byte-identical** membrane-proximal SASA.
- Build a deliberately **contaminated** implementation (reads the B-factor) → the fixture **separates
  them → test RED.** Confirm the red.
- Fix to coordinates-only → fixture yields identical → **test GREEN.**
- **If this test cannot be made to go red on a contaminated impl, the fixture is not biting and the
  proxy's confidence-blindness is unproven** — that is a stop-and-report condition, not a proceed.

**Why this is the load-bearing test.** A proxy that silently leaks pLDDT would look clean while
reproducing the exact confound D-075 exists to exclude — the "function exists ≠ function does what it
claims" failure class. The whole value of `geom_proxy` is that it is confidence-blind; that property
must be *proven by a biting test*, not asserted.

#### Decision (3) — the popularity-matched control (the direct attention test)

D-065 tests attention only indirectly (via feature removal). D-075 tests it directly. A new script
`scripts/attention_control.py` computes, per target, two frozen attention proxies:

| Proxy | Definition | Source | Frozen |
|---|---|---|---|
| **`pdb_present`** | 1 if the target has an experimentally solved structure in the PDB, else 0 | RCSB/UniProt xref, **frozen date recorded** | binary, low-noise, the strong proxy |
| **`pub_count`** | literature density (PubMed hits for the gene symbol) | PubMed, **frozen query + date recorded** | continuous, noisier, catches attention without a solved structure |

**The control:** re-rank with the structural (ablated) score **after covariate-adjusting or
stratifying on the attention proxy**, and test whether positives still enrich. Run against
`pdb_present` and `pub_count` **separately** — a sensitivity pair, not one blessed number.

**⚠ Both proxies frozen (source + query + date recorded in the entry) BEFORE the control runs.** No
re-querying after seeing the result.

#### Decision (4) — ⚠ the interpretation is fixed BEFORE any run

| Outcome | Reading |
|---|---|
| **`geom_proxy` shift ≈ full-model shift** (proxy recovers what `no_plddt` lost) | **Confound weakened.** The signal is geometric accessibility, not confidence. The membrane-proximal information matters, but its *pLDDT* encoding was not what carried it. |
| **`geom_proxy` ≈ `no_plddt` ≈ chance** (proxy does not recover it) | **Two live readings, reported as such:** either the signal was pLDDT-as-attention, OR real membrane-proximal information exists but neither the SASA proxy nor n=12 can capture it. **Ambiguous, and reported ambiguous.** |
| **Signal survives popularity-matching on BOTH `pdb_present` and `pub_count`** | **Confound substantially excluded.** The strongest available evidence the axis is not attention. Grok's sinking question is answered. |
| **Signal survives one proxy but not the other** | **Informative split, reported honestly.** Not hidden, not averaged away. |
| **Signal vanishes under matching** | **Confound strengthened → Branch B.** The enrichment is not separable from research attention. **This is the finding, reported prominently** — it redirects the paper, and it is better found here than by a reviewer. |

**"≈" is deliberately not thresholded** (D-041 decision 4, D-065 precedent). Distributions reported
side by side, read in prose against this table.

#### Decision (5) — structural prevention of fishing and headline-drift (inherits D-065)

- **`--ablate` accepts only named sets:** `no_plddt`, `plddt_only` (D-065), `geom_proxy` (D-075).
  **Arbitrary subsets refused by the code.** No new set without a new dated entry.
- Each run writes its own `ranking_run`, `run_kind='sensitivity'`, set name tagged. **The
  pre-registered run (id=2) stays `run_kind='preregistered'`** and is what every result surface serves
  as *the* result.
- The attention control writes its own tagged artifact, `run_kind='attention_control'`, proxy name +
  frozen date recorded.
- **F-004 is not amended.** D-075's results land in the D-075 entry, citing F-004 and D-065, modifying
  neither.
- **The six-feature assertion on the pre-registered path stays green.** If it reddens, an ablation has
  leaked into the pre-registered path — the PR is wrong.

- **Deep-learning justification.** The question is *what ESMFold's own confidence encodes* — structure,
  or training-set representation. pLDDT is a network output used as signal (D-041 §2). Replacing it
  with a coordinate-only measure and matching on attention directly tests whether the network's
  uncertainty was carrying structure or carrying popularity. This is the most directly
  DL-relevant follow-up available, one refit + one control against an existing pipeline.

- **Consequences / test surface:**
  - **The confidence-blindness fixture (Decision 2) reds on a contaminated impl, greens on the clean
    one** — the load-bearing test.
  - `--ablate` refuses any set not in the named three — asserted; arbitrary subset raises.
  - Feature-count assertion: `geom_proxy` = **6 parameters** (5 features + intercept).
  - `run_kind` persisted; sensitivity/attention runs never returned where the pre-registered run is
    expected — fixture holds all kinds.
  - The three D-060 leakage guards **re-assert on the `geom_proxy` path**: scrambled comparator →
    identical coefficients; held-out features unchanged; λ-selector never sees the held-out index.
  - Determinism: same fixture, two runs, byte-identical coefficients.
  - Attention proxies: frozen date/query persisted; re-running the control with the same frozen inputs
    is byte-identical.

---

## 2. Order of work

1. **Confirm §0 prerequisites** (D-065 status, D-075 number, F-004 read-only). Stop-and-report if
   D-065 is unmerged.
2. **Land D-075 entry + the frozen interpretation (Decision 4).** Own commit, **before code.** This is
   what makes it pre-registered.
3. **Tests red first** — the confidence-blindness fixture (RED on contaminated impl), the `--ablate`
   refusal, the parameter count, `run_kind` filtering.
4. `core/features.py` — feature 7, membrane-proximal SASA, **coordinates only**, reusing feature 4's
   window rule. Confidence-blindness fixture goes green.
5. `core/scorer.py` — accept `geom_proxy` as a named set; **default path unchanged.**
6. `scripts/fit_scorer.py` — `--ablate geom_proxy`, persisting `run_kind`.
7. `scripts/attention_control.py` — compute `pdb_present` + `pub_count`, frozen date/query recorded;
   the matched-control run.
8. Migration only if `run_kind` / proxy columns need one — **additive, verified by
   `information_schema`.**
9. `ARCHITECTURE.md`, dry-diff, red-then-green audit, full gate, owner merge. **No run in this PR.**

## 3. ⚠ Five things that will bite

1. **Do not let the proxy read pLDDT/B-factor.** If it does, D-075 is void while looking clean. The
   Decision-2 fixture is the guard; if it will not go red on a contaminated impl, STOP.
2. **Freeze the attention proxies before running the control.** Re-querying PubMed after seeing the
   result is the fishing this entry prevents. Date + query in the entry.
3. **Do not re-run the pre-registered fit.** F-004 is read from its row.
4. **Report the collapse case prominently if it happens.** If the signal vanishes under matching, that
   is Branch B and it is the finding — the entry exists so that outcome is as publishable as survival.
5. **Do not add a fourth ablation or a third proxy to clarify an ambiguous result.** That is a new
   dated entry. Ambiguous is a legitimate, reportable outcome.

## 4. What "done" means

`geom_proxy` runnable and confidence-blind (fixture proven biting), the attention control runnable
against two frozen proxies, all leakage guards re-asserted, the pre-registered six-feature assertion
green, `run_kind` persisted and filterable, F-004 untouched. **Gate green. No run in this PR** — runs
are owner-authorised after merge, interpretation already frozen.

## 5. If something is wrong with these orders

Say so before building. Specifically: if D-065 is unmerged (§0), if the membrane-proximal window rule
cannot be reused without redefining it (a features finding that outranks this PR), or if `run_kind`
cannot persist without a migration the scope forbids.
