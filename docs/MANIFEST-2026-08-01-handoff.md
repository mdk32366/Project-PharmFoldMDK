# Package Manifest — 2026-08-01 session handoff (Planner → owner → Coder)

This is the index for everything produced this session. It states what each artifact is, the order to
stage/hand off, the dependency chain, and — most important — **every item that needs the owner's hand
before it merges or runs.** Nothing here has touched the repo, the gate, or the deployed surface.

---

## 1. What this session was

A planning-and-artifacts session, post-demo. It produced: one correction to the demo record, a
kickoff kit (deck + two reference docs), a scoped fold plan (D-072), an adversarial second opinion
(Grok) that became a pre-registered ablation (D-075), a cohort-boundary finding (F-009), a two-phase
roadmap, and **two Coder orders** (D-075, the held-out set). The semester is over; the optimization
target is now **a publishable paper**, and D-075 is the fork that decides which paper exists.

**No code was written. No PR opened. No run executed.** All execution is Coder's, in-repo, next.

---

## 2. The artifacts, by type

### Coder orders — the executable handoff
| File | What Coder does | Priority | Gate |
|---|---|---|---|
| `ORDERS-Code-2026-08-01-D-075-ablation.md` | Build the confidence-blind proxy ablation + attention control (extends D-065) | **TIER 0 — first** | Confirm D-065 status (§0) before starting |
| `ORDERS-Code-2026-08-01-heldout-validation-set.md` | Phase A: curate Kathad-excluded ADC targets (now). Phase B: fold+validate (gated) | TIER 1 | **Phase B gated on D-075 surviving** |

### Log entries — merge these (log leads code)
| File | Type | Number status |
|---|---|---|
| `CORRECTION-2026-08-01-nectin4-score.md` | Correction (NECTIN4 score/frame) | place where corrections live |
| `D-072-last-three-fold-plan.md` | Decision (the last three targets) | ⚠ **D-072 is TAKEN** (miniature notebook, `d46aa1a`) — renumber, next free is **D-076** |
| `D-075-pLDDT-ablation-preregistered.md` | **Decision** spec (reconciled to defer to the order) | ✅ **resolved: D-075** — drafted `F-008`, which was taken (`754e58f`); landed as a decision, not a finding |
| `F-009-cohort-boundary-false-negatives.md` | Finding (cohort = comparator; 4 false negatives) | ✅ **resolved: F-009** — confirmed free (highest merged finding was F-008) |

### Planning / vision
| File | What |
|---|---|
| `ROADMAP-phases-and-enhancements.md` | Two-phase architecture + stack-ranked enhancements + the D-075 fork |
| `CLOSEOUT-2026-08-01.md` | Session closeout |
| `PREWORK-next.md` | Baton into next session (spine = D-075) |
| `GROK-PROMPT-second-opinion.md` | The adversarial-review prompt (reusable) |

### Kickoff kit (owner eyeball needed — preview tool was down at build)
| File | What |
|---|---|
| `PharmFoldMDK_Deck.pptx` | 14-slide pitch, null-first framing |
| `PharmFoldMDK_Literature_Review.docx` | 7-paper novelty assessment |
| `PharmFoldMDK_Held_Out_Logic.docx` | The four exit reasons in depth |
| `PharmFoldMDK_Slide_LastThree.pptx` | Standalone last-three slide (also in deck) |

---

## 3. The dependency chain (what gates what)

```
D-065 (already exists — CONFIRM status)
   └─> D-075 order  [TIER 0, executes first]
          │
          ├─ SURVIVES ──> Branch A paper
          │                 └─> Held-out set Phase B (fold+validate)  [gated — runs only here]
          │                 └─> Roadmap Tier 1: expand positives past n=12
          │                 └─> Roadmap Tier 3: census + stacking (Phase 2, later)
          │
          └─ COLLAPSES ──> Branch B paper (cautionary methods)
                            └─> Held-out set Phase B ABANDONED (not deferred)

Held-out set Phase A (curation)  ── runs NOW, ungated, regardless of D-075
IGF2R fold (D-072 Tier 1)        ── runs NOW, ungated, cheap, no asterisk
```

**The single governing line:** D-075 decides which paper exists. Do not start Phase 2 (census,
stacking) or the held-out fold before it survives.

---

## 4. ⚠ Owner actions required before anything merges or runs

These are the things the Planner cannot resolve — they need the repo, UniProt, or an owner decision.

1. ~~**Confirm all new entry numbers**~~ — **DONE 2026-08-01.** Verified against the live
   `docs/README.md` (highest merged: **D-074**, **F-008**). Resolved: the ablation → **D-075** (drafted
   `F-008`, taken); cohort-boundary → **F-009** (free). **Still open: `D-072-last-three-fold-plan.md`
   is misnumbered** — D-072 is the miniature notebook (`d46aa1a`); next free is **D-076**. The
   held-out entry is unassigned until it lands.
2. ~~**Confirm D-065's status**~~ — **DONE 2026-08-01.** D-065 is **merged** (`e309545`, PR #91) **and
   its ablations have run** (F-005, `42a74ad`, PR #92; `no_plddt` = `ranking_run` id=3, `plddt_only` =
   id=4, `scorer_version=a927dc4532b7`). This is the §0 **proceed** branch, so `no_plddt` is a
   *measured* baseline, not a hypothetical — its real numbers anchor D-075 Decision 0/4.
3. **Verify three accessions** against UniProt before F-009 and the held-out set merge:
   CD30/TNFRSF8 (P28908?), CEACAM5 (P06731?), Trop-2/TACSTD2. **CD33 = P20138 is confirmed.**
   (Same discipline that caught the "first ADC" slip — check, don't recall.)
4. **Check IGF2R's label status** against `data/adc_reference_mapping.csv` before folding it — decides
   whether its fold moves F-004's denominators (D-072 §4).
5. **Eyeball the four kickoff-kit files** — the preview tool was down at build, so they were verified
   by structure/text, not by eye. Particular attention: deck slides 5 and 9 (the funnel/card layouts).
6. **Verify Site4Drug (arXiv 2606.01816)** and add the **PNAS 2026 surfaceome paper** before the lit
   review is used in a novelty claim (both flagged in the closeout).

---

## 5. Recommended handoff order to Coder

1. **D-075 order first** — it's Tier 0 and blocks the fork. Coder confirms D-065, lands the entry +
   frozen interpretation, builds tests-red-first, merges. Owner authorises the run.
2. **Held-out order, Phase A only** — can run in parallel with D-075 (no fold dependency). Produces
   the verified CSV. Phase B stays sealed until D-075's result.
3. **IGF2R fold (D-072 Tier 1)** — cheap, ungated, whenever a rental block is convenient.
4. Everything else (roadmap Tier 1+, Phase 2) waits on D-075's result per the chain in §3.

---

## 6. The one-line status

Two Coder orders ready (D-075 executes first; held-out set curates now, folds on survival), four log
entries to merge, a kickoff kit to eyeball, and six owner actions gating the merges. The project's
next real inflection is D-075's result — everything downstream branches on it. Nothing here is
shipped; it is staged, cross-checked, and ready to hand over.
