# PASTE-READY (REISSUE) — `D-109` corrected + `F-066` — T5 hold-48, P11717, and the cohort-82 intersection

> **Reissued:** 2026-09-02, after Code's PART 3 measurement. **Supersedes the first `D-109` draft in
> full** — do not land the earlier version. ⚠ Three Planner errors in that draft are corrected here
> and named in §Corrections, not patched away.
>
> **Integers confirmed free on `006d7a0`** (Code, this session): live maxima `D-108` / `F-064`.
> `F-050` remains RESERVED and unwritten. ⚠ `F-066` confirmed free and **LANDED 2026-09-02** alongside `D-109` and `F-065`; RESERVED.md's pointers moved in the same commit.
>
> ⚠ **No build, no enqueue, no rental, no fold, no repair.** `F-065` from the prior document stands
> unchanged and is not reproduced here.

---

## §Corrections — three Planner errors in the first `D-109` draft

1. ⚠ **The FAT2 statement was inverted.** The draft read *"at a 1,656 window, FAT2's run clears by
   18 residues."* FAT2's largest run is **1,674 — eighteen residues ABOVE 1,656.** It does not clear.
   **The error ran against the Planner's own recommendation:** at 1,656, four of the five non-mucin
   oversized runs already require interior cuts, so the incremental cost of 1,026 is **CDH23 alone**,
   not six proteins. **The draft overstated the price of its own ruling by a factor of five.**
2. ⚠ **`MUC16` was counted in ruling 5 after ruling 3 removed it.** The entry contradicted itself
   across two of its own rulings. Within the 45 the oversized-run set is **five**, not six.
3. ⚠ **The order requested a gene symbol no manifest carries.** No `census_manifest*.csv` has a
   symbol column. Code substituted `data/census/census_labels.csv` and **named the substitution.**
   The Planner wrote the order from the log's prose about the data rather than from the data.

4. ⚠⚠ **`F-015` was cited as having measured the chunk-size effect. It has measured nothing** — it is a
   reservation for an undesigned GPU run, and `docs/README.md` says so at three places. The measurement
   belongs to `F-012` alone. **Caught by Code before merge; landing it would have made this entry the first
   ever to cite `F-015`, which is the `F-050` failure `RESERVED.md` records against itself.**

⚠ **This is the fourth schema-or-arithmetic assertion the Planner made from a secondary source in one
session** (the others: F-017's absence, and four non-existent column names). **It is a pattern, not
three incidents, and `F-066` is not the place it belongs — it belongs in whatever entry records the
Planner's conduct this session.**

---

## PART 1 — `D-109` (REISSUED)

### D-109 — The T5 hold-48 is ruled in the repository log, retiled at the trained context, the mucins are held on their nature, and three cohort-82 targets are inside the hold

- **Date:** 2026-09-02 · **Status:** accepted — **spec only. No build, no enqueue, no rental, no fold.**
- **Ruled by:** the owner, in session 2026-09-02, on four points: (1) the repository `D-NNN`
  namespace governs; (2) the tile window returns to the trained context; (3) the three mucins are
  held on their **nature**; (4) **P11717's record is the pending row.**
- **Supersedes:** the tile geometry of the external spec at issue **#210** (1,656 / 128 / 1,528).
  ⚠ The rest of #210 is **adopted**: the 45/3 split, the stitch rule, block-diagonal PAE with null
  off-block, pilot-first, and must-be-able-to-fail success criteria.
- **Relates:** `D-104` · `F-060` · `D-095`+am1 · `D-098` · `D-090` · `D-064` dec 3 · `D-047` ·
  `F-042` · `D-106` · `D-107` · `D-108` · `F-012`/`F-015` (commensurability) · `F-065` · `F-066` ·
  `F-004` and `PAPERS-v2.md` P-001 (ruling 7).

#### Context

`jobs` holds **48 rows at `status='pending'`** — all `tier IS NULL`, `attempts = 0`,
`claimed_at IS NULL`, `structure_source = 'esmfold_local'`, created at the identical timestamp
`2026-09-01 18:06:31.58433Z`. They are the remainder of `cohort_tranche = 5`: **728 complete + 48
pending = 776**, matching `D-091` ruling 2's held 776.

⚠ **`tier IS NULL` is the hold mechanism, not a defect.** Under `D-090` the claim filters on tier in
the SQL, so a NULL-tier row is unclaimable. ⚠ All 48 carry `metadata.tier = 'rental'` and
`tier_reason = 'over_local_ceiling'` while `jobs.tier IS NULL` — **the intent is recorded in metadata
and the hold is enforced in the column.** Two representations, deliberately disagreeing.

⚠ **Which manifest the 48 were enqueued from is NOT established.** All seven manifest versions
contain all 48 with `span_aa` agreeing 48/48, so coverage cannot discriminate; only `v7` carries a
`tranche` column and reads `5` for 48/48. **Consistent-with is weaker than established, and is
recorded as the weaker thing.**

#### Ruling 1 — the repository namespace governs

The `D-NNN` / `F-NNN` / `A-NNN` space in `docs/README.md` is the project's only decision namespace.
The external `D-00NN` integers (`D-0024`, `D-0026`, `D-0027`) are **not project decision numbers**.
Their substance is adopted into repository entries or it does not bind. See `F-065`.
⚠ **Not a criticism of the external work** — it produced the 728 folds and this split.

#### Ruling 2 — the tile window is the trained context

| parameter | value | source |
|---|---|---|
| `tile_window_aa` | **1,026** | `D-104` — the trained context (`F-060`). "No card relieves it." |
| `min_overlap_aa` | **128** | adopted from #210 |
| tile count | `n = 1 if L ≤ 1026 else ceil((L − 1026)/898) + 1` | 898 = 1026 − 128 |
| placement | **uniform, full-width**: `start_i = 1 + round(i × (L − 1026)/(n − 1))`, `end_i = start_i + 1025`, final tile forced to `L` | below |
| domain snapping | edges snap to UniProt domain ends within **±64** | adopted from #210 |

⚠ **Why 1,026.** `D-104` names it the **trained context** — a property of ESMFold, not of a card —
and routes `L > 1,026` to **unroutable**: "not folded, not dropped, not cut." A 1,656-aa tile sits
**630 residues outside** it; every such tile is an extrapolation and its pLDDT uninterpretable
alongside the 3,497 folds already committed (`D-039` records pLDDT as uncalibrated for this cohort
even inside the context).

⚠ **Uniform full-width placement replaces #210's fixed stride.** A fixed stride leaves a short
terminal tile (IGF2R would end on 468 residues); termini are already the lowest-confidence region and
a short terminal tile compounds that with a small-context prediction. Uniform placement gives every
tile the full window and overlap **≥ 128 by construction**. ⚠ Overlap is then **variable between
proteins**, so the stitch rule must be per-residue and must not assume constant overlap width.

#### Ruling 3 — the mucins are `out_of_class` on their NATURE

**MUC16 `Q8WXI7` (14,451) · MUC12 `Q9UKN1` (5,364) · MUC17 `Q685J3` (4,368).** Not enqueued, not
tiled, not stitched. **Zero PDB, zero PAE.**

⚠ **The reason is the molecule, not the length.** Heavily O-glycosylated mucins whose extracellular
bulk is dominated by long repetitive PTS/VNTR regions with no single native conformation to predict.
A stitched product **would look like a structure and be a lie** (#210's phrasing, adopted) — `F-047`
in its most consequential form: well-formed, correctly typed, plausible, wrong, no error signal.

⚠ **Length is NOT the discriminator and must not be recorded as one.** A future long protein with an
ordered ECD is not automatically `out_of_class`; a shorter mucin is not automatically in class.
**The category is a per-protein judgement, made by the owner.**

⚠ `out_of_class` is a **held** state with a stated cause, not a terminal one. The named future path
is `D-107`'s msa tier, which is **not built**.

#### Ruling 4 — the build sequence, gated

**No step runs without a separate build GO. This entry is not that GO.**

1. **Emit tile rows** `{accession, start, end, parent_job_id, tile_index, n_tiles}`. Parent stays
   `tier IS NULL` until stitch succeeds — the `D-090` hold, unchanged.
2. **Fold tiles on the existing ESMFold path.** Same T5 recipe (`fp16` / chunk 64), **resolved at
   fold-time per `D-047`, never from frozen `inference_settings`.** Every tile `L ≤ 1,026`.
3. **Stitch:** overlap residues take the tile with **higher mean pLDDT**, decided per residue.
   ⚠ **No invented gap coordinates.** A residue covered by no tile is an error, not a gap.
4. **PAE per-tile. Stitched PAE block-diagonal. Off-block NULL, never 0.** ⚠ A zero would assert
   measured confidence between residue pairs never present in the same forward pass.
5. **Ceiling writer for the three mucins** — status only, zero artifacts.
6. **Pilot first: IGF2R `P11717`, ECD span L = 2,264 → 3 tiles.** ⚠ **Verified against the row's
   stored sequence by Code** (`length(metadata.sequence) = 2264 = span_aa = fold_length`).

   | tile | start | end | width | overlap w/ prev |
   |---|---|---|---|---|
   | 1 | 1 | 1,026 | 1,026 | — |
   | 2 | 620 | 1,645 | 1,026 | 407 |
   | 3 | 1,239 | 2,264 | 1,026 | 407 |

   ⚠ **Three tiles, not #210's two, and that is why the pilot is worth running: a middle tile has
   two seams,** which is where interior stitch defects live and which a 2-tile pilot cannot exercise.

#### Ruling 5 — the measured cost of 1,026 (CORRECTED)

The 45 non-mucin rows require **161 tiles** at the ruled geometry, against **106** at #210's window.
⚠ **Both figures verified by three independent computations — the recurrence, the closed form `ceil((L − OV)/(W − OV))`, and a constructive walk — which agree per-protein and also reproduce #210's own 106** —
the geometry is sound in both regimes and the difference is a real 52% increase in fold units.
**All 45 exceed one window; the smallest span is LRP4 at 1,705.**

`tranche6_runs.csv` records **6 of 141** in the `one_oversized_run` regime. ⚠ **MUC16 is one of them
and is excluded by ruling 3, so five fall inside the 45.** ⚠⚠ **Four of those five already exceed a
1,656 window** — FAT4 3,037 · FAT3 2,291 · FAT1 2,289 · FAT2 1,674. **The incremental cost of 1,026
is CDH23 (1,175) alone.**

⚠ **Interior cuts stay RD2 per `D-104`.** The disposition of all five — tiled with interior cuts,
held, or routed to `D-107` — is an **OPEN RULING.** This entry does not license them.

#### Ruling 6 — P11717's record is the PENDING row; the failed row is marked, never deleted

**`P11717` (IGF2R) exists twice.** The record is **job/analysis 3356** — `cohort_tranche = 5`,
`status='pending'`, ECD span **2,264**. Job/analysis **57** (`cohort_tranche = 0`, `failed`,
`tier='rental'`, OOM at **2,491 aa**) is the **historical artifact.**

⚠ **Job 57 is RETAINED and MARKED, never deleted or overwritten.** This is the `D-064` decision 3
precedent applied to `jobs`: `ranking_results` id=1 stays in place marked invalid because deleting it
"would silently erase the evidence that a false artifact existed." **The database is held to the same
standard as the log** — corrections are recorded, never quietly patched (`D-002`).

⚠ **What marking means is NOT ruled here** — no schema change, no status value, no write. **Stated,
not built.** See `F-066` for what job 57's error actually records.

#### Ruling 7 — ⚠⚠ three cohort-82 targets are inside the hold, and one is now permanently held

⚠⚠ **The hold-48 intersects the paper's cohort.** Measured against `data/cohort_82_accessions.txt`
(82 accessions, 4 header lines):

| accession | gene | in hold-48 as | tiles |
|---|---|---|---|
| **Q8WXI7** | **MUC16** | **`out_of_class` (ruling 3)** | **none — ever, under ESMFold** |
| **P11717** | **IGF2R** | the pilot (ruling 6) | 3 |
| **Q9NYQ8** | **FAT2** | one of the 45 | 5 |

These are exactly the three the cohort record names as stragglers — *79 folded of 82, 1 failed
(IGF2R), 2 over-ceiling (MUC16, FAT2).* **The hold-48 is where the paper's cohort's unfinished
business ended up.**

⚠ **The cohort's job statuses sum to 83 over 82 accessions** — 79 complete, 3 pending, 1 failed —
because `P11717` spans two job rows (ruling 6). **A count keyed on `jobs` and a count keyed on accession
differ by one here.** Any surface quoting "79 of 82" states which key it used.

⚠⚠ **MUC16 is therefore a cohort-82 target that will never carry an ESMFold structure**, on a stated
scientific cause rather than a compute limit. **That is a named permanent exclusion and it belongs on
the coverage surface and in P-001's limitations**, not only here.

⚠⚠ **OPEN RULING, and it is P-001's, not this entry's: a stitched multi-tile structure is NOT
established as commensurable with a single-pass fold.** `F-012` measured that chunk size alone changes
ESMFold's coordinates and pLDDT — chunk 16 versus 64, at int8, on a 114-aa fixture — and that the folded
cohort spans three recipes. ⚠ **`F-015` is RESERVED and UNWRITTEN.** The `None`-versus-`64` comparison at
fp16 — the cohort's actual variable — is a GPU run that has not been designed. **It has measured nothing,
and is named here as the reservation it is, not as evidence.** ⚠ **That absence cuts toward this ruling,
not away from it:** if single-pass commensurability is itself unmeasured at the cohort's own variable, then
a structure assembled from three separate forward passes is a **larger** break, not a smaller one.
**Folding FAT2 and IGF2R by tiling does NOT make them eligible for the ranking set, and this entry does not
make them eligible.** Whether they enter `F-004`'s denominators is a separate, pre-registerable ruling.

#### Deep-learning justification

The trained context is the constraint the tranche-5 remainder turns on. Ruling 2 keeps every forward
pass inside the regime the network was trained for, so per-residue confidence stays interpretable on
the same footing as the committed folds. Ruling 4 item 4 keeps the pair-confidence head honest across
seams: PAE is a **measured** pairwise quantity, and pairs never co-resident in one pass have **no**
measurement, not a zero. Ruling 3 refuses to emit a network output whose input regime the model
cannot represent. Ruling 7 refuses to let three assembled structures silently enter a ranking fitted
on single-pass folds.

#### Consequences

- The 48 stay unclaimable; `tier IS NULL` is now a documented hold with a named cause.
- ⚠ **`pending` carries two fates** — 45 awaiting a build GO, 3 held on nature — and the schema
  cannot distinguish them. **Stated, not built.** Before any build GO, either a named status exists
  for `out_of_class` or this entry is the statement that `pending` covers both.
- ⚠ Ruling 7 puts an item on **P-001**: MUC16's permanent exclusion, and the commensurability gate on
  FAT2/IGF2R.
- No schema change, no migration, no route change, no `ARCHITECTURE.md` change.

#### Assumptions refused

- That `tier IS NULL` on 48 rows was an enqueue defect. **It is the hold.**
- That the mucins are excluded for being long. **They are excluded for being mucins.**
- That 1,026 is a card limit. **It is the trained context.**
- That adopting #210's substance adopts its numbering.
- That job 57 may be deleted, repaired, or overwritten now that 3356 is the record.
- That a stitched structure is commensurable with a single-pass fold.
- That this entry authorises a build, a rental, an interior cut, a schema change, or the five
  oversized-run proteins' disposition.

- **Amended by:** —

---

## PART 2 — `F-066` (draft finding)

### F-066 — The IGF2R failure recorded as a card ceiling was a fold of the full chain, 227 residues longer than the ECD span the pipeline slices; and the attempt counter recorded zero attempts

- **Date:** 2026-09-02 · **Status:** ⚠ **OPEN.** It closes when the record states what job 57
  actually attempted, **or** when the attribution is corrected wherever it is carried.
- **How known (`D-016`):** read-only SQL against production as `pharmfold-readonly`, 2026-09-02,
  under `ORDERS-Code-2026-09-02-fold-state-measurement.md` PART 3 §6.

**THE MEASUREMENT.** `jobs`/`protein_analyses` **57**: `accession = P11717`, `cohort_tranche = 0`,
`status = 'failed'`, `tier = 'rental'`, `structure_source = ''` (**empty string, not NULL**),
`span_aa` **absent**, `pdb_path` / `pae_json_path` / `mean_plddt` all NULL, `claimed_at` set
2026-07-25, `completed_at` NULL, **`attempts = 0`**.

`jobs.error`, in part: *"CUDA OOM folding **2491 aa** at chunk_size=32 … Tried to allocate 11.84 GiB."*

**THREE THINGS, SEPARABLE.**

1. ⚠⚠ **The object folded was 2,491 aa — the full chain.** The pending row 3356 carries **2,264**,
   the sliced ECD span, verified against its own stored sequence. **The failed attempt was 227
   residues longer than the object the pipeline slices.**
   ⚠ **What is NOT claimed:** that this was a defect at the time. The ECD-slicing discipline may
   have landed after 2026-07-23, in which case 2,491 was correct then and the record simply does not
   say so. **Determining which requires the boundary-method history and has not been done.**
2. ⚠ **The project record carries this as *"IGF2R, A6000 ceiling."*** That reads as a card limit.
   The error is an OOM **on an object 227 residues longer than the one now scheduled.** ⚠ Whether
   the ECD span would also have OOM'd on that card is **unmeasured and is not asserted either way.**
   **The attribution may be right for the wrong reason, which is not the same as being right.**
3. ⚠ **`attempts = 0` on a row that was claimed and failed.** The counter did not record the attempt
   it failed on. ⚠ This is a **third** instance beside the two stale `claimed_open` failures already
   measured, and it is **not established** whether the counter is wrong or is incremented on a path
   this failure did not take.

**WHY IT MATTERS.** ⚠ **P11717 is the ruled pilot** (`D-109` ruling 6). The pilot's success criteria
must not be read against a historical failure of a **different object**. ⚠ And `structure_source = ''`
is an **empty string standing where a named category belongs** — the class this project closes
repeatedly: absent values are named categories with causes, never silent blanks.

**NOT CLAIMED.** That job 57 should be deleted (`D-109` ruling 6 forbids it) · that the ceiling
attribution is wrong (it is **unverified**, which is different) · that the counter is defective ·
that any other `structure_source` row is affected — **it is one row of 3,547.**

---

## PART 3 — What still needs an owner ruling

1. **The five oversized-run proteins** — FAT4, FAT3, FAT1, FAT2, CDH23. Interior cuts (RD2), held,
   or `D-107`. `D-109` ruling 5 leaves this open.
2. **Commensurability** — whether a stitched structure may enter `F-004`'s ranking set. `D-109`
   ruling 7 says not automatically; the ruling itself is P-001's.
3. **MUC16 on the coverage surface and in P-001's limitations** — a cohort-82 target permanently
   without a structure, on a scientific cause.
4. **Whether `F-066` earns its integer**, or folds into `D-109` ruling 6 as a sub-entry.
