# Orders for Code — sortable column headers on the target list (buildable NOW, on current data)

> **⚠ WHY THIS IS NOT GATED.** Sorting is a pure presentation change over data that already exists in
> `/api/analyses`. It needs no census, no D-075 result, no new fold, no scorer change. It pays off on
> the current ~79 targets AND becomes essential when the census adds thousands of rows — and it is
> deliberately built NOW, on a small eyeball-able set, so the sort interaction is proven before it
> ever faces thousands of rows where a sort bug is invisible.
>
> **Scope:** `ui/src/components/TargetList.jsx` + its test. Possibly a small shared sort helper +
> its own test. **NOT** `app/`, `core/`, `db/`, the API, the scorer, or the ranking computation.
>
> **NOT in this PR:** any census column (cancer / prevalence / lethality / served-status — those are
> gated on the census existing, `SPEC-tranche-ui-future.md`); any new API field; any change to what
> `/api/analyses` returns. This makes the columns that ALREADY exist sortable — nothing more.

---

## 0. What the Planner read in the repo (grounding)

`ui/src/components/TargetList.jsx` today:
- Renders a table: **Gene · Accession · Tier · mean pLDDT · Confidence.**
- Default sort: `[...filtered].sort((a, b) => (b.mean_plddt ?? 0) - (a.mean_plddt ?? 0))` — pLDDT
  descending (most-interpretable first). **⚠ The `?? 0` is the honesty trap this order must fix — see §2.**
- Has a **tier filter** (`tierFilter` state) with a D-028 note that tier is a filter, NOT a quality
  sort key. **This must keep working through sorting.**
- Derives everything live (no literal max — D-049/D-050). No hardcoded counts.
- Test contract (`TargetList.test.jsx`): tier shown per row, tier filter narrows/restores, and
  **"does NOT blend tiers into a combined quality score" (D-028).** All must stay green.

---

## 1. The feature

Make each column header a click-to-sort control:
- **First click** sorts ascending by that column; **second click** descending; a third returns to the
  **default** (pLDDT desc — the current behaviour, which must remain the initial state).
- Sortable columns: **Gene** (alphabetical), **Accession** (alphabetical), **Tier** (categorical —
  but see §3 caveat), **mean pLDDT** (numeric). **Confidence** sorts by the underlying pLDDT (it is a
  band OF pLDDT, so sorting it separately would be a second axis for one quantity — the
  two-sources-for-one-value trap; sort Confidence by mean_plddt or omit its header control).
- The active sort column + direction is **visibly indicated** in the header (arrow/caret), so the
  reader always knows how the list is ordered — an unlabelled sort is a silent reordering.
- **Default state unchanged:** on load, pLDDT desc, exactly as now. The most-interpretable-first story
  (and the "no target reaches high-confidence" ceiling read) survives.

---

## 2. ⚠ THE LOAD-BEARING RULE — absent values are a category, never a low number

The current `?? 0` coerces a missing pLDDT to zero, so an unmeasured target would sort as though it
scored the *worst*. On the folded-only list today this is latent; as a general sort mechanism (and
certainly once unscored census rows exist) it becomes a lie: **"no measurement" rendered as "lowest
measurement."**

**The rule:** rows with an absent sort value (`null`/`undefined` pLDDT, no score, etc.) are a
**distinct group that stays visibly present and labelled**, never silently sorted to the bottom as a
zero. Concretely:
- Absent-value rows sort as a **separate cluster** (conventionally after the measured rows in either
  direction), each still showing its `—` and its reason, never coerced to 0 and interleaved with real
  low scores.
- **Never drop or hide** a row because it lacks the active sort key. The project's whole coverage
  discipline (`CoverageView`, `Story`: every target present with its reason) must survive sorting.
- This is the rule that makes sortability compatible with the project's honesty rather than a quiet
  erosion of it. It is not optional polish.

**Test it (red first):** a fixture including a row with `mean_plddt: null` — sorting by pLDDT (either
direction) must keep that row rendered and labelled `—`, and must NOT place it as if it were the
lowest numeric value among measured rows. A naive `?? 0` implementation fails this; the fix passes it.

---

## 3. Preserve what exists (tests that must stay green)

- **Tier filter keeps working** — sorting and filtering compose: filter narrows the set, sort orders
  what remains. The three existing tier tests must pass unchanged.
- **D-028 — no combined score.** Sorting BY a single existing column is fine. **Do NOT invent a
  composite/blended sort key** (e.g. a "quality" sort mixing pLDDT and tier) — that is exactly the
  collapse D-028 forbids, and the existing test asserting no "blended/combined score" language must
  stay green. Tier remains a filter; if Tier is sortable it sorts alphabetically by tier label, with
  no implication of quality order.
- **Derive-don't-inscribe** — no literal counts or maxes introduced.

---

## 4. Tests (red first)

- **Sort by each column** reorders rows correctly (ascending then descending then default) — fixture
  with distinct values so order is unambiguous.
- **Absent-value rule (§2)** — the `null` pLDDT row stays present, labelled, not coerced to 0.
- **Active-sort indicator** renders and reflects the current column/direction.
- **Default on load is pLDDT desc** (current behaviour preserved).
- **Tier filter + sort compose** — filter to rental, sort by gene, both hold.
- **Existing `TargetList.test.jsx` cases pass unchanged** (tier legibility, filter narrow/restore,
  no blended score).

## 5. Order of work

1. Tests red first (per-column sort, absent-value rule, indicator, default-preserved, filter+sort compose).
2. A small pure sort helper (`(rows, key, dir) -> rows`) that encodes the absent-value rule in ONE
   place, with its own unit test — so the "absent is a category" logic is testable without rendering
   and reusable when census columns arrive.
3. Wire clickable headers + indicator into `TargetList.jsx`, default state unchanged.
4. Confirm the existing tier tests pass; gate; dry-diff; owner merge. **This deploys** — verify live
   that headers sort and the default order is unchanged post-deploy.

## 6. ⚠ Four things that will bite

1. **Do not coerce absent to 0.** The `?? 0` must go; absent is a labelled category (§2). This is the
   whole point of doing it now on 79 rows — get the rule right where you can see it.
2. **Do not change the default.** pLDDT desc on load; the ceiling-at-a-glance story depends on it.
3. **Do not invent a composite sort key** (D-028). One column at a time; tier stays a filter/label.
4. **Do not add census columns.** Cancer/prevalence/lethality/served are gated (census spec). This PR
   sorts the columns that exist. Build the mechanism; the future columns plug into it later.

## 7. What "done" means

Every existing column header sorts (asc/desc/default) with a visible active-sort indicator, absent
values stay present and labelled as a category (never coerced to a low number), the tier filter and
all existing tests stay green, the default load order is unchanged, the sort logic lives in one tested
helper ready for future columns, gate green, verified live post-deploy.

## 8. Why the helper matters for the future (context, not scope)

The census will add cancer-association, prevalence, lethality, and served-status columns. If the sort
logic — especially the absent-value rule — lives in one tested helper now, those future columns become
new sort keys in a proven mechanism, and the "unmeasured is a category, not a zero" discipline is
already enforced for them. Building the interaction on 79 eyeball-able rows first is deliberate:
a sort bug at 2,886 rows is invisible; at 79 it is obvious. This order builds the substrate; the
gated census UI (`SPEC-tranche-ui-future.md`) adds columns to it later.

## 9. If something is wrong with these orders

Say so before building. Specifically: if the current list genuinely never receives absent-pLDDT rows
(folded-only), the absent-value rule is still built and tested against a fixture — because the census
WILL send them and the rule must exist before it does, not be retrofitted under pressure. Do not skip
§2 on the grounds that today's data doesn't trigger it.
