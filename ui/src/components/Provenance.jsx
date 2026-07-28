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

  // D-071 — provenance strength is THREE-valued, ordered strongest to weakest (decision 1):
  //   state 1 — measured at FOLD TIME     : the fold's own fold_provenance recorded ≥1 env key (D-045).
  //   state 2 — measured LATER, same tier : no fold-time capture, but the tier's machine was measured
  //             after the fact (`detail.tier_environment`). The four fields render, WITH a qualifier.
  //   state 3 — absent                    : neither. One statement + D-070's "what we can say" block.
  // A reader must never have to work out which kind of claim they are looking at (decision 1).
  const envCaptured = ENV_FIELDS.some(([k]) => p[k] != null)   // state 1
  const tierEnv = detail.tier_environment || null              // state 2 (or null → state 3)

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
        {envCaptured ? (
          /* STATE 1 — measured at fold time (D-045). The four fields, UNqualified: the strongest claim. */
          <dl>
            {ENV_FIELDS.map(([k, label]) => (
              <div key={k}>
                <dt>{label}</dt>
                <dd>{p[k] != null ? String(p[k]) : <span className="not-captured">not captured</span>}</dd>
              </div>
            ))}
          </dl>
        ) : tierEnv ? (
          /* STATE 2 — measured LATER on this tier's machine (D-071). The four fields render FROM the
             tier record and NEVER without the qualifier — a reader must see this is not fold-time
             capture (decision 1). A measurement may enter the fields (D-070 dec 2 as amended by D-071);
             an inference never could. */
          <>
            <dl>
              {ENV_FIELDS.map(([k, label]) => (
                <div key={k}>
                  <dt>{label}</dt>
                  <dd>{tierEnv[k] != null ? String(tierEnv[k]) : <span className="not-captured">not captured</span>}</dd>
                </div>
              ))}
            </dl>
            <p className="prov-tier-qualifier">tier environment, measured {tierEnv.measured_at} — not recorded at fold time</p>
          </>
        ) : (
          /* STATE 3 — absent. No fold-time capture, and no measurable machine (the rental pods are
             ephemeral and gone — D-071 dec 3). ONE clear statement, not four "not captured" fields
             stacked like a broken form — a deliberate answer. The asymmetry with state 2 (no values vs
             values) is a TRUE thing about the project and stays legible: better presentation, not a
             softened distinction (owner). D-070's "what we can say" block travels here. */
          <>
            {/* ⚠ Unrecoverability is a claim about the MACHINE, and is attached to the ephemeral rental
                instance specifically — NOT to state 3 in general. State 3 is rental-only in production
                (all 42 local folds are state 2), but if a local fold ever fell through, the first clause
                stays true and the second simply does not render — the box is right there, D-071 just
                recovered it. Asserting unrecoverability about a machine you own would be the D-070
                failure inverted: claiming less than the record supports. */}
            <p className="prov-not-recorded">
              <strong>No environment was recorded for this fold</strong>
              {detail.tier === 'rental' ? (
                <>, and the machine that ran it — an <strong>ephemeral rental instance</strong> — is
                gone, so it cannot be reconstructed</>
              ) : null}.
            </p>
            <div className="note prov-recorded-note">
              <p>
                <strong>What we can say:</strong> this fold ran on the <strong>{detail.tier}</strong> tier
                {p.folded_at ? <> on <strong>{String(p.folded_at)}</strong></> : null}. Its software
                environment is pinned in the repository's worker manifest
                (<code>worker/requirements.txt</code>), but it was <strong>not recorded per-fold</strong> —
                capture began later (D-045). <strong>This is what the record holds, not a
                reconstruction</strong> — not a worse fold, just one we can say less about.
              </p>
            </div>
          </>
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
