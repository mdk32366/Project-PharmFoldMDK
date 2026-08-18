# F-040 — The single-chain finding: ESMFold folds monomers, so an obligate oligomer's subunit interface is indistinguishable from an antibody-accessible patch — and features 6 and 7 are biased **in a direction**, not merely noisily

> **STAGED ENTRY — merge into `docs/README.md`.** A finding against the instrument (**D-074**):
> it stays open until ESMFold no longer exhibits it, or until every surface reporting features 6
> and 7 carries the statement of what they get wrong.
>
> **⚠ Confirm the number against the live log before merging.** In the snapshot read this session
> the highest `### F-` entry is **F-010**, with **F-011** claimed by a staged file
> (`F-011-surfaceome-negative-class-v2.md`) and no `### F-011` entry in the log. **F-012 is the
> next free integer *if* F-011 lands as written.** Check the thing, not the reference to it.
>
> **⚠ Drafted from a project-knowledge snapshot, not a repository zip.** Every code fact below is
> marked with how it is known and requires confirmation against the live tree.

> ---
>
> ## ⚠⚠ RENUMBERED ON MERGE — F-012 → **F-040**
>
> **This entry claimed `F-012`. The live log had already spent it** (ESMFold's chunked trunk is not output-invariant). The document was
> authored against a snapshot whose highest `### D-` was **D-075**; the log stood at **D-092** when
> it arrived — seventeen decisions later.
>
> ⚠ **The note below is left exactly as written.** It is a true statement about the tree its author
> read, and rewriting it would falsify the provenance it exists to record. **The claim is corrected;
> the observation is not.** Its own instruction — *"Check the thing, not the reference to it"* — is
> what caught this (`F-039`).
>
> **Assigned `F-040` on 2026-08-17.** Cross-references to sibling staged entries were
> renumbered with them; citations to *other* entries were left untouched and are **not reviewed
> here**.
>
> ---

- **Date:** 2026-08-17
- **Status:** **Open.** Established as a structural gap; **unmeasured as to magnitude.** See §2 —
  the split between what is known and what is reasoned is the load-bearing part of this entry.
- **Type:** A **finding against the instrument.** It reports a class of error the pipeline cannot
  currently detect, name, or bound.
- **Relates:** **D-016** (every claim names how it is known); **D-027** (feature 6 — largest
  contiguous accessible patch — and the explicit rejection of pocket detection on the grounds that
  *"an antibody binds a surface patch, not a cavity"*); **D-028** (attribution is about the model,
  never the target); **D-058** (feature 6's two parameters, fixed by convention); **D-069** (every
  surface self-sufficient); **D-074** (the governing rule for this entry); **D-075 / feature 7**
  (`membrane_proximal_sasa`, the confidence-blind geom_proxy — **also affected, see §4**);
  **D-077 decision 1** (an axis that must not become a feature — the pattern §6 follows);
  **F-004** (the central result, whose *interpretation* this narrows); **F-005** (the pLDDT
  confound — this is a **second, independent** narrowing, not a restatement); **F-009** (the
  false-negative finding this rhymes with, at the instrument level rather than the cohort level).
- **Provenance (D-016):** raised by the Planner, 2026-08-17, while answering an owner question about
  rendering feature-6 patches on the 3Dmol structure viewer. Owner ruled the same session that it is
  logged as a finding **before** any About-ADCs briefing prose is drafted. A project-knowledge
  search for an existing record of this limitation returned nothing — **⚠ that is a fallback search
  and is not an absence proof.** Confirm against the live log before merging as novel.

---

## §1 — The finding, in one paragraph

ESMFold predicts the structure of **one chain**. Many cell-surface proteins are not physiologically
one chain: they are obligate homo- or hetero-oligomers, and the face by which subunits associate is
permanently buried in the assembled complex. That face is, by evolutionary construction, **large,
flat, and continuous** — which is precisely the geometry feature 6 was designed to reward. Folding a
single subunit therefore exposes an interface that does not exist in life, and the pipeline has **no
vocabulary to say so**: nothing in the manifest, the feature row, the score, or any surface records
oligomeric state, and feature 6 cannot distinguish an antibody-reachable patch from a subunit
interface. The error is not random. **It runs in one direction — toward scoring obligate oligomers
higher** — which makes it a bias rather than noise.

---

## §2 — ⚠ What is established, and what is reasoned. The distinction is the entry.

**This entry must not be read as a measured result.** It is not one. Splitting it honestly:

### Established — verifiable from code and model definition today

| Claim | How known (D-016) |
|---|---|
| ESMFold takes a single sequence and returns a single-chain structure | model definition; `worker/runner.py` `FoldResult` — snapshot |
| `core/features.py` parses one PDB, computes SASA over its atoms, and has no concept of a second chain | `parse_pdb`, `shrake_rupley`, `_largest_patch_fraction` — snapshot |
| Feature 6 rewards **large contiguous** accessible surface, at rel-SASA ≥ 0.25 / CA–CA ≤ 8 Å | `D-058` decision 2; `core/features.py` constants — snapshot |
| **No oligomeric state is recorded anywhere** — not in the manifest, `protein_analyses`, `protein_features`, or any payload | ⚠ **absence, from a fallback search.** Confirm against the live tree |
| The system therefore **cannot detect, flag, or bound** this error class | follows from the four rows above |

**That much is deductive and requires no measurement.** It is sufficient on its own to trigger
D-074: the instrument exhibits a defect it cannot report.

### Reasoned, not measured — everything about magnitude and direction on *this* cohort

- **That oligomerisation interfaces are large and flat** is a general structural-biology claim.
  Planner recollection; **not verified against primary literature and citations not checkable from
  here.** Verify before it reaches the paper.
- **That the bias is directional on the 56-target ranking set** is an inference from the conjunction
  above, **not an observation.** No one has looked.
- **How many cohort or census members are obligate oligomers** is unknown. No annotation exists.
- **Whether the bias is large enough to move a rank** is unknown, and is the only question that
  determines whether this narrows F-004's interpretation materially or trivially.

**Nothing in §2's second half may be stated as a finding until §5 runs.**

---

## §3 — The distinction that stops this being overclaimed: obligate vs. induced association

The finding is **not uniform across the cohort**, and treating it as uniform would be its own error.

- **Obligate constitutive oligomers** — multi-subunit channels and receptors that exist as an
  assembly essentially always. The isolated subunit is **never the physiological species**, so its
  modelled interface is an artefact with no in-life counterpart. *This is where the finding bites
  hardest.*
- **Ligand-induced dimers** — receptor tyrosine kinases that dimerise on ligand binding and spend
  meaningful time as monomers. Here the "interface" **is** genuinely solvent-exposed part of the
  time, so a patch there is not automatically an artefact. It may even be a real epitope: the
  therapeutic antibody pertuzumab is understood to bind HER2's dimerisation face. *⚠ Planner
  recollection, citation not verifiable from here — check before use.*
- **Constitutive covalent heterodimers** processed from one precursor are a third case and may be
  partly handled already by the ECD-slicing boundary logic — **unexamined**.

**Candidate probes, offered as leads and explicitly NOT as findings.** Planner domain recollection,
**unverified against the cohort CSV or UniProt**: `GRIN1` (an NMDA-receptor subunit, obligate
heteromer) and `SCNN1A` (an ENaC subunit, obligate heterotrimer) are the sharpest candidates for the
obligate class, and both appear in D-077's list of thirteen targets in the (440, 630) band.
`EGFR`, `HER2`, `PDGFRB`, `CSF1R`, `MERTK` are candidates for the induced class; `CDH11` for the
constitutive-homodimer class. **Every name here requires verification before it is used for
anything.**

---

## §4 — Feature 7 and the geom_proxy ablation are affected too, and it is not obvious in which direction

D-075's `membrane_proximal_sasa` (feature 7) is confidence-blind by construction, and Run A used it
to show that a purely geometric axis recovers what `no_plddt` lost. **That result is a statement
about geometry — and this finding is a statement about whose geometry.**

- Feature 7 averages SASA over the C-terminal (membrane-proximal) window. Whether subunit interfaces
  concentrate in that window, avoid it, or distribute indifferently is **class-dependent and
  unknown**.
- So feature 7 may be **more** contaminated than feature 6, **less**, or equally. There is no basis
  to guess, and this entry does not.
- **⚠ This does not invalidate Run A or D-075.** The ablation was pre-registered, executed as
  written, and its arithmetic stands. What this finding touches is the **interpretation** — *"a
  confidence-blind structural axis recovers the signal"* is unchanged; *"and that axis measures
  antibody-reachable surface"* is the part now carrying an unbounded error term.

**The same holds for F-004.** Its pre-registration, its execution, and its numbers stand untouched.
Its **write-up** must carry this. F-005 already narrowed the claim on the confidence axis; this
narrows it on the **accessibility** axis, and the two are independent — a reader who has absorbed
F-005 has not absorbed this.

---

## §5 — The measurement that would settle magnitude, pre-registered here before it runs

**Frozen before execution. The reading of each outcome is fixed now** (D-041 decision 4 discipline —
no tolerance invented after seeing the result).

**Design.** Annotate every ranked target with an oligomeric-state category drawn from a **named
external annotation with a recorded retrieval date** — UniProt subunit-structure annotation is the
obvious candidate, confirmed under D-093 decision 6's supplier-before-contract rule. Categories:
`obligate_oligomer` · `induced_dimer` · `monomer` · `unannotated`. **`unannotated` is a category with
a reason, never merged into `monomer`** — the whole class of errors this project keeps catching is
absence silently becoming a low value.

Then compare feature 6 and feature 7 distributions across categories, and compare the ranking with
`obligate_oligomer` targets held out.

| Outcome | Reading — **fixed now** |
|---|---|
| `obligate_oligomer` targets show **no** elevation in feature 6/7 versus `monomer` | The mechanism is real but does not express at this cohort's scale. Finding stays **open** and disclosed (D-074), but F-004's interpretation is **not** further narrowed. |
| They show elevation, **and** holding them out does **not** move the ranking materially | Bias confirmed, consequence bounded and small. F-004's write-up carries the bound as a stated number rather than an open term. |
| They show elevation **and** holding them out moves the ranking | **The most important outcome, and the one the entry exists for.** F-004's structural claim is narrowed a second time, in writing, with the magnitude stated. |
| `unannotated` is large enough to make the comparison uninformative | A finding about the **annotation supply**, reported as such — not a null result, and not silently discarded. |

**No fifth reading. No post-hoc tolerance.**

**Binding constraint on the measurement itself:** the held-out comparison is a **sensitivity
analysis**, run under `run_kind='sensitivity'`, and — per D-065 — it is **never served as the
result**. It cannot become the reported ranking, and it does not amend F-004's numbers.

---

## §6 — ⚠ Oligomeric state MUST NOT become feature 8, and MUST NOT filter anything

Same shape as D-077 decision 1 and D-075 decision 5, and refused in advance for the same reason:
the temptation after a satisfying annotation is to promote it to an axis.

1. **Not a feature.** D-027's six stands; the named-set refusal stands unamended. An eighth feature
   requires a new dated entry and would need its own pre-registration.
2. **Not a filter.** Obligate oligomers stay in the cohort and in the census, **annotated, not
   dropped.** Dropping them would be F-009's error committed deliberately — and several of them are
   real ADC-relevant biology.
3. **Not a suitability signal in either direction.** Being an oligomer is neither disqualifying nor
   favourable. It is a **statement about how much confidence features 6 and 7 deserve for that
   target** — a liability on the instrument, not an attribute of the protein.
4. **The badge rule applies verbatim** (GPI precedent): where oligomeric state is shown, the
   attribute and the liability render **together**, in the same frame, and the attribute is never
   rendered alone as a positive signal.

---

## §7 — Resolution path, per D-074

D-074 gives two exits. Only one is available.

- **The instrument stops exhibiting it** — would require folding complexes rather than single chains.
  ESMFold does not do this. A different predictor would break D-003's graded claim (*we run
  ESMFold*) and D-021's cross-method comparability. **Closed for this project.**
- **The instrument carries the statement of what it gets wrong** — **the available exit, and
  therefore mandatory.** Concretely:
  - Every surface reporting feature 6 or feature 7 states that the structure is a **single-chain
    prediction** and that a subunit interface is indistinguishable from an accessible patch.
  - The Limitations page carries this finding in full, with §2's established/reasoned split intact.
  - **If patch rendering ever ships on the 3Dmol viewer, this disclosure is a precondition, not an
    enhancement.** A coloured patch is a stronger claim than a sentence and needs the stronger
    caveat. Rendering without it is barred.
  - The merged glossary carries `oligomer`, `obligate oligomer`, `subunit interface`, and
    `single-chain prediction`, dual-audience, each with exactly one entry.

**The finding remains OPEN until those four are shipped, and §5 does not close it.** Measuring the
magnitude bounds the error; it does not remove it.

---

## §8 — Deep-learning justification

**This is a finding about what a neural structure predictor is and is not modelling**, which is the
most direct DL content the project produces. ESMFold's training objective is single-chain structure
from single-sequence input; quaternary structure is **outside the objective**, so the model does not
fail at it — it was never asked. The pipeline then reads a geometric quantity off that output and
treats it as biology, and **the gap between "what the model optimised" and "what we read off it" is
where the error lives.**

That gap is the general lesson, and it is the same lesson as **F-005** at a different layer: F-005
found the signal partly tracking the model's *confidence* rather than the protein; this finds a
geometric feature partly tracking the model's *scope* rather than the protein. Both are cases of a
downstream quantity inheriting a property of the predictor rather than of the target. **A project
that catches this twice, in two different ways, is demonstrating the habit the finding requires** —
which is worth more to a reader than either individual catch.

---

## §9 — Test surface

**Assertable today, before §5 runs:**

- Every surface rendering `largest_patch_fraction` or `membrane_proximal_sasa` carries the
  single-chain disclosure string; a surface that renders the number without it fails (D-069).
- No UI string asserts that a patch is antibody-accessible, reachable, or an epitope — the D-028
  copywriting assertion, extended to this finding's vocabulary.
- Patch rendering on the viewer, if built, cannot mount without the disclosure component present —
  **proven by revert** (A-017: remove it, watch the gate redden).
- Every glossary term in §7 resolves to exactly one entry; no term has two definitions.

**Assertable when §5 runs:**

- `unannotated` is a category with a reason and appears in every count; categories sum to the
  denominator (the partition invariant).
- The held-out comparison runs under `run_kind='sensitivity'` and is unreachable from
  `/api/ranking` — proven by revert (D-065 precedent).
- Oligomeric state is absent from `as_feature_dict()` and from every scorer input path; adding it
  reddens the six-feature assertion.

---

## §10 — What this entry does NOT do

- **It does not amend F-004, F-005, D-075, or Run A.** No number moves. Only interpretation, and
  only in writing.
- **It does not claim a measured bias.** §2 governs; §5 is unrun.
- **It does not name any target as an obligate oligomer.** §3's list is unverified leads.
- **It does not add a feature, a filter, or a score** (§6).
- **It does not gate D-093.** It gates the **About-ADCs briefing prose**, by owner ruling,
  2026-08-17.
