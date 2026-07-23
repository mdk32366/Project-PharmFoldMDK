# UI Plan v2 — PharmFoldMDK

**Supersedes:** `docs/UI_Plan.md` (2026-07-16) in full. That document predates D-011, D-015,
D-020/021/022, D-024, D-026, D-028, D-031, and D-033; it names Streamlit as the primary
technology and `py3Dmol`/`stmol` for 3D, and describes a product this system is not building.
See §0 for what changed and why the rewrite was needed rather than an edit.

**Date:** 2026-07-23 · **Status:** Planner's plan, ruled where a decision entry rules it,
proposed where it does not. **The decision log wins** over this document wherever they diverge
(CLAUDE.md rule 3).

**Technology:** React consuming the FastAPI read API (D-033), 3Dmol.js directly for structure
(D-033), served by the same Fly app under `/api` (D-034 decision 6).

---

## 0. Why v1 was replaced rather than edited

v1 is not wrong in a way that a find-and-replace on "Streamlit" would fix. **It describes a
different product.** The gap, stated plainly so the rewrite's scope is auditable:

| v1 assumes | What is actually ruled and built |
|---|---|
| Users with accounts, login, profile, API keys | **No auth, no users.** Reads are public and unauthenticated (D-034 §4); `protein_analyses.user_id` is a nullable column with no `users` table (D-019) |
| On-demand analysis — a user pastes a sequence and clicks "Run Analysis" | **Offline batch.** The cohort is a fixed 82 targets (D-020); folds are enqueued by CLI and run by a worker the owner starts (D-004, DEP-004). Nothing folds on a page load |
| Arbitrary input: UniProt lookup, FASTA paste, PDB upload | **A fixed cohort.** `input_type` exists but every row is `uniprot` from the measured cohort. There is no ingestion path from the UI |
| Mutation simulator, wild-type vs. mutant comparison | **Not in any ruled entry.** No scorer input, no feature, no data |
| Pocket / binding-site druggability scores | **Not built and not ruled.** D-027's feature set does not include pocket detection |
| Report generation (PDF/Markdown), semantic library search | **Iteration 3+ aspiration.** `analysis_embeddings` exists as a schema (D-019) with nothing writing to it |
| The central output is a structure with a confidence score | **The central output is a comparative ranking with a disagreement classification** (D-015, D-028). The structure is an input to that, not the deliverable |

**The last row is the substantive one.** v1's centre of gravity is "predict a structure and show
it." The graded claim is: *a learned scorer ranks this cohort differently from an evidence-based
baseline, here is where they disagree, here is what class each disagreement is, and here is what
that class can and cannot support.* A UI built to v1's plan would render the project's inputs
beautifully and its finding not at all.

**What survives from v1:** the ADC framing and the educational intent (§7 below), the 3D
capability list (D-033 confirmed every item survives the `py3Dmol` → 3Dmol.js switch), and the
progressive-disclosure and confidence-communication principles.

---

## 1. What the UI is for

**One sentence:** make the project's scientific claim legible to a reader who did not build it,
including a grader — and make its limits equally legible.

Three ruled entries define the standard, and none of them is satisfied by "the data renders":

- **D-024** — coverage and limitations are a **first-class surface, not a footnote.** The
  coverage line travels with every ranking; held-out and excluded rows are reachable; boundary
  method is visible per target; fold provenance is surfaced.
- **D-028** — the system **detects and classifies** disagreement and **does not explain it.**
  Attribution is a statement about the model, never about the target. Per-class quality tooltips
  render inline, not on a methods page.
- **D-015 §1a** — disagreement classes are **visually distinct.** A class-1 and a class-2 that
  render identically in a sorted table mean entirely different things and would read the same.

D-033's framing is the design brief: *"A beautiful UI that flattens the class distinction fails
D-028; a plain one that renders it correctly succeeds."*

---

## 2. What data actually exists (D-016 — this plan is designed against it, not against intent)

Queried from production 2026-07-23. **This section is why the UI is built now and not in July:**
it is designed against landed folds, not an imagined shape.

**42 `protein_analyses` rows**, all `complete`, no nulls in `pdb_path` / `mean_plddt` /
`pae_json_path`. Composition: **40 `ranked`/`sliced_ecd` + 2 `held_out`/`whole`**, all
`tier: local`.

**Per row, from the read API (D-034):**

- **List** (`GET /api/analyses`): `id`, `accession`, `label`, `gene`, `mean_plddt`,
  `disposition`, `held_out`, `tier`, `tier_reason`, `boundary_method`, `fold_length`,
  `full_length`
- **Detail** (`GET /api/analyses/{id}`): the above plus `sequence` and `fold_provenance`
  (`model_id`, `model_revision`, `dtype`, `chunk_size`, `truncated`, `folded_at`, `mean_plddt`,
  `input_length`, `ca_atom_count`)
- **Structure** (`GET /api/analyses/{id}/structure`): the PDB, ~194–232 KB
- **pLDDT** (`GET /api/analyses/{id}/plddt`): per-residue array, ~6 KB

**No PAE route** (D-034 decision 3). **No ranking, no scorer output, no disagreement classes —
they do not exist yet** (D-027 → fit → step 3).

**⚠ The confidence spread is a design constraint, not a detail.** Measured `mean_plddt` runs
**34.78 to 81.40**. The distribution, computed over all 42 rows rather than summarised:

| Band | Count | Share |
|---|---|---|
| `< 50` | 10 | **24%** |
| `< 60` | 19 | **45%** |
| `< 70` | 24 | **57%** |

**Nearly half this cohort folded below pLDDT 60** — a region where an ESMFold structure is not
reliably interpretable. A UI that renders a
34.78 structure identically to a 77.26 one is committing the D-024 failure in the small. Whatever
surface shows a structure must show how far to trust it, in the same view.

---

## 3. Page structure

Four surfaces. No sidebar with six destinations; no settings, no account, no library.

### 3.1 Cohort view — the ranking table *(the centrepiece; waits for the scorer)*

The demo's slide-8 surface. **Cannot be built until the scorer exists**, and must not be mocked
(the pre-work names this explicitly: a mock ranking gets thrown away).

When it exists it carries, per row: target, baseline rank, structural rank, delta, **disagreement
class rendered visually distinct** (D-015 §1a), and feature attribution phrased as a statement
about the model (D-028).

**The coverage line renders with the table, not beneath it** (D-024). Its structure is the
three-cell partition (`ranked` / `held_out` / `excluded`) plus the two breakout subsets
(`unmeasured_tier`, `no_topology`) — the object `core/manifest.py` already produces.

**Held-out and excluded rows are reachable from the coverage line**, not silently absent (D-022:
*"MUC16 is CA-125; a reviewer who knows the field notices its absence immediately"*).

### 3.2 Target view — structure, confidence, provenance *(buildable today)*

Everything here works against the 42 landed folds with no scorer.

- **Structure viewer** — 3Dmol.js loading `/api/analyses/{id}/structure` by URL, coloured
  per-residue by pLDDT from `/api/analyses/{id}/plddt`. Cartoon default; surface and stick
  available. NECTIN4 (id 1) is the first rendered target.
- **Confidence** — mean pLDDT with an explicit interpretive band, not a bare number (§2's
  34.78–81.40 spread is the reason). Per-residue pLDDT plot beneath the viewer.
- **Provenance panel** — `model_id`, `model_revision`, `dtype`, `chunk_size`, `truncated`,
  `folded_at`, `input_length`, `ca_atom_count`, `boundary_method`, `uniprot_release`. **This is
  what makes "we ran this ourselves, at a named revision" checkable** rather than asserted
  (D-015, D-031).
- **Boundary method, visible per target** (D-024): `sliced_ecd` with its `ecd_start`/`ecd_end`,
  or `whole` — and for a `whole` fold, the fact that it *has no sliceable ECD* is the reason,
  which is a real limitation and belongs on the screen.

### 3.3 Coverage view — the honest denominator *(BLOCKED — no supplier exists)*

Reachable from the coverage line anywhere it appears. Shows the full 82: what is ranked, what is
held out and **why**, what is excluded and **why by name**, what is folded and what is not yet.

**⚠ This surface has no data supplier, and the read API structurally cannot become one.**
`GET /api/analyses` returns the **42 folded rows** and nothing else. It cannot produce:

- the **denominator 82** — only folded rows exist in `protein_analyses`;
- the **excluded rows by name** (MUC16, FAT2) — D-026 gives them no `protein_analyses` row at
  all, so they are not absent from the response, they are absent from the *table*;
- the **29 rental-tier unfolded** — not enqueued, and a fold-derived table has no way to
  represent "not yet."

The coverage object lives in `core/manifest.py` and **is served nowhere.** Left unaddressed,
React would reconstruct a partial line from 42 folded rows and quietly lose the *"of 82"* — which
is the entire point of D-024.

**This is the same supplier-before-contract failure D-034 was written to avoid, one surface
over.** It needs its own entry before step 4 — a `GET /api/coverage` route or a build-time
manifest export — ruled on the same discipline as D-034: shape and payload decided against the
real object, then built tests-first. **Step 3 (target view) is fully supplied by D-034 and is not
blocked by this.**

### 3.4 Method note — what the system claims *(short, static)*

D-028's non-goals stated as commitments: the system detects and classifies disagreement and does
**not** explain it; no biological causal claim; no ordering of disagreements by "interestingness."
Plus the class-2 known-confound note (§4.3).

**This does not replace the inline tooltips.** D-028 is explicit that per-class quality renders
*with* the finding; this page is for the reader who wants the whole frame at once.

---

## 4. The three surfaces that are the actual deliverable

Everything above is scaffolding for these. Each is a ruled requirement with a named failure mode.

### 4.1 The coverage line (D-024)

**Requirement:** renders *with* every ranking, as part of the result — not on a separate tab.
Three-cell partition plus two breakouts; breakouts are **subsets that cut across the partition**
(`unmeasured_tier ⊆ ranked`, `no_topology ⊆ held_out`) and **are not summed into it**.

**Failure mode:** implemented as a caveat, or as a number in a corner. D-024 exists because four
separate entries each produced a constraint that "will be implemented as caveats if they are
implemented at all."

### 4.2 Disagreement classes, visually distinct (D-015 §1a, D-028)

**Requirement:** class-1 and class-2 are distinguishable **at a glance in a sorted table** — by
colour, badge, and grouping, not by a word in a column a reader may not read.

| Class | Supports | Does **not** support |
|---|---|---|
| **Class-1 — checkable** | The comparator can be tested against an outcome already decided (e.g. an approved ADC target the baseline filtered out). Evidence **about the comparator**. | A demonstrated pattern — it is a *single instance* (D-015 §2's own caveat) |
| **Class-2 — hypothesis** | The structural axis orders this target differently. A **generated hypothesis**, on an axis never measured against outcome. | Anything about whether the structural ordering is *right*. There is no outcome to check it against |

**Rendered inline**, as tooltips or equivalent (D-028). **Failure mode:** a UI that renders the
ranking correctly and flattens the classes satisfies the letter of these entries and defeats
their purpose (D-033).

### 4.3 The known-confound note (D-028)

**Requirement:** where a disagreement is explicable by known homology relationships — convergent
folds, divergent sequences within a family, domain shuffling — it is **class-2 with a known
confound**, and the UI says so *where the disagreement is shown*.

**Why this one is called out separately:** D-028 flags it as *"the one most likely to be
omitted."* The headline "structure and sequence disagree" invites *"yes, and?"* — that is the
premise of structural biology, not a result of this project. The supportable finding is narrower
and therefore stronger.

---

## 5. Feature attribution — the one-sentence-wide gap

D-027's features are interpretable, so a disagreement can be attributed to one. **Attribution is
not explanation, and D-028 rules the gap between them is one sentence wide in a UI.**

- ✅ *"Feature 6 accounts for most of this target's structural rank."* — a statement about the
  model, and true.
- ❌ *"This target ranks higher because its epitope is more accessible."* — a statement about
  biology, which the system has no standing to make.

**The UI's obligation is to make which one it is asserting unambiguous**, because a reader will
write the second in their notes after reading the first unless the interface is explicit. This is
a copywriting requirement as much as a component requirement: **every attribution string names
the model as its subject.**

---

## 6. 3D visualization (D-033)

**3Dmol.js directly.** `py3Dmol` is a Python wrapper around 3Dmol.js and was only ever needed to
embed it in Streamlit; every capability v1 listed survives the switch:

PDB load from URL or string · residue highlighting and selection · surface / cartoon / stick
representations · **colour by pLDDT** · pocket surface rendering *(if pocket data ever exists —
it does not today)* · mutation highlighting *(not in scope; no mutation feature is ruled)*.

**Load by URL, not inline string.** D-034 decision 2 serves the PDB from its own route precisely
so the viewer takes the URL and the browser caches the structure independently of the metadata.

**Fallback:** the target view must not be a blank frame if the viewer fails. Provenance,
confidence, and the per-residue plot are independently useful and render from JSON alone.

---

## 7. ADC framing and onboarding — metaphor kept, outcome claims bounded

v1's "Mission Briefing" is worth carrying forward largely intact. A reader who does not
understand what an ADC *is* cannot evaluate why target selection is worth building a tool around,
and the guided-munition metaphor is the fastest correct route to that understanding.

### 7.1 Keep the metaphor — it is mechanism, not decoration

**The antibody / linker / payload analogy is pedagogically correct and it is the actual appeal of
the class.** Conventional cytotoxic chemotherapy is an area weapon: it acts on rapidly dividing
cells wherever they are, which is why the toxicity profile reads as a war of attrition — the
treatment's reach is not the disease's shape. An ADC is a guided munition: the antibody supplies
targeting, the linker holds the payload inert in circulation, and the cytotoxic is released at
the target cell. **That is a genuine change in delivery mechanism, and the metaphor names it
accurately.**

Keep v1's component table (antibody = guidance, linker = fuse, payload = warhead). Keep
"Operation: Precision Strike" as a section header if desired — a heading is a register choice,
not a claim. **Let the mechanism carry the excitement; it can.**

### 7.2 Bound the outcome claims — and say why target choice is hard

The metaphor describes **delivery**. It does not license claims about **outcomes**, and the
distinction is exactly the one D-028 draws between attribution and explanation, applied to
onboarding copy.

**What the copy must not assert:** that ADCs are chemotherapy without trade-offs, that they
render cancer routinely manageable, or that recurrence becomes trivially re-treatable. Those
overstate the record. ADCs are a real and substantial advance — **enfortumab vedotin targets
NECTIN4, which is `id 1` in this very cohort, and it changed outcomes in urothelial carcinoma** —
but the payload is still cytotoxic, linkers deconjugate in circulation, and the class carries its
own dose-limiting toxicities (interstitial lung disease, ocular effects, peripheral neuropathy,
varying by agent). Resistance develops, notably through **antigen downregulation**.

**That last fact is the bridge to the tool, and it should be stated rather than avoided:** an ADC
is only as good as its target. A target must be well-expressed on tumour cells, spare enough on
healthy tissue, accessible to an antibody, and stable enough not to be simply switched off under
pressure. **Choosing well is the unsolved part — which is what this project is about.**

### 7.3 Why this project exists

**Worked example, and the reason it is the worked example: NECTIN4.**

Enfortumab vedotin was approved for metastatic urothelial carcinoma — a setting where patients
who had already progressed through platinum chemotherapy and a checkpoint inhibitor had very
little left. EV moved outcomes there. It later displaced platinum chemotherapy in the first-line
setting in combination with pembrolizumab, which is the rarer achievement: not an incremental
addition to a regimen, but a standard of care changing.

**NECTIN4 is `id 1` in this cohort.** It was the first target folded through this system's
production path, at mean pLDDT **77.26**. That is not a coincidence of ordering — it is the
target chosen deliberately, by an author who worked at the company that developed the therapy and
watched it reach patients.

**What that history contributes to this document is a standard, not a sentiment.** Understanding
*why* EV works — targeting, linker stability, payload release, and the specific properties of
NECTIN4 that make it a viable target at all — is what makes target selection legible as the hard
part. A tool that ranks candidate targets is only worth building if one believes the choice
matters. It demonstrably does.

**⚠ And the success case is a bad prior, which this project's own data already shows.**
NECTIN4 is well-expressed, accessible, and stable enough not to be simply switched off under
pressure. **Most candidates are not.** In this cohort of 42 folded targets, `mean_plddt` ranges
from **34.78 to 81.40**, and **45% fall below 60** — a region where the structure is not
reliably interpretable. EV proves the *mechanism*; it says nothing about how easy the next target
is. A tool built in admiration of the one that worked could quietly encode *"find me more
NECTIN4s"* — and the coverage line (D-024), the disagreement classes (D-015 §1a), and the
detection-not-explanation boundary (D-028) are the discipline that prevents exactly that.

**This is the through-line of the whole document:** conviction about the mechanism, precision
about the limits. The two are not in tension. The mechanism is proven and worth being excited
about; the target selection is where the difficulty actually lives; and a system that is honest
about which is which is the more persuasive artefact, not the more timid one.

### 7.4 Why this bounding is a strength, not timidity

The project's credibility rests on D-024's honest coverage line and D-028's refusal to explain
what it cannot support. **Onboarding copy that overclaims and then hands the reader a scrupulously
qualified coverage line two clicks later reads as compliance rather than conviction** — a careful
reader notices the seam, and it retroactively cheapens the honest surfaces.

Copy that is enthusiastic about the mechanism and precise about the limits is consistent with
every other surface in this UI, and it makes the tool's purpose sharper: **the mechanism is
proven; the target selection is where the difficulty actually lives.**

### 7.5 Structural changes from v1

- **Drop:** the interactive cancer-target database that pre-fills a "New Analysis" screen —
  **there is no new-analysis screen and no ingestion path.** The cohort is fixed at 82 (D-020).
- **Reframe:** "Begin Mission — Analyze a Cancer Target" becomes an entry point into the *cohort
  view*, which is what actually exists.
- **Add:** NECTIN4 as the worked example. It is a marketed ADC target, it is `id 1`, it folded at
  **mean pLDDT 77.26**, and it is the first structure the viewer renders. **The onboarding and
  the data agree** — the reader is shown a real target from a real approved therapy, folded by
  this system.

---

## 8. Build order

Ruled by the pre-work's dependency chain (read API → shell → single-target → ranking).

| Step | What | Blocked by |
|---|---|---|
| 1 | **Read API** (D-034) | — *(shipped, #52)* |
| 2 | App shell + API client | step 1 |
| 3 | **Target view** — viewer, confidence, provenance, boundary method | step 2 + **the confidence-band ruling (§10), which must land with this step, not "eventually"** |
| 3b | **The coverage supplier** — `GET /api/coverage` or a manifest export, its own entry | step 1 |
| 4 | **Coverage view + coverage-line component** | **step 3b** — see §3.3; the read API cannot supply it |
| 5 | Method-note page + ADC context | step 2 |
| 6 | **Ranking table + disagreement classes + attribution** | **the scorer** (D-027 → features → fit) |

**Steps 2, 3, 3b, 4, 5 are this arc. Step 6 is not**, and naming that prevents building a mock
ranking that gets thrown away. The centrepiece is real work that cannot start until features and
a fit exist.

**Step 3b is a supplier, not UI work** — it is a route on the existing FastAPI app, built
tests-first through the gate exactly as D-034 was. Sequence it early; step 4 cannot begin without
it, and building step 4 against the 42 folded rows would produce a coverage line that is
confidently wrong.

---

## 9. Non-goals — commitments, not omissions

Per D-028's discipline: *"A non-goal is a commitment, not an omission… so that a later iteration
adding [it] does so as a ruled change with its own entry, rather than as a feature that arrived
because the UI had space for it."*

- **No user accounts, login, or settings.** Public reads, no users table.
- **No on-demand folding from the UI.** Folds are enqueued by CLI, run by a worker the owner
  starts. **A page load must never trigger inference** — on a paid card that is a cost bug.
- **No arbitrary sequence input.** The cohort is fixed.
- **No mutation simulator, no pocket druggability scores, no report generation, no semantic
  search.** None is ruled; all are v1 aspirations.
- **No explanation of disagreement** (D-028), **no ordering by "interestingness"** — an
  explanation wearing a number.
- **No PAE visualization.** No route serves it (D-034).

---

## 10. Open questions for their own entries

- **⚠ The coverage-data supplier (§3.3) — blocks step 4 and is the largest open item.**
  `GET /api/coverage` or a build-time manifest export. The read API returns 42 folded rows and
  cannot supply the 82 denominator, the named exclusions, or the unfolded. Ruled before step 4,
  on D-034's discipline: decide shape and payload against the real `core/manifest.py` object,
  then build tests-first.
- **The confidence bands — must land with step 3, not "eventually."** §2's distribution (45%
  below 60) is why a bare `mean_plddt` is insufficient; the target view needs the bands to render
  at all. ESMFold pLDDT convention is a starting point, not an authority. A small ruling, but a
  blocking one.
- **pLDDT colour source, recorded so it is not reverted by reflex.** §6 colours from the
  `/plddt` array, **not** from the PDB B-factor column. ESMFold carries pLDDT in B-factors too,
  but whether the served `structure.pdb`'s B-factors are on the 0–100 or 0–1 scale is
  **unverified** — and S-001 cost real confusion on exactly that rescaling. The array is the
  known-good source.
- **JS toolchain pinning** — ruled in **D-037** (`package-lock.json`, `npm ci`, outside D-013's
  hash-verified guarantee).
- **DEP-001 amendment** — ruled in **DEP-006** (two-stage build, static-serve path).
- **What a green deploy means, again.** DEP-004 is amended by the first UI to ship. Today a green
  deploy still means transport-up-and-queue-accepting, and **not** that a UI is reachable.
