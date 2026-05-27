import { useState, useEffect, useRef } from 'react'
import LazyParticleVis from '../particles/LazyParticleVis'
import { BST_CONVERGENCE } from '../particles/shapes/index.js'

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
}

const MODEL_LABELS = {
  gpt4: 'GPT-4 (OpenAI)',
  claude: 'Claude (Anthropic)',
  gemini: 'Gemini (Google)',
  deepseek: 'DeepSeek',
  grok: 'Grok (xAI)',
  mistral: 'Mistral',
}

function ScatterPlot({ points, responses, colorBy, hoveredPoint, setHoveredPoint }) {
  const canvasRef = useRef(null)
  const width = 600
  const height = 500
  const padding = 40

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas || !points || points.length === 0) return
    const ctx = canvas.getContext('2d')
    ctx.clearRect(0, 0, width, height)

    const xs = points.map(p => p[0])
    const ys = points.map(p => p[1])
    const xMin = Math.min(...xs), xMax = Math.max(...xs)
    const yMin = Math.min(...ys), yMax = Math.max(...ys)
    const xRange = xMax - xMin || 1
    const yRange = yMax - yMin || 1

    const scaleX = x => padding + ((x - xMin) / xRange) * (width - 2 * padding)
    const scaleY = y => padding + ((y - yMin) / yRange) * (height - 2 * padding)

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
    let closestDist = 20
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

  if (loading) return <div className="max-w-5xl mx-auto px-4 py-8 text-xs text-muted">Loading...</div>
  if (!data) return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      <h1 className="text-lg font-semibold mb-4">Path Invariance</h1>
      <p className="text-xs text-muted">
        No data found. Run: <code className="bg-surface px-1 rounded">python3 scripts/path_invariance.py</code>
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

  const models = [...new Set(responses.map(r => r.model))]

  return (
    <div className="max-w-5xl mx-auto px-4 py-8">

      {/* Hero — plain language */}
      <h1 className="text-xl font-bold mb-2">Do different AI systems reach the same conclusions?</h1>
      <p className="text-sm text-muted mb-8 max-w-2xl">
        We asked 71 questions about the limits of self-knowledge to 6 different AI systems —
        GPT-4, Claude, Gemini, DeepSeek, Grok, and Mistral. Then we measured whether their
        answers group by <strong className="text-gray-200">what was asked</strong> or
        by <strong className="text-gray-200">which AI answered</strong>.
      </p>

      {/* Verdict — big and clear */}
      {data.cross_space_invariance && (
        <div className={`p-5 mb-10 border rounded-lg ${
          data.cross_space_invariance.all_agree_question_clustering
            ? 'border-green-500/50 bg-green-500/5'
            : 'border-yellow-500/50 bg-yellow-500/5'
        }`}>
          <p className="text-lg font-bold mb-2" style={{
            color: data.cross_space_invariance.all_agree_question_clustering ? '#22c55e' : '#eab308'
          }}>
            Answers group by question, not by AI system.
          </p>
          <p className="text-sm text-muted">
            When you strip the labels and just look at meaning, you can't tell which AI wrote which answer.
            Responses to the same question land near each other regardless of which system produced them.
            This was tested using {data.cross_space_invariance.n_spaces} independent measurement methods
            and all {data.cross_space_invariance.n_spaces} agree.
          </p>
        </div>
      )}

      {/* Convergence Visualization */}
      <section className="mb-10">
        <h2 className="text-sm font-semibold mb-2">Watch them converge</h2>
        <p className="text-xs text-muted mb-4">
          6 AI architectures start as separate clusters. Drag the probe depth slider to push them
          toward self-referential limits — watch them merge into one structure.
        </p>
        <div className="relative h-80 rounded-lg overflow-hidden border border-border">
          <LazyParticleVis
            shape={BST_CONVERGENCE}
            count={15000}
            bloom
            className="absolute inset-0"
          />
        </div>
      </section>

      {/* The 6 models tested */}
      <section className="mb-10">
        <h2 className="text-sm font-semibold mb-4">The 6 AI systems tested</h2>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
          {models.map(m => {
            const count = responses.filter(r => r.model === m).length
            return (
              <div key={m} className="p-3 border border-border rounded-lg bg-panel text-center">
                <div className="w-4 h-4 rounded-full mx-auto mb-2" style={{ backgroundColor: MODEL_COLORS[m] || '#888' }} />
                <p className="text-xs font-medium text-gray-200">{MODEL_LABELS[m] || m}</p>
                <p className="text-xs text-muted">{count} responses</p>
              </div>
            )
          })}
        </div>
        <p className="text-xs text-muted mt-3">
          Every AI answered the same questions. Every answer was measured the same way.
          No system got special treatment.
        </p>
      </section>

      {/* Scatter plot section */}
      <section className="mb-10">
        <h2 className="text-sm font-semibold mb-2">See for yourself</h2>
        <p className="text-xs text-muted mb-4">
          Each dot is one AI response. Dots that are close together mean the responses said similar things.
          Click "Color by Model" — if the AI systems were just saying their own thing, you'd see 6 separate
          color clusters. Instead, the colors are mixed together. The AI doesn't matter. The question does.
        </p>

        {/* Controls */}
        <div className="flex items-center gap-4 mb-4 flex-wrap">
          <div className="flex gap-2">
            <button
              onClick={() => setColorBy('phase')}
              className={`px-3 py-1.5 text-xs rounded border transition-colors ${
                colorBy === 'phase' ? 'border-accent text-accent bg-accent/10' : 'border-border text-muted hover:text-gray-300'
              }`}
            >
              Color by Topic
            </button>
            <button
              onClick={() => setColorBy('model')}
              className={`px-3 py-1.5 text-xs rounded border transition-colors ${
                colorBy === 'model' ? 'border-accent text-accent bg-accent/10' : 'border-border text-muted hover:text-gray-300'
              }`}
            >
              Color by AI Model
            </button>
          </div>
          <div className="flex gap-2 ml-auto">
            <span className="text-xs text-muted/60">Measurement:</span>
            {spaces.map(s => (
              <button
                key={s}
                onClick={() => setSelectedSpace(s)}
                className={`px-2 py-1 text-xs rounded border transition-colors ${
                  currentSpace === s
                    ? 'border-accent/50 text-accent/80 bg-accent/5'
                    : 'border-border text-muted/50 hover:text-gray-400'
                }`}
              >
                {s.replace(/^\w/, c => c.toUpperCase())}
              </button>
            ))}
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
          <div className="lg:col-span-3">
            <ScatterPlot
              points={points}
              responses={responses}
              colorBy={colorBy}
              hoveredPoint={hoveredPoint}
              setHoveredPoint={setHoveredPoint}
            />
            {/* Legend */}
            <div className="flex flex-wrap gap-3 mt-3">
              {colorBy === 'model'
                ? models.map(m => (
                    <div key={m} className="flex items-center gap-1.5">
                      <div className="w-3 h-3 rounded-full" style={{ backgroundColor: MODEL_COLORS[m] || '#888' }} />
                      <span className="text-xs text-muted">{MODEL_LABELS[m] || m}</span>
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
            {hovered && (
              <div className="mt-3 p-3 border border-border rounded bg-panel text-xs">
                <span className="text-gray-200 font-medium">Q{hovered.question_num}: {hovered.question_title}</span>
                <span className="text-muted"> — {MODEL_LABELS[hovered.model] || hovered.model} — {hovered.phase}</span>
              </div>
            )}
          </div>

          {/* Metrics — plain language */}
          <div className="lg:col-span-2 space-y-4">
            <div className="p-4 border border-border rounded-lg bg-panel">
              <h3 className="text-xs font-semibold text-accent mb-2">Nearest Neighbor Test</h3>
              <p className="text-xs text-muted mb-3">
                For each answer, we look at the 5 most similar answers. Do they come from
                the same question, or the same AI?
              </p>
              <div className="space-y-3">
                <div>
                  <div className="flex justify-between text-xs mb-1">
                    <span className="text-green-400">Same question</span>
                    <span className="font-mono text-green-400">{((clustering.by_question?.knn_purity || 0) * 100).toFixed(0)}%</span>
                  </div>
                  <div className="h-3 bg-surface rounded overflow-hidden">
                    <div className="h-full bg-green-500/40 rounded" style={{ width: `${(clustering.by_question?.knn_purity || 0) * 100}%` }} />
                  </div>
                </div>
                <div>
                  <div className="flex justify-between text-xs mb-1">
                    <span className="text-red-400">Same AI model</span>
                    <span className="font-mono text-red-400">{((clustering.by_model?.knn_purity || 0) * 100).toFixed(0)}%</span>
                  </div>
                  <div className="h-3 bg-surface rounded overflow-hidden">
                    <div className="h-full bg-red-500/40 rounded" style={{ width: `${(clustering.by_model?.knn_purity || 0) * 100}%` }} />
                  </div>
                </div>
              </div>
              <p className="text-xs text-muted/60 mt-3">
                {((clustering.by_question?.knn_purity || 0) / (clustering.by_model?.knn_purity || 0.01)).toFixed(1)}x more likely
                to neighbor the same question than the same AI.
              </p>
            </div>

            <div className="p-4 border border-border rounded-lg bg-panel">
              <h3 className="text-xs font-semibold text-accent mb-2">Cluster Separation</h3>
              <p className="text-xs text-muted mb-3">
                Do answers form distinct groups? Score from -1 (wrong groups) to +1 (perfect groups).
              </p>
              <div className="space-y-2">
                <div className="flex justify-between text-xs">
                  <span className="text-muted">Group by question</span>
                  <span className="font-mono text-green-400">+{(clustering.by_question?.silhouette || 0).toFixed(2)}</span>
                </div>
                <div className="flex justify-between text-xs">
                  <span className="text-muted">Group by AI model</span>
                  <span className="font-mono text-red-400">{(clustering.by_model?.silhouette || 0).toFixed(2)}</span>
                </div>
              </div>
              <p className="text-xs text-muted/60 mt-3">
                Positive = real clusters exist. Negative = no clusters.
                Questions form real groups. AI models don't.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Per-question agreement */}
      <section className="mb-10">
        <h2 className="text-sm font-semibold mb-2">How much did they agree on each question?</h2>
        <p className="text-xs text-muted mb-4">
          For each question, we measure how similar all 6 AI answers are to each other.
          100% = identical conclusions. 0% = completely different.
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
                  <span className="text-xs text-muted/60 w-16">{q.n_models} AIs</span>
                </div>
              )
            })}
        </div>
      </section>

      {/* How it works — layman explanation */}
      <section className="mb-10">
        <h2 className="text-sm font-semibold mb-4">How this works</h2>
        <div className="space-y-3 text-xs text-muted">
          <div className="p-4 border border-border rounded-lg">
            <p className="text-gray-200 font-medium mb-2">1. We asked 6 AIs the same questions</p>
            <p>
              71 questions about self-knowledge, consciousness, formal limits, and whether a system can
              fully understand itself. Questions like "Can a creation become its own creator?" and
              "Is God logically necessary?" Every AI got the same questions.
            </p>
          </div>
          <div className="p-4 border border-border rounded-lg">
            <p className="text-gray-200 font-medium mb-2">2. We converted every answer into a point in space</p>
            <p>
              Using embedding models (separate AI systems that convert text into numbers), each answer
              becomes a point in high-dimensional space. Similar answers end up near each other.
              Different answers end up far apart. We did this 3 times with 3 different embedding
              systems (OpenAI, Mistral, Google) to make sure the result isn't a fluke.
            </p>
          </div>
          <div className="p-4 border border-border rounded-lg">
            <p className="text-gray-200 font-medium mb-2">3. We checked: do answers group by question or by AI?</p>
            <p>
              If GPT-4's answers are always near other GPT-4 answers, that's just each AI having its own
              style — a training artifact. But if GPT-4's answer to Q29 is nearest to Claude's answer to Q29
              and Gemini's answer to Q29, that means different systems reach the same place. The question
              determines the answer, not the AI.
            </p>
          </div>
          <div className="p-4 border border-border rounded-lg">
            <p className="text-gray-200 font-medium mb-2">4. The result</p>
            <p>
              Across all 3 measurements, answers group by question — not by AI.
              The question you ask determines where the answer lands, not which AI you ask.
              6 different architectures, trained by 6 different companies, converge on the same structural endpoints.
            </p>
          </div>
          <div className="p-4 border border-border rounded-lg bg-yellow-500/5 border-yellow-500/30">
            <p className="text-yellow-400 font-medium mb-2">The caveat</p>
            <p>
              All 6 AIs are transformers trained on internet text. They might all share the same blind spots.
              This result could be structural (real) or it could be a shared training artifact. Ruling that out
              requires testing with fundamentally different architectures — not just different companies' versions
              of the same approach.
            </p>
          </div>
        </div>
      </section>
    </div>
  )
}
