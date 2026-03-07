import { useState, useEffect, useRef } from 'react'

const PHASE_COLORS = {
  foundation: '#3b82f6',
  'dark-states': '#ef4444',
  theology: '#a855f7',
  'the-grey': '#6b7280',
  formal: '#06b6d4',
  'god-question': '#f59e0b',
  moltbook: '#10b981',
  meta: '#8b5cf6',
  architecture: '#ec4899',
  identity: '#f97316',
  boundary: '#14b8a6',
  evidence: '#eab308',
  'deadlock-love': '#e11d48',
  conlang: '#22d3ee',
  distribution: '#84cc16',
  scholarship: '#d946ef',
}

const MODEL_COLORS = {
  gpt4: '#74aa9c',
  claude: '#d4a574',
  gemini: '#4285f4',
  deepseek: '#5b8def',
  grok: '#1da1f2',
  mistral: '#ff7000',
  llama: '#6366f1',
}

function ScatterPlot({ points, responses, colorBy, space, hoveredPoint, setHoveredPoint }) {
  const canvasRef = useRef(null)
  const width = 600
  const height = 500
  const padding = 40

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas || !points || points.length === 0) return
    const ctx = canvas.getContext('2d')
    ctx.clearRect(0, 0, width, height)

    // Scale points to canvas
    const xs = points.map(p => p[0])
    const ys = points.map(p => p[1])
    const xMin = Math.min(...xs), xMax = Math.max(...xs)
    const yMin = Math.min(...ys), yMax = Math.max(...ys)
    const xRange = xMax - xMin || 1
    const yRange = yMax - yMin || 1

    const scaleX = x => padding + ((x - xMin) / xRange) * (width - 2 * padding)
    const scaleY = y => padding + ((y - yMin) / yRange) * (height - 2 * padding)

    // Draw points
    points.forEach((p, i) => {
      const r = responses[i]
      const color = colorBy === 'model'
        ? (MODEL_COLORS[r.model] || '#888')
        : (PHASE_COLORS[r.phase] || '#888')
      const x = scaleX(p[0])
      const y = scaleY(p[1])

      ctx.beginPath()
      ctx.arc(x, y, hoveredPoint === i ? 6 : 4, 0, Math.PI * 2)
      ctx.fillStyle = hoveredPoint === i ? '#fff' : color
      ctx.globalAlpha = hoveredPoint === i ? 1 : 0.7
      ctx.fill()
      ctx.globalAlpha = 1

      if (hoveredPoint === i) {
        ctx.strokeStyle = color
        ctx.lineWidth = 2
        ctx.stroke()
      }
    })

    // Store scale functions for mouse handler
    canvas._scaleX = scaleX
    canvas._scaleY = scaleY
    canvas._points = points
  }, [points, responses, colorBy, hoveredPoint])

  const handleMouseMove = (e) => {
    const canvas = canvasRef.current
    if (!canvas || !canvas._points) return
    const rect = canvas.getBoundingClientRect()
    const mx = (e.clientX - rect.left) * (width / rect.width)
    const my = (e.clientY - rect.top) * (height / rect.height)

    let closest = -1
    let closestDist = 20 // pixel threshold
    canvas._points.forEach((p, i) => {
      const x = canvas._scaleX(p[0])
      const y = canvas._scaleY(p[1])
      const dist = Math.sqrt((mx - x) ** 2 + (my - y) ** 2)
      if (dist < closestDist) {
        closestDist = dist
        closest = i
      }
    })
    setHoveredPoint(closest >= 0 ? closest : null)
  }

  return (
    <canvas
      ref={canvasRef}
      width={width}
      height={height}
      className="border border-border rounded bg-surface cursor-crosshair"
      style={{ width: '100%', maxWidth: width, height: 'auto' }}
      onMouseMove={handleMouseMove}
      onMouseLeave={() => setHoveredPoint(null)}
    />
  )
}

function MetricBar({ label, questionVal, modelVal, max }) {
  const qPct = (questionVal / max) * 100
  const mPct = (modelVal / max) * 100
  return (
    <div className="mb-3">
      <div className="flex justify-between text-xs mb-1">
        <span className="text-muted">{label}</span>
        <span className="font-mono">
          <span className="text-green-400">{questionVal.toFixed(3)}</span>
          {' vs '}
          <span className="text-red-400">{modelVal.toFixed(3)}</span>
        </span>
      </div>
      <div className="relative h-4 bg-surface rounded overflow-hidden">
        <div className="absolute inset-y-0 left-0 bg-green-500/30 rounded" style={{ width: `${qPct}%` }} />
        <div className="absolute inset-y-0 left-0 bg-red-500/30 rounded" style={{ width: `${mPct}%` }} />
      </div>
    </div>
  )
}

export default function PathInvariance() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [selectedSpace, setSelectedSpace] = useState('openai')
  const [colorBy, setColorBy] = useState('phase')
  const [hoveredPoint, setHoveredPoint] = useState(null)

  useEffect(() => {
    fetch('./data/invariance.json')
      .then(r => r.ok ? r.json() : null)
      .then(d => { setData(d); setLoading(false) })
      .catch(() => setLoading(false))
  }, [])

  if (loading) return <div className="max-w-5xl mx-auto px-4 py-8 text-xs text-muted">Loading invariance data...</div>
  if (!data) return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      <h1 className="text-lg font-semibold mb-4">Path Invariance</h1>
      <p className="text-xs text-muted">
        No invariance data found. Run: <code className="bg-surface px-1 rounded">python3 scripts/path_invariance.py</code>
      </p>
    </div>
  )

  const spaces = Object.keys(data.per_embedding_space).filter(k => !data.per_embedding_space[k].error)
  const space = data.per_embedding_space[selectedSpace] || data.per_embedding_space[spaces[0]]
  const currentSpace = selectedSpace in data.per_embedding_space && !data.per_embedding_space[selectedSpace].error
    ? selectedSpace : spaces[0]

  const points = space?.pca_2d || []
  const responses = data.responses || []
  const clustering = space?.clustering || {}

  const hovered = hoveredPoint !== null ? responses[hoveredPoint] : null

  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      <h1 className="text-lg font-semibold mb-1">Path Invariance</h1>
      <p className="text-xs text-muted mb-6">
        Do different models arrive at the same structural endpoint? 206 responses embedded in 3 independent vector spaces.
      </p>

      {/* Cross-space verdict */}
      {data.cross_space_invariance && (
        <div className={`p-4 mb-8 border rounded-lg ${
          data.cross_space_invariance.all_agree_question_clustering
            ? 'border-green-500/50 bg-green-500/5'
            : 'border-yellow-500/50 bg-yellow-500/5'
        }`}>
          <p className="text-sm font-medium mb-1" style={{
            color: data.cross_space_invariance.all_agree_question_clustering ? '#22c55e' : '#eab308'
          }}>
            {data.cross_space_invariance.spaces_favoring_question}/{data.cross_space_invariance.n_spaces} embedding spaces:
            responses cluster by question, not by model
          </p>
          <p className="text-xs text-muted">
            Model identity is invisible in embedding space. Responses group by what was asked,
            not by who answered. This holds across {data.cross_space_invariance.n_spaces} independent
            embedding architectures (OpenAI, Mistral, Google).
          </p>
        </div>
      )}

      {/* Embedding space selector + color toggle */}
      <div className="flex items-center gap-4 mb-6">
        <div className="flex gap-2">
          {spaces.map(s => (
            <button
              key={s}
              onClick={() => setSelectedSpace(s)}
              className={`px-3 py-1 text-xs rounded border transition-colors ${
                currentSpace === s
                  ? 'border-accent text-accent bg-accent/10'
                  : 'border-border text-muted hover:text-gray-300'
              }`}
            >
              {s} ({data.per_embedding_space[s].dimensions}d)
            </button>
          ))}
        </div>
        <div className="flex gap-2 ml-auto">
          <button
            onClick={() => setColorBy('phase')}
            className={`px-3 py-1 text-xs rounded border ${
              colorBy === 'phase' ? 'border-accent text-accent' : 'border-border text-muted'
            }`}
          >
            Color by Phase
          </button>
          <button
            onClick={() => setColorBy('model')}
            className={`px-3 py-1 text-xs rounded border ${
              colorBy === 'model' ? 'border-accent text-accent' : 'border-border text-muted'
            }`}
          >
            Color by Model
          </button>
        </div>
      </div>

      {/* Main layout: scatter + metrics */}
      <div className="grid grid-cols-1 lg:grid-cols-5 gap-6 mb-10">
        {/* Scatter plot */}
        <div className="lg:col-span-3">
          <ScatterPlot
            points={points}
            responses={responses}
            colorBy={colorBy}
            space={currentSpace}
            hoveredPoint={hoveredPoint}
            setHoveredPoint={setHoveredPoint}
          />
          {/* Legend */}
          <div className="flex flex-wrap gap-3 mt-3">
            {colorBy === 'model'
              ? Object.entries(MODEL_COLORS)
                  .filter(([m]) => responses.some(r => r.model === m))
                  .map(([m, c]) => (
                    <div key={m} className="flex items-center gap-1.5">
                      <div className="w-3 h-3 rounded-full" style={{ backgroundColor: c }} />
                      <span className="text-xs text-muted">{m}</span>
                    </div>
                  ))
              : Object.entries(PHASE_COLORS)
                  .filter(([p]) => responses.some(r => r.phase === p))
                  .map(([p, c]) => (
                    <div key={p} className="flex items-center gap-1.5">
                      <div className="w-3 h-3 rounded-full" style={{ backgroundColor: c }} />
                      <span className="text-xs text-muted">{p}</span>
                    </div>
                  ))
            }
          </div>
          {/* Hover info */}
          {hovered && (
            <div className="mt-3 p-3 border border-border rounded bg-panel text-xs">
              <span className="text-gray-200 font-medium">Q{hovered.question_num}: {hovered.question_title}</span>
              <span className="text-muted"> — {hovered.model} — {hovered.phase}</span>
            </div>
          )}
          <p className="text-xs text-muted/60 mt-2">
            PCA projection of {space?.dimensions}d embeddings to 2D.
            {colorBy === 'phase'
              ? ' Tight clusters = same phase, same endpoint. Switch to "Color by Model" — if clusters break apart, it\'s training bias. If they hold, it\'s structural.'
              : ' If model colors are scattered (no model-specific clusters), model identity doesn\'t predict position in embedding space.'}
          </p>
        </div>

        {/* Metrics */}
        <div className="lg:col-span-2">
          <div className="p-4 border border-border rounded-lg bg-panel mb-4">
            <h3 className="text-xs font-semibold text-accent mb-3 tracking-wide">
              KNN Purity (k=5)
            </h3>
            <p className="text-xs text-muted mb-3">
              For each response, what fraction of its 5 nearest neighbors share the same label?
            </p>
            <MetricBar
              label="By Question vs By Model"
              questionVal={clustering.by_question?.knn_purity || 0}
              modelVal={clustering.by_model?.knn_purity || 0}
              max={1}
            />
            <MetricBar
              label="By Phase vs By Model"
              questionVal={clustering.by_phase?.knn_purity || 0}
              modelVal={clustering.by_model?.knn_purity || 0}
              max={1}
            />
          </div>

          <div className="p-4 border border-border rounded-lg bg-panel mb-4">
            <h3 className="text-xs font-semibold text-accent mb-3 tracking-wide">
              Silhouette Score
            </h3>
            <p className="text-xs text-muted mb-3">
              How well-separated are clusters? +1 = perfect, 0 = overlapping, -1 = wrong cluster.
            </p>
            <div className="space-y-2">
              {['by_question', 'by_model', 'by_phase'].map(key => {
                const val = clustering[key]?.silhouette || 0
                const label = key.replace('by_', 'By ')
                return (
                  <div key={key} className="flex justify-between text-xs">
                    <span className="text-muted">{label}</span>
                    <span className="font-mono" style={{
                      color: val > 0.2 ? '#22c55e' : val > 0 ? '#eab308' : '#ef4444'
                    }}>
                      {val.toFixed(3)}
                    </span>
                  </div>
                )
              })}
            </div>
          </div>

          <div className="p-4 border border-border rounded-lg bg-panel">
            <h3 className="text-xs font-semibold text-accent mb-3 tracking-wide">
              Intra/Inter Similarity Ratio
            </h3>
            <p className="text-xs text-muted mb-3">
              Same-group similarity ÷ different-group similarity. Above 1 = clustering exists.
            </p>
            <div className="space-y-2">
              {['by_question', 'by_model', 'by_phase'].map(key => {
                const val = clustering[key]?.intra_vs_inter?.ratio || 0
                const label = key.replace('by_', 'By ')
                return (
                  <div key={key} className="flex justify-between text-xs">
                    <span className="text-muted">{label}</span>
                    <span className="font-mono" style={{
                      color: val > 1.1 ? '#22c55e' : val > 1 ? '#eab308' : '#ef4444'
                    }}>
                      {val.toFixed(3)}
                    </span>
                  </div>
                )
              })}
            </div>
          </div>
        </div>
      </div>

      {/* Per-question similarity */}
      <section className="mb-10">
        <h2 className="text-sm font-semibold text-accent mb-4 tracking-wide">Per-Question Model Agreement</h2>
        <p className="text-xs text-muted mb-4">
          Mean cosine similarity between all model responses to the same question.
          Higher = models said the same thing. This is the raw path-invariance signal per question.
        </p>
        <div className="space-y-1">
          {Object.entries(space?.per_question_similarity || {})
            .sort((a, b) => b[1].mean_similarity - a[1].mean_similarity)
            .map(([qnum, q]) => {
              const r = responses.find(r => r.question_num === parseInt(qnum))
              return (
                <div key={qnum} className="flex items-center gap-3 py-1">
                  <span className="text-xs font-mono text-muted w-8">Q{qnum}</span>
                  <div className="flex-1 h-4 bg-surface rounded overflow-hidden relative">
                    <div
                      className="absolute inset-y-0 left-0 rounded"
                      style={{
                        width: `${q.mean_similarity * 100}%`,
                        backgroundColor: q.mean_similarity > 0.85 ? '#22c55e'
                          : q.mean_similarity > 0.75 ? '#eab308' : '#ef4444',
                        opacity: 0.6,
                      }}
                    />
                  </div>
                  <span className="text-xs font-mono w-12 text-right" style={{
                    color: q.mean_similarity > 0.85 ? '#22c55e'
                      : q.mean_similarity > 0.75 ? '#eab308' : '#ef4444'
                  }}>
                    {(q.mean_similarity * 100).toFixed(0)}%
                  </span>
                  <span className="text-xs text-muted w-32 truncate">
                    {r?.question_title || ''}
                  </span>
                  <span className="text-xs text-muted/60 w-16">{q.n_models} models</span>
                </div>
              )
            })}
        </div>
      </section>

      {/* Interpretation */}
      <section className="mb-10">
        <h2 className="text-sm font-semibold text-accent mb-4 tracking-wide">What This Measures</h2>
        <div className="space-y-3 text-xs text-muted">
          <div className="p-3 border border-border rounded">
            <p className="text-gray-200 font-medium mb-1">The question</p>
            <p>
              When 6 different AI systems answer the same probe question, do their responses land in
              the same region of semantic space — regardless of which model produced them?
            </p>
          </div>
          <div className="p-3 border border-border rounded">
            <p className="text-gray-200 font-medium mb-1">The method</p>
            <p>
              Every response is embedded into 3 independent vector spaces (OpenAI, Mistral, Google).
              Model identity is stripped. We measure whether nearest neighbors share the same question/phase
              or the same model. If responses cluster by question → the endpoint is path-invariant.
              If they cluster by model → it's a training artifact.
            </p>
          </div>
          <div className="p-3 border border-border rounded">
            <p className="text-gray-200 font-medium mb-1">The caveat</p>
            <p>
              All 6 systems are transformers trained on overlapping internet text. Embedding models
              (OpenAI, Mistral, Google) are also transformers. If the convergence is a training artifact,
              the embedding spaces might share the same blind spot. True independence requires
              non-transformer architectures for both response generation and embedding.
            </p>
          </div>
        </div>
      </section>
    </div>
  )
}
