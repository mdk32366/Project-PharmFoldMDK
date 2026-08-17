# D-093 — The clinical association layer: protein → tumour → burden as a **traversal**, with the normal-tissue differential co-equal, and clinical burden barred from the scorer, the census filter, and every protein-level payload

> **STAGED ENTRY — merge into `docs/README.md` before any ingest runs.** This is a
> pre-registration. **It is void if code precedes it** (D-075 precedent, D-077 precedent).
>
> **⚠ Confirm the number against the live log before merging.** In the project snapshot read
> this session the highest `### D-` entry is **D-075**; **D-076** is claimed by a staged file
> (`docs/D-076-last-three-fold-plan.md`) with no `### D-076` entry in the log; **D-077** is
> staged (`D-077-local-fold-envelope-preregistered.md`); and **D-078 is reserved by name** in
> D-077 decision 7 for the F-008 precision A/B, which must be separately pre-registered before
> any dual-precision fold runs. **D-079 is therefore the next free integer *if* D-076 and D-077
> land as written and D-078 stays reserved.** Check the thing, not the reference to it.
>
> **⚠ This entry is written from a project-knowledge snapshot, not a repository zip.** Every
> `core/`, `db/`, and `app/` fact below is marked with how it is known. Confirm against the live
> tree before merging (grounding method: repository zip; project_knowledge_search is a fallback,
> not a continuity mechanism).

> ---
>
> ## ⚠⚠ RENUMBERED ON MERGE — D-079 → **D-093**
>
> **This entry claimed `D-079`. The live log had already spent it** (the census ingest of 2,807 surface proteins). The document was
> authored against a snapshot whose highest `### D-` was **D-075**; the log stood at **D-092** when
> it arrived — seventeen decisions later.
>
> ⚠ **The note below is left exactly as written.** It is a true statement about the tree its author
> read, and rewriting it would falsify the provenance it exists to record. **The claim is corrected;
> the observation is not.** Its own instruction — *"Check the thing, not the reference to it"* — is
> what caught this (`F-039`).
>
> **Assigned `D-093` on 2026-08-17.** Cross-references to sibling staged entries were
> renumbered with them; citations to *other* entries were left untouched and are **not reviewed
> here**.
>
> ---

- **Date:** 2026-08-17
- **Status:** Proposed → Accepted on merge. **Ruled before any ingest, any schema, any supplier call.**
- **Type:** A **decision**. It rules a data model, an evidence vocabulary, and — the load-bearing
  half — **what the resulting axis may and may not be used for.** Ingest results land later as
  their own F-entries.
- **Relates:** **D-015 §1a** (disagreement classes visually distinct); **D-016** (every claim names
  how it is known); **D-024** (coverage as a first-class surface; supplier-before-contract);
  **D-027** (the fixed six features — this entry adds none); **D-028** (the UI detects and
  classifies, never explains; attribution is about the model, never the target); **D-050**
  (derive, don't hardcode); **D-069** (every surface self-sufficient); **D-074** (a finding against
  an instrument stays open until the instrument no longer exhibits it or carries the statement of
  what it gets wrong); **D-075** (the geom_proxy ablation and the named-set refusal); **D-077**
  decisions 1 and 6 (an axis labelled as cost, barred from the model and from the census filter —
  **this entry is that ruling applied to a second axis**); **F-005** (signal partially carried by
  pLDDT); **F-009** (four validated ADC targets are false negatives of an expression filter);
  **F-022** (independence of source is not independence of inference); and the **membraneome census**
  (roadmap 3.1), whose ~2,807 surface proteins are this layer's denominator.
- **Provenance (D-016):** owner instruction, 2026-08-17 — *"we need a new source that associates the
  census proteins with cancers that exhibits those proteins extracellularly. This way every protein
  in the census that has an extracellular segment has a cancer association and some indication of
  lethality and mean time to death given existing therapies available."* Planner raised the
  on-target/off-tumour axis as an addition; owner ruled it **in this entry** rather than a separate
  one, same session.

---

## Context — what is being asked for, and why it is three things rather than one

The request names one artefact. It is three, and they have materially different epistemic footing:

| Sub-claim | What it is a property of | Evidence class |
|---|---|---|
| **protein → tumour** | the **protein** | expression / localisation measurement |
| **tumour → lethality** | the **disease** | population epidemiology |
| **tumour → survival under current standard of care** | the **disease, in an era** | population epidemiology, time-varying |

**The first is about your target. The second and third are not.** Collapsing them into one row is
the failure this entry exists to prevent, and it is the same shape as D-077 decision 1: a
satisfying new number, exactly collinear with something that is not suitability, promoted to an
axis because it feels informative.

**How known (D-016) — the state this entry is ruled against:**

| Fact | Source | Confidence |
|---|---|---|
| The census covers ~2,807 surface proteins (membraneome) | prior-session record | ⚠ **not re-derived this session** — re-derive from the live endpoint before any count reaches a surface |
| Census Task 4a (determinism control) in progress, worker idle, **no census rows ingested** | prior-session record | ⚠ owner ruled *stand by* on census, 2026-08-17 |
| `protein_features` carries the six D-027 features + feature 7, `null_reasons`, `feature_version` | `db/models.py`, snapshot | read this session |
| No clinical, expression, or disease table exists anywhere in the schema | snapshot — **absence, from a fallback search** | ⚠ **not an absence proof.** Confirm against the live tree |
| The `no_topology` band was misnamed and conflated five mechanisms; two-thirds of the membraneome is unmapped | prior-session finding | this is the reason the census exists |

**What makes this worth ruling before it is built:** the census is the largest denominator the
project has ever had. A biasing decision applied to 82 targets is a flaw. The same decision applied
to 2,807 is a **systematic distortion of an atlas**, and it will be invisible because every
individual row will look plausible. *Plausibility is the failure mode at scale.*

---

## Decision (1) — ⚠ **Clinical burden is a property of the DISEASE. It attaches by traversal and may never be a protein-level column.** The load-bearing ruling.

**The failure this prevents, stated concretely.** If MSLN's row carries `median_os_months: 11`, a
reader reads *MSLN is a lethal target*. It is not. It is a protein expressed in a cancer that kills
people. **Every** protein expressed in pancreatic adenocarcinoma inherits that identical number —
so the field does not discriminate between targets at all. It discriminates between diseases, and
then replicates one disease's number onto hundreds of protein rows, where it reads as a property of
each.

This is **D-028 one level out**, and it is *harder* to hold than D-028 was. Nobody misreads a
Spearman coefficient emotionally. Everybody misreads a survival figure. A mortality number placed
beside a suitability score will be read as a justification for the score no matter what the caption
says.

**Ruled:**

1. **The data model is a traversal, not a join into one row:**

   `protein → (expression evidence) → tumour_type → (burden statistic) → survival`

   Three tables, minimum: `protein_tumour_evidence` (the edge, protein-keyed), `tumour_types` (the
   node), `tumour_burden` (statistics, tumour-keyed). The **burden statistic is keyed on the tumour
   node and nothing else.**

2. **No protein-level payload may carry a burden field.** Not `protein_features`, not
   `target_scores`, not `/api/ranking`, not `/api/analyses`, not the census row. The column does not
   exist, and **a test asserts it does not, proven by revert** — add the column, watch the gate
   redden (A-017: the fixture must discriminate).

3. **The UI may walk the edge and display the number.** It must display it **as a property of the
   tumour**, in a visual frame that names the tumour, never as a protein attribute inline in a
   protein row. Same discipline as the GPI badge: the attribute and its liability travel together,
   and the liability is never rendered as a positive signal.

4. **Ordering by burden is barred at every surface.** A census sortable by median OS is a
   lethality leaderboard with protein names attached. If a burden-ordered view is ever wanted, it is
   a new dated entry with its own justification.

**Why the structural guarantee and not merely a test:** D-075 established the pattern — feature 7 is
confidence-blind *architecturally* (`Atom` carries no `b_factor`; `parse_pdb` never reads columns
60–66), not merely by assertion. The same standard applies here. The burden statistic should be
**unreachable from the protein path**, so a protein-level payload cannot pick it up by iterating a
row.

---

## Decision (2) — Localisation is **named, never inferred**. The evidence-type enum is the entry's second load-bearing piece.

The owner's requirement is *"exhibits those proteins **extracellularly**."* That is the correct
requirement and **no public source cleanly supplies it.** What exists:

| Source class | What it measures | What it does **not** establish |
|---|---|---|
| Bulk RNA (TCGA, GTEx) | transcript abundance in tissue | protein presence; localisation; cell of origin |
| IHC protein (HPA) | protein presence, tissue-level | ECD displayed on the tumour cell surface; antibody-dependent |
| Proteomics (CPTAC) | protein abundance | localisation |
| Surface proteomics / flow | surface display | rarely available per tumour type |

**Joining RNA-seq and rendering it as surface display is three inferential hops rendered as one
measurement.** That is **F-022** verbatim: independence of source is not independence of inference.

**Ruled — every `protein_tumour_evidence` row carries an `evidence_type`, and it renders:**

```
evidence_type ∈ {
  surface_confirmed,   -- surface proteomics / flow on tumour cells
  ihc_tumour,          -- protein-level IHC, tissue not cell-surface resolved
  rna_tumour,          -- transcript only
  inferred_topology,   -- our own ECD span says a surface segment exists; no expression evidence
  none                 -- searched, nothing found
}
```

- **The enum is ordinal in strength and must never be flattened to a boolean.** A UI that renders
  `rna_tumour` and `surface_confirmed` identically has manufactured a claim the data does not make.
- **`inferred_topology` is our own inference and is labelled as ours**, never as an external
  source's finding.
- **No surface may state or imply "this protein is displayed on the surface of this tumour" unless
  `evidence_type = surface_confirmed`.** Every weaker row states what it actually is.

---

## Decision (3) — The three D-077 rulings transfer verbatim, and the third is the one that matters at census scale

Clinical association is not a suitability axis. It is a **relevance and prioritisation** axis. It
says which disease a target is *about*; it says nothing about whether an antibody can bind it, be
internalised, or deliver payload.

1. **It MUST NOT become a model feature.** No eighth feature, no ninth. D-027's six stands; D-075
   decision 5's named-set refusal stands unamended. Adding a clinical feature requires a new dated
   entry and would import a new confound — *targets in well-studied cancers have more evidence*,
   which is attention-and-precedent, exactly the negative result D-015 §3 pre-registered.

2. **It MUST NOT be presented beside suitability without its label.** Any surface placing a
   suitability score and a burden statistic in one frame states, in that same frame, that they are
   different kinds of quantity (D-069, every surface self-sufficient).

3. **⚠ It MUST NOT filter the census.** *This is the ruling most likely to be violated by
   convenience.* A census that drops proteins with no known cancer association is a census of **what
   has already been studied**, not of the surfaceome. That is **F-009 at 2,807-row scale** — F-009
   recorded four clinically validated ADC targets (CD30, CEACAM5, CD33, Trop-2) falling out of an
   expression-based filter, and that was at n=82 against a curated cohort. At census scale the same
   error is unrecoverable and invisible.

   **`none` is a category with a reason, never an absence and never a low number.** Every count
   states its key. A protein with no association is reported as *searched, none found, here is what
   was searched* — not omitted, not zero, not null.

---

## Decision (4) — Survival statistics carry their tuple or they do not render. And "mean time to death" is not the statistic that exists.

**Correction to the request, recorded rather than silently substituted (corrections are explicit,
never quietly patched):** the owner asked for *mean time to death*. Survival distributions are
right-skewed and right-censored, so a mean is almost never published and is not estimable from the
public aggregates. What is published is **median overall survival** and **N-year relative
survival**. The entry supplies those and says so.

**Ruled — a burden statistic is a tuple or it is not a number:**

```
(tumour_site, stage_or_extent, statistic_type, value, population, data_era, source, retrieved_on)
```

- **`statistic_type` is explicit** — `median_os_months`, `five_year_relative_survival`, etc. Two
  statistic types are never compared or averaged.
- **⚠ `data_era` is mandatory and load-bearing.** Survival is not a constant. Melanoma, NSCLC, and
  RCC survival moved substantially with checkpoint inhibitors; a 2015 figure is *actively wrong* as
  a statement about current standard of care, not merely stale. A burden statistic without its era
  is undated evidence and D-016 refuses it.
- **Stage-unspecified figures are their own category**, never silently treated as all-stage or
  as any particular stage.
- **The rendering derives from the tuple; no burden sentence is ever hand-typed** (D-050,
  stale-literal discipline). Constraint A applies: every number on a surface derives from the
  payload, never a literal.

---

## Decision (5) — The normal-tissue differential is **co-equal**, not an appendix. Ruled into this entry by the owner.

**On-target / off-tumour toxicity ends more ADC programmes than insufficient tumour expression
does.** A target expressed in tumour *and* in heart, lung, skin, or peripheral nerve is a toxicity
problem regardless of how well the tumour expresses it. Tumour expression alone is **half a signal**;
the tumour-versus-normal differential is the whole one.

**Ruled:**

1. **Normal-tissue expression is ingested in the same pass as tumour expression**, from a normal
   reference (GTEx aggregate and/or HPA normal tissue — supplier confirmed under decision 6).
2. **⚠ No tumour-expression value renders anywhere without its normal-tissue comparator, or an
   explicit statement that no comparator was found.** A tumour number alone is the misleading half
   of a two-sided quantity, and rendering it alone is the same defect class as rendering a patch
   without its pLDDT.
3. **The differential carries the same `evidence_type` discipline as decision 2**, and — critically
   — **a differential may only be computed between two measurements of the same evidence class.**
   Tumour IHC minus normal RNA is not a differential; it is two different instruments subtracted.
   Cross-class comparison is barred, and the bar is enforced by the schema, not by care.
4. **The differential is not a score.** It is not thresholded into `safe` / `unsafe`. No cutoff is
   invented here, and inventing one later is a new dated entry.

---

## Decision (6) — Supplier before contract. No schema is final until each supplier is confirmed to serve what this entry assumes.

**D-024 needed this and so does this entry.** The tables above are written against what the Planner
*believes* these sources serve. That belief is pre-cutoff recollection and is not evidence.

**Before any schema is built, for each candidate supplier — HPA, GTEx, TCGA/GDC, SEER, CPTAC —
confirm and record, with the URL and the date read:**

1. What it actually serves, at what granularity (per-gene? per-tumour-type? per-stage?).
2. Whether the tier needed is the open tier or a controlled tier requiring authorisation.
3. Whether the identifier space joins to UniProt accession without a lossy intermediate mapping —
   **and if a mapping step is required, it is its own recorded step with its own failure category**,
   never a silent left-join. Unmapped is a category with a reason.
4. Stability: is there a versioned release, and can a retrieved value be pinned to it?
5. The verbatim required attribution string.

**A supplier that cannot answer (3) with a pinned mapping does not enter the schema.** Two paths to
one identifier, never compared, is the project's most-repeated defect class and an accession-mapping
join is exactly where it hides.

---

## Decision (7) — Fetch and cache, do not ship, until the inbound-terms check clears

**Owner ruling, 2026-08-17: the project's own licensing is closed — no license, all rights
retained.** This **supersedes the previously recorded AGPL + dual-licensing direction**, and is
recorded here as a reversal rather than a quiet drop.

**That ruling does not dispose of this item, because the exposure here is *inbound*, not outbound.**
Third-party data terms attach to the user of the data regardless of what license the user's own work
carries or does not carry. A share-alike or non-redistribution clause on an ingested dataset binds a
repository with no LICENSE file exactly as much as one with AGPL.

**Ruled — the conservative default, because it is reversible in the permissive direction and the
opposite is not:**

- The association layer is **fetched from its source and cached at runtime**. The cache lives under
  `data/derived/`, is **excluded from distribution**, and is **not committed**.
- **No third-party dataset is baked into the repository or the image** until its terms have been
  read, dated, and recorded.
- **The architectural fork is ruled now precisely because retrofitting it is expensive.** Discovering
  a redistribution constraint after surfaces are built on a committed table means deleting a data
  layer with dependents. Discovering that shipping was permitted all along costs one commit.

**Open item, gating ingest but not gating this ruling:** the terms check itself. The Planner could
not run it — web search was unavailable in the session this entry was drafted, and the container's
network allowlist excludes every relevant domain. **Planner recollection of these terms is explicitly
not evidence and does not enter the log.** The checklist is decision 6 items 1–5 plus: share-alike
present? commercial use permitted, restricted, or silent? does redistribution of *derived tables*
trigger anything the API-fetch path does not?

> **Also worth one question to the supervisor, cheap and potentially invalidating:** whether the
> university holds institutional DUAs covering any of these sources, and whether university IP
> policy bears on the "all rights retained" position independently of any data license.

---

## Decision (8) — What this entry does **NOT** do

- **It does not touch the six features, the scorer, the pre-registered run, or F-004.** Nothing here
  has a path to a reported result. If it ever does, that is a new entry and a new fit.
- **It does not filter, reorder, or reduce the census** (decision 3.3).
- **It does not authorise the second model.** See the DL note below — that is named, not started.
- **It does not resolve the oligomer finding**, which the owner ruled is logged first and which
  **gates the About-ADCs briefing prose, not this entry.** Confirm the next free `F-` against the
  live log; the snapshot showed `F-010` highest with `F-011` staged.
- **It does not restart the census.** Task 4a is on standby by owner ruling, 2026-08-17.

---

## Deep-learning justification

**Stated honestly, because dressing a curated join as deep learning would be the exact dishonesty
this project's log discipline exists to prevent: a curated join is not deep learning.**

The DL relevance is real but *consequential* rather than intrinsic, and it is two things:

1. **It is the first labelling instrument the project has that is not 22 positives.** D-027 fixed the
   feature count at six because 22 positives is ~3.7 per feature and that was the ceiling the
   labelled set supported. A census-scale tumour/normal differential across ~2,807 proteins is a
   labelled axis orders of magnitude larger. **That loosens the constraint that shaped the entire
   scorer design** — which is a genuine finding about the project's own method, and it is the
   honest version of the DL claim.

2. **It is the substrate for a second model, which is named here and started nowhere.** A learned
   target-prioritisation model over structure features *plus* tumour/normal differential is a real DL
   contribution with a real evaluation story. **It requires its own pre-registration, its own
   held-out design, and its own entry, and it must not touch F-004's cohort, denominators, or
   ranking run.** Naming it here is not authorising it — same posture D-077 decision 7 took toward
   D-078.

The load-bearing DL-course content in *this* entry is decision 1 and decision 3.3: **a model's
inputs determine what its outputs can mean, and a dataset silently filtered by clinical attention is
a dataset that has learned the literature rather than the biology.** F-009 already demonstrated that
failure at n=82. Refusing it in advance at n=2,807 is the entry's actual contribution.

---

## Consequences / test surface — written before any code (project rule)

**Structural, proven by revert (A-017 — the fixture must discriminate; red-then-green required):**

- No protein-level model or payload schema carries a burden field — add one, watch the gate redden.
- The burden statistic is unreachable from the protein path by iteration.
- `/api/ranking`, `/api/analyses`, `/api/coverage` payloads are asserted burden-free.

**Vocabulary and partition:**

- `evidence_type` is a closed enum; an unknown value raises, never coerces.
- `none` rows are present in every count and carry a reason; **the partition invariant binds** —
  evidence states sum to the census denominator, always, exactly as D-024's five-state coverage
  object does.
- No count renders without its key.

**Statistic integrity:**

- A burden row missing `stage_or_extent`, `data_era`, `source`, or `retrieved_on` is rejected at
  load — not defaulted, not null-coerced. **NULL coerced to 0.0 is the named plausibility failure and
  a survival field is where it would be lethal.**
- Two `statistic_type` values are never averaged or compared; a test proves the comparison path
  raises.
- No burden sentence in the UI is a literal; every number derives from the payload (D-050,
  Constraint A).

**Differential integrity:**

- A differential across two evidence classes raises rather than computes (decision 5.3).
- A tumour-expression value rendered without its comparator, or without an explicit
  no-comparator statement, fails a UI test (decision 5.2).

**Mapping:**

- Accession mapping is a recorded step with an explicit unmapped category; a silent left-join
  reddens.
- Mapped and unmapped counts sum to the input count.

**Glossary (owner ruling, 2026-08-17 — one merged glossary, hyperlinked, tooltipped):**

- Every term this layer introduces (`evidence_type` values, `median OS`, `relative survival`,
  `on-target/off-tumour`, `differential`) has **exactly one** glossary entry.
- Every occurrence of a glossary term in a UI string links to it and carries a tooltip.
- **No term has two definitions** — the assertion that keeps the ADC-briefing glossary and the
  16 rejected-topology-term glossary from drifting into two paths to one definition.
- Every entry is dual-audience: scientist and non-scientist, per the standing ruling.

---

## Open items this entry creates

| Item | Gates | Owner |
|---|---|---|
| Inbound terms check for all five suppliers (decision 7) | **ingest**, not this ruling | Matt (search unavailable to Planner this session) |
| Supplier capability confirmation (decision 6) | **schema** | Matt / Planner, next session |
| Oligomer finding logged as an F-entry | **About-ADCs briefing prose** | ruled 2026-08-17, not yet written |
| Census Task 4a | on standby by owner ruling | Matt |
| University DUA / IP position | the "all rights retained" assumption | Matt → Prof. Razzak |
| Second-model pre-registration | any fit over this layer | **not started, not authorised** |
