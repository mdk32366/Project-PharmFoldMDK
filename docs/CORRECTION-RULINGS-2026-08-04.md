# CORRECTION & RULINGS — 2026-08-04 — F-011's identifier claim, Code's two judgement calls, and a delivery-channel finding

Three items. The first is a correction to a merged entry; the second and third are rulings Code
asked for. **None requires a re-issue of F-011 — this note is appended to it**, per the project's
practice of recording corrections explicitly rather than patching quietly.

---

## §1 — CORRECTION to F-011 v2: the identifier mismatch is TOTAL, not partial

**F-011 v2 states:** *"`surfaceome_ids.txt` contains UniProt **entry names** (`1A01_HUMAN`), not
accessions."* True, and **weaker than the data supports.** As written it leaves room for a reader —
or a future implementer — to assume partial overlap and build a "try accession, else map" fallback
path that would silently succeed on nothing.

**Code flagged this. Independently re-verified by the Planner against
`surfaceome_ids.txt`, 2026-08-04, rather than accepted from the report:**

| Property | Count | Of 2,886 |
|---|---|---|
| Total lines / unique | 2,886 / 2,886 | 100% |
| **Accession-shaped** (UniProt regex) | **0** | **0%** |
| Ends `_HUMAN` | **2,886** | **100%** |
| Neither | **0** | 0% |

First three: `1A01_HUMAN`, `1A02_HUMAN`, `1A03_HUMAN`. Last three: `ZP3_HUMAN`, `ZP4_HUMAN`,
`ZPLD1_HUMAN`.

**The corrected claim:** *not one of the 2,886 identifiers is an accession. The file and this
project's join key have **zero** overlap by construction, and every join in the project is keyed by
accession. The mapping step is not a fallback or a cleanup pass — it is a hard prerequisite, and
until it runs the census has 2,886 identifiers and 0 joinable rows.*

⚠ **Why this correction is worth writing down rather than absorbing.** A "mostly" mismatch and a
total mismatch call for different code: the first wants a fallback, the second wants a **refusal**.
Code's `scripts/census_spans.py` already refuses on missing input rather than improvising — the
correct behaviour, arrived at before this correction, and now the entry says why it is correct.

---

## §2 — RULING on Code's judgement call 1: `obsolete` keeps its own bucket. **Not overruled.**

Correct, and for the reason given: **merging `obsolete` into any other status is lossy, and its own
bucket is the only non-lossy option.** An obsolete accession is a different fact from an unresolved
one — the first says *this identifier existed and was retired*, the second says *this identifier
could not be resolved at all.* Collapsing them would destroy the distinction that tells you whether
to go looking for a replacement.

**Extended, since the case will recur:** if Task B later resolves an obsolete entry to a replacement
accession, **the row keeps its `obsolete` provenance alongside the replacement** — it does not
become `resolved` as though nothing happened. The census must be able to answer *"how many of these
came through a retirement?"* later, and that answer is destroyed the moment the status is
overwritten. **Same principle as D-071's three-valued provenance strength.**

---

## §3 — RULING on Code's judgement call 2: `--annex-column` off by default. **Not overruled, and the policy is now set.**

The flag is right and defaulting it off was right — the order made annex spans conditional on the
annex being a distinct category, and Code implemented the mechanism without deciding the policy.
**That is exactly the Planner/Builder line working.**

**Policy, set here:** annex spans are **computed and reported, always, under a distinct label.**
Never merged into census totals, never omitted.

- **Computed**, because the annex's cost is real information: if the negative class is
  overwhelmingly large or overwhelmingly unfoldable, that bears directly on whether P-002 is
  tractable at all, and it costs nothing to know.
- **Distinctly labelled**, because a cost figure silently merging annex and census members is wrong
  in both directions — it inflates the census and it hides the annex.
- ⚠ **Reporting the annex's cost is NOT a claim that annex members are targets.** F-011's over-claim
  guard binds here unchanged.

---

## §4 — FINDING: the delivery channel is lossy in **both** directions, in one session

Recorded because it has now produced two distinct failures on the same day and the second one was
caught only by Code's own initiative.

| Failure | What happened | Caught by |
|---|---|---|
| **Duplicate** | `ORDERS-…-surfaceome-spans-v2.md` arrived twice (10:37, 10:58) over a copy already being worked from | **Code hashing both before reading** — byte-identical, so the work stood |
| **Drop** | `ORDERS-…-b-scale-readiness.md` never arrived at all — it owns Tasks A and B, which §1 of the spans order depends on | Code, on finding §1's inputs absent |

**The assumption that broke:** *a document the Planner produces reaches the Builder exactly once,
intact.* It has now broken as a duplicate **and** as a drop, in a single session. This is why the
project's standing note says paste is the reliable channel for anything gating work.

**The guard, and it already exists in practice:** Code hashed the duplicate before reading further.
Had the second copy differed, work would have continued against a superseded order with nothing
signalling it. **That behaviour becomes standard: any re-delivered document is hashed against the
copy in hand before any further work, and a mismatch is stop-and-report.**

**Reserve an A-entry** in `RESERVED.md`; it is written when KEEL-4 lands against v6, with A-014 and
A-016.

---

## §5 — The one blocker, stated plainly

**`ORDERS-Code-2026-08-04-b-scale-readiness.md` never arrived, and everything queued is behind it.**
It owns Task A (fetch and sha256-verify the real `table_S3_surfaceome.xlsx` against
`2f1b8262…`/`6864772`) and Task B (2,886 entry names → accessions, four buckets). The spans order's
§1 inputs are its outputs.

**Code was right not to improvise them** — duplicating that work is precisely what the spans v2
re-issue existed to prevent, and doing it anyway would have recreated the two-paths-to-one-quantity
defect the re-issue was written to remove.

**Nothing else is blocked on the Planner.** §2 is executed (14 tests, six guards proven by revert,
each failing at the assertion), §3's code is written and correctly withheld, the gate is green at
429/15.

---

## §6 — Recorded, unprompted, and worth keeping: Code improved on the order

`core/census.py` gives **identity failures precedence over any span** — a `multi`, `unresolved`, or
`obsolete` row is never classified by its ECD length. The order said those statuses must *survive to
the output*; it did not say they must *win*.

**Code's reasoning is better than the order's:** classifying such a row by its span **asserts an
identity the mapping step declined to establish.** A cost figure derived from the ECD length of a
protein we could not identify is a number about nothing.

Recorded as a Builder improvement, not absorbed silently.
