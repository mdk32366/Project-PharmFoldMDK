# RESERVED — announced-but-unwritten entry numbers

> **What this file is for.** The citation invariant is: *every cited `D-NNN` / `F-NNN` / `S-NNN` /
> `DEP-NNN` in `docs/README.md` and `ARCHITECTURE.md` resolves to a real `### ` entry.* It was
> **RESTORED on 2026-08-03**, not inherited — D-062 had accumulated **thirteen** citations with no
> entry, and F-009 was cited by shipped UI and by `ARCHITECTURE.md` while existing only as a staged
> document. See `docs/README.md` method-note item 7.
>
> **The problem this file solves.** Some references point *forward*, at entries deliberately not
> written yet. A forward reference that announces its own absence is **not** the D-062 defect —
> D-062's harm was that citations treated a missing entry as **settled authority**, with nothing in
> the text suggesting it was missing. **But it is indistinguishable from the defect to a checker.**
>
> So the distinction cannot live as prose scattered through a method note: that works only while the
> set is small enough to remember. **This file is the whitelist. The checker whitelists this file
> and nothing else.**
>
> ## ⚠ THE RULE
>
> **An unresolved reference that is not listed below is a finding, immediately.** Not a cleanup item,
> not a note for later — the same class as D-062, found early.
>
> Reserving a number is **not** authorisation to do the work behind it. It reserves the integer and
> records what would unblock it. A reservation that is never written is retired here, in the open,
> with a reason.

---

## How to run the check

Named, not built — deliberately, per **D-074 decision 3** (*do not answer a finding with a framework
that becomes a second thing to drift*). It is one command, and it found two holes the first time it
was run:

```bash
python - <<'PY'
import re, pathlib
log  = pathlib.Path('docs/README.md').read_text(encoding='utf-8')
arch = pathlib.Path('ARCHITECTURE.md').read_text(encoding='utf-8')
res  = pathlib.Path('docs/RESERVED.md').read_text(encoding='utf-8')

defined  = set(re.findall(r'^### ([DFS]-\d+|DEP-\d+|A-\d+)', log, re.M))
reserved = set(re.findall(r'^\| \*\*([DFA]-\d+)\*\*', res, re.M))
cited    = set(re.findall(r'\b(?:D|F|S|DEP|A)-\d{3}\b', log + arch))

missing = sorted(cited - defined - reserved)
print('UNRESOLVED AND UNRESERVED:', missing or 'none — invariant holds')
PY
```

**Read the output, not the exit code.** An empty list is the only passing result.

---

## Reserved numbers

> ### ⚠ The `A-` namespace is not ours to number, and citations carry a name because of it
>
> `A-` numbering is defined by **`KEEL-4-The-Assumption-Register-v1.md`, which this repository has
> never received** (see the document-status table below). `A-014`, `A-016` and `A-017` were all
> assigned **locally, by the same method**, into a namespace KEEL-4 is recorded as holding items
> 15/16/17 of. **So all three carry a live collision risk, not only the newest** — and `A-016` is
> already cited in shipped artifacts (`PAPERS-v2.md` P-001's methods section). Two authorities, no
> reconciliation, and we hold one.
>
> **The mitigation, available now and free:** every **new** local `A-` reference is written as
> **`A-0NN (descriptive name)`**, never as a bare number. If a number moves when KEEL-4 lands, the
> citations do not orphan — **the name carries them.** That is D-074's remedy (*a name that states
> its own rule*) applied to a citation rather than to a field. The names are in the rows below, so
> this file is the index bare citations resolve through.
>
> ⚠ **Forward-only. Existing citations are NOT rewritten** — not in `PAPERS-v2.md`, not in the
> sealed 2026-08-05 rulings, not in the log. Editing a sealed document to look as though it never
> used a bare number is the shape this project refuses; `RULINGS-2026-08-05-task2-task3-contract.md`
> §3.1 got a *pointer* rather than a corrected definition for the same reason.
>
> ⚠ **Nothing is renumbered.** `A-014`, `A-016`, `A-017` keep their integers. **The reconciliation
> when KEEL-4 lands must check all three**, not only `A-017`.


| Number | What it will be | Reserved by / when | What unblocks it |
|---|---|---|---|
| **F-042** | *The census discards PAE on every fold* — the model emits `predicted_aligned_error` on every forward pass, and for 2,690 of 2,690 census rows the pipeline persists it by neither path. Measured 2026-08-17: tranche 0 carries 79 of 80; tranches 1–4 carry **zero of 2,691**; the fold-day partition puts every PAE row on 2026-07-23/24/25 and none on 2026-08-16. | Owner, 2026-08-17; cited by **`D-099`** | **The owner writes it.** ⚠ Code is instructed not to draft it. ⚠ **`D-099` may rewrite it entirely**: if a local int8 chunked fold emits no `predicted_aligned_error`, this is a *different* finding (`pae_never_emitted`, not `pae_absent_local_tier`) and must be rewritten rather than amended. ⚠ A second, smaller finding is **open and not closed as done**: whether the 79 `pae_json_path` values resolve to files on the Fly volume — *a path is still not a file* — unverified because the volume read was denied to Code. |
| **D-010** | *Nothing.* A historical skip — the sequence runs D-001…D-009 then D-011. | Pre-2026-07-19 | **Never.** Not renumbered because commit `c07b95b` already names D-011. Permanent, documented in `docs/README.md`. |
| **D-078** | The F-008 precision A/B pre-registration — the controlled re-fold at the opposite precision | D-077 dec 7, 2026-08-04; ⟡ **trigger amended D-079, 2026-08-05** | ⟡ **AMENDED TRIGGER: the first census fold at a second precision.** D-079 dec 2 folds every target at whichever tier reaches it, so the census *creates* the overlap directly rather than waiting for a ceiling to rise. ⚠ **Its outcome can move F-004**, so it is written before any such fold runs. **Superseded trigger, recorded because a reservation whose condition changed silently is a reservation nobody can check:** *"a raised local ceiling — if D-077's bisection lifts the ceiling above 440, rental/fp16 targets become locally foldable at int8, creating the first overlap in a partition F-008 recorded as having none."* That route remains valid; it is no longer the only one, and no longer the first. |
| **D-080** | *A revert proof operates on committed state or on a copy — never on a working tree holding uncommitted work.* | Amendment §3, 2026-08-04 | Nothing — writable now. Prompted by assumption-register item 15, which is at **n=2** (D-075's process note is the first occurrence). |
| ~~**F-011**~~ | ~~The surfaceome negative class — SURFY's exclusion is condition-dependent localization, not "cannot be a target"~~ | ~~Planner, 2026-08-04~~ | ✅ **WRITTEN 2026-08-04**, in the same commit as F-016 — see `### F-011` in the log. No longer a reservation. ⚠ **It had been staged in `docs/` and pushed since 2026-08-04 without ever entering the log** — the D-062 defect in the Planner's own output, surfaced only because F-016 grepped for the header rather than the filename before merging on top of it. The landing note in the entry records this. Its magnitudes are **discharged by F-016**: 2,216 counted, `~5,102` withdrawn. |
| ~~**F-012**~~ | ~~Task 1 — the chunk-invariance verdict~~ | ~~D-077 dec 2 / amendment §1~~ | ✅ **WRITTEN 2026-08-04.** The run happened; row 2 fired (outputs differ, chunk 16 diverges from 64). No longer a reservation — see `### F-012` in the log. |
| **F-015** | Does an **unchunked** fold (`chunk_size=None`) differ from `chunk_size=64` at fp16? | F-012, 2026-08-04 | **A GPU run that has not been designed yet.** F-012 established that chunk_size can change output (16 vs 64, int8, 114 aa) and that the folded cohort spans three recipes — **34 targets at `('fp16', None)`**, 3 at `('fp16', 64)`, 42 at `('int8', 64)`. It did **not** measure `None` vs `64`, which is the comparison that would decide whether the cohort's rental folds are commensurable with each other. ⚠ Needs its own pre-registration before it runs, because its outcome could bear on every rental-tier feature. |
| **F-013** | Task 3 Arm A — the measured local ceiling | D-077 dec 3-4 / amendment §1 | **The GPU run.** Bisection in (440, 630) at int8/chunk 64, k=4, step 8. May legitimately return `unstable` at every length. |
| **F-014** | *Documenting a duplication is not managing it* — the tenth instance of the two-paths-to-one-quantity class, and the first where the drift was **written down and the writing-down substituted for the fix** | Amendment §7, 2026-08-04 | Nothing — writable now, but **held until `d077-local-fold-envelope` merges**, because it describes code that branch changes. |
| ~~**F-017**~~ | ~~The **D-075 result** — which row of D-075 Decision 4 fired, and what it licenses~~ | ~~`ORDERS-Code-2026-08-05-D-075-run.md` §5, 2026-08-05~~ | ✅ **WRITTEN 2026-08-06** — see `### F-017` in the log. No longer a reservation. ⚠ Reserved **before** the run, per its own trigger, so the number was settled while the result did not yet exist — it had been claimed twice in one morning and the census orders were corrected to yield it. The entry **cites D-075 and F-004 and amends neither**, and it states the fired Decision-4 row **quoted from the log** before anything else. |
| **F-018** | *An absent status recorded as an affirmative one* — the absent-value rule violated in the **passing** direction | `RULINGS-2026-08-05-task2-task3-contract.md` §4.2, widened by the identity-status, status-wins-over-span, and prose-retirement rulings, 2026-08-05 | **The fix landing.** Scope is **three code sites** — `core/census.py:97` and `scripts/ecd_lengths.py:128` (`or "resolved"`), `scripts/census_spans.py:112` (the `== "resolved"` gate) — **plus `categorise()`'s precedence failure** (a rule that stops firing because its vocabulary moved while its docstring goes on asserting it) **plus four prose sites** carrying retired vocabulary. ⚠ Any CSV lacking a status column would have had every row treated as resolved. Write it when the fix lands, not before. |
| **F-019** | *A SURFY class is a property of the identifier, not of the protein* — two proteins whose source entries disagree with each other about class | `RULINGS-2026-08-05-class-collision.md` §3, 2026-08-05 | **The class-conflict tag shipping.** Measured instance of **A-014**. ⚠ **OVER-CLAIM GUARD, AND IT BINDS: n = 2.** A **mechanism illustration, not a magnitude** — it says the class *can* be identifier-scoped and nothing about how often. ⚠ **It is NOT evidence for F-011's thesis:** F-011 is about how the negative class is *defined*, this is about how an assignment is *keyed* — adjacent, not the same, and P-002's named failure mode is exactly that promotion. **It must not be recruited into any count.** |
| ~~**F-020**~~ | ~~*An absent measurement coerced to zero and fit as though measured* — and a guard that names the defect in its own warning text, then proceeds anyway~~ | ~~`RULING-2026-08-05-STOP-feature-7-not-extracted.md` §3.6, 2026-08-05~~ | ✅ **WRITTEN 2026-08-06** — see `### F-020` in the log. No longer a reservation. ⚠ Reserved 2026-08-05 **before** the fix and written **after** the instrument stopped exhibiting the defect, which is the D-074 order: a finding is not closed when the fix is merged. ⚠ **Its closure evidence is Code's reading of the live database on 2026-08-05, attributed as such in the entry** — not Planner-verified. ⚠ **Still distinct from F-018:** identity path vs fit path, a miscounted census row vs a fabricated result. |
| **F-021** | *A loader that inserts where it must update, rewrites inputs it was not asked to touch, and binds to the most recent run by default* | `RULING-2026-08-05-STOP-feature-7-not-extracted.md` §3.6, 2026-08-05 | **Task B landing.** `scripts/extract_features.py:181` is `session.add(ProteinFeatures(...))` — pure insert, no delete, no upsert, so `--all --load` would have taken `protein_features` from 80 rows to **160 in two generations**; it rewrites features 1–6, so **F-004's stored result would survive while its derivation stopped being reproducible from the database**; and `:173-177` defaults `ranking_run_id` to `order_by(RankingRun.id.desc()).first()`, which is **id=4 (`plddt_only`)**, on a docstring assumption that was true when one run existed and is false now that four do. ⚠ **The remedy for a null-coerced-to-zero defect was itself a command that runs clean, prints a row count, and reddens nothing.** |
| **F-022** | *Independence of source is not independence of inference* — two pre-registrations written separately can agree and both be wrong | `RULING-2026-08-05-igf2r-bare-null.md` §2, 2026-08-05 | **The fix landing.** The Planner pre-registered *"IGF2R the only null, carrying its null-with-reason"*; Code independently pre-registered *"carrying `no residues resolvable from coordinates`"*. **Two sources, written apart, in agreement — and both false.** Both had read the same dry-run line and taken an **extraction-time report** for a **persisted field**; the stored `null_reasons` was written 2026-07-27, before feature 7 existed. ⚠ **This is a real limit on the discipline the 2026-08-05 session leaned on** — *two independent readings* corroborated 0007 twice, the census denominators, and the determinism result, but **when both readers derive an expectation from one upstream artifact, agreement measures only that they read it the same way.** ⚠ **What protected the run was not the second reader; it was writing the expectation down at all** — a false expectation stated in advance is falsifiable, where the same assumption held silently would have made a bare null look normal. Cite beside `A-016 (any red proves the assertion bites)` and `A-017 (the fixture must reach the code under test)`: same family, one level up. ⚠ Found by **both parties agreeing and being wrong**, not by one catching the other. |
| **F-023** | *A `null_reasons` map written before a seventh feature existed, leaving the one feature added later as the only uncategorised absence in the table* | `RULING-2026-08-05-igf2r-bare-null.md` §4, 2026-08-05 | **The F-017 follow-up.** After the Task C fill, `IGF2R` (`analysis_id=57`, `held_out`, `pdb_path IS NULL`) carries reasons for **six** features and **none for feature 7** — the only bare null in `protein_features`, table-wide count of feature-7 reasons: **0**. ⚠ *"An absent value is a category, never a bare null"* is stated **without an in-the-ranking-set qualifier**, and **a singleton anomaly is precisely what gets explained away six weeks later.** The Task C fill is **not** at fault: it writes one column by design, and writing `null_reasons` would have been *"rewrites inputs it was not asked to touch"* — F-021's own defect inside the PR fixing F-021. ⚠ **The reason already exists** — the extractor computes it today and every dry run prints it; it is **persisted, not invented**. ⚠ **D-074: not closed until `protein_features` holds no bare null** — not when the follow-up is written. |
| **A-017** *(the fixture must reach the code under test)* | *A revert proof must confirm the fixture reaches the code under test at all* — the positive control for a test's own fixture | `RULING-2026-08-05-task-A-ratified.md` §2, 2026-08-05 | **KEEL-4 landing.** ⚠ **A generalisation of A-016, not an instance of it.** A-016 says *confirm the red fires at the assertion*; this says **confirm the path was entered** — a red can fire at exactly the right assertion and still prove nothing. Found by Code in its own revert proof: the *"guard after run creation"* revert redded at `DID NOT RAISE` because the fixture had no positives, so `run_scorer` raised `DegenerateLabelSet` and never reached `create_ranking_run`. **The test would have passed under a guard placed anywhere, and it looked like proof.** Remedy shipped as `test_the_fixture_for_the_ordering_test_is_not_degenerate`. ⚠ **NUMBER PROVISIONAL:** `A-` numbering is defined by `KEEL-4-The-Assumption-Register-v1.md`, **which this repository has never received** (see the document-status table below). `A-017` is the lowest integer above every `A-` number known here; **it must be re-confirmed against KEEL-4 at merge**, and `A-015` was deliberately not taken because KEEL-4 is recorded as holding items 15/16/17 and the mapping is unverifiable from here. |
| **F-024** | *A pattern that occurs more than once, matched without a uniqueness check, takes the wrong occurrence* | `ORDERS-Code-2026-08-06-relocate-and-resume.md` §Task 2, 2026-08-06 | **Task 1's disposition — now known: the terminator was AD-HOC and is retired, so the instrument cannot exhibit it (D-074 satisfied). Writable; queued behind the tranche column.** ⚠ **Five dated instances, two agents, one day, one remedy.** (1) #123 header detection took the template **quoted inside** `RULING-2026-08-05-D-079-denominators-in-the-log.md` §3. (2) #129 header detection — the same file, the same way, again. (3) Query 2's `15` took the fifth `
---

### `, four entries downstream — **miscounted only.** (4) `e41ce85`'s insertion point — **the same fifth occurrence, and this one WROTE**, appending the Run B pre-registration into `### D-071` instead of `### D-075`. (5) The Planner's *"a different header by design"* read the **adjacent** sentence, *"Short by design"*, as the intended one. ⚠ **Four of the five were false positives that looked like confirmations.** The remedy is identical across all: **assert the match is unique, or anchor on something that is** — which is why `4ad9b02`'s unique-anchor replacement landed correctly while everything else that day did not. ⚠ **NOT an instance:** the `
---` boundary swallow in the first relocation attempt. That scan found the **right occurrence and took the wrong boundary** — adjacent mechanism, different remedy; recruiting it would inflate this row with something it is not (F-019's over-claim guard). ⚠ **Recorded here, separately, and explicitly NOT a sixth instance:** *a verification that shares an implementation with the thing it verifies will agree with it* — `e41ce85`'s check reported *"appended INSIDE the D-075 entry: True"* computed with the same broken terminator. **This is F-022's next level:** F-022 was two readers deriving from one artifact; this is a check importing the code under test. **Different remedy — F-022's was write the expectation down; this one's is the check must not share code with the code under test.** Unnumbered pending the owner's ruling on findings numbering. |
| **A-014** *(an upstream model’s negative class is a prediction, not a fact)* | *An upstream model's negative class is a prediction, not a fact* — the assumption F-011 catches | Planner, 2026-08-04 | **KEEL-4 landing.** ✅ Re-verified 2026-08-04 against the received F-011 v2, which cites it as *"reserved in `RESERVED.md`, unwritten until KEEL-4 lands against v6"*. ⚠ **KEEL-4 still not received by Code** — the only one of the four staged documents still missing. |
| **A-016** *(any red proves the assertion bites)* | *Any red proves the assertion bites* — the corrected red-then-green formulation | `PAPERS-v2.md` P-001, 2026-08-04 | **KEEL-4 landing.** Cited as the register entry behind P-001's methods-section correction: an error-red and a failure-red are different objects, the revert must be a realistic mistake, and it must fail at the assertion. Originates in the guard Code caught reddening as a collection error (F-012 session). |

---

## ⚠ Reserved WITHOUT a number — CLEARED 2026-08-16

> **This section is kept, empty of live entries, rather than deleted.** ⚠ An empty holding pen is a
> finding — *"the queue was worked through"* — where a removed section reads as *"there was never
> one."* Same rule as an empty band key versus an omitted one.

**Seven were written as `### F-026` … `### F-032` on 2026-08-16.** ⚠ **The owner's instruction was
to fan out to *the seven that actually occurred*, so the queue was filtered rather than transcribed:**

| written | finding |
|---|---|
| `F-026` | a verification sharing an implementation with its subject |
| `F-027` | derive from source, not from context |
| `F-028` | an order asking for confirmation invites confirmation |
| `F-029` | `assert` used as a guard vanishes under an optimisation flag |
| `F-030` | the unsafe branch was the default, reached by omission |
| `F-031` | two populations in one table, joined on a key no longer unique |
| `F-032` | a dry run that does not exercise its consumer's contract |

### ⚠ Two were NOT numbered, and the reason is recorded rather than left to inference

| not numbered | why |
|---|---|
| **The KEEL absence** | ⚠ **A missing document, not a defect that fired.** `KEEL-4-The-Assumption-Register-v1.md` has still never been received, and **`A-014` and `A-016` remain blocked on it**. It is a dependency, and it stays in *Status of the documents this register depends on* below — where a reader looking for missing inputs will find it. |
| **The `P0DKB6` yeast vocabulary** | ⚠ **Resolved, and resolved to cosmetic.** The organism check closed the serious branch: `MPC1L` is *Homo sapiens* `taxonId 9606`, reviewed Swiss-Prot, so **no non-human row is in the census, no denominator moves, and *"7,811 human proteins"* stands.** What remains is an ortholog-transfer annotation artifact that **changes no count** — `Cytoplasmic` and the mitochondrial terms are rejected regardless. It is ruled in `core/span_definition.py`'s `REJECTED_TERMS` and visible in the census glossary. |

### ⚠ And one that occurred TWICE today and was deliberately NOT numbered

**A guard placed downstream of the filter it guards watches nothing.** It fired on the VRAM overrun
guard (placed after the selector, so it stopped watching exactly the rows the selector excluded —
the rows it existed for) and on `check_sliced_length` (which, had it run only on the sliced branch,
would have gone green on 3,468 whole-sequence folds).

⚠ **Not numbered because the instruction was seven, and taking an eighth integer under momentum is
the `F-025` defect repeating.** It is recorded here so the next numbering ruling has it in hand.

---

## ⚠ F-025's provenance defect, recorded because the number was right by luck

**`### F-025` was claimed in commit `ba1e687` and in PR #133 on the strength of a chat message, and
it appeared NOWHERE in this register, the log or `ARCHITECTURE.md` at the time** — zero occurrences.

⚠ **The integer happened to be free.** Highest written was `F-020`; `F-021`–`F-024` were
reserved-unwritten; `F-025` was genuinely next. **So the outcome was correct and the procedure was
not**, and *"a Planner chat message cannot ratify what a committed document reserved"*
(`RULINGS-2026-08-07-span-definition.md` R5) is what made it correct rather than merely lucky.

**The register is now in step with the log**: `F-001`–`F-012`, `F-016`, `F-017`, `F-020`,
`F-025`–`F-032` written; `F-013`, `F-014`, `F-015`, `F-018`, `F-019`, `F-021`–`F-024` still
reserved-unwritten below. **`F-033`** (selenocysteine absent from the ESM vocabulary) **was written on 2026-08-16.** **`F-034`** (a verification harness that would have exceeded the fold ceiling) **was written on 2026-08-16.** **`F-035`** (tier routing computed but never enforced at claim time) **was written on 2026-08-16, owner-ruled a finding.** **`F-036`** (an unfetched row carries an empty `span_category`) **was written on 2026-08-16.** **`F-037`** (`span_aa` is the largest extracellular segment, not the extracellular content) **was written on 2026-08-16.** **`F-038`** (a census page displayed the cohort's measured ceiling) **was written on 2026-08-16.** **`F-039`** (staged documents claiming spent numbers) **was written on 2026-08-17.** **`F-040`** (single-chain / oligomer interface) **was merged on 2026-08-17**, as were **`D-093`** (clinical association layer) and **`D-094`** (claim discipline). **`F-041`** (two of three candidate boundary sources supply no boundary; InterPro supplies no count) **was written on 2026-08-17** and is **OPEN** — it is a property of the instrument. **`D-095`** (tranche 6 as tiling) **was written on 2026-08-17** and is ⚠ **PROPOSED, not ruled.** **`D-096`** (the ADC mechanism graphic becomes a raster illustration) **was written on 2026-08-17** and is **accepted**, then ⚠ **superseded in part the same day by `D-097`** (both graphics stay — the schematic is anatomy, the cartoon is process), which is **accepted**. ⚠ **D-096 was NOT amended away**; it records what shipped in `061eb3f`. **`D-098`** (tranche 6 scoped to the 141, superseding the scope clause of `D-091` ruling 3 and of `D-095`) **was written on 2026-08-17** and is **accepted** — ⚠ **merged at `D-098` after the owner ruling claimed `D-095`, which was already spent; the ruling's own "confirm against the live log" instruction is what caught it.** **`D-099`** (the control fold is not tranche 6) **was written on 2026-08-17** and is **accepted**. ⚠ **`F-042` is RESERVED, not written** — it is the owner's to draft and is cited by `D-099`; see the reservation table above. ⚠ **Next free `F-` integer: `F-043`. Next free `D-` integer: `D-100`.**

---

## Named deferrals — known, recorded, not built (D-074 dec 3)

> **Not reservations.** These carry no `D-`/`F-`/`A-` number and announce nothing forward. They are
> things this project knows about itself and has decided not to fix yet. ⚠ **The point of naming them
> is that an unnamed limitation reads as an oversight to the next reader, and an oversight gets
> "fixed" by someone who does not know why it is there.**

| Deferral | Recorded | What it costs |
|---|---|---|
| **Pagination is named, not built** — `list_analyses` is unfiltered and unpaginated | Census orders §1c, 2026-08-05 | Nothing while `protein_analyses` is the 82-row cohort. ⚠ Becomes load-bearing the moment the census is ingested. |
| **`fly-user` cannot read other sessions in `pg_stat_activity`** on Managed Postgres — returns one row, `<insufficient privilege>` | Owner + Code, 2026-08-05 | **Lock diagnosis via that route is unavailable.** Expect it again; do not read an empty result as "no other sessions". |
| **`db/migrations/env.py` sets no `connect_timeout`** | Owner + Code, 2026-08-05 | A half-dead tunnel **hangs indefinitely** where `scripts/dev_check_db.py` fails in 10 s. Not what happened on 2026-08-05 — the 0007 apply had already committed when its terminal appeared to hang — but the hazard is real and the two look identical from the keyboard. |
| **`--fill-feature-7` reports `N written` where `written` counts rows *assigned to*, including one assigned `None`** | Code, 2026-08-05 | The Task C write printed **`80 written`** while **79** rows received a value; `IGF2R` was assigned `None`. ⚠ **A true number that answers a different question than it appears to answer** — 2,886's shape, one table down. A tighter report reads *79 valued, 1 null-with-reason*. Closes with **F-023**. |

### Run B's four free parameters — CLOSED, and where to find the ruling

`### D-075` Decision (3) and Decision (4)'s matching rows were frozen before Run A and left **four
free parameters** open: *which* ablated score Run B re-ranks · *covariate-adjust **or** stratify* ·
what *"still enrich"* operationally means · and what happens when a proxy lookup fails.

**All four are closed** in `#### ⚠ RUN B PRE-REGISTRATION — four free parameters closed, 2026-08-06`,
appended to `### D-075`. Recorded here because an amendment at the end of the project's longest entry
is otherwise discoverable only by reading D-075 to its end.

⚠ **When they were closed, and the honest form of it:** ruled **after** Run A returned Decision 4
row 1, and **before any attention-proxy value existed** — `--freeze` was a deliberate stub,
`data/attention_proxies.json` did not exist, and no proxy had ever been computed for any target.
**The protection is that the data did not exist, not that the ruler was ignorant of Run A.** The
second would be false; the first is checkable, and the window closes permanently the moment the
wiring PR merges.

⚠ **The exclusion thresholds are recorded as arbitrary** — 0 excluded reports normally, 1–2 is
reportable with the targets named and the analysis repeated on the reduced set, 3 or more is **VOID**.
**An arbitrary threshold fixed before any pull is legitimate; the same number chosen afterwards is
not.** That difference is the entire reason the block exists.

---

### ⚠ Hash discipline: compare on normalised line endings

`git`'s `LF→CRLF` conversion on checkout means a document's committed bytes differ from its delivered
bytes — observed 2026-08-05 on `RULING-2026-08-05-A017-and-task-C-protocol.md`: **0 CRLFs delivered,
106 committed**, content byte-identical after normalising.

**Ruled:** hash comparison for text documents is performed **on `LF`-normalised bytes**. A raw-byte
mismatch that resolves under normalisation is **recorded, not escalated**; one that survives
normalisation is **stop-and-report, unchanged.**

⚠ **The reason is not convenience.** *"Hash before use, a mismatch is stop-and-report"* is
load-bearing on a channel that failed **three times** on 2026-08-05 — one document never arriving
across two reports, and another arriving twice. **A rule that raises a false alarm on every text
document trains its readers to ignore it, and that is how a real mismatch gets waved through.**

---

## Status of the documents this register depends on (D-016)

Four documents were unreceived when this register was created, so the F-011 and A-014 rows were
sourced from `AMENDMENT-2026-08-04-code-feedback.md`'s *description* of them — the pointer-not-proof
shape (method-note item 7) — and were flagged for re-verification. **Three have since arrived and
the flag is discharged:**

| Document | Received | Outcome of re-verification |
|---|---|---|
| `ORDERS-Code-2026-08-04-surfaceome-spans-v2.md` | ✅ 2026-08-04 | Re-issue; **byte-identical** to the 10:37 copy already in `docs/`, so no re-analysis was needed. |
| `F-011-surfaceome-negative-class-v2.md` | ✅ 2026-08-04 | **Matches the reservation.** Also *strengthens* the caution: it labels its own 2,216 and ~5,102 as unverified. |
| `PAPERS-v2.md` | ✅ 2026-08-04 | Introduces **A-016** (now reserved above) and the `P-NNN` paper namespace (P-001/P-002/P-003), which live in `PAPERS-v2.md`, not in the decision log. |
| `KEEL-4-The-Assumption-Register-v1.md` | ❌ **still missing** | Defines `A-` numbering and holds assumption items 15/16/17. **Both A-014 and A-016 are blocked on it**, and neither can be written until it lands. |

### ⟡ One number re-counted rather than inherited

F-011 v2's single verified figure was **re-counted from the file** rather than accepted: `surfaceome_ids.txt`
holds **2,886 non-empty lines, 2,886 unique** — confirmed. And a detail the entry states more softly
than the data supports: **0 of 2,886 are accession-shaped** and 2,886/2,886 carry `_HUMAN`, so the
entry-name-versus-accession mapping hazard is **total, not partial**. Every join in this project is
keyed by accession.

The membraneome table remains an **LFS pointer stub** — 132 bytes declaring
`oid sha256:2f1b8262…`, `size 6864772`, which matches what the spans order expects and therefore
confirms *which* file is wanted while proving the content is absent. **The negative class — the
subject of F-011 — has still never been counted.**

---

## Retired reservations

*(none yet — when a reserved number is abandoned rather than written, it moves here with the reason,
so a future reader can tell "abandoned" from "forgotten".)*
