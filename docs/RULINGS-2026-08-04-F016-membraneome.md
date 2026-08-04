# RULINGS — 2026-08-04 — F-016, the reconstructed membraneome, and a correction to a number I called verified

> ⚠ **Planner provenance:** these rulings are made from Code's report. The Planner has
> `surfaceome_ids.txt` (independently counted) but **not** the reconstructed workbook, and has not
> verified 7,903, 2,801, 2,807, or the HLA collapse at first hand. Every ruling below is on
> *method*; the numbers carry Code's provenance labels, not the Planner's.

---

## §1 — ⚠ CORRECTION: "2,886, verified from the file" was the right answer to the wrong question

The Planner counted `surfaceome_ids.txt` — 2,886 lines, 2,886 unique — and labelled it **VERIFIED**
in F-011 v2's provenance table, in contrast to the numbers taken from a figure legend. That count is
correct and it is **not the census denominator.**

**It is a count of identifiers. The denominator is distinct proteins.** Keyed by accession — as
every join in this project is — Code reports **2,807**, with 79 rows collapsing into four HLA loci
UniProt has since merged (HLA-B absorbing 35, HLA-A 21, HLA-C 14, HLA-DRB1 13).

**Both numbers are true. Only one is a denominator.** ⚠ *And the error is not that a number was
unverified — it is that a verified number was verified against the wrong question.* A provenance
label answers **"where did this come from?"** and says nothing about **"is this the quantity we
need?"** The label was doing work it cannot do, and it was doing it in the very table written to
stop exactly this class of error.

**Ruled:**
- Any census count states its **key**: *2,886 identifiers · 2,807 distinct accessions.* Neither
  appears alone.
- **2,807 is the surface-class denominator.** 2,886 is a property of the ID list.
- F-011's provenance table gains a `key` column. **⚠ A "verified" label with no key is now
  incomplete by construction**, here and everywhere.

*Note for later, not a ruling: the 79-row collapse is concentrated in HLA loci, which
tumour-selectivity filtering would likely remove anyway. That is a downstream, owner-reserved
judgement and **no reason to carry the inflation** — a denominator has to be right before it is
filtered.*

---

## §2 — The third class is the more important half of F-016

2,886 positive + 2,216 negative = 5,102 **classified**; the table holds **7,903**, leaving **2,801
rows with a blank Surfy cell.**

**The Planner's `~5,102` was wrong in a worse way than being unverified.** It was arithmetic
(2,886 + 2,216) resting on an unstated assumption — *the classes partition the table* — and it
produced a number that was internally consistent, plausible, and describes only the classified
subset. **A number that is wrong and consistent is harder to catch than one that is wrong and odd.**

**Ruled:**
- **Three classes, always named:** `surface` · `non_surface` · `unclassified`. **`unclassified` is
  never merged into either** and never dropped.
- **"Not positive" ≠ negative.** Code's figure: treating the complement as the negative class
  inflates it by 126% (5,017 vs 2,216).
- ⚠ **F-011's argument is unchanged and its scope narrows.** F-011 says SURFY's *negative* class is
  defined by steady-state localization under normal conditions. That still holds — for the 2,216.
  **It says nothing about the 2,801 unclassified**, which are unexamined by a different mechanism
  and are **not** evidence for F-011's thesis. **Do not recruit them.** The temptation will be to
  fold them in because a larger excluded set makes a better story; that is the over-claim guard,
  and it binds.
- **P-002's subject is the 2,216.** The 2,801 are a separate open question.

---

## §3 — Naming: **do not take the upstream name.** Not overruled — endorsed as doctrine.

Code declined to call a scrape `table_S3_surfaceome.xlsx` because that name belongs to an artifact
nobody has obtained. **Correct, and it is the single best judgement in the report.** Putting a
reconstruction under the upstream name would launder provenance in exactly the way `PROVENANCE.md`
exists to prevent, and it would do so *invisibly* — the file would look canonical to every future
reader and to every hash check aimed at the real thing.

**On the consequence — `census_spans.py --source` pointing at a nonexistent path — ruled: remove the
default entirely. Require the flag.**

A default naming a file that does not exist is a landmine: the day someone finally obtains the real
`table_S3_surfaceome.xlsx`, the script **silently changes source** with no diff and no signal.
Defaulting to the reconstruction is the mirror of the same problem. **No implicit source at all.**

**And whatever is passed, the script records that file's sha256 in its output.** Provenance travels
with the result, not with the invocation.

---

## §4 — Commit format: **commit it, no LFS, and add a CSV sidecar**

| Option | Ruling |
|---|---|
| **Git LFS** | ❌ **No.** LFS is what cost this project a day — the pointer looked like the file in two places. Adding LFS reproduces that failure for the next person who clones. |
| **Don't commit; regenerate** | ❌ No. A source of record that must be regenerated is not a record. |
| **Commit directly** | ✅ **Yes.** 590 KB is unremarkable for git. This artifact should never change; if it does, that is a **new dated file with a new name**, not a new version of this one. |

**⚠ Additionally: emit a CSV alongside the xlsx, and make the CSV the machine-readable source of
record.** The xlsx is for humans and carries the PROVENANCE sheet; **the CSV is diffable, greppable,
and reviewable in a pull request.** Tests read the CSV. A 7,903-row binary that no reviewer can
inspect in a diff is a place for silent change to live — and silent change in the census denominator
is the specific thing this whole day was spent preventing.

---

## §5 — Buckets that still need rules

Code's UniProt resolution: **7,746 active · 105 merged · 52 inactive**, zero unaccounted.

- **105 merged** — keep the pre-merge identifier **alongside** the current accession, never
  overwritten. Same principle as §2 of the earlier rulings note on `obsolete`: the census must be
  able to answer *"how many arrived through a merge?"*, and that answer dies the moment the status
  is replaced.
- **52 inactive** — retained, flagged, **not foldable** (no current sequence). **Never dropped.**
  Same treatment as unaffordable targets under D-077 dec 1.3: present, flagged, excluded from
  nothing.
- ⚠ **Q96PC5 and P01764 carry rows in two different classes.** That is a *separate* defect from the
  HLA collapse: **the classes are not disjoint by accession even before deduplication.** Needs its
  own rule — Planner recommendation is a `class_conflict` bucket, resolved by neither, reported as
  a count, because picking a class asserts a judgement SURFY did not make. **Owner's call.**
- **397 entry names and 452 gene symbols renamed upstream** — recorded, not acted on. They are the
  reason the census keys on accession, and they are evidence for §1's ruling.

---

## §6 — Sequencing before merge

1. ⚠ **Confirm `### F-011` is in the log, not only in `RESERVED.md`.** F-016 *discharges F-011's
   flags* — an entry cannot discharge flags in an entry that does not exist. If F-011 is still
   staged, **F-016 merges with it or after it, never before.** Code's own grep discipline applies:
   check for the header, not the filename.
2. **`084517a` stays unsquashed** (prior ruling, unchanged).
3. **F-014 stays reserved** until this branch merges, as recorded.
4. **F-016 supersedes two rows of F-011 v2's provenance table** — 2,216 moves to *counted*, and
   `~5,102` is **withdrawn, not corrected**: it was never a row count and no corrected version of it
   exists. F-011 gains a supersession note pointing at F-016.

---

## §7 — Recorded: this is the denominator work paying off exactly as intended

The purpose of the scale-readiness order was to close gaps that are *harmless only at N=82*. **Two
of them were live in the census before a single row was loaded:** the classes do not partition the
table, and the identifier count is not the protein count. Both would have shipped as a census
denominator that looked authoritative and was wrong by 126% in one direction and 79 proteins in the
other.

**Neither was found by a test. Both were found by someone opening the file and counting.**
