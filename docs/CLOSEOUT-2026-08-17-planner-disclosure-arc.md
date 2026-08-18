# CLOSEOUT — 2026-08-17 · The disclosure arc

> **⚠ This session spanned roughly a week of wall-clock time.** That has two consequences the next
> session must handle before anything else, and they are recorded first because they are the ones
> most likely to be skipped:
>
> 1. **Every staged entry is dated `2026-08-17`, the drafting date — not necessarily the ruling
>    date.** D-016 wants the date a thing was ruled. Where a ruling below was actually made earlier
>    in the span, **correct the date at merge.** The Planner cannot recover the true dates.
> 2. **All repository state in this close-out is either snapshot-read (today) or prior-session
>    recall (up to a week+ old, possibly more).** Every such claim is marked. **None of it is a
>    valid basis for action without re-confirmation against a repository zip.**

- **Session type:** Decision-and-content. **Zero code written. Zero folds run. Nothing deployed.**
- **Grounding used:** project-knowledge snapshot + `userMemories`. **No repository zip, no git
  metadata, no connector.** Per standing methodology this is a **fallback, not a continuity
  mechanism** — and it is the single largest caveat on everything below.
- **Owner rulings this session:** 5 (oligomer-first; merged glossary with links and tooltips;
  census on standby; clinical layer with normal-tissue differential in scope; licensing reversed to
  no-license; D-entry for the briefing copy).

---

## §1 — The merge queue, in dependency order

**Nothing merges until step 0 completes.**

| # | Artifact | Depends on | Gate |
|---|---|---|---|
| **0** | **Resolve the numbering chain** | — | see §2 |
| 1 | `F-012-single-chain-oligomer-interface.md` | F-011 landing | owner ruled: logged **before** briefing prose |
| 2 | `D-079-clinical-association-layer.md` | D-076, D-077 landing; D-078 staying reserved | — |
| 3 | `D-080-claim-discipline-educational-surfaces.md` | D-079 | governs items 4 and 5 |
| 4 | `glossary.json` | D-080 dec 3 | 16 topology terms still missing (recorded gap) |
| 5 | `BRIEFING-copy-about-adcs.md` | F-012, D-080 | adversarial review pass (D-080 dec 7) not yet run |

**Items 4 and 5 are content, not code, but D-080 rules they carry code-equivalent review weight.**

---

## §2 — ⚠ Step 0: the numbering chain, which is fragile and unverified

Read from the snapshot, **not from the live log**:

- Highest `### D-` **entry in the log**: **D-075**.
- **D-076** — claimed by a staged *file* (`D-076-last-three-fold-plan.md`), **no `### D-076` entry
  in the log**. This is the D-062 shape: a file that looks merged and is not.
- **D-077** — staged file, not merged.
- **D-078** — **reserved by name** in D-077 decision 7 for the F-008 precision A/B. Not free.
- Highest `### F-` **entry**: **F-010**. **F-011** claimed by a staged file
  (`F-011-surfaceome-negative-class-v2.md`), no log entry.

**So D-079, D-080, and F-012 are correct only if D-076, D-077, and F-011 all land as written and
D-078 stays reserved.** If any of those has moved in the intervening week, **three entries need
renumbering before merge, and a renumbered entry is otherwise indistinguishable from a misfiled
one** (D-027's own numbering note).

**Check the thing, not the reference to it.**

---

## §3 — What was ruled, and what is genuinely new

### F-012 — the single-chain finding
ESMFold folds monomers. An obligate oligomer's subunit interface is large, flat, and continuous —
the exact geometry feature 6 rewards — so it is **indistinguishable from an accessible patch**, and
the resulting bias is **directional, not random**. The pipeline has no vocabulary for it.

**The entry's discipline is its §2 split:** what is *established* (deductive, from code — sufficient
on its own to trigger D-074) versus what is *reasoned but unmeasured* (magnitude and direction on
this cohort — nobody has looked). §5 pre-registers the measurement with all four readings fixed
before it runs, including the fourth: if `unannotated` swamps the comparison, that is a finding
about **annotation supply**, reported as such.

**Touches nothing numeric.** F-004, F-005, D-075, and Run A keep every number. What changes is the
**write-up**: F-005 narrowed the claim on the *confidence* axis; this narrows it on the
*accessibility* axis, and the two are independent.

### D-079 — the clinical association layer
The request was one artifact and is three: protein→tumour (a property of the protein), and
tumour→lethality / tumour→survival (properties of a **disease**).

**Load-bearing ruling:** burden attaches by **traversal**, never as a protein column, and is
**structurally unreachable** from protein-level payloads — D-075's architectural-guarantee pattern,
not a test alone. Burden-ordered sorting is barred everywhere.

Also ruled: an ordinal `evidence_type` enum, never flattened to a boolean (localisation is **named,
never inferred** — F-022); D-077's three transferred rulings, of which **"must not filter the
census"** is the one convenience will attack, because it is F-009 at 2,807-row scale; survival
statistics carry a mandatory `(site × stage × era × population)` tuple or do not render; the
**normal-tissue differential co-equal** by owner ruling, with cross-evidence-class differentials
barred at the schema.

### D-080 — claim discipline in educational surfaces
**The genuinely new finding of the session.** D-028 governs what a surface *asserts*. It has nothing
to say about what a surface *supplies as a premise*. The briefing can be true, the Scorer can be
compliant, and **the reader assembles the forbidden sentence from both** — then attributes it to us,
with us unable to point at where we said it.

The ruled test is therefore not *"is each sentence true?"* but *"what forbidden sentence can a
reader build from this surface plus any other?"* Plus: the banned-phrase list as a **gate**; one
glossary as **data**, with the `source` field explicitly barred from re-splitting it; reading level
as **load-bearing on D-024** rather than stylistic; and disclosure as a **mount precondition** —
which generalises to *every* open finding without needing re-ruling.

**Decision 5 fills a hole in Constraint A** that had gone unnoticed: Constraint A rules every number
derives from the payload, and has no provision for a number that is not a project measurement at
all. Three kinds now — derived, external, configured — with derived-adjacent-to-external-unmarked
barred, because the external number otherwise **borrows the derived one's provenance**.

---

## §4 — Corrections recorded, not quietly patched

Five, per the standing rule that corrections are explicit.

1. **"~440 aa ceiling" is imprecise** and appears that way in the project's own shorthand. 440 is
   `CEILING_KNOWN_GOOD` — the highest length **known to work** at int8 / chunk 64. 630 is known-bad
   4-for-4. **The band between is unmeasured.** Concrete cost already paid: ENTPD1 at 441 aa was
   routed to paid rental for being one residue over a bound nobody measured. Also: **440 applies to
   the ECD span, not protein length** — a 2,000 aa protein with a 400 aa ECD folds locally.
2. **"Mean time to death" is not the statistic that exists.** Survival distributions are
   right-skewed and censored; the mean is not published and not estimable from public aggregates.
   Substituted median OS and N-year relative survival, **recorded in D-079 dec 4 rather than
   silently swapped.**
3. **Licensing direction reversed.** AGPL + dual-licensing → **no license, all rights retained**
   (owner ruling). Recorded as a reversal in D-079 dec 7. **Separated from the inbound question**:
   third-party data terms bind regardless of what the repo's own license says or omits.
4. **Planner self-correction.** The oligomer point was first raised as though established. It is
   not — F-012 §2 rewrites it into established/reasoned, and the unmeasured half is the larger
   half. Recorded because the first framing would have entered the paper as a finding.
5. **Planner could not run the licensing search.** Web search unavailable; container network
   allowlist excludes every relevant domain. **Planner recollection of license terms was offered in
   chat and deliberately kept out of the log.** It is not evidence.

---

## §5 — What was NOT done

- **No code. No tests. No deploy.** Nothing reached Fly.io; nothing was written to touch it.
- **Census Task 4a: standby by owner ruling.** No census rows ingested. ⚠ Worker state is
  **prior-session recall**, now a week+ stale — **re-confirm before resuming**.
- **No supplier confirmed** for the clinical layer. D-079 dec 6's five-point checklist is unrun.
- **No licensing terms read** (§4.5).
- **F-012 §5 unrun** — the oligomer magnitude measurement is pre-registered, not executed.
- **16 rejected topology terms not merged** into `glossary.json` — recorded gap, not omission.
- **The two `external_value` numbers unverified** (~90% conformational epitopes; 15–25 contact
  residues). Flagged in copy and glossary. **UI-shippable as marked-external; barred from the paper
  until sourced.**
- **Adversarial premise-assembly review pass** (D-080 dec 7) not run.
- **§3's F-012 target names unverified** — `GRIN1`, `SCNN1A`, `EGFR`, `HER2`, `CDH11` are Planner
  recollection offered as **leads, not findings**.

---

## §6 — Open items carried forward

| Item | Gates | Owner | Age |
|---|---|---|---|
| Numbering chain resolution | **all three entries** | Matt | new |
| Ruling-date correction on staged entries | merge accuracy (D-016) | Matt | new |
| Census Task 4a | census rows, P-002 | Matt | carried, **stale** |
| D-075 / P-001 gate | the paper | Matt | carried |
| Supplier confirmation ×5 | D-079 schema | Matt / Planner | new |
| Inbound terms check ×5 | ingest only | Matt | new |
| 16 topology glossary terms | glossary completeness | Matt / Planner | carried |
| External-value citations ×2 | **the paper**, not the UI | Matt | new |
| Adversarial review pass | briefing ship | Matt / Planner | new |
| F-012 §5 measurement | bounding the bias | Matt | new |
| Banned-phrase gate | briefing ship | Builder | new |
| University DUA / IP position | the all-rights-retained assumption | Matt → Razzak | new |
| Second-model pre-registration | any fit over the clinical layer | **not authorised** | new |

---

## §7 — Pre-work seed for the next session

*Paste this into the next Planner session. Attach the repository zip in the same message.*

```
CONTINUITY — from CLOSEOUT 2026-08-17 (the disclosure arc)

GROUNDING: repo zip attached. Prior session had NO zip — it ran on
project-knowledge snapshot + memory. Treat every state claim in the five
staged artifacts as UNCONFIRMED until checked against this tree.

FIVE ARTIFACTS STAGED, none merged:
  F-012  single-chain / oligomer-interface finding
  D-079  clinical association layer (protein→tumour→burden as traversal)
  D-080  claim discipline in educational surfaces
  glossary.json          (49 terms; 16 topology terms MISSING)
  BRIEFING-copy-about-adcs.md

FIRST MOVE, before anything else:
  Resolve the numbering chain. D-076/D-077/F-011 are staged FILES with no
  log entries. D-078 is RESERVED (F-008 precision A/B). If any moved during
  the week this session spanned, three entries renumber before merge.
  Also: all three are dated 2026-08-17 = drafting date, not ruling date.
  Correct at merge (D-016).

SECOND: re-confirm census Task 4a state. Prior-session recall is a week+
  stale. Owner ruled STANDBY; do not resume without confirming worker and
  DB state from the live system.

NOTHING NUMERIC MOVED. F-004, F-005, D-075, Run A keep every number.
F-012 narrows F-004's INTERPRETATION on the accessibility axis, in writing
only. D-075's ablation arithmetic stands.

CANDIDATE NEXT ARCS (owner's call, not sequenced here):
  a) merge queue + adversarial review pass → ship the briefing
  b) F-012 §5 — measure the oligomer bias magnitude (pre-registered)
  c) D-079 supplier confirmation (5-point checklist, dec 6)
  d) resume census Task 4a
  P-001 remains gated on D-075.

DO NOT: add a feature (D-027's six stands), filter the census by anything
clinical or by foldability, or let a burden statistic reach a protein-level
payload.
```

---

## §8 — Session assessment

**What this session was:** a disclosure arc. Three entries and two content artifacts, all of which
constrain what the system may say rather than extending what it can do. **No capability was added
and that was correct** — the capability the owner opened with (rendering patches on the viewer)
turned out to be gated on a finding nobody had logged, and building it first would have shipped a
directional bias with a colour on it.

**The catch worth noting:** the session's most valuable output, D-080 decision 1, was **found while
drafting**, not while planning. The gap between *asserting a claim* and *supplying a premise* was
invisible until copy existed to test D-028 against. That is an argument for writing the artifact
rather than specifying it — and it is the second time this session that drafting surfaced something
reasoning had missed (Constraint A's missing third category was the first).

**The pattern that produced all of it** remains the owner's domain questions. *"How does the
antibody-antigen connection work?"* produced F-012. *"What does 440aa mean?"* produced correction 1.
*"Explain this in 8th grade language"* produced the copy that produced D-080. **Three questions,
three load-bearing outputs, none of which were on any roadmap at session start.**
