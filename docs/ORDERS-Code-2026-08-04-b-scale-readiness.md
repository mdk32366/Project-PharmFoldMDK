# ORDERS — Code — 2026-08-04 (second) — close the gaps that are harmless only at N=82

> **KEEL-4 is on hold.** KEEL is at **v6**; the staged assumption-register document was written
> against v5 and must be reconciled before it lands. Owner ruling: **close of day.** Do not act on
> it, do not add rows to it, and treat the A-NNN references in today's artifacts as reserved. The
> two Planner assumptions surfaced this session (Trop-2 fixture, missing determinism control) are
> **held in `RESERVED.md`**, not written, until the register lands against v6.
>
> **Confirm every number against `RESERVED.md` and the live log before use.** The Planner is working
> from a 2026-08-04 zip plus two Code reports and has no repository access.

---

## §0 — The organizing idea, because it decides what is in scope

Every gap below has the same shape: **it is correct today only because the cohort is 82.** None is a
bug now; all become defects the moment the denominator moves. That shape is the whole reason for
this order.

| Gap | Why it is harmless today | What it becomes at census scale |
|---|---|---|
| `list_analyses` unfiltered | `protein_analyses` *is* the cohort | The target list silently **becomes** the census |
| `analysis_id` null on failure (F-010) | One row fails | Hundreds fail; the field is consumed by then |
| Three fold recipes (F-015) | Nobody compared across tiers | Commensurability is load-bearing for every census claim |
| Accessions curated by hand | 82 rows, eyeballed | 2,886 rows, and a 10-row file once carried two errors |
| One fold with no recipe record | 1 of 80 | A category, not an anomaly |

**Scope: harden, do not expand.** Nothing here loads a census row, folds a census target, changes a
route's output, or touches the scorer. **The census build remains gated on D-075.** This order makes
the system *able* to expand; it does not expand it.

---

## §1 — TASK A · Get the real membraneome table and prove it is the real one

`table_S3_surfaceome.xlsx` in Downloads **and** in project context is a **Git LFS pointer**: 132
bytes declaring `oid sha256:2f1b8262463ce1c59a1f945d22f0e9638cb3bfbf5aabe197f43b562a62fb055a`,
`size 6864772`. Verified by the Planner against the project-context copy.

1. Re-fetch from the **direct source**, `https://wlab.ethz.ch/surfaceome/table_S3_surfaceome.xlsx`
   (plain HTTP, not a git remote — the pointer came from a mirror), or via LFS smudge.
2. ✅ **Verify against the declared oid before anything reads it.** `sha256sum` must equal
   `2f1b8262…` and the size must be `6864772`. **We have the expected hash before the file — use
   it.** A mismatch is stop-and-report, not a retry.
3. Record source URL, hash, size, date in `data/census/PROVENANCE.md`.
4. **Read every count off the file.** Row count, count at each SURFY score cutoff, and the
   positive/negative split. **No count from this order, any conversation, or any paper abstract.**

---

## §2 — TASK B · Entry names → accessions, with the failure modes as first-class outputs

⚠ **`surfaceome_ids.txt` does not contain accessions.** Verified by the Planner: **2,886 lines,
2,886 unique, all UniProt *entry names*** (`1A01_HUMAN`, `1A02_HUMAN`, …). Every join in this project
is keyed by **accession**. Entry names are explicitly not stable identifiers; accessions are.

**The precedent that sets the bar:** a **ten-line** seed file once carried **two** wrong accessions
(2026-07-22). At 2,886 rows, an unverified mapping is not a risk, it is a certainty.

### Tests first

| Test | Assertion | Prove it bites by |
|---|---|---|
| `test_every_input_id_lands_in_exactly_one_bucket` | resolved ∪ obsolete ∪ multi ∪ unresolved partitions the input; **counts sum to the input count** | Dropping a bucket → red |
| `test_unresolved_is_a_bucket_not_a_silent_drop` | An unmappable id appears in output with its reason | Filtering it out → red |
| `test_one_to_many_is_not_silently_collapsed` | An entry name resolving to >1 accession lands in `multi`, **never** first-wins | Taking `[0]` → red |
| `test_mapping_is_cached_and_rerun_is_byte_identical` | Second run reads cache, identical output | Re-querying → red |
| `test_no_accession_is_synthesized` | No code path constructs an accession from a string pattern | Adding a regex derivation → red |

**⚠ An empty bucket must be asserted empty, not left blank.** `unresolved: 0` is a finding; a
missing `unresolved` key is an unanswered question wearing the same clothes.

### Then the code

Extend `scripts/map_genes_to_uniprot.py` (it exists and has the client). Batch against the UniProt
REST ID-mapping endpoint, cache to disk, rate-limit. Emit `data/census/accession_map.csv` with
`entry_name, accession, status, resolved_on` plus a summary naming all four bucket counts.

**Owner-reserved:** how `multi` rows are resolved is an identity judgement, not a mechanical one.
**Leave them in `multi` and report the list.** Do not pick.

---

## §3 — TASK C · Cohort scoping — the hard ordering constraint

**This ships before any census row can exist in the database.** Not the same PR as a load; earlier.

**How known (D-016):** `app/reads.py:110-114` — `list_analyses` is
`select(ProteinAnalysis).order_by(ProteinAnalysis.id)`, unfiltered and unpaginated.
`ui/src/components/TargetList.jsx` renders whatever it returns.

1. `protein_analyses` gains a **cohort tag** — additive, nullable, migration backfills every
   existing row to tranche zero. (Migration **0008**; **0007 is still unapplied to prod** and this
   order does not apply it.)
2. Every route that enumerates analyses filters to tranche zero. Test asserts it, **proven by
   revert** — remove the filter, insert a foreign-cohort row in the fixture, watch it appear.
3. **Pagination is named, not built.** At 82 rows it is not a defect; it becomes one at census
   scale. Record it in `RESERVED.md` as a known deferral so the next person meets it as a decision
   rather than a surprise.

---

## §4 — TASK D · Close F-010, because it stops being cosmetic

F-010 is logged deliberately unfixed and D-074 keeps it open until the instrument stops exhibiting
it. Today one row is affected. At census scale, **failures become a population**, and the field is
null exactly on the rows a reader most wants to click.

**Owner ruling needed — F-010 names two honest options and this order does not choose:**
(a) populate `analysis_id` for every target that *has* an analysis row, or
(b) rename to `folded_analysis_id` so the name states its own rule.

**Whichever is chosen, the test asserts the failed row's behaviour specifically** — a test over the
folded majority passes under both the bug and the fix. Use IGF2R.

---

## §5 — TASK E · Recipe integrity — the F-015 groundwork

Code's read of `fold_provenance`: 80 folded rows across `('int8',64)×42`, `('fp16',None)×34`,
`('fp16',64)×3`, **and one with no record.**

1. **A fold may not complete without its recipe recorded at fold time** (D-047's principle, made
   enforceable). The one-with-no-record becomes structurally impossible. Test proven by revert.
2. **The census declares one recipe up front**, recorded in its manifest, so a census fold is never
   silently produced under a different one. **Do not re-fold the 82 to unify recipes** — that would
   touch the reported cohort, which F-008 forbids.
3. **No claim in either direction about the 34 unchunked folds.** Code's posture is correct and is
   now the ruling: *"those 34 are fine"* is exactly as unsupported as the opposite.

---

## §6 — TASK F · The one cheap experiment: chunked vs unchunked (F-015's actual question)

⚠ **Task 1c measured chunk-size variation (64 vs 32 vs 16). The cohort's variable is chunked versus
not (None vs 64).** Adjacent questions; not the same one. The cohort's split has never been tested.

**Pre-register before running** (its own entry — confirm the number against `RESERVED.md`):

- **Design:** one short target that fits unchunked locally. Fold at `int8/None` and `int8/64`.
  Same dtype, same length, **chunking as the only variable.**
- **⚠ Determinism control first, and it is mandatory** — two folds at the *same* recipe, both arms,
  before any comparison is read. Without it, *"None differs from 64"* and *"folding is
  nondeterministic"* are the same observation. **This was missing from the Task 1c order; it is not
  missing again.**
- **Fixture:** name it from what exists in the repo. **Not Trop-2** — TACSTD2/P09758 has no sequence
  here, because F-009 records it as one of the four targets *excluded* from the 82. The Planner
  specified it anyway; the Task 1c fallback (GPU-test fixture source, 114 aa) is the precedent.
- **Frozen reading, both outcomes, before numbers:** byte-identical → chunking-vs-not does not
  change output *at this dtype and length*, and the cohort's `None`/`64` split is unproblematic **in
  that regime only**. Any difference → the cohort spans non-commensurable recipes and F-015 is
  load-bearing.
- **⚠ Neither outcome generalizes to fp16 or to cohort lengths.** Both are unmeasured and the entry
  says so in itself (D-074). **No carve-out from a partial agreement** — the same refusal Code
  correctly made when 64 and 32 matched perfectly.

---

## §7 — Out of scope, explicitly

- **No census rows in the database.** Task C makes it *safe*; it does not do it.
- **No census folds. No UI. No scorer, no features, no ranking.**
- **No D-075 run, no migration 0007.** Unchanged; both are owner-gated and neither belongs in a
  travel-day window.
- **No Task 3 Arm A** unless the owner is at the keyboard — twenty folds driven into an OOM boundary
  on the box whose precedent is a host bugcheck.
- **No KEEL-4 work.** Held to close of day, pending v6 reconciliation.

## §8 — Done when

Real xlsx verified against the known sha256 · all counts read off files · the 2,886 mapped with four
bucket counts all asserted, `multi` reported not resolved · cohort tag shipped and route filtering
proven by revert · F-010 closed under an owner ruling with the failed row named in the test · recipe
recorded at fold time or the fold fails · Task F pre-registered before it runs, determinism control
first · gate green · **nothing deployed, nothing loaded, nothing folded beyond Task F's fixture.**
