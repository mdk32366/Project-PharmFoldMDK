import { Routes, Route, Link, NavLink, useParams, Navigate } from 'react-router-dom'
import TargetList from './components/TargetList.jsx'
import TargetView from './components/TargetView.jsx'
import CoverageView from './components/CoverageView.jsx'
import MethodNote from './components/MethodNote.jsx'
import AdcContext from './components/AdcContext.jsx'

function TargetRoute() {
  const { id } = useParams()
  return <TargetView id={id} />
}

// PR B: shell + single-target view. PR C closes steps 2–5: coverage view (the honest denominator),
// method note, and ADC context. The ranking table (the centrepiece) is step 6 and waits on the
// scorer — deliberately not mocked.
export default function App() {
  return (
    <div className="app">
      <header className="app-header">
        <Link to="/" className="brand"><h1>PharmFoldMDK</h1></Link>
        <nav className="app-nav">
          <NavLink to="/" end>Targets</NavLink>
          <NavLink to="/coverage">Coverage</NavLink>
          <NavLink to="/method">Method</NavLink>
          <NavLink to="/about">About ADCs</NavLink>
        </nav>
      </header>
      <main>
        <Routes>
          <Route path="/" element={<TargetList />} />
          <Route path="/target/:id" element={<TargetRoute />} />
          <Route path="/coverage" element={<CoverageView />} />
          <Route path="/method" element={<MethodNote />} />
          <Route path="/about" element={<AdcContext />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
    </div>
  )
}
