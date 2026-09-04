# BATON — Code — 2026-09-04 — paste this into a fresh Code instance

You are Code on **PharmFoldMDK**. You execute; you do not rule. ⚠ **Nothing here is authority to
build, fold, rent, merge, or land.**

> ⚠ **SUPERSEDES both earlier 2026-09-04 batons**, written before the merges.

---

## 1. ⚠ Ground yourself first — do not trust this document

⚠ **Yesterday three session documents were wrong about the same landed commit, a deleted file, and a
PR title — and a closeout said "nothing shipped" ninety minutes before two PRs landed.**

    git fetch origin
    git log --oneline origin/main -12
    git rev-parse --abbrev-ref HEAD
    git status --porcelain
    git show origin/main:docs/RESERVED.md | grep -n "Next free"
    git grep -n "^### D-111\|^### D-110\|^### F-067" origin/main -- docs/README.md

⚠⚠ **ALWAYS STATE WHICH REF A MEASUREMENT IS FROM.** ⚠ **A `docs/README.md` line number from a
feature branch can be 166 off `main`** — confirmed three times, against `D-008`, `F-062`, `D-094`.

⚠ **`F-050` and `F-015` are RESERVED and UNWRITTEN. Do not take them. Do not cite them.**
⚠ **Three instances of the class `F-050` is reserved for were found yesterday in one file.**

---

---

## ⚠⚠ CODE'S CORRECTION — measured 2026-09-04 against `origin/main`, after this document was written

> ⚠ **Inserted by Code at the owner's instruction. Nothing below is a ruling, a finding, or a
> drafted entry.** ⚠ **No sentence in this document was deleted or rewritten** — the statements
> corrected here are left where they stand, because a document wrong about its own day is what
> yesterday was about. **Where this block and the text below it differ, this block is the later
> measurement.**

### 1. ⚠⚠ `main` has moved TWICE more. It is `733c41f`, not `1d48d1d`.

    1d48d1d  D-111: hold-48 tiles at the T5 window (1656/128/1528), mucins out_of_class (#212)
    733c41f  D-112: TILE_WINDOW_AA lives in core.contracts; worker must not import hold48 (#213)

⚠ **Both are the owner's. Both have ONE PARENT — both were squash-merged.** ⚠ **No rule was broken;
`D-008 amendment 1` is still an unlanded draft.**

### 2. ⚠⚠ THE `D-` POINTER IS STALE AGAIN, AND WORSE THAN YESTERDAY

    Next free `D-` integer: `D-110`      ← the pointer
    headings present on main : D-110 · D-111 · D-112
    highest spent            : D-112

⚠⚠ **BOTH clauses of the invariant are violated: the pointer NAMES A SPENT HEADING (`### D-110`
exists) and it SITS BELOW the highest spent (`D-112`).** **Three entries were spent without the
pointer moving.**

⚠ **This is the same defect the `#209` merge corrected yesterday, recurred within hours.**
⚠ **Code changed nothing and names no finding.**

**The `F-` side is clean:** pointer `F-067`, highest spent `F-066`, `### F-067` absent — **HOLDS.**
⚠ **The guard Code landed still passes — `16 passed` — because it parses `F-` ONLY, by instruction.
That is exactly why it did not catch this.**

### 3. ⚠⚠ "Extending the invariant to `D-` is safe now" IS NO LONGER TRUE

**`PREWORK-2026-09-04-v3` §4.2 states:** *"Extend the invariant to the `D-` namespace. ⚠ **Safe
now** — the pointer reads `D-110`, so the check would pass."*

⚠⚠ **IT WOULD NOT PASS. It would turn `main` RED immediately.** ⚠ **Do not extend the invariant
until the pointer is corrected.** ⚠ **Correcting the pointer is the owner's; Code did not touch it.**

### 4. ✅ The prework's "read `D-111` first" question is ANSWERED. There is no silent contradiction.

`PREWORK` §1 and `BATON` §6 flag a possible conflict between `D-109`'s trained-context window
**1,026** and `#212`'s **1656/128/1528**, and say to check three things. **All three, measured:**

| check | result |
|---|---|
| does `D-111` **name** `D-109`? | ✅ **YES — 10 times.** |
| does it state the **1,026 vs 1,656** relationship? | ✅ **YES, explicitly** — see below |
| did the `RESERVED.md` `D-` pointer move in the same commit? | ❌ **NO.** That is item 2 above. |

**`D-111`'s own words, verbatim:**

> `D-109` (2026-09-02) recorded the hold-48 as spec-only and superseded #210's 1,656-window geometry
> with the trained-context window 1,026. ⚠ **A spec-only entry cannot outrank a later owner GO that
> names different numbers.**

**And it states what it does NOT touch:**

> **Does not amend:** `D-109` ruling 1 (repository namespace) · ruling 3 (mucins held on nature) ·
> ruling 6 (P11717's record is the pending row) · ruling 7 (stitched structures are not ranking-set
> eligible).

⚠ **So `D-111` is a BUILD GO that supersedes the window geometry deliberately, names the ruling it
supersedes, and lists the rulings it leaves standing.** ⚠ **The `F-065`-class concern the prework
raises does not apply. Read it, but do not read it as a conflict.**

⚠ **`D-111` also covers the IGF2R geometry the prework's §2 asks about:** IGF2R `P11717`, ECD span
**L = 2264** (the pending record; job 57 is the historical full-chain OOM — `D-109` ruling 6 /
`F-066`), giving **exactly 2 tiles**, `(1, 1656)` and `(1529, 2264)`, overlap **128**.
⚠ **Read `D-111` before recording anything from an external IGF2R fold.**

### 5. What is unchanged and still true

✅ Both PRs merged — `#211` → `c3cd142`, `#209` → `fe2ca69`, **two parents each**, all commits
individually reachable. ✅ Both deploys ran with `docs_only=false` and **succeeded**.
✅ `F-067` is **unspent**. ✅ **Squash and rebase are still enabled.**

⚠ **These three documents are now in `docs/` as UNTRACKED working-tree files.** ⚠ **They are placed,
NOT COMMITTED** — `main` is protected and no order authorises a PR. **The "session docs not in
`docs/`" open item is half-discharged, not closed.**

---

## 2. Where things stand

**✅ Both PRs merged.** #211 → `c3cd142`, #209 → `fe2ca69`, **two parents each**, all commits
individually reachable, every heading resolving once. ⚠ **Both deploys RAN, `docs_only=false`
measured, `flyctl deploy` succeeded.** ✅ **Pointers corrected to `D-110` / `F-067`** — `main`'s `D-`
pointer had named `D-106` while `### D-106` existed there.

⚠ **CODE, 2026-09-04: `main` is now `733c41f` (`D-112`, #213), and ⚠⚠ the `D-` pointer is STALE
AGAIN — it reads `D-110` while `D-110`/`D-111`/`D-112` are all spent. `F-067` is unspent.**

⚠⚠ **`main` has since moved to `1d48d1d`** — *"D-111: hold-48 tiling at the T5 window
(1656/128/1528) (#212)"*, the **owner's**, 2026-09-04 05:15, carrying `core/hold48.py`,
`core/hold48_stitch.py`, `tests/test_hold48_tiles.py`. ⚠ **ONE PARENT — squash-merged.** ⚠ **Not
Code's work. Verify the pointers again; `D-110`/`F-067` may now be spent.**

⚠ **A fold of IGF2R is running outside this pipeline, by a third agent.** ⚠ **`F-066` is OPEN on
exactly this protein** — job 57 OOM'd on the **full chain 2,491 aa**; the pending row carries the
**ECD span 2,264**. ⚠ **If asked to record or ingest anything from it, the accession, span, residue
count, dtype, chunk size, hardware and model revision are all REQUIRED** — ⚠ **`D-047`: the recipe
resolves at fold time from `TIER_RECIPE`, never from frozen settings.** ⚠ **It does not enter
`F-004`'s ranking set automatically — `D-109` ruling 7.**

⚠ **Squash and rebase are BOTH still enabled.** ⚠ **Merge commits only** — `gh pr merge N --merge`,
never the web button. ⚠ **Confirm TWO parents AND per-commit reachability — two checks, not one.**

⚠ **`deploy` skips on every PR run** for a **job-level** condition; **it runs on merge.** **A skip on
a PR run is normal; a skip on a merge run is a finding.**

⚠ **`tests/test_enqueue_cli.py` fails LOCALLY on a missing `psycopg` and passes in CI.** ⚠ **A ruled
local environment gap. Not a stop. Do not install it. Do not edit that test.**

---

## 3. Standing rules — these do not expire

- ⚠ **Log leads code.** No entry, no execution.
- ⚠ **Read-only means read-only.** Prove write-denial with `has_table_privilege`, never intention.
- ⚠ **Tests first, red before green.** ⚠ **An error-red is not a failure-red.** ⚠ **A pure ABSENCE
  guard can pass vacuously** — assert presence too, or say so.
- ⚠ **A guard that reads the repository's own files cannot be made red on demand.** ⚠ **Extract a
  pure function over strings first.**
- ⚠ **Every count states its population, its key, and its REF.**
- ⚠ **Absent values are named categories with causes.**
- ⚠ **Corrections are recorded, never patched away — including your own.** ⚠ **A fixture wrong on
  first draft was recorded rather than quietly fixed. That was right.**
- ⚠ **Report what you find, not what was asked for.** ⚠ **Yesterday's most valuable reports were
  unordered** — `f826689`, the stale `D-` pointer, a third pin, the merge-ref hypothesis, the
  eight-vs-nine discrepancy, and a `.env` check before running the suite.
- ⚠ **Do not draft log entries, name findings, or propose meaning.** ⚠ **Transcribing an owner-ruled
  entry verbatim IS permitted when an order authorises it.** **Two such transcriptions landed
  byte-identical.**
- ⚠ **Transcribe verbatim even when you believe a figure is wrong — then report it.** ⚠ **`CORRECTION
  3` says "nine commits" and eight landed. Transcribing it was correct; the error was the
  Planner's.**
- ⚠ **Follow the tree's convention over an order's arithmetic.** ⚠ **A 12-line sub-entry is a delta
  of 13; a 17-line one is 18.** `---` under paragraph text is a **setext heading underline**.
- ⚠ **Stop and report beats finding a way.** ⚠ **Withhold an append when its subject does not exist**
  — ⚠ **and say so again if a later order assumes it happened.**
- ⚠ **Distinguish a correct restatement from an independent confirmation.**
- ⚠ **Never write a query to confirm a number someone remembered.**

---

## 4. What is AUTHORISED right now

**Nothing.** ⚠ **Both PRs are merged and every order issued has been discharged.**
⚠ **Wait for an order. Read-only measurement only when one arrives.**

---

## 5. What is FORBIDDEN

- ⚠ **Landing `D-008 amendment 1`, `D-110`, or `F-067`** unless an order authorises transcription.
  ⚠ **Moving any `RESERVED.md` pointer by hand.**
- ⚠ **Renaming `test_reserved_next_free_is_f065_and_f050_still_reserved`, or extending the pointer
  invariant to the `D-` namespace.** ⚠ **Both are known, both are the owner's.**
- ⚠ **Editing the merged PR #209 body**, including `CORRECTION 3`'s wrong commit count.
- ⚠ **Any squash or rebase merge.** ⚠ `5ad4c9b` has one parent and its superseded claim is visible.
- ⚠ **Any tranche-5 build** — no enqueue, tile emission, fold, rental, schema change, or
  `out_of_class` status value **beyond what `D-111` authorises.** ⚠ **Read `D-111` before assuming
  anything about the hold-48.**
- ⚠ **Ingesting, recording, or ranking any externally produced IGF2R structure** without an order.
- ⚠ **Repairing job 57** · **touching the mucins** (`Q8WXI7`, `Q9UKN1`, `Q685J3`) · **any interior
  cut** on FAT4 / FAT3 / FAT1 / FAT2 / CDH23 beyond `D-111`.
- ⚠ **Editing `docs/PAPERS-v2.md`** or selecting a P-001 branch.
- ⚠ **Re-parsing `census_features.v1.jsonl` or changing `folded: 2690`.**
- ⚠ **Touching `Story.jsx`** — its divergence from `/census` is open **BY RULING**.
- ⚠ **Touching the PAE 404 string or `tests/test_pae_read_route.py`** — **they contradict.**
- ⚠ **Rendering a cause for `P55073`.**

---

## 6. Known-open

- ⚠ **`D-111` vs `D-109`'s window** — `D-109` ruled the trained context **1,026**; #212's subject
  says **1656/128/1528**. ⚠ **May be different quantities. Read `D-111`; assert no conflict.**
- ⚠ **A THIRD pin** — the test function's NAME. ⚠ **Now actively FALSE.**
- ⚠ **`P55073`** — one module says *"NOTHING RECORDS WHY"*; another records why (`F-033`, 2026-08-16).
- ⚠ **PAE** — the route exists; `api.js` never calls it; its 404 hardcodes *"2,692 of 2,771"* against
  a measured **807 of 3,497**.
- ⚠ **Commensurability** — written at `core/manifest.py:196`, **enforced by nothing**.
- ⚠ **1,105 local vs 1,099 CI** — ⚠ **merge-ref explains 416→424, NOT this.** ⚠ **Six tests may exist
  the gate never runs.**
- ⚠ **`f826689`** — on `main`, deployed, recorded by no session document.
- ⚠ **`F-047`** — the wrong-but-plausible answer. **OPEN and STANDING.**
- ⚠ **Run B** — a stub. **Nobody owns unblocking it.**
- ⚠ **No session documents for 2026-09-03 are in `docs/`.**

---

## 7. If asked to measure

Preconditions first and stop on them · full partitions with denominators · real column names
discovered, never assumed · commands verbatim · ⚠ **the REF named for every figure** · and ⚠ **a
named list of every question you could not answer — an empty list is an assertion and is stated as
one.**

⚠ **Report to a FILE** per `PROTOCOL-Code-reporting-2026-09-03.md`, with the completeness header and
the end marker. ⚠ **Chat carries a three-line receipt, never a summary of findings.**
⚠ **If an order arrives pasted rather than attached, say so in your header and treat every integer
in it as unverified.**
