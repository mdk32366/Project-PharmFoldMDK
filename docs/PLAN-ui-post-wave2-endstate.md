# PLAN — UI after the Wave2 / PAE / hold-48 end state

**Decision:** [`D-117`](README.md) (confirm the `### D-117` header exists before citing).
**Date:** 2026-09-05 · **Status:** plan only. ⚠ **Not an implementation GO. Not a Kabsch GO.**
**Audience:** Matt (operator / owner). Reviewer and worker roles are named per surface.

> **Stance.** The stitcher is a **pLDDT assembler**, not a Kabsch superimposer. Known IGF2R
> seam ≈ **88.76 Å**. Kabsch / restitch Spec is **PARKED** until Matt GO. No surface may
> imply seams are scientifically solved. This document inventories what exists and what
> it now lies about. It does not ship UI.

---

## 0. Provenance (D-016) — two kinds of claim

**Ops numbers** below are **owner-verified 2026-09-05 PT** (task brief). They were **not
re-queried against Fly or RunPod** in the PR that landed this file. A later session that
needs them live must name a query or log line.

| Claim | Value | How known |
|---|---|---|
| Waves A/B/C1/C2 rental tiles | complete | owner closeout 2026-09-05 PT |
| C2 L=1656 | n=36, `has_pae=36`, `lack_pae=0` | same |
| PAE | retrieved to Fly Volume `pharmfoldmdk` | same |
| Pod | Terminated | same |
| RunPod remaining | ~$10.25 | same |
| `stitch_readiness` | live (#224 / D-116) | log + tree |
| Wave1 stitch | PASS 10 / FAIL 17 (false-ready incomplete cover) | D-116 / owner |
| Wave2 stitch | COMPLETE; `ready_n=17` attempted=17 PASS=17 FAIL=0 | owner closeout |
| Unique stitched parents (UI / end-state inventory) | **27 unique** = Wave1 PASS **10** + Wave2 PASS **17** | Architect review #225; do not use Wave2-only 17 as the closed-out parent count |
| First parent | job **2817** `Q9P273` mean_plddt=61.07 tiles=`[3673,3630]` | owner closeout |
| Dup-tile preference | use **3673/3674/3675**; spares **3693/3695/3696** unused | owner closeout |
| Stitcher | pLDDT assembler, not Kabsch | `core/hold48_stitch.py` |
| IGF2R seam | ~88.76 Å | owner analysis |
| Kabsch / restitch | PARKED until Matt GO | owner ruling |
| Assembler path | via Fly | owner closeout |

**Code-side inventory** is from the tree on the branch that added this file
(`ui/src/App.jsx`, `app/reads.py`, `app/read_routes.py`, `core/hold48.py`,
`core/census_unfolded.py`, `ui/src/censusSummary.js`, `docs/GUIDE-renting-hold48.md`).

---

## 1. What exists (and what does not)

There is **one public web app**: the React SPA at `https://pharmfoldmdk.fly.dev`, served
by the same FastAPI process (DEP-006). Seven nav routes + two detail routes. **No
Streamlit.** **No auth, no users, no admin.** Reads are unauthenticated; `/jobs/*` is
bearer-guarded and has **no HTML**.

| Kind | Present? | Where |
|---|---|---|
| Public React SPA | yes | `ui/` → `/`, `/targets`, `/target/:id`, `/coverage`, `/census`, `/census/:id`, `/scorer`, `/method`, `/about` |
| Job list / detail | **no** | worker routes only (`POST /jobs/claim`, artifacts, complete, fail, pae) |
| Stitch / review screen | **no** | laptop/Fly assembler + `stitch_readiness` CLI |
| Rental / hold-48 ops dashboard | **no** | [`GUIDE-renting-hold48.md`](GUIDE-renting-hold48.md) is the operator UI |
| Transport-health UI | **no** | Pane A `fly logs`; Pane C `worker.log` |
| Fail / open / claimed filters | **no** (no jobs UI) | TargetList has **tier** + search only; Coverage is 3-valued fold |
| PAE heatmap | **no** | `GET /api/analyses/{id}/pae` exists; React never calls it |
| Stitched-PDB viewer (named) | **no** | `StructureViewer` streams whatever `pdb_path` is stored |
| CLI TUI | **no** | argparse CLIs (`emit_tile_jobs`, `retrieve_rental_pae`, `stitch_readiness`) |
| FastAPI explorer | yes | `/docs`, `/redoc`, `/openapi.json` (framework defaults; excluded from architecture-contract) |
| Demo notebook | yes | `notebooks/miniature_NECTIN4.ipynb` (NECTIN4 only) |
| Papers / briefing surfaces | docs, not app | `docs/papers/surfaces/`; `/about` names questions only (D-094 am1) |
| External consoles | not in repo | Fly dashboard, RunPod, MPG |

`UI_Plan.md` (Streamlit) is **superseded**. `UI_Plan_v2.md` is original intent; this plan
and `D-117` win where they diverge (CLAUDE.md rule 3).

---

## 2. Verified end state the UI must now speak

Speak these as **categories**, not as a solved science story:

1. **Tiles exist** as first-class analyses (`hold48_kind=tile`, own `pdb_path` + `pae_json_path`).
2. **Parents** stay `jobs.tier` NULL until stitch policy says otherwise (D-111 / `stitch_succeeded`
   does **not** set `tier='rental'`).
3. **27 unique stitched parents** have an **assembled** PDB/PAE/pLDDT (pLDDT-overlap
   assembler) = Wave1 PASS **10** + Wave2 PASS **17**. Wave2's own batch result remains
   17/17 PASS. That is not a single forward pass.
4. **Dup tiles:** prefer the **lower** job ids; name the unused spares. Do not show both as
   two proteins.
5. **PAE is present** on hold-48 tiles (C2 36/36) and on assembled parents. `F-042`
   (2,690 census rows with no PAE on the **v1 artifact**) is still true *about that
   artifact*. A 404 copy that says "2,692 of 2,771 have no PAE" is no longer the ordinary
   case for a **new** tile row.
6. **Rental is over.** Pod Terminated. GUIDE must not read as "go rent a card."
7. **Mucins** remain `out_of_class` — zero PDB/PAE; not stitch-ready (`expected_n=0`).
8. **Cohort IGF2R** (tranche 0, job 57, CUDA OOM) is a **different measurement** from
   **census IGF2R tiles** (D-081). Both facts stay; neither substitutes for the other.
9. **Stitched ≠ ranking-eligible** (`D-109` ruling 7). Scorer / ranking set unchanged.

---

## 3. Surface inventory

Each surface: purpose · who · assumptions · gaps/lies · UX · priority · Kabsch park.

### 3.1 `/` Story — `Story.jsx`

| | |
|---|---|
| **Purpose / who** | Cold-open for a grader / reviewer: where the deep learning is. |
| **Assumes today** | Cohort fold counts from `/api/analyses` + `/api/coverage`. Census beat from `/api/census/summary` (live). Failed/excluded named. No tiles, no stitch, no PAE. |
| **Gaps / lies** | `census_summary` counts every census row with `pdb_path` + mean pLDDT. **Tiles inflate `folded`.** D-094 am1 already recorded Story-live vs `/census`-frozen; Wave2 makes the live number *wrong in a new way* (tile rows), not just newer. IGF2R can still appear in the "attempted and did not complete" clause (cohort coverage) while census tiles exist. |
| **UX** | Keep Story qualitative on stitch. If the census sentence stays, it must **exclude tiles** or say "N parent structures + M tile windows." Do not announce "we assembled 17 holoproteins" — the closed-out unique inventory is **27 unique** stitched parents (Wave1 PASS **10** + Wave2 PASS **17**). Name the assembler only if a later GO adds a one-line beat with the seam caveat. |
| **Priority** | **P0** if `census_summary` starts counting tiles as proteins (denominator lie on the most-read screen). Else **P1** (known live-vs-frozen hole). |
| **Kabsch** | If a stitch sentence is added: **"assembled by pLDDT overlap, not superimposed."** No "full-length structure solved." |

### 3.2 `/targets` TargetList — `TargetList.jsx`

| | |
|---|---|
| **Purpose / who** | Reviewer picker over the **82**. Rank default; tier filter; search. |
| **Assumes today** | Tranche-0 only (`list_analyses`). IGF2R is the CUDA-OOM singleton: hardcoded *"held out; fold subsequently attempted and failed (CUDA OOM)"*. Absent pLDDT is a trailing category. |
| **Gaps / lies** | Cohort IGF2R **is** still failed (job 57). The lie is **omission**: a reader concludes the protein has no structure, while census tiles / a census assembly exist under D-081. Hardcoded "CUDA OOM" will rot if a later cohort re-fold lands. No tile / stitch / PAE columns (correct for this population **if** the other fold is named). |
| **UX** | Keep the OOM on the **cohort** row. Add one clause: *"a later census tiling of this accession is a different span definition — see Census."* Do not link the census PDB into `/target/:id` (D-081). Do not mark IGF2R folded here because tiles exist. |
| **Priority** | **P1** (review honesty). Becomes **P0** if anyone treats the list as "IGF2R has no fold in the project." |
| **Kabsch** | Do not put a stitch badge on the cohort row. |

### 3.3 `/target/:id` TargetView + StructureViewer

| | |
|---|---|
| **Purpose / who** | Reviewer: 3Dmol cartoon coloured by `/plddt` array (not B-factor, S-001), confidence, provenance, scorer panel, two cancer sections. |
| **Assumes today** | One analysis = one single-pass fold. 404 structure = "this fold did not complete." No PAE fetch. Provenance is weights / recipe / environment (D-071 3-state). Rental env is ephemeral / unrecoverable (state 3). |
| **Gaps / lies** | Fine **for tranche-0 rows** that are still single-pass. Dangerous **if** a stitched parent `pdb_path` is ever served through this page without an assembler banner. `get_plddt_path` looks for `plddt.json` beside `pdb_path`; `write_stitched` writes `stitched_plddt.json` — a parent pointed at `stitched.pdb` **404s pLDDT** and the viewer fails or degrades. No download affordance; no seam label. |
| **UX** | Cohort pages: keep as-is + IGF2R cross-pointer (3.2). If a stitched id is reachable here: **P0 banner** before the viewer — assembler, not Kabsch; seam not solved; not ranking-eligible. Download: `stitched.pdb` + `stitched_plddt.json` + `stitched_pae.json` with those names. Do not colour from B-factor. |
| **Priority** | **P0** the moment a stitched PDB is on this route. Until then **P1** (IGF2R pointer). |
| **Kabsch** | Banner is mandatory. No "align domains" CTA. No seam-healed colouring. |

### 3.4 `/coverage` + `CoverageLine`

| | |
|---|---|
| **Purpose / who** | Reviewer: honest 82 denominator. 3-valued `fold_status`. |
| **Assumes today** | Tranche-0 join. Copy still says ranked-unfolded *"await a rental fold."* Excluded = named & oversize. |
| **Gaps / lies** | IGF2R stays `failed` (correct for cohort). FAT2 / MUC16 stay excluded-from-ranking (correct) but FAT2 is tileable and MUC16 is `out_of_class` — the note still reads like "too big to exist." "Awaiting rental" is **false** for hold-48 (rental closed) and **misleading** if any ranked-unfolded remain. |
| **UX** | Keep 3-valued fold on **this** population. Change "awaiting rental" → "not folded in the cohort" when `rankedUnfolded>0`. On IGF2R / FAT2 / MUC16 notes: one clause each — failed oneshot vs tiled census vs mucin never-ESMFold. No coverage-payload change required for the copy fix (D-094 am1 hole on coverage provenance stays D-110). |
| **Priority** | **P1** copy. **P0** if the line implies the 48 are still waiting on a card. |
| **Kabsch** | None. Do not mark coverage `folded` from a stitch. |

### 3.5 `/census` CensusView + CensusTable + `censusSummary.js`

| | |
|---|---|
| **Purpose / who** | Reviewer: unscored population (D-079 / D-087). Frozen literals + live table. |
| **Assumes today** | Tranche 5: **728 folded, 48 held** (`heldCause` D-090/D-109, measured **2026-09-02**). `REASON_COPY.above_local_ceiling` = *"waiting on rented capacity."* Table: accession / gene / span / topology / pLDDT / tranche / profile / stained. No tile / PAE / stitch columns. Default sort accession. Cap 200. |
| **Gaps / lies** | **P0 identity.** `list_census` has no `hold48_kind` filter → each complete tile is a folded row with the **parent accession** and **tile `span_aa`**. `unfolded_rows()` still emits the 48 parents (v1 features artifact has **zero** tranche-5 lines) → same accession can be NOT FOLDED **and** one or more tile rows. React key `r.id ?? r.accession` hides a collision only when ids exist; two tile ids = two rows that look like two proteins. Frozen **"48 held"** is false after Wave2. Profile / staining attach by gene and would **duplicate** across tile rows. |
| **UX** | **Phase 1 (P0):** project **one row per accession**. Parent if `pdb_path` (assembled); else "tiled, not assembled"; else NOT FOLDED with a **closed-rental** reason (not "waiting on rented capacity"). Badge: `single-pass` / `assembled (provisional)` / `tiles only` / `mucin — not folded`. Filter: those four + "has PAE" / "no PAE (F-042 class)." Do **not** default-sort by pLDDT. Tranche-5 literals: `planned 776` vs `in artifact 0` stay; replace `48 held` with owner-dated **tiles complete / 27 unique stitched parents (Wave1 PASS 10 + Wave2 PASS 17) / mucins 3 / remainder named** — or stop rendering the 2026-09-02 hold sentence until re-measured. |
| **Priority** | **P0** |
| **Kabsch** | Assembled badge = **provisional assembler**. Tooltip: "overlap by pLDDT; not superimposed; seam not solved." |

### 3.6 `/census/:id` CensusProteinView + CensusDetail

| | |
|---|---|
| **Purpose / who** | Reviewer: one census protein. Deliberately no scorer panel (D-089). |
| **Assumes today** | One fold or NOT FOLDED. `resolve_census_accession` = first census row with `pdb_path`. Viewer + confidence + topology + profile + HPA. No PAE. No tiles. |
| **Gaps / lies** | **P0:** accession can open a **tile** (1,656 aa) as the ectodomain. Status says "Folded — tranche 5" with no `hold48_kind`. Structural profile on a **tile** or **assembly** is a different object than on a single-pass fold (D-109 ruling 7) — showing it without a refusal/category is a premise. IGF2R unfolded card still tells the cohort OOM story and not the tiles. Mucin card should stay NOT FOLDED with `out_of_class`, not "waiting on rented capacity." |
| **UX** | Resolve **parent first**; tiles are children. Page sections: (1) identity + **kind badge**; (2) stitch-readiness (`expected_n` / `present_complete_n` / `missing` / `uncovered_n`) — ops numbers, not a GO button; (3) tile table: job id, window, status, PAE yes/no, **chosen vs spare** (lower id preferred; name 3693/3695/3696 unused); (4) viewer of **parent assembled** PDB with assembler banner, **or** a tile viewer explicitly titled "tile *i* of *n*, residues a–b"; (5) downloads named `stitched.*` vs `tileN.*`; (6) profile: **refuse or category** on assembled/tile until a commensurability GO; (7) empty states: mucin / not ready / tiles-only / assembled-provisional. |
| **Priority** | **P0** resolve + badge. **P1** tile table / readiness / downloads. |
| **Kabsch** | Viewer banner. No superimpose control. Seam Å is a **measured caveat** (IGF2R ~88.76), not a "fix seams" CTA. |

### 3.7 `/scorer` ScorerView + TargetScorerPanel

| | |
|---|---|
| **Purpose / who** | Reviewer: F-004 at reduced scope. |
| **Assumes today** | Frozen pre-registered run. Census not scored. |
| **Gaps / lies** | Ranking set must **not** grow by the **27 unique** stitched parents (Wave1 PASS **10** + Wave2 PASS **17**). Silence is correct **until** someone adds those rows. |
| **UX** | One method-note line if assembled PDBs become visible elsewhere: *"The 27 unique stitched parents (Wave1 PASS 10 + Wave2 PASS 17) are not in this ranking (D-109)."* No new columns. |
| **Priority** | **P1** (one sentence when census shows assemblies). Else P2. |
| **Kabsch** | Do not imply assemblies are now rankable. |

### 3.8 `/method` MethodNote + ArchitectureDiagram + `system-model.json`

| | |
|---|---|
| **Purpose / who** | Reviewer: claims, non-goals, topology. Diagram pinned to live routes. |
| **Assumes today** | External GPU = "Local GPU worker" + **"Rented A6000."** Routes include `/pae` (worker + read). Copy: "rented A6000 pull jobs." |
| **Gaps / lies** | Hold-48 ran on **RTX PRO 6000 Blackwell**, not the A6000. No stitch / tile / assembler node. `/api/.../pae` is in the model but the UI does not consume it — the diagram can imply a PAE **figure** exists. |
| **UX** | Relabel rental node **"Rented GPU (A6000 cohort 29 · Blackwell hold-48)"** or split nodes. One sentence: assembler-only stitch; Kabsch parked. Do not draw a "structure alignment" box. |
| **Priority** | **P1** (educational premise). |
| **Kabsch** | No alignment box. |

### 3.9 `/about` AdcContext

| | |
|---|---|
| **Purpose / who** | Reviewer / student: ADC mechanism; 82 is a comparator; paper **questions** only. |
| **Assumes today** | Comment still names "the 48 hold." "What's next" is MSA / AF2-class, not-built (D-107). |
| **Gaps / lies** | Low user-visible lie (comment). Mechanism graphics unchanged. |
| **UX** | Do not add a Wave2 results section. Optional: "oversized proteins were tiled and assembled; that is not this page." |
| **Priority** | **P2** |
| **Kabsch** | None. |

### 3.10 Shared widgets (Confidence, PlddtExplainer, Provenance, Glossary)

| | |
|---|---|
| **Purpose / who** | Reviewer: pLDDT literacy; PAE named as the domain-arrangement metric. |
| **Assumes today** | Single-pass. Explainer: "High pLDDT with poor PAE is a real trap" — and **no PAE is shown**. "Nothing on this site has been re-folded under an alternative method." Provenance has no `hold48_kind` / stitch fields. Glossary defines PAE. |
| **Gaps / lies** | After Wave2, "alternative method" is incomplete: **assembly is a second construction** of coordinates. PAE-without-a-figure is the D-110 hole; for assemblies, off-block **null** is a third fact (never shared a forward pass). Mean pLDDT on an assembly is a **winner-tile** mean, not one pass. |
| **UX** | Explainer addendum **only on assembled/tile pages**: assembler; null off-block ≠ "domains independently placed in 3D"; seam Å if measured. Provenance: `hold48_kind`, parent job, tile window, chosen tile ids, `stitch_readiness` snapshot. Confidence header on assemblies: **"Assembled-chain pLDDT (winner tile per residue)."** |
| **Priority** | **P1** on protein pages that show assemblies. Explainer-only change on cohort pages is P2. |
| **Kabsch** | Explainer must not say PAE "will be fixed by alignment." |

### 3.11 Read API (not a page, but the UI's premises)

| Route | Today | Post-Wave2 gap | P |
|---|---|---|---|
| `GET /api/census` | all `pdb_path` + unfolded artifact rows | tile leak; no kind | **P0** |
| `GET /api/census/summary` | counts those rows | tile-inflated `folded` | **P0** |
| `GET /api/census/{id}` | first `pdb_path` | may be a tile | **P0** |
| `GET /api/analyses/{id}/structure` | stored `pdb_path` | may be tile or assembled; no Content-Disposition honesty | P1 |
| `GET /api/analyses/{id}/plddt` | sibling `plddt.json` | **name mismatch** vs `stitched_plddt.json` | **P0** if parent points at `stitched.pdb` |
| `GET /api/analyses/{id}/pae` | 404 copy cites F-042 2,692/2,771 | ordinary case for **tiles** is 200; copy is stale | P1 |
| `GET /api/coverage` | tranche 0 | IGF2R failed remains correct | P1 copy only |
| `GET /api/ranking` | valid preregistered run | must not absorb assemblies | P1 guard (already true if no new persist) |

No `GET /api/jobs`. No `GET /api/stitch`. No readiness route. That is fine until a review
UI is a GO — Phase 2 can join `stitch_readiness` server-side or keep it CLI-only.

### 3.12 Operator surfaces (Matt / worker)

#### GUIDE-renting-hold48.md — **the** hold-48 UI

| | |
|---|---|
| **Who** | Matt (operator). Worker follows paste blocks. |
| **Assumes today** | Rental **live**: clean-card cold start, emit GO, Step 0 balance, C2 15 h, Step 11 **local** stitch, parent 3356 still NULL, IGF2R tiles 3589/3590, "not a stitch GO," `$14.17` historical, ~$50 envelope. |
| **Gaps / lies** | After closeout this reads as **open procedure**. Step 11 does not mention Wave2 17/17, the **27 unique** stitched parents (Wave1 PASS 10 + Wave2 PASS 17), parent 2817, dup-id preference, or Fly assembler. Kill-switch table still "when unsure, don't Terminate" as if a pod exists. |
| **UX** | **Banner at top (P0):** rental E2E **CLOSED** 2026-09-05 PT; pod Terminated; do not Deploy; do not emit. Move the live runbook under **"Historical — do not run unless Matt re-opens rental."** New "Review" section: Wave2 17/17 PASS (batch); **27 unique** stitched parents = Wave1 PASS **10** + Wave2 PASS **17**; prefer 3673/3674/3675; `stitch_readiness` before any re-stitch; assembler-only; Kabsch parked; UI plan = this file. Money line: ~$10.25 remaining (owner figure; re-glance before any new rent). |
| **Priority** | **P0** |
| **Kabsch** | Step 11 must say **assembler only**; Kabsch parked; no "fix the 88.76 Å seam" procedure. |

#### GUIDE-renting-the-a6000.md

Historical cohort-29 path. Already points at the hold-48 guide. **P2:** one line "hold-48 rental closed; do not use this file for T5 tiles."

#### BUDGET-hold48-tiers-2026-09-04.md

Forecast / wave mix. **P1** for ops: stamp "superseded as a live forecast by 2026-09-05 closeout; keep as the pre-run model." Do not silently edit measured walls.

#### CLI (no TUI)

`python -m scripts.retrieve_rental_pae`, `core.hold48.emit_tile_jobs`, `stitch_readiness`, `write_stitched`, `worker.main`. **P1** docs: print chosen-vs-spare tile ids; refuse stitch unless `stitch_readiness.ready`; warn assembler-not-Kabsch. **P2** to wrap in a TUI.

#### FastAPI `/docs`

Operator/debug. PAE 404 text is a premise. **P2** unless someone uses it as the review UI.

#### Demo notebook

NECTIN4 single-pass. **P2:** one cell "census assemblies are a different object."

#### Fly / RunPod / MPG consoles

External. **P2** in-app health. Pane A/C remain the transport view.

#### `docs/papers/` and keel

Not operator UI. Do not put Wave2 numbers in a paper surface without a P-NNN gate.

---

## 4. Cross-cutting P0 / P1 / P2

### P0 — misleading or dangerous (do first)

1. **Census identity:** one row per accession; never a tile as a protein. Fix `list_census` + `resolve_census_accession` + React keys.
2. **`census_summary` / Story** must not count tiles as folded proteins.
3. **Stop "48 held" / "waiting on rented capacity"** on `/census` and unfolded copy.
4. **GUIDE hold-48 CLOSED banner** — do not invite another Deploy.
5. **Assembler / seam disclosure** on any 3D view of a stitched PDB (and refuse Kabsch language).
6. **`plddt.json` vs `stitched_plddt.json`** if a parent `pdb_path` points at `stitched.pdb` — otherwise the viewer silently degrades.
7. **Dup tiles:** never two protein rows; prefer lower ids 3673/3674/3675.

### P1 — needed to review Wave2

1. Parent page: kind badge, readiness counts, tile table, chosen vs spare, PAE present/absent.
2. Downloads named `stitched.*` / `tileN.*` with provenance.
3. IGF2R **two populations** on Targets + Coverage + census card (OOM vs tiles; D-081).
4. Coverage / CoverageLine: drop "awaiting rental" as the default not-folded gloss.
5. Method diagram: Blackwell + assembler-only sentence.
6. Scorer one-liner: assemblies not in F-004.
7. Confidence / Provenance / Explainer addenda **on assembled/tile pages**.
8. PAE route 404 copy: F-042 is about the **old census artifact**, not "tiles have no PAE."
9. GUIDE Review section + BUDGET "historical forecast" stamp.
10. Structural profile: refuse or category on tile/assembly (D-109).

### P2 — nice

1. PAE heatmap with D-110 provenance (null off-block visible, not coloured as 0).
2. Job-queue screen (fail/open/claimed). Not required for Wave2 review if GUIDE + SQL stay.
3. Transport-health dashboard.
4. In-app rental money widget (GUIDE already forbids fake precision).
5. Notebook / About / A6000-guide one-liners.
6. MSA "what's next" remains correct; do not replace it with Kabsch.

---

## 5. Kabsch park — what must stay provisional

Until Matt GO on a restitch spec:

| Must stay labelled provisional | Must not ship |
|---|---|
| Any assembled PDB in 3Dmol | "Aligned," "superimposed," "seams solved," "full-length AF-quality" |
| Winner-tile pLDDT as chain confidence | Treating it as one forward pass |
| Block-diagonal PAE with null off-block | Colouring null as 0 (that was the D-111 refuse) |
| IGF2R ~88.76 Å seam | A "fix seam" button or silent Kabsch |
| D-109: not ranking-eligible | Adding the **27 unique** stitched parents (Wave1 PASS **10** + Wave2 PASS **17**) to `/scorer` |
| Dup-tile choice (lower id) | Implied scientific preference beyond "first complete cover" |
| Mucin `out_of_class` | A fake assembled mucin |

A later Kabsch GO is its own `D-NNN`. This plan does not pre-authorise it.

---

## 6. Phased plan Matt can act on

### Phase 0 — this PR (done when it merges)

- [x] `### D-117` in the log
- [x] This plan
- [x] `ARCHITECTURE.md` end-state note
- [ ] **Not in this PR:** UI, Kabsch, Fly, enqueue

### Phase 1 — honesty GO (P0) — next implementation entry

**Goal:** a reviewer cannot mistake a tile for a protein or a closed rental for an open one.

⚠ **D-118 is the BUILD GO for this phase's P0 items only.** Kabsch stays parked.

1. Read-API projection: `hold48_kind`, parent/tile/assembled/mucin; `list_census` **one row per accession**.
2. `resolve_census_accession` prefers parent, never an arbitrary tile.
3. `census_summary` uses the same projection.
4. Replace tranche-5 "48 held" + `REASON_COPY` rental-waiting language (dated, sourced).
5. GUIDE CLOSED banner + historical collapse.
6. Viewer: assembler banner **if** `pdb_path` is assembled; fix pLDDT sibling path.
7. Tests **first** (D-117 consequence): parent + two tiles → one census row; accession opens parent.

⚠ New `D-NNN` **before** this code. No Kabsch. No ranking ingest.

### Phase 2 — review GO (P1)

**Goal:** Matt can audit Wave2 on `/census/:id` without SQL.

1. Tile table + readiness counts + chosen/spare ids.
2. Downloads + PAE present/absent badge (not a heatmap).
3. IGF2R two-population copy on Targets / Coverage / census card.
4. Method + Scorer + Explainer/Provenance addenda.
5. BUDGET / GUIDE Review appendix.

### Phase 3 — optional (P2) — only if Matt wants it

- D-110 PAE figure (nulls visible).
- Jobs / transport screens.
- Notebook / About polish.

**Explicitly out of phase 1–3:** Kabsch, restitch, ranking-set expansion, mucin folding, MSA.

---

## 7. Matt checklist (prioritized)

Copy this into a session note. Check means "done in a later GO," not in D-117.

**P0**

- [ ] Census list cannot show two rows for `Q9P273` (parent 2817 / tiles 3673+3630)
- [ ] `/census/Q9P273` opens the **parent / assembled** story, not tile 3673 alone as the protein
- [ ] Story folded-count does not jump by tile cardinality
- [ ] `/census` does not say 48 held or "waiting on rented capacity"
- [ ] GUIDE-renting-hold48 opens with CLOSED / do-not-Deploy
- [ ] Any stitched 3D view says **assembler, not Kabsch**; seam not solved
- [ ] Spare tiles 3693/3695/3696 are not a second protein
- [ ] pLDDT loads for an assembled parent (`stitched_plddt.json` or equivalent)

**P1**

- [ ] Parent card shows readiness `expected_n` / missing / uncovered
- [ ] Tile table with PAE yes/no and chosen-vs-spare
- [ ] Downloads: `stitched.*` vs `tileN.*`
- [ ] IGF2R cohort OOM and census tiles are both named, neither substituted
- [ ] Coverage drops "awaiting rental" as the not-folded gloss
- [ ] Scorer states assemblies are outside F-004
- [ ] Method diagram does not say the only rental was an A6000
- [ ] Structural profile does not treat an assembly as a single-pass measurement

**P2**

- [ ] PAE heatmap with null off-block provenance (D-110)
- [ ] Jobs UI only if SQL/GUIDE is no longer enough
- [ ] Kabsch still parked unless a new GO exists

---

## 8. What this file is not

- Not a licence to implement UI in the same PR as D-117.
- Not a licence to run Kabsch, restitch, or re-open rental.
- Not a re-measurement of Fly. Ops integers stay attributed to the 2026-09-05 PT closeout
  until someone names a new query.
- Not a replacement for `UI_Plan_v2.md`. That file remains original intent; this file is
  the post-Wave2 honesty plan.
