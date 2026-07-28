// Provenance panel (UI Plan v2 §3.2, D-015/D-031; two-population render D-046 §3 / D-048 §3.1).
// This is what makes "we ran ESMFold ourselves, at a named revision" CHECKABLE rather than
// asserted — the deep-learning claim made auditable.
//
// The three field classes answer three different questions and are grouped as such (D-046 rule 3):
//   - WEIGHTS  — *what ran*      (model_id / model_revision)
//   - RECIPE   — *how it ran*    (dtype / chunk_size / input_length / …)
//   - ENVIRONMENT — *what it ran on* (torch / transformers / device / cuda) — D-045
//
// Two populations (D-045): pre-D-045 folds carry NO environment record; post-D-045 folds do. An
// absent environment field reads "not captured" — never a value, never a bare em-dash that could
// be mistaken for "none" (D-046 rule 1). The gap is named ONCE at the population level with its
// reason (D-046 rule 2), not repeated per field. No completeness score (D-046 §3): a fold we can
// say less about is not a worse fold.

const WEIGHTS_FIELDS = [
  ['model_id', 'Model'],
  ['model_revision', 'Revision'],
]
const RECIPE_FIELDS = [
  ['dtype', 'Precision'],
  ['chunk_size', 'Chunk size'],
  ['input_length', 'Residues folded'],
  ['ca_atom_count', 'Cα atoms'],
  ['truncated', 'Truncated'],
  ['folded_at', 'Folded at'],
]
// The four D-045 environment fields, in "what it ran on" order.
const ENV_FIELDS = [
  ['torch_version', 'PyTorch'],
  ['transformers_version', 'transformers'],
  ['device_name', 'Device'],
  ['cuda_version', 'CUDA'],
]

// A plain value cell: renders the value, or an em-dash for a genuinely-absent-but-not-a-population
// field (recipe/weights nulls read as "—", meaning "none/not applicable here").
function Row({ label, value }) {
  return (
    <div>
      <dt>{label}</dt>
      <dd>{value != null ? String(value) : '—'}</dd>
    </div>
  )
}

export default function Provenance({ detail }) {
  const p = detail.fold_provenance || {}
  const sliced = detail.boundary_method === 'sliced_ecd' && detail.ecd_start != null

  // The population test: a post-D-045 fold recorded at least one environment key. A pre-D-045 fold
  // recorded none — the honest statement for it is "predates capture", per field AND once overall.
  const envCaptured = ENV_FIELDS.some(([k]) => p[k] != null)

  return (
    <section className="provenance panel">
      <h3>Provenance — we ran this ourselves</h3>

      <div role="group" aria-label="Model weights" className="prov-group prov-weights">
        <h4>What ran — the weights</h4>
        <dl>
          {WEIGHTS_FIELDS.map(([k, label]) => <Row key={k} label={label} value={p[k]} />)}
        </dl>
      </div>

      <div role="group" aria-label="Compute recipe" className="prov-group prov-recipe">
        <h4>How it ran — the recipe</h4>
        <dl>
          {RECIPE_FIELDS.map(([k, label]) => <Row key={k} label={label} value={p[k]} />)}
          <div>
            <dt>Boundary method</dt>
            <dd>{detail.boundary_method}{sliced ? ` (residues ${detail.ecd_start}–${detail.ecd_end})` : ''}</dd>
          </div>
          <div>
            <dt>UniProt release</dt>
            <dd>{detail.uniprot_release != null ? String(detail.uniprot_release) : '—'}</dd>
          </div>
        </dl>
      </div>

      <div role="group" aria-label="Software environment" className="prov-group prov-environment">
        <h4>What it ran on — the environment</h4>
        <dl>
          {ENV_FIELDS.map(([k, label]) => (
            <div key={k}>
              <dt>{label}</dt>
              {/* Rule 1: absent env field is "not captured", NEVER a value, NEVER a bare em-dash. */}
              <dd>{p[k] != null ? String(p[k]) : <span className="not-captured">not captured</span>}</dd>
            </div>
          ))}
        </dl>
        {!envCaptured && (
          // D-070: for an uncaptured environment, say what the record DOES hold — tier, folded_at, and
          // the worker manifest BY NAME — strictly more than "not captured", and NEVER an inferred
          // version (F-007: an inference would have been wrong on the one fold that could check it). The
          // four captured fields above stay "not captured" (dec 2); this block is separate and says what
          // it is — what the record holds, not what ran (dec 1). Names the manifest, never its contents
          // (dec 3): no version string, no device model appears here — all Constraint-A.
          <div className="note prov-recorded-note">
            <p>
              <strong>What we can say:</strong> this fold ran on the <strong>{detail.tier}</strong> tier
              {p.folded_at ? <> on <strong>{String(p.folded_at)}</strong></> : null}. Its software
              environment is pinned in the repository's worker manifest
              (<code>worker/requirements.txt</code>), but it was <strong>not recorded per-fold</strong> —
              capture began later (D-045), and the record is written worker-side at fold time and cannot
              be reconstructed. <strong>This is what the record holds, not a reconstruction</strong> —
              not a worse fold, just one we can say less about.
            </p>
          </div>
        )}
      </div>

      {detail.boundary_method === 'whole' && (
        <p className="note">
          Folded as the whole chain — this target has no sliceable extracellular domain, which is
          itself a limitation (it is held out of cross-method ranking, D-021).
        </p>
      )}
    </section>
  )
}
