import { bandFor, BANDS } from '../plddt.js'
import PlddtPlot from './PlddtPlot.jsx'
import PlddtSpread from './PlddtSpread.jsx'

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
// ⚠⚠ `caveat` OVERRIDES the band's own note, and it exists because the default is a statement
// about the COHORT. `plddt.js` bakes in "cohort max 84.23", which is true of the 82 and was shown
// unchanged on census protein pages — where the max is 89.25 and six rows exceed it. A page about
// one population must not display another population's ceiling, least of all one this protein
// beats. Passing nothing keeps the cohort behaviour exactly as it was (F-038).
export default function Confidence({ meanPlddt, plddt, caveat, assembled = false }) {
  const band = bandFor(meanPlddt)
  const note = caveat !== undefined ? caveat : band.caveat
  return (
    <section className="confidence panel">
      <h3>{assembled ? 'Assembled-chain pLDDT (winner tile per residue)' : 'Confidence'}</h3>
      <div className="band-headline" style={{ borderLeftColor: band.color }}>
        <span className="plddt-num">{meanPlddt != null ? meanPlddt.toFixed(2) : '—'}</span>
        <span className="band-label" style={{ color: band.color }}>{band.label}</span>
      </div>
      {/* ⚠⚠ THE DISCLOSURE SITS WITH THE NUMBER, NOT ONLY ON THE VIEWER (D-150). A reader who
          scrolls past a failed 3Dmol frame — or reads this panel on a narrow screen where the
          viewer is far above it — meets a confident-looking mean with nothing saying what it is
          the confidence OF. For an assembly it is the winner tile's self-report at each residue,
          stitched across a seam that is not solved, so it does not describe one continuous
          model the way a single-pass mean does. */}
      {assembled && (
        <p className="caveat assembled-disclosure">
          ⚠ <strong>This mean is over an assembled chain, not one ESMFold pass.</strong> Each
          residue&rsquo;s value is the winner tile&rsquo;s, joined by pLDDT overlap and{' '}
          <strong>not</strong> superimposed — seams are <strong>not scientifically solved</strong>,
          so the structure is <strong>provisional</strong> and this number does not certify it.
        </p>
      )}
      {note && <p className="caveat">⚠ {note}</p>}
      <PlddtSpread plddt={plddt} />{/* D-048 §3.4: the spread the mean hides, beside the mean. */}
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
