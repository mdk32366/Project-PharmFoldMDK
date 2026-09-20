import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { getCensusStructuralRanking } from '../api.js'

// D-169 Contract A — browse UI for GET /api/census-structural-ranking.
// ⚠ Not the cohort-82 learned scorer. STRUCTURAL_ONLY only.

const BANNER =
  'STRUCTURAL_ONLY — membrane × ECD × pLDDT structure score. ' +
  'Not ADC readiness. Not a shortlist. Not the cohort-82 learned scorer. ' +
  'Live source of truth is GET /api/census-structural-ranking ' +
  '(the spreadsheet is a review lens only).'

export { BANNER as STRUCTURAL_RANK_BANNER }

export default function CensusStructuralRank() {
  const [payload, setPayload] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    setError(null)
    getCensusStructuralRanking()
      .then((data) => { if (!cancelled) setPayload(data) })
      .catch((e) => { if (!cancelled) setError(e?.message || String(e)) })
      .finally(() => { if (!cancelled) setLoading(false) })
    return () => { cancelled = true }
  }, [])

  if (loading) {
    return (
      <section className="census-structural-rank panel" data-testid="census-structural-rank">
        <p className="census-structural-banner" data-testid="structural-only-banner">{BANNER}</p>
        <p>Loading structural rank…</p>
      </section>
    )
  }

  if (error) {
    return (
      <section className="census-structural-rank panel" data-testid="census-structural-rank">
        <p className="census-structural-banner" data-testid="structural-only-banner">{BANNER}</p>
        <p role="alert">Could not load structural ranking: {error}</p>
      </section>
    )
  }

  const status = payload?.result_status
  const rows = Array.isArray(payload?.rows) ? payload.rows : []

  if (status && status !== 'valid') {
    return (
      <section className="census-structural-rank panel" data-testid="census-structural-rank">
        <p className="census-structural-banner" data-testid="structural-only-banner">{BANNER}</p>
        <p role="alert">Structural ranking is not valid right now (result_status={status}). No ranks shown.</p>
      </section>
    )
  }

  if (!rows.length) {
    return (
      <section className="census-structural-rank panel" data-testid="census-structural-rank">
        <p className="census-structural-banner" data-testid="structural-only-banner">{BANNER}</p>
        <p>No structural-rank rows returned.</p>
      </section>
    )
  }

  return (
    <section className="census-structural-rank panel" data-testid="census-structural-rank">
      <p className="census-structural-banner" data-testid="structural-only-banner">{BANNER}</p>
      <p className="note">
        {payload?.n_candidates != null
          ? `${payload.n_candidates.toLocaleString()} candidates in the structure-only order.`
          : `${rows.length.toLocaleString()} rows.`}
        {' '}This is not the cohort-82 Scorer ranking.
      </p>
      <div className="table-scroll census-table-scroll">
        <table className="census-table structural-rank-table">
          <thead>
            <tr>
              <th scope="col">Rank</th>
              <th scope="col">Gene</th>
              <th scope="col">Accession</th>
              <th scope="col">Score</th>
              <th scope="col">Flags</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => {
              const acc = row.accession
              const flags = Array.isArray(row.flags) ? row.flags : (row.ecd_intermittent ? ['ecd_intermittent'] : [])
              return (
                <tr key={acc || row.rank}>
                  <td>{row.rank ?? row.rank_within_statistic ?? ''}</td>
                  <td>{row.gene || '—'}</td>
                  <td>{acc ? <Link to={`/census/${acc}`}>{acc}</Link> : '—'}</td>
                  <td>{row.structural_score != null ? Number(row.structural_score).toFixed(4) : '—'}</td>
                  <td>{flags.length ? flags.join(', ') : '—'}</td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </section>
  )
}
