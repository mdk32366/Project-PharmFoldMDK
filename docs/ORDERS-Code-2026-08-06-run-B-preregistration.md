# ORDERS — Code — 2026-08-06 — RUN B PRE-REGISTRATION. Commit this before the fetchers work.

> **COMMITTED to `docs/` as provenance. CITED BY the log, not restated in it — where this file and
> `docs/README.md` differ, THE LOG GOVERNS.** ⚠ This file records how a decision was reached; it is
> not itself authority. Check the `### D-NNN` / `### F-NNN` header, not a reference to it.

## ONE TASK.
**If this document does not end with `— END OF RUN B PRE-REGISTRATION (1 of 1) —`, it truncated. Report and request re-delivery.**

---

## AUTHORISATION LIMITS — READ FIRST

**Authorises:** one docs-only commit into `docs/README.md` (a `### D-075` amendment block) and `docs/RESERVED.md`.

**Does NOT authorise:** ⚠ **Run B.** Not the freeze, not the pull, not `--ablate`, not `attention_control` with live fetchers, not any scorer run, not any write to `ranking_runs` / `ranking_results` / `target_scores` / `protein_features`. **`ranking_run` id=5 is a committed result and is read-only on the same terms as id=2.**

⚠ **Nothing in this document touches the census.** That is a separate order and the two are parallel.

## STOP AND REPORT

- `data/attention_proxies.json` exists, or `--freeze` performs a live query — **the window this document depends on has already closed; stop and report**
- committing this would require amending `### F-004`, `### F-005`, or `### F-017`
- the checker's output is anything other than `UNRESOLVED AND UNRESERVED: none — invariant holds`

---

## WHY THIS COMMITS NOW, AND WHY IT CANNOT WAIT FOR THE WIRING PR

`ORDERS-Code-2026-08-05-D-075-run.md` §3 and `### D-075` Decision (3) leave **four free parameters unresolved**. Each was ruled by the owner on 2026-08-06. **All four were ruled after Run A's result was known and before any Run B input existed** — the fetchers are a stub, `data/attention_proxies.json` does not exist, and no proxy value has ever been computed.

⚠ **That window closes permanently the moment the wiring PR merges.** After that, any ruling is made with the data available, and the pre-registration is worthless. **This is the only honest moment to write it down.**

⚠ **The disclosure is not softened and appears in the committed text:** *ruled 2026-08-06, after Run A returned Decision 4 row 1, before any attention-proxy value existed.*

---

## THE COMMIT

Append to `### D-075` in `docs/README.md` as a clearly-headed amendment block. **Do not edit Decisions 0–6 in place** — this resolves ambiguities inside them and says so; it does not rewrite them.

### BEGIN AMENDMENT — COMMIT VERBATIM

```markdown
#### ⚠ RUN B PRE-REGISTRATION — four free parameters closed, 2026-08-06

**Ruled by the owner 2026-08-06, after Run A returned Decision 4 row 1 (F-017), and BEFORE any
attention-proxy value existed** — `scripts/attention_control.py --freeze` was a deliberate stub,
`data/attention_proxies.json` did not exist, and no proxy had ever been computed for any target.
**The protection is that the data did not exist, not that the ruler was ignorant of Run A.** Stating
the second would be false; the first is checkable.

Decision 3 and Decision 4's matching rows were frozen before Run A. They left four parameters open.
Closing them after seeing a Run B result would be the fishing this entry exists to prevent. They are
closed here instead.

**Ruling 1 — which score Run B re-ranks: `geom_proxy` (`ranking_run` id=5).**
Decision 3 says *"re-rank with the structural (ablated) score."* When written, the only ablated run
was `no_plddt`. Decision 3's own opening sentence distinguishes this control from that one —
*"D-065 tests attention only indirectly, via feature removal. This tests it directly"* — and D-065
**is** `no_plddt`. `geom_proxy` is the confidence-blind structural axis the result now rests on.
⚠ `no_plddt` (id=3) is Decision 4's *baseline*; matching on it would answer a question nobody asked.

**Ruling 2 — covariate-adjust AND stratify, as a declared sensitivity pair.**
Decision 3 says *"covariate-adjusting or stratifying."* The `or` is a live free parameter inside a
frozen decision. **Both are run.** This is Decision 3's own discipline — *"a sensitivity pair, not
one blessed number"* — applied to the method rather than to the proxy. **Four results total: two
methods × two proxies.** ⚠ **Disagreement between methods is reported as disagreement and is not
resolved toward the cleaner one**, exactly as Decision 4 treats disagreement among the triple.
The stratification rule for `pub_count`, being a second free parameter, is fixed here: **quartiles of
the frozen `pub_count` over the 56 ranking-set rows, computed from the snapshot, never re-cut.**
`pdb_present` is binary and strata are its two values.

**Ruling 3 — what "still enrich" means: the triple, against `geom_proxy`'s unmatched result.**
Decision 4's matching rows say *survives* / *survives one but not the other* / *vanishes*, and never
operationalise *survives*. Run A needed no judgement because Decision 4 anchored it to explicit
numbers. Run B is read the same way: **median, mean, and count ≥0.5 of the matched positive
percentiles, read against `geom_proxy`'s unmatched triple — 0.6607 / 0.6324 / 8-of-12 — as the
anchor.** *Survives* = all three sit toward it. ⚠ **No threshold, no significance test, no single
statistic** (D-041 dec 4; D-065/D-075 dec 5). The anchor is a number that already exists in the
record and cannot be tuned.

**Ruling 4 — the proxies are three-valued, and absence excludes rather than defaults.**
Decision 3 defines `pdb_present` as *"1 if the target has an experimentally solved structure in the
PDB, else 0"* — binary, with no state for *"the lookup failed."* ⚠ **This fills that gap; it does
not amend the definition.** A protein with no PDB entry is a **measured zero**. A protein whose
lookup errored is an **absence**, and coercing it to `0`/`False` manufactures a positive claim about
the world out of a network failure — **which in a matching analysis does not merely miscount, it
moves the matching.** F-020's shape, in the control rather than the fit.

Both proxies are recorded as **`measured` / `measured_zero` / `absent_with_reason`.** An absent value
is a **CATEGORY** — never `0`, never `False`, never a bare null. **A target with an absent proxy is
excluded from that proxy's matched analysis and named**, never defaulted into it.

**The exclusion thresholds, fixed here and acknowledged as arbitrary:**
- **0 positives excluded** — report normally.
- **1–2 positives excluded** — ⚠ **run is reportable, with the excluded targets named, and the
  analysis repeated on the reduced set with both results shown.** At n=12 one exclusion is 8% of the
  label set; that fact is stated wherever the result appears.
- **3 or more positives excluded** — ⚠ **VOID.** Fix the fetcher, re-pull under a **new as-of date**,
  and record the void run and its reason. A void run is not deleted.

⚠ **These numbers are arbitrary and are recorded as arbitrary. An arbitrary threshold fixed before
any pull is legitimate; the same number chosen afterwards is not.** That difference is the whole
reason this block exists.

**Sequencing, unchanged from §3 of the run order:** Run B follows the wiring PR and the freeze, in
its own window, under separate owner authorisation. The proxies are frozen with source, query
string, and date recorded **before** any Run B result is read, and re-running from the frozen
snapshot must be byte-identical.
```

### END AMENDMENT

---

## AFTER THE COMMIT

1. **`docs/RESERVED.md`** — record the Run B pre-registration as the resolution of Decision 3's open parameters, so the amendment is discoverable from the reservation index rather than only by reading D-075 to the end.
2. **Run the checker verbatim. Read the output, not the exit code.** Report the literal string and the reserved set size.
3. **Report the commit hash.**

⚠ **Then stop.** The next obvious step is the wiring PR, and the step after that is the freeze, and the step after that is Run B. **Each has its own order. Close the window.**

---

## WHAT THIS DOES NOT SETTLE

- **The scoring gate's reading.** *"No census row is scored before D-075 fires"* — D-075 has fired on Run A, and Decision 4's matching rows belong to Run B. **Owner ruling outstanding.** ⚠ **It gates scoring, not folding**, so the census crank is not held by it.
- **F-024 and findings numbering** — three findings queued for one free integer, owner ruling outstanding.
- **KEEL-4's A- reconciliation** — see the KEEL report; the register as delivered defines the schema but does not enumerate the numbered items, so `A-014` / `A-016` / `A-017` still cannot be checked.

— END OF RUN B PRE-REGISTRATION (1 of 1) —
