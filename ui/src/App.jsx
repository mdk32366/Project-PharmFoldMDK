import { Routes, Route, Link, useParams, Navigate } from 'react-router-dom'
import TargetList from './components/TargetList.jsx'
import TargetView from './components/TargetView.jsx'

function TargetRoute() {
  const { id } = useParams()
  return <TargetView id={id} />
}

// PR B: the shell + single-target experience. The ranking table (the demo's centrepiece) is step 6
// and waits on the scorer — deliberately not mocked. The coverage view is PR C.
export default function App() {
  return (
    <div className="app">
      <header className="app-header">
        <Link to="/" className="brand"><h1>PharmFoldMDK</h1></Link>
        <span className="tagline">ADC target exploration — structures we folded ourselves</span>
      </header>
      <main>
        <Routes>
          <Route path="/" element={<TargetList />} />
          <Route path="/target/:id" element={<TargetRoute />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
    </div>
  )
}
