# ORDERS — Code — census feature extraction, overnight, to an ARTIFACT

**AUTHORED-SHA256** (range: **first `## §` header → EOF**, anchored to line starts) = `2db7bd0e77536b8fda7b757d55a9047053d7ed3bd2ad88d4d41a24cd60cb5197`
**bytes** = `5552`

> ⚠ **DOWNLOAD AND COMMIT. DO NOT RETYPE. No landing header.**
>
> ⚠⚠ **THE OVERNIGHT RUN WRITES A FILE, NOT DATABASE ROWS.** **Nothing touches production while it
> runs.** The ingest is a separate, later, gated step with its own bar. **The Fly VM is
> `shared-cpu-1x, 512mb` and is the wrong place for this regardless.**
>
> ⚠ Planner grounding `7011e24`. **No GPU, no rental, no fold, no fit, no refit, no ranking run.**
> **Tranche 5 HELD** (`D-091` r2).

---

## §0 — Why this is CPU, and the Planner's correction

**`core/features.py` has ZERO third-party imports** — `D-058` decision 1, enforced. **Stdlib only.
No `torch`, no CUDA, no `numpy`, no `freesasa`.** ⚠ **The 2,690 folds already exist; that GPU spend
is sunk. `mean_plddt_ecd` and `membrane_proximal_plddt` come from pLDDT already stored.**

⚠⚠ **The Planner briefly wrote extraction into the rental budget. It is not a rental claimant.**
**Corrected in `PREWORK-2026-08-20` §1 in the open.**

---

## §1 — ⚠⚠ Task LA — THREE PRE-FLIGHT CHECKS. Do not start the night on any of them unanswered

**LA1 — ⚠ Does `D-079` PERMIT extracting features over census rows?** **Read the entry and quote the
governing sentence.** ⚠⚠ **`D-089` says *"`D-079` bars scoring any census row."* Extraction is not
scoring — but the Planner has not read `D-079`'s clause and will not assert it.** **`D-079` amendment
1's ruling 3 REQUIRES a distribution measurement that requires these features, so extraction must be
permitted or the amendment is unexecutable — but that is an argument, not a reading.** **If it is
barred, STOP AND REPORT: a `D-079` amendment 2 is one turn and the Planner writes it.**

**LA2 — Time it on TEN structures and project.** ⚠ **Report seconds per structure, the spread, and
the projected wall clock for 2,690** — **and pick the ten to span the span-length range, not the
first ten.** *Pure-Python SASA is O(atoms × sphere points); a 200-residue protein and a 1,000-residue
one are not the same job.*

**LA3 — ⚠⚠ DETERMINISM, AND THERE IS A SPECIFIC RISK.** **`largest_patch_fraction` clusters surface
patches. If any step iterates a `set`, `PYTHONHASHSEED` changes iteration order and TIES BREAK
DIFFERENTLY.** ⚠ **Run the same ten structures twice with different `PYTHONHASHSEED` values and
hash-compare the outputs.** **If they differ, STOP AND REPORT — that is a finding about the
extractor, and it would have silently produced a non-reproducible census.**
⚠ **Pin `PYTHONHASHSEED` for the run either way, and record its value in the manifest.**

## §2 — ⚠⚠ Task LB — the acceptance bar, and it is free

**80 `protein_features` rows already exist, all pointing at `cohort_tranche = 0`.**

**LB1 — Re-extract features for those cohort targets with the CURRENT code and compare against the
STORED values, field by field.** ⚠ **Hash the serialised feature tuples; do not compare a summary.**

**LB2 — ⚠⚠ BOTH OUTCOMES ARE PRE-REGISTERED HERE, BEFORE THE RUN:**
- **They match** → **the extractor reproduces its own history and the census run is trustworthy.**
  Proceed.
- ⚠⚠ **They do NOT match** → **the stored cohort features are not reproducible from current code.**
  **That is a FINDING, it is larger than this task, and it lands before any census extraction
  proceeds** — because `F-051`, `F-005`, `F-017` and run 2 all rest on those 80 rows.
  ⚠ **Report the per-field deltas. Do not adjust anything to make them match.**

**LB3 — ⚠ Report which code revision the 80 were extracted at, if the record says.** **If it does
not, say so — that is `F-045`'s shape and it belongs in the report.**

## §3 — Task LC — the run itself

**LC1 — Output is a FILE**: `data/census/census_features.v1.jsonl` or equivalent, ⚠ **plus a manifest
carrying: the code revision, `PYTHONHASHSEED`, start and end timestamps, row counts by outcome, and
the `sha256` of the output.** **A run is a construction, not an observation.**

**LC2 — ⚠⚠ RESUMABLE. An overnight job that dies at row 2,400 RESUMES; it does not restart.**
⚠ **A partial output is marked partial in the manifest and is never mistaken for a complete one.**

**LC3 — ⚠⚠ EVERY FAILURE IS A CATEGORY WITH A CAUSE. Never a skip, never a zero, never a blank.**
At minimum, and add any you find: `structure_file_absent` · `structure_malformed` ·
`span_below_floor` · `extraction_error`. ⚠ **Each carries the accession and the exception where there
is one.** **Counts sum to 2,690 with the key stated.**

**LC4 — ⚠ `F-048`'s 58 are excluded AT COMPUTATION**, per `D-079` amendment 1 ruling 6, carrying
`refused_span_below_floor`. ⚠⚠ **A value computed and then hidden is a value that will eventually be
exported.** **`Q9ULH0` is a 5-residue span.**

**LC5 — ⚠ Do not write to any database. Do not open a tunnel. Do not ingest.** **The artifact is the
deliverable.**

## §4 — ⚠ What happens in the morning, so the night is not wasted

**The artifact is the input to `D-079` amendment 1 ruling 3's distribution measurement** — the
`KB1`–`KB4` work that returned UNDEFINED yesterday. ⚠⚠ **`KB3`'s union — how many rows are out of
range on AT LEAST ONE feature — is the number that decides whether the census gets a profile or a
refusal at scale.**

⚠ **The Planner's recorded expectation stands untested and is not adjusted:** *`ecd_length` worst,
`mean_plddt_ecd` mildest, a minority out of range on the strict test.*

**Ingest into the database is a LATER, SEPARATE, GATED step** with its own transactional bar, on the
`GC` pattern. ⚠ **Not tonight.**

## §5 — Report, in the morning

⚠ **`LA2`'s projection and `LA3`'s determinism result BEFORE you start the long run** — they are
minutes and they decide whether the night is worth spending.
Then: the manifest · row counts by outcome summing to 2,690 · the `sha256` · ⚠ **`LB`'s comparison as
numbers** · branch and tip · the invariant with its keys · the gate without `.env`.
