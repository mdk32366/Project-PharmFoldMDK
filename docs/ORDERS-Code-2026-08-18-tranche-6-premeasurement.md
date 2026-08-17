# ORDERS — Code — 2026-08-18 — the measurements that PRECEDE the tranche 6 design document

> **This is not the design document.** `D-091` ruling 3 requires a design document before anything
> folds. This order produces the four measurements the document cannot be written honestly without,
> and it produces them **before** the document commits to anything — because requirement 1 says
> *picking a boundary source after seeing results is how a boundary gets chosen for the answer it
> gives*, and the same hazard applies to picking a **population** and a **verdict** after seeing
> results.
>
> **No GPU. No rental. No production write. No `pytest` with `.env` sourced.**
> Every task is disk-local or one read-only `SELECT`, except A2 which is a network pull.
>
> **Tests first on every task**, each proven by revert (A-017), each with a fixture that
> **discriminates** — a fixture that passes under the defect is not a fixture.

---

## §0 — The pre-registration, written before any count is read

⚠⚠ **These commitments are made NOW, with no counts in hand. Read them before running anything.**

**P1 — The choice criterion for the boundary source is fixed here.** A source qualifies only if it
(i) publishes **versioned, dated releases** that an artifact can stamp, (ii) assigns **residue-level
coordinates**, not family membership, and (iii) is obtainable for **all 141 rows**, not just the 10.
Among qualifying sources the fold runs under the one with the **highest residue coverage of the V2
span**. ⚠ If more than one qualifies and coverage does not separate them, **the tie goes to the
owner as a recorded ruling — never to a margin, a threshold, or a dial.**

**P2 — All three sources are reported regardless of which one folds.** The artifact carries
`boundary_source` and `boundary_source_version`. A source that lost is a measurement, not a
deletion.

**P3 — ⚠ Every candidate source is itself a model output, and the design document must say so.**
Pfam and InterPro boundaries are HMM matches. UniProt `Domain` on proteins of this size is largely
propagated from PROSITE/ProRule profiles. **There is no curated ground truth here to pick.**
`A-014` holds — a model's positive class is a prediction, not a fact — and it holds three times
over. Choosing a boundary source is **choosing a model to feed a model**, and the assembled
artifact inherits both.

**P4 — No verdict on requirement 3 is written before Task B reports.** If PAE is absent, the
honest design document says *"the measurement that would settle this is unavailable and here is
what it would cost to obtain"* — it does not substitute an argument.

---

## §1 — Task A — the boundary-source agreement count

**Question:** is the boundary source a live question, or do the sources agree?

### A1 — UniProt, cache-only, zero network

`scripts/tranche6_domain_census.py --source uniprot`

Reads `data/census/spancache/{acc}.json` for the **141** rows of `census_manifest.v7.csv` with
`tranche=5` and `span_aa > 1026`. ⚠ **The 141, not the 10** — see §4.

Per accession emit: `n_domain`, `n_repeat`, `residues_in_domains`, `residues_in_span_not_in_any_domain`,
`n_domains_wholly_inside_the_V2_span`, `n_domains_straddling_the_span_boundary`.

⚠⚠ **`n_domain` over the chain and `n_domain` inside the V2 span are DIFFERENT NUMBERS, and the
naive count is the chain.** A cytoplasmic-tail domain is a domain; it is not a domain we would
fold. **Both are emitted; neither is allowed to stand alone.** This is `F-037` one level down again
and it must not be rediscovered after a fold.

⚠ **Verify before A2 spends a request:** print the `uniProtKBCrossReferences` block for one real
cached entry and confirm whether Pfam/InterPro entries carry location coordinates. The Planner's
read is that they carry `EntryName` and `MatchStatus` and **no coordinates** — *general knowledge,
not sourced at first hand (D-016)*. **If they do carry coordinates, A2 is unnecessary and this
order is wrong; say so and stop.**

### A2 — InterPro / Pfam, network, only if A1's check says it is needed

Endpoint as a **committed constant**, not a literal in a call. It inherits `census_spans_v2`'s
rules verbatim, because they were ruled for exactly this failure mode:

- every record carries its own `fetched_on` and the source release read **at that moment**
- header records first and last fetch date and the release at each; ⚠ **if they differ, both are
  reported and neither is collapsed**
- a disk cache, so a halted pull resumes
- ⚠ **a permission denial or a rate-limit refusal is STOP-AND-REPORT** — never a retry, never a
  workaround, never a per-accession re-query. Per-accession retry is where shopping hides once the
  endpoint and the accession set are fixed.

### A3 — the agreement table

Pairwise, per accession: how many boundaries in source X have a counterpart in source Y within
±*k* residues.

⚠⚠ **Report `k` at 0, 5, 10, 25 and 50. Do not choose one.** A single tolerance is a dial wearing
the costume of a measurement — the `GUARD_CHAIN_SHORTER_THAN_LONGEST` reasoning, applied before the
defect rather than after it.

**Tests first (A1/A2/A3).** Synthetic UniProt JSON fixtures:
1. three `Domain` features, one carrying an **UNKNOWN coordinate modifier** → becomes a named
   category, never a silent drop. ⚠ Prove by revert: remove the branch, watch a real domain vanish
   from the count with nothing red.
2. a protein whose domains lie **entirely outside** the V2 span → `n_domains_wholly_inside == 0`
   while `n_domain > 0`. ⚠ **This is the discriminating fixture.** A test that only uses proteins
   whose domains sit inside the span passes under the chain-count defect.
3. a domain **straddling** `span_start` → counted as straddling, in neither of the other two
   buckets, and the buckets sum to `n_domain`.

---

## §2 — Task B — the PAE inventory

**Question:** does the census carry PAE, the learned inter-residue confidence about **relative
position**, which is the only thing in the system that speaks to *"a structure or a set of
structures?"*

Three places to look, and **the answer is a category per row, never a boolean**:

| category | meaning |
|---|---|
| `pae_registered` | `protein_analyses.pae_json_path IS NOT NULL` **and** the file resolves |
| `pae_on_disk_unregistered` | ⚠ a `pae.json` exists under the worker artifact dir, DB column is NULL |
| `pae_absent_local_tier` | ⚠ emitted by the model, persisted by neither path |
| `pae_never_emitted` | the fold produced no `predicted_aligned_error` |

**Do:**
1. Report whether `WORKER_ARTIFACT_DIR` is **set** on the local worker. ⚠ **Report set/unset. Do
   not print `.env`.** The DB credential in it is still unrotated.
2. List `{WORKER_ARTIFACT_DIR}/{job_id}/pae.json` for census job ids, if the var is set.
3. One read-only `SELECT` over `protein_analyses` for census rows: count by
   `pae_json_path IS NULL`. ⚠ Through the `fly mpg proxy` on 16380, from a script **file** — a
   shell one-liner eats backticks, and it corrupted three log fragments on 2026-08-17.

⚠ **Read `worker/main.py:_persist_pae_local` before running this and quote the condition in the
report.** The Planner's read is `if artifact_dir:` with a docstring scoping it to the rental box.
**If that read is wrong the whole of §3 is moot and the finding must not be written.**

**Tests first.** A fixture where the file exists on disk and the DB column is NULL must classify
`pae_on_disk_unregistered` — ⚠ **not present, and not absent.** Prove by revert: collapse the four
categories to a boolean and watch that row silently join whichever neighbour it is nearest.

**⚠ If Task B reports `pae_absent_local_tier` across the census, that is `F-041`** and I will write
it: *the model produces, on every forward pass, the one quantity that distinguishes a rigid
multi-domain structure from a set of independently-confident domains — and the pipeline discards it
for 2,690 folds.* **Do not write the entry. Report the numbers; the finding is the Planner's.**

---

## §3 — Task C — the in-context multi-domain population

**Question:** requirement 3 can be answered by measurement on proteins we have **already folded**,
at zero rental cost — but only if such proteins exist and only if Task B finds PAE.

From manifest v7 ⋈ `spancache`: of the **2,690 folded rows in tranches 1–4**, how many carry **≥2
UniProt `Domain` features wholly inside the V2 span**? Bucket by domain count and by span length.

⚠ **This is the population that makes the design document empirical instead of argumentative.** A
protein that folds in one pass *and* has internal domain boundaries is the control: fold it whole,
fold its domains separately, compare. **Assembly can be validated where assembly is not needed** —
which is the only place validating it is possible.

**Do not run the comparison.** This task counts the population. Whether the comparison runs is a
`D-095` decision and it is gated on Task B.

---

## §4 — Task D — re-derive the scoping counts independently

⚠ **Do not take the Planner's numbers.** Two paths to one quantity, compared — which is the remedy
for this project's most-repeated defect class, not an instance of it.

Re-derive from `census_manifest.v7.csv`, and **report any disagreement as a defect, not as a
rounding difference:**

| quantity | Planner's measurement, 2026-08-18 |
|---|---|
| tranche 5 total | 776 |
| 441–850 / 851–1,026 / 1,027+ | 566 / 69 / 141 |
| of the 141: named in D-091 r3 | 10 |
| of the 141: the three mucins | 3 |
| ⚠ of the 141: **named nowhere** | **128** |
| of the 141: 1,027–2,000 aa | 102 |
| distinct `boundary_method` values across all 3,467 rows | 1 (`sliced_ecd`) |

**Tests first:** the band-split function must red if a boundary is moved by one residue — the
441/851/1,027 edges are load-bearing and a `<` for a `<=` is invisible in a total.

---

## §5 — What is deliberately NOT in this order

- **No `boundary_method` value is added.** ⚠ Extending `RECOGNISED_BOUNDARY_METHODS` is `D-095`,
  and doing it here would put an assembled method one keystroke from a fold before the document
  that governs it exists. **`D-091` ruling 3 is the gate and this order does not open it.**
- **No fold, no rental, no ingest, no migration, no schema change.**
- **No `P55073` implementation** — ruled, still open, not today.
- **No InterPro pull if A1's cross-reference check makes it unnecessary.**

---

## §6 — Deliverable

A report, in chat, per task: the numbers, the artifact each came from, and — for every count — the
**key it is counted over**. ⚠ Every absence is a category with a cause. If a task cannot run, that
is a result with a reason, and it is reported as one rather than skipped.
