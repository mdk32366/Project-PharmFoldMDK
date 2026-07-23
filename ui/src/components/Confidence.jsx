import { bandFor, BANDS } from '../plddt.js'
import PlddtPlot from './PlddtPlot.jsx'

function BandLegend() {
  return (
    <ul className="band-legend">
      {BANDS.map((b) => (
        <li key={b.label}>
          <span className="swatch" style={{ background: b.color }} />
          <span>{b.min > 0 ? `≥ ${b.min}` : '< 50'} · {b.label}</span>
        </li>
      ))}
    </ul>
  )
}

// Confidence element (D-039). The mean pLDDT is never a bare number — it carries its band, and the
// top band carries the cohort-max caveat where it is read (owner ruling). The self-report note keeps
// the claim where the metric actually lives (attribution-not-explanation, D-028).
export default function Confidence({ meanPlddt, plddt }) {
  const band = bandFor(meanPlddt)
  return (
    <section className="confidence panel">
      <h3>Confidence</h3>
      <div className="band-headline" style={{ borderLeftColor: band.color }}>
        <span className="plddt-num">{meanPlddt != null ? meanPlddt.toFixed(2) : '—'}</span>
        <span className="band-label" style={{ color: band.color }}>{band.label}</span>
      </div>
      {band.caveat && <p className="caveat">⚠ {band.caveat}</p>}
      <p className="self-report">
        pLDDT is the model's <em>self-reported</em> confidence in local backbone geometry — not a
        measure of whether the fold is correct, and not calibrated against experimental structures
        for these targets.
      </p>
      <PlddtPlot plddt={plddt} />
      <BandLegend />
    </section>
  )
}
