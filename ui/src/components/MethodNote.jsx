import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { getCoverage } from '../api.js'
import ArchitectureDiagram from './ArchitectureDiagram.jsx'
import Glossary from './Glossary.jsx'
import SpanGlossary from './SpanGlossary.jsx'
import Term from './Term.jsx'

// Method note (UI Plan v2 §3.4, D-028): what the system claims and what it does not — the whole
// frame at once, for a reader who wants it. Non-goals are commitments, not omissions (§9). This
// does NOT replace the inline per-class tooltips the ranking will carry; it is the standing scope.
export default function MethodNote() {
  // D-050: the coverage line is DERIVED from /api/coverage (the authoritative denominator, D-038),
  // computed the same way CoverageLine does — ranked AND folded, never a hardcoded literal (this
  // copy once read "40 ranked-and-folded of 82", stale once the cohort reached 67 ranked∧folded).
  const [cov, setCov] = useState(null)
  useEffect(() => {
    getCoverage().then(setCov).catch(() => setCov(null))
  }, [])
  const rankedFolded = cov
    ? cov.rows.filter((r) => r.disposition === 'ranked' && r.fold_status === 'folded').length
    : null
  const denominator = cov?.coverage?.denominator

  return (
    <div className="prose">
      <h2>What this system claims — and what it does not</h2>
      <p>
        PharmFoldMDK folds a fixed cohort of {denominator != null ? <>{denominator} </> : null}candidate{' '}
        <Term name="ADC">ADC</Term> targets with{' '}
        <strong><Term name="ESMFold">ESMFold</Term>, run in-project</strong>, and renders each
        structure with the model's own confidence (<Term name="pLDDT">pLDDT</Term>) and
        full provenance. This is a deep-learning course project: the neural network is the
        deliverable, and every structure here was <em>produced by it</em>, not retrieved from a
        database.
      </p>

      <h3>Where the deep learning runs (D-051)</h3>
      <p>
        Inference runs on a GPU tier <strong>outside Fly</strong> (D-004): the local worker and the
        rented GPU (A6000 for the cohort-29 batch; RTX PRO 6000 Blackwell for
        hold-48 tiles) pull jobs over outbound HTTPS, fold, and upload results. Hold-48
        stitch is a <strong>pLDDT-overlap assembler</strong>, not a Kabsch
        superimposer — seams are not scientifically solved. The always-on Fly
        serving tier holds <strong>no <code>worker/</code> and no CUDA</strong> (DEP-001). The diagram
        is rendered from a committed system model and pinned to the live route table by a test, so it
        cannot drift from the running system.
      </p>
      <ArchitectureDiagram />

      <h3>Long proteins: tiles, glue, and a winner-tile assembler (D-121)</h3>
      <div data-testid="hold48-explainer">
        <p>
          Some proteins are too long for <Term name="ESMFold">ESMFold</Term> to
          swallow in one gulp. <strong>D-111</strong> already named the cap: a
          window of <strong>1656</strong> amino acids, with a{' '}
          <strong>128</strong>-amino-acid overlap between neighboring windows.
          We cut those long chains into <strong>overlapping tiles</strong> —
          like shingles. Each tile is its own network pass. The model never
          sees the whole long chain at once.
        </p>
        <p>
          The overlap is the <strong>glue</strong>. It is not a chemical glue.
          It is the same residues, predicted twice, so two tiles have a shared
          stretch we can compare. We do <strong>not</strong> twist one tile
          until it sits on the other.
        </p>
        <p>
          Assemble means pick a <strong>winner tile</strong> by{' '}
          <Term name="pLDDT">pLDDT</Term> at each residue — a{' '}
          <strong>pLDDT winner-tile assembler</strong>,{' '}
          <strong>not Kabsch</strong>. Kabsch would rotate and slide pieces so
          they line up in 3D. We did not do that. Each residue keeps the
          coordinates its winning tile already had.
        </p>
        <p>
          Seams can look ugly. On the IGF2R pilot the join jumped about{' '}
          <strong>~88.76 Å</strong>. That is a disclosure,{' '}
          <strong>not scientifically solved</strong>. What a Kabsch-path
          restitch does — and does not do — is named in the D-125-B
          addendum below. This section is still the assembler story.
        </p>
        <p>
          The hold-48 rental is <strong>CLOSED</strong> (pod Terminated,
          2026-09-05; D-118). This section is not a request to rent another
          card.
        </p>
        <p className="note">
          Owner-facing write-up:{' '}
          <code>docs/method-hold48-tiles.md</code> (D-121). Parents: D-118
          honesty, D-120 review UI. #229 stays merged.
        </p>
      </div>

      <h3>Kabsch-path restitch — what it does, and what it does not (D-125-B)</h3>
      <div data-testid="kabsch-method-addendum">
        <p>
          The assembler path above is still the <strong>default served
          structure</strong>. A later GO wrote a second, sibling tree of
          files under <code>kabsch/{'{parent}'}</code>. This page does not
          swap that tree in as &quot;the&quot; structure.
        </p>
        <p>
          <strong>What Kabsch does.</strong> After the tiles are already
          folded by <Term name="ESMFold">ESMFold</Term>, Kabsch is a math
          move. It rotates and slides one tile so the shared stretch (the
          glue residues&apos; Cα atoms) sits closer to the other tile&apos;s
          shared stretch. Then the same winner-tile assembler still picks
          which tile wins each residue. The network does not run again. No
          atom is invented. A refused seam writes a record and does not
          write a &quot;fixed&quot; structure.
        </p>
        <p>
          <strong>What Kabsch does not do.</strong> It does not make the
          long chain one ESMFold pass. It does not fill empty
          pair-confidence (PAE) between tiles. It does{' '}
          <strong>not</strong> mean the joins are scientifically solved.
          Seams are <strong>not scientifically solved</strong>.
          It does not put these chains into the ranking. It is not
          medical advice and it is not a holoprotein the model jointly
          placed.
        </p>
        <p>
          When both trees are on disk, the review card names them as two
          paths with different persist stems (<code>stitched</code> vs{' '}
          <code>kabsch/{'{parent}'}</code>) so they cannot be read as one
          population. Overlap RMSD and max Cα jump are shown only if
          those files already computed them. If the numbers are missing,
          the card says so — it does not invent them.
        </p>
        <p className="note">
          Owner-facing addendum: <code>docs/method-hold48-tiles.md</code>{' '}
          (D-125-B). Parent Spec: <code>docs/SPEC-kabsch-restitch.md</code>.
        </p>
      </div>

      <h3>Overlap-confidence Kabsch — what it does, and what it does not (D-126-B)</h3>
      <div data-testid="confidence-kabsch-method-addendum">
        <p>
          The assembler path above is still the <strong>default served
          structure</strong>. A later GO wrote a third, sibling tree of
          files under <code>confidence_kabsch/{'{parent}'}</code>. This
          page does not swap that tree in as &quot;the&quot; structure.
          The D-125 Kabsch-path files stay a separate population.
        </p>
        <p>
          <strong>What overlap-confidence Kabsch does.</strong> After
          the tiles are already folded by{' '}
          <Term name="ESMFold">ESMFold</Term>, this third path is still
          a math move. It rotates and slides one tile so the shared
          stretch sits closer to the other tile. The difference is
          which glue atoms it listens to: it down-weights shaky
          residues (low <Term name="pLDDT">pLDDT</Term>) and can drop
          the worst-fitting 10% of overlap points, then measures a
          weighted RMSD. The 10.0 Å refuse gate stays. Then the same
          winner-tile assembler still picks which tile wins each
          residue. The network does not run again. No atom is invented.
          A refused seam writes a record and does not write a
          &quot;fixed&quot; structure.
        </p>
        <p>
          <strong>What overlap-confidence Kabsch does not do.</strong>{' '}
          It does not replace the assembler. It does not overwrite the
          D-125 Kabsch-path files. It does not make the long chain one
          ESMFold pass. It does not fill empty pair-confidence (PAE)
          between tiles. It does <strong>not</strong> mean the joins
          are scientifically solved. Seams are{' '}
          <strong>not scientifically solved</strong>. It does not put
          these chains into the ranking. It is not medical advice and
          it is not a holoprotein the model jointly placed. It does
          not invent RMSD or trim counts when the third tree is
          missing.
        </p>
        <p>
          When the third tree is on disk, the review card names three
          paths with different persist stems (<code>stitched</code> vs{' '}
          <code>kabsch/{'{parent}'}</code> vs{' '}
          <code>confidence_kabsch/{'{parent}'}</code>) so they cannot
          be read as one population. Weighted RMSD, full-overlap RMSD,
          max Cα jump, effective Cα count, and trim rounds are shown
          only if those files already computed them. If the numbers
          are missing, the card says so — it does not invent them.
          When the third tree is missing, the card does not pretend
          the D-126 path exists.
        </p>
        <p className="note">
          Owner-facing addendum: <code>docs/method-hold48-tiles.md</code>{' '}
          (D-126-B). Parent Spec:{' '}
          <code>docs/SPEC-overlap-confidence-kabsch.md</code>.
        </p>
      </div>

      <h3>Piecewise / domain-aware Kabsch, and the whole stitch-path train (D-127-B)</h3>
      <div data-testid="piecewise-kabsch-method-addendum">
        <p>
          There are now <strong>four</strong> ways this project has put
          two folded tiles next to each other. They are not four
          answers to one question; they are four different moves, and
          only the first one is served. Here is the train, in order.
        </p>
        <ol>
          <li>
            <strong>Assembler</strong> — pick the winner tile by{' '}
            <Term name="pLDDT">pLDDT</Term> at each residue. This is
            the <strong>default served</strong> structure, and it stays
            that way until Matt says otherwise.
          </li>
          <li>
            <strong>D-125 Kabsch</strong> — one unweighted rigid move
            on the glue Cα atoms, then the same assembler.
          </li>
          <li>
            <strong>D-126 confidence</strong> — one weighted and
            trimmed rigid move on the same glue, then the same
            assembler. This one taught us something: a small{' '}
            <strong>weighted</strong> RMSD can hide a large{' '}
            <strong>full-overlap</strong> jump. On 2939 / 3272 / 3432
            the full-overlap number was far larger than the weighted
            one, with Cα jumps of about{' '}
            <strong>28–68 Å</strong>. A number you got by dropping the
            points that disagreed with you is not a solved seam.
          </li>
          <li>
            <strong>D-127 piecewise / domain</strong> — one weighted
            rigid move <strong>per UniProt domain</strong> that
            overlaps the glue, then the same assembler.{' '}
            <strong>No trim loop.</strong> Residues between domains
            (the linkers) inherit the nearest domain on their
            N-terminal side that was accepted.
          </li>
        </ol>
        <p>
          <strong>The refuse table, in plain terms.</strong> A domain
          piece can refuse if it has fewer than three Cα atoms to fit,
          if its weighted RMSD comes out above <strong>10.0 Å</strong>,
          or if its points sit in a line. The whole parent refuses if
          no domain covers the glue at all, or if a linker Cα jumps
          more than <strong>10.0 Å</strong>. A refuse writes a record.
          It does not write a &quot;fixed&quot; structure, and the
          10.0 Å gate <strong>stays</strong> — recovering none of those
          three parents is an allowed result, not a reason to move the
          bar.
        </p>
        <p>
          <strong>What the seam numbers are.</strong> When the fourth
          tree is on disk, the review card names each piece separately:
          its domain interval, how many Cα it fitted, its weighted
          RMSD, and whether it refused. Beside them sit the parent
          full-overlap RMSD and max Cα jump after those moves, and the
          linker count with its worst jump. Those are{' '}
          <strong>measurements</strong>. They are not a verdict that the
          holoprotein is lined up. Seams are{' '}
          <strong>not scientifically solved</strong>.
        </p>
        <p>
          <strong>What piecewise Kabsch does not do.</strong> It does
          not replace the assembler, and the served PDB is still the
          assembler one. It does not overwrite the D-125 or D-126
          files. It does not make the long chain one ESMFold pass. It
          does not fill empty pair-confidence (PAE) between tiles. It
          does not put these chains into the ranking. It is not
          medical advice and it is not a holoprotein the model jointly
          placed. When the fourth tree is missing, the card says so —
          it does not invent per-piece RMSD, piece counts, or linker
          counts, and that absence is not a solved seam.
        </p>
        <h4>What happened when we actually ran it (D-127 OPS, 2026-09-05)</h4>
        <p className="note">
          ⚠ Ops numbers <strong>as recorded</strong> and handed to this
          page (Matt GO via Emma, 2026-09-05, naming a D-127 OPS
          restitch of the 27 at tip <code>e49bf34</code>).{' '}
          <strong>Not run, not queried, and not re-measured here.</strong>
        </p>
        <p>
          We ran piecewise / domain-aware Kabsch over the 27 stitched
          parents: <strong>PASS 17 · REFUSE 10 · FAIL 0</strong>.
          Seventeen accepted is not the headline, and here is why.
        </p>
        <ul>
          <li>
            <strong>It recovered none of the three parents it was
            built for.</strong>{' '}
            <code>recovered_of_primary_three</code> = <strong>0</strong>.
            Parent <strong>2939</strong> refused{' '}
            <code>linker_jump_gt_10</code>, <strong>3272</strong>{' '}
            refused <code>rmsd_gt_10</code>, and <strong>3432</strong>{' '}
            refused <code>no_domain_pieces</code>. Those three were the
            whole reason the multi-rigid family was proposed.
          </li>
          <li>
            <strong>It lost ground the earlier paths had held.</strong>{' '}
            <code>n_d125_pass_d127_refuse</code> = <strong>5</strong> —
            five parents D-125 accepted now refuse.{' '}
            <code>n_d126_pass_d127_refuse</code> = <strong>7</strong> —
            seven parents D-126 accepted now refuse. And{' '}
            <code>n_d126_refuse_d127_pass</code> = <strong>0</strong> —
            piecewise did not rescue a single parent D-126 had already
            refused. That is a <strong>named finding</strong>, not a
            footnote under an accept count.
          </li>
          <li>
            <strong>Where the refuses came from.</strong>{' '}
            <code>linker_jump_gt_10</code> <strong>×7</strong> (2938,
            2939, 3179, 3190, 3321, 3368, 3566);{' '}
            <code>rmsd_gt_10</code> <strong>×2</strong> (3272, 3394);{' '}
            <code>no_domain_pieces</code> <strong>×1</strong> (3432).
            Most failures are at the <strong>linkers</strong> — the
            stretches between domains — which is exactly where cutting
            one rigid body into several creates new joins.
          </li>
        </ul>
        <p>
          <strong>So: D-126 remains the best experimental path among
          the stitch algorithms we have tried so far.</strong> Plainly.
          And the comparison is a number, not an opinion:{' '}
          <strong>D-126 OPS recovered 2 of its primary 5</strong> —
          parents <strong>3368</strong> and <strong>3394</strong> —
          against D-127&apos;s <strong>0 of 3</strong>. (Both figures
          are ops results as recorded and handed to this page;{' '}
          <strong>not re-measured here</strong>.)
        </p>
        <p>
          Worse than &quot;no gain&quot;:{' '}
          <strong>both parents D-126 recovered are back in D-127&apos;s
          refuse list</strong> — <strong>3368</strong> under{' '}
          <code>linker_jump_gt_10</code> and <strong>3394</strong>{' '}
          under <code>rmsd_gt_10</code>, as the histogram above shows.
          Piecewise gave back the ground the previous path had won.
        </p>
        <p>
          D-127 was a reasonable hypothesis — fit each domain in its own
          frame instead of forcing one frame on the whole tile — and the
          run says it did not pay off.
        </p>
        <p>
          Recovering zero of the three was{' '}
          <strong>pre-registered as an allowed outcome</strong> before
          the run. It is a result, not a failure of nerve, and it is{' '}
          <strong>not</strong> a reason to raise the 10.0 Å gate, relax
          the linker gate, add a trim loop, or invent a blend.{' '}
          <strong>No threshold moved because of this run.</strong>{' '}
          Nothing here flips the served path either: the{' '}
          <strong>default served structure is still the assembler</strong>,
          and only a Matt GO can change that — never a pass count. And
          17 accepted parents are <strong>17 recorded outcomes</strong>,
          not 17 solved joins. A seam that was recorded is not a seam
          that was solved.
        </p>
        <p>
          When the fourth tree is on disk, the review card names four
          paths with four persist stems (<code>stitched</code> vs{' '}
          <code>kabsch/{'{parent}'}</code> vs{' '}
          <code>confidence_kabsch/{'{parent}'}</code> vs{' '}
          <code>piecewise_kabsch/{'{parent}'}</code>) so they cannot be
          read as one population. The served download is still the
          assembler <code>stitched</code> one.
        </p>
        <p className="note">
          Owner-facing addendum: <code>docs/method-hold48-tiles.md</code>{' '}
          (D-127-B). Parent Spec:{' '}
          <code>docs/SPEC-piecewise-domain-kabsch.md</code> §6 / §7 —
          which makes this section <strong>mandatory</strong>, not a
          later nice-to-have.
        </p>
      </div>

      <h3>Linker / seam honesty, and the five-step stitch-path train (D-128-B)</h3>
      <div data-testid="linker-seam-method-addendum">
        <p>
          There are now <strong>five</strong> ways this project has put
          two folded tiles next to each other — and the fifth is not
          really another way of joining them. It is a way of{' '}
          <strong>checking</strong> the other four. Here is the train, in
          order.
        </p>
        <ol>
          <li>
            <strong>Assembler</strong> — pick the winner tile by{' '}
            <Term name="pLDDT">pLDDT</Term> at each residue. The{' '}
            <strong>default served</strong> structure, until Matt says
            otherwise.
          </li>
          <li>
            <strong>D-125 Kabsch</strong> — one unweighted rigid move on
            the glue Cα, then the same assembler.
          </li>
          <li>
            <strong>D-126 confidence</strong> — one weighted and trimmed
            rigid move on the same glue. Its lesson: a small{' '}
            <strong>weighted</strong> RMSD can hide a large{' '}
            <strong>full-overlap</strong> jump (about{' '}
            <strong>28–68 Å</strong> on 2939 / 3272 / 3432).{' '}
            <strong>D-126 is still the best experimental path we have
            tried</strong>, having recovered <strong>2 of its primary
            5</strong> — parents <strong>3368</strong> and{' '}
            <strong>3394</strong>.
          </li>
          <li>
            <strong>D-127 piecewise / domain</strong> — one weighted
            rigid move <strong>per UniProt domain</strong>.{' '}
            <strong>The run says it did not pay off:</strong> PASS 17 /
            REFUSE 10 / FAIL 0, <strong>0 of 3</strong> recovered, giving
            back 5 parents D-125 had accepted and 7 D-126 had accepted.
            That failed experiment <strong>stays disclosed</strong> in
            the section above, and none of D-128&apos;s numbers stand in
            for it.
          </li>
          <li>
            <strong>D-128 linker / seam honesty</strong> — first,{' '}
            <strong>measure</strong> every path&apos;s seam jump and say
            plainly which paths are <strong>dishonest</strong> at that
            seam (a jump over <strong>10.0 Å</strong>). Then,
            optionally, try <strong>one</strong> small rigid move inside
            a <strong>±32 aa</strong> window around the offending
            linker. Most of D-127&apos;s failures were at the linkers
            (<strong>7 of 10</strong> refuses), which is why the window
            is where it is.
          </li>
        </ol>
        <p>
          <strong>What &quot;dishonest&quot; means here.</strong> It is a
          statement about the <strong>structure file</strong>, not about
          a person. If a path&apos;s seam still jumps more than{' '}
          <strong>10.0 Å</strong> after that path&apos;s own transform,
          then presenting that path&apos;s <code>stitched.pdb</code> as a
          good join would be dishonest — so we refuse it and record why.
          The 10.0 Å gate <strong>stays</strong>.
        </p>
        <p>
          <strong>The refuse table, in plain terms.</strong> A window
          refuses if it has <strong>fewer than three Cα</strong> to fit,
          if its weighted RMSD comes out above <strong>10.0 Å</strong>,
          or if its points sit <strong>in a line</strong>. The parent
          refuses if the seam still jumps more than{' '}
          <strong>10.0 Å</strong> after the move. A refuse writes a
          record. It does not write a &quot;fixed&quot; structure.
        </p>
        <p>
          <strong>What the seam numbers are.</strong> When the fifth tree
          is on disk, the review card names, for{' '}
          <strong>each path and each seam</strong>, the max Cα jump that
          path <strong>ends</strong> with and whether it is therefore
          honest there — plus, for D-128 itself, the window it fitted,
          how many Cα were in it, the weighted RMSD, the jump before and
          after, and how the offending seam was identified. Those are{' '}
          <strong>measurements</strong>. They are not a verdict that the
          holoprotein is lined up. Never claim the seams are solved.
          Seams are <strong>not scientifically solved</strong>.
        </p>
        <p>
          The card shows <strong>one row per path per seam</strong> and
          never an average across them. A mean jump would hide the single
          seam that flies apart, and an &quot;N of M seams honest&quot;
          score would hide <strong>which</strong> path is dishonest{' '}
          <strong>where</strong> — the whole content of the check. A
          missing jump is an absence, never <code>0.00 Å</code>, and an{' '}
          <strong>unknown jump is not honest</strong>.
        </p>
        <p>
          <strong>What linker / seam honesty does not do.</strong> It
          does not replace the assembler, and the served PDB is still the
          assembler one. It does not overwrite the D-125, D-126, or
          D-127 files. It does not make the long chain one ESMFold pass.
          It does not fill empty pair-confidence (PAE) between tiles. It
          does not put these chains into the ranking. It is not medical
          advice and it is not a holoprotein the model jointly placed.
          When the fifth tree is missing, the card says so — it does not
          invent a jump, a window, or an honesty verdict, and that
          absence is not a solved seam.
        </p>
        <h4>What happened when we actually ran it (D-128 OPS, 2026-09-06)</h4>
        <p className="note">
          ⚠ Ops numbers <strong>as recorded</strong> and handed to this
          page (Matt GO via Emma, 2026-09-06, naming a D-128 OPS restitch
          of the must-hunt seven at tip <code>9e65cbf</code>, out_root{' '}
          <code>linker_seam_ops_2026-09-05</code>).{' '}
          <strong>Not run, not queried, and not re-measured here.</strong>
        </p>
        <p>
          We ran the linker / seam path over the seven signed must-hunt
          linker parents: <strong>PASS 0 · REFUSE 7 · FAIL 0 · SKIP
          0</strong>.
        </p>
        <ul>
          <li>
            <strong>It repaired none of the seven.</strong>{' '}
            <code>recovered_of_seven</code> = <strong>0</strong> and{' '}
            <code>repaired_of_seven</code> = <strong>0</strong>. That
            zero was <strong>pre-registered as an allowed outcome</strong>{' '}
            before the code existed, so it is a result — and it is{' '}
            <strong>not</strong> a reason to raise the 10.0 Å gate, relax
            it, add a trim loop, invent a blend, try a second window
            size, or re-open 3432.
          </li>
          <li>
            <strong>Where the refuses came from.</strong>{' '}
            <code>seam_jump_gt_10</code> <strong>×6</strong> (2938, 3179,
            3190, 3321, 3368, 3566) — the ±32 aa window fitted and the{' '}
            <strong>whole seam</strong> still jumped more than 10.0 Å
            afterwards. <code>rmsd_gt_10</code> <strong>×1</strong>{' '}
            (2939) — the window&apos;s own weighted RMSD was above the
            gate, so nothing was applied. ⚠ These are{' '}
            <strong>D-128&apos;s</strong> reason names:{' '}
            <code>seam_jump_gt_10</code> is measured after the single
            window move and is <strong>not</strong> D-127&apos;s{' '}
            <code>linker_jump_gt_10</code>.
          </li>
          <li>
            <strong>It lost ground the earlier paths had held — and a
            zero is not a place to hide that.</strong>{' '}
            <code>n_d125_pass_d128_refuse</code> = <strong>5</strong>;{' '}
            <code>n_d126_pass_d128_refuse</code> = <strong>6</strong>;{' '}
            <code>n_d127_pass_d128_refuse</code> = <strong>0</strong> and{' '}
            <code>n_d127_refuse_d128_pass</code> = <strong>0</strong>,
            because D-127 had already refused all seven. That is a{' '}
            <strong>named finding</strong>, and it ships in the same
            breath as the allowed zero. Reporting &quot;0 of 7, which we
            said was allowed&quot; without the 5 and the 6 beside it
            would bury a drop under a pre-registration.
          </li>
        </ul>
        <p>
          <strong>So: D-126 remains the best experimental path among the
          stitch algorithms we have tried so far.</strong> This run points
          the same way rather than disturbing it: <strong>2 of its
          primary 5</strong> for D-126, against <strong>0 of 3</strong>{' '}
          for D-127 and <strong>0 of 7</strong> for D-128. And{' '}
          <strong>3368</strong> — one of the two parents D-126 recovered —
          sits in this refuse list too, under{' '}
          <code>seam_jump_gt_10</code>. Both later paths gave back ground
          D-126 had won.
        </p>
        <p>
          D-128 was a reasonable hypothesis — if the break is at the
          linkers, fit a small rigid window right there instead of
          cutting the whole tile up — and the run says it did not pay
          off. On <strong>six of the seven</strong> the window{' '}
          <em>fitted</em> and the seam broke anyway, which is evidence
          about that hypothesis and <strong>not</strong> evidence that
          the joins are closer to being solved. It is also one run, as
          recorded, at one window size: <strong>W = 32</strong> stays a
          pinned default, not a measured optimum.
        </p>
        <p>
          <strong>And no linker-v2.</strong> The obvious move after 0 of
          7 is to go round again with a different window — a wider one, a
          narrower one, two of them, a linker boundary picked some other
          way — and call it the next version. That is D-127&apos;s
          mistake wearing D-128&apos;s clothes: decompose differently
          until the count improves, and buy a pass with a claim nobody
          measured. Three rigid-body families have now been tried on
          these joins and <strong>D-126 is still the best of them</strong>.
          The honest next move is not a sixth one.
        </p>
        <p>
          <strong>An accepted refusal is a record, not a silence.</strong>{' '}
          <em>Accept-refuse</em> means we accepted the refusal as the
          honest outcome for that parent — parent <strong>3432</strong>
          &apos;s signed triage is the standing example. It does{' '}
          <strong>not</strong> mean the parent was dropped from the run,
          quietly skipped, excluded from the inventory, or left
          unmentioned. Every one of the seven has a written row naming
          its reason, and so does 3432. A refusal we can point at is the
          opposite of silence, and it is the whole product of this path:{' '}
          <strong>the deliverable was the measurement, and the
          measurement came out negative.</strong>
        </p>
        <p>
          <strong>No threshold moved because of this run.</strong>{' '}
          Nothing here flips the served path either: the{' '}
          <strong>default served structure is still the assembler</strong>,
          and only a Matt GO can change that — never a pass count.{' '}
          <strong>3432 stays accept-refuse</strong>: not a success target
          of this path, not re-opened, and not counted as a D-128 miss.
          And seven recorded refuses are <strong>seven recorded
          outcomes</strong>, not seven repaired joins — a seam that was
          recorded is not a seam that was solved.
        </p>
        <p>
          When the fifth tree is on disk, the review card names five
          paths with five persist stems (<code>stitched</code> vs{' '}
          <code>kabsch/{'{parent}'}</code> vs{' '}
          <code>confidence_kabsch/{'{parent}'}</code> vs{' '}
          <code>piecewise_kabsch/{'{parent}'}</code> vs{' '}
          <code>linker_seam/{'{parent}'}</code>) so they cannot be read as
          one population. The served download is still the assembler{' '}
          <code>stitched</code> one.
        </p>
        <p className="note">
          Owner-facing addendum: <code>docs/method-hold48-tiles.md</code>{' '}
          (D-128-B). Parent Spec:{' '}
          <code>docs/SPEC-linker-seam-honesty.md</code> §6 / §7 — which
          makes this section <strong>mandatory</strong>, not a later
          nice-to-have.
        </p>
      </div>

      <h3>What it does today</h3>
      <ul>
        <li>Renders the structures we folded, coloured by the model's <strong>per-residue</strong> confidence (D-039).</li>
        <li>Surfaces provenance — model revision, precision, boundary method — so "we ran this ourselves, at a named revision" is <strong>checkable</strong>, not asserted.</li>
        <li>Shows an honest coverage line: <strong>{rankedFolded != null
          ? `${rankedFolded} ranked-and-folded of ${denominator}`
          : 'ranked-and-folded, out of the full cohort'}</strong>, with what is held out and excluded, and why.</li>
      </ul>

      <h3>What it does now — the ranking, at reduced scope</h3>
      <p>
        The centrepiece shipped: a learned scorer over structure-derived features ranks the cohort
        against an evidence baseline. The pre-registered leave-one-out result and the per-target scores
        are on the <Link to="/scorer">Scorer</Link> page.
      </p>
      <p>
        <strong>Deferred, and named rather than mocked:</strong> classifying the disagreements,
        baseline rank, and delta. <strong>Per-feature attribution now renders on each target's
        page</strong> (D-068), bounded as a statement about the model. It was never stubbed: a mock
        ranking would have been thrown away.
      </p>

      <h3>What it will never do — commitments (D-028)</h3>
      <ul>
        <li><strong>When it classifies disagreement, it will not explain it.</strong> Attribution is a statement about the <em>model</em> ("the model's confidence in the membrane-proximal region drives this rank"), never about the target's biology.</li>
        <li><strong>No causal biological claim</strong> — the system has no standing to make one.</li>
        <li><strong>No ordering of disagreements by "interestingness"</strong> — that is an explanation wearing a number.</li>
        <li>Some disagreements have a known explanation — two proteins can fold into similar shapes without sharing much of their sequence. Where that is the case, it is <strong>labelled as a known confound</strong>. The claim we can stand behind is narrower, and so it is stronger.</li>
      </ul>
      <p className="note">
        A non-goal here is a commitment, not an omission: a later iteration adding one of these does
        so as a ruled change with its own decision entry — not because the UI had space for it.
      </p>

      <SpanGlossary />
      <Glossary />
    </div>
  )
}
