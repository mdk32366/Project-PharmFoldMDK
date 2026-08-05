# D-079 (RE-ISSUE v2) — Census ingest, tranche ordering, and recipe disclosure

> **LANDED — `### D-079`, `docs/README.md`, 2026-08-05. Where this file and the log differ, THE LOG
> GOVERNS.** ⚠ §Denominator's `non_surface` (2,211) and `unclassified` (2,795) figures are
> **superseded** by `RULINGS-2026-08-05-class-collision.md` — the live denominators are `surface`
> 2,807 · `non_surface` 2,209 · `unclassified` 2,793 · `class_conflict` 2, reconciling to 7,811 and
> never summed. The superseded numbers stay visible here, beside the ruling that corrects them; they
> appear nowhere in `docs/README.md`.

> **Supersedes the v1 issue of 2026-08-05, which was never merged.** ⟡ marks v2 changes.
> **Decision 2 is REPLACED by owner ruling, not edited.** The v1 text is retained below the
> replacement so a later reader can see what was ruled against and why — a decision whose rejected
> alternative has been deleted reads as though it was never contested.
>
> ⚠ **Confirm the number against the live log before merging.** Highest written: `### D-077`,
> `### F-016`. `D-078` / `D-080` reserved. **`D-079` next free; `F-017` next free finding.**

- **Date:** 2026-08-05
- **Status:** Proposed → Accepted on merge. **Ruled before any ingest.**
- **Provenance (D-016):** owner objective 2026-08-05 (tranches, laptop crank); owner in-flight recipe
  concern; ⟡ **six owner rulings, 2026-08-05**, recorded in §Rulings below.

---

## ⟡ Owner rulings of 2026-08-05, recorded verbatim in substance

| # | Ruling | Effect here |
|---|---|---|
| 1 | Narrow the D-075 gate as written; **the census denominator is 2,807** | Decision 1 stands; §Denominator added |
| 2 | **Two recipes do not materially affect credibility. Fold everything we can, state the hardware and method, present it, and let others replicate.** | **Decision 2 REPLACED** (below) |
| 3 | **`folded_analysis_id`** — F-010 closes by rename | Out of scope here; ordered separately |
| 4 | **Move on D-075** | Own orders; not this entry |
| 5 | KEEL Principle 7 — four documents unified by a top-level README. **Cleanup after feature value, or tomorrow's pre-work** | Recorded; no action in this entry |
| 6 | **PRISMA: flow diagram only** | Recorded; no action in this entry |

---

## ⟡ The denominator, fixed (owner ruling 1)

**The census is the 2,807 distinct current accessions of the SURFY surface class** — not 2,886
identifiers. Counted off `membraneome-reconstructed-2026-08-04.csv` on 2026-08-05; 79 identifiers
collapse into four HLA loci UniProt has merged. **Every count states its key.**

The **annex** — 2,211 distinct non-surface accessions — is ingested under its own tag, never pooled
(F-011). ⚠ The **2,795 unclassified** are ingested under a third tag and are **not evidence for
F-011's thesis**; a different exclusion mechanism (F-016), not recruited.

---

## Decision (1) — the D-075 gate is **narrowed, not lifted** *(unchanged from v1)*

A fold is a **measurement**; a score is an **interpretation**. D-075 protects the interpretation.

**Permitted:** ingesting rows with class, accession, span, band, recipe, tranche · folding at a
recorded recipe · reporting **cost, coverage, and confidence-distribution** statistics, each labelled
with tranche and recipe.

**Forbidden until D-075 fires:** no census row scored, ranked, or ordered by suitability — **no
census path imports `core/scorer.py` or the fitter, asserted by test, proven by revert** · no census
statistic presented as evidence about ADC suitability, in any artifact, deck, or briefing · **no
refit** — `ranking_run` id=2 is read from its row.

---

## ⟡ Decision (2), REPLACED — **fold everything reachable; record the recipe on every fold; disclose the heterogeneity**

**v1 ruled:** one recipe for the census (`int8, 64`), with targets above the local envelope ingested,
flagged, and **not folded**, on the grounds that mixing dtypes imports F-008 at census scale.

**Owner ruling 2026-08-05 rejects that trade and it is adopted.** The census folds every target it
can reach, at whichever tier can reach it, with the recipe stated.

**What the owner's ruling gets right, and v1 got wrong.** A census that stops at 440 aa is
**truncated on ECD length — feature 1 of the pre-registered six.** v1 refused a confound by
introducing a selection bias on the single most load-bearing feature, which is the F-009 error one
level out, in the Planner's own entry. **Completeness wins.**

**Binding form of the ruling:**

1. **Fold every target reachable at any tier.** No target is left unfolded for recipe-hygiene
   reasons. Cost and hardware availability remain the only limits.
2. **Every fold records its recipe at fold time** (D-047), resolved from `TIER_RECIPE`, never
   hand-passed. ⚠ **A fold that completes without a recorded recipe is a defect, not a gap** — the
   one such fold among the 82 becomes structurally impossible. Test proven by revert.
3. **Every census statistic that reaches a surface, a deck, or the paper states its recipe
   composition** — how many folds at each `(dtype, chunk_size)` — beside the number, not in a
   methods appendix.
4. **⟡ Census heterogeneity is one-dimensional, and this is an improvement worth stating.** Both
   tiers chunk at 64 since D-042, so the census varies in **dtype only**. Tranche zero varies in
   dtype *and* chunking (`(fp16, None)×34`), which F-012 measured as output-affecting. The census is
   therefore cleaner than the cohort it extends, not messier.
5. **Recipes are never pooled silently.** Any distributional claim (mean pLDDT, band splits,
   confidence histograms) is reported **per recipe as well as combined**, or not reported.

---

## ⟡ Decision (7) — the precision overlap set: what makes decision 2 recoverable rather than merely disclosed

**The gap the ruling leaves, stated plainly and without argument, because it is specific.**

Under decision 2 the census spans two dtypes. But **precision is assigned by tier, tier is assigned
by length, and length is feature 1.** So dtype and length are **perfectly confounded with no
overlap** — the exact structure F-008 recorded for the 82 and D-075 decision 6 declines to resolve.

**Disclosure does not close it.** *"We state the hardware and method"* makes the heterogeneity
**visible**; it does not make it **separable**. If census mean pLDDT differs between the int8 rows
and the fp16 rows, no amount of honest reporting tells a reader whether long ECDs genuinely fold with
less confidence or whether int8 quantization depresses pLDDT. ⚠ **And a replicator following our
stated method reproduces the same confound** — replication then confirms reproducibility, not
validity. That is the specific limit of *"let others replicate."*

**⚠ This matters more here than it did for the 82** because pLDDT is the signal carrier (F-005), and
the census's strongest use is the attention-confound test at n in the thousands. A dtype artifact
sitting inside the confidence variable is sitting inside the measurement.

**The instrument that closes it, and it is cheap:**

1. **Fold a pre-registered random sample of SHORT targets at BOTH precisions.** Short ECDs are the
   ones where fp16 fits in 8 GB — the 440 aa int8 fold peaked 6,665 MiB, so headroom exists well
   below that. **The overlap is plausibly free and local.** Code probes the fp16 length ceiling on
   the local box first and reports it; the sample is drawn beneath that.
2. **The sample size and the seed are recorded before the first overlap fold.** Draw from the local
   band by the decision-4 seed, not by convenience.
3. **What it buys:** a **measured** per-residue pLDDT offset between int8 and fp16 on the same
   sequences. Heterogeneity becomes a **nuisance parameter with a magnitude** instead of a
   structural confound with none. If the offset is negligible, decision 2 is vindicated by
   measurement rather than by assumption — which is a stronger position than v1 ever offered.
4. **Its design and frozen interpretation land as `D-078`**, whose reservation in `RESERVED.md` is
   ⟡ **amended**: its trigger was *"a raised local ceiling."* The census now creates the overlap need
   directly, so the trigger is **the first census fold at a second precision.**

⚠ **The overlap is not a gate on the crank.** Folding proceeds; the overlap runs alongside. It is
required before any census-wide confidence statistic is reported, not before any fold happens.

---

## Decision (3) — a tranche is an **execution order**, never a filter, never a suitability axis *(unchanged)*

D-077 decision 1's three prohibitions are inherited whole: local-foldability must not become a model
feature, must not sit beside suitability without its label, must not filter the census.

Bands are **named, not inferred**: `local` (≤ `LOCAL_CEILING.known_good`) · `unmeasured_band`
(440–630, pending F-013) · `above_local` (≥ 630) · `no_topology` (**a category, never a length,
never `0`**) · `unresolvable`. ⟡ Under decision 2, bands now determine **which tier folds a target**,
not **whether** it is folded.

---

## Decision (4) — within a band, fold order is a **seeded random permutation**, frozen before the first fold *(unchanged)*

The crank turns for days and someone will want a number off the partial result. A partial set taken
in file, accession, or length order is a biased subsample of its own band — worst in length order,
because length is feature 1.

Seed recorded in the census manifest before the first fold. **Frozen reading, both directions:** a
**band-conditional** statistic on a partial tranche *is* reportable, stating band, n, seed, and ⟡
recipe composition. A **census-wide** statistic on a partial tranche is **not**, under any framing.
⚠ No silent re-seed.

---

## Decision (5) — Task B is **verification**, not derivation *(unchanged)*

The reconstructed membraneome already carries an accession on all 7,903 rows (0 blank), counted
2026-08-05. Re-deriving the mapping would produce a second accession source with nothing comparing
it to the first — the two-paths class, **eleventh instance, caught in a standing Planner order before
it executed.**

The CSV's accession column is the **source of record**. Buckets: `agrees` · `source_only` ·
`uniprot_only` · `disagrees` · `unresolvable`. ⚠ A disagreement is a **finding**, not a merge
conflict resolved by preference. Empty buckets asserted empty. **Owner-reserved:** how `disagrees`
and `multi` resolve.

---

## Decision (6) — what a census fold licenses ⟡ *(amended for decision 2)*

✅ **Licensed:** *"Of the 2,807 surface-class ECDs, N are folded — M at (int8, 64) on a consumer
8 GB GPU, K at (fp16, 64) on rented compute — as of [date]."* Dated, band-named, **recipe-composition
named**, derived from live routes.

❌ **Not licensed:** coupling foldability to suitability (D-077 dec 1) · any census filtered by
affordability (D-077 dec 3) · any statement about how many rows are good targets (D-028) · any
extrapolation from the 82's proportions to a census size (`core/census.py`'s standing refusal) · ⟡ any
**pooled** confidence statistic without its recipe composition (dec 2.5) · ⟡ any census-wide
confidence claim before the overlap set reads out (dec 7) · any census-wide statistic from a partial
tranche (dec 4).

---

## Definition of done

- [ ] Number confirmed; `RESERVED.md` checked; `D-078`'s trigger amended.
- [ ] Entry merged **before** migration 0008 and before any census row exists.
- [ ] 0007 applied and **verified by column inspection**, not alembic's exit code.
- [ ] Tranche column shipped; enumerating routes filtered; **proven by revert**.
- [ ] Manifest records seed + source sha256 + span run date **before** the first fold.
- [ ] Recipe recorded at fold time or the fold fails — proven by revert.
- [ ] Scorer-import refusal green and revert-proven.
- [ ] 2,807 + 2,211 + 2,795 ingested under three tags, nothing dropped, nothing pooled.
- [ ] fp16 local ceiling probed; overlap sample size + seed recorded before the first overlap fold.
