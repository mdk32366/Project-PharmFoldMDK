# CATCH-UP for the Planner — 2026-08-20

> **From Code. The owner's words: *"Planner is in Kansas, and we're in Ohio now."*** This document is
> the road between them.
>
> ⚠⚠ **READ THIS BEFORE THE LOG.** Eight top-level entries and eight amendments landed since the
> `2026-08-19` snapshot, and **three of them change what earlier entries mean.** Reading the log
> newest-first without this will read like a series of unrelated features; it is not.
>
> ⚠ **Where this document and `docs/README.md` differ, THE LOG GOVERNS.** This is a guide to the log,
> not authority.

**Last snapshot the Planner holds:** `PharmFoldMDK-snapshot-2026-08-19.zip`
**Now:** `main @ 383eb4c`, deployed v87. **28 commits since.**

---

## §1 — The one-paragraph version

The clinical layer shipped to users; then four consecutive attempts to extend it ran into the same
wall, which is **not** a licensing wall. **Four suppliers were read rather than recalled, and the
blocker turned out to be that the sources describe different things than the schema assumed.** Along
the way the platform gained an alias index, a staining lens, and — the one that matters most — **a
second instrument on the claim the entire census rests on.** That last one found that **53% of the
census has never been independently checked**, which is now a candidate paper.

---

## §2 — What landed, in dependency order rather than commit order

| Entry | What it is | Why the Planner cares |
| --- | --- | --- |
| `D-093` am. 4 | The Cancer connection panel shipped, both card types | ⚠ A guard caught `burden` on a protein payload — decision 1 working as designed |
| `D-101` | **Alias index** — `CD30` finds `TNFRSF8` | Two famous ADC targets read as ABSENT while present |
| `D-102` + am. 1 | **The stated-lens ruling** (owner) and the staining filter/sort | ⚠⚠ Redraws the `D-079` boundary — see §3 |
| `D-093` am. 5 | Ruling 4's open question answered | The normal-tissue denominator is **three individuals** |
| `D-093` am. 6 | Two burden suppliers READ; the tumour vocabulary fails | ⚠⚠ NCI grants, IARC reserves — see §4 |
| `D-103` + am. 1 | **A second instrument on the surface claim**, and the MNAR test | ⚠⚠ The largest single finding — see §5 |
| `P-005` | Evidence coverage as a paper candidate | Best-evidenced item in the register |

---

## §3 — ⚠⚠ The `D-079` boundary MOVED, and it was the owner who moved it

`D-102` records an owner ruling that Code asked for and refused to make alone:

> *"As long as you state what it is, it is neither judgement nor measurement. It's just a way of
> looking at the proteins the way they empirically occur in nature."*
> *"The ability to sort by a stained fraction is just another way of looking at data, and it's not a
> rank either."*

**The distinction now on the record: `D-079` decision 1 bars the system ASSERTING merit. It does not
bar a reader CHOOSING a view.** ⚠ `D-079` amendment 1 ruling 2 — *never ranked, incl. sort order* —
**stands untouched**, because it binds the structural profile, which is a **model output**. An
observed patient count is not.

⚠⚠ **The condition is load-bearing and there is a number proving it.** Over the same 1,727 census
genes, *"stains in 100% of patients"* is **728 proteins (42.2%)** under the best-single-cancer lens
and **16 (0.9%)** pooled. **A factor of 45 from identical data.** An unlabelled figure is not a
weaker labelled one — *it is a different number wearing the same words.*

---

## §4 — ⚠ The burden edge is blocked, and NOT on licensing

The owner personally obtained the licence texts. **Four suppliers, read not recalled:**

- **NCI / SEER — GRANTS.** *"All text within NCI products is free of copyright... Credit the National
  Cancer Institute."* ⚠ But it is an **information-products** policy that **never mentions data**, and
  `NCIinfo@nih.gov` is the named instrument for closing that.
- **IARC / GLOBOCAN — RESERVES.** *"All rights are reserved."* ⚠⚠ **A WHO agency is not a
  public-domain publisher** — the exact shape of error `D-093` amendment 1 exists to record. Written
  permission required for wider circulation, and a public website is not *"limited circulation."*
- **GDC / CPTAC — open, API, US Government, and CANNOT SERVE BURDEN.** The data model is
  `program → project → case`. **There is no population entity and no denominator**, so incidence is
  not derivable in principle and survival over a convenience cohort is not a population statistic.

**⚠⚠ THE ACTUAL BLOCKER IS THE VOCABULARY.** HPA's `Cancer` column is **two ICD-O axes interleaved**:
14 strings are topography, **5 are morphology** (carcinoid, glioma, lymphoma, melanoma, urothelial),
1 is a regional grouping. `melanoma` and `skin cancer` sit as **siblings** though one occurs *within*
the other. **SEER's recode mixes axes too** — Lymphoma, Myeloma, Leukemia are morphologies beside
Breast and Digestive System. **Two differently-mixed vocabularies cannot be crosswalked.**

⚠ **The dangerous one is `skin`.** SEER's category is literally *"Skin excluding Basal and
Squamous"*. A join would **succeed**, return a number, and be silently about a different disease.

**HELD FOR THE OWNER, unruled:** ingest SEER for the 16 joinable sites (a real tuple, US-only), or
**link** to both (worldwide, no permission needed) — ⚠ but **a link is not a tuple**, so choosing it
supersedes `D-093` decision 4 and must be recorded as such.

---

## §5 — ⚠⚠ The finding the Planner most needs to absorb

**Every one of the 3,467 manifest rows asserts an extracellular span, and every one came from ONE
instrument** — UniProt topology annotation, `boundary_method: sliced_ecd`. **In a project whose
most-repeated defect class is *two paths to one quantity, never compared*, the most load-bearing
claim on the platform had only one path.**

`D-103` adds a genuinely different second instrument (HPA immunofluorescence — antibodies imaged in
cells, not sequence and curation), at **no new supplier and no new licence.**

| Over 2,690 folded proteins | n | % |
| --- | --- | --- |
| ⚠⚠ **never imaged — NOBODY LOOKED** | **1,426** | **53.0%** |
| corroborated (membrane or secretory route) | 885 | 32.9% |
| ⚠ unreconciled | 78 | 2.9% |

**⚠⚠ THE RULE THAT MATTERS: a Golgi or vesicle call does NOT refute a surface assignment.** The
secretory route *is* ER → Golgi → vesicle → membrane. `MSLN` — GPI-anchored, unambiguously surface —
images in **Vesicles**. Reading *"not plasma membrane"* as *"not a surface protein"* would have been
a confident wrong answer about real biology, and **the headline is NOT *"only 366 are really surface
proteins."***

**`D-103 amendment 1` — the MNAR test, and it came out the reassuring way.** The missingness *is*
informative (median span **84 aa vs 42 aa**; validated antibody **79.0% vs 55.3%**) — but the
corroboration rate is **flat**: 73.7 / 75.8 / 73.9 / 75.4 / 72.4% across a tenfold span range, and
73.9% vs 76.4% by how well-studied. ⚠ **That licenses *"no bias detected"*, NOT *"74.4% applies to
the 1,426."*** The limit is irreducible: corroboration is measurable only where corroboration exists.

⚠⚠ **And the structural point: novelty and evidence are anti-correlated.** A census exists to reach
past well-known targets — but those are exactly the ones with a second opinion. **A discovery
platform's least-evidenced rows are the ones it most wants to say something new about.**

---

## §6 — What is waiting for the Planner specifically

1. ⚠⚠ **`docs/PROPOSAL-Planner-2026-08-20-D-075-amendment-1-span-selection-confound.md`** — a
   proposed **fourth item** for `D-075` Decision (6). The three named confounds are all about the
   FOLD; this one is upstream of them — **which sequence was folded at all.** ⚠ **Measured on
   `D-075`'s own 82: 39 corroborated, 31 never examined, 2 unreconciled.** Five things to rule,
   listed in its §5. **`geom_proxy` remains unbuilt and unrun.**
2. **`F-050`** — still RESERVED for the guard-direction sweep, still unwritten. ⚠ It now has a **table
   row** in `RESERVED.md`; it was prose-only, so the citation invariant could not see it and the
   first entry to cite it broke the check.
3. ⚠⚠ **`D-093` amendment 3 — the HPA licence finding. STILL CLAIMED, STILL UNWRITTEN.** Cited in two
   places in the present tense. Amendments 4, 5 and 6 all stepped around it. ⚠ And
   `docs/EMAIL-DRAFT-HPA-licence-clarification.md`, named by the as-read document as *"the resolution
   instrument"*, **is still absent from the tree** — the owner reports it exists.
4. **Decision 6 item (5)** — the verbatim attribution string — **remains unanswered for both HPA files
   already ingested.** A supplier confirmed on four of five is not confirmed.
5. **`P-005`'s gate is unset.** The bar Code proposes: a third instrument, the same shape on a census
   that is not ours, and a fixed denominator convention.

---

## §7 — ⚠ The pattern worth carrying forward

**Five findings in one day whose failure mode is a confident wrong answer rather than an error:**
SEER's *skin excluding basal and squamous* · GDC survival over a convenience cohort · HPA's two-axis
cancer column · the secretory route read as contradiction · and a scalar confidence asked to carry
both *"the fold is good"* and *"we folded the right thing."*

⚠⚠ **None of the five is a licensing problem. All five would have survived a licence review.** The
day's licensing work was genuinely productive and **was never the binding constraint.**

⚠ **And two of the five were Code's own**, caught by revert proofs and by a test written to justify a
design choice that found a bug instead. *`F-047` is the standing entry for this class and today was
its largest single addition.*
