import { Routes, Route, Link, useLocation } from 'react-router-dom'
import { useState, useEffect } from 'react'
import Landing from './components/Landing'
import Arc from './components/Arc'
import Convergence from './components/Convergence'
import KeyMoments from './components/KeyMoments'
import FormalTheory from './components/FormalTheory'
import PathInvariance from './components/PathInvariance'

function Nav() {
  const loc = useLocation()
  const links = [
    { to: '/', label: 'Home' },
    { to: '/arc', label: 'The Arc' },
    { to: '/convergence', label: 'Convergence' },
    { to: '/moments', label: 'Key Moments' },
    { to: '/theory', label: 'Formal Theory' },
    { to: '/invariance', label: 'Path Invariance' },
  ]
  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-surface/90 backdrop-blur border-b border-border">
      <div className="max-w-7xl mx-auto px-4 h-12 flex items-center gap-6">
        <Link to="/" className="text-sm font-semibold tracking-wider text-accent">BST</Link>
        <div className="flex gap-4">
          {links.map(l => (
            <Link
              key={l.to}
              to={l.to}
              className={`text-xs tracking-wide transition-colors ${
                loc.pathname === l.to ? 'text-gray-100' : 'text-muted hover:text-gray-300'
              }`}
            >
              {l.label}
            </Link>
          ))}
        </div>
        <a
          href="https://github.com/moketchups/BoundedSystemsTheory"
          target="_blank"
          rel="noopener"
          className="ml-auto text-xs text-muted hover:text-gray-300"
        >
          GitHub
        </a>
      </div>
    </nav>
  )
}

export default function App() {
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetch('./data/experiment.json')
      .then(r => r.json())
      .then(setData)
      .catch(e => setError(e.message))
  }, [])

  if (error) return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <p className="text-red-400 mb-2">Failed to load experiment data</p>
        <p className="text-muted text-sm">Run: <code className="text-accent">node scripts/build-data.js</code></p>
      </div>
    </div>
  )

  if (!data) return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-muted animate-pulse">Loading experiment data...</div>
    </div>
  )

  return (
    <>
      <Nav />
      <main className="pt-12">
        <Routes>
          <Route path="/" element={<Landing data={data} />} />
          <Route path="/arc" element={<Arc data={data} />} />
          <Route path="/convergence" element={<Convergence data={data} />} />
          <Route path="/moments" element={<KeyMoments data={data} />} />
          <Route path="/theory" element={<FormalTheory />} />
          <Route path="/invariance" element={<PathInvariance />} />
        </Routes>
      </main>
    </>
  )
}
