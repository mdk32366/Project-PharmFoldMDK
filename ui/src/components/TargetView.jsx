import { useEffect, useState } from 'react'
import { getAnalysis, getPlddt } from '../api.js'
import StructureViewer from './StructureViewer.jsx'
import Confidence from './Confidence.jsx'
import Provenance from './Provenance.jsx'

// The single-target experience (UI Plan v2 §3.2): structure coloured by pLDDT, confidence with its
// band, provenance that makes the DL claim checkable. NECTIN4 (id 1) is the first rendered target.
export default function TargetView({ id }) {
  const [detail, setDetail] = useState(null)
  const [plddt, setPlddt] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    let cancelled = false
    setDetail(null)
    setPlddt(null)
    setError(null)
    Promise.all([getAnalysis(id), getPlddt(id)])
      .then(([d, p]) => { if (!cancelled) { setDetail(d); setPlddt(p) } })
      .catch((e) => { if (!cancelled) setError(e.message) })
    return () => { cancelled = true }
  }, [id])

  if (error) return <p className="error">Could not load target {id}: {error}</p>
  if (!detail) return <p className="loading">Loading target {id}…</p>

  return (
    <article className="target">
      <header className="target-header">
        <h2>{detail.gene}</h2>
        <p className="subtitle">{detail.accession} · {detail.label}</p>
      </header>
      <StructureViewer id={id} />
      <div className="panels">
        <Confidence meanPlddt={detail.mean_plddt} plddt={plddt} />
        <Provenance detail={detail} />
      </div>
    </article>
  )
}
