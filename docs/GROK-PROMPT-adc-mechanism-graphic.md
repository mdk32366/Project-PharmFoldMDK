# GROK PROMPT — the ADC mechanism graphic for the About ADCs surface

> **Purpose.** Regenerate the 5-panel ADC mechanism cartoon so it can replace `AdcSchematic.jsx`
> on `/about` without contradicting the copy beside it.
>
> **Status:** the graphic is NOT yet approved for the surface.
>
> | version | time | sha256 (first 8) | verdict |
> |---|---|---|---|
> | `grok-image-2e6b3470…` | 11:49 | `A5B26E31` | ❌ rejected — all five defects |
> | `grok-image-3f66b6ae…` | 11:54 | `A2D7EB2F` | ❌ rejected — added caption text, corrected **nothing**; the new Step 3 caption put the thyroid error into prose |
> | `grok-image-9e579701…` | 12:09 | `D48547A2` | ⚠ **all five original defects FIXED**, two new word-level errors introduced (see §3) |
>
> ⚠ **A corrected image still needs a `D-096` log entry before it lands**, because swapping it in
> replaces a component built under **D-052** (hand-rolled SVG, structurally incapable of reading as
> a model output) on the surface **D-094** governs. That is a design decision, and the log leads the
> code.

---

## What was wrong, so it is not reintroduced

| # | Defect | Why it matters |
|---|---|---|
| 1 | ⚠⚠ **"cancerous thyroid cell" / "Thyroid cell"** | **PADCEV (enfortumab vedotin) targets Nectin-4 in UROTHELIAL (bladder) carcinoma.** Thyroid is simply the wrong organ, and `AdcContext.jsx:59` and `:74` say "bladder cancer" and "metastatic urothelial carcinoma" **on the same screen**. |
| 2 | ⚠ **"PADCEV — the cancer destroyer"** | The page's thesis one line below is *"The metaphor is about delivery, **not cure**."* The surface is deliberately written to avoid over-claim vocabulary rather than negate it (`AdcContext.jsx:123`). |
| 3 | ⚠ **"Step 2: Neutralization"** | Not an ADC step. Neutralization is what a blocking antibody does. An ADC **binds, is internalised, traffics to the lysosome, releases payload, kills the cell.** v2's own caption ("attaches to the NECTIN-4 protein") contradicts the title above it. |
| 4 | ⚠ **Step 5 kills the whole butterfly-shaped gland** | Conflates one cell with an entire organ, and implies destroying the organ is the goal. The payload kills **the targeted cell.** |
| 5 | Lowercase "padcev" / "nectin-4" mid-sentence | Inconsistent with the labels in the same image. |

---

## THE PROMPT — paste this

```
Create a 5-panel educational comic strip explaining how the antibody-drug conjugate
PADCEV (enfortumab vedotin) works. Keep the exact art style of the previous version:
glossy 3D-rendered cartoon, deep blue starfield background, bright yellow title
banners with black text, a friendly blue Y-shaped antibody character with large
expressive eyes, and white handwritten-style annotation labels with arrows.

CRITICAL FACTUAL REQUIREMENTS — the previous versions got these wrong:

1. The cancer cell is a UROTHELIAL (BLADDER) CANCER CELL. It is NOT a thyroid cell.
   Remove every occurrence of the words "thyroid" and "gland". Label it
   "cancerous urothelial (bladder) cell".

2. Do NOT call PADCEV "the cancer destroyer" or any similar phrase. Label it
   "PADCEV - an antibody-drug conjugate". It is a targeted delivery vehicle,
   not a cure.

3. Panel 2 is "Binding", NOT "Neutralization".

4. In the final panel, ONE cancer cell dies - not an organ. Keep it at the same
   scale as the cell shown in panels 1 through 4.

5. Write PADCEV and NECTIN-4 in consistent capitals everywhere.

THE FIVE PANELS:

Panel 1 - "Step 1: Binding"
  A single rounded cancerous urothelial (bladder) cell. Small protein shapes
  stick out of its surface. The blue antibody character floats above, reaching
  toward one of them.
  Labels: "PADCEV - an antibody-drug conjugate" with an arrow to the antibody;
  "NECTIN-4 - a protein on the surface of the cancer cell" with an arrow to a
  surface protein; "cancerous urothelial (bladder) cell" with an arrow to the cell.

Panel 2 - "Step 2: Internalization"
  The antibody, still gripping the NECTIN-4 protein, is drawn inward as the cell
  membrane folds around it, forming a pocket.
  Caption: "The cell pulls PADCEV inside, still attached to NECTIN-4."

Panel 3 - "Step 3: Lysosome"
  The antibody is now inside a rounded internal compartment within the cell. The
  compartment glows faintly to suggest it is breaking things down.
  Caption: "Inside the cell, the linker is cut and the payload comes free."

Panel 4 - "Step 4: Payload Release"
  The payload - small glowing capsule shapes, NOT hand grenades - scatters out
  from the antibody into the cell interior.
  Caption: "MMAE, the cytotoxic payload, is released inside the cell."

Panel 5 - "Step 5: Cell Death"
  The SAME SINGLE CELL from panel 1, now shrunken, darkened and collapsing
  inward. Same scale as before. No organ, no anatomy beyond the one cell.
  Caption: "The payload disrupts the cell's internal scaffolding and the cell dies."

Wide horizontal layout, five equal panels side by side separated by thin dark
gutters. Text must be large and legible.
```

---

## §3 — THE v3 FOLLOW-UP PROMPT — two words, nothing else

⚠ **Minimal-change instruction on purpose.** v2 proved that a regeneration can change everything
except what was asked. Re-verify all five original defects after this pass; do not assume they held.

```
This is very close. Keep the image EXACTLY as it is - same five panels, same art
style, same layout, same characters, same captions - and change only TWO WORDS:

1. Panel 4 currently reads "MMAE, the cytoplasmic payload, is released inside the
   cell." Change "cytoplasmic" to "cytotoxic". It should read:
   "MMAE, the cytotoxic payload, is released inside the cell."

2. Panel 1 currently reads "PADCEV - an antibody-drug conjugated". Change
   "conjugated" to "conjugate". It should read:
   "PADCEV - an antibody-drug conjugate"

Change nothing else. Do not alter the panel titles, the other captions, the
labels, the colours, the characters or the composition.
```

**Optional, only if another pass is being run anyway:** the antibody carries hand grenades in
panels 1–4 but releases blue capsules in panel 4 — the payload it holds is not the payload it
drops. Cosmetic, and not worth a regeneration on its own.

---

## After it comes back — the checklist before it lands

1. **sha256 the new file BEFORE moving it.** ⚠ A filename is not an identity: two grok images
   already share the `grok-image-*.jpg` shape, and this project lost a document to exactly that on
   2026-08-17.
2. **Read every label in the returned image** and confirm the five defects above are gone. ⚠ v2
   looked different and had corrected nothing — *the image changing is not the image being fixed.*
3. **Write `D-096`** — replacing a D-052 component on a D-094 surface.
4. ⚠ **The D-052 property must be preserved:** the replacement must still import nothing from
   `api.js`, so it remains structurally incapable of reading as a model output. A static asset
   satisfies this, but the three tests in `AdcSchematic.test.jsx` assert the caption text, the
   absent-import property, and the `/target/1` link — **all three need updating, red-then-green.**
5. ⚠ **`ui/` currently holds ZERO image assets.** A ~700 KB JPEG is a new asset class with no
   pipeline; confirm how the built `UI_DIR` serves it before assuming Vite handles it.
6. **Keep the disclosure caption.** D-094 makes it a mount precondition, and the artwork is a
   cartoon — the caption is what stops a stylised drawing reading as a depiction of real structure.
