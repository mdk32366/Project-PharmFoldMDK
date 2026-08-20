// The clinical edges — D-093 edges 1 and 2. On BOTH card types (owner ruling, option 2).
//
// ⚠⚠ THIS IS THE SECTION THAT TIES A PROTEIN TO SOMETHING A PERSON CAN UNDERSTAND. Not a score:
// patient counts. "Of 12 ovarian tumours tested, 10 stained positive" is a sentence a clinician,
// a reviewer and a stranger all read the same way, and it is the point of the whole layer.
//
// ⚠ BOTH EDGES OR NEITHER (D-093 decision 5, amendment 2 ruling 2). The tumour panel alone is the
// flattering half. MSLN stains in 83% of ovarian tumours AND stains High in bronchus and fallopian
// tube — a card showing only the first would be selling rather than describing, so the normal
// tissues render in the same section, never behind a tab or a fold.
//
// ⚠⚠ AND IT IS NOT THE EXPRESSION GRID. `CancerAssociations` (D-053) shows the paper's quasi
// H-score over the 82; this shows HPA immunohistochemistry over 3,364 genes. Different measurement,
// different source, different population — and the 82 appear in BOTH. They are kept as two
// visibly distinct sections with different headings, different wording and different classes,
// because F-049's family is one thing wearing two names and this is the inverse risk: two things
// a reader would happily merge into one.
//
// ⚠ No ratio is shown. tumour_normal_ratio() raises by design (ruling 4) and nothing here divides.

import { HpaDeepLink } from './HpaAttribution.jsx'
import { ofCount, plural } from '../plural.js'
import { poolingMarker } from '../tumourPooling.js'

const LEVEL_WORD = {
  High: 'strong', Medium: 'moderate', Low: 'weak', 'Not detected': 'none',
}

// ⚠⚠ `heading` AND `scopeNote` EXIST BECAUSE OF AN OWNER RULING (2026-08-21): promote the HPA
// panels into the "Cancer associations" section, census-wide.
//
// The census card carried TWO adjacent cancer headings: this one, full — LAMP1 stains in breast
// 11/11, cervical 12/12, colorectal 12/12 — and "Cancer associations" immediately beneath it,
// empty. **The association source is the 82 cohort targets and nothing else** (337 rows, 82 distinct
// symbols), so for all 3,385 census proteins that box could never fill. A reader looking for cancer
// associations found the empty one and stopped.
//
// ⚠ D-093 KEEPS THE TWO MEASUREMENTS SEPARATE AND THIS DOES NOT MERGE THEM. Kathad's quasi H-score
// and HPA's patient counts are different measurements from different sources; blending them is
// what the ruling forbids. On a COHORT card both exist and both still render, separately. On a
// CENSUS card the Kathad measurement DOES NOT EXIST — there is nothing to keep separate from — so
// the section a reader reads for cancer associations is the one that has data, and the fact that
// the other source does not cover this protein is demoted to a footnote rather than a heading.
//
// ⚠ Tumours and normal tissues still render TOGETHER: D-093 decision 5 makes the normal-tissue
// differential co-equal, and a tumour panel alone is the flattering half.
export default function ClinicalEdges({ block, heading, scopeNote }) {
  if (!block) return null
  const title = heading ?? 'Cancer connection'

  // ⚠ An absent gene is a CATEGORY, not an empty panel: HPA's IHC covers fewer proteins than its
  // RNA does, and 960 of 2,687 folded census genes are absent. Saying "no data" would read as
  // "tested and found nothing", which is a different and false claim.
  if (block.status === 'ihc_gene_absent' || block.status === 'not_determinable') {
    return (
      <section className="clin">
        <h3>{title}</h3>
        {scopeNote}
        <p className="clin-absent">
          <strong>Not covered by the antibody atlas.</strong>{' '}
          {block.status === 'not_determinable'
            ? 'This record carries no gene symbol, so the protein cannot be looked up.'
            : 'This protein is not among those stained and scored by the Human Protein Atlas.'}{' '}
          That means <em>nobody looked</em> — not that they looked and found nothing.
        </p>
        <BurdenSlot />
      </section>
    )
  }

  const { tumours = [], normal_tissues: normals = [] } = block

  return (
    <section className="clin">
      <h3>{title}</h3>
      {scopeNote}
      <p className="clin-boundary">{block.boundary}</p>

      <h4>Where it appears in tumours</h4>
      {tumours.length === 0 ? (
        <p className="clin-absent">
          <strong>Tested, and no tumour panel recorded.</strong> The protein is in the atlas but
          carries no tumour staining — an empty panel, not an absent one.
        </p>
      ) : (
        <ul className="clin-tumours">
          {tumours.map((t) => {
            // ⚠⚠ D-093 amendment 10 §4/§5 — the marker is a property of the (protein × tumour type)
            // PAIR, so it is computed HERE, per row, and NOT as a card banner. Returns null for the
            // 17 of 20 categories nothing is sourced for, and those rows render exactly as before.
            const pooling = poolingMarker(block.gene, t.cancer)
            return (
            <li key={t.cancer}>
              <span className="clin-cancer">{t.cancer}</span>
              <span className="clin-count">
                {/* ⚠ the COUNTS, not just the fraction. 10 of 12 and 100 of 120 are different
                    facts, and a bare percentage hides which one you are reading. */}
                <strong>{t.patients_positive}</strong> of <strong>{t.patients_tested}</strong>{' '}
                {plural(t.patients_tested, 'sample')} stained
              </span>
              {/* ⚠⚠ SELF-SUFFICIENT. "A flag that requires a click to mean anything is not a
                  disclosure" — so the sentence says WHAT is pooled, never merely that something is.
                  ⚠ The source rides with the claim: a row cannot render the caveat without the
                  citation that licenses it. */}
              {pooling && (
                <span className="clin-pooled" title={pooling.sources.join(' · ')}>
                  {' '}⚠ {pooling.text}
                </span>
              )}
            </li>
          )})}
        </ul>
      )}

      {/* ⚠⚠ CO-EQUAL, IN THE SAME SECTION, NEVER COLLAPSED OR HIDDEN. This is the half that
          qualifies a target instead of selling it: a protein that stains in tumours AND in healthy
          lung is a harder ADC problem, and the card must say so on the same screen. */}
      <h4>Where it also appears in healthy tissue</h4>
      {normals.length === 0 ? (
        <p className="clin-absent">
          <strong>No staining recorded in normal tissue.</strong> Read with care: absence here
          means the panel did not detect it, not that it is absent from the body.
        </p>
      ) : (
        <>
          <p className="clin-normal-why">
            A protein that also sits on healthy tissue is a harder target — the payload cannot
            tell the two apart.
          </p>
          {/* ⚠⚠ THE TWO HALVES ARE CO-EQUAL IN POSITION AND UNEQUAL IN EVIDENTIAL WEIGHT, AND
              UNTIL NOW THE SURFACE DID NOT SAY SO. The tumour half prints its n on every row
              ("10 of 12 samples stained"). This half printed "2 of 3 cell types" — which LOOKS
              like a sample size and is not one. HPA's own methods page: normal tissues are
              "represented by samples from three individuals each, one core per individual".
              ⚠ A reader comparing 10-of-12 against a confident-looking "High" is comparing
              twelve patients against three people, and nothing on the card told them. */}
          <p className="clin-normal-basis">
            <strong>Read the weight of this, not just the word.</strong> The atlas stains{' '}
            <strong>three individuals per tissue</strong> (a few tissues six, one just one), so a
            level here rests on far fewer people than the tumour counts above. The cell-type figure
            below is <em>not</em> a patient count. ⚠ How the level is decided when those
            individuals disagree is <strong>not documented at the source</strong>.
          </p>
          <ul className="clin-normals">
            {normals.map((n) => (
              <li key={n.tissue}>
                <span className="clin-tissue">{n.tissue}</span>
                <span className="clin-level">
                  {LEVEL_WORD[n.highest] ?? n.highest} staining
                  <span className="clin-cells"> · {ofCount(n.detected_in, n.cell_types, 'cell type')}</span>
                </span>
              </li>
            ))}
          </ul>
        </>
      )}

      <BurdenSlot />
      {/* ⚠⚠ PER VIEW, not per page: the tumour panel links to /pathology and the normal
          panel to /tissue. A single block per page does not discharge the precondition. */}
      {/* ⚠⚠ PER VIEW AND PER PRESENCE. The tumour panel links to /pathology and the normal
          panel to /tissue — DIFFERENT deep links, so these two never collapse into one. Measured:
          75 of 79 sampled cards carry three distinct deep links across their blocks, which is
          why the fix is a SPLIT BY CASE and not a de-duplication.
          ⚠ Each half appears only when its own half rendered rows: `normal_tissues` was empty on
          39 of 79 sampled cards while still carrying a citation. */}
      {block.tumours?.length > 0 && (
        <HpaDeepLink attribution={block.attribution_tumour} view="pathology" />
      )}
      {block.normal_tissues?.length > 0 && (
        <HpaDeepLink attribution={block.attribution_normal} view="normal_tissue" />
      )}
      <p className="clin-source">{block.source}</p>

      {/* ⚠⚠ THE SURFACE QUOTES THE PAGE — owner ruling R1. It does NOT adopt the licence.
          The first version asserted "CC BY-SA 3.0", taking a side. Amendment 4 removed the
          assertion and left silence. ⚠ Silence leaves a reader unable to verify anything; an
          attributed quotation with a resolvable link and a date is verifiable and claims nothing.
          ⚠⚠ THREE PROPERTIES, EACH ASSERTED SEPARATELY: the attributive clause (reported speech,
          never adoption), the link (a quotation without one is just a claim in someone else's
          words), and the date read (the page can change; ours is pinned to a day).
          ⚠ The quotation is VERBATIM and includes "3.0 International" — a version that does not
          exist. We do not say so here. Correcting someone else's page on our page is worse than
          quoting it, and that observation belongs in the log. */}
      {block.licence_statement && (
        <figure className="clin-licence">
          <figcaption className="clin-licence-attrib">
            {block.licence_statement.attributive}{' '}
            (<a href={block.licence_statement.url} rel="noopener noreferrer" target="_blank">
              {block.licence_statement.url}
            </a>, read {block.licence_statement.date_read}):
          </figcaption>
          <blockquote className="clin-licence-quote">
            &ldquo;{block.licence_statement.quotation}&rdquo;
          </blockquote>
        </figure>
      )}
    </section>
  )
}

// ⚠⚠ RULING 1 MADE VISIBLE. The burden slot RENDERS — never a blank, never a zero, never an
// omission. A missing section reads as "not relevant"; a stated refusal reads as "we know this is
// missing and why", which is the only honest version.
function BurdenSlot() {
  // ⚠⚠ THE COPY LIVES HERE, NOT IN THE PAYLOAD, AND A GUARD IS WHY. `D-093` decision 1: clinical
  // burden is a property of the DISEASE — it attaches by traversal and may never be a
  // protein-level field. The first version shipped `burden` and `burden_note` on the protein
  // block and `test_no_protein_level_model_or_payload_carries_a_burden_field` reddened on it.
  // ⚠ The refusal is identical for every protein and every disease, so it is a constant, not data.
  return (
    <div className="clin-burden">
      <h4>How common, how deadly</h4>
      {/* ⚠⚠ THE CAUSE WAS RESTATED AS THE MEASURED ONE (owner ruling, 2026-08-21). This block used
          to lead with "no licensed source", which is true of the ONE withdrawn source and is NOT
          why the others are unattempted. `D-093` amendment 6 measured the actual obstacle, and it
          is a VOCABULARY problem, not a licensing one — so a reader was being given a reason that
          would not be fixed by obtaining a licence. */}
      {/* ⚠⚠ ONE LINE, AND THE PREVIOUS VERSION WAS FALSE (owner ruling, 2026-08-21 · `WA`).
          It said *"the tumour names cannot be matched up"* — a claim of total impossibility.
          `D-093` amendment 6 measured **four failures out of twenty**. Generalising four into all
          twenty is not a caveat, it is a false statement, and replacing a false claim with a true
          one waits on nothing.
          ⚠ AND ~150 WORDS EXPLAINING AN ABSENCE, ON 2,690 CARDS, OUTWEIGHED THE TUMOUR PANEL BELOW
          THAT HAS DATA — which is how a reader concludes the protein has none. The explanation
          belongs on the crosswalk page; the card gets the fact.
          ⚠ No number here until `VA`/`WB` reports: "how many" is being measured, and printing a
          count before it is measured would repeat the error in the other direction. */}
      <p className="clin-burden-missing">
        <strong>Incidence and survival are not shown — we do not have that data.</strong> Some
        tumour names in this atlas cannot be reliably matched to registry categories; how many is
        being measured.
      </p>
    </div>
  )
}
