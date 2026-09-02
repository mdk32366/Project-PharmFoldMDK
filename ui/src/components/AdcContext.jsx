import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { listAnalyses } from '../api.js'
import { HELDOUT_EXAMPLES } from '../heldoutExamples.js'
import AdcSchematic from './AdcSchematic.jsx'
import AdcMechanismPanels from './AdcMechanismPanels.jsx'
import Term from './Term.jsx'

// ADC framing / onboarding (UI Plan v2 §7): keep the metaphor (it is mechanism, not decoration),
// bound the outcome claims, and let the honest limits sharpen the purpose rather than soften it.
// The through-line: conviction about the mechanism, precision about the limits.
export default function AdcContext() {
  // D-050: the cohort statistics below are DERIVED from the live cohort, never hardcoded — a literal
  // count rots silently as the cohort grows (this copy once read "42 … 34.78 to 81.40 … 45%", stale
  // by 42->79). Folded = analyses carrying a numeric mean_plddt; 60 is the D-039 trust divider.
  const [stats, setStats] = useState(null)
  useEffect(() => {
    listAnalyses()
      .then((rows) => {
        const vals = rows
          .map((r) => r.mean_plddt)
          .filter((v) => typeof v === 'number' && !Number.isNaN(v))
        if (!vals.length) return
        const below = vals.filter((v) => v < 60).length
        // D-051 §5: NECTIN4's mean pLDDT was the last hardcoded per-target literal (77.26); derive
        // it from the same fetch. NECTIN4 is id 1 (the prose commits to that); fall back to gene.
        const nectin = rows.find((r) => r.gene === 'NECTIN4' || r.id === 1)
        setStats({
          n: vals.length,
          min: Math.min(...vals),
          max: Math.max(...vals),
          belowPct: Math.round((below / vals.length) * 100),
          nectin4: nectin && typeof nectin.mean_plddt === 'number' ? nectin.mean_plddt : null,
        })
      })
      .catch(() => setStats(null))
  }, [])

  return (
    <div className="prose">
      <h2>What an <Term name="ADC">ADC</Term> is, and why target choice is the hard part</h2>

      <p>
        Standard chemotherapy is a blunt weapon: it attacks fast-dividing cells all over the body,
        so it harms healthy tissue along with the tumour. An <strong>antibody–drug conjugate</strong>{' '}
        is a guided one:
      </p>
      <ul className="adc-parts">
        <li><strong>Antibody</strong> — guidance. It binds a protein the tumour over-expresses.</li>
        <li><strong>Linker</strong> — the fuse. It holds the payload inert in circulation.</li>
        <li><strong>Payload</strong> — the warhead. A cytotoxic released at the target cell.</li>
      </ul>
      <p>That is a genuine change in <em>delivery mechanism</em>, and the metaphor names it accurately.</p>

      <AdcSchematic />

      {/* D-097: anatomy, then process. The schematic above names the parts; the panels below show
          what those parts do, in order. ⚠ The order is load-bearing — "the linker is cut" in panel
          3 is unreadable to someone who has not been shown a linker. */}
      <h3>What happens when it reaches the tumour cell</h3>
      <p>
        Those parts act in a sequence. The antibody finds its target on the cell surface and binds
        it; the cell draws the whole assembly inside; the linker is cut; and the payload is released
        where it can act. <strong>NECTIN4</strong> is the target below, and enfortumab vedotin
        (PADCEV) is the ADC — the worked example this project returns to throughout.
      </p>

      <AdcMechanismPanels />

      <h3>What the mechanism does not license</h3>
      <p>
        The metaphor is about delivery, not cure. ADCs are a real advance — enfortumab vedotin
        targets <strong>NECTIN4</strong> and changed outcomes in bladder cancer — but the payload is
        still toxic, the linker can release it too early in the blood, and each drug brings its own
        serious side effects (harm to the lungs, eyes, and nerves, depending on the agent). Tumours
        also fight back, often by making less of the target protein. So an ADC is only as good as its
        target.
      </p>

      <h3>Why this project exists</h3>
      <p>
        A target must be well-expressed on tumour cells, spare enough on healthy tissue, accessible to
        an antibody, and stable enough not to be simply switched off under pressure.{' '}
        <strong>Choosing well is the unsolved part — which is what this project is about.</strong>
      </p>
      <p>
        <strong>NECTIN4</strong> is the worked example. Enfortumab vedotin was approved for metastatic
        urothelial carcinoma — where patients past platinum chemotherapy and a checkpoint inhibitor had
        little left — and later displaced platinum in the first-line setting with pembrolizumab, the
        rarer achievement of a standard of care changing. It is <code>id 1</code> in this cohort, the
        first target folded through this system's production path{stats?.nectin4 != null && (
          <>, at mean pLDDT <strong>{stats.nectin4.toFixed(2)}</strong></>
        )}. <Link to="/target/1">See its structure →</Link>
      </p>

      <h3>⚠ The success case is a bad prior — and this cohort's own data shows it</h3>
      <p>
        NECTIN4 is well-expressed, accessible, and stable. <strong>Most candidates are not.</strong>{' '}
        {stats ? (
          <>Across the {stats.n} folded targets, mean pLDDT runs from{' '}
          <strong>{stats.min.toFixed(2)} to {stats.max.toFixed(2)}</strong>, and{' '}
          <strong>{stats.belowPct}% fall below 60</strong> — a region where the structure is not
          reliably interpretable.</>
        ) : (
          <>Across the folded targets, mean pLDDT spans a wide range and a substantial fraction fall
          below 60 — a region where the structure is not reliably interpretable.</>
        )}{' '}
        Enfortumab vedotin proves the <em>mechanism</em>; it says nothing about how easy
        the next target is. A tool built in admiration of the one that worked could quietly encode
        "find me more NECTIN4s" — and the{' '}
        <Link to="/coverage">honest coverage line</Link>, the confidence bands, and the
        detection-not-explanation boundary (<Link to="/method">method</Link>) are the discipline that
        prevents exactly that.
      </p>
      {/* F-009 — the cohort-boundary paragraph. OWNER-COPY PLACEHOLDER: substance fixed by the order,
          wording for the owner to finalise. The example targets are DERIVED from heldoutExamples.js,
          which is drift-tested against data/heldout_positives.csv, so no accession is hand-typed. */}
      <h3>What the 82 is — a comparator, not a census</h3>
      <p>
        The {stats ? stats.n : ''} targets here come from one published cohort (Kathad et al.), selected
        by <strong>expression and selectivity</strong> in tumour tissue. That makes it a{' '}
        <strong>comparator set</strong> — the fixed list this project re-orders — and{' '}
        <strong>not a complete census</strong> of antigens an ADC could target.
      </p>
      <p>
        The boundary is checkable, because clinically-validated ADC targets fall outside it:{' '}
        {HELDOUT_EXAMPLES.map((e, i) => (
          <span key={e.uniprot_accession}>
            {i > 0 ? ', ' : ''}
            <strong>{e.display}</strong> ({e.adc})
          </span>
        ))}
        . Each is the target of an approved or late-phase ADC, and each is absent because the
        cohort&rsquo;s <em>expression</em> filter excluded it — not because it is a poor target.
      </p>
      {/* ⚠ Phrased to avoid the over-claim vocabulary ENTIRELY, not to negate it. The denylist test
          matches phrases, so it cannot tell an assertion from a disclaimer — and it should not have
          to. A guard that must parse negation is a guard that can be talked around, so the copy
          simply does not use the words. */}
      <p className="note">
        Stated plainly: a re-ordering of this comparator is a claim about <em>this</em> list, not about
        the whole target space. The targets above are unfolded and unscored here, so this project makes
        no judgement about them either way — the honest point is that the comparator has blind spots,
        not that anything else fills them. It is the same discipline that resists &ldquo;find me more
        NECTIN4s&rdquo;: a slice is not the whole.
      </p>
      <p className="note">
        Conviction about the mechanism, precision about the limits. The mechanism is proven and worth
        being excited about; the target selection is where the difficulty actually lives; and a system
        honest about which is which is the more persuasive artefact, not the more timid one.
      </p>

      {/* D-107: future msa tier, named and marked not-built. ESMFold remains the cheap first pass
          we actually run. AlphaFold 3 is out of scope until a license and a compute path still mean
          we ran it. The 48 hold and the 246 reap are not this entry. */}
      <h3>What&rsquo;s next (not built)</h3>
      <p>
        A second fold recipe beside ESMFold — MSA search, then an AF2-class model. Same queue, same
        artifacts, same UI. ESMFold stays the cheap first pass. AlphaFold 3 is out of scope until we
        can name a license and a compute path that still means we ran it.
      </p>
    </div>
  )
}
