# ORDERS — Code — the citation invariant cannot see amendments, and a live reference has been dangling through three of them

**AUTHORED-SHA256** (range: **first `## §` header → EOF**, anchored to line starts) = `7cee2f72ef548926c55f8cf3a3a97799edcb493d9ec1839751a592a556a53f86`
**bytes** = `6226`

> ⚠ **DOWNLOAD AND COMMIT. DO NOT RETYPE. No landing header.**
>
> ⚠ Planner grounding is the snapshot at **`b06d378cfcfb3e55038ee5a88b46fd85778828f8`** — ⚠⚠ **no
> `SNAPSHOT_MANIFEST.txt` in the archive (661 files, closed enumeration), so this is a `git archive`
> and the Planner CANNOT state whether the tree was dirty.** Every repository claim below is **as of
> `b06d378`** and is a question.
>
> **No GPU, no rental, no fold, no fit, no refit, no ranking run.**

---

## §0 — ⚠⚠ The defect, and it is live right now

**`D-093 amendment 3` is cited THREE times in `docs/README.md`, in the present tense, and there is no
`#### D-093 amendment 3`.** Amendments **1, 2, 4, 5 and 6** exist. **Three landed on top of the gap.**

⚠⚠ **The citation invariant reports 154 / 15 / 169 and HOLDS — because `D-093 amendment 3` matches
the pattern `D-093`, which exists.** **The checker proves the PARENT exists and has no access to
whether the AMENDMENT does.** ⚠ **That is `F-044`'s exact shape one level down** — *a reference that
resolves, to the wrong thing* — **and it is structural, not incidental.**

**And what the gap costs is not bookkeeping.** ⚠⚠ **`D-093 amendment 3` is the entry that records the
HPA licence as UNRESOLVED. Without it, the log's standing authority is amendment 1 clause 1: *"HPA is
CC BY 4.0."*** **`D-093 amendment 4`'s own title says *"the surface asserted a licence the log calls
UNRESOLVED"* — the log calls it no such thing, because the entry that would was never committed.**

---

## §1 — Task MA — enumerate the citation FORMS before writing any pattern

⚠⚠ **Do not write the regex from the Planner's survey.** It found `‹ID› amendment N` and
`‹ID› amendments N and M`, ⚠ **but `docs/CATCHUP-Planner-2026-08-20.md` uses `D-093 am. 4` — an
abbreviated form the Planner's pattern would MISS.** **A checker that silently ignores a form is the
defect it was written to fix.**

**MA1 — Enumerate every distinct way an amendment is referenced across `docs/` and `ARCHITECTURE.md`.**
**Report the forms with counts.** ⚠ Include at minimum: `amendment N` · `amendments N and M` ·
`am. N` · `amendment ‹N›` (the placeholder form the Planner has used) · any ordinal-word form.

**MA2 — ⚠ Decide and STATE which forms the checker recognises and which it deliberately does not**,
and **why**. **An unrecognised form is a category with a cause, never a silent pass.**

## §2 — ⚠⚠ Task MB — write the check RED FIRST, against the real defect

**No synthetic fixture is needed. The defect is in the tree today.**

**MB1 — Extend the invariant to resolve amendment references against `#### ‹ID› amendment N`
headers.** ⚠ **Same output discipline as the parent check: the figure states its key** — e.g.
`amendments cited N | defined M | unresolved: …`.

**MB2 — ⚠⚠ RUN IT BEFORE LANDING `D-093 amendment 3` AND WATCH IT GO RED ON EXACTLY THAT REFERENCE.**
**Report the red output verbatim.** ⚠ *A check that has never been seen to fail is decoration*, and
this one can be proven against a real, live, three-times-cited dangling reference. **Then land
amendment 3 and watch it go green.** **Report both.**

**MB3 — ⚠⚠ REPORT THE FULL UNRESOLVED LIST ON THE FIRST RUN. DO NOT ASSUME IT IS ONLY
`D-093 amendment 3`.** **The Planner checked one pattern against one corpus and found one hit; that
is not the same as there being one.**

**MB4 — ⚠ Is there a RESERVED equivalent for amendments?** **Report whether `RESERVED.md` has ever
held an amendment-level row.** **If not, say so and the check is `cited − defined = 0` with no
reserve term** — ⚠ **and say that explicitly in the entry, because a missing term looks like an
oversight to the next reader.**

**MB5 — ⚠ Guard the checker against the failure that just bit `F-050`.** That reservation was
**prose-only, so the invariant could not see it**, and the first entry to cite it broke the check.
**Whatever structure the amendment check reads, assert that the structure is what it thinks it is** —
*a parser silently matching zero rows returns a valid answer about nothing.* ⚠⚠ **Same class as the
hash range whose markers appeared twice and hashed ZERO BYTES.**

## §3 — Task MC — land `D-093 amendment 3`

**The Planner holds it.** ⚠ **AUTHORED-SHA256 `a594115421ee8bb3be704dabd2c4dde5b4d4b66afbc383e79a401d8d55637a71`, 9,527 bytes, range first `####` header → EOF.**

⚠ **It is written against `7011e24` and three amendments have landed since.** **Read it before
landing and report any statement it makes that amendments 4, 5 or 6 have overtaken** — ⚠⚠ **in
particular whether its ruling that *the surface may proceed with full attribution as a hard
precondition* is consistent with what amendment 4 actually shipped.** **If it conflicts, STOP AND
REPORT: the Planner writes amendment 7 rather than landing a stale ruling.**

## §4 — ⚠ Task MD — one thing the owner should see, reported not acted on

**The owner's position is that the HPA email is now moot because *"four of the five potential sources
were US Government sources."***

⚠⚠ **`D-093` decision 6's five are HPA · GTEx · TCGA/GDC · SEER · CPTAC. Four are US Government —
GTEx and GDC under NIH, SEER and CPTAC under NCI. THE FIFTH IS HPA, AND HPA IS THE SUPPLIER THE EMAIL
ADDRESSES.** **HPA is KTH and Uppsala, publishes its own CC licence, and its data is already ingested
and already live on the surface.**

**MD1 — Confirm or refute that mapping from the entry, quoted.** ⚠ **If the Planner has it wrong, say
so plainly.**
**MD2 — ⚠ Report whether anything in amendments 4, 5 or 6 resolves the HPA licence identity.**
**If nothing does, the discrepancy — *ShareAlike 3.0 International* on the page against *CC BY 4.0*
in amendment 1 clause 1 — remains open and the owner should rule knowingly rather than by
inheritance.**

## §5 — ⚠ Not ordered

**No ingest, no migration, no surface change, no credential work, no fold, no rental.**
**Nothing touches `D-075` or `geom_proxy`** — that amendment is separate and unmerged.
⚠⚠ **And do not "fix" any dangling reference by deleting the citation. A citation removed is a
finding erased.** **If a reference cannot resolve, it is reported and the Planner writes the entry.**

## §6 — Report

⚠ **`MB2`'s RED output first, verbatim** — it is the proof the check works.
Then `MB3`'s full unresolved list · the forms from `MA1` with counts · branch and tip · **number and
title of every entry landed in the message that lands it** · the invariant with its keys, **now
including the amendment figures** · the gate without `.env` sourced.
