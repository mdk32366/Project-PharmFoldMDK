# Pre-Work — next session (post-2026-08-01)

> **Grounding:** confirm main with `git log --oneline -1` before any work. Read first:
> `CLOSEOUT-2026-08-01.md`, then `D-075-pLDDT-ablation-preregistered.md`,
> `F-009-cohort-boundary-false-negatives.md`, the correction note, and
> `D-076-last-three-fold-plan.md`.
> **Character of this session, chosen deliberately:** the last session produced *artifacts, a plan,
> and a second opinion that wrote a test the current result cannot yet pass.* This session's spine is
> **D-075 — the pLDDT-ablation** — because it is the single highest-leverage thing on the project:
> it either hardens the headline against the sharpest external critique or converts a hidden weakness
> into a stated finding. Around it: execute the one unambiguous fold (IGF2R), land the F-009 cohort
> framing, and merge the staged entries. It is a **refit-and-verify session**, not a build arc — D-075
> folds nothing new.

---

## §0 — Before anything: three cheap confirmations

None of these is building; all three prevent a wrong step.

1. **Confirm the D-072 number.** The live log is ahead of the project snapshot. Read
   `docs/README.md` for the highest D-entry; renumber the drafted D-072 if taken. Log leads code —
   this entry must be real before any fold it authorises runs.
2. **Check IGF2R's label status** against `data/adc_reference_mapping.csv`. It is not one of the 12
   named positives, but confirm by symbol/accession. **This decides whether folding IGF2R moves
   F-004's denominators** — if it is a labelled positive above the pLDDT floor, its fold is a
   pre-authorised result update (D-072 §4), and you want that known *before* the fold, not after.
3. **Re-read the correction note.** The one standing risk from the demo is the *frame*, not the
   number. Any artifact or talk that leads with NECTIN4-ranks-high reintroduces the pLDDT-attention
   confound. The staged deck already leads with the null; keep it that way in anything derived.

---

## §1 — The priority: run D-075, the pLDDT-ablation (the sharpest test the project has)

This is the spine. The Grok second opinion escalated the pLDDT-attention confound from an open caveat
to a potentially load-bearing objection and named the test F-004 never ran. D-075 runs it, both
outcomes pre-registered. **Do this before the artifacts get pitched to anyone**, because it decides
whether the headline survives contact with the critic.

**Order within D-075 (do not reorder — the freeze discipline is the point):**

1. **Confirm the D-075 number** against `docs/README.md`; renumber if taken.
2. **Build the pLDDT-free proxy** (membrane-proximal SASA from raw coordinates) **red-then-green.**
   The test that must bite first: two structures, identical backbone, different pLDDT columns → must
   yield **identical** proxy value. Red on a deliberately contaminated impl, green on the clean one.
   **If the proxy ever reads the pLDDT/B-factor column, the whole ablation is void** — this is the
   one place a silent leak destroys the result while looking clean (F-004 §7 failure class).
3. **Freeze the proxy** — definition, window, extraction — **before the refit runs.** No inspecting
   the result then tweaking the proxy. Verified, not assumed.
4. **Run A (primary):** refit the L2 logistic on the 4 non-pLDDT features + the proxy, same λ/LOO
   mechanic, same 12 positives, same floor. Recompute the 12 LOO percentiles, the head-to-head on the
   8, and the Spearman. **Read the §3 interpretation of D-075 that fires — but have both in front of
   you before you look at the numbers.**
5. **Run B (sensitivity):** popularity-matched control on **both** PDB-presence (B1) and publication
   count (B2), proxies frozen with source + date. Only meaningful if Run A survives; if A collapses,
   B is moot and that's recorded.
6. **Record D-075 through the gate**, the interpretation that fired, no silent edit. If the headline
   changed (collapse case), the deck + lit review update to the true post-ablation status.

**The mindset (from the closeout):** a survival hardens the claim; a collapse is a *real finding*,
better found by us than by the room. The only losing move is not running it. Grok wrote the test; go
pass it, or learn something real from failing it.

## §1b — The one executable-now fold: IGF2R (Tier 1)

This is the only fold with no asterisk and no utility question. Do it early; it is the session's
concrete deliverable.

- **Re-enqueue IGF2R on the rental tier**, recipe resolved at fold time (D-047), sequence length
  checked against what ceilinged last run. If it still ceilings on the A6000, escalate one rung
  (H100 80 GB, same workflow). **Same ESMFold-v1 / sliced-ECD recipe as the other 79** — its six
  features are directly comparable.
- **On success:** cohort 79 → 80. Every coverage/ranking number **re-derives from the endpoints**
  (`/api/coverage`, `/api/ranking`) — no re-hardcoding (stale-literal discipline). If §0.2 found
  IGF2R labelled and above floor, F-004's denominators update; run that through the gate as a
  result update, not a silent edit.
- **On failure at the next tier too:** record it as a finding (the ceiling is real at a named size)
  and IGF2R joins the "on ice" set — but that is the unlikely branch; IGF2R is ordered and was a
  transient-ceiling casualty, not a size wall.
- **What this is NOT:** it is not FAT2 or MUC16. Those stay on ice behind the novelty trigger
  (D-072 §3). Resist folding them to look complete — that is the one move that spends honesty
  capital for coverage optics (D-072 §5).

---

## §2 — Land F-009 (the cohort framing) and close the citation verifications

Desk work, not code. Makes the artifacts answer the "your list is incomplete" question before it's
asked, and hardens the novelty claim.

1. **Land the F-009 comparator-not-census framing.** Confirm the F-009 number. Add a line to the deck
   (cohort/methods slide) and the held-out-logic doc: *the 82 is Kathad's expression comparator, not a
   target census; CD30, CEACAM5, and Trop-2 are clinically-validated ADC targets its filters excluded
   — which is why an orthogonal axis is worth testing.* **Keep the §3 guard:** indict the comparator,
   never claim "our scorer would have caught them." Log the held-out-positive label set as future work
   (it may be the answer to Grok's sinking question — see F-009 §4).
2. **Add the PNAS 2026 surfaceome-mapping paper to the lit review** as the true nearest neighbour Grok
   surfaced, with the explicit distinction: it scores *site-level* geometric/chemical features for
   binder-seed design; this project computes *target-level* ECD statistics to re-rank an expression
   cohort. Make the distinction, don't assume it.
3. **Verify Site4Drug (arXiv 2606.01816)** and SEPPA/SITA by opening the primary sources — still
   provisional (snippet-cited). If closer to target-ranking than framed, fold it in.
4. **Drop method-novelty language** across the deck and lit review in favour of *"first honest
   measurement of an under-explored axis"* — Grok's "incremental / manufactured gap" critique is
   partly fair and this is the defensible framing.

*(The Grok second opinion itself is DONE — it ran this session; §1 and this section are its output.)*

---

## §3 — What merges, and in what order

The staged documents are the owner's to place. Sequencing when they land:

- **D-075, D-072, F-009** merge as log entries first (log leads code), numbers confirmed. D-075's
  interpretation section must be committed **before** the refit runs — that is what makes it
  pre-registered rather than post-hoc.
- **The correction note** is placed where the project keeps corrections.
- **The lit review** merges only after Site4Drug is verified **and** the PNAS 2026 paper is added
  (§2.2–2.3) — an unverified or incomplete citation set in a novelty claim is exactly what the
  discipline exists to prevent.
- **The deck and held-out doc** merge after the F-009 cohort line is added and any method-novelty
  language is dropped (§2.4), pending the owner's eyeball on the two funnel/card slides (preview tool
  was down when they were built).
- **The result-bearing artifacts (deck result slides, lit-review F-004 section) may need a second
  update after D-075 runs** — if the ablation changes the headline, they change with it. Don't treat
  them as final until D-075 has a result.

---

## §4 — What this session is not

- **Not the scorer arc, not the ranking table's deferred columns.** Those remain where F-004 /
  D-062 left them — deferred, not mocked. Nothing here reopens them.
- **Not FAT2 or MUC16.** On ice, trigger unmet (D-072 §3).
- **Not a build arc.** If it turns into one, that is scope growth from a session that was meant to
  confirm, fold once, and verify. Name it if it happens.

---

## §5 — Start-here

1. §0 — three confirmations (D-072/D-075/F-009 numbers, IGF2R label, correction frame).
2. **§1 — D-075 the ablation: build the pLDDT-free proxy red-then-green, freeze it, run A, then B.**
   This is the spine. Have both pre-registered interpretations in front of you before reading numbers.
3. §1b — fold IGF2R; update results through the gate if it lands.
4. §2 — land F-009 cohort framing, add PNAS 2026, verify Site4Drug, drop method-novelty language.
5. §3 — merge the log entries (D-075 interpretation before its refit), then place the artifacts.

**The through-line into the next kickoff:** the demo proved the honesty layer holds under a grader
who wasn't probing it — and then an adversarial second opinion probed the *one* thing the grader
didn't, and found the confound F-004 had named but never tested. That is the project working exactly
as designed: someone wrote the test that bites, and the response is to run it, not to argue the score.
D-075 is that test. If the geometric signal survives without the confidence features, the headline is
bulletproof; if it doesn't, the collapse is a real finding and a better label (the F-009 held-out set)
is the path forward. Either way, the room's sharpest question gets answered by us, first. Add the
cohort-boundary framing so "your list is incomplete" becomes a supporting data point, fold IGF2R to
close the one honest coverage gap, and the kickoff kit is not just polished but *stress-tested.*
