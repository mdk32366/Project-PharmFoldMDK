# Session Pre-Work — The UI Arc (Step 2)

**Preceded by:** the first-fold session — pipeline live end to end, first NECTIN4 structure
durable, and (if the overnight batch ran) ~40 local-tier structures in hand.
**Session type:** first session of the UI arc. Decision-light on architecture (D-033 already
ruled React), build-heavy — but with real data to build against for the first time.

---

## 0. Provenance (D-016)

Planner works from tree `6792c21` + the live prod DB. `worker/main.py`, the enqueue CLI, and
#48/#49/#50 are Builder-reported / observed via the running system, not read from the Planner's
tree. Confirm counts against prod at session start.

**What is real now, and it changes everything about this arc:** there is at least one true
`protein_analyses` row (NECTIN4, mean pLDDT 77.26), and likely ~40 after the overnight batch.
**The UI builds against real folds, not mocks.** This is why the first fold was sequenced before
the UI (1 → 2 → 3): a structure viewer built against imagined data is rebuilt when the data
arrives; built against a real PDB, it is built once.

---

## 1. What is already ruled

- **D-033** — the UI is **React consuming the FastAPI API**, superseding D-004's Streamlit
  clause. 3Dmol.js directly for structure (not `py3Dmol`, which was a Streamlit wrapper).
- **D-024** — coverage/limitations is a first-class surface: the coverage line travels with
  every ranking; held-out and excluded rows reachable; boundary method per target; provenance
  surfaced.
- **D-028** — the UI **detects and classifies** disagreement, **does not explain** it.
  Attribution is a statement about the model ("feature 6 drives this rank"), never about the
  target. Per-class quality tooltips, inline.
- **D-015 §1a** — disagreement classes visually distinct.

The UI's *purpose* is these entries made legible to a reader, including a grader. That is the
standard the build is held to, not "does it render the data."

---

## 2. What to build, in dependency order

### 2.0 — THE FIRST MOVE, ruled before any React: the read API

**This is decided, not a gap to notice.** The arc opens by ruling and building the read API,
because there is nothing for React to consume until it exists. `app/` exposes only the four
**worker→Fly** routes (claim/artifacts/complete/fail) and **zero UI→data routes** — no
`GET /analyses`, no `GET /analyses/{id}`, no way to hand a PDB to the structure viewer. You
cannot spec React against an API that does not exist, and you do not build the API without
ruling its shape first. So the sequence is: **confirm the cohort → rule the read API against it
→ build it tests-first through the gate → then React.** Same supplier-before-contract discipline
D-024 needed.

**Why it is ruled against the real cohort, not tonight's one row:** the ~40 overnight folds are
what let the read API be designed against actual data — what fields are populated, what a PDB
payload actually weighs, what a partial coverage line looks like at 40/82. Ruling it against a
single NECTIN4 row would be speccing against a sample of one. **So step 1 of the session is
looking at the landed cohort; the entry is drafted against what is seen there.**

**The decision surface the entry must settle** (these are real choices, not plumbing):
- **What `GET /analyses` returns** — the full list for a ranking table, or a lighter picker
  payload? Fold data only (exists now) vs. scorer output (does not exist yet — so: fold-only
  for this arc).
- **How the PDB is served** — inline in JSON, a separate `GET /analyses/{id}/structure`
  streaming off the Volume, or a signed URL. 3Dmol.js takes either a string or a URL, so this
  choice couples the API and the viewer.
- **Auth posture** — the worker routes carry the bearer token. A UI read API is a different
  posture, and **D-004's no-inbound-exposure constraint has something to say** — rule it
  explicitly rather than defaulting.

Everything below in §2 depends on this shipping first.

---

**Buildable once the read API exists, against tonight's folds (no scorer needed):**
- **App shell + API client** — the React foundation, talking to `pharmfoldmdk.fly.dev`. Purely
  result-independent; the safest first thing.
- **Single-target view / structure viewer** — 3Dmol.js rendering a real `structure.pdb`,
  coloured by pLDDT (the `plddt.json` is per-residue). NECTIN4 is the first test case.
- **Provenance panel** — model revision, dtype, chunk_size, source, `truncated`, mean pLDDT,
  folded_at, from `meta.fold_provenance` (D-031). Makes "we ran this ourselves" legible (D-015).
- **Coverage-line component** — the structured object from D-024 (three-cell partition + two
  breakouts). With ~40 of 82 folded it shows a real, partial coverage line.

**Waits for the scorer (step 3, NOT this session):**
- The ranking table (baseline vs structural rank, movers).
- Disagreement classes and their tooltips (D-028) — there is no structural ranking until the
  scorer runs, and no scorer until the cohort's features exist (D-027 extractor).

**So this session's honest scope: the single-target experience and the shell.** The ranking —
the demo's centrepiece, slide 8 — is real work that cannot start until features and a fit exist.
Naming that now prevents building a mock ranking that gets thrown away.

---

## 3. The read API is §2.0 — the arc's ruled first move

Promoted out of "gaps to expect" because it is now the deliberate opening, not a surprise. See
§2.0. **Confirm at session start that no `GET` route exists on `app/`** (Planner's tree shows
only the four worker routes; verify against HEAD) — if one was added, the entry adjusts, but the
decision surface (route shape, PDB serving, auth posture) still gets ruled before React.

---

## 4. Frontend-design note

Per the `frontend-design` skill and D-033: this is a graded interface whose job is to make a
scientific claim legible. Favour clarity over decoration — the disagreement-class distinction
(D-015 §1a) and the honest coverage line (D-024) are the design's substance. A beautiful UI
that flattens the class distinction fails D-028; a plain one that renders it correctly succeeds.

---

## 5. Sequence

1. **Check how the batch landed** — the `Counter` query from the run guide. `complete: 42`
   clean, or `complete: N, failed: M` with the failures to inspect (the `error` column). This
   is the cohort the read API is designed against.
2. **Look at the real cohort** — row count in `protein_analyses`, which fields are populated, a
   PDB size or two off the Volume. This is what makes the read-API entry concrete rather than
   speculative.
3. **Rule the read API** (§2.0) against what step 2 shows — route shape, PDB serving, auth
   posture, as its own entry. **This is the arc's first real decision.**
4. **Build the read API** → tests-first → required checks → deploy. The supplier.
5. **React shell + API client** against the now-existing API.
6. **Single-target view**: structure viewer (3Dmol.js + real PDB), provenance panel, coverage
   line. NECTIN4 as the first rendered target.
7. **Not this session:** the ranking view. It waits for the scorer (D-027 → fit → step 3).

---

## 6. Definition of done

- Prod state confirmed; read API ruled and built (tests-first, through the gate, deployed).
- React shell live, talking to the API.
- One real fold rendered end to end in the browser: structure coloured by pLDDT, provenance
  visible, coverage line showing the real partial-cohort numbers.
- Close-out — after the last merge.

---

## 7. Also on the board (owner actions, not UI)

- **The frozen worker requirements** — D-018 amendment PR (re-save UTF-8).
- **`docs/HAZARD-search-path-seams.md` + D-032** — stock-image correction.
- **D-030/D-031 amendment** — the measured 50 s and ~2.2× PAE ratio, and the sharper heartbeat
  motivation.
- **The large-rental first fold** — the measurement that actually tests the lease. Needs the
  A6000, and gates nothing in the UI arc.
