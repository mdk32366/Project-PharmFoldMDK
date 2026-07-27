import systemModel from '../system-model.json'

// D-051: the architecture diagram, RENDERED FROM ui/src/system-model.json — never hand-drawn.
// tests/test_architecture_contract.py pins the model's route lists to the live FastAPI route table
// (both directions), so this picture cannot drift from the running system. No route string or node
// label is typed into this JSX — every path and node comes from the model. Hand-rolled SVG (D-037):
// no diagram library enters the bundle. The load-bearing claim is the topology — inference runs on
// the external GPU tier, not on Fly (D-004); the Fly tier is GPU-free (DEP-001).

const W = 760
const NODE_W = 250
const NODE_H = 50
const GAP = 26
const PAD = 60

export default function ArchitectureDiagram({ model = systemModel }) {
  const fly = model.nodes.filter((n) => n.zone === 'fly')
  const ext = model.nodes.filter((n) => n.zone !== 'fly')
  const colX = { fly: PAD, ext: W - PAD - NODE_W }
  const yOf = (i) => PAD + 24 + i * (NODE_H + GAP)
  const pos = {}
  fly.forEach((n, i) => { pos[n.id] = { x: colX.fly, y: yOf(i) } })
  ext.forEach((n, i) => { pos[n.id] = { x: colX.ext, y: yOf(i) } })
  const rows = Math.max(fly.length, ext.length, 1)
  const H = yOf(rows) + PAD
  const cx = (id) => pos[id].x + NODE_W / 2
  const cy = (id) => pos[id].y + NODE_H / 2
  const zoneBox = (nodes, x) => ({
    x: x - 16, y: PAD - 8, w: NODE_W + 32,
    h: (Math.max(nodes.length, 1)) * (NODE_H + GAP) + 20,
  })
  const flyBox = zoneBox(fly, colX.fly)
  const extBox = zoneBox(ext, colX.ext)

  return (
    <figure className="arch-diagram">
      <figcaption>
        Where inference runs. Rendered from <code>system-model.json</code> and pinned to the live
        route table by <code>tests/test_architecture_contract.py</code> — adding or removing a route
        reddens the gate until this picture is updated, so it cannot drift from the running system.
      </figcaption>
      <svg viewBox={`0 0 ${W} ${H}`} role="img"
           aria-label="System architecture: a Fly serving tier with no GPU, and an external GPU tier where ESMFold runs">
        <g className="arch-zone arch-zone-fly">
          <rect x={flyBox.x} y={flyBox.y} width={flyBox.w} height={flyBox.h} rx="10" />
          <text x={flyBox.x + flyBox.w / 2} y={PAD - 16} className="arch-zone-label">
            Fly serving tier — no GPU (DEP-001)
          </text>
        </g>
        <g className="arch-zone arch-zone-external">
          <rect x={extBox.x} y={extBox.y} width={extBox.w} height={extBox.h} rx="10" />
          <text x={extBox.x + extBox.w / 2} y={PAD - 16} className="arch-zone-label">
            External — GPU tier, not on Fly (D-004)
          </text>
        </g>
        {model.edges.map((e, i) => (
          <g className="arch-edge" key={`${e.from}-${e.to}-${i}`}>
            <line x1={cx(e.from)} y1={cy(e.from)} x2={cx(e.to)} y2={cy(e.to)} />
            <text x={(cx(e.from) + cx(e.to)) / 2} y={(cy(e.from) + cy(e.to)) / 2 - 5}>{e.label}</text>
          </g>
        ))}
        {model.nodes.map((n) => (
          <g className={`arch-node ${n.gpu ? 'arch-node-gpu' : ''}`} key={n.id}>
            <rect x={pos[n.id].x} y={pos[n.id].y} width={NODE_W} height={NODE_H} rx="6" />
            <text x={pos[n.id].x + NODE_W / 2} y={pos[n.id].y + NODE_H / 2}>{n.label}</text>
          </g>
        ))}
      </svg>
      <div className="arch-routes">
        <div>
          <h4>Public reads — <code>/api/*</code>, no auth</h4>
          <ul>
            {model.routes.public_api.map((r) => (
              <li key={r.path}><code>{r.methods.join(', ')} {r.path}</code></li>
            ))}
          </ul>
        </div>
        <div>
          <h4>Worker routes — <code>/jobs/*</code>, bearer-guarded</h4>
          <ul>
            {model.routes.worker_jobs.map((r) => (
              <li key={r.path}><code>{r.methods.join(', ')} {r.path}</code></li>
            ))}
          </ul>
        </div>
      </div>
    </figure>
  )
}
