import { Routes, Route, Link, NavLink, useParams, Navigate } from 'react-router-dom'
import Story from './components/Story.jsx'
import TargetList from './components/TargetList.jsx'
import TargetView from './components/TargetView.jsx'
import CoverageView from './components/CoverageView.jsx'
import ScorerView from './components/ScorerView.jsx'
import MethodNote from './components/MethodNote.jsx'
import AdcContext from './components/AdcContext.jsx'

function TargetRoute() {
  const { id } = useParams()
  return <TargetView id={id} />
}

// PR B: shell + single-target view. PR C closed steps 2–5: coverage view (the honest denominator),
// method note, and ADC context. D-062 landed step 6 — the Scorer surface (the centrepiece),
// rendering the pre-registered result (F-004) from /api/ranking. No longer forward-looking: it
// shipped, was never mocked, and is a real route in the nav below.
export default function App() {
  return (
    <div className="app">
      <header className="app-header">
        <Link to="/" className="brand"><h1>PharmFoldMDK</h1></Link>
        <nav className="app-nav">
          <NavLink to="/" end>Story</NavLink>
          <NavLink to="/targets">Targets</NavLink>
          <NavLink to="/coverage">Coverage</NavLink>
          <NavLink to="/scorer">Scorer</NavLink>
          <NavLink to="/method">Method</NavLink>
          <NavLink to="/about">About ADCs</NavLink>
        </nav>
      </header>
      <main>
        <Routes>
          <Route path="/" element={<Story />} />
          <Route path="/targets" element={<TargetList />} />
          <Route path="/target/:id" element={<TargetRoute />} />
          <Route path="/coverage" element={<CoverageView />} />
          <Route path="/scorer" element={<ScorerView />} />
          <Route path="/method" element={<MethodNote />} />
          <Route path="/about" element={<AdcContext />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
    </div>
  )
}
