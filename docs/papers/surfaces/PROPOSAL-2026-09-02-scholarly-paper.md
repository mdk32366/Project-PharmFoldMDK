# Proposal for a Scholarly Paper — PharmFoldMDK

> **Date drafted:** 2026-09-02 · **Revision 2:** 2026-09-02, against the 2026-09-02 snapshot
> (HEAD `55601bb`, ⚠ **working tree DIRTY — not a commit**).
> **Type:** A summary document for a non-specialist reader. **Not an authority.**
> **Status:** Draft. The branch is not selected — see §6.
>
> **⚠ This document is derived, not authoritative.** Every substantive statement traces to a log
> entry: **D-015 §1** (Kathad's filters; comparator-not-oracle), **D-100** (the quasi-H-score
> reproduced exactly from S3), **F-043** (the cutoff's stability — ⚠ OPEN, with withdrawn figures),
> **F-004** (the pre-registered result), **F-005** (the confidence ablation), **F-017** (the
> confidence-blind refit), **F-009** (the four false negatives and the over-claim guard), **F-051**
> (attribution share — ⚠ OPEN), **D-075** (the pre-committed branches), **PAPERS-v2.md** (P-001).
> Where this document and a log entry differ, **the log entry governs.** This is a reading surface,
> not a second source of truth.
>
> **⚠ D-074 obligation (F-043).** F-043 is an OPEN finding against this project's comparator. It
> stays open until the comparator no longer exhibits the problem **or** until every surface citing
> the expression ranking carries the statement of what it gets wrong. **This document cites the
> expression ranking, so §2.1 carries that statement. It is not optional and must not be cut for
> length.**
>
> **⚠ Register:** written for a non-technical reader. Plain language is deliberate. It is not a
> licence to overstate — the constraints in §6 bind this document as they bind every other artefact.

### ⚠ What changed in revision 2

Revision 1 said the deciding run was outstanding and held both branches at equal weight. **That was
drafted from a stale context and was wrong.** F-017 landed 2026-08-06. §4.1 and §6.1 are rewritten,
not appended to. §2.1 is rewritten from hand-waving into measured numbers from D-100 and F-043,
with F-043's withdrawal carried. The error is recorded as a Planner finding (§8), not absorbed.

---

## §1 — The problem

Most people pick ADC targets by looking at expression — which proteins show up much more often on
tumor cells than on healthy ones. Rank by that, pick the top of the list.

That method has a track record of missing good targets. Kathad et al. 2024 used expression filters
and left out **Trop-2, CD33, CD30, and CEACAM5**. All four are real ADC targets that reached
patients. CD33 is the target of Mylotarg — the first ADC ever approved. Four misses is a pattern.

*(Source: F-009. Absence checked by grep against `data/adc_reference_mapping.csv` and
`data/cohort_82.txt`; accessions verified against the UniProt REST API.)*

---

## §2 — The blind spots

Kathad's filters are published, so the kinds of holes the method has can be described directly.

**⚠ What is NOT established:** which specific filter dropped which specific target. The four
absences are confirmed. The per-target mechanism is not traced. That is checkable work, it has not
been done, and it is not guessed at here.

### 2.1 — A hard line through a coarse measurement

**This section carries the D-074 statement of what the comparator gets wrong (F-043).**

The method keeps any protein scoring 150 or above on a 0–300 expression scale. Two things about
that scale, both measured:

**The panel is tiny.** The score is a weighted percentage over a tissue panel of **median 11
patients, mean 10.2, maximum 12**. **246 of 1,640 rows rest on 4 patients or fewer; two rest on
two.** At 12 patients the score can only move in 8.33-point steps. At 4 patients, 25-point steps.
So a hard cutoff is being applied to a number that can only take a few dozen distinct values.

**The cutoff lands exactly on the most crowded value.** **52 pairs sit at exactly 150.0.** Using
"150 or above" keeps 337 pairs. Using "above 150" keeps **285**. The direction of the inequality
sign is worth 52 pairs — and all 52 are float-equal to 150.0, none above it.

**The paper disagrees with itself across two representations of its own data.** Recomputing from
raw patient counts gives 337; using the paper's own printed percentage columns with the paper's own
formula gives **329**. Eight pairs fall below the line on rounding alone.

**⚠ Three limits on this section, stated before anyone cites it:**

1. **No claim that Kathad's arithmetic is wrong.** D-100 reproduced every value exactly — 337 of
   337 kept, 1,303 of 1,303 excluded. The finding is about the **stability of the filter's output**,
   not its correctness. Their published denominator convention was read off the file, not inferred.
2. **The flip-rate figures are WITHDRAWN and must not be cited.** An earlier version of F-043
   published a percentage of surviving pairs that turn on a single pathologist call. The
   perturbation rule behind it was underspecified and the number could not be reproduced. It was
   withdrawn the same day, before any external use, and recorded as a **Planner finding**. The
   re-derivation is pre-registered and outstanding. **Nothing in this section depends on it.**
3. **Whether Kathad's own limitations section states this is UNCHECKED.** "They did not mention it"
   is not a claim this document makes. It decides whether the framing is *quantifying a stated
   caveat* or *identifying an unstated one*, and that has not been determined.

**Why it matters here.** F-009 records four clinically-validated targets as false negatives of this
filter. Instability at the boundary is a **mechanism** that produces false negatives — it turns four
anecdotes into an expected behaviour. ⚠ **It does not prove those four arose this way.** Checking
whether they sit near the cutoff is a separate, pre-registerable measurement that has not been run.

### 2.2 — Throwing out anything found in important healthy tissue

Any protein highly expressed in 13 critical normal tissues gets dropped. That sounds obviously
right — you don't want the drug attacking healthy organs. But the real question is whether the
damage is tolerable and manageable. Some approved ADCs hit targets healthy cells carry too, and the
side effects are handled with dosing and monitoring. A filter this strict deletes drugs that work.

### 2.3 — Requiring the RNA and the protein to agree

Cells make RNA first, then build proteins from it. The method requires those two measurements to
line up. Usually they do. But sometimes a cell already has the protein built and moves it to the
surface when conditions change — under stress, low oxygen, or after treatment. Then the RNA looks
flat while the protein sits on the surface, and the filter throws it out.

*(This is the subject of candidate paper **P-002**, which currently has a question and no
measurement, and is recorded as such.)*

### 2.4 — The scoring rewards proteins people already study

The evidence score counts how many papers exist, whether antibodies were already made, and whether
the target reached trials. A protein nobody studied scores low *because* nobody studied it. That is
circular — a popularity score wearing a biology costume.

**⚠ The same trap applies to this project's own method, and §4.1 reports what happened when it was
tested.** This section does not point at a flaw in their method that this project has escaped.

### 2.5 — Nobody measured shape at all

Kathad's entire feature set is about *how much* protein is there. Nothing asks whether a drug can
physically reach it. No structures were folded, so this axis isn't measured — it's absent.

### 2.6 — Why this strengthens the argument rather than weakening it

Kathad et al. published their filters in full and openly recorded that those filters excluded
**TROP2, HER3, and CLDN18.2**. They flagged misses of their own. That is a transparent paper, and
§2.1's numbers exist only because the underlying data was published richly enough to recompute.

Which is the point: **these blind spots are not sloppiness. They are properties of what
expression-based ranking is.** A more careful version of the same approach has the same holes. That
is the case for adding a second, independent axis rather than tightening the first one's filters.

---

## §3 — The idea, and what was built

§2.5 is the blind spot this project can act on. An ADC must physically attach to the part of the
protein sticking out of the cell, so the shape of that part should matter. Nobody measured it
carefully across a whole set of targets, because nobody had the structures. Folding models make
getting them cheap.

**What exists:** a pipeline that predicts the 3D shape of each candidate target's extracellular
segment using **ESMFold, run in-project** — not retrieved from a structure database. It derives
shape-based features from those predictions, fits a ranking model, and asks: *does the shape-based
ranking reorder the expression-based one in a way that means something?*

---

## §4 — Why this appears to be publishable

### 4.1 — The confidence question was asked, and answered — with a narrower answer than hoped

Folding models report how confident they are in each prediction (**pLDDT**). Models are more
confident about heavily studied proteins. Heavily studied proteins are also the ones people already
tried as ADC targets. So a shape-based ranking that appears to work might be re-discovering which
proteins are famous.

The test was specified first, and both readings were committed in writing before it ran (D-075
Decision 4). **The result:**

- **Remove the confidence features and the signal drops** (F-005): median 0.5625, 6 of 12 targets
  above the midpoint, against the full model's 0.6071 and 8 of 12.
- **Replace them with a single measure of the same region computed from coordinates alone — never
  reading confidence — and the signal comes back** (F-017): median 0.6607, 8 of 12. The
  pre-registered row that fired reads **"confound weakened."**

**⚠ Four things this does not license, all recorded in F-017 itself:**

1. **The confidence-blind measure scores slightly higher than the full model. That is not a
   finding.** The gap is three of the finest increments the ranking set can express, and one
   target's rank moves it. Decision 4 has no row for "better than the full model."
2. **A confidence-only model carries the highest median of any run** (0.6786, 9 of 12). It is
   correctly not an anchor and the interpretation does not use it — but omitting it would
   misrepresent the result. Confidence plainly does carry signal. **Two encodings of one quantity,
   both of which work.**
3. **Architecturally blind is not statistically independent.** The confidence-blind feature is
   computed over coordinates ESMFold itself produced, and it correlates with the confidence
   features at Pearson −0.49 and −0.62 — moderately, in the expected direction. The code cannot see
   confidence; that is proven by a test that reddens on a contaminated version. **The supportable
   statement is: it recovers the signal without reading confidence — not free of confidence.**
4. **F-005 is refined, not reversed.** It stands as recorded.

**⚠ And the harder half of the test has not run.** The popularity-matched control (Run B) is
**blocked, not pending** — the freeze script is a deliberate stub; the assembly seam shipped without
the network fetchers. Because Run A has now survived, **the attention proxies will be frozen knowing
that.** The rules governing the pull were fixed in advance; the pull itself is post-result. That
disclosure travels with any use of this result and is not softened.

**⚠ One further open item:** F-051 measures that "the two confidence features" is really one —
membrane-proximal confidence carries 32.2% of attribution, mean confidence 6.4%. That finding is
OPEN with a pre-registered fork and is not interpreted here.

### 4.2 — The critique of the existing method stands alone

§2's blind spots are documented, measured, and reproducible from published data. They say something
about expression-based ranking regardless of how this project's scorer performs.

### 4.3 — The method discipline is the differentiator

Predictions recorded before results. Stated denominators. Corrections written into the log rather
than quietly patched — including the withdrawal in §2.1, this document's own revision in §8, and
the four "does not license" clauses above. Tests required to fail before they are trusted to pass.

That is not the contribution. It is what makes the contribution trustworthy.

---

## §5 — Why it could matter: better, faster, cheaper ADCs

**⚠ None of this is demonstrated.** It is the case for why the work is worth doing.

**Better.** Expression asks *is there a lot of this protein on the tumor?* It does not ask *can a
drug get to it?* A target can pass the first and fail the second. A shape-based check adds a second,
independent way to sort candidates — and §2.1 shows the first axis has a boundary that 52 pairs sit
exactly on.

**Faster.** Testing a target in the lab means making an antibody, attaching a drug, and running cell
and animal experiments — months per target. Predicting a shape takes hours. A computational screen
does not replace the experiments; it decides which experiments are worth running.

**Cheaper.** ADC programs fail late and expensively. Moving a *this will not work* signal from phase
2 back to a computational screen saves everything in between. Cheap failures early are how expensive
successes later get funded.

**And the outcome easy to overlook:** a clear negative result also saves money — it stops other
groups spending years on the same dead end.

---

## §6 — What must be said plainly

### 6.1 — The branch is not selected

Run A survived and its reading is recorded (F-017). **That is not branch selection.** Two papers
remain committed at equal prominence in `PAPERS-v2.md`:

- **Branch A** — a structure-derived axis for ADC target prioritization is orthogonal to expression
  and robust to confidence confounds.
- **Branch B** — predicted-structure confidence confounds structure-based target prioritization: a
  cautionary analysis.

D-075's stronger reading — *confound substantially excluded* — requires the signal to survive
popularity-matching on **both** attention proxies. **That run is blocked.** What is established is
the weaker row: confound weakened. ⚠ **The register and this document must not drift on that
distinction.**

### 6.2 — The boundary that does not move (F-009 §3)

*The expression method has documented blind spots* is established, and §2.1 now measures one of
them.

*This project's scorer fills them* is **not** established and is not asserted anywhere here. The
four targets in §1 are unfolded and unscored. Two (CD30, CD33) are attention-rich — the exact
confound D-075 exists to test — so using them as validation would walk into the problem the project
is trying to measure.

Only the first claim is proven.

---

## §7 — Definition of done

- [ ] Cross-checked against `docs/README.md` and `PAPERS-v2.md` — **partially discharged at revision
      2** against the 2026-09-02 snapshot, which was **DIRTY**. Re-check against a commit.
- [x] §6.1 revised after Run A. ⚠ **Revised again when Run B resolves or is formally abandoned.**
- [x] §2.1 carries the F-043 D-074 statement, with the withdrawn figures excluded by name.
- [ ] §2 gains the per-target filter trace, or keeps its explicit "not established" marker.
- [ ] The near-cutoff check on the four false negatives — pre-registered, not yet run.
- [ ] The §6.2 over-claim guard respected in any derived artefact (deck, abstract, email).
- [ ] Every cited entry resolves. **New citations at revision 2: D-100, F-005, F-017, F-043, F-051.**
      ⚠ The citation invariant proves a reference *resolves*, never that it resolves to the right
      thing (F-044).

---

## §8 — ⚠ Revision 1's error, recorded rather than absorbed

Revision 1 stated that the deciding run was outstanding and held both branches at equal weight. **F-017
had been in the log since 2026-08-06.** The Planner asserted its absence from stale context, four
times in one session, and the document was landed under D-108 carrying that error.

**This is the KEEL V9 prohibition — never assert absence from a stale snapshot — and it is a Planner
finding, not a footnote.** D-108's decision to leave §7's cross-check item **open** rather than
marking it discharged is what made the error visible on the next grounding. That was the right call
and it worked.
