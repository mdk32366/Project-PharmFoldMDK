# DRAFT — `P-001` methods section, 2026-09-15

> ⚠⚠ **DRAFT. Nothing here is a ruling, and two items below are explicitly PENDING the owner.**
> Written during slice 3's unattended fold. It assembles material the claim register
> (`docs/PAPERS-v2.md`) has been holding *for* a methods section that did not exist, and adds the
> four disclosures whose rulings landed between 2026-09-11 and 2026-09-15.
>
> **What this draft is for:** to be argued with. Every number in it is either cited to an entry or
> marked as unverified, and the sections that require an owner ruling say so rather than choosing.

---

## 0. Ordering, and why the result comes first

The register's *Open before submission* list opens with **the Run B triples and their
interpretation**, not with the disclosures. That ordering is kept here: the disclosures are the
spine of the section's second half, but a methods section that leads with its caveats invites the
reader to discount the result before reading it.

---

## 1. Pre-registration, and what was frozen before what

⚠⚠ **The interpretation table was frozen before the numbers existed** (`D-075` Decision 4). This is
the load-bearing claim of the whole design and it is stated first, because every arm below is read
through a table nobody could have tuned to the outcome.

⚠ **And the countervailing fact travels with it, by ruling:** *the proxies were frozen knowing
Run A survived.* That sentence is on the snapshot's face and belongs here, not in a footnote.

⚠⚠ **What it does and does not reach, stated precisely, because the loose version concedes more
than is true.** The **arms were pre-specified** and the **interpretation table was frozen before the
numbers existed**, so **Run B's outcome is uncontaminated** — no reading was chosen after seeing a
result. What was chosen under partial knowledge is **the proxy set**: which three attention proxies
to build, selected by people who already knew Run A had survived.

**So the admission is narrower than "the pre-registration came after a positive result", and truer:
the design is clean and the choice of instrument is not blind.** ⚠ It is also why `pdb_present`
moving toward the anchor on all three statistics is the weaker of the three arms *as evidence*,
despite being the strongest numerically — a solved-structure proxy is the one a team that had seen
Run A would most naturally reach for.

`data/attention_proxies.json`, frozen 2026-09-12.

## 2. Population

- **82 cohort targets.** **56 of 82** joined to the served ranking; **26 skipped for carrying no
  structural score — skipped, never fabricated.**
- ⚠ **All 12 Group B positives are present**, so no arm's count is taken over a reduced positive
  set. This is what makes the three counts comparable to each other at all.
- **Null counts: 0 of 82 on all three arms.** No result rests on an absent measurement, and no
  low-attention stratum conceals a fetch failure.

## 3. Run B — popularity-matched comparison, three arms

Each cell is the **median / mean / count ≥ 0.5** of the positives' within-stratum percentiles.
⚠⚠ **The triple is the unit.** `D-075` forbids a single-statistic reading in terms, and §3.2 below
is the reason that rule exists.

| arm | median | mean | ≥ 0.5 | against the anchor |
|---|---|---|---|---|
| `geom_proxy` unmatched (anchor) | 0.6607 | 0.6324 | 8-of-12 | — |
| `no_plddt` baseline (`F-005`) | 0.5625 | 0.5893 | 6-of-12 | — |
| **`pdb_present`** | 0.6564 | 0.6615 | **10-of-12** | toward the anchor on all three |
| **`pub_count_tagged`** | 0.5893 | 0.6310 | 9-of-12 | mean and count toward the anchor |
| **`pub_count_atm`** | 0.5357 | 0.5923 | 7-of-12 | ⚠ **mixed — §3.2** |

**Headline.** The structural enrichment **survives popularity-matching on all three frozen
attention proxies** — `F-072`, ruled Branch A by the owner, 2026-09-12.

### 3.1 ⚠ The `pub_count_atm` arm is MIXED against the baseline — and each margin is stated in the instrument's own units

⚠⚠ **A margin is only a difference if it exceeds the resolution that produced it.** `D-075` fixes
those units: **per-target percentiles quantise in 1/112 = 0.00893**, and **the 12-value median in
1/224 = 0.00446.** Every comparison below is given in them.

| statistic | `pub_count_atm` | `no_plddt` baseline | margin | in instrument units |
|---|---|---|---|---|
| median | 0.5357 | 0.5625 | −0.0268 | ⚠ **−6.0 × 1/224** — resolvable, and below |
| mean | 0.5923 | 0.5893 | +0.0030 | ⚠ **+0.34 of ONE target's percentile step** |
| count ≥ 0.5 | 7-of-12 | 6-of-12 | +1 | **one rank step** — the fragility property itself |

⚠⚠ **So the earlier phrasing — *one is below, two are above* — is itself an over-reading.** It
presents three commensurable comparisons and invites a reader to score the arm 2–1 toward *above*.
**Only one of the three margins is resolvable at all.** The mean's margin is **a third of the
smallest change a single target's rank can produce**; it is not an increase, it is a tie the
instrument cannot split.

> **The honest statement: the median is below by six of the median's own increments; the mean is
> indistinguishable from the baseline at this resolution; the count is above by one rank step.**

**Mixed still holds — and it now means one resolvable difference and two margins at or under the
resolution limit.** ⚠ That is a far better argument for why a split is the *expected* case at
n = 12 (§5.1) than the count of arms pointing each way, which was never the right question.

⚠ **For scale:** the same arm's median sits **−28.0 × 1/224** from the *anchor*. The distance that
matters is not the one to the baseline.

### 3.2 ⚠⚠ The PubMed arm disagreement — a limit on the reading, not a footnote

The two PubMed arms disagree by 2-of-12. **It cannot be read as *"even the stricter arm survives."***

The mechanism that would have told us *which* arm is conservative — a fame-correlated undercount in
the tagged arm — was **tested across all 82 targets before the freeze and found flat**:

- Spearman **rho = +0.026**
- quartile means **1.40 / 1.31 / 1.56 / 1.31**
- the two largest undercounts on **`PODXL`** and **`TNFRSF10C`**, ⚠ **both with zero solved
  structures**

The owner replaced it with **symbol ambiguity**, which is measured — ⚠ **and ambiguity carries no
direction.** So: **the disagreement is real and its sign carries no warrant.** That is a limit on
what the comparison can support, and it is stated in the methods section.

---

## 4. Disclosures

Four, each with a ruling behind it. ⚠ None is a paper-blocker; all four are things a reviewer would
be right to ask about and wrong to have to discover.

### 4.1 `tile_cut_kind = whole_run` on all 1,532 tiles

Cut legibility is a **`D-094` mount precondition**, and **nothing records a cut kind**. Carried
here, or the precondition is unmet on the live surface. (`D-095` amendment 3, ruled in 2026-09-12:
8 of 10 `no_domains` rows carry InterPro features inside the folded span; the vocabulary was never
emitted.)

### 4.2 ⚠ The cost stamp is computed at 440 aa; the campaign operated at 384

`D-164` / `F-074`. Two ceilings, **both correct and differently derived**:

- `LOCAL_CEILING.local_bound = 440` — the measured fold-clean bound for the card `F-062` was
  written about.
- `CAMPAIGN_CAP_AA = 384` — this host's operating cap, because `F-063` reached `highest_ok = 384`
  and the host bugchecked before 392 (`F-064`: post-fold headroom collapse). **Both findings OPEN.**

**The disclosure, affirmatively: 119 tranche-4 rows are served marked `local` and were never folded
by this campaign**, and **every use of the word `local` names which sense it carries.** The served
cost stamp now states its ceiling; this paper states the same.

⚠ **The band, with its key:** `384 < span ≤ 440` **by definition** — 119 rows. The **observed**
spans run **385–439**, and **zero rows sit at exactly 440**. Both figures are true and they are
different keys; writing the observed range as though it were the definition would silently exclude
a row at the bound if one ever existed. **Zero rows sit above 440 either**, so these 119 are exactly
`D-157`'s named remainder.

⚠ Stated negatively, which follows rather than leads: any claim that the campaign covers the
**local-foldable** census is false by those 119 rows. The claim that holds is that it covers the
census **within its own operating cap**.

### 4.3 ⚠ Run 2's status at submission — and the 2026-09-13 boundary

`F-042` requires that the PAE-recovery status **be stated rather than assumed complete**. As of
this draft:

⚠⚠ **EVERY COUNT STATES ITS KEY.** Four different census-sized numbers appear in this project and
they are four different populations; a reader meeting two of them without keys will assume one is
wrong.

| key | count |
|---|---|
| `census_manifest.v7.csv` rows | **3,467** |
| tranche 1–4 rows carrying a span | **2,691** |
| Run 1 **jobs**, any status | **3,656** |
| Run 1 jobs with `status = complete` | **3,651** |

| population | artifacts present | key |
|---|---|---|
| Run 1 census | **3,651 of 3,651** — verified by full sweep | jobs with `status = complete` |
| Task 3 twenty | 20 / 20 | enqueued job ids |
| slice 1 (251–384) | 342 / 342 | enqueued job ids |
| slice 2 (1–30) | ⚠ **480 of 517**; 37 lost | enqueued job ids |
| slice 3 (31–100) | folding at time of writing | enqueued job ids |

⚠ The 5 Run 1 jobs that are not `complete` (2 `failed`, 3 `pending`) hold no artifact, which is the
expected state and not loss; the two failures are `P11717` (`F-066`) and `P55073` (`F-033`).

⚠⚠ **`F-078`:** 37 slice 2 folds were lost from **both** the database and the artifact volume at a
single instant — contiguous, nothing lost before it, nothing kept after it. They are owed a re-fold.

⚠ **The boundary is stated from the database, which is the leg that stays verifiable:** job `4868`
completed `2026-09-13T15:24:36.578Z` and **survived**; job `4869` was claimed **64 ms** later and
did **not**. The hourly backup labelled `15:24:33Z` corroborates it and is **not** what the claim
rests on — `fly mpg backup list` no longer reaches that date (`F-078` amendment 1).

✅ **The loss does not reach this paper.** It is confined to Run 2, which `D-161` records as
instrument measurement that does not grow the population, does not enter `F-004`, and does not bear
on `F-072`. **The census is intact and that is measured, not assumed.**

### 4.4 `F-068`'s consequence

The structural scoring runs **predate the `D-105` topology reaching the writing path**. Stated
plainly: the scores in this result were computed before a topology correction that is now on the
writing path, and were not recomputed under it.

---

## 5. Statistical power

⚠⚠ **There are two n's in this paper and they answer different questions. Conflating them is the
first mistake available to a reader**, so they are separated before anything else is said.

| | n | what it measures | status |
|---|---|---|---|
| **Run B** | **12** | Group B positives, within-stratum percentiles | `F-072`, Branch A ruled |
| **Commensurability arm** | **4** | ADC-approved targets with expression data | ⚠ **underpowered; neither branch established** |

### 5.1 n = 12 — what the design can and cannot resolve

`D-075` Decision 0 fixed the power properties **before the numbers existed**, and they are
quantitative rather than hedging:

1. **A median is not a stable anchor at n = 12.**
2. **One target's rank moves the count.** ⚠ The observed `pub_count_atm` count, 7-of-12, is
   **one rank step** from 8-of-12.
3. **Ten of the finest available increments span the FULL → `no_plddt` median gap** —
   0.607 − 0.5625 = 0.0445 = **10.0 × 1/224**, measured exactly. The resolution of the instrument
   is a large fraction of the effect being measured.
   ⚠⚠ **That "ten" belongs to that gap and to no other.** `pub_count_atm`'s median gap from the
   same baseline is **6.0 × 1/224** (§3.1). Carrying "ten increments" into a sentence about a
   different arm would transplant a property measured on one gap onto another — the
   two-paths-to-one-quantity class, in prose rather than code.

⚠⚠ **The consequence is the part that must not be lost: at n = 12 a SPLIT between the three
statistics is the EXPECTED case, not a failure of the result.** Decision 0 says so in advance, which
is why §3.1's mixed `pub_count_atm` arm is reported as a split rather than resolved to one number.
A design that could only report a clean direction would be a design that had to manufacture one.

⚠ **And "at baseline" is not "at chance."** The `no_plddt` baseline is itself **above 0.5 on both
median and mean** (0.5625 / 0.5893). An arm sitting at the baseline has not shown the absence of
signal; it has shown the absence of signal *beyond what the baseline already carries*.

### 5.2 ⚠⚠ Spearman is a dead discriminator here, and is reported as evidence of nothing

Against the two-valued comparator, the full model and `no_plddt` agree to **full float precision**
(−0.04828045495852675) while their **per-target percentiles differ by up to 0.25**. With a
two-valued comparator Spearman depends only on the rank-sum of the score-5 group and is quantised in
**~0.024 steps** (`F-005` Finding 5 predicted exactly this).

> ⚠ **If a further arm returns the same Spearman value, that is not corroboration — it is the
> statistic being blind.**

It is reported for completeness and **carries no weight in any reading.** A methods section that
quoted it as agreement would be quoting an artefact of the comparator's cardinality.

⚠ **Why report a statistic that decides nothing?** Because a reviewer will compute it. Finding it
present and already characterised is a different experience from finding it absent — an omitted
Spearman looks like a statistic that was run and disliked. **It is here so that it cannot be
discovered.**

### 5.3 n = 4 — the commensurability arm returned a third outcome

**4 of 82.** ⚠ If a median is not a stable anchor at twelve, **at four nothing is.**

| target | rank | detection | `High` | `qh ≥ 150` |
|---|---|---|---|---|
| `ERBB2` breast | 7 / 56 | 7/11 | 4 | ✅ 154.55 |
| `NECTIN4` urothelial | 8 / 56 | 11/12 | 3 | ✅ 200.00 |
| `EGFR` glioma | 3 / 56 | 11/12 | 6 | ✅ 216.67 |
| ⚠ `FGFR3` urothelial | **34 / 56** | 6/11 | 2 | ⚠ below cutoff |

Three sit high, one sits low. ⚠⚠ **The bars disagree on one row of four — and one row is 25% of the
sample. That is not a direction.**

⚠ **A reading trap, named because it is easy to fall into:** the `D-053` grid's own cutoff *is*
`qh ≥ 150`, so `FGFR3`'s absence from it means **below cutoff, not no data.** The third column is
evidence of a value, not of a gap.

**The pre-registration offered two outcomes — DIRECTIONAL or SCATTERED — and the answer was a
third: UNDERPOWERED.** Amendment 1 permitted that explicitly. The limitation therefore stands as
**dilution, unquantified — not as bias with a sign.**

### 5.4 ⚠⚠ Two epistemic points that generalise past this measurement

These belong in the methods discussion rather than the limitations list, because they are about what
the design can establish rather than about what went wrong.

> **A pre-registration that MATCHES cannot distinguish *correctly anticipated* from *the data was
> never going to say otherwise*.**

The prediction here — *scattered, and more honestly underpowered* — was recorded before the run and
matched. ⚠ **At n = 4 no other answer was available, so the prediction cost nothing and proved
nothing.**

> **Agreement is weaker evidence than disagreement.**

⚠ **A pre-registration's value is in the outcomes it could have been wrong about**, and on this
design the predictions that *failed* elsewhere in the project carried more information than this
one that held.

⚠⚠ **Stated in general form deliberately.** The register asserts *"the Planner's two MISSES on the
census distribution were worth more than this hit"* (`PAPERS-v2.md`, and the standalone amendment)
— **and neither place names the two, nor does anything else in the repository.** Under `D-016` a
claim that cannot name how it is known does not belong in a paper as a count. The general form is
supportable; *two* is not, until they are identified.

### 5.5 What the power analysis leaves standing

- ✅ **Run B's Branch A ruling is not weakened by n = 12** — the design anticipated the split and
  read it under a table frozen beforehand. What n = 12 forbids is a **single-statistic headline**,
  and none is claimed.
- ⚠ **The commensurability question is not answered**, and §7 records it as the owner's ruling
  rather than resolving it here.
- ⚠ **No claim in this paper rests on the n = 4 arm.**

---

## 6. Limitations

- **`F-069` / `F-070` / `F-071`** — span-pipeline limitations, viewer silence, the category E labels
  gap. ⚠ Repair is unblocked by the freeze, but **`D-075`'s anchor rests on a frozen set that a
  span change would move**, so repair before submission trades one disclosure for a larger one.
- ✅ **n = 12 power — written, §5.** (This bullet previously read *"to be written"* and was stale
  the moment §5 landed.)
- ⚠ **`F-048`** — 58 census proteins whose V2 span is a short extracellular loop inside a larger
  transmembrane domain, the shortest a five-residue span. OPEN.

---

## 7. ⚠⚠ PENDING — not drafted here, because they are rulings and not prose

1. **`P-001`'s commensurability ruling** — `P-001 amendment 2` returned the **third** pre-registered
   outcome, `underpowered` at n = 4, and neither branch is established. **Still the owner's.**
2. **The commensurability limitation written to Grok's steelman**, which depends on (1).
3. **Systematic lit review** (PRISMA-grade), **Site4Drug / PNAS 2026 verification**,
   **method-novelty language** → *"first honest measurement of an under-explored axis."*

⚠ A methods section cannot be finished over an unruled commensurability question, and this draft
does not pretend otherwise.
