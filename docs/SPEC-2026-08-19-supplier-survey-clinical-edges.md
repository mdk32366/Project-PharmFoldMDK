# SPEC — SUPPLIER SURVEY — tying cancers to the 3,467 — `D-093` decision 6, run

> **COMMITTED to `docs/` as provenance. CITED BY the log, not restated in it — where this file and
> `docs/README.md` differ, THE LOG GOVERNS.** ⚠ This file records how a decision was reached; it is
> not itself authority.
>
> ⚠ **LANDED BY CODE, 2026-08-19, from `b7ecc2a`.** Received as chat text, not as a file, alongside
> `ORDERS-Code-2026-08-19-clinical-edges-1-and-2.md`.
>
> ⚠⚠ **NO `AUTHORED-SHA256` IS DECLARED.** The document's header promises one *"in the delivering
> message"* and **no value was delivered.** Declaring the block over Code's own transcription would
> make the `HASH-MATCH` verdict meaningless. **Recorded, not fabricated.** ⚠ This copy is reflowed,
> not byte-preserved — `BB4` measured that reflowing costs 142–284 bytes on a document this size.
>
> ⚠ **NOTHING HERE IS ORDERED.** The survey says so itself, and Code treated it as context.

---

## §0 — ⚠⚠ The trap, pre-registered before any supplier is chosen

**Expression in a tumour is not association with a cancer.**

Every surface protein is expressed somewhere. **An IHC-threshold join over 3,467 proteins × 20 cancers will return a plausible "cancer association" for very nearly all of them**, well-formed, correctly-typed, and mostly meaningless. ⚠ **`F-047`'s class, at 69,340 cells.**

⚠⚠ **And it is worse than a generic risk: `P-004` is this project's appraisal of an expression-threshold target screen.** Item 2 argues the score conflates prevalence with intensity; item 5 argues the cutoff sits on the modal value of an ~11-patient estimator. **We cannot publish that and then ship the same instrument under our own name.**

**Pre-registered, before any ingest: an expression edge is labelled as an expression edge and never rendered as an association.** The evidence-type enum of `D-093` decision 2 is the mechanism that already exists for this; §3 populates it.

## §1 — The three edges. Conflating them is the whole risk

`D-093` decision 1 fixes the traversal: `protein → (expression evidence) → tumour_type → (burden statistic) → survival`

**That is not one join. It is three edges with three evidence classes and three supplier questions.**

| # | edge | what it claims | supplier state |
|---|---|---|---|
| **1** | protein → tumour, **expression** | this protein is detected in this tumour type, at these intensities, in n patients | ✓ **VALIDATED** — §2 |
| **2** | protein → normal tissue, **differential** | ⚠ co-equal under decision 5, **not an appendix** | **candidate identified, unvalidated** — §2 |
| **3** | tumour_type → **burden** | a property of the DISEASE, attached by traversal | ⚠⚠ **NO SUPPLIER** — §4 |

⚠ **Decision 1 bars a burden number from every protein-level payload.** Edge 3 is therefore not "more columns on a protein row" under any design — it is a separate keyed table, and it is the edge with no supplier.

## §2 — Edge 1 is closed, and edge 2 is one file away

**`pathology.tsv`, HPA v22 — the supplier is already validated at `D-100`.**

- **401,800 rows · 20,090 genes × 20 cancers.** Reproduced S3's grid **1,640 / 1,640, all four count columns identical.** ⚠ **Accepted by reproduction, not by version label** — five wrong files were rejected on the way to it.
- **Licence: CC BY 4.0**, read 2026-08-17 (`D-093` amendment 1 clause 1). ⚠ **Column-scoped ingest: `High`, `Medium`, `Low`, `Not detected`, `total`, gene and cancer keys are IN.**
- **Version pinned `v22`** for two independent reasons — Kathad comparability and HPA's own citation format. `https://v22.proteinatlas.org/about/download`.

**Edge 2 — `normal_tissue.tsv`, HPA v22.** Same organisation, same licence, same version pin, same column-scoped rule. ⚠ **Not fetched, not reproduced, not validated.** **It is the co-equal half of decision 5 and it is currently absent** — and *absent* here is a category with a cause, namely *nobody has fetched it*, not *it does not exist*.

⚠⚠ **The join is where this fails, and it fails silently.** The census key is a **UniProt accession**; HPA's key is an **Ensembl gene ID plus a gene name**. **That is a two-hop mapping**, and *a case-mismatched join returning a clean zero three times* is already a catalogued `F-047` member. **Decision 6's question (3) demands a pinned mapping, and this is the one that must answer it.**

**The four absence categories are already named** (`PREWORK §2b`): `ihc_gene_absent` · `ihc_panel_empty` · `hpa_absent` · `accession_ambiguous`. ⚠ **They must be reported before any coverage percentage is, and the percentage must never absorb them.**

## §3 — ⚠ The evidence-type enum, and the strongest class is already in the repo

`D-093` decision 2 requires an **ordinal** evidence-type enum. Ordered weakest to strongest:

1. **`differential_expression`** — HPA IHC. ⚠ **What §0 warns about. It is what we have, and it is the weakest thing on this list.**
2. **`proteomic_abundance`** — CPTAC. ⚠ Licence **UNREAD**. `D-093`'s own table already records that abundance ≠ localisation.
3. **`genetic_association` / driver status** — candidates **COSMIC · OncoKB · Open Targets**. ⚠⚠ **All three UNREAD. Do not assume any of them is permissive** — this is precisely the recollection that produced amendment 1.
4. **`therapeutic_precedent`** — a target with an approved or clinical ADC in that indication. ⚠ **`data/adc_reference_mapping.csv` is already in the tree**: small, curated, and the strongest evidence any of these edges can carry.

⚠⚠ **AND `therapeutic_precedent` MAY NEVER BE A SCORING FEATURE.** *"Has been developed as an ADC target"* used to rank ADC targets is circular — **the identical argument that bars GPI status**, and the identical argument `P-004` item 1 makes against Kathad's own validation step. **It is a label and a filter. It is not a feature.**

## §4 — ⚠⚠ THE HARD STOP: decision 4 requires a survival tuple and no licensed supplier can fill it

`D-093` decision 4: **a burden statistic is a tuple or it is not a number** — `stage_or_extent`, `data_era`, `source`, `retrieved_on`, all mandatory, rejected at write without them.

**But amendment 1 clause 2 excludes every `Cancer prognostics — … (TCGA)` column**, TCGA carrying bespoke unread User terms. ⚠ **The survival data HPA redistributes is the data the licence ruling removed.**

**So the schema currently mandates a field that nothing licensed can populate.** And decision 6 is explicit: *a supplier that cannot answer (3) with a pinned mapping does not enter the schema.*

**Candidates for edge 3, all UNREAD and none characterised:**

| candidate | what it would supply | ⚠ what must be read first |
|---|---|---|
| **SEER** | US incidence and survival by cancer site | terms; **and it is US-only, which is a stated limit, not a caveat** |
| **GLOBOCAN / IARC** | global incidence and mortality | terms |
| **TCGA / GDC direct** | survival at patient level | ⚠⚠ **the same User terms amendment 1 refused second-hand.** Reading them is the only way this changes |
| **CPTAC** | proteomics, some clinical | terms |

⚠ **The taxonomy will not line up.** HPA's 20 cancer types are coarse — *"breast cancer"*, not *"HER2-low breast cancer"* — while ADC indications are narrow: **CLDN18.2 in gastric, NECTIN4 in urothelial.** **A burden statistic keyed to a 20-type taxonomy joined to an indication-level claim is two paths to one quantity, never compared.** *The crosswalk is itself a supplier question.*

## §5 — What I recommend, and the two rulings it needs

**The layer ships in stages, with edge 3 as a NAMED GAP rather than a delayed release.**

1. **Edge 1 now** — the supplier is validated and the licence is ruled. ⚠ **Labelled `differential_expression`, never as association.**
2. **Edge 2 next** — `normal_tissue.tsv`, same fetch, same reproduction bar. **Decision 5 makes it co-equal, so edge 1 shipping alone is already a deviation and must be recorded as one.**
3. **Edge 3 held**, with `burden_supplier_unlicensed` as a **visible category on the surface** — not a blank, not a zero, and not a quiet omission. ⚠ *Every absence is a category with a cause.*

**Two rulings, both yours:**

- ⚠⚠ **Does the layer ship without survival at all?** Decision 4 says a tuple or nothing. **The honest reading is that nothing is what decision 4 requires today**, and the alternative is reading TCGA's User terms — which is real work and possibly a lawyer.
- **Is `therapeutic_precedent` ingested as a label at all**, given it can never score? ⚠ **My view: yes, because it is the only edge on the list that reflects a decision a drug developer actually made** — but it must carry the circularity warning in the same frame it renders in, the way GPI does.

⚠ **Nothing above is ordered.** Decision 6's three questions are unanswered for four of five suppliers, and **`D-093` is void if code precedes it.**
