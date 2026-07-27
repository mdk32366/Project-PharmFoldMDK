# Session Brief — Code, 2026-07-26 (open with this)

You are the **Builder**. I am the Planner. The owner (Matt) decides all merges. Three PRs today,
sequenced. Detail lives in two orders documents; this is the baton, the sequence, and the contract
for what you hand back.

## Documents — read in this order

1. `docs/CLOSEOUT-2026-07-25.md` — where yesterday ended.
2. `PREWORK-2026-07-26.md` — today's grounding and the rulings already made.
3. `ORDERS-Code-2026-07-26-D-051-D-052.md` — **PR 1 and PR 2.**
4. `ORDERS-Code-2026-07-26-D-053-D-054.md` — **PR 3.**

Everything below assumes you have read all four. Where this brief and an orders doc disagree, the
orders doc wins on detail; this brief wins on sequence.

---

## 0. Pre-flight — do this before writing anything

```
git log --oneline -3          # snapshot was 0aa4fbf; confirm and report if it has moved
pytest -q                     # report the REAL number
cd ui && npm test             # expect 30 passing across 6 files
```

**Report all three numbers before starting.** The Python baseline of ~232 is *inherited from
yesterday's closeout and has not been verified this session* — I counted 227 `def test_` statically
and could not run the suite. Whatever `pytest -q` actually says is the baseline of record from here.

**If the suite is red at HEAD, stop and report.** Do not start a PR on a red base; you will not be
able to tell your failures from the ones already there.

**One file needs placing before PR 3:** the owner will supply `cancer_associations.csv` (a Planner
artefact, not in the repo yet). It goes to `data/cancer_associations.csv`, committed **verbatim,
header comment block intact** — the header is part of the artefact. Verify on arrival: 337 data
rows, 82 unique symbols, zero rows with an empty `source_citation`.

---

## 1. Sequence — three PRs, in order, no combining

| PR | Contents | Gate on |
|---|---|---|
| **1** | D-051 — architecture contract test, `system-model.json`, diagram, Story surface, nav restructure to five, `ARCHITECTURE.md`, plus the two small fixes (`77.26`, `CoverageLine`) | green |
| **2** | D-052 — the ADC mechanism schematic | green |
| **3** | D-053 + D-054 entries; associations supplier, route, component | green |

PR 1 must land before PR 3, because PR 3 adds a route that PR 1's contract test is supposed to
catch. Do not reorder them to save time — the ordering *is* one of the tests.

**Per PR, without exception:**

- Log entry into `docs/README.md` **first**, before the code it describes.
- Tests written before implementation. **Red first, and captured** — paste the failure output into
  the PR description. A test that never went red is not confirmed to bite.
- `ARCHITECTURE.md` current before the PR is filed (CLAUDE.md rule 2).
- Gate green — `test` (pytest + UI vitest), `postgres`. **You do not merge.** Owner merges.
- Nothing deploys that has not passed the gate.

---

## 2. The free check — report it either way

PR 3 adds `GET /api/associations`. If PR 1's architecture contract test is doing its job, PR 3
should turn it **red** until `system-model.json` lists the new route, then green once it does.

**Report what actually happens.** If it goes red — the mechanism built this morning is proven live,
on the same day, by an unrelated change. If it does *not* go red, the contract test is decorative
and PR 1 needs revisiting before delivery. This costs nothing and is the most informative single
observation available today, in either direction.

---

## 3. Stop conditions — report, don't work around

Stop and report rather than proceeding if:

- **A contract or pin test won't pass and the tempting fix is to loosen the assertion.** A test that
  passes because it stopped checking is worse than no test — it reports coverage it does not have.
  This applies specifically to the D-051 route-set equality and the D-053 real-file pin.
- **FastAPI route introspection is messier than the orders assume** (mounts, the SPA catch-all,
  `/openapi.json`). Propose the alternative; do not write around it quietly.
- **The nav move to five surfaces breaks something I did not find.** I checked — nothing asserts
  what `/` renders, and `test_ui_serving.py` asserts only route ordering. If there is a dependency I
  missed, that is a finding, not a patch.
- **The associations CSV does not reproduce for you** — 337 pairs, 82 targets, zero unmatched. I
  derived that file; I did not transcribe it. If your numbers differ, yours outrank my orders.
- **Anything in the orders is wrong.** Both orders docs end with a section naming where I am most
  likely to be wrong. Those are invitations, not disclaimers.

---

## 4. What to hand back (the closeout depends on this)

For each PR: branch name, merge SHA, the red-then-green evidence, and the test-count delta.

At session end, one report containing:

1. **Real suite counts** — Python and UI, before and after.
2. **Merge SHAs** for all three PRs, and main's final SHA.
3. **The contract-test observation** from §2 — red or not red.
4. **What did not ship**, and why. Expected still-standing: the ranking table (blocked on the
   scorer, deliberately not mocked), the evidence baseline (D-054, deferred with a trigger), the
   remaining untested components, and the 07-25 §5 doc fixes if they did not fit.
5. **Anything you found that contradicts these orders**, including anything that contradicts my
   reading of the repo in `PREWORK-2026-07-26.md` §0. Twelve premise corrections are on record;
   the thirteenth is more valuable than a clean report.

---

## 5. The through-line, so you know what to protect when a trade-off appears

Every surface shipping today is a **claim about the system**, and each gets the same treatment every
other claim in this project has had: **derived if it is a number, pinned by a test if it is a
structure, labelled if it is an illustration.** When something has to give under time pressure, give
up scope — a surface can be dropped. Do not give up the derivation, the pin, or the label on a
surface that ships. A decorative honesty layer is worse than none, because it claims a rigour it
does not have, on the one project whose entire argument is that it does.
