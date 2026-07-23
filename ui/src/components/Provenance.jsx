// Provenance panel (UI Plan v2 §3.2, D-015/D-031). This is what makes "we ran ESMFold ourselves,
// at a named revision" CHECKABLE rather than asserted — the deep-learning claim made auditable.
const FIELDS = [
  ['model_id', 'Model'],
  ['model_revision', 'Revision'],
  ['dtype', 'Precision'],
  ['chunk_size', 'Chunk size'],
  ['input_length', 'Residues folded'],
  ['ca_atom_count', 'Cα atoms'],
  ['truncated', 'Truncated'],
  ['folded_at', 'Folded at'],
]

export default function Provenance({ detail }) {
  const p = detail.fold_provenance || {}
  const sliced = detail.boundary_method === 'sliced_ecd' && detail.ecd_start != null
  return (
    <section className="provenance panel">
      <h3>Provenance — we ran this ourselves</h3>
      <dl>
        {FIELDS.map(([k, label]) => (
          <div key={k}>
            <dt>{label}</dt>
            <dd>{p[k] != null ? String(p[k]) : '—'}</dd>
          </div>
        ))}
        <div>
          <dt>Boundary method</dt>
          <dd>{detail.boundary_method}{sliced ? ` (residues ${detail.ecd_start}–${detail.ecd_end})` : ''}</dd>
        </div>
        <div>
          <dt>UniProt release</dt>
          <dd>{detail.uniprot_release ?? '—'}</dd>
        </div>
      </dl>
      {detail.boundary_method === 'whole' && (
        <p className="note">
          Folded as the whole chain — this target has no sliceable extracellular domain, which is
          itself a limitation (it is held out of cross-method ranking, D-021).
        </p>
      )}
    </section>
  )
}
