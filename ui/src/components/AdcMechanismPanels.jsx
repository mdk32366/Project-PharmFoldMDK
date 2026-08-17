import adcMechanism from '../assets/adc-mechanism-padcev-nectin4.jpg'

// D-097: the PROCESS half of the ADC explanation â€” five panels in time, reachable without a
// technical background. Its companion is AdcSchematic, which answers the other question: that one is
// ANATOMY (antibody / linker / payload / antigen), this one is SEQUENCE (bind, internalise, cleave,
// release, kill). âš  They are not two versions of one graphic, and the schematic must come FIRST â€”
// a reader cannot follow "the linker is cut" in panel 3 without having been shown a linker.
//
// âš  D-052 holds here for the same reason it holds for the schematic, and it is the reason this is a
// separate component rather than markup inside AdcContext: it imports NOTHING from api.js and takes
// no props, so it is a pure function of nothing and cannot quietly begin rendering something the
// network produced. Its test asserts that independently.
//
// âš âš  D-096's named cost, still live for THIS half: the panel wording is PIXELS. The over-claim
// denylist tests cannot read it. The `alt` below is the only version-controlled record of what the
// artwork says, and it is pinned by test so an asset swap cannot silently change the claim.
//
// âš  DELIBERATE DIVERGENCE from the pixels (D-096): the shipped asset (sha256 33AEC70Fâ€¦) reads
// "cyttoxic" and "an antibody-drug conjugation". This transcription reads "cytotoxic" and
// "conjugate". A transcription conveys meaning to a reader who cannot see the image; propagating a
// typo into a screen reader serves nobody.
const ALT = [
  'Five-panel illustration of how the antibody-drug conjugate PADCEV works on a cancerous',
  'urothelial (bladder) cell.',
  'Step 1, Binding: PADCEV, an antibody-drug conjugate, binds NECTIN-4, a protein on the surface',
  'of the cancer cell.',
  'Step 2, Internalization: the cell pulls PADCEV inside, still attached to NECTIN-4.',
  'Step 3, Lysosome: inside the cell, the linker is cut and the payload comes free.',
  'Step 4, Payload Release: MMAE, the cytotoxic payload, is released inside the cell.',
  'Step 5, Cell Death: the payload disrupts the cellâ€™s internal scaffolding and the cell dies.',
].join(' ')

export default function AdcMechanismPanels() {
  return (
    <figure className="adc-panels">
      {/* âš  width/height are the INTRINSIC pixel dimensions of the asset, not a display size â€” CSS
          still drives layout (width:100%, height:auto). They exist so the browser can reserve the
          aspect-ratio box BEFORE the 707 KB fetch resolves. Without them, `loading="lazy"` collapses
          the figure to a 0-height line and the caption jumps up under the heading until the image
          arrives. Caught on the deployed site, not locally, because a fast dev server hides it. */}
      <img src={adcMechanism} alt={ALT} width="2128" height="912" loading="lazy" decoding="async" />
      <figcaption>
        <strong>Illustration â€” not a structure produced by this system.</strong>{' '}
        A cartoon of the delivery sequence, drawn at no real scale: the cell, the antibody and the
        payload are drawings, not depictions of real molecules.
      </figcaption>
    </figure>
  )
}
