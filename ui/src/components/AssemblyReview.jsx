import { Link } from 'react-router-dom'

// D-120 / PLAN §3.6 — review payload for an assembled parent.
// D-125-B — dual-path honesty: name assembler vs Kabsch-path when A's
// sibling tree is on disk. D-126-B — triple-path honesty: name the
// confidence_kabsch/ tree when (and only when) it is on disk.
// Ops numbers, not a restitch GO. Seams not solved.

function formatMeasure(value, { missing = 'not computed on this path' } = {}) {
  if (value == null || value === '') return missing
  if (typeof value === 'number' && Number.isFinite(value)) {
    return `${value.toFixed(2)} Å`
  }
  return String(value)
}

function formatCount(value) {
  if (value == null || value === '') return 'not computed on this path'
  return String(value)
}

function DualPathHonesty({ dualPath, triplePath }) {
  const paths = triplePath || dualPath
  if (!paths) return null
  const assembler = paths.assembler || {}
  const kabsch = paths.kabsch || {}
  const d126 = paths.confidence_kabsch || {}
  const three = Boolean(d126.present)
  const seams = kabsch.seams || []
  const d126Seams = d126.seams || []
  return (
    <div className="dual-path" data-testid="dual-path-honesty">
      <h4>{three ? 'Three paths — not one population' : 'Two paths — not one population'}</h4>
      <p className="caveat">
        ⚠ Persist stems must not collide. Assembler files stay{' '}
        <code>{assembler.persist_stem || 'stitched'}</code>. Kabsch-path
        files, when present, live under{' '}
        <code>{kabsch.persist_stem || 'kabsch/{parent}'}</code>
        {three ? (
          <>
            . Overlap-confidence Kabsch-path files live under{' '}
            <code>{d126.persist_stem || 'confidence_kabsch/{parent}'}</code>
          </>
        ) : null}
        . The assembler PDB remains the default served structure. Seams are{' '}
        <strong>not scientifically solved</strong>.
      </p>
      <dl className="assembly-prov">
        <div>
          <dt>Assembler path</dt>
          <dd>{assembler.label || 'pLDDT winner-tile assembler (default served)'}</dd>
        </div>
        <div>
          <dt>Kabsch-path</dt>
          <dd>{kabsch.present ? kabsch.label : (kabsch.empty_note || 'not on disk for this parent')}</dd>
        </div>
        <div>
          <dt>Kabsch persist stem</dt>
          <dd><code>{kabsch.persist_stem || '—'}</code></dd>
        </div>
        {three ? (
          <>
            <div>
              <dt>Overlap-confidence Kabsch-path</dt>
              <dd>{d126.label}</dd>
            </div>
            <div>
              <dt>D-126 persist stem</dt>
              <dd><code>{d126.persist_stem || '—'}</code></dd>
            </div>
            <div>
              <dt>D-126 parent outcome</dt>
              <dd data-testid="d126-accepted">
                {d126.accepted === true
                  ? 'accepted on this path — not the served PDB'
                  : d126.accepted === false
                    ? 'refused — recorded outcome, not a success badge'
                    : 'not recorded'}
              </dd>
            </div>
          </>
        ) : null}
      </dl>

      {kabsch.present ? (
        <div data-testid="kabsch-seams">
          <h4>Kabsch-path seam measurements</h4>
          <p className="note">
            Numbers come from A&apos;s <code>provenance.json</code> /{' '}
            <code>seams.jsonl</code>. A missing RMSD or max Cα jump is an
            absence, not a solved seam. A refuse is a recorded outcome,
            not a &quot;fixed&quot; badge.
          </p>
          {seams.length === 0 ? (
            <p className="note" data-testid="kabsch-seams-empty">
              Seam rows were not written on this path.
            </p>
          ) : (
            <table className="tile-table">
              <thead>
                <tr>
                  <th>Tiles</th>
                  <th>Overlap</th>
                  <th>n_Cα</th>
                  <th>RMSD</th>
                  <th>Max Cα jump</th>
                  <th>Refuse</th>
                </tr>
              </thead>
              <tbody>
                {seams.map((s, i) => (
                  <tr key={`${s.moving_tile_index}-${i}`}>
                    <td className="mono">
                      {s.reference_tile_index}→{s.moving_tile_index}
                    </td>
                    <td className="mono">
                      {s.overlap_start != null && s.overlap_end != null
                        ? `${s.overlap_start}–${s.overlap_end}`
                        : '—'}
                    </td>
                    <td className="mono">{s.n_ca != null ? s.n_ca : '—'}</td>
                    <td>{formatMeasure(s.rmsd_angstrom)}</td>
                    <td>{formatMeasure(s.max_ca_jump_angstrom)}</td>
                    <td className="mono">{s.refuse_reason == null ? 'none' : s.refuse_reason}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      ) : (
        <p className="note" data-testid="kabsch-path-empty">
          {kabsch.empty_note
            || 'Kabsch-path artifacts are not on disk for this parent. No overlap RMSD and no max Cα jump to show.'}
        </p>
      )}

      {three ? (
        <div data-testid="d126-seams">
          <h4>Overlap-confidence Kabsch-path seam measurements</h4>
          <p className="note">
            Numbers come from A&apos;s D-126 <code>provenance.json</code> /{' '}
            <code>seams.jsonl</code>. Weighted RMSD, full-overlap RMSD,
            max Cα jump, n_ca_eff, and trim rounds are absences when
            missing — not a solved seam. A refuse is a recorded
            outcome, not a &quot;fixed&quot; badge. This path is never
            the default served PDB.
          </p>
          {d126Seams.length === 0 ? (
            <p className="note" data-testid="d126-seams-empty">
              Seam rows were not written on this path.
            </p>
          ) : (
            <table className="tile-table">
              <thead>
                <tr>
                  <th>Tiles</th>
                  <th>Overlap</th>
                  <th>n_Cα</th>
                  <th>n_Cα_eff</th>
                  <th>Weighted RMSD</th>
                  <th>Full-overlap RMSD</th>
                  <th>Max Cα jump</th>
                  <th>Trim rounds</th>
                  <th>Refuse</th>
                </tr>
              </thead>
              <tbody>
                {d126Seams.map((s, i) => (
                  <tr key={`d126-${s.moving_tile_index}-${i}`}>
                    <td className="mono">
                      {s.reference_tile_index}→{s.moving_tile_index}
                    </td>
                    <td className="mono">
                      {s.overlap_start != null && s.overlap_end != null
                        ? `${s.overlap_start}–${s.overlap_end}`
                        : '—'}
                    </td>
                    <td className="mono">{s.n_ca != null ? s.n_ca : '—'}</td>
                    <td className="mono">{formatCount(s.n_ca_eff)}</td>
                    <td>{formatMeasure(s.rmsd_angstrom)}</td>
                    <td>{formatMeasure(s.rmsd_full_overlap_angstrom)}</td>
                    <td>{formatMeasure(s.max_ca_jump_angstrom)}</td>
                    <td className="mono">{formatCount(s.trim_rounds)}</td>
                    <td className="mono">{s.refuse_reason == null ? 'none' : s.refuse_reason}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      ) : null}
    </div>
  )
}

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

      <DownloadList items={review.downloads?.stitched} heading="Downloads — assembler stitched.*" />
      <DownloadList items={review.downloads?.tiles} heading="Downloads — tileN.* / spare*" />

      <DualPathHonesty dualPath={review.dual_path} triplePath={review.triple_path} />

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
