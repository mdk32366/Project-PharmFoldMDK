// D-123 — thin verbatim extract from docs/pharmfold-adc-nectin4-paper.md (Part 2).
//
// ⚠ THIS FILE IS NOT AUTHORITATIVE AND MUST NOT DRIFT. The owner Doc is the source.
// Every science string below is a character substring of that file. Not rewritten,
// not shortened, not paraphrased. Markdown **bold** is the only render transform.
// Chrome titles (TWO_TRACKS_TITLE, EV_NOT_V_KEY_TITLE, STANDING_LINE) are labels,
// not science — they are excluded from the substring pin.
//
// ⚠ Part 1 is not extracted. /about already teaches ADC mechanism; a full-Doc
// paste would be the dump this GO refuses.
//
// aboutPaper.test.js asserts every VERBATIM_EXCERPTS member appears in the Doc.

export const PAPER_SOURCE_PATH = 'docs/pharmfold-adc-nectin4-paper.md'

// UI chrome from the BUILD GO — not a Doc sentence.
export const TWO_TRACKS_TITLE = 'Two tracks (Nectin-4 / ADC framing)'
export const EV_NOT_V_KEY_TITLE = 'EV is not a universal V-key'

// D-094 discipline on our chrome: "asks whether", never "shows that".
export const STANDING_LINE =
  'This section is derived from docs/pharmfold-adc-nectin4-paper.md and is not a source of truth. ' +
  'It asks whether the same antibody is a universal V-domain key. ' +
  'Nothing below is a project ranking result.'

// Paper heading, exact.
export const SHORT_ANSWER_HEADING = 'Short answer'

export const SHORT_ANSWER = [
  '**Same EV antibody, other proteins:** Do not assume yes. A V domain is a common fold shape, not the same lock. Taiwan FDA assessment: EV/AGS-22M6E bound Nectin-4 but **not** Nectin-1, -2, or -3. Broader IgV cross-binding = **unknown** without lab tests.',
  '**Next targets after building EV:** Realistic path is usually a **new antibody** against a **new membrane protein**, reusing ADC learnings.',
  '**Bond types:** H-bonds, electrostatics, van der Waals are how antibodies in general stick — not a special third Padcev-only bond.',
]

// Paper heading, exact (including ≠).
export const V_SURFACE_HEADING = 'V surface ≠ EV keyhole'

export const V_SURFACE_BODY =
  '"V-type" = immunoglobulin-variable-like fold. Other proteins can share the brick without sharing the lock. PDB 4JJH = Nectin-4 D1 structure for shape searches, not EV-binding proof.'

export const TRACK_A =
  '**Track A — Reuse EV antibody:** List membrane IgV / nectin-like ECDs — feasible. Wet binding assays — required. No bind → stop. Do not rank docking guesses as hits. Track A is mostly off-target risk mapping unless wet binding is shown.'

export const TRACK_B =
  '**Track B — New Ab, new antigen, reuse ADC learnings** (realistic next-target path): topology; cancer vs normal; internalization; antigen density; fold confidence (pLDDT); epitope exposure; ADC suitability; do **not** require IgV/4JJH similarity; rank by (cancer × membrane × internalization × density) / normal risk.'

export const BOTTOM_LINE_HEADING = 'Bottom line'

export const BOTTOM_LINE_1 =
  "Padcev's durable connection to Nectin-4's outside is a high-affinity, often two-armed, non-covalent CDR fit on the membrane-distant V domain, while MMAE is covalently attached to the antibody and released after internalization."

export const BOTTOM_LINE_2 =
  'That same antibody is not a universal V-domain key. For next targets after EV, rank folded membrane proteins by ADC biology, then make a **new** antibody — unless wet assays prove the existing EV antibody truly binds something else.'

// The pin set — every member must be a substring of the owner Doc.
export const VERBATIM_EXCERPTS = [
  SHORT_ANSWER_HEADING,
  ...SHORT_ANSWER,
  V_SURFACE_HEADING,
  V_SURFACE_BODY,
  TRACK_A,
  TRACK_B,
  BOTTOM_LINE_HEADING,
  BOTTOM_LINE_1,
  BOTTOM_LINE_2,
]
