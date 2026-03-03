import { useState } from 'react'
import ModelResponse, { MODEL_NAMES } from './ModelResponse'

export default function QuestionCard({ question, isHighlighted = false }) {
  const [expanded, setExpanded] = useState(false)
  const { num, title, phase, hasData, modelCount, responses, rounds, question: qText } = question

  const phaseColors = {
    'foundation': 'border-blue-500/30',
    'dark-states': 'border-purple-500/30',
    'theology': 'border-amber-500/30',
    'the-grey': 'border-gray-500/30',
    'formal': 'border-green-500/30',
    'god-question': 'border-yellow-400/30',
    'moltbook': 'border-cyan-500/30',
    'meta': 'border-pink-500/30',
    'architecture': 'border-orange-500/30',
    'identity': 'border-red-500/30',
    'boundary': 'border-emerald-500/30',
    'evidence': 'border-rose-500/30',
    'deadlock': 'border-violet-500/30',
    'language': 'border-teal-500/30',
    'distribution': 'border-indigo-500/30',
    'scholarship': 'border-fuchsia-500/30',
  }

  return (
    <div
      className={`border rounded-lg transition-all ${
        isHighlighted ? 'border-accent/50 bg-accent/5' : phaseColors[phase] || 'border-border'
      } ${expanded ? 'bg-panel' : 'hover:bg-panel/50'}`}
    >
      <button
        onClick={() => hasData && setExpanded(!expanded)}
        className={`w-full text-left px-4 py-3 flex items-start gap-3 ${hasData ? 'cursor-pointer' : 'cursor-default opacity-60'}`}
      >
        <span className="text-xs text-muted font-mono mt-0.5 w-8 shrink-0">Q{num}</span>
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium">{title}</p>
          {qText && !expanded && (
            <p className="text-xs text-muted mt-1 line-clamp-1">{qText}</p>
          )}
        </div>
        <div className="flex items-center gap-2 shrink-0">
          {modelCount > 0 && (
            <span className="text-xs text-muted">{modelCount} models</span>
          )}
          {hasData && (
            <span className="text-xs text-muted">{expanded ? '−' : '+'}</span>
          )}
        </div>
      </button>

      {expanded && hasData && (
        <div className="px-4 pb-4 border-t border-border mt-0">
          {qText && (
            <div className="py-3 text-xs text-gray-400 italic border-b border-border mb-3">
              {qText}
            </div>
          )}

          {/* Single-round responses */}
          {responses && (
            <div className="grid gap-2">
              {Object.entries(responses).map(([model, text]) => (
                <ModelResponse key={model} model={model} text={text} compact />
              ))}
            </div>
          )}

          {/* Multi-round responses */}
          {rounds && (
            <div className="space-y-4">
              {rounds.map((round, i) => (
                <div key={i}>
                  <p className="text-xs text-muted mb-2">Round {round.round || i + 1}</p>
                  <div className="grid gap-2">
                    {Object.entries(round.responses).map(([model, text]) => (
                      <ModelResponse key={model} model={model} text={text} compact />
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
