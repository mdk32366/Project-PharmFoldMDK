import { Routes, Route, Link, NavLink, useLocation, useParams, Navigate } from 'react-router-dom'
import Story from './components/Story.jsx'
import TargetList from './components/TargetList.jsx'
import TargetView from './components/TargetView.jsx'
import CensusView from './components/CensusView.jsx'
import CensusProteinView from './components/CensusProteinView.jsx'
import ScorerView from './components/ScorerView.jsx'
import MethodNote from './components/MethodNote.jsx'
import AdcContext from './components/AdcContext.jsx'
import AdcsView from './components/AdcsView.jsx'
import AdcCard from './components/AdcCard.jsx'
import AdcPipelineCard from './components/AdcPipelineCard.jsx'
import CancerBurdenView from './components/CancerBurdenView.jsx'

function TargetRoute() {
  const { id } = useParams()
  return <TargetView id={id} />
}

function CensusProteinRoute() {
  const { id } = useParams()
  return <CensusProteinView id={id} />
}

function AdcCardRoute() {
  const { id } = useParams()
  return <AdcCard id={id} />
}

function AdcPipelineCardRoute() {
  const { id } = useParams()
  return <AdcPipelineCard id={id} />
}

// PR B: shell + single-target view. PR C closed steps 2–5: coverage view (the honest denominator),
// method note, and ADC context. D-062 landed step 6 — the Scorer surface (the centrepiece),
// rendering the pre-registered result (F-004) from /api/ranking. No longer forward-looking: it
// shipped, was never mocked, and is a real route in the nav below.
// D-122 landed ADC-B — `/adcs` + `/adcs/:id` consume the D-119 catalog. Nav: ADCs.
// D-124 / ADC-C-B adds a Pipeline shelf on `/adcs` and `/adcs/pipeline/:id`
// (declared before `:id` so the literal is not captured as an approved id).
// D-149 adds `/cancer-burden` — a DEDICATED disease-level surface (US cancer deaths and new
// cases from SEER official aggregates). It is its own nav landmark on purpose: it must not be
// buried in Method and must not appear on Census or Scorer, where a burden figure would read as
// an input to a score. It joins to no protein, accession, score or rank.
// ⚠⚠ D-151 — ONE SURFACE IS A TABLE AND THE REST ARE PROSE, AND `main` USED TO TREAT THEM ALIKE.
// `main { max-width: 60rem }` is the right measure for a paragraph and the wrong one for an
// thirteen-column census: it left a wide empty gutter down both sides of the page while the table
// itself was squeezed to about 57rem and then scrolled off the right edge. The owner's words,
// 2026-09-09: *"we are not using the entire left side of the table real estate and the list scrolls
// off the right side."*
// ⚠ The wide measure is granted BY ROUTE, not by a component reaching up and restyling its own
// container. A `<main>` whose width depends on which page is inside it is a decision about the
// shell, so it is made in the shell — and it is one class, so a test can assert it structurally
// rather than trying to measure a layout jsdom does not compute.
// ⚠ EXACTLY `/census`. `/census/:id` is a protein CARD — prose, one column, and it keeps the
// reading measure. A `startsWith` here would have widened it too, which is the opposite of what a
// card needs.
//
// ⚠⚠ D-152 — THE OTHER FIVE LISTS JOIN IT, AND THE SET IS STILL A SET OF EXACT PATHS. The owner's
// ask was to apply the census treatment to the rest of the surfaces; `main { max-width: 60rem }` is
// a reading measure, and it was cropping `/targets` (eight columns, two of them holding sentences),
// `/coverage` (a Note column of prose), `/scorer` (a two-column layout squeezed into one measure),
// `/cancer-burden` (seven columns, three of them long labels) and `/adcs` (five columns on the
// Pipeline shelf) in exactly the way it was cropping the census.
// ⚠⚠ D-155 — THE OWNER OVERRULED THE READING-MEASURE ARGUMENT, AND D-152 DECISION 2 IS SUPERSEDED
// IN PART. That decision held `/`, `/method` and `/about` out of this set on the reasoning that
// *"60rem is the right measure for a paragraph and widening them would make them harder to read"*
// — the sentence directly above this one until this entry. Owner, 2026-09-10, after seeing all
// three live beside the widened lists: *"The Story, Method, and About ADCs surfaces should match
// the wider format of the other surfaces."* ⚠ The original reasoning is kept in the log rather
// than edited away (D-129-C): it was a defensible argument about typography and it lost to the
// owner's judgement about a site that now reads as two different sites. `/method` is the clearest
// case — its D-138 contents rail is a second column, and a two-column layout inside a one-column
// measure is what D-152 itself called out on `/scorer`.
// ⚠ MEMBERSHIP IS STILL A JUDGEMENT ABOUT THE ROUTE, and every CARD is still deliberately out.
// `/target/:id`, `/census/:id`, `/adcs/:id` and `/adcs/pipeline/:id` keep the reading measure —
// a card is one object's story and gains nothing from 96rem.
// ⚠ And every entry is still a LITERAL rather than a `startsWith`, for that same reason.
// ⚠⚠ `/coverage` LEFT THIS SET BY LEAVING THE ROUTER (D-155). Its content is the honest-denominator
// panel, the disposition/fold facts and the census strip, and all of it now renders on `/targets`
// over the same 82 rows — see the entry for why one population had two tables.
const WIDE_ROUTES = new Set([
  '/', '/targets', '/census', '/scorer', '/cancer-burden', '/adcs', '/method', '/about',
])

export default function App() {
  const { pathname } = useLocation()
  const wide = WIDE_ROUTES.has(pathname)
  return (
    <div className="app">
      <header className="app-header">
        <Link to="/" className="brand"><h1>PharmFoldMDK</h1></Link>
        {/* ⚠ D-135: LABELLED, because the page can now hold two navigation landmarks — the Story
            grew a beat contents of its own. Two unnamed `nav` regions are indistinguishable to a
            screen reader, and the site nav is the one that is a contract. */}
        <nav className="app-nav" aria-label="Site">
          <NavLink to="/" end>Story</NavLink>
          {/* ⚠ D-151 (owner ruling 2026-09-09): the LABEL is "Initial Targets" and the PATH stays
              `/targets`. The word "Targets" alone read as *the* targets of this project while the
              census holds 3,467 more, and the cohort-82 is the STARTING list — the comparator
              D-051/F-009 already describe in prose. ⚠ Renaming the route as well would break every
              deep link the Story CTA, the census card and every shared address already point at,
              which is a cost the label does not need to pay. */}
          <NavLink to="/targets">Initial Targets</NavLink>
          <NavLink to="/census">Census</NavLink>
          <NavLink to="/scorer">Scorer</NavLink>
          {/* ⚠⚠ D-149: ITS OWN TOP-LEVEL LANDMARK, not a panel on Method and not a column on
              Census. A burden figure on a scoring surface is one glance from being read as an
              input to the score — the "cancer ×" composite refused by D-143/D-144/D-146. */}
          <NavLink to="/cancer-burden">Cancer burden</NavLink>
          <NavLink to="/method">Method</NavLink>
          <NavLink to="/adcs">ADCs</NavLink>
          <NavLink to="/about">About ADCs</NavLink>
        </nav>
      </header>
      <main className={wide ? 'wide' : undefined}>
        <Routes>
          <Route path="/" element={<Story />} />
          <Route path="/targets" element={<TargetList />} />
          <Route path="/target/:id" element={<TargetRoute />} />
          <Route path="/census" element={<CensusView />} />
          <Route path="/census/:id" element={<CensusProteinRoute />} />
          <Route path="/scorer" element={<ScorerView />} />
          <Route path="/cancer-burden" element={<CancerBurdenView />} />
          <Route path="/method" element={<MethodNote />} />
          <Route path="/adcs" element={<AdcsView />} />
          <Route path="/adcs/pipeline/:id" element={<AdcPipelineCardRoute />} />
          <Route path="/adcs/:id" element={<AdcCardRoute />} />
          <Route path="/about" element={<AdcContext />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
    </div>
  )
}
