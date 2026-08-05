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

| Number | What it will be | Reserved by / when | What unblocks it |
|---|---|---|---|
| **D-010** | *Nothing.* A historical skip — the sequence runs D-001…D-009 then D-011. | Pre-2026-07-19 | **Never.** Not renumbered because commit `c07b95b` already names D-011. Permanent, documented in `docs/README.md`. |
| **D-078** | The F-008 precision A/B pre-registration — the controlled re-fold at the opposite precision | D-077 dec 7, 2026-08-04; ⟡ **trigger amended D-079, 2026-08-05** | ⟡ **AMENDED TRIGGER: the first census fold at a second precision.** D-079 dec 2 folds every target at whichever tier reaches it, so the census *creates* the overlap directly rather than waiting for a ceiling to rise. ⚠ **Its outcome can move F-004**, so it is written before any such fold runs. **Superseded trigger, recorded because a reservation whose condition changed silently is a reservation nobody can check:** *"a raised local ceiling — if D-077's bisection lifts the ceiling above 440, rental/fp16 targets become locally foldable at int8, creating the first overlap in a partition F-008 recorded as having none."* That route remains valid; it is no longer the only one, and no longer the first. |
| **D-080** | *A revert proof operates on committed state or on a copy — never on a working tree holding uncommitted work.* | Amendment §3, 2026-08-04 | Nothing — writable now. Prompted by assumption-register item 15, which is at **n=2** (D-075's process note is the first occurrence). |
| ~~**F-011**~~ | ~~The surfaceome negative class — SURFY's exclusion is condition-dependent localization, not "cannot be a target"~~ | ~~Planner, 2026-08-04~~ | ✅ **WRITTEN 2026-08-04**, in the same commit as F-016 — see `### F-011` in the log. No longer a reservation. ⚠ **It had been staged in `docs/` and pushed since 2026-08-04 without ever entering the log** — the D-062 defect in the Planner's own output, surfaced only because F-016 grepped for the header rather than the filename before merging on top of it. The landing note in the entry records this. Its magnitudes are **discharged by F-016**: 2,216 counted, `~5,102` withdrawn. |
| ~~**F-012**~~ | ~~Task 1 — the chunk-invariance verdict~~ | ~~D-077 dec 2 / amendment §1~~ | ✅ **WRITTEN 2026-08-04.** The run happened; row 2 fired (outputs differ, chunk 16 diverges from 64). No longer a reservation — see `### F-012` in the log. |
| **F-015** | Does an **unchunked** fold (`chunk_size=None`) differ from `chunk_size=64` at fp16? | F-012, 2026-08-04 | **A GPU run that has not been designed yet.** F-012 established that chunk_size can change output (16 vs 64, int8, 114 aa) and that the folded cohort spans three recipes — **34 targets at `('fp16', None)`**, 3 at `('fp16', 64)`, 42 at `('int8', 64)`. It did **not** measure `None` vs `64`, which is the comparison that would decide whether the cohort's rental folds are commensurable with each other. ⚠ Needs its own pre-registration before it runs, because its outcome could bear on every rental-tier feature. |
| **F-013** | Task 3 Arm A — the measured local ceiling | D-077 dec 3-4 / amendment §1 | **The GPU run.** Bisection in (440, 630) at int8/chunk 64, k=4, step 8. May legitimately return `unstable` at every length. |
| **F-014** | *Documenting a duplication is not managing it* — the tenth instance of the two-paths-to-one-quantity class, and the first where the drift was **written down and the writing-down substituted for the fix** | Amendment §7, 2026-08-04 | Nothing — writable now, but **held until `d077-local-fold-envelope` merges**, because it describes code that branch changes. |
| **F-017** | The **D-075 result** — which row of D-075 Decision 4 fired, and what it licenses | `ORDERS-Code-2026-08-05-D-075-run.md` §5, 2026-08-05 | **The run.** ⚠ Reserved **before** the run so the number is not contested mid-session. ⚠ **F-017 was claimed twice in one morning** — by the D-075 result and by a census stop-condition — and the census orders were corrected to *confirm the next free number at the time*. **F-017 is the D-075 result and nothing else.** The entry cites D-075 and F-004 and amends neither, and it states the fired Decision-4 row **quoted from the log** before it states anything else. |
| **F-018** | *An absent status recorded as an affirmative one* — the absent-value rule violated in the **passing** direction | `RULINGS-2026-08-05-task2-task3-contract.md` §4.2, widened by the identity-status, status-wins-over-span, and prose-retirement rulings, 2026-08-05 | **The fix landing.** Scope is **three code sites** — `core/census.py:97` and `scripts/ecd_lengths.py:128` (`or "resolved"`), `scripts/census_spans.py:112` (the `== "resolved"` gate) — **plus `categorise()`'s precedence failure** (a rule that stops firing because its vocabulary moved while its docstring goes on asserting it) **plus four prose sites** carrying retired vocabulary. ⚠ Any CSV lacking a status column would have had every row treated as resolved. Write it when the fix lands, not before. |
| **F-019** | *A SURFY class is a property of the identifier, not of the protein* — two proteins whose source entries disagree with each other about class | `RULINGS-2026-08-05-class-collision.md` §3, 2026-08-05 | **The class-conflict tag shipping.** Measured instance of **A-014**. ⚠ **OVER-CLAIM GUARD, AND IT BINDS: n = 2.** A **mechanism illustration, not a magnitude** — it says the class *can* be identifier-scoped and nothing about how often. ⚠ **It is NOT evidence for F-011's thesis:** F-011 is about how the negative class is *defined*, this is about how an assignment is *keyed* — adjacent, not the same, and P-002's named failure mode is exactly that promotion. **It must not be recruited into any count.** |
| **A-014** | *An upstream model's negative class is a prediction, not a fact* — the assumption F-011 catches | Planner, 2026-08-04 | **KEEL-4 landing.** ✅ Re-verified 2026-08-04 against the received F-011 v2, which cites it as *"reserved in `RESERVED.md`, unwritten until KEEL-4 lands against v6"*. ⚠ **KEEL-4 still not received by Code** — the only one of the four staged documents still missing. |
| **A-016** | *Any red proves the assertion bites* — the corrected red-then-green formulation | `PAPERS-v2.md` P-001, 2026-08-04 | **KEEL-4 landing.** Cited as the register entry behind P-001's methods-section correction: an error-red and a failure-red are different objects, the revert must be a realistic mistake, and it must fail at the assertion. Originates in the guard Code caught reddening as a collection error (F-012 session). |

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
