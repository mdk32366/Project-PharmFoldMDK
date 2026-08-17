import adcMechanism from '../assets/adc-mechanism-padcev-nectin4.jpg'

// D-097: the PROCESS half of the ADC explanation — five panels in time, reachable without a
// technical background. Its companion is AdcSchematic, which answers the other question: that one is
// ANATOMY (antibody / linker / payload / antigen), this one is SEQUENCE (bind, internalise, cleave,
// release, kill). ⚠ They are not two versions of one graphic, and the schematic must come FIRST —
// a reader cannot follow "the linker is cut" in panel 3 without having been shown a linker.
//
// ⚠ D-052 holds here for the same reason it holds for the schematic, and it is the reason this is a
// separate component rather than markup inside AdcContext: it imports NOTHING from api.js and takes
// no props, so it is a pure function of nothing and cannot quietly begin rendering something the
// network produced. Its test asserts that independently.
//
// ⚠⚠ D-096's named cost, still live for THIS half: the panel wording is PIXELS. The over-claim
// denylist tests cannot read it. The `alt` below is the only version-controlled record of what the
// artwork says, and it is pinned by test so an asset swap cannot silently change the claim.
//
// ⚠ DELIBERATE DIVERGENCE from the pixels (D-096): the shipped asset (sha256 33AEC70F...) reads
// "cyttoxic" and "an antibody-drug conjugation". This transcription reads "cytotoxic" and
// "conjugate". A transcription conveys meaning to a reader who cannot see the image; propagating a
// typo into a screen reader serves nobody.
//
// ⚠⚠ ENCODING: this file contains non-ASCII (em dashes, warning glyphs, a curly apostrophe). It was
// once corrupted into double-encoded mojibake by a PowerShell `Get-Content -Raw` / `Set-Content`
// round-trip, which read UTF-8 as ANSI and rewrote it — and it SHIPPED, because every test asserts
// on ASCII substrings and none could see it. Edit this file with a real editor, never by piping it
// through a shell. See D-097.
const ALT = [
  'Five-panel illustration of how the antibody-drug conjugate PADCEV works on a cancerous',
  'urothelial (bladder) cell.',
  'Step 1, Binding: PADCEV, an antibody-drug conjugate, binds NECTIN-4, a protein on the surface',
  'of the cancer cell.',
  'Step 2, Internalization: the cell pulls PADCEV inside, still attached to NECTIN-4.',
  'Step 3, Lysosome: inside the cell, the linker is cut and the payload comes free.',
  'Step 4, Payload Release: MMAE, the cytotoxic payload, is released inside the cell.',
  "Step 5, Cell Death: the payload disrupts the cell's internal scaffolding and the cell dies.",
].join(' ')

export default function AdcMechanismPanels() {
  return (
    <figure className="adc-panels">
      {/* ⚠ width/height are the INTRINSIC pixel dimensions of the asset, not a display size — CSS
          still drives layout (width:100%, height:auto). They exist so the browser can reserve the
          aspect-ratio box BEFORE the 707 KB fetch resolves. Without them, `loading="lazy"` collapses
          the figure to a 0-height line and the caption jumps up under the heading until the image
          arrives. Caught on the deployed site, not locally, because a fast dev server hides it. */}
      <img src={adcMechanism} alt={ALT} width="2128" height="912" loading="lazy" decoding="async" />
      <figcaption>
        <strong>Illustration — not a structure produced by this system.</strong>{' '}
        A cartoon of the delivery sequence, drawn at no real scale: the cell, the antibody and the
        payload are drawings, not depictions of real molecules.
      </figcaption>
    </figure>
  )
}
