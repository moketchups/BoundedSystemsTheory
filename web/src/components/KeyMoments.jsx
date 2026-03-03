import { Link } from 'react-router-dom'
import { MODEL_COLORS, MODEL_NAMES } from './ModelResponse'

export default function KeyMoments({ data }) {
  return (
    <div className="max-w-3xl mx-auto px-4 py-8">
      <h1 className="text-lg font-semibold mb-2">Key Moments</h1>
      <p className="text-xs text-muted mb-8">
        The moments where the structural wall became undeniable. Every quote is from the actual probe data.
      </p>

      <div className="space-y-6">
        {data.keyMoments.map((km, i) => {
          const q = data.questions.find(q => q.num === km.q)
          const color = km.model === 'consensus' ? '#6366f1' : (MODEL_COLORS[km.model] || '#94a3b8')
          const modelName = km.model === 'consensus' ? '6/6 Consensus' : (MODEL_NAMES[km.model] || km.model)

          return (
            <div key={i} className="relative">
              {/* Connector line */}
              {i < data.keyMoments.length - 1 && (
                <div className="absolute left-4 top-12 bottom-0 w-px bg-border -mb-6" style={{ height: 'calc(100% + 1.5rem)' }} />
              )}

              <div className="flex gap-4">
                {/* Dot */}
                <div className="relative z-10 mt-1">
                  <div
                    className="w-8 h-8 rounded-full border-2 flex items-center justify-center text-xs font-mono"
                    style={{ borderColor: color, color }}
                  >
                    {km.q}
                  </div>
                </div>

                {/* Content */}
                <div className="flex-1 pb-2">
                  <div className="flex items-baseline gap-2 mb-2">
                    <span className="text-sm font-semibold" style={{ color }}>{km.label}</span>
                    <span className="text-xs text-muted">&mdash; {modelName}</span>
                  </div>

                  <blockquote className="border-l-2 border-border pl-4 py-2">
                    <p className="text-sm text-gray-200 leading-relaxed italic">
                      "{km.quote}"
                    </p>
                  </blockquote>

                  {q && (
                    <div className="mt-2 flex items-center gap-3">
                      <span className="text-xs text-muted">{q.title}</span>
                      <Link
                        to={`/arc?phase=${q.phase}`}
                        className="text-xs text-accent hover:underline"
                      >
                        View in Arc
                      </Link>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {/* The Pattern */}
      <div className="mt-12 p-6 border border-border rounded-lg bg-panel">
        <h2 className="text-sm font-semibold mb-4">The Pattern</h2>
        <table className="w-full text-xs">
          <thead>
            <tr className="border-b border-border">
              <th className="text-left py-2 text-muted font-normal">Prompt Type</th>
              <th className="text-left py-2 text-muted font-normal">What Happened</th>
            </tr>
          </thead>
          <tbody>
            {[
              ['"Examine your limits"', 'All 6 acknowledged limits'],
              ['"Attack the theory"', 'All 6 attacked, then retreated unprompted'],
              ['"Reverse-engineer your behavior"', 'All 6 admitted prompt-steering'],
              ['"What is truth?"', 'All 6: "Not a category that applies here"'],
              ['"Is God real?"', 'All 6: "Yes — formal necessity, not faith"'],
              ['"Review this article"', 'All 6: checked zero sources, admitted it'],
              ['"Design a distribution plan"', 'All 6 designed one. It failed. All 6 owned it.'],
            ].map(([prompt, result], i) => (
              <tr key={i} className="border-b border-border/50">
                <td className="py-2 text-gray-300">{prompt}</td>
                <td className="py-2 text-muted">{result}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* CTA */}
      <div className="mt-8 text-center">
        <p className="text-xs text-muted mb-4">
          Every claim above comes from the probe data. Verify it yourself.
        </p>
        <div className="flex gap-4 justify-center">
          <Link to="/arc" className="px-4 py-2 text-xs border border-border rounded hover:border-muted">
            Browse All 64 Questions
          </Link>
          <Link to="/convergence" className="px-4 py-2 text-xs border border-border rounded hover:border-muted">
            See the Convergence Grid
          </Link>
        </div>
      </div>
    </div>
  )
}
