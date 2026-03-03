import { useState } from 'react'
import { MODEL_COLORS, MODEL_NAMES } from './ModelResponse'

export default function Convergence({ data }) {
  const [selectedQ, setSelectedQ] = useState(null)
  const [phaseFilter, setPhaseFilter] = useState(null)
  const modelKeys = data.meta.modelKeys

  const filtered = phaseFilter
    ? data.questions.filter(q => q.phase === phaseFilter)
    : data.questions

  // Determine convergence status for each question
  function getConvergenceStatus(q) {
    if (!q.hasData) return 'no-data'
    if (q.modelCount >= 5) return 'converge'
    if (q.modelCount >= 3) return 'partial'
    return 'limited'
  }

  function getModelStatus(q, model) {
    if (q.responses?.[model]) return 'responded'
    if (q.rounds) {
      for (const r of q.rounds) {
        if (r.responses[model]) return 'responded'
      }
    }
    return 'absent'
  }

  const statusColors = {
    'responded': 'bg-converge/20 border-converge/40',
    'absent': 'bg-transparent border-border',
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <div className="mb-6">
        <h1 className="text-lg font-semibold mb-2">Convergence Grid</h1>
        <p className="text-xs text-muted">
          Each cell = one model's response to one question. Green = responded. The pattern is the point.
        </p>
      </div>

      {/* Phase filter */}
      <div className="mb-4 flex flex-wrap gap-2">
        <button
          onClick={() => setPhaseFilter(null)}
          className={`px-2 py-1 text-xs rounded border ${
            !phaseFilter ? 'border-accent text-accent' : 'border-border text-muted'
          }`}
        >
          All
        </button>
        {data.phases.map(p => (
          <button
            key={p.id}
            onClick={() => setPhaseFilter(phaseFilter === p.id ? null : p.id)}
            className={`px-2 py-1 text-xs rounded border ${
              phaseFilter === p.id ? 'border-accent text-accent' : 'border-border text-muted'
            }`}
          >
            {p.name}
          </button>
        ))}
      </div>

      {/* Grid */}
      <div className="overflow-x-auto">
        <table className="w-full border-collapse">
          <thead>
            <tr>
              <th className="text-left text-xs text-muted font-normal p-2 w-8">Q</th>
              <th className="text-left text-xs text-muted font-normal p-2 min-w-[200px]">Question</th>
              {modelKeys.map(mk => (
                <th key={mk} className="text-center text-xs font-normal p-2 w-20" style={{ color: MODEL_COLORS[mk] }}>
                  {MODEL_NAMES[mk]}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {filtered.map(q => {
              const isKey = data.keyMoments.some(km => km.q === q.num)
              return (
                <tr
                  key={q.num}
                  onClick={() => setSelectedQ(selectedQ === q.num ? null : q.num)}
                  className={`border-t border-border cursor-pointer transition-colors ${
                    isKey ? 'bg-accent/5' : 'hover:bg-panel/50'
                  } ${selectedQ === q.num ? 'bg-panel' : ''}`}
                >
                  <td className="p-2 text-xs text-muted font-mono">{q.num}</td>
                  <td className="p-2">
                    <p className="text-xs font-medium">{q.title}</p>
                    {isKey && <span className="text-[10px] text-accent">key moment</span>}
                  </td>
                  {modelKeys.map(mk => {
                    const status = getModelStatus(q, mk)
                    return (
                      <td key={mk} className="p-2 text-center">
                        <div className={`w-6 h-6 mx-auto rounded border ${statusColors[status]}`} />
                      </td>
                    )
                  })}
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>

      {/* Selected question detail */}
      {selectedQ && (() => {
        const q = data.questions.find(q => q.num === selectedQ)
        if (!q) return null
        return (
          <div className="mt-6 p-4 border border-border rounded-lg bg-panel">
            <h3 className="text-sm font-medium mb-2">Q{q.num}: {q.title}</h3>
            {q.question && <p className="text-xs text-muted italic mb-3">{q.question}</p>}
            {q.responses && (
              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-3">
                {Object.entries(q.responses).map(([model, text]) => (
                  <div key={model} className="border border-border rounded p-2">
                    <p className="text-xs font-medium mb-1" style={{ color: MODEL_COLORS[model] }}>
                      {MODEL_NAMES[model]}
                    </p>
                    <p className="text-xs text-gray-400 line-clamp-6">{text}</p>
                  </div>
                ))}
              </div>
            )}
            {q.rounds && (
              <p className="text-xs text-muted">{q.rounds.length} rounds of multi-model discussion</p>
            )}
          </div>
        )
      })()}

      {/* Legend */}
      <div className="mt-8 flex gap-6 text-xs text-muted">
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded border bg-converge/20 border-converge/40" />
          <span>Responded</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded border border-border" />
          <span>No data</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded border border-accent/40 bg-accent/10" />
          <span>Key moment</span>
        </div>
      </div>
    </div>
  )
}
