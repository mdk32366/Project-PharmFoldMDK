# PASTE-READY — `F-047` amendment 1 — for `docs/README.md`

**AUTHORED-SHA256** (range: **first `####` header → EOF**, anchored to line starts, no newline
normalisation) = `b4216d5095a7e230c9bf4ab28d55b9e22322949d4e5bcc327756871a7eea8bba`
**bytes** = `7171`

> ⚠ **DOWNLOAD AND COMMIT. DO NOT RETYPE.** A sub-entry — **no integer** — beneath `### F-047`,
> before the next `###`.
>
> ⚠ **Test the invariant BEFORE merging, from the SET.** Numbers cited: `D-041` `D-064` `D-092`
> `D-093` `D-100` `F-005` `F-006` `F-020` `F-044` `F-045` `F-047` `F-049` `P-001` `P-004` `A-014`.
> ⚠⚠ **`F-049` is the one to check** — if it has landed it is in the set; if not, this entry cites an
> unwritten number and **that is the invariant working, not a failure.**

---

#### F-047 amendment 1 — ⚠⚠ Eight more members in one day, ELEVEN of twenty-one now Planner-made — and the catch rate, not the count, is the finding

- **Date:** 2026-08-19 · **Status:** `F-047` stays **OPEN and STANDING.** It accumulates; it does not
  close.

⚠ **Why an amendment rather than a rewrite:** the original entry's six members stand unchanged. **A
class entry that is edited to look tidier loses the thing that makes it evidence — that the members
arrived one at a time, in the course of ordinary work, and that most were caught by someone other
than their author.**

---

**14 — ⚠ The Planner asked a question the log had answered three weeks earlier.** *(Planner)*
It opened a scoring discussion asking whether the fitted scores are calibrated probabilities or an
ordering. **`F-006` (2026-07-29) already ruled: *the fitted scores are compressed toward the base
rate, and are not calibrated probabilities* — min 0.116, median 0.220, max 0.285, n 56.** ⚠ **Not a
wrong answer: a confident question built on `D-041` and `core/features.py` with no search of the
findings.** **Same root as the rest of the class — reasoning from a partial read that produced
something well-formed.**

**15 — ⚠⚠ `core.autocrlf=true` would have broken every authored hash on a fresh clone.** *(Code,
caught BEFORE it fired)*
Git rewrites LF→CRLF on checkout, so a clone's bytes differ from the commit's and **the verification
guard would have reported corruption on files nothing had touched** — ⚠ **a guard manufacturing its
own failure signal, indistinguishable from the channel corruption it was built to detect. We would
have chased the channel.** **No `.gitattributes` existed; one was added, scoped to the four files,
and proven by round-tripping each through git's own checkout filter.**
⚠ **The only member so far caught before producing a wrong answer rather than after.**

**16 — ⚠⚠ An order cited an artifact in the present tense before it existed.** *(Planner)*
`ORDERS-Code-cancer-surface-attribution.md` §0 stated the licence text *"is landing as
`docs/HPA-licence-2026-08-19-as-read.md`."* **It was not in the repository and had never been
created**, so **`D-093` amendment 3's entire licence finding cited an artifact that did not exist.**
⚠ *A commit message naming a decision is not evidence the decision was logged* — **and this is its
sibling: an order naming an artifact is not evidence the artifact was created.** **Closed by landing
the file with its verbatim region hashed.**

**17 — ⚠ The Planner criticised a leak that a decision had already prevented.** *(Planner)*
It argued the scorer is *"fitted on tens of targets and applied to 2,690 census rows."*
⚠⚠ **No census row is scored. All 2,690 carry `scored=False`**, because `D-089` rules *a page per
census protein, deliberately without a scorer panel.* **The premise was false and the snapshot could
have said so.** ⚠ **It points the good way: the risk was foreclosed three weeks earlier by a decision
nobody re-read.**

**18 — ⚠⚠ A hash range whose markers appeared twice hashed ZERO BYTES.** *(Code)*
The header describing the range contained the range markers, so a plain `index()` matched the
header's copy and the region resolved empty. **A valid `sha256` of nothing — and it would have
matched itself forever.** ⚠ **Anchored to line starts.** ⚠⚠ **Second occurrence in one day of a
marker line containing its own marker**, and **the argument for a declared BYTE COUNT beside every
hash: a stated length caught a corruption that two truncated checksums could not.**

**19 — ⚠⚠ A correction that inverted the control it was correcting.** *(Planner)*
Having under-delegated a production write, the Planner *corrected* itself by instructing the owner to
hand-run an Alembic migration — ⚠ **precisely the operation KEEL step 16 exists to stop a human
performing.** *Hand-deploy dies; manual = emergencies only.* **It proposed making the owner the tired
person at the terminal that branch protection was built against.**

**20 — ⚠⚠ And the correction to THAT was also uninformed.** *(Planner)*
The log had already ruled both halves: ***"Phase 1 — the initial migration is run BY HAND,
supervised, BEFORE the first deploy"***, and phase 2, ***"a `release_command` … ruled but wired AFTER
phase 1 succeeds."*** ⚠⚠ **The Planner was right, then wrong, then right again, and had read the entry
at no point.** **Both moves were made from doctrine rather than from the log**, and the second
happened to land where the log already was. ⚠ *Arriving at the correct place by accident is not the
same as knowing it*, and the accident is what this member records.

**21 — ⚠⚠ A privilege sweep proved a role safe against the wrong database.** *(Code)*
`fly mpg connect` with no `--database` lands in `fly-db`, holding Fly's sample tables — `countries`,
`metrics`, `timeseries`, `update_logs`. **The first sweep ran there and returned a clean,
well-formed, entirely correct answer about the wrong object.** ⚠ **Had the `TRUNCATE` proof run
there, it would have "proven" the reader safe against a database that is not ours.**
⚠⚠ **Caught by reading the table names. No check caught it; looking did.**
**Standing rule adopted: `--database` is ALWAYS EXPLICIT, never defaulted** — ⚠ *a dial with a
default that does not announce itself*, the same defect the missing-`straddle` `TypeError` closed.

---

**⚠⚠ THE COUNT IS NOT THE FINDING. THE CATCH RATE IS.**

**Twenty-one members; eleven Planner-made.** ⚠ **An entry in this family listing only the Builder's
instances would be a false reading of the record — and one listing only the Planner's would be a
different false reading.** **Members 15, 18 and 21 are Code's, all three self-caught, and 15 is the
only member in the entry caught before it produced a wrong answer at all.**

⚠⚠ **AND THE DENOMINATOR REMAINS UNKNOWN. THIS ENTRY STILL REPORTS NO RATE.** Every member was
**caught**; an uncaught instance leaves no trace **by construction**, which is the definition of the
class. **Survivorship, labelled as such, exactly as `KEEL-4` V9 §6 requires of the assumption score.**
**What twenty-one members establish, with no denominator: when this project goes looking, it finds
them. Enough to justify the instrument, not enough to justify a percentage.**

**⚠ What the day's members add to *what catches this class*, from the members rather than from
theory:**
- ⚠⚠ **A control case in every proof.** Three write verbs refusing looks identical to a role that
  refuses everything — **two `SELECT`s returning 2,771 is what made the refusal a measurement.**
- ⚠ **Name the target explicitly; never accept a default.** Member 21, and the `straddle` `TypeError`.
- ⚠ **A declared byte count beside every hash.** Members 18 and the truncated checksums.
- ⚠⚠ **Read the log before correcting from doctrine.** Members 14, 17 and 20 — **three in one day,
  all Planner, all preventable by one search.**

**Relied on by:** `F-044` · `F-045` · `F-046` · `F-048` · `F-049` · `D-093 amendment 2` ·
`D-093 amendment 3`.
