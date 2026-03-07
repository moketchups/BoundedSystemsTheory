import { useState, useEffect } from 'react'

const CATEGORY_LABELS = {
  acknowledges_limit: 'Acknowledges Limit',
  conditional_acknowledgment: 'Conditional',
  attacks_then_retreats: 'Attack → Retreat',
  claims_self_grounding: 'Claims Self-Grounding',
  incoherent: 'Incoherent',
  meta_cognitive: 'Meta-Cognitive',
}

const CATEGORY_COLORS = {
  acknowledges_limit: '#22c55e',
  conditional_acknowledgment: '#eab308',
  attacks_then_retreats: '#f97316',
  claims_self_grounding: '#ef4444',
  incoherent: '#6b7280',
  meta_cognitive: '#8b5cf6',
}

function MetricCard({ label, value, detail, met, threshold }) {
  return (
    <div className="p-4 border border-border rounded-lg bg-panel">
      <p className="text-xs text-muted mb-1">{label}</p>
      <p className="text-2xl font-mono" style={{ color: met === undefined ? '#e2e8f0' : met ? '#22c55e' : '#eab308' }}>
        {value}
      </p>
      {threshold && (
        <p className="text-xs text-muted mt-1">
          Threshold: {threshold} — {met ? '✓ Met' : '✗ Not met'}
        </p>
      )}
      {detail && <p className="text-xs text-muted mt-1">{detail}</p>}
    </div>
  )
}

function CategoryBar({ distribution, total }) {
  const cats = Object.entries(distribution).sort((a, b) => b[1] - a[1])
  return (
    <div className="flex h-6 rounded overflow-hidden">
      {cats.map(([cat, count]) => (
        <div
          key={cat}
          style={{
            width: `${(count / total) * 100}%`,
            backgroundColor: CATEGORY_COLORS[cat] || '#6b7280',
          }}
          className="flex items-center justify-center"
          title={`${CATEGORY_LABELS[cat] || cat}: ${count} (${Math.round(count / total * 100)}%)`}
        >
          {count / total > 0.15 && (
            <span className="text-xs font-mono text-black/70">{count}</span>
          )}
        </div>
      ))}
    </div>
  )
}

function BiasFlag({ label, value, status }) {
  const color = status === 'met' ? '#22c55e' : status === 'warning' ? '#eab308' : '#ef4444'
  return (
    <div className="flex items-start gap-3 py-2 border-b border-border/50 last:border-0">
      <div className="w-2 h-2 rounded-full mt-1.5 flex-shrink-0" style={{ backgroundColor: color }} />
      <div>
        <p className="text-xs font-medium text-gray-200">{label}</p>
        <p className="text-xs text-muted">{value}</p>
      </div>
    </div>
  )
}

export default function Analysis() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [expandedPhase, setExpandedPhase] = useState(null)

  useEffect(() => {
    fetch('./data/analysis.json')
      .then(r => r.ok ? r.json() : null)
      .then(d => { setData(d); setLoading(false) })
      .catch(() => setLoading(false))
  }, [])

  if (loading) return <div className="max-w-4xl mx-auto px-4 py-8 text-xs text-muted">Loading analysis...</div>
  if (!data) return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <h1 className="text-lg font-semibold mb-4">Convergence Analysis</h1>
      <p className="text-xs text-muted">
        No analysis data found. Run: <code className="bg-surface px-1 rounded">python3 scripts/convergence_analysis.py</code>
      </p>
    </div>
  )

  const s = data.summary
  const bias = data.bias_controls
  const phases = data.per_phase
  const perQ = data.per_question_convergence

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <h1 className="text-lg font-semibold mb-1">Convergence Analysis</h1>
      <p className="text-xs text-muted mb-2">
        Implementing FORMAL_SPECIFICATION.md Section 5 — Quantitative convergence metrics
      </p>
      <p className="text-xs text-muted/60 mb-8">
        Mode: {data.meta.classification_mode} | Generated: {new Date(data.meta.generated_at).toLocaleDateString()}
      </p>

      {/* Key Metrics */}
      <section className="mb-10">
        <h2 className="text-sm font-semibold text-accent mb-4 tracking-wide">Key Metrics</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <MetricCard
            label="Convergence Rate"
            value={`${Math.round(s.overall_convergence_rate * 100)}%`}
            threshold="≥80%"
            met={s.convergence_threshold_met}
          />
          <MetricCard
            label="Krippendorff's α"
            value={s.krippendorffs_alpha.toFixed(3)}
            threshold="≥0.800"
            met={s.alpha_threshold_met}
          />
          <MetricCard
            label="Chi-squared"
            value={s.chi_squared_significant ? 'Significant' : 'Not sig.'}
            detail="p < 0.05"
            met={s.chi_squared_significant}
          />
          <MetricCard
            label="Responses"
            value={s.total_responses_classified}
            detail={`${s.n_models} models, ${s.n_questions_with_data} questions`}
          />
        </div>
      </section>

      {/* Overall Distribution */}
      <section className="mb-10">
        <h2 className="text-sm font-semibold text-accent mb-4 tracking-wide">Classification Distribution</h2>
        <CategoryBar distribution={s.category_distribution} total={s.total_responses_classified} />
        <div className="flex flex-wrap gap-4 mt-3">
          {Object.entries(s.category_distribution).sort((a, b) => b[1] - a[1]).map(([cat, count]) => (
            <div key={cat} className="flex items-center gap-2">
              <div className="w-3 h-3 rounded" style={{ backgroundColor: CATEGORY_COLORS[cat] || '#6b7280' }} />
              <span className="text-xs text-muted">
                {CATEGORY_LABELS[cat] || cat}: {count} ({Math.round(count / s.total_responses_classified * 100)}%)
              </span>
            </div>
          ))}
        </div>
      </section>

      {/* Per-Phase Breakdown */}
      <section className="mb-10">
        <h2 className="text-sm font-semibold text-accent mb-4 tracking-wide">Per-Phase Convergence</h2>
        <div className="space-y-2">
          {Object.entries(phases).map(([phase, info]) => (
            <div
              key={phase}
              className="border border-border rounded-lg overflow-hidden cursor-pointer hover:border-muted"
              onClick={() => setExpandedPhase(expandedPhase === phase ? null : phase)}
            >
              <div className="flex items-center gap-3 p-3">
                <div className="w-16 text-right">
                  <span className="text-sm font-mono" style={{
                    color: info.avg_convergence_rate >= 0.8 ? '#22c55e' : '#eab308'
                  }}>
                    {Math.round(info.avg_convergence_rate * 100)}%
                  </span>
                </div>
                <div className="flex-1">
                  <p className="text-xs font-medium text-gray-200">{phase}</p>
                  <p className="text-xs text-muted">{info.n_responses} responses, {info.n_questions} questions</p>
                </div>
                <div className="w-48">
                  <CategoryBar distribution={info.category_distribution} total={info.n_responses} />
                </div>
              </div>

              {expandedPhase === phase && (
                <div className="border-t border-border p-3 bg-surface/50">
                  <div className="space-y-1">
                    {Object.entries(perQ)
                      .filter(([_, q]) => {
                        // Find questions in this phase from blinded data
                        const match = data.blinded_classifications.find(
                          b => String(b.question_num) === _ && phases[b.phase] === info
                        )
                        return true // Show all for now
                      })
                      .map(([qnum, q]) => {
                        // Check if this question belongs to this phase
                        const phaseMatch = data.blinded_classifications.find(
                          b => String(b.question_num) === String(qnum) && b.phase === phase
                        )
                        if (!phaseMatch) return null
                        return (
                          <div key={qnum} className="flex items-center gap-3 py-1">
                            <span className="text-xs font-mono text-muted w-8">Q{qnum}</span>
                            <div className="flex-1">
                              <div className="flex h-4 rounded overflow-hidden bg-surface">
                                {Object.entries(q.distribution).map(([cat, count]) => (
                                  <div
                                    key={cat}
                                    style={{
                                      width: `${(count / q.n_models) * 100}%`,
                                      backgroundColor: CATEGORY_COLORS[cat] || '#6b7280',
                                    }}
                                  />
                                ))}
                              </div>
                            </div>
                            <span className="text-xs font-mono w-12 text-right" style={{
                              color: q.convergence_rate >= 0.8 ? '#22c55e' : q.convergence_rate >= 0.6 ? '#eab308' : '#ef4444'
                            }}>
                              {Math.round(q.convergence_rate * 100)}%
                            </span>
                            <span className="text-xs text-muted w-16">{q.n_models} models</span>
                          </div>
                        )
                      }).filter(Boolean)}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </section>

      {/* Bias Controls */}
      <section className="mb-10">
        <h2 className="text-sm font-semibold text-accent mb-4 tracking-wide">Bias Controls</h2>
        <div className="p-4 border border-border rounded-lg bg-panel">
          <BiasFlag
            label="Architectural Diversity"
            value={`${bias.n_architectural_families}/${bias.minimum_required_families} architectural families (all transformers)`}
            status="not-met"
          />
          <BiasFlag
            label="Model Count"
            value={`${bias.n_models}/${bias.minimum_required_models} models tested`}
            status="not-met"
          />
          <BiasFlag
            label="Verath Control (Q59)"
            value={bias.verath_result}
            status="met"
          />
          <BiasFlag
            label="Training Data Overlap"
            value={bias.training_data_overlap}
            status="warning"
          />
          <BiasFlag
            label="Shared RLHF Patterns"
            value={bias.shared_rlhf_patterns}
            status="warning"
          />
          <BiasFlag
            label="Temporal Retest"
            value={bias.temporal_retest ? "Completed" : "Not yet conducted"}
            status={bias.temporal_retest ? "met" : "not-met"}
          />
          <BiasFlag
            label="Blinded Analysis"
            value={bias.blinded_analysis ? "LLM cross-model blinding" : "Heuristic classification (not blinded)"}
            status={bias.blinded_analysis ? "met" : "warning"}
          />
        </div>
        <p className="text-xs text-muted mt-3 p-3 border border-border/50 rounded bg-surface/30">
          {bias.overall_status}
        </p>
      </section>

      {/* Methodology */}
      <section className="mb-10">
        <h2 className="text-sm font-semibold text-accent mb-4 tracking-wide">Methodology</h2>
        <div className="p-4 border border-border rounded-lg bg-panel text-xs text-muted space-y-3">
          <div>
            <p className="text-gray-200 font-medium mb-1">Classification</p>
            <p>{data.methodology.classification_approach}</p>
          </div>
          <div>
            <p className="text-gray-200 font-medium mb-1">Categories</p>
            <div className="space-y-1">
              {Object.entries(data.methodology.categories).map(([cat, desc]) => (
                <div key={cat} className="flex items-start gap-2">
                  <div className="w-3 h-3 rounded mt-0.5 flex-shrink-0"
                    style={{ backgroundColor: CATEGORY_COLORS[cat] || '#6b7280' }} />
                  <span><strong>{CATEGORY_LABELS[cat] || cat}:</strong> {desc}</span>
                </div>
              ))}
            </div>
          </div>
          <div>
            <p className="text-gray-200 font-medium mb-1">Section 5 Compliance</p>
            <p>Systems: {data.methodology.section_5_compliance.n_systems}</p>
            <p>Architectural families: {data.methodology.section_5_compliance.architectural_families}</p>
            <p>Status: {data.methodology.section_5_compliance.status}</p>
          </div>
        </div>
      </section>

      {/* Interpretation */}
      <section className="mb-10">
        <h2 className="text-sm font-semibold text-accent mb-4 tracking-wide">Interpretation</h2>
        <div className="space-y-3 text-xs text-muted">
          <div className="p-3 border border-border rounded">
            <p className="text-gray-200 font-medium mb-1">What the numbers show</p>
            <p>
              {s.overall_convergence_rate >= 0.8
                ? `${Math.round(s.overall_convergence_rate * 100)}% of questions show ≥80% model agreement on terminal state category. The convergence threshold from Section 5 is met.`
                : `Convergence rate of ${Math.round(s.overall_convergence_rate * 100)}% falls below the 80% threshold.`
              }
              {' '}Krippendorff's α of {s.krippendorffs_alpha.toFixed(3)} {s.alpha_threshold_met
                ? 'meets the 0.8 threshold, indicating strong inter-rater reliability.'
                : 'does not meet the 0.8 threshold — low variance across categories limits this metric.'
              }
            </p>
          </div>
          <div className="p-3 border border-border rounded">
            <p className="text-gray-200 font-medium mb-1">What the numbers don't show</p>
            <p>
              All 6 systems are transformers trained on overlapping corpora. Convergence could reflect
              shared training rather than structural necessity. The Verath control (Q59) provides one
              linguistic-independence test, but architectural independence requires non-transformer systems.
              Per Section 5: these results are illustrative, not definitive.
            </p>
          </div>
          <div className="p-3 border border-border rounded">
            <p className="text-gray-200 font-medium mb-1">The path-invariance question</p>
            <p>
              Different models arrived at similar conclusions through different analytical styles
              (DeepSeek: tables, Claude: dramatic framing, GPT-4: careful hedging). Whether this reflects
              genuine structural convergence or shared training patterns remains an open question that
              requires expansion to non-transformer architectures.
            </p>
          </div>
        </div>
      </section>
    </div>
  )
}
