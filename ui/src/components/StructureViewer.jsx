import { useEffect, useRef, useState } from 'react'
import { structureUrl, getPlddt } from '../api.js'
import { colorFor } from '../plddt.js'

// 3Dmol.js structure viewer. Loads the PDB BY URL (D-034 decision 2) and colours each residue by
// the /plddt ARRAY (D-039) — NEVER the PDB B-factor column, whose 0–100-vs-0–1 scale is unverified
// (S-001 cost real confusion on exactly that rescaling). 3Dmol is dynamically imported so it is a
// separate chunk loaded only on the target view, keeping the list page light.
export default function StructureViewer({ id }) {
  const ref = useRef(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let viewer = null
    let cancelled = false

    async function render() {
      setLoading(true)
      setError(null)
      try {
        const mod = await import('3dmol')
        const $3Dmol = mod.default ?? mod
        const [pdb, plddt] = await Promise.all([
          fetch(structureUrl(id)).then((r) => {
            if (!r.ok) throw new Error(`structure -> HTTP ${r.status}`)
            return r.text()
          }),
          getPlddt(id),
        ])
        if (cancelled || !ref.current) return
        ref.current.innerHTML = ''
        viewer = $3Dmol.createViewer(ref.current, { backgroundColor: '#0b1020' })
        viewer.addModel(pdb, 'pdb')
        // colour per-residue from the array; resi is 1-based, the array 0-based
        viewer.setStyle({}, {
          cartoon: { colorfunc: (atom) => colorFor(plddt[atom.resi - 1]) },
        })
        viewer.zoomTo()
        viewer.render()
      } catch (e) {
        if (!cancelled) setError(e.message)
      } finally {
        if (!cancelled) setLoading(false)
      }
    }

    render()
    return () => {
      cancelled = true
      try { if (viewer) viewer.clear() } catch { /* viewer teardown is best-effort */ }
    }
  }, [id])

  // Fallback (orders §3 / UI Plan v2 §6): the target view must not be a blank frame if the viewer
  // fails — provenance, confidence, and the plot render from JSON alone, below this.
  if (error) {
    return (
      <div className="viewer-fallback">
        Structure viewer unavailable ({error}). Confidence and provenance below still render.
      </div>
    )
  }
  return (
    <div className="viewer-wrap">
      {loading && <div className="viewer-loading">Loading structure…</div>}
      <div ref={ref} className="viewer" />
    </div>
  )
}
