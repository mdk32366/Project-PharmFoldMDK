# AMENDMENT — 2026-08-19 — Planner's three log entries: `D-095 amendment 1`, `F-044 amendment 1`, `F-047`

> **COMMITTED to `docs/` as provenance. CITED BY the log, not restated in it — where this file and
> `docs/README.md` differ, THE LOG GOVERNS.** ⚠ This file records how a decision was reached; it is
> not itself authority. Check the `### F-NNN` / `#### D-NNN amendment` header, not a reference to it.
>
> ⚠ **LANDED, not authored here.** Received 2026-08-19 from the Planner. The three entries below were
> merged into `docs/README.md`: **`F-047` as a new top-level entry** at the head of the log, and the
> two amendments as **sub-entries beneath their parents** (`### D-095`, `### F-044`), on the
> `D-099 amendment 1` / `D-093 amendment 1` precedent. **Only `F-047` consumed an integer.**
>
> ⚠⚠ **THE `sha256` BELOW IS NOT "AS RECEIVED", AND THE DIFFERENCE MATTERS.** `F-047` member 3's
> remedy — *`sha256` as received, stamped by whoever lands it* — **assumes a file changes hands.**
> This document arrived as **chat text, not as a file**, so no received artefact exists to hash.
> **`sha256` of the entry body as transcribed and landed: `0cb1084b923ddb29256916635c4057eee68c20035d239dc84301cc8672cd81ea`.**
> That proves what was landed; it does **not** prove it matches what was sent. ⚠ **A weaker claim,
> labelled as one** — the member bit the landing of its own entry, and that is recorded in `F-047`.
>
> ⚠ **Code's landing notes are appended inside each entry**, marked `LANDED BY CODE`, and change no
> Planner text. One imprecision in `D-095 amendment 1` item 1 is reported there rather than edited.

> ⚠⚠ **THE AUTHORED-HASH CONTRACT (`BB1`–`BB3`), and it records a MISMATCH rather than resolving one.**
>
> ```
> AUTHORED-SHA256: 2d25c6dfc154e36cc0b3b0ad7bf60efb3c835c96893275673464c7dcfd478e4a
> HASH-RANGE: #### D-095 amendment 1 -> EOF
> LANDED-SHA256: 0cb1084b923ddb29256916635c4057eee68c20035d239dc84301cc8672cd81ea
> HASH-MATCH: no
> ```
>
> ⚠ **The mismatch is EVIDENCE ABOUT THE CHANNEL AND ABOUT THE LANDER, and it does not resolve to
> either.** As landed the range is **19,212 bytes** against the authored **18,028**; with Code's
> three `LANDED BY CODE` bullets removed it is **17,597**, still **431 short**. ⚠⚠ **Code reflowed
> the Planner's hard-wrapped lines when transcribing, which accounts for at most ~284 of those 431
> — so roughly 150 bytes remain unexplained and CANNOT be attributed.** The hash cannot separate
> channel loss from transcription because the lander did not preserve bytes.
>
> **The finding that follows: an authored hash is only informative if the lander transcribes
> verbatim, line breaks included.** The contract is sound; this landing did not meet its
> precondition, and that is recorded rather than smoothed.

---

#### D-095 amendment 1 — ⚠⚠ The design document is about TILING AT GAPS with a six-row exception, not about cutting cadherin stacks — and `merge_rule` manufactures the problem it exists to solve

- **Date:** 2026-08-19 · **Status:** ⚠ **`D-095` moves PROPOSED → RULED.** `D-091 (tranche 6 design gate)` ruling 3 requires *written **and** ruled*; this amendment discharges the second half. **Tranche 5's 776 rows are released from the design gate by this entry and remain held by `D-091` ruling 2 (rental spend) alone.**

- **Why an amendment and not a rewrite.** `D-095` was written on ten subjects before four things were known. ⚠ **Every correction below is recorded against the original text rather than replacing it** — the run/domain error preserved in the script's `merge()` docstring is the precedent, and the document's most important structural fact came out of that preservation.

- ⚠⚠ **1 — THE HEADLINE IS INVERTED.** **135 of 141 tile at gaps and sever nothing; 6 need exactly one `run_interior` cut each.** `D-095` reads as a document about severing cadherin stacks and is a document about tiling at natural seams with a six-row exception. **The exception is real and it is an exception.**

- **2 — The population is the 141**, per `D-098 (tranche 6 scoped to the 141 past-context rows)`, not the ten that motivated it. ⚠ **Key, stated once and carried everywhere below: one row per `census_accession`, `tranche = 5` AND `span_aa > 1026` strictly.**

- **3 — Decision 1's stated basis is CORRECTED; the choice stands.** *"Chosen by availability"* expired when Task A2 fetched the InterPro **matches** API — **10,592 boundaries with coordinates**, the instrument `F-041 (two of three candidate boundary sources cannot supply a boundary)` named as missing. ⚠ **`F-041`'s deeper point carries the choice instead, and it is the stronger reason: the disagreement is between MODELS, so no arbiter exists** — `ECO:0000255` on **416 of 521** features, `ECO:0000269` **zero times**, and best exact boundary agreement anywhere **58.0%**, which **moves with the type filter** (58.0 / 55.8 / 47.0 at k=0). **A source chosen because no source can be right is a different claim from a source chosen because it was to hand, and only one of them survives a reader.**

- ⚠⚠ **4 — `merge_rule` IS A RULED DECISION, NOT A RECORDED PARAMETER — and it manufactures the problem this document exists to solve.** The shipped rule stands: **abutting OR overlapping**, `start <= prev_end + 1`.
  - **The counterfactual, and it is why the rule is ruled rather than recorded.** Under **overlapping ONLY**, `rows>ctx` is **0** — under all three straddle rules — and FAT1 is **39 runs, not 9.** ⚠ **The entire tiling problem exists because abutment is joined.**
  - ⚠⚠ **But overlapping-ONLY does not REMOVE the cut. It RELABELS it.** The 141 are past context **by span**, so tiles are required under every merge rule and `tile_max_aa` binds either way. FAT1's cuts would then land at abutting boundaries — `35-149 | 150-257`, **a gap of ZERO residues** — and be filed as `gap` or `domain_boundary` instead of `run_interior`. **The molecule is severed identically and the artifact stops saying so.**
  - ⚠ **Under `D-094 (claim discipline in educational surfaces)` the `run_interior` disclosure is a MOUNT PRECONDITION.** Overlapping-ONLY would extinguish the precondition while leaving the hazard exactly where it was. **That is the ruling's whole basis.**
  - ⚠ **Without this counterfactual in the entry, item 1's headline is a CONSTRUCTION presented as an OBSERVATION** — the 275-residue shape one level up. *Code's framing, adopted.*

- **5 — Gap tolerance is ZERO uncovered residues, and the artifact records `0`.** ⚠ **Not the expression.** `start <= prev_end + 1` reads as a tolerance of one residue and **is not one** — the `+ 1` is an artifact of inclusive coordinates. **100–200 and 201–300 join; 100–200 and 202–300 stay two runs. One uncovered residue is enough to split.**

- **6 — `straddle_handling = CLIP`, and it is ruled FOR ONE-SIDED OVERHANGS ONLY.** Recorded on every derived artifact beside `merge_rule` and its gap tolerance. ⚠ **Three unstated parameters were found on one derived object in two days: a run is a construction, not an observation.**
  - **CLIP moves nothing in this population's decisions.** Set-identical six under clipping; **2 of 141 rows change at all** — `Q9Y493`/ZAN `n_domains` 16→17, `Q6V1P9`/DCHS2 25→27 with `largest_run` 832→847, leaving DCHS2 **179 aa short of context.** **139 rows byte-identical.**
  - **Two paths to one quantity, compared on the numbers:** clipped Task L gives **180,802 / 91,500 / 33.6%**, reproducing `tranche6_domains.uniprot.csv` **to the residue**. **CLIP − DROP = 275. Exact.**
  - ⚠⚠ **THE ENGULFING CASE IS A DISTINCT CATEGORY AND IS EXPLICITLY NOT RULED.** CLIP's stated reason — *a clipped straddler occupies its residues; dropping it manufactures a gap at the span boundary that does not exist in the molecule* — **is about EDGES. An engulfing feature has no edge inside the span, so the reason does not reach it.** Clipping one would assert that the span **is** the domain. **`clip` therefore REFUSES it** (`UnruledEngulfingFeature`) rather than assuming: **0 in the 141, 58 in the census.** See **`F-048`**.

- ⚠ **7 — `tile_max_aa` is a SPEND DECISION and `D-095` nowhere says so.** `known_good = 440` at int8 against a trained context of **1,026** means **every tile over 440 aa needs a rental card** — and **`D-091` ruling 2 holds all rental spend.** ⚠ **Tiling does not avoid rental; it changes the bill.** **The number is measured, not proposed** — `F-034`'s lesson, and `1,000` was never folded.

- **8 — `tile_cut_kind` gains a fourth value, `run_interior`** (owner ruling). FAT1–4 stay **in scope** and are folded, **with the cut made legible from the artifact alone.** ⚠ Under `D-094` its disclosure is a **mount precondition, not a caption** — this is the first surface built *under* `D-094` rather than retrofitted to it.

- **9 — The five-regime table, with its zero printed.** `all_runs_in_context` **123** · `no_domains` **10** · `one_oversized_run` **6** · `single_run_only` **2** · `multiple_oversized_runs` **0** = **141**, identically under both straddle rules. ⚠ **`multiple_oversized_runs` is kept as an unfirable branch carrying its zero: an empty category is a measurement; a deleted one reads as *we never looked*.**
  - **`single_run_only` is `Q8TEM1`/NUP210 (largest run 74) and `Q9NTG1`/PKDREJ (699)** — both far inside context, **disjoint from the six, not a subset.**
  - ⚠⚠ **The disjointness is a DATA FACT WITH A NAMED RISK, never a proof.** `classify_regime` tests `len(runs) == 1` **before** counting oversized runs, so a one-run protein whose single run exceeded context would be filed `single_run_only` and **silently vanish from the six.** **Rows in that state today: 0, under all three straddle rules — reported, not omitted.**

- **10 — The founding measurements are RULE-INVARIANT, and the reason is narrower than it looks.** **FAT1 = 2,289 aa and FAT4 = 3,037 aa under `admit_raw`, `drop` and `clip` alike** — ⚠ **because none of the ten carries a straddling domain at all** (0 / 0 / 0). **The rules do not agree on a hard case; the ten contain no hard case.** **No founding number needs amending, and the claim that survives is the narrow one.**

- **11 — `D-095`'s evidence script is re-cited AT A REVISION**, and the claim is stronger than expected. `scripts/tranche6_domain_survey.py` was reconciled at `fc8040c`; ⚠ **its stdout is byte-identical pre and post, `aad52b28a7eac3f471666eebaf729eb201526da77e714eac368f7aaef2711cd3`.** **So the entry does not say *the script changed* — it says *the evidence script's output is unchanged, and here is the hash.*** ⚠ **The comparison could not be made the same way for `scripts/tranche6_runs.py`** — the pre-change file cannot run against the post-change module, which is the missing-`straddle` `TypeError` **working as designed.** **An absence with a cause, not an untested path.**

- **12 — The divergence this amendment was measured across is disclosed, not smoothed.** Three straddle predicates lived under one function name; the numbers above were taken **against the divergent code at `7011e24`** and the code was reconciled afterwards at `fc8040c`, in a separate commit. **See `F-046`.** ⚠ **You cannot measure a divergence you have already removed.**

- **Deep-learning justification, unchanged and reinforced:** the trained context is a property of the **model**, not of the hardware, so tiling is a modelling decision about what the network was trained to represent. ⚠ The document's central claim — **that per-tile confidence is not composable into a whole-molecule confidence** — is a statement about what the predictor actually outputs, and it is what stops a tiled artifact being read as a 4,000-residue prediction.

- **Assumptions relied on:** `A-014 (an upstream model's negative class is a prediction, not a fact)` — twice, since both the boundary source and the surface filter are model outputs.

- **Evidence:** `scripts/tranche6_runs.py` · `scripts/tranche6_domain_survey.py` · `scripts/tranche6_runs_clip_compare.py` · `data/census/tranche6_runs.csv` · `data/census/tranche6_domains.uniprot.csv`. **Commits `7591164`, `fc8040c`, `59b2624`.**

- ⚠ **LANDED BY CODE, 2026-08-19.** Verbatim from `docs/AMENDMENT-2026-08-19-planner-log-entries.md`. **One imprecision is reported rather than silently edited:** item 1's *"135 of 141 tile at gaps"* is `141 − 6`, and **10 of those 135 are the `no_domains` rows**, which have nothing to tile at — assembly there is **undefined, not seamless** (item 9 prints the 10 separately, so the entry is internally consistent; the headline sentence alone is not). **`135 sever nothing` is exact; `135 tile at gaps` over-reaches by the 10.**

---

#### F-044 amendment 1 — ⚠⚠ A Planner instance: the reserved row's CLASS matched, its INSTANCE did not, and the pointer that would have shown it was never followed

- **Date:** 2026-08-19 · **Status:** the finding stays **OPEN** — `D-074`: a finding against an instrument stays open until the instrument no longer exhibits it. **This is the instrument exhibiting it, one day after the entry was written.**

- **What happened.** The Planner directed that the `domain_intervals` divergence be written as **`F-014`**, quoting that reservation's text — *"documenting a duplication is not managing it — the tenth instance of the two-paths-to-one-quantity class, and the first where the drift was written down and the writing-down substituted for the fix."* **The class description matched exactly.**

- ⚠⚠ **`F-014` is reserved for a different instance.** `AMENDMENT-2026-08-04-code-feedback.md` §160–165 reserves it for **`scripts/ecd_lengths.py` carrying a hand-duplicated `CEILING_KNOWN_GOOD`/`CEILING_KNOWN_BAD` while `core/manifest.py`'s comment documented the duplication.** `ARCHITECTURE.md:693–697` records that instance **already fixed and guarded** by `tests/test_manifest.py::test_no_second_copy_of_the_ceiling_survives_in_the_tree`.

- ⚠ **The specific failure, and it is sharper than a misread.** `RESERVED.md`'s row carries **two** columns — the class description **and** a pointer, *"Amendment §7, 2026-08-04"*. **The Planner read the description and never followed the pointer.** It then **ordered Code to check the reservation's RELEASE CONDITION** (*held until `d077-local-fold-envelope` merges*) — ⚠⚠ **so it verified the half that had a check and asserted the half that did not.** *Pointer-is-not-proof, one day after writing the rule against it.*

- **Caught by Code**, who followed the pointer and reported the mismatch rather than writing what was ordered. ⚠ **`F-014` remains RESERVED and untouched;** the divergence took `F-046`.

- ⚠ **What this adds to `F-044`.** The original entry establishes that the citation invariant proves a reference **resolves**, never that it resolves to the **right thing**. **This instance shows the same hole in a `RESERVED.md` row**: the whitelist proves a number is legitimately unwritten and has no access to **what it was reserved for.** **The remedy is the one already ruled — cite by number AND name — extended to reservations: a reservation is cited by number and INSTANCE, never by class.**

- ⚠ **LANDED BY CODE, 2026-08-19.** Verbatim from `docs/AMENDMENT-2026-08-19-planner-log-entries.md`. **The release condition itself was verified and holds:** `d077-local-fold-envelope` merged as PR #122 at `d6622f9`, 2026-08-05, an ancestor of both `main` and `HEAD`, with **0** commits unmerged. **So `F-014` is writable today — for its own subject, which is not this one.**

---

### F-047 — ⚠ The wrong-but-plausible answer: the defect class where nothing errors, nothing is malformed, and the number is wrong

- **Date:** 2026-08-19 · **Status:** ⚠ **OPEN and STANDING.** It accumulates members; it does not close.

- **The shape.** A query, a guard, a grep or a report returns a **well-formed, correctly-typed, plausibly-sized answer that is wrong** — and **nothing objects.** ⚠ **This is not an error class. Errors announce themselves. This class is defined by its silence**, and it is `F-011`'s *plausibility, not error, is the failure mode at scale* applied to the instruments rather than to the data.

- ⚠ **Already doctrine, and the entry cites rather than re-derives it.** **KEEL-1 V9 Principle 8's fifth clause** names it: *"be most suspicious of the well-formed answer: an empty result from a mismatched key, a zero from a stale connection, a 405 read as a 404. In every one of those the wrong answer arrives correctly formatted, and nothing objects."* ⚠⚠ **Three of that clause's examples are this project's own scars.**

- **The members, and THREE OF SIX ARE PLANNER-MADE. That is the point of the entry.**

  1. ⚠⚠ **The `50` that should have been `58`** *(Planner, 2026-08-19)*. The ruling on the engulfing category **quoted a count measured under the strict-both convention while simultaneously ruling the at-or-before / at-or-after convention.** 4 features sit flush at `s0`, 4 flush at `s1`; **those 8 are exactly what the convention moves.** ⚠ **The hazard fired inside the order that commissioned the check for it** — the same order wrote *"which side it falls on is a choice, not a fact."*
  2. ⚠⚠ **The `## P-004` grep** *(Planner, 2026-08-19)*. Written as a guard against a **false collision** (`P-00[0-9]` returns `DEP-004`/`DEP-005`), it **manufactures a false absence**: P-003 and P-004 carry `⟡`, so their headings are `## ⟡ P-003 —` and `^## P-00` **excludes exactly the two entries the check is about.** The result reads *P-003 is cited with no entry* — clean, confident, false. **Committed in `docs/PREWORK-2026-08-19.md` §2b; corrected by a landing note beside it, the instruction not edited.** ⚠ **Code's own record of the catch: *luck of ordering, not a control.***
  3. ⚠⚠ **`COMMITTED to docs/ as provenance`, false on four documents** *(Planner, 2026-08-19)*. Four `ORDERS-Code-2026-08-19*` files each assert their own provenance in their header and **none was in the repository.** ⚠ **A document asserting its own provenance cannot be falsified from inside itself** — the sharpest member of the pointer-is-not-proof family. **Cause: paste to Code and commit to repo are two acts, and the header claimed the second because the first had happened.** **Remedy, structural rather than documentary:** the author writes **`TO BE COMMITTED`**, and the landing header — received time, `sha256` as received, and the note that only the header differs — **is stamped by whoever lands it**, on the `ORDERS-Code-2026-08-18-tranche-6-premeasurement.md` precedent. **The author no longer makes the claim, so the author cannot make it falsely.**
  4. **The `−18 / +4 / −39 / −2` byte deltas** *(Code, self-caught)*. Four true numbers offered as evidence that the re-verification covered the `.pyc` collision. ⚠ **They describe a different driver, in a different file, at different sizes** — the colliding pair was `a < s0 → a <= s0` and `b < s0 → b <= s0`, both **`+1`**. ⚠⚠ *A clean number meaning something other than it appears to, inside the report of a finding about exactly that.* **See `F-045`.**
  5. **The sum-to-sum partition check** *(Code, self-caught)*. A partition validated by comparing its total to itself — **a tautology that could not fail.** ⚠ **A partition that checks only its total is not checked.** Replaced by a per-cause reconciliation: **2,033 + 215 + 21 + 58 + 0 = 2,327**, and **2,327 + 1,140 = 3,467.**
  6. **The prior catalogue** (`PREWORK-2026-08-19` §3): a **case-mismatched join returning a clean zero three times** · a **`Staged` secret answering `0` rows** where a restart does not apply it · a **`405` read as a `404`** · **five wrong files in one day, every one real, well-formed, correctly-schema'd data from the right organisation.**

- ⚠⚠ **THE DENOMINATOR IS UNKNOWN AND THIS ENTRY MUST NEVER REPORT A RATE.** Every member above was **caught**. An instance that was never caught leaves no trace by construction — that is the definition of the class. **This is survivorship and must be labelled as such wherever it appears**, exactly as `KEEL-4 V9` §6 requires of the assumption score. **What six members do establish, with no denominator: when this project went looking, it found them. Enough to justify the instrument, and not enough to justify a percentage.**

- **What actually catches this class, from the members rather than from theory:**
  - ⚠ **A declared length beat a checksum.** Two passages arrived with corrupted `sha256` values; the **stated byte counts** (149 → 120, 289 → 259) caught the corruption the hashes could not.
  - **Reconcile both directions and per-cause, never total-to-total.**
  - **Reproduce a known-good subset** — `D-100`'s 337/337 and 1,303/1,303, `M4`'s six reported **as accessions rather than as a count.**
  - ⚠ **Make the check able to fail on the corpus it runs against.** `F-046`'s invisible inequality and `F-045`'s self-check that fails when the disagreeing-span count is zero are the same move.

- **Relied on by:** `F-044` · `F-045` · `F-046` · `F-048` · `D-095 amendment 1`.

- ⚠ **LANDED BY CODE, 2026-08-19.** Verbatim from `docs/AMENDMENT-2026-08-19-planner-log-entries.md`, which releases this number from `docs/RESERVED.md`. ⚠⚠ **One member of this entry bit the landing of this entry.** Member 3's remedy — *`sha256` as received, stamped by whoever lands it* — **assumes a file changes hands.** This document arrived as **chat text, not as a file**, so **no received-artefact hash exists to record**, and the hash in the landing header is of **Code's transcription**, which is a strictly weaker claim: it proves what was landed, not that it matches what was sent. **The remedy is sound and its precondition was not met. Recorded rather than papered over.**
