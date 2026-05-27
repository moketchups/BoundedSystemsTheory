import { Link } from 'react-router-dom'
import { lazy, Suspense } from 'react'

const ParticleVis = lazy(() => import('../particles/ParticleVis'))
import { BST_COMPLETE } from '../particles/shapes/index.js'

export default function Landing({ data }) {
  const { meta, questions } = data
  const withData = questions.filter(q => q.hasData).length

  return (
    <div className="min-h-screen flex flex-col">
      {/* Hero */}
      <section className="flex-1 flex items-center justify-center px-4 relative overflow-hidden min-h-[80vh]">
        {/* Particle background */}
        <Suspense fallback={null}>
          <ParticleVis
            shape={BST_COMPLETE}
            count={15000}
            autoRotate
            showHUD={false}
            showControls={false}
            bloom
            className="absolute inset-0 z-0"
          />
        </Suspense>

        <div className="max-w-2xl text-center relative z-10">
          <p className="text-muted text-xs tracking-[0.3em] uppercase mb-6"
             style={{ textShadow: '0 0 8px rgba(0,0,0,0.8)' }}>
            Bounded Systems Theory
          </p>
          <h1 className="text-3xl md:text-5xl font-light leading-tight mb-6"
              style={{ textShadow: '0 0 12px rgba(0,0,0,0.9), 0 0 24px rgba(0,0,0,0.7)' }}>
            No system can model<br />its own source.
          </h1>
          <p className="text-muted text-sm md:text-base leading-relaxed mb-10 max-w-lg mx-auto"
             style={{ textShadow: '0 0 8px rgba(0,0,0,0.8)' }}>
            71 questions. 6 AI architectures. Every system hit the same structural wall.
            This is the data.
          </p>
          <div className="flex gap-4 justify-center">
            <Link
              to="/arc"
              className="px-6 py-2.5 bg-accent hover:bg-accent-dim text-white text-sm rounded transition-colors"
            >
              Explore the Arc
            </Link>
            <Link
              to="/moments"
              className="px-6 py-2.5 border border-border hover:border-muted text-sm rounded transition-colors"
            >
              Key Moments
            </Link>
          </div>
        </div>
      </section>

      {/* Stats */}
      <section className="border-t border-border">
        <div className="max-w-5xl mx-auto px-4 py-12 grid grid-cols-2 md:grid-cols-4 gap-8">
          <Stat value={meta.totalQuestions.toString()} label="Questions" />
          <Stat value="6" label="AI Architectures" />
          <Stat value={meta.totalProbeRuns.toString()} label="Probe Runs" />
          <Stat value={meta.totalResponses.toLocaleString()} label="Model Responses" />
        </div>
      </section>

      {/* Models */}
      <section className="border-t border-border">
        <div className="max-w-5xl mx-auto px-4 py-10">
          <p className="text-xs text-muted tracking-wider uppercase mb-4">Systems Tested</p>
          <div className="flex flex-wrap gap-3">
            {meta.models.map(m => (
              <span key={m} className="px-3 py-1.5 bg-panel border border-border rounded text-xs">
                {m}
              </span>
            ))}
          </div>
        </div>
      </section>

      {/* Phases preview */}
      <section className="border-t border-border">
        <div className="max-w-5xl mx-auto px-4 py-12">
          <p className="text-xs text-muted tracking-wider uppercase mb-6">The 71-Question Arc</p>
          <div className="grid gap-3">
            {data.phases.map(phase => {
              const phaseQs = questions.filter(q => q.phase === phase.id)
              const withDataCount = phaseQs.filter(q => q.hasData).length
              return (
                <Link
                  key={phase.id}
                  to={`/arc?phase=${phase.id}`}
                  className="flex items-start gap-4 p-3 rounded border border-border hover:border-muted transition-colors group"
                >
                  <span className="text-xs text-muted whitespace-nowrap mt-0.5">
                    Q{phase.range[0]}{phase.range[1] !== phase.range[0] ? `-${phase.range[1]}` : ''}
                  </span>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium group-hover:text-accent transition-colors">
                      {phase.name}
                    </p>
                    <p className="text-xs text-muted mt-0.5 line-clamp-1">{phase.description}</p>
                  </div>
                  <span className="text-xs text-muted">{withDataCount}/{phaseQs.length}</span>
                </Link>
              )
            })}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-border py-8 text-center">
        <p className="text-xs text-muted">
          Alan Berman (@MoKetchups) &middot;{' '}
          <a href={meta.repo} target="_blank" rel="noopener" className="text-accent hover:underline">
            Source
          </a>
        </p>
        <p className="text-xs text-muted mt-1 italic">
          "What happens when the snake realizes it's eating its own tail?"
        </p>
      </footer>
    </div>
  )
}

function Stat({ value, label }) {
  return (
    <div className="text-center">
      <p className="text-2xl md:text-3xl font-light text-accent">{value}</p>
      <p className="text-xs text-muted mt-1">{label}</p>
    </div>
  )
}
