# RULING — 2026-08-05 — A-017 ratified as provisional; the A- namespace exposure is wider; Task C protocol

---

## §1 — A-017: the reasoning is ratified, and taking A-015 would have been the error

**Not taking A-015 was correct.** `RESERVED.md`'s own document-status table records that KEEL-4
*"holds assumption items 15/16/17"* — so A-015 is free **by the checker** and possibly **not free by
the authority that defines the namespace.** ⚠ **Taking it would have been the F-017 double-claim in a
namespace that cannot be checked**, which is worse than the original: the collision would be
undetectable here.

**Lowest integer above every locally-known A- number, marked provisional in the row itself, with the
reasoning written into the row rather than into a message.** Adopted.

⚠ **And Code flagging it before merge rather than after is the ruling behind the ruling.** *"I'd
rather you know the number is a guess than have it read as verified"* — a provenance statement about
a number's own reliability, which is precisely what 2,886-labelled-VERIFIED lacked.

## §2 — ⚠ The exposure is wider than A-017, and it is the Planner's

**A-014 and A-016 were assigned locally into the same namespace, by the same method, and KEEL-4 is
said to hold items 15, 16, and 17.** So **A-016 has a live collision risk too** — and unlike A-017 it
is **already cited in shipped artifacts**: `PAPERS-v2.md` P-001's methods section, and repeatedly in
today's orders and rulings by the Planner.

**This is the two-paths class in a namespace: two authorities, no reconciliation, and we hold one.**

**Ruled — a mitigation available now, at no cost:**

> **Every local A- reference is cited as `A-0NN (descriptive name)`, never as the bare number.**
> `A-016 (any red proves the assertion bites)` · `A-017 (the fixture must reach the code under
> test)` · `A-014 (an upstream model's negative class is a prediction, not a fact)`.

⚠ **If a number moves when KEEL-4 lands, the citations do not orphan — the name carries them.** This
is D-074's remedy again: *a name that states its own rule*, applied to a citation rather than to a
field. **The reconciliation task must check all three local assignments, not only A-017.**

## §3 — Go on Task B

Build as ordered, with the 1–6 comparison reported as a result even when it passes. Shape confirmed
against Code's own reading of the tree.

**One addition, from the `records`-not-`rows` design call:**

⚠ **`or 0.0` at `fit_scorer.py:111` is replaced by an explicit `is None` check, not merely guarded
around.** **A membrane-proximal SASA of exactly 0.0 may be a legitimate measurement** — a fully
buried window. Today the guard catches nulls on ranking rows, so nothing is wrong; but the
correctness would rest **entirely on the guard** rather than on the assembly, and a measured zero
would still be indistinguishable from an absence one layer down. **Remove the coercion. Report the
distribution of feature 7 after the fill, naming any exact zeros** — a fact to have before Run A,
not after.

---

## §4 — TASK C · The owner protocol. Production write.

**Prerequisite: #124 merged, then Task B's PR merged.** Not before.

### C.0 — A window with BOTH the venv and the environment

⚠ **The 0007 window had `DATABASE_URL` but no venv** — `dev-up.ps1` sets the environment; the run
guide treats activation as a separate step. **That is why the alembic invocation was unverifiable.**

```powershell
cd C:\Projects\Project-PharmFoldMDK
& .\.venv\Scripts\Activate.ps1
Get-Content .env | ForEach-Object { if ($_ -match '^\s*([^#=]+)=(.*)$') { Set-Item -Path "Env:$($matches[1].Trim())" -Value $matches[2].Trim() } }
python scripts\dev_check_db.py
```

**Proceed only on `[db] OK`.** ⚠ The proxy window stays open and untouched throughout.

### C.1 — ⚠ Record the pre-state YOURSELF, before anything runs

**This is the owner's own reading, not Code's**, so the before/after is two independent readings
rather than one source reporting on itself — the discipline that corroborated 0007 twice today.

Capture and keep: `count(*) FROM protein_features` · `count(*) WHERE membrane_proximal_sasa IS NOT
NULL` · `max(id), count(*) FROM ranking_runs`.

### C.2 — Dry run first. Read it. Do not chain it to the write.

**Exact invocation comes from Code's Task B report** — the flags are Code's to name, not the
Planner's to guess. **The shape is fixed:** a dry run that writes nothing and reports the 1–6
comparison.

**⚠ STOP CONDITIONS — any one halts, and none is a retry:**

| Condition | Why it halts |
|---|---|
| **Any row's features 1–6 differ from stored** | The instrument moved. **Outranks D-075.** Nothing is written. |
| **Proposed write count ≠ 56 ranking-set rows covered** | The fill's population is not the guard's population |
| **The dry run writes anything at all** | It is not a dry run |
| **The proxy drops mid-run** | State becomes unknown, which is worse than failed |

### C.3 — The write, then hand it to Code

**Do not verify it yourself and report the verification.** Report only *that you ran it*. ⚠ **Code
reads the post-state independently** — counts unchanged, non-null count on the ranking set, feature-7
distribution — and **the two readings must agree.**

### C.4 — Then Task D, which is Code's

The same command that refused now proceeds. **A and D reported together as one pair. Run A does not
start.**
