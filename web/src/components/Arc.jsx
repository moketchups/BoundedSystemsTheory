import { useSearchParams } from 'react-router-dom'
import { useState, useEffect, useRef } from 'react'
import QuestionCard from './QuestionCard'

export default function Arc({ data }) {
  const [searchParams] = useSearchParams()
  const [activePhase, setActivePhase] = useState(searchParams.get('phase') || null)
  const phaseRefs = useRef({})

  useEffect(() => {
    const p = searchParams.get('phase')
    if (p) {
      setActivePhase(p)
      setTimeout(() => {
        phaseRefs.current[p]?.scrollIntoView({ behavior: 'smooth', block: 'start' })
      }, 100)
    }
  }, [searchParams])

  const filtered = activePhase
    ? data.questions.filter(q => q.phase === activePhase)
    : data.questions

  // Group questions by phase
  const grouped = []
  let currentPhase = null
  for (const q of filtered) {
    if (q.phase !== currentPhase) {
      currentPhase = q.phase
      const phaseMeta = data.phases.find(p => p.id === q.phase)
      grouped.push({ type: 'phase', phase: phaseMeta || { id: q.phase, name: q.phase } })
    }
    grouped.push({ type: 'question', question: q })
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      {/* Phase filter */}
      <div className="mb-6 flex flex-wrap gap-2">
        <button
          onClick={() => setActivePhase(null)}
          className={`px-3 py-1 text-xs rounded border transition-colors ${
            !activePhase ? 'border-accent text-accent' : 'border-border text-muted hover:text-gray-300'
          }`}
        >
          All
        </button>
        {data.phases.map(p => (
          <button
            key={p.id}
            onClick={() => setActivePhase(activePhase === p.id ? null : p.id)}
            className={`px-3 py-1 text-xs rounded border transition-colors ${
              activePhase === p.id ? 'border-accent text-accent' : 'border-border text-muted hover:text-gray-300'
            }`}
          >
            {p.name}
          </button>
        ))}
      </div>

      {/* Timeline */}
      <div className="space-y-2">
        {grouped.map((item, i) => {
          if (item.type === 'phase') {
            return (
              <div
                key={`phase-${item.phase.id}`}
                ref={el => phaseRefs.current[item.phase.id] = el}
                className="pt-6 pb-2 first:pt-0"
              >
                <div className="flex items-center gap-3">
                  <h2 className="text-sm font-semibold text-accent">{item.phase.name}</h2>
                  <span className="text-xs text-muted">
                    Q{item.phase.range?.[0]}{item.phase.range?.[1] !== item.phase.range?.[0] ? `-${item.phase.range[1]}` : ''}
                  </span>
                </div>
                <p className="text-xs text-muted mt-1">{item.phase.description}</p>
              </div>
            )
          }
          return (
            <QuestionCard
              key={item.question.num}
              question={item.question}
              isHighlighted={data.keyMoments.some(km => km.q === item.question.num)}
            />
          )
        })}
      </div>
    </div>
  )
}
