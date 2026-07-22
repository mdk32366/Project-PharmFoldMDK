### D-029 — The approved-ADC reference: openFDA for approval, a reviewed file for antigens, and two freshness dates
- **Date:** 2026-07-22
- **Status:** **Proposed**
- **Context:** D-015 §2 leaves an item marked **blocking §2's completeness**:

  > **Open, blocking §2's completeness:** the reconciliation of the full approved-ADC target set
  > against the 82 has **not been run**. Group C is currently the three exclusions the authors
  > named; there may be others they did not. A mechanical reconciliation script closes this and
  > must run before the cohort is called final.

  Group C is the sharpest test the project has — targets the baseline pipeline filtered out
  that turned out to be validated. It is currently **three targets the paper itself named**
  (TROP2, HER3, CLDN18.2). Whether there are others the paper did not name is unknown, and
  "unknown" is doing load-bearing work in a claim the project intends to make.

  Closing it requires answering: *which UniProt accessions are targeted by approved ADCs?*
  **That question has no single authoritative source**, and this entry rules how it is answered.

---

- **Finding: the FDA database answers half the question, and the half it answers is not the
  hard half.**

  `https://api.fda.gov/drug/drugsfda.json` — free, no authentication required, updated daily
  Monday–Friday, full bulk download available. Its **five searchable top-level fields** are
  `application_number`, `openfda`, `products`, `sponsor_name`, `submissions`
  (verified 2026-07-22 against openFDA's own field reference).

  **There is no target-antigen field. There is no ADC flag.** Drugs@FDA records that a
  product was approved; it does not record what the molecule binds. So the query the project
  actually needs — accession-level — is **not answerable from FDA data alone**, and no amount
  of query construction changes that. This is a structural property of the dataset, not a gap
  to be worked around.

  **A second, narrower boundary:** Drugs@FDA excludes products regulated by CBER. Most
  oncology ADCs sit with CDER, so the practical impact is small — but it is a stated coverage
  limit, not an assumed-complete list.

  **The secondary literature disagrees with itself, and is stale by construction.** Reviews
  surveyed 2026-07-22 variously report 14 or 15 approved ADCs and describe belantamab
  mafodotin as withdrawn — but it was re-approved in October 2025 in combination, and a
  CD123-directed ADC was approved in May 2026. **Any count taken from a review paper is wrong
  the moment the field moves, and the field has moved twice in the last year.** A single-paper
  source is therefore rejected: it is simpler, but it inherits a cutoff with no way to detect
  that it has passed.

---

- **Decision — a three-part reference, with the seam between the parts stated:**

  **(1) openFDA is the authority for APPROVAL STATUS.** Queried by application number,
  recorded with the query date. Reproducible, citable, and refreshable.

  **(2) A checked-in mapping file is the authority for DRUG → TARGET ANTIGEN → UniProt
  ACCESSION.** Roughly 16 rows. **Each row cites its own source** for the antigen assignment —
  label, primary literature, or reference database — and the file is reviewed by hand.

  **Its smallness is a feature, not an embarrassment.** Sixteen rows can be read in full by a
  reviewer, which is the correct level of scrutiny for a set that determines what counts as a
  Group C finding. A computed mapping at this scale would be less trustworthy, not more.

  **(3) The mapping is NOT FDA-sourced, and the reference must say so wherever it is used.**
  This is the seam. Part (1) is authoritative and dated; part (2) is a reviewed human judgement.
  Presenting them as one "FDA-derived target list" would attribute to the FDA a claim it does
  not make — the same error class as the two `search_path` seams sharing a name
  (`docs/HAZARD-search-path-seams.md`), and as D-024's `tier=rental` needing `tier_reason` so a
  conservative routing could not read as a measured one.

---

- **Detection is automatable; assignment is not. The refresh is built accordingly.**

  A scheduled job queries openFDA and **diffs against the checked-in file**, reporting: new
  approvals absent from the mapping, withdrawals or marketing-status changes, and rows whose
  application number no longer resolves.

  **What it cannot do is extend the mapping** — assigning a target antigen to a new approval is
  a human read every time. So the job's output is *"the mapping is stale, and here is exactly
  which rows are missing,"* which is the useful half:

  > **The failure mode being guarded against is not INCOMPLETE — it is SILENTLY incomplete.**
  > A file with a freshness date and a job that detects drift is a materially different artefact
  > from a file someone compiled once and stopped thinking about. This entry does not claim the
  > list will be complete. It claims its incompleteness will be **dated and detectable.**

- **⚠ The refresh job is ADVISORY and MUST NOT be able to redden the gate.** It runs as a
  separate scheduled workflow that **opens an issue**; it is not a required check and not part
  of the test suite.

  **Rationale, and it is the same argument D-018 made** about `worker/requirements.txt` sitting
  outside the lock-file guarantee: a check that depends on an external service can go red for
  reasons unrelated to any change in this repository. If openFDA is unreachable, rate-limits, or
  renames a field, a gating check would redden the build on a day nobody touched the code —
  which trains everyone to ignore red, and a gate that is routinely ignored is worse than no
  gate. **The gate stays hermetic. Freshness is advisory.**

- **Two dates are surfaced in the UI, never collapsed into one.** They go stale at different
  rates and conflating them would overstate the weaker one:

  | Date | Meaning | Refresh |
  |---|---|---|
  | **Approvals reconciled** | last successful openFDA diff | automated, could be days old |
  | **Antigen mapping reviewed** | last human review of drug → accession | manual, will lag, and is the genuinely incomplete one |

  A single "last updated" stamp would take the automated date and imply it covers the manual
  one. **The mapping's review date is the honest one to show most prominently**, because it
  bounds what the reference can actually support.

---

- **Test surface, written before the script (project rule):**
  - **The reconciliation is pure given a fixture** — the openFDA response and the mapping file
    in, the diff out. **No network in the test suite.** A recorded fixture response is checked
    in; the live query happens only in the scheduled workflow.
  - **A new approval absent from the mapping is DETECTED**, and the diff names it. This is the
    job's entire purpose and it is the test that proves it works.
  - **A stale application number is detected** rather than silently dropped.
  - **Every mapping row has a non-empty source citation** — a row without one fails, so an
    uncited antigen assignment cannot enter the file.
  - **Accessions in the mapping resolve against the cohort** — a Group C candidate is either in
    the 82 or explicitly outside it, never ambiguous.
  - **The two dates are distinct fields** and no code path writes one from the other.

- **Deep-learning justification:** indirect but real. Group C is the project's sharpest
  evaluation instrument — a target the baseline filtered out and the world subsequently
  validated is worth more than any aggregate correlation. **The instrument is only as good as
  the set that defines it**, and D-015 §2 already carries the caveat that three named
  exclusions are *a single instance and not a demonstrated pattern*. This entry is what would
  let that caveat ever be lifted or strengthened by evidence rather than by assertion.

- **Consequences / follow-ups:**
  - **Closes D-015 §2's blocking item** once the reconciliation runs — the cohort cannot be
    called final before it does.
  - **Group C may grow.** If reconciliation finds approved-ADC targets among the 82 that the
    baseline did not name, Group C expands and D-015 §2's single-instance caveat weakens in the
    project's favour. **If it finds none, that is also a result** and must be reported as such
    rather than quietly leaving Group C at three.
  - **The mapping file needs an owner and a review cadence**, or the second date becomes a
    stamp nobody refreshes. Recorded as an open owner action rather than assumed.
  - **This entry does not rule the antigen sources themselves** — which label, which database,
    which paper per row. That is per-row and belongs in the file's own citations, not here.
