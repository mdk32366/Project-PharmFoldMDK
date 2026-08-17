import { Link } from 'react-router-dom'
import adcMechanism from '../assets/adc-mechanism-padcev-nectin4.jpg'

// D-052 / D-096: the ADC mechanism illustration — structurally prevented from reading as a model
// output. It imports NOTHING from api.js and takes no analysis props: a pure function of nothing, so
// it cannot quietly begin rendering something the network produced. The label says so; the *absent
// import* is what enforces it (a label can be edited away by a later hand — an import that does not
// exist cannot start lying).
//
// ⚠ D-096 replaced the hand-rolled SVG with a raster illustration. The medium changed; the property
// did NOT. A static imported asset takes no props and calls no API, so the D-052 guarantee holds for
// exactly the reason it always did — which is why the "invokes NO api.js export" test still passes
// unchanged. ⚠⚠ The load-bearing half of D-052 was never "SVG"; it was "imports nothing".
//
// ⚠⚠ THE COST D-096 NAMES: the graphic's words are now PIXELS. The over-claim denylist tests can no
// longer read what this surface says, because there is nothing textual to read. The `alt` below is
// the ONLY version-controlled record of the panel content, and its wording is pinned by test.
//
// ⚠ DELIBERATE DIVERGENCE from the pixels, recorded in D-096: the shipped asset (sha256 33AEC70F…)
// reads "cyttoxic" and "an antibody-drug conjugation". The transcription says "cytotoxic" and
// "conjugate". A transcription exists to convey meaning to a reader who cannot see the image, and
// propagating a typo into a screen reader serves nobody.
const ALT = [
  'Five-panel illustration of how the antibody-drug conjugate PADCEV works on a cancerous',
  'urothelial (bladder) cell.',
  'Step 1, Binding: PADCEV, an antibody-drug conjugate, binds NECTIN-4, a protein on the surface',
  'of the cancer cell.',
  'Step 2, Internalization: the cell pulls PADCEV inside, still attached to NECTIN-4.',
  'Step 3, Lysosome: inside the cell, the linker is cut and the payload comes free.',
  'Step 4, Payload Release: MMAE, the cytotoxic payload, is released inside the cell.',
  'Step 5, Cell Death: the payload disrupts the cell’s internal scaffolding and the cell dies.',
].join(' ')

export default function AdcSchematic() {
  return (
    <figure className="adc-schematic">
      <img src={adcMechanism} alt={ALT} loading="lazy" decoding="async" />
      <figcaption>
        <strong>Schematic illustration — not a structure produced by this system.</strong>{' '}
        A stylised drawing of the mechanism, not an ESMFold output — the cell, the antibody and the
        payload are cartoons, drawn at no real scale.{' '}
        <Link to="/target/1">See a real folded structure →</Link>
      </figcaption>
    </figure>
  )
}
