import { Link } from 'react-router-dom'

// D-052: the ADC mechanism schematic — an ILLUSTRATION, structurally prevented from reading as a
// model output. It imports NOTHING from api.js and takes no analysis props: a pure function of
// nothing, so it cannot quietly begin rendering something the network produced. The label says so;
// the *absent import* is what enforces it (a label can be edited away by a later hand — an import
// that does not exist cannot start lying). Hand-rolled SVG (D-037): no diagram library in the bundle.
export default function AdcSchematic() {
  return (
    <figure className="adc-schematic">
      <svg viewBox="0 0 440 170" role="img"
           aria-label="Schematic of an antibody–drug conjugate: an antibody bound to a target antigen, a linker, and a cytotoxic payload">
        <g className="adc-antibody">
          <line x1="70" y1="120" x2="70" y2="72" />
          <line x1="70" y1="72" x2="44" y2="38" />
          <line x1="70" y1="72" x2="96" y2="38" />
          <text x="70" y="150">Antibody</text>
        </g>
        <g className="adc-linker">
          <line x1="70" y1="120" x2="184" y2="120" strokeDasharray="6 5" />
          <text x="127" y="108">Linker</text>
        </g>
        <g className="adc-payload">
          <circle cx="204" cy="120" r="16" />
          <text x="204" y="152">Payload</text>
        </g>
        <g className="adc-target">
          <line x1="320" y1="20" x2="320" y2="150" />
          <rect x="320" y="64" width="18" height="18" />
          <text x="392" y="70">Antigen</text>
          <text x="392" y="88">on the</text>
          <text x="392" y="106">tumour cell</text>
        </g>
      </svg>
      <figcaption>
        <strong>Schematic illustration — not a structure produced by this system.</strong>{' '}
        The antibody / linker / payload above is a drawing of the mechanism, not an ESMFold output.{' '}
        <Link to="/target/1">See a real folded structure →</Link>
      </figcaption>
    </figure>
  )
}
