# PharmFoldMDK — Architecture

> **Living document.** This file is the single source of truth for how PharmFoldMDK
> is built and why. It MUST be updated **in the same change** that alters the
> architecture, and it MUST be brought current **before any PR is filed**. If a PR
> changes structure, data flow, dependencies, or deployment and does not touch this
> file, the PR is incomplete. See [`docs/README.md`](docs/README.md) for the
> chronological log of individual design decisions.

**Project**: PharmFoldMDK — an Antibody-Drug Conjugate (ADC) target exploration platform.
**Context**: Graded coursework for a **Deep Learning** class in an ML Master's program.
**Status (2026-07-23)**: Infrastructure complete and proven on real engines — the job queue
(D-009 §1, proven on Postgres 16 incl. `SKIP LOCKED`), migrations + pgvector (D-017/D-019), and
the GPU-tier **fold-runner** (`worker/runner.py`, D-018). Cohort measured (D-020); boundary/tier
decisions ruled (D-021/D-022). The **orchestrator manifest** (D-023, `core/manifest.py`) turns the measured cohort into a
deterministic, reviewable routing table plus the D-024 structured coverage object; the **enqueue**
(D-026, `core/enqueue.py`) turns each foldable row into a `protein_analyses` row (the exact
residues + UniProt release + folded span) and a `pending` `jobs` row carrying the tier's fold
recipe — 80 of 82 enqueue, the 2 named exclusions get none, idempotent per cohort version. The
**worker's job-pull loop** (D-030, `worker/orchestrator.py`) is built as a pure, transport-agnostic
loop over an injected client protocol (claim → fold → upload → complete, with server-side
done-ordering and the transport/fold-failure taxonomy). The **Fly transport** (D-031, `app/` +
`worker/http_client.py`) now realizes that protocol over HTTP: **five** routes (claim / artifacts /
complete / fail / **pae**), one shared bearer token, the upload route writing the post-fold columns
in a compensated Volume+DB transaction, `/complete` enforcing done-ordering server-side (409 until
`pdb_path` commits), and **`pae` (D-036)** storing the rental tier's out-of-band PAE +
`pae_json_path` in that same compensated boundary. It merged as the first PR under the now-**required** Postgres check (D-032).
The **deployment arc** (DEP-001…004) then wired the Fly serving tier: a Docker image — **two-stage
since DEP-006** (a `node:20-slim` stage compiles the React bundle; **Node never enters the runtime
stage**) — whose runtime tier is `app/` + `core/` + `db/` + `data/` (the cohort CSVs the D-038
coverage route computes from), the hash-locked lock, **no `worker/`/CUDA** (DEP-001, enforced by an
image-contents test that also pins the two-stage shape), a `fly.toml`, and a `deploy` job that runs `flyctl deploy --app pharmfoldmdk`
behind a doc-only guard on the job (DEP-002) with an app-scoped `FLY_API_TOKEN` (DEP-003). A green
deploy means **the transport API is up and the queue accepts work — not** that any fold has run
(DEP-004); the worker is hand-started on the GPU box. The UI was ruled **React**, superseding
D-004's Streamlit clause (D-033). The **read API** (D-034, `app/read_routes.py` + `app/reads.py`)
is the UI arc's first build — the supplier React consumes: **seven** public `GET /api/*` routes (the
sixth, `associations`, added by D-053). Four
over the 42 landed local folds (a light `analyses` list, a full `analyses/{id}` record with
`fold_provenance`, a streamed `analyses/{id}/structure` serving the stored `pdb_path` as
`text/plain`, an `analyses/{id}/plddt` array, and an `analyses/{id}/pae` stream serving the stored
`pae_json_path` — ⚠ read-only, and a **404 is the ordinary case**: 2,692 of 2,771 rows carry no PAE
at all, which is `F-042` recorded rather than a missing file. ⚠⚠ It exists so an analysis question
about the 79 cohort matrices is answered **through the gate** instead of by reaching into the
production filesystem, which is the shape `KEEL V8-a` closes); and **`coverage`** (D-038) — the D-024 coverage
object computed from `core/manifest.py` over **all 82**, joined to `protein_analyses` (and, D-043,
to `jobs`) for a three-valued `fold_status` — `folded` / `failed` / `not_folded`, so attempted-and-
failed is shown as distinct from never-attempted — i.e. the honest denominator the fold-derived list
structurally cannot give.
**Reads are unauthenticated** (public UniProt structures, no PII); the
four worker routes stay bearer-guarded — an asymmetric posture pinned by a route-introspecting test
(`/jobs` guarded, `/api` open, no third category). No PAE route (D-034 decision 3).
The **React bundle** (DEP-006; `ui/`, Vite build) now ships in that image and is served by the same
FastAPI app under `/` — **one process, two things** — with `/api`/`/jobs` matched *before* the SPA
fallback (route ordering, asserted). Its JS toolchain is pinned by `package-lock.json` + `npm ci`
(D-037): a **third dependency world** outside D-013's hash guarantee, acceptable because it is
build-time only (like D-018's GPU tier). **D-046 adds a test harness to that world** — `vitest` +
`@testing-library/react` + `@testing-library/jest-dom` + `jsdom` as **devDependencies**, run by the
gate's `test` job (`npm ci && npm run test` in `ui/`); these are *weaker still* than build-time deps
(neither runtime nor bundle-output), and the image-contents test guarantees none of them cross the
stage boundary into the runtime image. **A green deploy now means a UI is reachable** (DEP-004
amended). PR A shipped the shell; **PR B the single-target view** — a 3Dmol.js structure coloured
per-residue by pLDDT from the `/plddt` array (**not** the PDB B-factor column, whose scale is
unverified — S-001), a confidence element with the D-039 bands and the cohort-max caveat, and a
provenance panel that makes "we ran ESMFold ourselves, at a named revision" checkable. 3Dmol is a
lazy-loaded chunk (the list page stays ~57 KB gzip). **PR C the coverage view** — the honest
`ranked ∧ folded` line (computed client-side from `/api/coverage`'s `disposition` + `fold_status`,
never the manifest's ranked count nor the raw folded count, D-024/D-050), the full-82 drill-down with
held-out/excluded reachable by name (D-022), a method note (D-028 non-goals as commitments), and
the ADC-context onboarding (UI Plan v2 §7). That **closes UI Plan v2 steps 2–5**; the ranking table
(step 6, the demo centrepiece) waited on the scorer (D-027 → fit) and is deliberately not mocked.
**D-062 lands step 6 — the `Scorer` surface (sixth nav)** rendering the pre-registered result (F-004)
from a new `GET /api/ranking` route (`reads.ranking_payload`: the latest **valid** run — the
zero-positive `ranking_results` id=1 is marked invalid, D-064 dec 3, and never served — with a
four-valued `result_status` `complete`/`partial`/`raised`/`not_run`; the route also filters
`run_kind='preregistered'` — D-065 — so a sensitivity ablation is never served as the result). `ScorerView.jsx` renders five
sections (cascade → labels → pre-registration → result → reduced ranking table with its coverage
line); the ranking table is real scores at reduced scope (rank · symbol · score · excluded-set-with-
reasons), with baseline/delta/disagreement/attribution **named as deferred, not mocked** (β·x
attributions are stored in `target_scores`, a display gap not a data gap). Every number — 12, 22, 56,
8, the median, the Spearman — is derived from `/api/ranking`, never typed (Constraint A); the
mean/median reversal is rendered and caveat (b) (the pLDDT-attention confound) travels with the
result. The route is the **fourth** firing of the D-051 architecture-contract test (live route →
`system-model.json` updated in the same PR). **D-055/D-062 amendment (2026-07-29):** the surface is
**two-column** (explanation A–D left, the ranking table + coverage line right; stacks on narrow, with
the coverage line still preceding its table and caveat (b) still following the result in DOM order),
terms decode via **in-situ `Term` tooltips** (a focusable `<button>` + `role="tooltip"`, keyboard/tap
not hover-alone; the glossary page is retained as a secondary index and its contract guard unchanged),
and caveat (b) is updated per **F-005** — the specific attention mechanism is **not supported** and an
order-versus-disorder question replaces it; the ranking is noted as substantially pLDDT-driven so the
`structural score` definition does not imply the geometry features do the work.
**D-066 amendment (2026-07-29):** `CoverageLine` no longer asserts what the *ranking* covers — the
forward-looking *"once the scorer exists — covers these N"* clause is **removed** (it was false on
`/scorer`, 67 ranked & folded above a 56-row table, and unverifiable on `/coverage`), so the shared
component states only the **D-024 partition** on both surfaces, asserted by an absence test. The
scorer supplies its own **67 → 56 reconciliation** (ranked & folded → above the pLDDT-50 floor)
immediately above its table, all three numbers derived — a denominator that travels with its claim.
The right column is reduced to **coverage box (partition + named exclusions) + table**: the intro
paragraph is removed, the F-005 pLDDT-driven note and the observed score range (min/median/max) move
into a new **`Score`-column tooltip** distinct from the `structural score` `Term`, carrying the
non-calibration claim boundary (**F-006** — the score is *not* a calibrated probability, calibration
never tested), and the deferred-columns note moves under section D. Vocabulary fixed (D-066 dec 4):
**`ranked`** is the D-024 disposition (over 82); the ranking's membership is **`rankable`** (56). The
absence set (Constraint A) extends to `0.116`/`0.220`/`0.285`/`67`.
**D-068 lands the target scorer panel.** `TargetView` gains `<TargetScorerPanel>`, which closes the
loop from the ranking table back to the per-target page: the judgement that ranked it, or — the common
case — a **reasoned "no score", never a blank** (dec 1). `targetStatus()` (pure, `ui/src/targetScore.js`)
resolves a target to one of five states with **fold state preceding disposition** (owner ruling: no
fold → no measurements → no disposition applies; so IGF2R, fold-failed and held-out, reads *not folded*,
not *held out*): `not_folded → held_out → below_floor → ranked → unranked_unexplained` (the last a
defensive named state; a partition test pins the four buckets summing to the cohort with the fifth at
zero). **Precedence amended 2026-07-29** — held_out (pLDDT-independent) precedes below_floor, realigning
the UI with the backend `_exclusion_reason` after the walk caught TMEM108 labelled two ways on two
surfaces; not_folded still leads (IGF2R). Every number is
**derived from `/api/ranking` + the target's own record, joined client-side by accession/gene — no route
change, no `system-model.json` edit** (§1 report). A score never renders without its rank-of-56 and
min/median/max context (dec 2); a **labelled** target shows both its in-fit score and its out-of-sample
LOO percentile, marked labelled (dec 4); F-005's ambiguity is the **shared `<PlddtAmbiguityNote>`
component** (D-069 dec 2 — one source, also rendering on Scorer's caveat (b), so the claim can't drift).
Bounded per D-028/F-006/D-041: no biology, no probability, no "promising". **MethodNote's "attribution
not yet rendered" line is corrected in the same PR** (dec 5) — rendering it here made that sentence
false. Adjacent: **D-045 Phase-2 pod CUDA verification discharged by measurement** (07-25 folds carry
`cuda_version`/`device_name`; the `Provenance` post-D-045 test already gate-locks the display path).
**D-048 then lands UI-depth §3** on the D-046 harness (tests-first, 26 UI tests green): the
provenance panel renders D-045's two populations honestly — captured environment shown, absent
environment read as *"not captured"* with a single population-level note, never as a value or a
bare em-dash (D-046 §3); tier is legible and filterable in the list (local int8 vs. rental fp16,
never blended, D-028); a per-residue pLDDT spread sits beside the mean (the model's own confidence
varying across the chain, hand-rolled SVG, D-037); and the D-039 band scheme is re-pinned as a
single source of truth (structure and legend cannot disagree), with the numeric re-justification of
the 60 line against the enlarged live cohort left as a named owner action (D-016 — the individual
`mean_plddt` values live in Postgres, not a repo artefact, so they are not fabricated here).
**Confidence is then DEMOTED on the list (2026-08-03, un-gated honesty fix).** The band vocabulary was
always careful — *"Confident **backbone**"*, *"backbone unreliable"* — but the list undid it: a bare
`Confidence` header beside a traffic-light dot, as visually prominent as the identity columns, which at
a glance reads as a verdict on the **target** rather than a check on the **fold**. Three changes, none
removing a value: the header is qualified (**`Fold confidence`**), the dot becomes visually secondary
to identity (`.dot-secondary`/`.col-secondary` — one semantic class, because prominence was itself an
owner ruling under D-039/D-048 and the treatment stays owner-reserved), and one line states what
confidence is **not** (*"not a judgement of whether the target is a good ADC candidate"*). **Demotion
is not deletion** — every value, band and colour still renders, and the detail-view confidence layer
(`Confidence.jsx`, `PlddtPlot`, `PlddtSpread`) is untouched, as are the D-039 boundaries `70/60/50/0`.
**The target-quality slot is reserved, not filled:** the structural-suitability score is gated on the
D-075 result, so this stops confidence *impersonating* it without supplying it — asserted by a denylist
test (no `suitability score` / `good target` / `recommended` / `promising` language on the list).
**The list then becomes SORTABLE, and the `?? 0` coercion is removed (2026-08-03).** Every existing
column is click-to-sort (asc → desc → back to the default, which stays **pLDDT desc** so the
ceiling-at-a-glance read survives), with the active column and direction announced through `aria-sort`
on the `<th>` — an unlabelled sort is a silent reordering. Ordering lives in **`ui/src/sortRows.js`**,
unit-tested away from the DOM, so the census's future columns become new sort keys in a proven
mechanism instead of a retrofit. **Fold confidence has no sort control of its own** — it is a band *of*
mean pLDDT, and a second control would be two axes for one quantity. ⚠ **The load-bearing rule is that
an absent value is a CATEGORY, never a low number.** The previous
`(b.mean_plddt ?? 0) - (a.mean_plddt ?? 0)` coerced a missing measurement to zero, so an unmeasured
target sorted as the *worst* — and this was **live, not latent**: IGF2R sits on the deployed list with
`mean_plddt: null` because its fold hit a CUDA OOM at 2,491 aa. Absent rows now form a trailing cluster
in **both** directions (absence is off the axis, not at an end of it), are never dropped, and are
distinguished from a measured `0`. Each states its **real** reason — `fold_status` + `fail_reason` from
`/api/coverage`, joined client-side by accession (the D-068 `TargetScorerPanel` pattern: **no route
change, no `system-model.json` edit**) — because a generic dash over a specific failure is exactly the
smoothing this project refuses. The coverage join is **additive**: a supplier failure degrades the
reason text, never the list, asserted by test.
**F-009's cohort boundary then reaches the surface (2026-08-03).** Both `/about` and `/scorer` presented
the Kathad 82 as *"the cohort"* with no statement that it is an **expression-and-selectivity selected
comparator, not a census** — leaving a reader to assume the ranking speaks to the whole ADC target
space, when it re-orders a fixed list. `AdcContext.jsx` gains the paragraph (the primary home: it
already derives its cohort stats live, D-050/D-051) and `ScorerView.jsx` §A's cascade line gains a
one-line qualifier that **links to About rather than restating it**, so the framing has a single source
and cannot drift between two surfaces. The four example targets — CD30, CD33, CEACAM5, Trop-2, each the
antigen of an approved or late-phase ADC — are **derived, not inscribed**: they live in
`ui/src/heldoutExamples.js` and `heldoutExamples.test.js` asserts every `gene_symbol` + accession
appears in `data/heldout_positives.csv`, whose accessions came from UniProt. ⚠ **The over-claim guard is
a denylist test, not an editorial habit** (F-009 §3): the note indicts the *comparator's* completeness
and must never imply the scorer would surface these targets — they are unfolded and unscored, and
CD30/CD33 are attention-rich, the exact confound D-075 exists to test, so implying validation would
pre-empt a sealed pre-registration. Two lessons are recorded in the test itself: the denylist is scoped
**specifically** to the scorer/axis/ranking (a broad `proves the…` pattern fired on the shipped, correct
*"enfortumab vedotin proves the mechanism"*), and the copy **avoids the banned vocabulary outright
rather than negating it**, because a phrase-level guard cannot distinguish a claim from a disclaimer and
should not have to. The existing confound layer — `PlddtAmbiguityNote`, the *"find me more NECTIN4s"*
caveat, `ScorerView`'s negative-outcome text — is untouched; no route added, `system-model.json`
unchanged.
**D-070 then D-071 make provenance THREE-valued:** an uncaptured fold first gained a *"what we can
say"* block (tier + folded_at + the worker manifest **by name**, never its contents — D-070); D-071
then splits *uncaptured* into **measured-later** and **absent**. The detail projection gains a
`tier_environment` field (`app/reads.py`, keyed by `tier` from `data/tier_environments.json` — a field
on the existing route, no new route, no `system-model.json` change). **State 1** (fold-time capture)
renders the four fields unqualified; **state 2** (the local box measured after the folds — one reading
for all 42 local folds) renders them **with a "measured {date} — not recorded at fold time" qualifier**
(D-070 dec 2 amended: a *measurement* may enter the fields, an *inference* never can — F-007 is why);
**state 3** (the ephemeral rental pods, gone) renders one statement, not a four-field grid, plus D-070's
block. **Rental gets no state-2 record by construction** (decision 3) — ephemeral compute costs
provenance you cannot get back. This makes **F-008's two-precision confound checkable on the surface**.
The local measurement matched the pin exactly, closing F-007's *"unknown, not fine"* local bound.
**D-051 adds the narrative surfaces and moves the nav to five by absorption** (not addition — UI
Plan v2 §3's four-surface constraint is honoured, D-028 §9): a **Story** cold-open at `/` (the
research question, that *we ran ESMFold ourselves*, and what came out — every cohort number derived
from `/api/analyses`+`/api/coverage`, never a literal, Constraint A / D-050), with the target list
moved to `/targets`; and an **architecture diagram absorbed into `/method`**, rendered from a
committed **`ui/src/system-model.json`** rather than hand-drawn. `tests/test_architecture_contract.py`
walks the live FastAPI route table and asserts **set-equality in both directions** with the model's
declared `/api`+`/jobs` routes — adding or removing a route reddens the gate until the picture is
updated (the `test_image_contents.py` pattern of reading a non-Python artefact as its subject). Its
load-bearing claim is the **topology**, pinned too: inference runs on the GPU tier *outside* Fly
(D-004); the serving image is GPU-free (DEP-001). Two D-050 follow-ups close here — `AdcContext`'s
NECTIN4 pLDDT is now derived (the last hardcoded per-target literal), and `CoverageLine`'s
zero-`rankedUnfolded` wording. **Named Constraint-A gap, deferred (freeze push 2026-07-29):**
`plddt.js`'s `COHORT_MAX_PLDDT = 84.23` is a cohort statistic typed as a module constant — it is
**rendered only** (the top-band caveat string; the band boundaries are 70/60/50/0, so it sets no
threshold), and deriving it would thread a data source into a currently source-free pure module for a
value correct today. Recorded here beside the former NECTIN4 `77.26` literal rather than converted on
freeze day.
**D-053 adds per-target cancer associations** — a sixth public read route `GET /api/associations`
served by the pure file-derived supplier `core/cancer_associations.py` (mirrors `adc_reference.py`:
rejects an uncited row, validates `qh_score`, groups sorted-descending, flags cohort-join misses),
rendered by a `CancerAssociations` panel in `TargetView`. Derived from the Kathad S3 quasi-H-score
grid at the paper's 150 cutoff — **337 pairs across all 82 targets**; *our* derivation, agreeing with
the paper's OSMR figure and disagreeing with its 290/16 headline (recorded as a finding, not
reconciled away, D-053 dec 3). An **expression** claim, labelled as such on screen — not causation,
not indication — in a palette deliberately distinct from the pLDDT bands (a different quantity, §2a).
**D-054 records the evidence baseline as a deliberate deferral with a trigger** (the published 17-of-82
comparator stays unsurfaced until there is a ranking to compare it against; no code). `cohort_82.txt`'s
S3-sheet provenance label corrected in passing (`Target_expression_in_tumor`; the 82 are unchanged).
**D-075 pre-registers the confidence-blind ablation (2026-08-01) — built, not run.** D-065's
`no_plddt` answered *does the shift survive removing pLDDT?* but removal also destroys the
membrane-proximal *information*, so its null was ambiguous. D-075 adds **`geom_proxy`** — `no_plddt`
plus **feature 7**, membrane-proximal SASA measured from coordinates alone — so the axis is tested
with its information **restored** rather than amputated, and a **popularity-matched control**
(`scripts/attention_control.py`) that tests attention directly against two frozen proxies
(`pdb_present`, `pub_count`) instead of only via feature removal. The entry is the
**pre-registration**: it landed as its own commit before any implementation, and Decision 4's
interpretation is frozen against the **measured** `no_plddt` baseline (`ranking_run` id=3 — median
**0.5625** / mean **0.5893** / **6-of-12**, which is *not* "chance": only the count is even). Every
reading is judged on that explicit **triple**, never one statistic (D-041 dec 4), and **Spearman is
recorded as a dead discriminator** — FULL and `no_plddt` agree to full float precision while their
per-target percentiles differ by up to 0.25. **F-004 (id=2) is untouched and read from its row.**
Confidence-blindness is proven by a **two-armed** fixture (differing pLDDT *values*, and differing
pLDDT *array length* — the second because the first cannot catch a `len(plddt)` dependency), and the
contaminated implementation is kept permanently in the test file so the *fixture's own bite* is
re-asserted on every gate run rather than demonstrated once. Migration **`0007`** adds
`membrane_proximal_sasa` additively; **no run is in the PR** — the ablation and the control are
owner-authorised afterwards, with the interpretation already fixed. **What D-075 cannot separate is
named in the entry (dec 6):** F-008's precision confound is inherited by feature 7, since
tier/precision/length are mutually confounded with no overlap.
**Next (owner-gated):** the app-scoped token + Fly app/Postgres/secrets provisioning so the first
real deploy goes green; then starting the worker for the first end-to-end large rental fold — which
retires the PROVISIONAL 60-min lease threshold (D-030) and D-031's estimated PAE ratio with measured
values.

---

## 1. Prime Directive: Deep Learning Is the Core, Not a Wrapper

This is a **deep learning course project**. The grade depends on deep learning doing
**load-bearing work** — a neural network must be responsible for a primary output, not
merely calling an external service that happens to use ML internally.

Every architectural decision is evaluated against the question: **"Where is the deep
learning, and is *our* system running/using it in a defensible way?"**

- ✅ Running a protein language model (e.g. ESMFold) to fold sequences into 3D structure.
- ✅ A learned model that scores druggability / pocket suitability from structural features.
- ✅ Learned embeddings (from a neural encoder) powering semantic search over analyses.
- ✅ A model predicting mutation impact (ΔΔG / binding-site disruption).
- ⚠️ Pure retrieval from AlphaFold DB or UniProt lookups — acceptable as a *fallback or
  input*, but it cannot be the graded deliverable on its own.

**Rule:** at least one iteration's headline feature must be a deep-learning model that
this project runs or fine-tunes. This is recorded and defended in `docs/README.md`.

---

## 2. System Overview

PharmFoldMDK lets a user enter a cancer type or an overexpressed protein and returns
AI-driven structural analysis of that protein as a potential ADC target: predicted 3D
structure with confidence, druggable pockets, an ADC-suitability assessment, mutation
impact, and pharma-relevant reports.

```
   ┌─────────────── FLY.IO (serving tier, always-on, NO GPU) ───────────────┐
   │   ┌─────────────────────────────────────────────┐                       │
   │   │              Streamlit Frontend               │                      │
   │   │  Mission Briefing · New Analysis · Library ·  │                      │
   │   │            Reports · Settings                 │                      │
   │   └───────────────────┬───────────────────────────┘                     │
   │                       │ HTTP (internal)                                  │
   │   ┌───────────────────▼───────────────────────────┐                     │
   │   │                FastAPI Backend                 │                     │
   │   │   auth · analyses API · job queue · results    │                     │
   │   └──────────────┬──────────────────┬──────────────┘                    │
   │                  │                   │                                   │
   │        ┌─────────▼────────┐   ┌──────▼──────────────┐                    │
   │        │  Postgres +      │   │  Fly Volume /data   │                    │
   │        │  pgvector        │   │  PDB/CIF, PAE,      │                     │
   │        │  relational +    │   │  reports, uploads   │                    │
   │        │  JSONB + vectors │   │  (paths in DB)      │                    │
   │        │  + job queue     │   └─────────────────────┘                    │
   │        └─────────▲────────┘                                              │
   └──────────────────┼──────────────────────────────────────────────────────┘
                      │  authenticated OUTBOUND poll / upload (pull-based)
                      │  (worker claims pending jobs, folds, uploads results)
   ┌──────────────────┴──────────────────────────────────────────────────────┐
   │           LOCAL MACHINE (inference tier — NVIDIA GPU, 8 GB VRAM)          │
   │   Worker: poll → ESMFold (ESM-2 + folding head) → pLDDT/PAE → upload      │
   │   No inbound exposure. Queues gracefully when offline. (D-004)            │
   └──────────────────────────────────────────────────────────────────────────┘
```

**Boundary rule:** the database stores structured data, JSONB metadata, vectors, and the
**job queue**; **large binary artifacts (PDB/mmCIF, PAE JSON, generated reports, uploads)
live on the Fly Volume**, with only their paths recorded in Postgres.

**Topology rule (D-004):** deep-learning inference does **not** run on Fly. The Fly serving
tier is GPU-free and always on; a **local GPU worker** pulls jobs from Fly, runs ESMFold,
and uploads results back over an authenticated outbound connection. No inbound port is
opened on the local machine.

---

## 3. Component Architecture

| Layer | Responsibility | Planned tech |
|-------|----------------|--------------|
| **Frontend** | Interactive UI, 3D visualization, onboarding | Streamlit; `py3Dmol`/`stmol` for 3D |
| **Backend API** | Auth, request handling, **job queue** management, results | FastAPI + Uvicorn (on Fly) |
| **Worker transport** (D-031, D-036) | The **five** worker→Fly routes realizing the D-030 loop's protocol: claim → inline `FoldSpec`; artifacts → post-fold columns in a compensated Volume+DB transaction (idempotent; **PAE no longer travels here** — D-035 part 2; **D-106:** `persist_fold` omits `pae_json_path` from the UPDATE when the upload has no PAE, so a harvested D-036 path survives a re-fold); complete → 409 until `pdb_path` commits; fail → terminal; **pae → stores the gzipped PAE + `pae_json_path` in the same compensated boundary** (D-036, `persist_pae`, the rental tier's out-of-band transfer). Shared bearer token per route; all five under `/jobs`, so D-034's prefix property is unchanged. Client-side is `worker/http_client.py` (**no longer uploads PAE** — D-035 part 2; maps non-2xx → `TransportError`; sets an **explicit `httpx.Timeout`** — D-035 §3a: the httpx 5 s default would time out a slow upload, retry, exhaust attempts, and re-fold on a **paid** card) | `app/` (FastAPI, on Fly) + `worker/http_client.py` (httpx, GPU tier); hermetic route/boundary/client tests + a real-Postgres seam-1 handler-write test |
| **Read API** (D-034, D-038, D-053, D-062) | Seven public `GET /api/*` routes the React UI (D-033) consumes: `analyses` (light list — `id`/`accession`/`label`/`gene`/`mean_plddt`/`disposition`/`held_out`/`tier`/`tier_reason`/`boundary_method`/`fold_length`/`full_length`, **no `sequence`/`fold_provenance`**); `analyses/{id}` (full record incl. `sequence` + `fold_provenance`); `analyses/{id}/structure` (streams the stored `pdb_path`, `text/plain`); `analyses/{id}/plddt` (per-residue array); **`coverage`** (D-038 — the D-024 coverage object over **all 82** from `core/manifest.py`, joined to `protein_analyses` and `jobs` for a three-valued `fold_status` `folded`/`failed`/`not_folded` (D-043, `fail_reason` from `jobs.error`); the honest denominator the fold-derived list cannot supply); **`associations`** (D-053, the derived cancer-association map); **`ranking`** (D-062 — the latest **valid** scorer run: the pre-registered result F-004 + the 56 per-target scores; the invalid zero-positive `ranking_results` id=1 is never served, D-064 dec 3). **Unauthenticated by design** — writes stay bearer-guarded; the asymmetry is pinned by a route-prefix auth test (`/jobs` guarded, `/api` open, no third category). ⚠ **`GET /api/analyses/{id}/pae` now exists** (F-042 / later read-API work); the React bundle **does not consume it** (D-117). The older "No PAE route" clause is historical. | `app/read_routes.py` (thin handlers) + `app/reads.py` (query/projection, incl. the read-only `core/manifest.py` consume); hermetic SQLite `TestClient` tests |
| **Orchestration** (D-023, D-026) | `manifest.py`: measured cohort → deterministic routing table + D-024 coverage object, **reviewable before any job is created**. `enqueue.py`: foldable rows → `protein_analyses` (exact residues + UniProt release + folded span) + `pending` `jobs` (tier fold recipe); idempotent, 80/82 (2 named exclusions get none). ⚠ **An exclusion states its SCOPE and, when the protein is foldable at all, the CONDITIONS** (D-085): *excluded* has never meant *unfoldable*, and `MUC16`/`FAT2` are **queued in the census at tranche 5, tier=rental** — a guard treating the registry as "cannot fold" would silently drop two rows that are scheduled to succeed. `Exclusion.__post_init__` **refuses** a foldable entry with no conditions. `--requeue ACC…` (D-044) is the deliberate re-fold path idempotency cannot give — resets non-complete jobs to `pending`, leaves a completed fold untouched. ⚠ **D-111:** MUC16 is a mucin and goes `out_of_class` (never ESMFold); FAT2 is in the tileable 45, not a oneshot rental. The D-085 exclusion-registry warning still holds — *excluded* is not *unfoldable* — but the hold-48 GO is the later ruling for those two rows' fold path. | `core/manifest.py`, `core/enqueue.py` — CPU-side; hermetic on SQLite + a real-Postgres commit test |
| **T5 hold-48 tiling** (D-111, D-112, D-113, D-114, D-115, D-116, D-117, D-118) | BUILD GO 2026-09-04 (issue #210). The 48 pending remainder of tranche 5 (`census_manifest.v7.csv`, `span_aa > 1656`) splits **45 tiled / 3 mucins `out_of_class`**. Planner emits tile rows `{accession, start, end, parent_job_id}` at window **1656**, overlap **128**, stride **1528**; parent `jobs.tier` stays NULL until stitch. Tiles claim on the existing ESMFold path at the T5 recipe (`fp16` / chunk 64, `D-047`). Stitch: overlap by per-residue pLDDT; PAE block-diagonal with **null off-block, never 0**. Mucins write **zero** PDB/PAE. Claim of a mucin or a hold parent as one-sequence `tier=rental` **raises**. ⚠ **D-111/D-112 PRs ran no GPU and did not enqueue.** The IGF2R pilot subsequently folded two tiles (jobs **3589** L=1608 / **3590** L=797) on an **RTX PRO 6000 Blackwell**; remaining **104** unsnapped tiles wait on a **clean-card cold start** of [`docs/GUIDE-renting-hold48.md`](docs/GUIDE-renting-hold48.md) (D-113; operator flow is general — rent → setup → worker → empty-queue prove → retrieve → Terminate — not a re-test after a named D-NNN) before any emit of the other 44. Budget: [`docs/BUDGET-hold48-tiers-2026-09-04.md`](docs/BUDGET-hold48-tiers-2026-09-04.md) (**$2.19/hr** Matt/Trinity pin; fold-only IGF2R **$0.31**; remaining balance after Terminate **$14.17** measured). **D-114:** account ceiling ≈ **$50**; Matt tops up before Wave 0 / emit; `$14.17` is historical and does **not** authorize C2; RunPod balance glance is mandatory (GUIDE Step 0 — do not vacation on E). D-113 forecasts stand. ⚠ **No Fly change in D-113. The 1656 cap is not raised. Peak VRAM is a named unknown (UNKNOWN) — do not invent a number; next cold run captures `nvidia-smi` (runbook Step 5).** Emit is `core.hold48.emit_tile_jobs` (never `python -m core.enqueue --bucket rental`). Optional `length_min`/`length_max` (both default None = all planned tiles; Wave A `length_max=800` — D-111 amendment 1 / issue #210 / BUDGET-hold48 Wave A) write rental children only in-band and skip existing `parent_job_id`+tile_index/window rows; out-of-band siblings are not created (not NULL-tiered). ⚠ **D-113 live-snap (2026-09-04):** live C1 queue is **n=38** (11 unsnapped-native + 27 domain-snap ex-1656), vs BUDGET unsnapped C1 **n=11**; §5 C1 cap is still the envelope (D-113 live-snap note + D-111 amendment 1). ⚠ **D-112:** `TILE_WINDOW_AA` / overlap / stride live in `core/contracts.py` (stdlib leaf). `worker/main.py` imports the cap from there, **never** from `core.hold48`. Git pin for a rental pod is **`origin/main`** with the AST `ImportFrom` assert (D-115); `1d48d1d` is D-111 and dies on sqlalchemy. Minimum live pin was PR **#213** (`733c41f`). Pane A prints `WORKER_AUTH_TOKEN` from the laptop `.env` (`fly secrets list` names only). ⚠ **D-116 stitch-ready gate:** ops call `core.hold48.stitch_readiness(session, parent_job, parent_analysis, *, domain_ends=…, cache_dir=…)` — same `plan_tiles` path as emit (emit-time snap must match). Ready iff every expected `TileSpec` has a child with the same `parent_job_id` + (`tile_index` or window) that is `complete` + PDB present + PAE present, **and** the expected tiles cover the span (`uncovered_n=0`), **and** `expected_n>0`. A loose "any child with pdb+pae" SQL is the wave1 false-ready class (parent **2817**: `n_tiles_rows=1` on a long span; wave1 FAIL 17). Mucin / no tiles → not ready, empty expected. Countable return; does not change `hold48_stitch.py`. ⚠ **END STATE 2026-09-05 PT (owner-verified closeout; not re-queried on Fly in the D-117 PR):** Waves A/B/C1/C2 tiles complete; C2 L=1656 n=36 `has_pae=36` `lack_pae=0`; PAE on Volume `pharmfoldmdk`; pod Terminated (~$10.25 RunPod left). Wave1 stitch PASS 10 / FAIL 17 (false-ready class). Wave2 stitch COMPLETE `ready_n=17` attempted=17 PASS=17 FAIL=0. ⚠ **27 unique** stitched parents = Wave1 PASS **10** + Wave2 PASS **17** (UI / end-state inventory; Wave2 17/17 remains the Wave2 batch). First parent **2817** `Q9P273` mean_plddt=61.07 tiles=`[3673,3630]`; prefer lower dup ids **3673/3674/3675** (spares **3693/3695/3696** unused). Stitch is a **pLDDT assembler**, not Kabsch; IGF2R seam ~88.76 Å; Kabsch/restitch **PARKED**. Assembler-only path via Fly. ⚠ **The sentences above that still wait on a clean-card cold start / remaining 104 tiles / `$14.17` authorize-nothing are HISTORICAL** — they describe the path that produced this end state, not a live queue. ⚠ **D-118:** GUIDE opens **CLOSED** (pod Terminated 2026-09-05 PT; do not Deploy). Census identity / Story counts / assembler disclosure are the Phase 1 P0 honesty GO. Plan: [`docs/PLAN-ui-post-wave2-endstate.md`](docs/PLAN-ui-post-wave2-endstate.md). **No Kabsch GO. No jobs dashboard.** | `core/contracts.py` (window); `core/hold48.py` (`emit_tile_jobs`, `stitch_readiness`), `core/hold48_stitch.py`; `app/artifacts.py` (claim guard); `worker/main.py` (length cap); `docs/GUIDE-renting-hold48.md` + `docs/BUDGET-hold48-tiers-2026-09-04.md` (D-113, D-114); [`docs/PLAN-ui-post-wave2-endstate.md`](docs/PLAN-ui-post-wave2-endstate.md) (D-117); hermetic fixture tests in `tests/test_hold48_tiles.py` + `tests/test_hold48_stitch_readiness.py` (D-116) + `tests/test_worker_main.py` (import graph) |
| **ADC reference** (D-029, D-040) | The scorer arc's *label* + *comparator* data. `evidence_scores.csv`: the **17 of 82** exact 1-5 scores the paper text publishes (Fig 4A/4B only; the other 65 are null-with-reason, no imputation). `adc_reference_mapping.csv`: one curated drug→antigen→accession file for **Group B** (in-cohort ADC positives, the labels) and **Group C** (approved ADC targets outside the 82), split by a **computed** `in_cohort_82` (never typed). Group B is derived & per-row-cited, not inherited; roster curation is a reserved hand-review. Pure functions: symbol→accession join (misses surfaced), Group B/C classification, openFDA reconciliation (live query only in the advisory scheduled job, never the gate). | `core/adc_reference.py` — pure, fixture-tested; `data/*.csv` |
| **Feature extraction** (D-027, D-058, D-075) | The scorer arc's *inputs*. `core/features.py`: the **pure** extractor — six D-027 features (ECD length, length-normalised Rg, mean & membrane-proximal pLDDT, length-normalised SASA, largest accessible-patch fraction) from `(structure.pdb, plddt, boundary_method)`, **zero third-party imports** (SASA is an in-repo Shrake–Rupley kernel — 92 golden-spiral points, 1.4 Å probe, committed vdW-radii table, spatial-grid neighbour search; `numpy`/`scipy` are in no lock file and `core/` ships — DEP-001). Never raises: an uncomputable feature is **null with a reason**, never imputed. **D-075 adds feature 7, `membrane_proximal_sasa`** — mean per-residue SASA over the C-terminal membrane-proximal window, the **confidence-blind** counterpart of feature 4. It reuses feature 4's window rule through the shared `membrane_proximal_k()` helper but takes `n_res` from the **parsed coordinate residues, never `len(plddt)`**; `plddt` is not a parameter of its computation. Its blindness is *architecturally* guaranteed, not merely tested — `Atom` carries no `b_factor` and `parse_pdb` never reads columns 60-66, so the confidence column is unreachable from the coordinate path. Kept out of `FEATURE_NAMES` (still six) in a separate `EXTENDED_FEATURE_NAMES`, so a seventh column cannot drift into the graded model by being appended to one list. `scripts/extract_features.py`: an **offline client of the public read API** (`/api/analyses`, `/{id}/structure`, `/{id}/plddt`, joined to the D-023 manifest for the boundary), computing features for **every** folded row — `held_out` included, filtered late (D-058 Addendum 2 §2) — and handling a structure-less row (a failed fold, e.g. IGF2R) as null-with-a-reason without crashing the batch. The loader writes `protein_features` via `DATABASE_URL`, exactly as `core/enqueue.py` builds its engine. **Serving tier never computes a feature.** | `core/features.py` (pure, ships, fixture-tested incl. a closed-form SASA anchor); `scripts/extract_features.py` (offline, excluded from the image); `httpx` |
| **Scorer** (D-015 §3, D-041, D-060) | The learned ADC-suitability model, **by hand in pure stdlib** (`numpy`/`scipy`/`sklearn` are in no lock file). `core/scorer.py`: L2-regularized logistic regression over the six standardized features — **seven parameters** (six coefficients + intercept), fit by **IRLS** (Newton on the penalized log-likelihood; non-convergence **raises**, never a silent estimate). Evaluation is pre-registered and every free parameter fixed before a result exists (D-060): **no RNG** (deterministic stratified folds), a **13-point λ grid** selected by 5-fold inner CV *inside each LOO fold*, leave-one-out reporting a **distribution** of held-out-positive percentiles over the ranking set (56, F-002), a **Spearman** vs the evidence-score comparator, and a head-to-head on one **common reference set** (the comparator is two-valued → degenerate by construction). **The LOO runs first and independently of the ranking-table full-data fit, and a fold that fails to converge is recorded (named, `converged=False`) without aborting the loop** — the distribution is reported over the folds that converged, with the non-convergent count and names carried (D-063). A degenerate fit set (zero positives **or** zero negatives) and quasi-complete separation produce the *identical* failure signature (the unpenalized-intercept Hessian is singular), so a **degenerate label set raises `DegenerateLabelSet` before any IRLS iteration** (D-064) — a meaningless input must never read as a result about the data; the intercept stays unpenalized and the grid is never extended (D-063 refusals). ⚠ **Label (Group B) and comparator (evidence score) are different quantities and never mix** — a scrambled-comparator fixture must give byte-identical coefficients. Attribution is `β_k·x_k` per target (D-041 dec 1). `scripts/fit_scorer.py`: assembles rows from `protein_features` + labels + evidence via a **single label path** (`core.adc_reference.group_b`, joined on **accession** — D-064 dec 1; the bespoke `read_group_b_labels`/`read_evidence_scores` that once returned zero positives are deleted, not two paths), runs the evaluation, and on `--run --persist` writes `target_scores` + `ranking_results` (D-061) with survivorship status (`loo_status`/`fulldata_status`/`status_detail`, D-064 dec 5) to a **new** `ranking_run` (the invalid zero-positive run stays marked, not overwritten — D-064 dec 3). **D-065/D-075 sensitivity ablations:** `run_scorer(feature_set=…)` fits a NAMED feature subset — `no_plddt` (5 params), `plddt_only` (3 params), or **`geom_proxy` (D-075: `no_plddt` + feature 7 → 5 features, 6 params)** — to test whether the signal is carried by pLDDT (F-004 caveat b); **any name not in `FEATURE_SETS` raises** (arbitrary subsets refused by construction), the pre-registered path stays six features/seven parameters, and `--ablate` writes a `run_kind='sensitivity'` run that the surface never serves as the result. **D-075 makes the projection unconditional** — it previously skipped projection for the pre-registered set, which was safe only while every row carried exactly six features; with feature 7 present at index 6 a skipped projection would have silently fit the *graded* model on seven features/eight parameters. A test asserting 6 coefficients against a 7-wide row is the guard. **Written and fixture-tested; the fit and each ablation are separate owner-authorised runs.** | `core/scorer.py` (pure, ships, fixture-tested incl. leakage guards); `scripts/fit_scorer.py` (offline, excluded from the image) |
| **Span definition** (F-025, D-081) | ⚠ **TWO definitions exist and neither is "the" definition.** `core/span_definition.py` holds both names and the ruled vocabulary; `core/span_extract.py` is the **V2** extractor. **V1** (`v1-extracellular-substring-2026-07-21`) is a substring match on `"extracellular"` and is **frozen for the 82 permanently** — `scripts/ecd_lengths.py:parse()` is untouched and there is **no shared code path**, because a shared path would make the freeze impossible to guarantee. **V2** (`v2-ruled-vocabulary-2026-08-07`) is an **accepted term LIST, never a substring** — the biological test is *can this face ever reach the outside of the cell?* Secretory-pathway faces (`Lumenal`, `Vesicular`, `Exoplasmic loop`, `Perinuclear space`, …) yes; mitochondrial/peroxisomal/nuclear **no, on any mechanism**. ⚠ `Perinuclear space` is accepted while `Nuclear` is rejected, so a substring rewrite silently drops 16 rows. GPI-anchored proteins have **no topology by design** and take their own rule: **the chains CONTAINING the anchor, latest start** — `min(start)` was wrong *live* on MSLN (561 aa carrying a secreted fragment) and an earlier "chain ending at the anchor" rule wrongly excluded CEACAM5. Absences are **categories with causes** — `no_extracellular_span`, `span_boundary_unknown`, `term_unruled`, `absent_with_reason`, `span_contains_transmembrane` — never a zero and never a band meaning five things. **Every artifact naming a span states which definition produced it.** | `core/span_definition.py`, `core/span_extract.py` (pure, stdlib); `scripts/census_reparse.py` (cache-only, no network) |
| **Census manifest & tranches** (D-079, D-083) | `scripts/census_manifest.py` — the **pre-registration of what folds and how**, built from the V2 span artifacts. Carries `span_start`/`span_end` (⚠ **a length cannot slice a sequence** — the census manifest once had only `span_aa`), `boundary_method` per row, band, tier, and **two identities that never stand for one another**: `fold_order_key` (the accession **set** only — membership, stable across span revisions **by design**) and `manifest_content_hash` (coordinates, band, tier, rule, definition). ⚠ Revisions 1 and 3 once had **identical membership and identical fold order while two spans differed**, so an unchanged order is *not* evidence of an unchanged manifest. The identity **function** is itself versioned (`identity_fn_version`) — two hashes from different functions are never compared without both versions named. The **seed is written to disk before the first shuffle**; a **tranche is a PARTITION and the seed is the ORDER WITHIN one**, so size-banding never reorders. Revisions are **retained, never overwritten**, and a rebuild **requires a stated reason**. **Tranche-6 per-tile manifest (RA2, D-104):** `scripts/tranche6_tiles.py` emits `data/census/tranche6_tiles.csv` — one row per merged RUN (`tile_cut_kind=whole_run`), same inputs/merge/straddle as `tranche6_runs.py`, routed `local` / `rental` / `unroutable` under `tile_max_aa=1026` `route_at=440`. ⚠ Two-path against `tranche6_runs.csv`'s `n_runs` and `largest_run` per accession; a disagreement is a defect. Interior cuts stay RD2. | `scripts/census_manifest.py`; `data/census/census_manifest.v*.csv` + provenance; `scripts/tranche6_tiles.py`; `data/census/tranche6_tiles.csv` |
| **VRAM guard** (D-082) | ⚠⚠ **On WDDM an over-allocation is not refused — the driver spills to system memory, and that path bugchecked the host.** Every prior instrument assumed an `except` would catch it; **none runs, because there is no process left.** `core/vram_guard.py` therefore **prevents rather than catches**, in three layers: **(1) driver** — sysmem fallback disabled, ⚠ **owner action, and `sysmem_fallback_state()` reports `unknown`, never `ok`**, because reporting a setting we cannot query as fine is an absent measurement coerced into an affirmative; **(2) allocator** — `set_per_process_memory_fraction` makes PyTorch raise in Python, ⚠ a strong guard and *not* a proof (cuBLAS/cuDNN workspaces bypass the caching allocator, and it binds on **reserved**, not demand); **(3) process** — `worker/fold_supervisor.py` runs the fold in a **spawned, persistent** child, so a segfault / driver reset / allocator abort becomes a **named** outcome (`FoldChildDied`, carrying the exit code) with the crank alive, distinct from a fold that merely raised. ⚠⚠ **It does not survive a bugcheck — nothing does**, which is why layers 1 and 2 exist. ⚠ **Wired but OFF unless `WORKER_FOLD_IN_CHILD=1` (D-084)**, and the state is printed on every worker start either way: it was built mid-tranche, and a default-on layer would have changed the fold path's process topology at a restart nobody was told about. The child is **persistent, one per worker** — `_MODEL_CACHE` is per-process, so a child per fold would reload 8.4 GB every time — and the **parent never imports torch**, so only one process holds weights. ⚠ **A death is never retried automatically**: a crash loop that re-folds the row that killed it takes a whole tranche with it. `preflight()` **refuses rather than attempts**: a length with no measured requirement is `refused_no_measurement`, a category and not a green light. ⚠ **`f059_peak_gib(L)` records `F-059`'s law (`5.24 + 7.215e-06 · L^1.983`) and is not a measured `requirement_mib` (F-061)** — the `preflight` signature is unchanged; RA3 writes the prediction on the tile and still calls `preflight(..., requirement_mib=None)`. ⚠ The fold loop still does not consult the guard (`F-049`; RB, not RA). `HOST_DOWN` is **inferred, never observed** — a job left `claimed` across a restart is *evidence*, and its absence is explicitly **not** proof of health. ⚠ **F-062:** a measured-success envelope is card-bound — S-005's 6665 MiB produced **FIT then CUDA OOM** on Blackwell; F-059 within 10% does not certify free headroom. `scripts/ceiling_climb.py` **refuses to climb without `--layer1-attested`**, honors `--fold-in-child` / `WORKER_FOLD_IN_CHILD=1` (D-082 layer 3: cap, fold, peak, and empty-cache run in a persistent child so the parent does not hold a second weight copy), defaults `--start 248 --stop 456 --step 8 --memory-fraction 0.85 --tier local` with empty-cache ON, and writes a **fresh** jsonl under `data/census/` (`ceiling_climb.int8.blackwell.jsonl`). ⚠ A climb is not this change — Kaylee runs it on the laptop GPU. ⚠ `F-050` stays RESERVED. The D-104 routing table is not rewritten here. ⚠ **D-105 (RB re-gate only):** `scripts/rb_local_tile_folds.py` dispatches **each tile fold in a fresh spawned process that exits before the next parent preflight** (`worker/rb_tile_child.py`) — not `FoldSupervisor` / `ClimbChild` spanning the batch. Parent then `gc` + `empty_cache`, then preflight; insufficient free **STOP**s (does not skip). Artifact `data/control/rb_local/rb_local_summary.regate384.procpertile.csv` (does not overwrite the PR #201 early-stop CSV or RB4 `rb_local_summary.csv`). Envelope/filter unchanged (F-063 6357, L≤384 after 1482 local). No GPU folds in the D-105 PR. | `core/vram_guard.py`; `worker/fold_supervisor.py`; `worker/ceiling_climb_child.py`; `worker/rb_tile_child.py` (D-105 one-shot); `scripts/ceiling_climb.py` (climbs, ⚠ **never bisects** — the probe that bisected 209→313 aa killed the host; layer 3 opt-in via `--fold-in-child` / `WORKER_FOLD_IN_CHILD=1`); `scripts/rb_local_tile_folds.py` |
| **Fold reconciliation** (D-082) | ⚠ **No `assert` does guard work** — `assert` vanishes under `python -O`, so a guard written as one is a comment that occasionally runs. `core/fold_reconcile.py` raises explicitly at **two ends for two failure modes**: `check_sliced_length` at **enqueue**, where the slice is cut (⚠ **both branches checked** — `whole` makes a checkable claim too); `reconcile_fold` **after the fold**, comparing the manifest span, the enqueue length and ⚠ **the residue count read out of the PDB itself**, because a count taken from the same record as the claim cannot disagree with it. An **absent claim is not a satisfied claim** — nothing to compare **raises**. | `core/fold_reconcile.py` (pure, stdlib) |
| **Census ingest** (D-079, D-083) | `scripts/census_ingest.py` — **one tranche per invocation**, ORM models only, ⚠ **never hand-written SQL against production**. Writes `protein_analyses` with `cohort_tranche = <1..5>` (⚠ **never 0, never NULL**) and `ranking_run_id = **NULL**` — the structural bar on scoring, since `fit_scorer` selects **by run id**. `meta["tier"]` is load-bearing: `/claim` **raises** without it (D-047), and the recipe is deliberately **not** stored as authority — `dtype`/`chunk_size` resolve from `TIER_RECIPE` at claim time. ⚠ **The dry run builds a real `FoldSpec` from every payload before any write**: an earlier version omitted `model_revision`, `/claim` raised `KeyError` **after** marking each job `claimed`, and ten jobs became permanently stuck with `attempts=0` and no error. A dry run that does not exercise the consumer's contract is not a dry run. | `scripts/census_ingest.py`; `tests/test_census_ingest_claim_contract.py` (reads the required keys **out of `app/artifacts.py`'s source**, not a hand-kept list) |
| **Census surface** (D-079 dec 1, D-083, D-087, D-117, D-118) | ⚠⚠ **Unscored by construction.** `/census` shows the census as a **population** — counts, tranches, absences-with-causes, and the limitations — with **no score and no rank**. ⚠ **D-087 reversed the "no per-protein row" clause** (owner: *"why hide it under a bushel?"*): `CensusTable` is searchable/sortable; default order is accession, never pLDDT; every row carries `scored: false`. The "not scored" statement sits **above** the numbers. ⚠ **D-118 (Phase 1 P0):** `list_census` projects **one row per accession** — a tile is never a protein; `/census/{accession}` opens the parent/assembled analysis; `census_summary.folded` does not count tile windows; assembled pLDDT loads `stitched_plddt.json`; viewer banner states assembler-not-Kabsch (IGF2R seam ≈ 88.76 Å is not solved). The D-117 leak is remedied here. Plan remains [`docs/PLAN-ui-post-wave2-endstate.md`](docs/PLAN-ui-post-wave2-endstate.md) (P1 tile table / Kabsch still later GOs). ⚠ **Every cohort read is tranche-filtered**: 75 of the 82 cohort accessions also appear in the census, so an unfiltered `_folded_accessions` would have put a census `analysis_id` under HER2's accession and **overwritten the cohort's own coverage**. A test enumerates every `select(ProteinAnalysis…)` in `app/` and requires the filter — with a narrow, stated exemption for **primary-key lookups**, since filtering `artifacts_present` would make every census fold un-completable. | `ui/src/censusSummary.js`, `ui/src/components/CensusView.jsx`, `ui/src/components/CensusTable.jsx`; `app/reads.py` (`list_census`); `tests/test_no_census_leak_on_tranche_zero.py` |
| **Local GPU worker** | Polls Fly for jobs, runs **ESMFold** on the local NVIDIA GPU for targets **under the length ceiling**, uploads artifacts back (D-004) — **not deployed to Fly**. ⚠ The fold record now names the **NVIDIA driver** (D-082): a ceiling and a determinism verdict are valid only under the recipe **and the stack** that produced them, and the environment is assigned **from the captured dict, not field by field** — a hand-written list drifted the moment a fifth key appeared. | Python worker; PyTorch + Hugging Face (`facebook/esmfold_v1`), int8 trunk |
| **Rented-GPU batch** (D-011, D-035, D-113, D-114) | One-time offline fold of the **29 above-ceiling** targets — the **same `worker/` loop** on a rented box calling the same transport routes, differing only in the FoldSpec (fp16, unquantised, unchunked), **not** an API to a hosted folder (Prime Directive, D-035 §2). Claim→complete uploads `structure.pdb`/`plddt.json`/`provenance.json` (~1 MB even at 2213 aa); **PAE is persisted to the pod's local disk (rental-scoped, `WORKER_ARTIFACT_DIR`) and transferred out-of-band via a dedicated retrieval route** into the analysis's Volume dir, so `pae_json_path` is populated for **both tiers** — asymmetric in transport, identical on disk. Retrieval is a **blocking pre-termination step** (no network volumes, D-011: pod-disk PAE is destroyed on termination). **Hold-48 tiles are a later rental on the same transport**, not this 29: card/class, git pin, pip order, and emit path are [`docs/GUIDE-renting-hold48.md`](docs/GUIDE-renting-hold48.md) (D-113), **not** [`docs/GUIDE-renting-the-a6000.md`](docs/GUIDE-renting-the-a6000.md). | RunPod RTX A6000 48 GB (cohort 29); hold-48 pilot on RTX PRO 6000 Blackwell (`docs/BUDGET-hold48-tiers-2026-09-04.md`); committed repo code, not a one-off script |
| **DL / Inference core** | The neural work: **ESMFold structure prediction (D-003)**, plus pocket/druggability scoring, embeddings, mutation impact | PyTorch + Hugging Face; `biopython` for parsing |
| **Data layer** | Persistence, relationships, vector search | Postgres + pgvector, SQLModel/SQLAlchemy, Alembic |
| **Object storage** | Large structure/report files | Fly Volume mounted at `/data`, organized `/data/analyses/{id}/` |

> **Ratified (D-003 + D-004):** we **run ESMFold ourselves** — the ESM-2 protein language
> model + folding head predicting 3D structure from a single sequence, emitting pLDDT and
> PAE — **on a local GPU worker, not on Fly** (see §5). AlphaFold DB / UniProt retrieval is
> demoted to an optional fast path + fallback, not the deliverable.

---

## 4. Data Model (from Database Plan v2)

> ### The census is now BUILT, and this section describes it because the code exists
>
> **The pointer that stood here said: *"the design lives in `### D-079`; this file gains it when the
> code does."*** ⚠ **The code does. Migration `0008` is applied, `db/models.py` carries
> `cohort_tranche`, and census rows exist in production.** The pointer is replaced rather than
> amended, so the transition is legible: this file described an intention, and now describes a
> thing.
>
> **`protein_analyses` is no longer the cohort alone.** It holds two populations separated by one
> nullable integer:
>
> | `cohort_tranche` | population | scored? |
> |---|---|---|
> | **0** | the 82-target cohort (D-023) | yes — `### F-004`, `### F-017` |
> | **1–5** | the census, size-banded (`### D-083`) | ⚠ **never** — `### D-079` dec 1 |
> | ⚠ **NULL** | ⚠ **nothing. A NULL is a bug, not a category** | — |
>
> ⚠⚠ **THE SEPARATION IS LOAD-BEARING AND IT IS NOT OBVIOUS: 75 of the 82 cohort accessions ALSO
> APPEAR IN THE CENSUS** — HER2, EGFR, MSLN, IGF2R, MUC16 among them; all 82 are in the roster.
> `input_value` is therefore **not unique**, and every join keyed on accession must say which
> population it means. Two unfiltered reads (`_folded_accessions`, `_failed_accessions`) would have
> put a census `analysis_id` under HER2's accession and **overwritten the cohort's own coverage** —
> found by measurement **before** the first census row was written, and now guarded by a test that
> enumerates every `select(ProteinAnalysis…)` in `app/`.
>
> **The filter is `== COHORT_TRANCHE`, never a negation.** ⚠ `!= 1` would admit a NULL-tranche row;
> an untagged row must be **invisible** to the cohort surface, not included by a comparison that
> treats absence as safe.
>
> ⚠ **Census rows carry `ranking_run_id = NULL`**, because `scripts/fit_scorer.py` selects **by run
> id** — that NULL is what makes "the census is never scored" structural rather than remembered.
>
> **What is deliberately still absent:** no census row carries `protein_features`, no census row
> appears in `target_scores` or `ranking_results`, and no surface ranks one.

Primary entities (full column detail in [`docs/Database_Plan_v2_Postgres.md`](docs/Database_Plan_v2_Postgres.md)):

- **`users`** — auth (username + hashed password), JSONB `preferences`. **Not built yet** (no
  auth code); this is why `protein_analyses.user_id` carries no FK yet (D-019).
- **`protein_analyses`** (D-019, `db.models.ProteinAnalysis`) — core durable record: input
  type/value, structure source, `pdb_path`, `mean_plddt`, `pae_json_path`, JSONB `metadata`
  (attr `meta` — "metadata" is reserved on the ORM Base), notes, and a nullable
  `ranking_run_id` FK → `ranking_runs` (D-015 §4). `user_id` is a nullable integer with **no FK
  yet** — deferred until `users` exists, the same pattern as the old `analysis_id` deferral.
- **`ranking_runs`** (D-019, `db.models.RankingRun`) — versions one cohort ranking
  (`target_list_version`, `scorer_version`, `created_at`), so a result ties to the target-list
  and scorer that produced it (D-015 §4, §7).
- **`protein_features`** (D-058, `db.models.ProteinFeatures`, migration **`0003`**) — the six
  D-027 structure-derived features for one fold: six nullable `Float` columns (`ecd_length`,
  `radius_of_gyration`, `mean_plddt_ecd`, `membrane_proximal_plddt`, `sasa_normalized`,
  `largest_patch_fraction`), **plus `membrane_proximal_sasa` — feature 7, migration `0007`
  (D-075)**: the confidence-blind proxy, nullable and **deliberately not backfilled** (every
  pre-D-075 row stays NULL, an honest "not computed yet"; a `server_default` would have handed
  `geom_proxy` 79 values that were never measured).
  > ⚠ **SUPERSEDED 2026-08-05 — the parenthetical above, not the design claim.** The column was
  > **measured**, not backfilled: the Task C fill (`scripts/extract_features.py --fill-feature-7`)
  > wrote `membrane_proximal_sasa` **in place** across the ranking set, from coordinates, aborting
  > the entire fill if any row's features 1–6 had drifted from what was stored.
  > **Per `docs/CLOSEOUT-2026-08-05.md` — Code's reading of the live database; not verified from
  > this tree.** For the population, the residual null and its reason, see the close-out and
  > **`### F-023`**; **no count is inscribed here** because this document's author cannot see the
  > database.
  > **The design claim stands and is why the fill was safe:** feature 7 is still never backfilled
  > with an *inferred* value. A `server_default` would have supplied numbers nobody measured — which
  > is precisely the defect **`### F-020`** records, arriving by a different route. Measuring the
  > column is the one thing D-070 dec 2 always permitted.
  > ⚠ **Do not read the numeral in the sentence above as a current count.** It is a hypothetical
  > about `server_default`, written before the fill; that it now resembles the measured population is
  > a coincidence of arithmetic, and the kind a reader in a hurry converts into a fact.
  **Feature 7 is not one of D-027's six and never
  reaches the pre-registered path** — `FEATURE_NAMES` still has exactly six entries, asserted by the
  gate, and `run_scorer` projects onto its named set's indices so the graded fit uses columns 0–5
  regardless of how wide a row is. A JSONB `null_reasons` records **why** any is null (D-027's
  null-with-a-reason — *never* an imputed mean), the stored D-041 §5 floor decision
  (`mean_plddt`, `below_plddt_floor`), a source-hash `feature_version`, and FKs to
  `protein_analyses` (the fold read) and `ranking_runs` (the run). **A plain ORM model** (no
  pgvector) so it builds under both SQLite `create_all` and the `0003` migration. Migration
  `0003` is **purely additive** — one new table, no `ALTER`, no backfill — and is **verified by
  querying `information_schema.tables`, not by alembic's exit code** (`docs/HAZARD-search-path-seams.md`:
  a `SET search_path` before `begin_transaction()` once let a rolled-back upgrade exit 0); the
  `postgres` CI job runs the chain end to end. Features are computed **offline** by `core.features`
  and written by `scripts/extract_features.py`; the serving tier never computes one (D-058 dec 3).
- **`target_scores`** (D-061, `db.models.TargetScore`, migration **`0004`**) — one row per ranked
  target per run: `score` (predicted probability), `attributions` (JSON — the six `β_k·x_k`, D-041
  dec 1), `rank`, with FKs to `ranking_runs` + `protein_analyses`. Only ranking-set targets get a
  row; excluded targets are carried on `ranking_results` with their reason, never a fabricated score.
- **`ranking_results`** (D-061, `db.models.RankingResult`, migration **`0004`**) — one row per run:
  D-041's **headline distribution** (`structural_percentiles`, JSON — not a scalar), the head-to-head
  percentiles, the Spearman, every denominator (`n_ranking_set`/`n_fit_positives`/`headto_reference_n`/
  `plddt_floor`), the per-fold `{symbol, λ, converged}` + grid-edge flag, the `excluded` set with reasons,
  `scorer_version` + `feature_version`, and (migration `0005`, D-064) **`loo_status` / `fulldata_status`
  / `status_detail`** — the survivorship status of a run (which pre-registered statistics were
  producible; a blocked statistic is null *with* its reason), and where the invalid zero-positive
  `ranking_results` id=1 is marked (owner action). Both tables are additive (`0004`/`0005`, verified by
  `information_schema` query), plain ORM models (no pgvector), written offline by `scripts/fit_scorer.py`.
- **`analysis_embeddings`** — `vector(384)` + HNSW cosine index for semantic search
  (Iteration 3+). **Created in migration 0002 as raw SQL only — deliberately NOT an ORM model**
  (D-019), so the Postgres `vector` type never reaches SQLite `create_all` and no `pgvector`
  Python dep is added. This is the **first vector column, and it closes the last unproven point
  (D-017):** the migration runs `CREATE SCHEMA IF NOT EXISTS extensions; CREATE EXTENSION IF NOT
  EXISTS vector SCHEMA extensions;` then a **bare** `vector(384)` that resolves via env.py's
  `search_path` seam — exercised for real in the `postgres` CI job (now on a `pgvector/pgvector:pg16`
  image). Idempotent no-ops on prod (D-014). The **app-runtime** connection will need the same
  search_path — a separate seam in the engine config when the app queries embeddings (D-012 §5a).
- **`mutations`** / **`reports`** — 1:N from an analysis; **deferred** (Iteration 2/3, D-019).
- **`jobs`** (D-009 §1, **implemented in PR A** as `db.models.JobRecord`) — **transient**
  fold-queue state, kept **separate** from the durable `protein_analyses` record: `analysis_id`
  (see FK note), `status` (`pending`/`claimed`/`complete`/`failed`), `claimed_at`, `worker_id`,
  `attempts`, `error`, and `inference_settings` JSONB (model revision + `source`/ECD bounds —
  the per-target slicing identity, authoritative; plus `dtype`/`chunk_size`, which since **D-047
  are a non-authoritative enqueue-time *hint***). **The fold recipe is resolved at fold-time, not
  frozen at enqueue (D-047):** `build_fold_spec` (`app/artifacts.py`) reads `dtype`/`chunk_size`
  from the current `TIER_RECIPE[tier]` (`tier` from the analysis `meta`), never from the stored
  hint — so a recipe change (e.g. D-042's rental `chunk_size` `None`→`64`) reaches already-enqueued
  jobs on the next claim, instead of a requeue faithfully replaying a stale recipe. The
  reproducibility record is `fold_provenance` (D-045), which captures what each fold *actually*
  ran. `TIER_RECIPE` lives in `core/contracts.py` (the serving-safe leaf, beside `FoldSpec`) so the
  serving tier resolves it without importing `worker/` (DEP-001). **D-112:** `TILE_WINDOW_AA`
  (1656) and the D-111 overlap/stride integers live in the same file, so `worker/main.py` can
  refuse `L>1656` without importing `core.hold48`. **D-107 amendment 1:** `jobs.tier`
  may be `msa` — a claimable partition, still filtered by `tier = :tier` (F-035). `TIER_RECIPE`
  remains ESMFold-only (`local` int8/64, `rental` fp16/64); `msa` is **not** a key, so
  `build_fold_spec` fails loud rather than returning an ESMFold `FoldSpec`. The known-tier set
  used at enqueue/validation (`KNOWN_TIERS`) includes `msa` so that string is not treated as
  unknown and dropped. NULL-tier remains unclaimable (the 48 hold is not this change). The MSA
  worker (MMseqs2/OpenFold) is slice C, not this change. Reached through the `JobQueue`
  **seam** (`core/queue.py`):
  claimed via `SELECT … FOR UPDATE SKIP LOCKED` (the one Postgres-only, unproven-in-CI
  operation), while `complete`/`fail`/`reap_stale` are portable and tested for real on SQLite.
  Stale `claimed` jobs (age **strictly** > 30 min) are requeued, `attempts++`, up to
  **`MAX_ATTEMPTS = 3`** then terminal `[reaped-out]` (D-009 §1 Amendment 1); an explicit `fail`
  is terminal and leaves `attempts` untouched (Amendment 2); claim order is explicit FIFO by
  `created_at` (Amendment 3). **`analysis_id` FK → `protein_analyses` — CLOSED in D-019** (was
  deferred under Amendment 4; the migration that created `protein_analyses` added it in the same
  migration). This is the durable queue the local GPU worker (D-004) pulls from.

**Relationships:** `users` 1:N `protein_analyses` 1:N (`mutations`, `reports`, `jobs`).
**Migrations:** Alembic, versioned. Any schema change ships with a migration.

**Anticipated — `ranking_runs` (D-015 §4).** Iteration 2 makes cohort ranking the spine, so the
schema must anticipate it now: a `ranking_runs` row (target-list version, scorer version,
timestamp) with a **nullable** `ranking_run_id` FK on `protein_analyses` — cheap to establish
up front, expensive to retrofit into an applied migration chain. **This is not yet built**
(PR A created neither table). The load-bearing consequence for whoever writes the
`protein_analyses` migration: that single migration must, together, (a) create
`protein_analyses`, (b) add the deferred `jobs.analysis_id` FK that closes D-009 §1 Amendment 4,
and (c) create `ranking_runs` + the nullable `ranking_run_id` FK. Because `protein_analyses`
does not exist yet, all of this is a clean first-cut, not a retrofit.

**Engine — Postgres from the first migration (D-012); host is the existing Fly **MPG** cluster
`sentinel-holy-rain-4562`, database `pharmfoldmdk`, pgvector **v0.8.2** (D-014).** "Fly
Postgres" is **not** precise enough: it spans two products, and the **unmanaged** one cannot run
pgvector at all — measured, `pg_available_extensions` returns zero rows for `vector`, so the
extension is absent from the image rather than merely disabled. Prod is **Postgres 16**; keep
local dev and any Postgres CI container on 16.

⚠️ **pgvector is installed in the `extensions` schema, not `public`** — a migration emitting a
bare `vector(384)` fails with `type "vector" does not exist`. The first migration that creates a
vector column must schema-qualify the type or set `search_path`, and record which (D-012 §5a,
D-014). Alembic uses the **direct** connection (transaction-mode poolers break DDL); the app
uses the pooled one.

The SQLite-on-Volume prototype path
is closed, not deferred: pgvector hosts the learned embeddings, and the queue-claim mechanism
is Postgres-specific. **The test DB remains SQLite (D-005), so prod and test run different
engines** — and `SELECT … FOR UPDATE SKIP LOCKED` is a **syntax error** on SQLite, not an
unsupported feature that degrades (measured on SQLite 3.45.1: `near "FOR": syntax error`;
`FOR UPDATE` alone is rejected too). The claim path therefore **cannot execute in the suite at
all**. It is reached through a repository seam — a `JobQueue` protocol with `PostgresJobQueue`
(real, never run in CI) and a test double named `UnlockedFakeJobQueue` so no reader mistakes it
for coverage. **The seam is an honesty mechanism, not coverage**: only a Postgres integration
job in the gate will ever exercise the real claim path, and that job does not yet exist. This
is the same shape as the JARVIS `create_all`-vs-migration-chain gap, which was invisible to a
green suite until a Postgres CI job exposed it.

---

## 5. Storage, Deployment & Inference Topology

### Topology — serving tier + **split compute** (D-004, amended by D-011)

- **Serving tier — Fly.io (always-on, no GPU):** Streamlit + FastAPI, Postgres + pgvector,
  Fly Volume. Hosts the app, the data, and the **job queue**.
  **Fly GPU is eliminated, not deprioritised (D-011):** Fly deprecated GPU Machines and they become
  **unavailable after 2026-08-01**. Fly is the serving tier only.
- **Inference tier A — local machine (NVIDIA Blackwell, 8 GB VRAM):** a **`worker/`** process that
  **pulls** pending jobs from Fly over an authenticated **outbound** connection, runs
  ESMFold (int8 trunk / bf16 base, `chunk 64`) on the local GPU, uploads PDB/pLDDT/PAE back, and
  marks the job done/error. **Not deployed to Fly.** No inbound exposure; jobs queue when offline.
  **Scope: every target under the measured length ceiling** — Trop-2 (~250 aa), Nectin-4 (~350 aa),
  the 440 aa class. **0 crashes in ~94 folds.**
- **Inference tier B — rented GPU, one-time batch (D-011):** targets **above** the ceiling
  (HER2-class, ~630 aa). **RunPod RTX A6000 48 GB @ $0.49/hr**, Secure Cloud, per-second billing,
  no egress fees, **container disk only** (network volumes bill $0.07/GB/month even when stopped).
  A ≥24 GB card runs fp16 `esmfold_v1` **unquantised and unchunked**, so the entire local
  mitigation stack stops binding. **Estimated total for the Iteration-1 large-ECD cache: ~$0.25.**
  The batch must be **committed, reproducible code in this repo**, not a one-off script
  (binding condition of D-009 §3).

### Fly serving-tier specifics

- **Database (D-014):** the existing **Fly MPG** cluster `sentinel-holy-rain-4562`, own database
  `pharmfoldmdk`, **Postgres 16**, pgvector **v0.8.2** enabled per-database from the dashboard.
  **Narrowed from "Fly Postgres addon" deliberately** — that phrase spans two products, and the
  **unmanaged** one cannot run pgvector at all (measured: `pg_available_extensions` returns zero
  rows for `vector`, i.e. absent from the image, not merely disabled). No `CREATE EXTENSION`
  step is needed here; the extension is already on, **in the `extensions` schema** — see §4.
- **Compute isolation — a named coupling, not a safety assumption (D-014):** the cluster is
  Basic / Shared×2 / 1 GB RAM across *all* its databases, shared with JARVIS's `fly-db`.
  Logical isolation is real (separate database, separate extension state, a bad migration is
  contained); **CPU and memory are not**. A runaway query in one database can starve the other,
  and a cluster-level incident takes both down.
- **Connections (D-014):** Alembic on the **direct** string (transaction-mode poolers break DDL
  and session-level operations), the app on the **pooled** string. Both in secrets, never in the
  repo.
- **Files:** Fly Volume at `/data`; DB holds paths only.
- **Backups:** MPG managed backups + volume snapshots.
- **Migrations:** Alembic versioned scripts, applied on deploy.
- **Region:** SJC, matching the cluster and existing apps — since Feb 2026 inter-region private
  networking bills at Machine rates, so the serving tier should not drift out of SJC.

### Deploy gate (D-005 → proven & hardened in D-008) — no untested code to prod

- **GitHub Actions:** PRs and pushes to `main` run a `test` job; the **Fly deploy job runs
  only if tests pass** (`deploy: needs: [test]`). Needs `FLY_API_TOKEN` in Actions secrets.
- **Branch protection on `main` is the actual enforcement (D-008):** require a PR, require
  the **`test`** check, **`enforce_admins: true`** (no bypass, owner included), no direct
  pushes. Without it the gate is advisory — a failing check does not block a merge, and
  `git push origin main` walks straight past it.
- **No `paths-ignore` (D-008):** since `test` is a *required* check, it must report on every
  PR or a doc-only PR hangs unmergeable; the ~20s suite therefore runs on everything. When
  real deploy is wired, guard the **deploy job** (not the trigger) against doc-only changes.
- **Locked dependency graph (D-013 + Amendment A):** the gate installs
  **`requirements-dev.lock`** with **`--require-hashes`**. The `.txt` manifests are the
  human-edited inputs (what we want); the `.lock` files are what those resolved to — every
  transitive pinned and hashed, compiled by `uv pip compile --generate-hashes --universal
  --python-version 3.11`. **uv is a local authoring tool and is not installed in CI**; the lock
  is plain hashed-requirements format, so the gate uses stock pip.
  **Why the lock and not just exact pins:** four direct pins resolved to *thirteen* installed
  packages, so pinning the manifest left nine transitives floating — a breaking upstream release
  could redden the gate with no commit in this repo. The requirement is that a red gate is
  always attributable to a commit here, and only the lock delivers that. It is the
  environment-level counterpart of the pinned model revision recorded per-fold in
  `inference_settings` (D-004), and §7's reproducibility commitment needs both.
  **Install and test are independently breakable:** when the check goes red, read which step
  failed. Pip caching is deliberately **off** (D-013 §3). The CUDA stack
  (`torch`/`transformers`/`bitsandbytes`) is **never** installed in CI; it belongs to the GPU
  tier and gets its own manifest with `worker/`.
  *Residual:* the lock fixes versions and hashes, not index availability — a PyPI outage still
  reddens the gate and is not attributable to a commit.
- **UI component tests in the `test` job (D-046).** The `test` job gains a Node step
  (`actions/setup-node`, Node 20 to match the Dockerfile builder) running **`npm ci && npm run
  test`** in `ui/` — `npm ci` enforces the committed `package-lock.json` (D-037: fails on drift,
  never rewrites it), and `vitest run` executes the component suite non-interactively. It runs in
  the same *required* `test` job, not a separate one, so a red UI test blocks the gate: a UI step
  that could not fail would read as coverage without being it. The test devDependencies are
  build-time-only and never reach the runtime image (image-contents test, D-046 §2).
- **Postgres integration job (D-017) — the seam's other half.** A second CI job, `postgres`,
  stands up a real **Postgres 16** service container (matching prod, D-014), installs the same
  locked deps, applies migrations with **`alembic upgrade head`** (the real chain, *not*
  `create_all`), and runs the `@pytest.mark.postgres` tests. Those prove what the SQLite `test`
  job structurally cannot: that the migration chain builds the schema, that env.py's Postgres-only
  `search_path` SET runs without error, and that `PostgresJobQueue.claim`'s `FOR UPDATE SKIP
  LOCKED` is **atomic** (a locked row is skipped; all-locked yields None). `deploy` now
  **`needs: [test, postgres]`**. The postgres-marked tests auto-skip in the `test` job (no
  `DATABASE_URL`), so they are inert there and real only here.
  **Not yet a branch-protection required check** — that is an owner action (branch protection is
  owner-set, D-008), deliberately deferred until the service-container job proves stable, per the
  D-013 caution that a flaky *required* check with no admin bypass deadlocks every PR. Until it is
  required, `deploy: needs` is the gate: a broken migration cannot deploy even if a PR merged.
  **Still unexercised:** the service image is stock `postgres:16` and there is no vector column
  yet, so env.py's `search_path`→`extensions` *resolution* is proven only insofar as the SET does
  not error; it switches to a pgvector image when the vector-column migration lands (D-017).

### ⚠ VRAM constraint (8 GB) — fold path is UNRESOLVED (D-006 invalidated by S-001)

**Measured 2026-07-19 (S-001):** the fp16 model is resident at **8116 MiB** against **7043 MiB
free / 8151 MiB physical** — it spills to shared system RAM *before any fold*. **fp16 alone does
not fit `esmfold_v1` in 8 GB.** The D-006 ladder (fp16 → chunking → cap → ECD → caching) is
**invalid at rung one**: rungs 2+ reduce *activation* memory and cannot fix a *resident-weight*
overrun. Weights are **9.58 GB on disk** (not ~2.5 GB). Warm-cache load is **15–16 s**.

**The local GPU tier is BLOCKED ON HARDWARE (S-002 Q1, 2026-07-19).** Three 630 aa attempts each
ended in an identical host bugcheck (`0x00020001`). Windows event logs (**not** the minidumps —
unreadable without admin) identify the component: **PCIe Advanced Error Reporting faults on the
inference GPU itself** (`PCI\VEN_10DE&DEV_2D39` = RTX PRO 2000 Blackwell), with 3 fatal WHEA
errors matching the 3 crashes 1:1 and **no** display-driver TDR. VBS/HVCI is running, which is why
a fatal hardware error surfaces as HYPERVISOR_ERROR.

**Latent fault, workload-triggered — neither "unrelated bad hardware" nor "we broke it."**
Corrected AER errors on this exact device predate the project (148 across 7 days since
2026-05-27, on days with no ESMFold), and a May 27 fatal proves the link can go fatal without us.
But the `0x00020001` signature has **zero** occurrences before today. One fatal in eight weeks vs
**three in twenty minutes** ≈ four orders of magnitude — the workload is an **accelerant**.

**Mechanism — TESTED 2026-07-19 AND NOT SUPPORTED.** The hypothesis was *spill → sustained PCIe
traffic → corrected errors escalate*. Both arms were run under the new driver: **int8 non-spilling
(600 s, 83 folds) and fp16 spilling (368 s, 5 folds) each logged 0 corrected, 0 fatal, 0 bugchecks.**
Restoring spill did **not** restore errors, so spill is **not sufficient** to trigger the fault at
248 aa under driver 596.72. The **NVIDIA driver update (595.71 → 596.72)** is now the leading
explanation — but is **not established**: the original crash condition (**HER2, 630 aa**) was never
reproduced, and a 6-minute clean window has weak power against a fault that historically appeared on
8 days out of ~54. **Absence of errors is not evidence the fault is gone.**

**HER2 WAS TESTED (S-004, 2026-07-19) — IT CRASHED THE HOST.** int8, `chunk 64`, **no spill at rest**
(resident 5351 MiB vs 7043 free), bugcheck `0x00020001` at **19:02:28**, ~56 s into the first fold.
**Fourth crash of the day; fourth on HER2.** Driver 596.72 and other GPU apps are eliminated — it
reproduced with the new driver and an empty GPU process list.

**Sequence length is the discriminator; duration is not.** The fp16 control had just run five
individual folds of **73–74 s each without crashing**; S-004 died at **~56 s** — a *shorter* fold.
Spill is eliminated independently, since int8 does not spill and crashed anyway.

**The strongest, instrument-free evidence:**
> **4 crashes in 4 HER2 (630 aa) attempts. 0 crashes in ~93 Trop-2 (248 aa) folds** — both
> precisions, spilling and not, including 83 consecutive folds under sustained load.

**⚠ WHEA corrected-error rate is NOT a valid leading indicator (F-001).** The fatal is logged in the
same second as the corrected errors in all four crashes, and six burst days produced 65/40/31
corrected errors with **zero** fatals. Judge stability by **crash count**, never by corrected-error
rate.

**Length ceiling bisected (S-005, 2026-07-19): it lies in (440, 630).** HER2 ECD truncated to
**440 aa folded clean** — 28.6 s at `chunk 64`, peak **6665 MiB** (no spill), pLDDT 84.27,
440/440 CA atoms, **zero WHEA events, zero bugchecks**.

**Consequence — a far narrower constraint than S-004 alone implied.** The local tier **can** fold
most of the curated ADC set: Trop-2 (~250 aa), Nectin-4 (~350 aa), and anything up to at least
**440 aa**. **Only HER2-class targets (>440 aa) need external compute.** Still inside D-004 §5,
still **not** retrieval.

> *Inference, not measurement:* peak at 440 aa left only **378 MiB** of headroom against 7043 MiB
> free, so 630 aa at `chunk 64` would plausibly have spilled mid-fold — meaning **HER2 might yet
> fold at `chunk 16/32`**, which S-004 crashed before reaching. S-004's peak was lost with its
> corrupted JSON, so this is untested.

#### The ceiling is now a structure, not two ints (D-077 decisions 3–4, 2026-08-04)

**Structural change, no routing change.** `CEILING_KNOWN_GOOD` / `CEILING_KNOWN_BAD` no longer exist
as bare module-level integers. `core/manifest.py` exports a single frozen **`FoldCeiling`** carrying
`(hardware, dtype, chunk_size, known_good, known_bad, unstable_band)`, and `LOCAL_CEILING` reads its
`dtype`/`chunk_size` from `TIER_RECIPE["local"]` rather than restating them. **440 and 630 are
unchanged and not one target moved tier** — the instrument moved, the number did not (D-077: the
constant moves only in the same PR as the F-entry that measured it).

**Why:** `worker/ceiling_probe.py` takes `--dtype` as a free CLI argument and defaulted it to `fp16`
(it was written for the A6000, D-022). A local run that forgot `--dtype int8` would have measured a
ceiling for a recipe **the local tier does not use**, and that number would have been written into
the constant that routes **int8** production folds — two paths to one quantity, never compared.
`--tier local` now resolves the recipe from `TIER_RECIPE` and **refuses** a contradicting `--dtype`.

**A second copy was found in the same pass:** `scripts/ecd_lengths.py:51-52` declared its own
`CEILING_KNOWN_GOOD`/`CEILING_KNOWN_BAD`, and `core/manifest.py`'s comment documented the
duplication ("mirrors `scripts/ecd_lengths.py:46-52`"). It now imports the structure, and
`tests/test_manifest.py::test_no_second_copy_of_the_ceiling_survives_in_the_tree` fails if a bare
literal reappears under `core/`, `scripts/`, `worker/` or `app/`.

**The boundary may be a band.** The probe assumed a sharp monotone boundary and *could not report
that it isn't one*: any single `ok` raised the floor, any single failure lowered the ceiling, and
`next_probe_length` then raised `ValueError` on inverted bounds — so `ok@560, oom@500`, entirely
plausible 378 MiB from the wall, made the probe **crash rather than report the flakiness**. D-077
dec 4 pre-registered that crash as **a result, not a bug**, and added a repeat layer above the
untouched bisection: a length is known-good only on **4 consecutive** clean folds (k inherited from
630 aa's 4-for-4, not invented), known-bad only on 4 consecutive failures, and anything else is
**`unstable`** — a legitimate reportable outcome. `FoldCeiling.unstable_band` carries it, and
**routing uses the low end**, because the cost of routing an unfoldable target to local is a crashed
host while the cost of routing a foldable one to rental is a few dollars.

**Not yet measured.** The ceiling itself is still open: `unstable_band` is `None`, the band
(440, 630) is unprobed, and Task 3 Arm A is owner-authorised GPU work.

#### ⚠ MEASURED 2026-08-04 (F-012): the chunked trunk is NOT output-invariant

**`chunk_size` is a recipe dimension, not a memory knob.** Folding one fixed 114-aa sequence at
`int8` under chunk 64 / 32 / 16: **64 and 32 were byte-identical; 16 diverged** — 45/342 coordinate
values (max **1.0e-3 Å**, one unit in the last place the PDB format writes) and 111/114 pLDDT values
(max **2.08e-3**). A determinism control was run first — two folds at the *same* recipe are
byte-identical — so this is a real effect of `chunk_size`, not run-to-run noise.

D-077 decision 2 fixed this reading before the run: *differ at all, by any margin* → **the local
ceiling is defined ONLY at chunk 64, folds across chunk sizes are NOT commensurable, and the
extended-envelope branch (Arm B, probing at chunk 32/16) is ABANDONED, not deferred.** Arm A, at the
production recipe, is unaffected.

**The consequence for the existing cohort, found by querying rather than assumed.** `fold_provenance`
(D-045) shows the 80 folded rows span **three recipes**: `('int8', 64)` × 42, **`('fp16', None)` × 34**,
`('fp16', 64)` × 3, plus one row with no provenance. The 34 unchunked folds are D-042's history —
rental `chunk_size` was `None` until the first rental run falsified the no-chunk assumption. This was
harmless only while chunking was *assumed* output-invariant.

**⚠ What is NOT established:** the run compared 64/32/16 at int8 on one short sequence. **`None` vs
`64` is unmeasured**, at fp16 and at cohort lengths. So it is not known whether those 34 folds differ
from the 37 chunked ones, or by how much — and the claim that they are fine is as unsupported as the
claim that they are not. That measurement is **reserved as F-015**. No reported result changes:
F-004, F-005 and the ranking are untouched, and nothing here reaches the scorer.

**Consequence:** cache generation *may* move to **different compute** (cloud GPU / Colab / cluster)
to de-risk the schedule — a ≥16 GB GPU also makes the fp16 non-fit stop binding — but that is
de-risking, **not** a verdict against the local tier. Inside the D-004 §5 boundary either way, and
**not** a retreat to retrieval.

**Replacement rung one is now MEASURED (S-003, 2026-07-19): quantize the ESM-2 LM trunk to int8
(`bitsandbytes`), folding head at full precision.** On the Trop-2 ECD (248 aa): resident
**5351 MiB**, peak **5779 MiB** — comfortably under both the 7799 MiB target and the 7043 MiB
actually free — **no spill**, and ~1.8× faster than fp16. Mean pLDDT 74.7 vs the 70.7 fp16 baseline —
**verified reproducible** (two folds: pLDDT delta 0.000, CA-RMSD 0.0000 Å, so the shift is a real
precision effect, not variance) and **verified non-degenerate** (248/248 CA atoms, zero NaN coords,
Rg 18.74 Å against a 17.9 Å compact-globular expectation). *Accuracy is still unproven: pLDDT is
self-confidence, so a cross-precision TM-score/RMSD comparison remains the outstanding follow-up.* **bf16 is rung two**
— same footprint as fp16 so it cannot fix the fit, but it costs nothing and holds quality (+0.2).
CPU-offload is **excluded by design**: it trades VRAM for the PCIe traffic implicated in the link
fault. Per D-004 §5 this stays inside "smaller model / narrower targets" and explicitly **does not**
mean retreating to AlphaFold retrieval.

**Still unconfirmed:** whether a non-spilling configuration stops the host crashes — that is
S-002 Q1, now testable against a config that genuinely fits.

> **Resolved — D-012 (engine) + D-014 (host).** Prod is **Postgres-first** from the first
> migration; the SQLite-on-Volume prototype path is closed, not deferred. Host is the existing
> **MPG** cluster with pgvector v0.8.2 (see §5). *(The **test** DB remains SQLite — D-005 — and
> D-012 §3–§5 turns that split from a footnote into a named structural exposure: the
> `SKIP LOCKED` claim path is a **syntax error** on SQLite and has never executed.)*

---

## 6. Iteration Roadmap (DL mapped)

| Iter | Product goal | Deep-learning content |
|------|--------------|-----------------------|
| **1 (MVP)** | **Cache-first (D-009 §3)**: Mission Briefing + curated ADC target DB served from pre-folded cached artifacts; live user folding deferred. **Two caps, not one (D-009 §3 amendment):** the **cache-build cap** is bounded by *memory fit + host stability only* — wall time is **not** a criterion, so `chunk 16/8` and multi-minute folds are acceptable; the **interactive cap** (Iteration 1.5+) is latency-bounded (`chunk ≥32`, `<120 s`). This is what makes large ECDs such as **HER2 (630 aa)** reachable for the cache even if never viable interactively | **ESMFold run in-project (D-003)** — the pipeline that *produces* the cache must be real, committed, reproducible code (binding condition of D-009 §3) |
| **2** | **Target ranking becomes the spine (D-015)** — a comparative view over the 82-target cohort (baseline evidence rank vs. structural rank, delta, movers), with single-target analysis as the drill-down. Plus mutation simulator, comparison views, pocket scoring | **The learned ADC-suitability scorer (D-015 §3)** — structure-derived features from our own ESMFold folds → a small trained model calibrated on the 22-positive labelled set, evaluation pre-registered (leave-one-out, fixed feature count, **two** named negatives incl. strong-correlation-is-null), with per-target fold/boundary/pLDDT diagnostics gating any ranking claim (D-015 §1a: disagreement is the expected outcome; the comparator is not an oracle). ESMFold stops being the deliverable and becomes the scorer's **input**. Also learned mutation-impact / druggability |
| **3** | Reports, semantic library search | Neural embeddings + pgvector semantic search; report synthesis |
| **4 (stretch)** | Epitope suggestion, ADC complex modeling, agentic workflows | Advanced/agentic DL |

---

## 7. Cross-Cutting Concerns

- **Security (MVP):** username + hashed password (bcrypt/passlib); protected API routes.
- **Confidence honesty:** pLDDT/PAE surfaced clearly; outputs framed with caveats.
- **Testing (D-005):** all tests live in **`tests/`**. Two kinds — **functional** (`pytest`,
  `*.py`: data layer, inference logic, API, worker contract) and **user-based** (structured
  human scenarios) — see [`docs/Test_Plan.md`](docs/Test_Plan.md). The **test DB is SQLite**
  (in-memory/temp); external calls and ESMFold inference are **mocked** for speed/determinism.
  ~~**Gap:** SQLite can't exercise pgvector/Postgres-specific paths~~ — **the Postgres
  integration job now exists (D-017):** a `postgres` CI job applies the real Alembic chain and
  exercises `SKIP LOCKED` against Postgres 16. The **fold-runner** adds a parallel split
  (D-018): its pure logic (provenance, pLDDT rescale, truncation recording) is unit-tested on
  the gate, while the GPU-bound `fold` auto-skips without torch+CUDA (`@pytest.mark.gpu`) and is
  validated on a GPU host — there is no GPU CI runner.
- **Reproducibility (course expectation):** pin model weights/versions, seed where
  relevant, and record any training/fine-tuning config so results can be reproduced.
  - Serving-tier deps are locked and hash-verified in CI (D-013 Amendment A).
  - **GPU-tier deps are a named, accepted gap (D-018):** `worker/requirements.txt`
    (`torch==2.11.0+cu128`, `transformers==5.14.1`, `bitsandbytes==0.49.2`, measured in S-003) is
    **never installed by CI** and so is **not covered by the lock-file guarantee** — a breaking
    release there is discovered at fold time, not by a red gate. Reproducibility of the GPU tier
    therefore rests on these pins plus the ESMFold weight revision pinned in `worker/runner.py`
    (`MODEL_REVISION`). `accelerate` has no measured pin yet (D-016: named, not invented) — pinned
    from the first GPU install.
  - **Every fold records its own provenance (D-018):** dtype, chunk_size, model revision,
    sliced-ECD-vs-whole, ECD bounds, and any length-cap truncation — written beside the artifacts.
    The truncation flag is load-bearing: D-015 §1a excludes truncated folds from ranking claims,
    which is unenforceable unless captured at fold time. **Since D-045, the record also names the
    software environment under the weights** — `torch_version`, `transformers_version`, `device_name`,
    `cuda_version` — all optional (the 80 pre-D-045 folds carry none; the cohort is two honest
    populations, and the UI shows the split rather than inventing values). Captured post-fold in
    `fold()` and never fatal (a capture failure can't take down the batch, D-042); `build_provenance`
    stays torch-free so the module still unit-tests on the no-CUDA CI gate.

---

## 8. Repository Layout (target)

```
Project-PharmFoldMDK/
├── ARCHITECTURE.md          # this file — living source of truth
├── README.md                # how to run / deploy (kept current in Phase 6)
├── CLAUDE.md                # living-doc governance rules
├── app/                     # Fly serving tier (FastAPI): main.py (create_app factory),
│                            #   routes.py (D-031/D-036 five worker→Fly routes), artifacts.py (FoldSpec
│                            #   projection + compensated Volume+DB persist), deps.py, config.py
├── core/                    # queue.py (JobQueue seam + is_stale), manifest.py (D-023 routing
│                            #   table + D-024 coverage), enqueue.py (D-026 manifest → analyses+jobs;
│                            #   `python -m core.enqueue` CLI, subset-capable for the first fold),
│                            #   contracts.py (FoldSpec + TIER_RECIPE + TILE_WINDOW_AA —
│                            #     tier-neutral stdlib leaf, DEP-001 / D-112),
│                            #   features.py (D-027/D-058 pure six-feature extractor + in-repo
│                            #   Shrake-Rupley SASA, zero third-party imports; ships, never served),
│                            #   scorer.py (D-041/D-060 L2 logistic regression by hand — IRLS, LOO,
│                            #   nested-CV lambda, Spearman; pure stdlib, seven parameters),
│                            #   foldability.py (D-077 dec 6 census cost model: span → local/
│                            #     rental/over_ceiling. A COST axis, never a suitability axis —
│                            #     a test asserts scorer.py and features.py never import it)
├── worker/                  # GPU tier (NOT deployed to Fly): runner.py (D-018 fold-runner),
│                            #   orchestrator.py (D-030 job-pull loop, pure/transport-agnostic),
│                            #   http_client.py (D-031 concrete HTTP QueueClient, gzips PAE),
│                            #   main.py (entry point: wire client+loop+fold, `python -m worker.main`),
│                            #   ceiling_probe.py (D-022 A6000-ceiling bisection, owner-run;
│                            #     D-077 adds --tier recipe resolution + the k=4 repeat layer),
│                            #   fold_compare.py (D-077 exact chunk-invariance comparator, pure),
│                            #   fold_supervisor.py (D-082 persistent fold child),
│                            #   ceiling_climb_child.py (persistent climb child),
│                            #   rb_tile_child.py (D-105 one-shot tile child — exits per tile),
│                            #   requirements.txt (CUDA deps + httpx, never installed by CI)
├── db/                      # models (db/models.py) + Alembic migrations (db/migrations/)
├── scripts/                 # ecd_lengths.py, map_genes_to_uniprot.py, deploy_guard.py (DEP-002),
│                            #   curate_group_b.py (D-057), extract_features.py (D-058 offline
│                            #   feature driver + protein_features loader; excluded from the image),
│                            #   fit_scorer.py (D-060 scorer fit driver; written, not run on real labels),
│                            #   intersection_check.py (D-073 pre-fit denominators A-I; owner-run
│                            #   against the LIVE deployment, stdlib only, not gated),
│                            #   attention_control.py (D-075 dec 3 popularity-matched control:
│                            #   --freeze snapshots pdb_present + pub_count ONCE with query+date to
│                            #   data/attention_proxies.json, --control reads ONLY that snapshot and
│                            #   never queries, so a re-run is byte-identical; stdlib, owner-run),
│                            #   rb_local_tile_folds.py (RB re-gate; D-105 process-per-tile)
├── tests/                   # pytest; SQLite test DB (D-005). doubles.py = test-only fakes
├── docs/                    # plans, notes, and the design-decision log (README.md);
│                            #   GUIDE-renting-hold48.md + BUDGET-hold48-tiers-2026-09-04.md (D-113, D-114; D-115 AST pin)
├── notebooks/               # miniature_NECTIN4.ipynb (D-072) — demo-only live-fold walkthrough of
│                            #   the whole pipeline on one target; imports real core/+worker/, NOT
│                            #   gated, NOT in the image (excluded via .dockerignore)
├── .github/workflows/       # CI: test + postgres gates → Fly deploy job (D-005/DEP-002)
├── Dockerfile               # serving-tier image: runtime tier only, no worker/CUDA (DEP-001)
├── .dockerignore            # keeps worker/, venv, tests, docs out of the build context (DEP-001)
├── fly.toml                 # Fly serving-tier config: app pharmfoldmdk, always-on, Volume mount
├── alembic.ini              # migration config; URL from $DATABASE_URL (direct conn, D-014)
├── pytest.ini               # pythonpath=. so tests import core/ and db/ (PR A)
├── requirements.txt         # runtime deps — human-edited input, exact pins (D-013)
├── requirements-dev.txt     # runtime + test deps — human-edited input (D-013)
├── requirements.lock        # compiled: every transitive pinned + hashed (Amendment A)
├── requirements-dev.lock    # compiled; THIS is what the gate installs, --require-hashes
└── requirements-notebook.txt # DEMO-ONLY 4th dependency world (D-072): the GPU stack for
                             #   notebooks/, never in requirements.lock/-dev.lock or the image
```

Today the repo holds the governance files, `docs/`, the **keel** (D-007), the **pinned +
locked dependency graph** (D-013), and — as of PR A (D-009 §1 implementation) — the **job
queue**: `core/queue.py` (the `JobQueue` seam, the pure `is_stale` predicate, and
`PostgresJobQueue`), `db/models.py` (`JobRecord`), and the first Alembic migration under
`db/migrations/`, plus the **fold-runner** (`worker/runner.py` + `worker/requirements.txt`,
D-018 — first GPU-tier code), the **job-pull loop** (`worker/orchestrator.py`, D-030), and the
**Fly transport** (`app/` + `worker/http_client.py`, D-031 — first application code on Fly). The
rest — the `Dockerfile` and real Fly deploy wiring, the Streamlit frontend, and the remaining
Database Plan tables — is created as iterations land, and this layout section is updated when it
changes.

The GPU tier's dependencies (`torch`, `transformers`, `bitsandbytes`) are **not** in these
manifests and will live in a separate one under `worker/` — CI runs on a CPU runner and must
never install a CUDA stack.

---

## 9. Governance (how this doc stays true)

1. **Every PR that changes architecture updates this file in the same PR.** No exceptions.
2. **Every design decision is written into [`docs/README.md`](docs/README.md) *before*
   the work it describes is finished** — the decision log leads the code, not the reverse.
3. When a decision in the log changes the system's shape, fold the outcome into the
   relevant section here so this document never drifts from reality.
