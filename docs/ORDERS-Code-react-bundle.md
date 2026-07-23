# Orders for Code — The React bundle: shell, target view, coverage view

**Session:** 2026-07-23 (continuing). **Planner:** Claude. **Builder:** Code.
**Entries:** `DEP-006` + `D-037` (supplied, land with the bundle).
**Spec:** **UI Plan v2** — `§3` (surfaces), `§4` (the three deliverable surfaces), `§8` (build
order), `§9` (non-goals). The plan is the spec; these orders are the sequencing and the traps.

**Target: Friday.** Steps 2–5 of UI Plan v2 §8. **Step 6 — the ranking table, disagreement
classes, attribution — is NOT in scope and must not be mocked.** It waits on the scorer.

---

## 0. Land the entries first (CLAUDE.md rule 1)

`DEP-006` (image gains a build stage + static serve) and `D-037` (JS toolchain pinning) into
`docs/README.md`. **DEP-004 is amended in the same PR** — on this merge a green deploy finally
means a UI is reachable, which it has never meant before. That is DEP-004's own stated trigger.

`ARCHITECTURE.md`: the serving tier becomes FastAPI + a static React bundle, one process.

---

## 1. Suggested PR split — three, not one

Friday is the constraint, and one enormous PR is the slower path when a check reddens.

| PR | Contents | Provable by |
|---|---|---|
| **A — the plumbing** | DEP-006 + D-037 entries, two-stage Dockerfile, static mount, `ui/` scaffold rendering one hardcoded line, CI `npm ci` step | Deploy is green **and** `GET /api/analyses` still returns JSON, not `index.html` |
| **B — the target view** | API client, structure viewer, confidence, provenance panel | NECTIN4 renders in a browser |
| **C — coverage + method note** | Coverage view, coverage-line component, ADC context page | The real 40/82 line renders |

**A is the risky one and it is deliberately tiny.** It proves the image, the route ordering, and
the deploy path with almost no UI in it. If something is going to fight, it fights there, with
nothing else in flight.

---

## 2. ⚠ Traps, verified against the tree

**(a) Route ordering will break the read API silently.** A SPA catch-all that matches `/api`
returns `index.html` with a 200 — no error, no red test, and the UI mysteriously gets HTML where
it expected JSON. **Mount `/api` and `/jobs` before the static fallback, and assert it:**
`GET /api/analyses` must return the API's JSON in the test suite, not just in a browser.

**(b) `tests/test_image_contents.py` is strict and must stay that way.** It forbids the literal
strings `torch`, `transformers`, `bitsandbytes`, `streamlit` in the Dockerfile's non-comment
lines, and asserts `copy app` / `copy core` / `copy db` are present. The two-stage rewrite keeps
all of that true. **Do not weaken the test to accommodate the build** — extend it (DEP-006 test
surface: no `npm`/`node` after the runtime `FROM`).

**(c) `.dockerignore`** excludes `tests/`, `docs/`, `scripts/`, `worker/`. **Do not add `ui/`** —
stage 1 needs it. **Do add `ui/node_modules/` and `ui/dist/`**, or the build context balloons.

**(d) The 512 MB machine.** Static assets are small, but the bundle should not be casually large.
This is the same machine that buffers upload bodies (D-035 §3c).

---

## 3. What the UI renders — from D-034's measured payload

```
GET /api/analyses            → 42 rows, 9,360 B, 12 fields, flat ~223 B/row
GET /api/analyses/{id}       → + sequence + fold_provenance
GET /api/analyses/{id}/structure → PDB, ~194–232 KB, text/plain
GET /api/analyses/{id}/plddt → per-residue array, ~6 KB
```

**Target view (UI Plan v2 §3.2):**
- **3Dmol.js loads the structure BY URL**, not as an inline string — D-034 decision 2 served it
  from its own route precisely so the browser caches it independently of the metadata.
- **Colour by pLDDT** from the `/plddt` array. This is the deep-learning output made visible; it
  is not decoration.
- **Provenance panel:** `model_id`, `model_revision`, `dtype`, `chunk_size`, `truncated`,
  `folded_at`, `input_length`, `ca_atom_count`, `boundary_method`, `uniprot_release`. **This is
  what makes "we ran ESMFold ourselves, at a named revision" checkable rather than asserted.**
- **Boundary method per target** (D-024): `sliced_ecd` with its bounds, or `whole` — and for a
  `whole` fold, that it *has no sliceable ECD* is the reason and belongs on screen.
- **NECTIN4 (`id 1`) is the first rendered target.**

**⚠ Confidence is not a bare number.** Measured `mean_plddt` runs **34.78–81.40**; roughly a
third of the cohort is below 60, where an ESMFold structure is not reliably interpretable.
Rendering a 34.78 structure identically to NECTIN4's 77.26 is the D-024 failure in miniature.
**Bands are needed** — UI Plan v2 §10 flags the exact boundaries as a small open ruling.
**Propose them in the PR with a justification** (ESMFold/AlphaFold pLDDT convention is a starting
point, not an authority) and they get ruled on review.

**Coverage view (§3.3):** the three-cell partition + two breakouts, from `core/manifest.py`'s
existing object. Today it renders a real **40 ranked-and-folded of 82**. Held-out and excluded
rows must be **reachable**, not silently absent (D-022: *"MUC16 is CA-125; a reviewer who knows
the field notices its absence immediately"*).

---

## 4. Design

Read `/mnt/skills/public/frontend-design/SKILL.md` before writing components.

UI Plan v2 §1 is the brief, and D-033 states the standard: *"A beautiful UI that flattens the
class distinction fails D-028; a plain one that renders it correctly succeeds."* Clarity over
decoration. The honest coverage line and the provenance panel **are** the design's substance.

---

## 5. Non-goals — commitments, not omissions (UI Plan v2 §9)

No accounts, no login, no settings. **No on-demand folding — a page load must never trigger
inference** (on a paid card that is a cost bug). No sequence input. No mutation simulator, pocket
scores, report generation, or semantic search. **No mock ranking, no placeholder disagreement
classes.** No PAE visualization — no route serves it.

**Dependency discipline (D-037):** React, a router, 3Dmol.js. Beyond those, justify. A chart
library for one pLDDT plot is a real question and hand-rolled SVG is a legitimate answer.

---

## 6. Definition of done

- `DEP-006` + `D-037` landed; DEP-004 amended; `ARCHITECTURE.md` current.
- Three PRs, each through both required checks, each deployed.
- **NECTIN4 rendering in a browser at `pharmfoldmdk.fly.dev`** — structure coloured by pLDDT,
  provenance visible, boundary method shown.
- The coverage line showing the real partial-cohort numbers.
- `GET /api/analyses` still returns JSON — asserted in the suite, not just observed.
- **Report:** the confidence-band proposal and its justification; the built bundle's size.

---

## 7. Standing instruction

Unchanged from part 2, and it has now paid for itself twice today. If the plan is wrong against
the tree, **surface it rather than working around it.** An entry before code, never a workaround.
