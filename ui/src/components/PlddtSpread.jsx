import { colorFor } from '../plddt.js'
import { ofCount } from '../plural.js'

// Per-residue pLDDT spread (D-048 §3.4, UI-depth §2.5). The mean hides the spread — NECTIN4 runs
// 50.1–93.4 on a mean of 77.26. This states min/median/max and the fraction of residues below the
// trust divider (60, D-039), plus a hand-rolled SVG sparkline (D-037: no chart lib for one plot).
// It surfaces uncertainty; it never manufactures a headline confidence number (UI-depth trap c).

const DIVIDER = 60 // D-039: below this the backbone is unreliable — the "how much of the chain is trustworthy" line.

function median(sorted) {
  const n = sorted.length
  const mid = n >> 1
  return n % 2 ? sorted[mid] : (sorted[mid - 1] + sorted[mid]) / 2
}

export default function PlddtSpread({ plddt }) {
  if (!plddt || !plddt.length) return null
  const n = plddt.length
  const sorted = [...plddt].sort((a, b) => a - b)
  const min = sorted[0]
  const max = sorted[n - 1]
  const med = median(sorted)
  const below = plddt.filter((v) => v < DIVIDER).length
  const belowPct = Math.round((below / n) * 100)

  // Sparkline geometry (hand-rolled SVG, D-037), coloured by the same D-039 band scheme as the
  // structure and the full plot, so every view tells one story.
  const W = 220
  const H = 40
  const x = (i) => (n === 1 ? 0 : (i / (n - 1)) * W)
  const y = (v) => H - (v / 100) * H
  const barW = Math.max(1, W / n)

  return (
    <div className="plddt-spread">
      <div className="spread-stats">
        <span data-testid="spread-min" className="spread-stat">
          <span className="spread-k">min</span> {min.toFixed(1)}
        </span>
        <span data-testid="spread-median" className="spread-stat">
          <span className="spread-k">median</span> {med.toFixed(1)}
        </span>
        <span data-testid="spread-max" className="spread-stat">
          <span className="spread-k">max</span> {max.toFixed(1)}
        </span>
      </div>
      <svg viewBox={`0 0 ${W} ${H}`} width="100%" role="img"
           aria-label={`Per-residue pLDDT sparkline across ${n} residues, ranging ${min.toFixed(1)} to ${max.toFixed(1)}`}>
        <line x1={0} x2={W} y1={y(DIVIDER)} y2={y(DIVIDER)} stroke="#33415533" strokeDasharray="2 2" />
        {plddt.map((v, i) => (
          <rect key={i} x={x(i)} y={y(v)} width={barW} height={H - y(v)} fill={colorFor(v)} />
        ))}
      </svg>
      <p data-testid="spread-below-divider" className="spread-below">
        {ofCount(below, n, 'residue')} ({belowPct}%) fall below {DIVIDER} — the mean does not show this.
      </p>
    </div>
  )
}
