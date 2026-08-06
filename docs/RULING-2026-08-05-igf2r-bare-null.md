# RULING — 2026-08-05 — IGF2R's bare null: proceed to Task D. And the two pre-registrations agreed on something false.

> **COMMITTED to `docs/` as provenance. CITED BY the log, not restated in it — where this file and
> `docs/README.md` differ, THE LOG GOVERNS.** ⚠ This file records how a decision was reached; it is
> not itself authority. Check the `### D-NNN` / `### F-NNN` header, not a reference to it.

---

## §1 — Which rule actually fired, because the distinction is load-bearing

Code cited **§C.3 — *the two readings must agree*** — as the basis for stopping.

⚠ **That is not what happened.** The owner reported **only that the write ran** and **did not read
the post-state**, exactly as C.3 required. **There was one reading, not two.** The two readings did
not disagree; there was nothing to compare.

**What actually fired is different and more interesting: a pre-registered clause failed.** Clause 3
of both pre-registrations said the null would carry its reason. It does not.

**Code's behaviour was right and its citation was wrong.** ⚠ Stopping on an unexpected result is
correct under either rule — but *"the readings disagreed"* and *"the expectation was false"* are
different findings with different remedies, and today has repeatedly turned on exactly that kind of
precision. **Recorded so the close-out does not inherit the wrong one.**

---

## §2 — ⚠ The finding underneath: two independent pre-registrations agreed, and both were wrong

The Planner wrote *"IGF2R the only null, carrying its null-with-reason."* Code independently wrote
*"IGF2R, carrying no residues resolvable from…"*. **Two sources, written separately, in agreement —
and false.**

**Why they agreed.** Both read the same dry-run line:

```
NULLS  IGF2R  P11717  … membrane_proximal_sasa=no structure (fold failed - no PDB)
```

…and both took it for a **persisted field**. It is an **extraction-time report.** The stored
`null_reasons` was written **2026-07-27, before feature 7 existed**, and the fill writes one column
by design.

⚠ **This is a real limit on the discipline this whole session leaned on.** *Two independent
readings* has corroborated 0007 twice, the census denominators, and the determinism result. **But
independence of readers is not independence of reasoning.** When both readers derive an expectation
from the same upstream artifact, agreement measures nothing but that they read it the same way.

**The protection that worked was not the second reader. It was the pre-registration being written
down at all** — a false expectation stated in advance is falsifiable; the same assumption held
silently would have made a bare null look normal.

**Reserve `F-022`** — *two independent pre-registrations can agree and both be wrong when derived
from a common artifact; independence of source is not independence of inference.* ⚠ Cite alongside
`A-016` and `A-017 (the fixture must discriminate)`: same family, one level up.

---

## §3 — RULING: proceed to Task D. The fill is not at fault and Code's read is adopted.

**Code's analysis is correct on every point** and its refusal to write `null_reasons` was right —
doing so would have been *"rewrites inputs it was not asked to touch,"* **F-021's own defect, in the
PR that fixes F-021.**

**Why it does not gate Task D:**

1. **IGF2R cannot reach the fit.** `disposition='held_out'`, `pdb_path IS NULL`, six of six features
   null → `features_complete` is False → the `(0.0,)*7` inert branch, excluded by construction.
2. **The guard operates on ranking-set rows.** All 56 carry values; IGF2R is not among them —
   measured by the instrument, not asserted.
3. **No surface renders feature 7.** It is not one of D-027's six and reaches no route.

**And the fix is not one JSON key in practice.** The fill writes one column **by design**; adding
`null_reasons` requires a code path that does not exist. So *"fix it now"* means another PR **and
another production write**, at the end of a fifteen-hour session, on a row the run cannot touch.
⚠ **That trade is worse than the gap.**

**Ruled: Task D proceeds. The gap is recorded, not carried silently.**

---

## §4 — But it is a real defect and it gets closed, not filed

⚠ **IGF2R now holds the only bare null in `protein_features`** — *"an absent value is a category,
never a bare null"* is stated **without an in-the-ranking-set qualifier**, and it is among this
project's most-cited rules. **A singleton anomaly is precisely what gets explained away six weeks
later.**

**Reserve `F-023`** — *a null_reasons map written before a seventh feature existed, leaving the one
feature added later as the only uncategorised absence in the table.*

**Closed in the follow-up that lands the F-017 commit**, alongside the three environment findings and
the `80 written / 79 valued` reporting imprecision. ⚠ **The reason already exists** — the extractor
computes it today, as the dry run printed. **Nothing is invented; it is persisted.**

⚠ **D-074 applies:** F-023 is not closed until `protein_features` holds no bare null — not when the
follow-up is written.

---

## §5 — Task D, unchanged

**The same command that refused now proceeds.** Report Task A's refusal and Task D's pass **as one
before/after pair** — that pair is F-020's closure evidence under D-074.

**⚠ Stop at the point the guard passes. Run A does not start.**
