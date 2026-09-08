import { Link } from 'react-router-dom'

// D-120 / PLAN §3.6 — review payload for an assembled parent.
// D-125-B — dual-path honesty: name assembler vs Kabsch-path when A's
// sibling tree is on disk. D-126-B — triple-path honesty: name the
// confidence_kabsch/ tree when (and only when) it is on disk.
// D-127-B — four-path honesty: name the piecewise_kabsch/ tree the same
// way, and render ONE ROW PER DOMAIN PIECE. A seam average across pieces
// would hide the per-domain disagreement multi-rigid exists to expose,
// which is the D-126 lie surface wearing a new number.
// D-128-B — five-path honesty: name the linker_seam/ tree, and render A's
// §1a rows ONE PER (PATH, SEAM). Those rows are cross-path, so the
// tempting collapse here is a mean jump per path or an "N of M honest"
// tally — either would hide WHICH path is dishonest WHERE, which is the
// whole content of §1a. No average is derived anywhere below.
// D-129-B — Phase 5 named-refuse: the eight accept-refuse parents get the
// signed label, and it renders WITH the D-128 OPS rollup rather than beside
// it. 3272 / 3394 stay Phase 4 and render as open.
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

// Spec §1a is three-valued and unknown is NOT honest. A null jump has no
// verdict to render, so it must not fall through to either boolean.
function honestyWord(honest) {
  if (honest === true) return 'honest at this seam (≤ 10.0 Å)'
  if (honest === false) return 'dishonest at this seam (> 10.0 Å)'
  return 'unknown — not honest'
}

function pathCountWord(three, four, five) {
  if (five) return 'Five'
  if (four) return 'Four'
  if (three) return 'Three'
  return 'Two'
}

function DualPathHonesty({ dualPath, triplePath, fourPath, fivePath }) {
  const paths = fivePath || fourPath || triplePath || dualPath
  if (!paths) return null
  const assembler = paths.assembler || {}
  const kabsch = paths.kabsch || {}
  const d126 = paths.confidence_kabsch || {}
  const d127 = paths.piecewise_kabsch || {}
  const d128 = paths.linker_seam || {}
  const three = Boolean(d126.present)
  const four = Boolean(d127.present)
  const five = Boolean(d128.present)
  const seams = kabsch.seams || []
  const d126Seams = d126.seams || []
  const d127Seams = d127.seams || []
  const d128Seams = d128.seams || []
  const honestyRows = d128.seam_honesty || []
  return (
    <div className="dual-path" data-testid="dual-path-honesty">
      <h4>{pathCountWord(three, four, five)} paths — not one population</h4>
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
        {four ? (
          <>
            . Piecewise / domain-aware Kabsch-path files live under{' '}
            <code>{d127.persist_stem || 'piecewise_kabsch/{parent}'}</code>
          </>
        ) : null}
        {five ? (
          <>
            . Linker / seam honesty files live under{' '}
            <code>{d128.persist_stem || 'linker_seam/{parent}'}</code>
          </>
        ) : null}
        . The assembler PDB remains the <em>default</em> served structure;
        which path is actually served for <em>this</em> parent is resolved
        below under <strong>D-139</strong>. Seams are{' '}
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
        {four ? (
          <>
            <div>
              <dt>Piecewise / domain-aware Kabsch-path</dt>
              <dd>{d127.label}</dd>
            </div>
            <div>
              <dt>D-127 persist stem</dt>
              <dd><code>{d127.persist_stem || '—'}</code></dd>
            </div>
            <div>
              <dt>D-127 parent outcome</dt>
              <dd data-testid="d127-accepted">
                {d127.accepted === true
                  ? 'accepted on this path — not the served PDB'
                  : d127.accepted === false
                    ? 'refused — recorded outcome, not a success badge'
                    : 'not recorded'}
              </dd>
            </div>
          </>
        ) : null}
        {five ? (
          <>
            <div>
              <dt>Linker / seam honesty path</dt>
              <dd>{d128.label}</dd>
            </div>
            <div>
              <dt>D-128 persist stem</dt>
              <dd><code>{d128.persist_stem || '—'}</code></dd>
            </div>
            <div>
              <dt>D-128 parent outcome</dt>
              <dd data-testid="d128-accepted">
                {d128.accepted === true
                  ? 'accepted on this path — not the served PDB'
                  : d128.accepted === false
                    ? 'refused — recorded outcome, not a success badge'
                    : 'not recorded'}
              </dd>
            </div>
            <div>
              <dt>±32 aa window transform applied</dt>
              <dd data-testid="d128-repaired">
                {d128.repaired === true
                  ? 'at least one seam window was transformed — a recorded move, not a repaired seam'
                  : d128.repaired === false
                    ? 'no window transform was applied on this parent'
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
            outcome, not a &quot;fixed&quot; badge. This path is never the{' '}
            <em>default</em> served PDB — under <strong>D-139</strong> it is
            served only to the recorded PASS seventeen, and only when this
            tree is on disk and accepted. See the served-path block below.
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

      {four ? (
        <div data-testid="d127-seams">
          <h4>Piecewise / domain-aware Kabsch-path seam measurements</h4>
          <p className="note">
            Numbers come from A&apos;s D-127 <code>provenance.json</code> /{' '}
            <code>seams.jsonl</code>. This path fits{' '}
            <strong>one rigid move per UniProt domain</strong> that
            overlaps the glue, so each seam is shown as{' '}
            <strong>one row per piece</strong> — no seam average, no best
            piece. The parent full-overlap RMSD and max Cα jump sit
            beside those rows as the cross-check, because a small
            per-piece RMSD can still accompany a large full-overlap jump.
            Missing values are absences, not zeros: on a
            refuse-before-transform there is nothing to measure. A refuse
            is a recorded outcome, not a &quot;fixed&quot; badge. This
            path is never the default served PDB, and{' '}
            <strong>D-139 did not change that</strong> — the one flip it
            signed serves D-126, never this path.
          </p>
          {d127Seams.length === 0 ? (
            <p className="note" data-testid="d127-seams-empty">
              Seam rows were not written on this path.
            </p>
          ) : (
            d127Seams.map((s, i) => (
              <div className="d127-seam" key={`d127-${s.moving_tile_index}-${i}`}>
                <h5>
                  Seam {s.reference_tile_index}→{s.moving_tile_index}
                  {s.overlap_start != null && s.overlap_end != null
                    ? ` — overlap ${s.overlap_start}–${s.overlap_end}`
                    : null}
                </h5>
                <dl className="assembly-prov">
                  <div>
                    <dt>Full-overlap RMSD (unweighted, after the piecewise moves)</dt>
                    <dd>{formatMeasure(s.rmsd_full_overlap_angstrom)}</dd>
                  </div>
                  <div>
                    <dt>Max Cα jump (full overlap, after the piecewise moves)</dt>
                    <dd>{formatMeasure(s.max_ca_jump_angstrom)}</dd>
                  </div>
                  <div>
                    <dt>Linker residues (inherit the nearest N-terminal accepted piece)</dt>
                    <dd className="mono">{formatCount(s.linker_n)}</dd>
                  </div>
                  <div>
                    <dt>Max linker Cα jump</dt>
                    <dd>{formatMeasure(s.max_linker_ca_jump)}</dd>
                  </div>
                  <div>
                    <dt>Seam outcome</dt>
                    <dd className="mono">
                      {s.refuse_reason == null ? 'none' : s.refuse_reason}
                    </dd>
                  </div>
                </dl>
                {(s.pieces || []).length === 0 ? (
                  <p className="note" data-testid={`d127-pieces-empty-${i}`}>
                    No per-piece rows were recorded for this seam
                    {s.pieces_empty_reason ? ` (${s.pieces_empty_reason})` : null}.
                    That absence is not a count of zero refused pieces.
                  </p>
                ) : (
                  <table className="tile-table">
                    <thead>
                      <tr>
                        <th>Domain piece (span-relative)</th>
                        <th>n_Cα</th>
                        <th>Weighted RMSD</th>
                        <th>Refuse</th>
                      </tr>
                    </thead>
                    <tbody>
                      {s.pieces.map((p, j) => (
                        <tr key={`d127-piece-${i}-${j}`}>
                          <td className="mono">
                            {Array.isArray(p.interval) && p.interval.length === 2
                              ? `${p.interval[0]}–${p.interval[1]}`
                              : '—'}
                          </td>
                          <td className="mono">{p.n_ca != null ? p.n_ca : '—'}</td>
                          <td>{formatMeasure(p.rmsd_angstrom)}</td>
                          <td className="mono">
                            {p.refuse_reason == null ? 'none' : p.refuse_reason}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )}
              </div>
            ))
          )}
        </div>
      ) : null}

      {five ? (
        <div data-testid="d128-seam-honesty">
          <h4>Seam honesty — every path, every seam (D-128 §1a)</h4>
          <p className="note">
            Numbers come from A&apos;s D-128{' '}
            <code>seam_honesty.jsonl</code>. Each row is{' '}
            <strong>one path at one seam</strong>: the max Cα jump that
            path <strong>ends</strong> with, and whether it is therefore{' '}
            <strong>honest</strong> there — a jump over{' '}
            <strong>10.0 Å</strong> is <strong>dishonest for that
            seam</strong>. There is deliberately <strong>no average, no
            per-path score, and no &quot;how many seams passed&quot;
            count</strong>: a mean would hide the one seam that flies
            apart, which is the disagreement these rows exist to show. A
            missing jump is an <strong>absence</strong>, never{' '}
            <code>0.00 Å</code>, and <strong>unknown is not
            honest</strong>. Each row also says how it is known — read
            from that path&apos;s record, measured from the artifacts
            that path itself wrote, or an absence with a reason.
          </p>
          {honestyRows.length === 0 ? (
            <p className="note" data-testid="d128-honesty-empty">
              No per-path seam honesty rows were recorded
              {d128.seam_honesty_empty_reason
                ? ` (${d128.seam_honesty_empty_reason})`
                : null}
              . That absence is not a count of zero dishonest seams.
            </p>
          ) : (
            <table className="tile-table">
              <thead>
                <tr>
                  <th>Path</th>
                  <th>Tiles</th>
                  <th>Max Cα jump</th>
                  <th>Honest?</th>
                  <th>Linker Cα</th>
                  <th>Max linker jump</th>
                  <th>How it is known</th>
                  <th>Refuse</th>
                </tr>
              </thead>
              <tbody>
                {honestyRows.map((r, i) => (
                  <tr key={`d128-honesty-${r.path}-${i}`}>
                    <td className="mono">{r.path || '—'}</td>
                    <td className="mono">
                      {r.reference_tile_index != null && r.moving_tile_index != null
                        ? `${r.reference_tile_index}→${r.moving_tile_index}`
                        : 'whole path'}
                    </td>
                    <td>{formatMeasure(r.max_ca_jump_angstrom, { missing: 'not measured' })}</td>
                    <td>
                      {honestyWord(r.honest)}
                      {r.honest_disagrees_with_record ? (
                        <> — recorded verdict disagrees with the 10.0 Å gate; the gate wins</>
                      ) : null}
                    </td>
                    <td className="mono">
                      {r.linker_fields_applicable
                        ? formatCount(r.linker_n)
                        : 'not defined on this path'}
                    </td>
                    <td>
                      {r.linker_fields_applicable
                        ? formatMeasure(r.max_linker_ca_jump)
                        : 'not defined on this path'}
                    </td>
                    <td className="mono">
                      {r.source || '—'}
                      {r.absence_reason ? ` (${r.absence_reason})` : null}
                    </td>
                    <td className="mono">{r.refuse_reason == null ? 'none' : r.refuse_reason}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      ) : null}

      {five ? (
        <div data-testid="d128-seams">
          <h4>Linker / seam honesty path — window fit</h4>
          <p className="note">
            Numbers come from A&apos;s D-128 <code>provenance.json</code> /{' '}
            <code>seams.jsonl</code>. This path fits{' '}
            <strong>at most one weighted rigid move</strong> inside a{' '}
            <strong>±32 aa window</strong> around the offending seam, and
            moves nothing outside it. The post-move jump is measured
            across the <strong>whole seam</strong>, not just the window
            that was fitted — a window that lands while the rest of the
            seam flies apart is not a held join. Missing values are
            absences, not zeros: on a refuse-before-transform there is
            nothing to measure. A refuse is a recorded outcome, not a
            &quot;fixed&quot; badge. This path is never the default
            served PDB, and <strong>D-139 did not change that</strong> —
            the one flip it signed serves D-126, never this path.
          </p>
          {d128Seams.length === 0 ? (
            <p className="note" data-testid="d128-seams-empty">
              Seam rows were not written on this path.
            </p>
          ) : (
            <table className="tile-table">
              <thead>
                <tr>
                  <th>Tiles</th>
                  <th>Overlap</th>
                  <th>Window (±{d128.window_half_width_aa ?? 32} aa)</th>
                  <th>n_Cα</th>
                  <th>Weighted RMSD</th>
                  <th>Jump before</th>
                  <th>Jump after (whole seam)</th>
                  <th>Honest?</th>
                  <th>Seam identified by</th>
                  <th>Refuse</th>
                </tr>
              </thead>
              <tbody>
                {d128Seams.map((s, i) => (
                  <tr key={`d128-${s.moving_tile_index}-${i}`}>
                    <td className="mono">
                      {s.reference_tile_index}→{s.moving_tile_index}
                    </td>
                    <td className="mono">
                      {s.overlap_start != null && s.overlap_end != null
                        ? `${s.overlap_start}–${s.overlap_end}`
                        : '—'}
                    </td>
                    <td className="mono">
                      {s.window_start != null && s.window_end != null
                        ? `${s.window_start}–${s.window_end}`
                        : 'no window fitted'}
                    </td>
                    <td className="mono">{formatCount(s.n_ca)}</td>
                    <td>{formatMeasure(s.rmsd_angstrom)}</td>
                    <td>{formatMeasure(s.pre_transform_max_ca_jump_angstrom)}</td>
                    <td>{formatMeasure(s.max_ca_jump_angstrom)}</td>
                    <td>{honestyWord(s.honest)}</td>
                    <td className="mono">
                      {s.no_offending_seam
                        ? 'nothing offended — no window fitted'
                        : s.offending_seam_source || '—'}
                    </td>
                    <td className="mono">{s.refuse_reason == null ? 'none' : s.refuse_reason}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
          <p className="note" data-testid="d128-served-note">
            {d128.success_pdb_on_disk
              ? 'A D-128-path stitched.pdb is on disk for this parent and every seam ended inside the gate. It is still not the served structure.'
              : 'No D-128-path stitched.pdb is presented as an honest result for this parent. A dishonest or unknown seam never carries one, and no assembler / D-125 / D-126 / D-127 file stands in for it.'}{' '}
            The assembler PDB remains the <em>default</em> served
            structure — see the <strong>D-139</strong> block below for what
            this parent is actually handed — and{' '}
            <strong>a seam that was recorded is not a seam that was
            solved</strong>.
          </p>
        </div>
      ) : null}
    </div>
  )
}

// D-139 — which path's bytes this parent is actually handed.
//
// ⚠ The reason is NOT optional. "Assembler" on its own cannot tell a reader
// that this parent was never eligible from that its D-126 run refused, and
// that distinction is the whole Phase 4 / Phase 5 vocabulary. So the named
// reason renders in the same block as the answer, and the block is only
// omitted when the payload carries no served-path decision at all.
const SERVED_PATH_NAMES = {
  assembler: 'Assembler (winner-tile)',
  confidence_kabsch: 'D-126 overlap-confidence Kabsch',
}

function ServedPath({ served }) {
  if (!served || !served.served) return null
  const flipped = served.served === 'confidence_kabsch'
  return (
    <div className="served-path" data-testid="served-path">
      <h4>Which structure this parent is served (D-139)</h4>
      <dl className="assembly-prov">
        <div>
          <dt>served path</dt>
          <dd data-testid="served-path-name">
            <strong>{SERVED_PATH_NAMES[served.served] || served.served}</strong>
          </dd>
        </div>
        <div>
          <dt>persist stem</dt>
          <dd><code>{served.persist_stem || '—'}</code></dd>
        </div>
        <div>
          <dt>in the recorded PASS {served.pass_subset_n ?? 17}</dt>
          <dd data-testid="served-path-eligible">
            {served.eligible ? 'yes' : 'no'}
          </dd>
        </div>
        <div>
          <dt>flipped off assembler</dt>
          <dd data-testid="served-path-flipped">{flipped ? 'yes' : 'no'}</dd>
        </div>
        {served.not_flipped_reason ? (
          <div>
            <dt>reason</dt>
            <dd className="mono" data-testid="served-path-reason">
              {served.not_flipped_reason}
            </dd>
          </div>
        ) : null}
      </dl>
      <p className="note" data-testid="served-path-note">
        {flipped
          ? 'This parent is in the recorded D-126 PASS subset and its confidence-Kabsch tree is on disk and accepted, so that structure is what the download returns — as stitched_confidence_kabsch.pdb, never stitched.pdb.'
          : served.not_flipped_note}{' '}
        The gate is an allowlist plus four checks, never a pass count, and
        there is no auto-flip. <strong>A served structure is a recorded
        outcome, not a solved seam.</strong>
      </p>
    </div>
  )
}

// D-129-B — Phase 5 named-refuse label for the eight accept-refuse parents.
// The label and the D-128 OPS rollup are ONE block on purpose: "accepted"
// reads like resolution, and a friendly word that outlives its numbers is
// exactly what Spec §4 calls a violation. After D-131, 3272 / 3394 render
// as named refuse / accept-refuse with the Phase 4 0/2 rollup (D-130-B / D-131).
function Phase5Fate({ fate }) {
  if (!fate || !fate.fate) return null
  const rollup = fate.ops_rollup
  const isPhase4 = fate.phase === 'phase4' || (rollup && rollup.recovered_of_two !== undefined)
  return (
    <div className="phase5-fate" data-testid="phase5-fate">
      <h4>
        {isPhase4
          ? 'Phase 4 fate — what we now call this join'
          : 'Phase 5 fate — what we now call this join'}
      </h4>
      <dl className="assembly-prov">
        <div>
          <dt>Fate</dt>
          <dd data-testid="phase5-label">
            <strong>{fate.label}</strong>
          </dd>
        </div>
        <div>
          <dt>Recorded refuse reason</dt>
          <dd className="mono">
            {fate.recorded_refuse_reason || 'not recorded'}
            {fate.recorded_by_path ? ` (recorded by ${fate.recorded_by_path})` : null}
          </dd>
        </div>
      </dl>
      <p className="note">{fate.meaning}</p>
      {fate.is_accept_refuse ? (
        <p className="note">
          This is <strong>{fate.not_a_miss}</strong>. It is{' '}
          <strong>not solved, not fixed, not repaired</strong>, and it is
          not an open must-hunt: there is no fifth stitch algorithm
          coming. The <strong>assembler</strong> remains the default
          served structure.
        </p>
      ) : null}
      {fate.already_accept_refuse_note ? (
        <p className="note" data-testid="phase5-3432-note">
          {fate.already_accept_refuse_note}
        </p>
      ) : null}
      {fate.is_accept_refuse && rollup && !isPhase4 ? (
        <div data-testid="phase5-ops-rollup">
          <h4>Why we stopped — the D-128 OPS rollup, as recorded</h4>
          <p className="note">
            ⚠ Ops numbers <strong>as recorded</strong> by{' '}
            {rollup.recorded_by} at tip <code>{rollup.recorded_at_tip}</code>,
            out_root <code>{rollup.out_root}</code>.{' '}
            <strong>Not run, not queried, and not re-measured here.</strong>{' '}
            This rollup is of <strong>{rollup.population}</strong>.
          </p>
          <ul>
            <li>
              Outcome of the seven:{' '}
              <strong>
                PASS {rollup.pass} · REFUSE {rollup.refuse} · FAIL{' '}
                {rollup.fail} · SKIP {rollup.skip}
              </strong>
              . <code>repaired_of_seven</code> ={' '}
              <strong>{rollup.repaired_of_seven}</strong> — and that zero
              was <strong>pre-registered as an allowed outcome</strong> (
              {rollup.pre_registered_at}).
            </li>
            <li data-testid="phase5-give-back">
              <code>n_d125_pass_d128_refuse</code> ={' '}
              <strong>{rollup.n_d125_pass_d128_refuse}</strong>;{' '}
              <code>n_d126_pass_d128_refuse</code> ={' '}
              <strong>{rollup.n_d126_pass_d128_refuse}</strong>;{' '}
              <code>n_d127_pass_d128_refuse</code> ={' '}
              <strong>{rollup.n_d127_pass_d128_refuse}</strong> and{' '}
              <code>n_d127_refuse_d128_pass</code> ={' '}
              <strong>{rollup.n_d127_refuse_d128_pass}</strong>.{' '}
              {rollup.give_back_note}.
            </li>
            <li>
              Where the refuses came from:{' '}
              <code>seam_jump_gt_10</code> (
              {(rollup.refuse_seam_jump_gt_10 || []).join(', ')}) and{' '}
              <code>rmsd_gt_10</code> (
              {(rollup.refuse_rmsd_gt_10 || []).join(', ')}). The{' '}
              <strong>{rollup.gate_angstrom} Å</strong> gate stays.
            </li>
            <li>{rollup.best_experimental_path}.</li>
          </ul>
        </div>
      ) : null}
      {fate.is_accept_refuse && rollup && isPhase4 ? (
        <div data-testid="phase4-ops-rollup">
          <h4>Why we stopped — the Phase 4 residual-RMSD OPS rollup, as recorded</h4>
          <p className="note">
            ⚠ Ops numbers <strong>as recorded</strong> at tip{' '}
            <code>{rollup.recorded_at_tip}</code>, out_root{' '}
            <code>{rollup.out_root}</code>.{' '}
            <strong>Not run, not queried, and not re-measured here.</strong>{' '}
            This rollup is of <strong>{rollup.population}</strong>.
          </p>
          <ul>
            <li>
              Outcome of the two:{' '}
              <strong>
                PASS {rollup.pass} · REFUSE {rollup.refuse} · FAIL{' '}
                {rollup.fail}
              </strong>
              . <code>recovered_of_two</code> ={' '}
              <strong>{rollup.recovered_of_two}</strong> — recovering zero
              of the two was an <strong>allowed outcome</strong> (
              {rollup.pre_registered_at}).
            </li>
            <li data-testid="phase4-refuse-rows">
              <strong>3272</strong> refused <code>rmsd_irreducible</code>
              {rollup.notes && rollup.notes[3272]
                ? ` — ${rollup.notes[3272]}`
                : ''}; <strong>3394</strong> refused{' '}
              <code>rmsd_gt_10</code>
              {rollup.notes && rollup.notes[3394]
                ? ` — ${rollup.notes[3394]}`
                : ''}. The <strong>{rollup.gate_angstrom} Å</strong> gate
              stays.
            </li>
            <li>{rollup.best_experimental_path}.</li>
          </ul>
        </div>
      ) : null}
      {fate.moves_only_on ? (
        <p className="note" data-testid="phase5-phase4-open">
          This parent is <strong>open</strong>. It moves only on{' '}
          {fate.moves_only_on}, and no card, ops run, or tidy-up may
          reclassify it.
        </p>
      ) : null}
      {isPhase4 && fate.hunt_closed ? (
        <p className="note" data-testid="phase4-labelled">
          Phase 4 pair labelled: hunt stopped after OPS 0/2 and Matt&apos;s
          named-refuse sign. See Method (D-130-B / D-131).
        </p>
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

      <DualPathHonesty
        dualPath={review.dual_path}
        triplePath={review.triple_path}
        fourPath={review.four_path}
        fivePath={review.five_path}
      />

      <ServedPath served={review.served_path} />

      <Phase5Fate fate={review.phase5_fate} />

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
        {/* ⚠ D-132 — TWO MEMBERSHIPS, AND A PARENT CAN BE IN ONE AND NOT THE OTHER. The
            assembled inventory is the measured 45 on the volume; the Wave1+Wave2 row is
            the 2026-09-05 closeout slice of 27 inside it. Collapsing them is exactly how
            the 27 came to be rendered as the live count. */}
        <div>
          <dt>in assembled inventory of 45 (measured 2026-09-08)</dt>
          <dd>{review.in_assembled_inventory ? 'yes' : 'no'}</dd>
        </div>
        <div>
          <dt>in Wave1+Wave2 closeout slice of 27 (2026-09-05)</dt>
          <dd>{review.in_wave1_wave2_inventory ? 'yes' : 'no'}</dd>
        </div>
      </dl>
      <p className="note">
        The 45 unique assembled parents — the 2026-09-05 Wave1+Wave2 slice of 27 plus 18
        that were already on the volume — are not in the{' '}
        <Link to="/scorer">F-004 ranking</Link> (D-109). The stitch-path OPS runs
        (D-127 / D-128 / D-130) were run on the 27; none of their numbers describe
        the other 18.
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
