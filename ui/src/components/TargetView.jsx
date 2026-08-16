import { useEffect, useState } from 'react'
import { getAnalysis, getPlddt, getRanking } from '../api.js'
import StructureViewer from './StructureViewer.jsx'
import Confidence from './Confidence.jsx'
import PlddtExplainer from './PlddtExplainer.jsx'
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
    // D-069 earning its keep: a page that errors is maximally NON-self-sufficient. Only getAnalysis is
    // page-critical — if the target does not exist, that IS the error. Every other fold-dependent
    // fetch degrades on its own (D-068 fix / owner note): a failed fold (IGF2R) has no plddt.json, and
    // its 404 must never stop the "not folded" scorer panel from rendering its reason (D-068 dec 1).
    getAnalysis(id)
      .then((d) => { if (!cancelled) setDetail(d) })
      .catch((e) => { if (!cancelled) setError(e.message) })
    getPlddt(id)
      .then((p) => { if (!cancelled) setPlddt(p) })
      .catch(() => { if (!cancelled) setPlddt(null) })   // no per-residue plot, but the page stands
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
        <PlddtExplainer />
        <Provenance detail={detail} />
      </div>
      <TargetScorerPanel detail={detail} ranking={ranking} />
      <CancerAssociations symbol={detail.gene} />
    </article>
  )
}
