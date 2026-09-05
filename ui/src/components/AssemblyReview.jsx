import { Link } from 'react-router-dom'

// D-120 / PLAN §3.6 — review payload for an assembled parent.
// Ops numbers, not a restitch GO. Kabsch stays parked.

function PaeBadge({ yes }) {
  return (
    <span className={yes ? 'pae-yes' : 'pae-no'}>
      {yes ? 'PAE yes' : 'PAE no'}
    </span>
  )
}

function DownloadList({ items, heading }) {
  const rows = (items || []).filter((d) => d.available !== false)
  if (!rows.length) return null
  return (
    <div className="assembly-downloads">
      <h4>{heading}</h4>
      <ul>
        {rows.map((d) => (
          <li key={d.name}>
            <a href={d.href} download={d.name}>{d.name}</a>
            {d.role === 'spare' ? <span className="spare-tag"> spare</span> : null}
          </li>
        ))}
      </ul>
    </div>
  )
}

export default function AssemblyReview({ review }) {
  if (!review) return null
  const ready = review.readiness || {}
  const missing = ready.missing || []
  return (
    <section className="assembly-review panel" data-testid="assembly-review">
      <h3>Assembly review</h3>
      <p className="caveat">
        ⚠ {review.assembler_note}. {review.seam_note} These counts are{' '}
        <strong>ops numbers, not a restitch button</strong>.
      </p>

      <h4>Stitch readiness</h4>
      <ul className="status-list" data-testid="stitch-readiness">
        <li>source: <code>{ready.source}</code></li>
        <li>expected_n: <strong>{ready.expected_n}</strong></li>
        <li>present_complete_n: <strong>{ready.present_complete_n}</strong></li>
        <li>missing: <strong>{missing.length}</strong>
          {missing.length > 0 && (
            <> ({missing.map((m) => `${m.start}–${m.end}`).join(', ')})</>
          )}
        </li>
        <li>uncovered_n: <strong>{ready.uncovered_n}</strong></li>
      </ul>
      {ready.note && <p className="note">{ready.note}</p>}

      <h4>Tiles — chosen vs spare</h4>
      <p className="note">
        Prefer the lower job / analysis id. Named unused spares:{' '}
        <code>3693 / 3695 / 3696</code>. Preferred lower ids:{' '}
        <code>3673 / 3674 / 3675</code>.
      </p>
      <table className="tile-table">
        <thead>
          <tr>
            <th>Id</th>
            <th>Window</th>
            <th>Status</th>
            <th>PAE</th>
            <th>Role</th>
          </tr>
        </thead>
        <tbody>
          {(review.tiles || []).map((t) => (
            <tr key={t.analysis_id} className={`tile-role-${t.role}`}>
              <td className="mono">
                {t.job_id != null ? t.job_id : t.analysis_id}
                {t.job_id != null && t.job_id !== t.analysis_id
                  ? ` (analysis ${t.analysis_id})`
                  : null}
              </td>
              <td className="mono">
                {t.start != null && t.end != null ? `${t.start}–${t.end}` : '—'}
                {t.span_aa != null ? ` (${t.span_aa} aa)` : null}
              </td>
              <td>{t.status}</td>
              <td><PaeBadge yes={t.has_pae} /></td>
              <td>
                <strong>{t.role}</strong>
                {t.named_spare ? ' — named unused spare' : null}
                {t.preferred_lower_id ? ' — preferred lower id' : null}
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      <DownloadList items={review.downloads?.stitched} heading="Downloads — stitched.*" />
      <DownloadList items={review.downloads?.tiles} heading="Downloads — tileN.* / spare*" />

      <h4>Assembly provenance</h4>
      <dl className="assembly-prov">
        <div><dt>hold48_kind</dt><dd>{review.hold48_kind ?? '—'}</dd></div>
        <div><dt>parent analysis</dt><dd>{review.parent_analysis_id}</dd></div>
        <div>
          <dt>parent job</dt>
          <dd>{review.parent_job_id != null ? review.parent_job_id : 'not on this card'}</dd>
        </div>
        <div>
          <dt>chosen tile ids</dt>
          <dd>{(review.chosen_tile_ids || []).join(', ') || '—'}</dd>
        </div>
        <div>
          <dt>spare tile ids</dt>
          <dd>{(review.spare_tile_ids || []).join(', ') || 'none'}</dd>
        </div>
        <div>
          <dt>in Wave1+Wave2 inventory of 27</dt>
          <dd>{review.in_wave1_wave2_inventory ? 'yes' : 'no'}</dd>
        </div>
      </dl>
      <p className="note">
        The 27 unique stitched parents are not in the{' '}
        <Link to="/scorer">F-004 ranking</Link> (D-109).
      </p>
    </section>
  )
}

export function Igf2rTwoPopulation({ copy }) {
  if (!copy) return null
  return (
    <aside className="igf2r-two-pop" data-testid="igf2r-two-pop">
      <p>
        <strong>Two populations, neither substituted.</strong>{' '}
        {copy.cohort} {copy.census}
      </p>
    </aside>
  )
}
