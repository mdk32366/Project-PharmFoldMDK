import { useEffect, useState } from 'react'
import { getAnalysis, getPlddt, getRanking } from '../api.js'
import StructureViewer from './StructureViewer.jsx'
import Confidence from './Confidence.jsx'
import Provenance from './Provenance.jsx'
import CancerAssociations from './CancerAssociations.jsx'
import TargetScorerPanel from './TargetScorerPanel.jsx'

// The single-target experience (UI Plan v2 §3.2): structure coloured by pLDDT, confidence with its
// band, provenance that makes the DL claim checkable, and — D-068 — the scorer result that ranked it
// (or a reasoned "no score"). The ranking is cohort-wide, so it is fetched once and joined client-side
// by accession/gene (D-068 §1: no route change); a ranking failure must not break the target page,
// so it is fetched OUTSIDE the page-critical Promise.all. NECTIN4 (id 1) is the first rendered target.
export default function TargetView({ id }) {
  const [detail, setDetail] = useState(null)
  const [plddt, setPlddt] = useState(null)
  const [ranking, setRanking] = useState(null)
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

  useEffect(() => {
    let cancelled = false
    getRanking().then((r) => { if (!cancelled) setRanking(r) }).catch(() => { if (!cancelled) setRanking(null) })
    return () => { cancelled = true }
  }, [])

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
      <TargetScorerPanel detail={detail} ranking={ranking} />
      <CancerAssociations symbol={detail.gene} />
    </article>
  )
}
