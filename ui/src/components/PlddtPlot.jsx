import { colorFor } from '../plddt.js'

// Per-residue pLDDT, hand-rolled SVG (D-037: a chart library for one plot type is a real cost in a
// weaker-guarantee dependency world; hand-rolled SVG is the legitimate answer). Bars are coloured by
// the same D-039 band scheme as the structure, so the plot and the 3D view tell one story. The
// 50/60/70 band lines are drawn so a reader sees where this fold sits relative to the trust divider.
export default function PlddtPlot({ plddt }) {
  if (!plddt || !plddt.length) return null
  const W = 680
  const H = 140
  const pad = 28
  const n = plddt.length
  const x = (i) => pad + (n === 1 ? 0 : (i / (n - 1)) * (W - 2 * pad))
  const y = (v) => H - pad - (v / 100) * (H - 2 * pad)
  const barW = Math.max(1, (W - 2 * pad) / n)

  return (
    <svg viewBox={`0 0 ${W} ${H}`} width="100%" role="img"
         aria-label={`Per-residue pLDDT across ${n} residues`}>
      {[50, 60, 70].map((t) => (
        <g key={t}>
          <line x1={pad} x2={W - pad} y1={y(t)} y2={y(t)} stroke="#33415522" />
          <text x={W - pad + 2} y={y(t) + 3} fontSize="9" fill="#64748b">{t}</text>
        </g>
      ))}
      {plddt.map((v, i) => (
        <rect key={i} x={x(i)} y={y(v)} width={barW} height={y(0) - y(v)} fill={colorFor(v)} />
      ))}
      <text x={pad} y={H - 6} fontSize="10" fill="#64748b">residue 1</text>
      <text x={W - pad} y={H - 6} fontSize="10" fill="#64748b" textAnchor="end">{n}</text>
    </svg>
  )
}
