# SPEC — 2026-09-17 · PDB coverage census over the census, step 1, in tranches

> ⚠⚠ **Where this file and the log differ, THE LOG GOVERNS.**
> ⚠ Landing header added by Code at landing, 2026-09-17. **The body below is the document as
> delivered, byte-for-byte**; no AUTHORED-SHA256 range is declared over it.

**Owner:** Matt Kelly · **Planner:** Claude Opus 5 · **Builder:** Code
**Issued:** 2026-09-17, America/Los_Angeles. The `09-17` label is the real calendar date.
**Status:** ⚠ **PRE-REGISTRATION. It authorises nothing on its own** — it is the document an orders file
points at. **Owner accepted the recommendation 2026-09-17:** run this alongside `A-032` step 1 next
sitting, both being public-API reads that gate bigger work.

> ⚠⚠ **NO DATABASE. NO TUNNEL. NO GPU. NO FOLDING.** Every tranche below is a **public-API read** plus
> local file writes. ⚠ **Nothing here compares a structure to a structure** — that is step 2, and it is
> **not specified by this document.**

---

## 0. What this measures, and what it deliberately does not

**Measures:** for each of the **3,467** census accessions — does any PDB entry map to it, does that entry
**overlap the ECD span we folded**, and **by how many residues.**

⚠ **Does NOT measure:** whether our fold is right. **No lDDT, no TM-score, no superposition, no
downloaded coordinates.** This is a **coverage census**, and its whole purpose is to **size or kill step
2** before a line of comparison code is written.

⚠⚠ **Why the distinction is load-bearing:** the human-proteome anchor is **5,885 of 20,610** accessions
mapping to any PDB structure (≈29%), of which only **2,617** have full coverage (≈13%). The census is the
**surfaceome** — the hardest class to crystallise — and we folded **sliced ECD spans**, so a deposited
structure only helps if it overlaps that span. ⚠ **A cytoplasmic kinase-domain structure of a receptor is
a PDB hit that says nothing about the ECD we folded.**

**The Planner's unmeasured expectation, recorded so it can be wrong:** usable ECD overlap **well under
20%, possibly under 10%.** ⚠ **It is a guess. This census replaces it. It is NOT a pre-registered
expectation and nothing is judged against it.**

---

## 1. ⚠ Absence is a set of NAMED CATEGORIES, never a low number

Every accession lands in **exactly one** outcome. ⚠ **The categories sum to 3,467 and the sum is stated**
— a breakdown that does not reconcile with the population is how a silent extra category hides
(`decisions.md:2860`).

| outcome | meaning |
|---|---|
| `pdb_ecd_overlap` | an entry maps, overlaps the folded ECD span, and meets the minimum overlap |
| `overlap_below_minimum` | maps and overlaps, but **shorter** than §3's minimum |
| `entry_but_no_ecd_overlap` | entry exists, maps to the accession, **no residue intersection** with the folded span |
| `engineered_construct_only` | every overlapping entry is disqualified by §3's construct policy |
| `no_pdb_entry` | SIFTS maps **no** PDB entry to this accession |
| `accession_unresolved` | ⚠ the accession itself did not resolve — **an instrument condition, not a biology result** |
| `span_unknown` | ⚠ we hold **no folded ECD span** for this representative — **a project-state condition, not a PDB fact** |

⚠⚠ **`accession_unresolved` and `span_unknown` are never folded into `no_pdb_entry`.** They are ours, not
the PDB's, and conflating them would report our gap as nature's.

---

## 2. Tranches. Run in order. Each is a stopping point.

⚠ **Each tranche writes its own artifact with its own sha256, is independently resumable, and reports
before the next begins.** ⚠ **A partial pull is reported AS PARTIAL, with how far it got** — a truncated
pull presented as complete is this project's shared defect class.

| # | population | n | why here |
|---|---|---|---|
| **T0** | **none — instrument only** | 0 | Tests first, offline fixtures, **no network.** §5. |
| **T1** | **the cohort 82** | 82 | ⚠⚠ **Instrument calibration, not a result.** These are known targets — HER2, NECTIN4, TROP2, CEACAM5 — with structures we can verify by eye. **§4's stop condition lives here.** |
| **T2** | **the v2 sampled 300** | 300 | Aligns with the November spine. ⚠ Whatever step 2 becomes, **Stage 1's answer key is decided by this tranche** regardless of whether the census-wide benchmark ever runs. |
| **T3** | remainder, **by census tranche** (1×1,307 · 2×535 · 3×517 · 4×332 · 5×776) | balance of 3,467 | Batched on the manifest's own tranching, so a stop loses **one batch**, not the run. ⚠ **Tranche 5 is the rental/tiled population** — report it separately; its spans are the least PDB-tractable. |
| **T4** | **no reads — the report and the gate** | — | §6. |

⚠ **T2 and T3 must not start until T1 has passed §4.** ⚠ **No tranche is re-run to improve a number.**

---

## 3. ⚠⚠ Pre-registered policy — FIXED BEFORE T1, never adjusted after seeing a distribution

1. **Source of truth for mapping: SIFTS residue-level UniProt↔PDB mappings.** ⚠ Not a name search, not a
   BLAST, not an entry-title match.
2. **Minimum overlap: 50 residues** intersecting the folded ECD span. Below it → `overlap_below_minimum`.
3. **Minimum sequence identity over the overlap: 95%**, so isoform and ortholog mismatches are excluded.
4. **Construct policy.** An overlapping entry is **disqualified** if the overlap region is majority
   engineered mutation, or if the overlap is a fusion/chimera partner rather than the target itself. ⚠
   SIFTS flags these; **the policy is ours and it is written here, before the data.**
5. **Resolution and method are RECORDED, not filtered, at step 1.** ⚠ Filtering belongs to step 2. Step 1
   records method and resolution so step 2's cutoff can be chosen **on the measured distribution** —
   which is the one thing step 1 legitimately hands forward.
6. **Multiple entries per accession: all are counted; the best single overlap is named.** "Best" =
   longest qualifying overlap; tie → higher resolution; tie → lower PDB ID, deterministically.
7. **The folded ECD span is read from OUR record**, and which record is stated. ⚠ If no span is held →
   `span_unknown`, never a computed guess.
8. ⚠ **`PYTHONHASHSEED` pinned in every manifest**, and each tranche's artifact records the **SIFTS /
   PDBe release** it read. **A coverage number without a release date is not reproducible** — the PDB
   grew from 150,000 entries in 2019 to nearly 250,000 by 2026, so this number has a shelf life and says
   so.

---

## 4. ⚠⚠ T1's stop condition — the instrument must prove it can see

**T1 is not a result. It is the check that the pipeline works at all.**

**Stop and report, before T2, if any of:**

1. **HER2 (`P04626`) returns `no_pdb_entry`.** ⚠ **That is an instrument failure, not a finding.** HER2 is
   among the best-characterised ECDs in the archive.
2. **Two paths disagree** on whether an accession has any entry — the SIFTS mapping and a direct
   PDBe entry listing for the same accession must agree on **presence/absence**. ⚠ **Two paths to one
   quantity is this project's most-repeated defect class**, and this is where it gets checked cheaply.
3. **The seven outcomes do not sum to 82.**
4. **More than 5 of the 82 land in `accession_unresolved` or `span_unknown`** — that points at our record,
   not at the PDB, and it is investigated before the remaining 3,385 are pulled.

⚠ **A low but coherent hit rate in T1 is NOT a stop.** That is the measurement, and it may be the answer.

---

## 5. T0 — the instrument, tests first

**Tests RED at the assertion, then the script.** Pinned, at minimum:

1. **Every count is its own `count(*)` / explicit tally.** ⚠ A test **fails** if any count derives from a
   list length — the defect the R1–R4 instrument caught **inside its own draft** (`len(R4_ACCESSIONS)`).
2. **All seven outcomes initialise to `0` and none can vanish when empty.** ⚠⚠ **`D-027` at the reporting
   surface** — a key that disappears at zero reads as *"not measured"* rather than *"measured none."* An
   outcome the code produces that is not in the list is **ADDED, never folded** into another.
3. **The categories sum to the population, and the sum is asserted.**
4. **Every capped list says it is capped**, carrying a count it did not derive from its own length.
5. **Printed output is ASCII, asserted on the PRINTED BYTES.** ⚠ *A source-only ASCII check is not an
   output ASCII check* — today's lesson, and it was found only in CI.
6. **Write-once artifacts with their own sha256**; a second run over an existing artifact **raises**.
7. **Resumability:** a killed tranche restarts **without re-reading what it already holds**, and the
   resume path is tested.
8. **Offline fixtures only.** ⚠ **No test touches the network.** Fixtures include: an accession with many
   entries, one with an ECD-adjacent but non-overlapping entry, one chimera, one below the 50-residue
   minimum, one unresolved accession, and one with no held span.
9. **A-017 discrimination:** every assertion is shown **capable of failing**, on a fixture built to make
   it fail. ⚠ An assertion that passes on both an empty and a populated fixture **has measured nothing.**
10. **Rate limiting and caching are polite and configurable**; a 429 or timeout is a **recorded outcome**,
    not a silent retry loop. ⚠ **A cache hit is labelled as a cache hit in the artifact.**

**CI green — `test` and `postgres` both — before T1 reads anything.** ⚠ **Nothing here deploys.**

---

## 6. T4 — the report, and the gate it decides

**Reports:** the seven outcomes with their sum, for **each tranche separately and combined**; overlap
length distribution for `pdb_ecd_overlap`; method and resolution distributions; ⚠ **tranche 5 broken out
separately**; and the SIFTS/PDBe release read.

**Then the gate, which is the OWNER's decision and not the Builder's:**

| if `pdb_ecd_overlap` is | Planner recommendation |
|---|---|
| large enough to support a census-wide claim | **step 2 census-wide** — a scope change to v2, needing its own D-entry |
| moderate | **step 2 on the qualifying subset only**, with §7's bias stated in the paper |
| small | ⚠ **step 2 stays on the v2 cohort-82-plus-300 spine.** The census-wide census is then a **finding in its own right** — nobody has measured PDB coverage of this surfaceome census — and it is publishable as such. **Killing step 2 is a successful outcome of step 1, not a failure.** |

⚠ **The threshold numbers are NOT set here on purpose**, and that is a deliberate departure from
pre-registering everything: the honest cut depends on the overlap-length distribution, which does not
exist yet. ⚠⚠ **What IS pre-registered: the owner sets the threshold on the DISTRIBUTION SHAPE, before
any comparison is run, and the threshold is written down before step 2 begins.**

---

## 7. ⚠⚠ The bias, pre-registered so a reviewer cannot introduce it

**Proteins with PDB structures are not a random sample of the census.** They are the ones that were
**tractable to crystallise and commercially interesting** — which for a surfaceome census means enriched
for exactly the well-studied ADC targets and depleted of everything else.

⚠ **Therefore: calibration measured on the PDB-covered subset does NOT transfer to the census as a
whole.** The paper states this **as a limit of the design**, not as a caveat discovered afterwards.

**And a second limit, stated plainly:** deposited structures are **themselves models fit to experimental
data** — resolution limits, unmodelled loops, crystal-contact artifacts, engineered constructs. ⚠ They
are a **far better judge than pLDDT grading its own homework**, and they are **not ground truth.** Step
2's wording must not promote them to it.

---

## 8. Integers and scope

⚠⚠ **This spec spends NO integer.** It names what will be needed; **Code confirms next-free from
`RESERVED.md` at write time and reserves in the same commit that spends.** ⚠ **A pointer moved past an
unwritten integer is the `D-062` shape** — today's `F-081` was written precisely to avoid it.

| needed | for |
|---|---|
| an **F-** entry | T4's coverage finding |
| a **D-** entry | ⚠ **only if** the gate chooses a census-wide step 2 — that is a **scope change to v2**, whose answer key is currently the cohort 82 plus 300 sampled |

⚠ **`D-169` and `D-170` are already owed to `SPEC-A-032` §2.6 and §3.7 and are not this.** Any decision
from this spec takes the **next free** integer at the time it is written, not a number reserved here.

**Out of scope, explicitly:** step 2 in any form · downloading coordinates · any superposition or
distance metric · re-folding · anything touching `core/scorer.py` · any change to v1's sealed results ·
⚠ **and this work does not displace the November spine — the AF2 comparison is what makes the class
deadline.**
