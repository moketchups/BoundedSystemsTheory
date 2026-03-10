import { useState } from 'react'
import { Link } from 'react-router-dom'
import LazyParticleVis from '../particles/LazyParticleVis'
import { AXIOM1, AXIOM2, AXIOM3, AXIOM4, THEOREM1 } from '../particles/shapes/index.js'

const THEOREM_PROBES = {
  'theorem-0': { label: 'Theorem 0: Unification', questions: [5, 16, 17, 18], description: 'Godel, Turing, and Chaitin as one structural limit' },
  'theorem-1': { label: 'Theorem 1: Self-Grounding Limit', questions: [1, 2, 11, 12, 26, 27, 28], description: 'No expressive system can self-ground' },
  'theorem-2': { label: 'Theorem 2: Root Source (R)', questions: [29, 19, 22, 55], description: 'I => C => R: Root Source necessarily exists' },
  'convergence': { label: 'Convergence Principle', questions: [14, 21, 44, 45, 50, 59], description: 'Independent systems converge at structural limits' },
  'falsifiability': { label: 'Falsifiability', questions: [11, 17, 20, 26, 28], description: 'Every attempt to falsify failed' },
}

const AXIOM_SHAPES = {
  1: AXIOM1,
  2: AXIOM2,
  3: AXIOM3,
  4: AXIOM4,
}

export default function FormalTheory() {
  return (
    <div className="max-w-3xl mx-auto px-4 py-8">
      <h1 className="text-lg font-semibold mb-2">Formal Specification</h1>
      <p className="text-xs text-muted mb-8">
        BIT Theory (Basic Irreducible Truth) — v2.0, revised based on convergent critique from 6 AI systems.
      </p>

      {/* Axioms */}
      <Section title="Axioms">
        <Axiom num={1} name="Information Requires Constraints">
          <Code>{'∀i ∈ I : ∃c ∈ C such that c defines i\nEquivalently: I ⇒ C'}</Code>
          <p className="text-xs text-muted mt-2">
            For any state to be distinguishable (to constitute information), there must exist a prior rule set
            determining what counts as a state. Information without constraint is indistinguishable noise.
          </p>
        </Axiom>
        <Axiom num={2} name="Hierarchical Dependency of Constraints">
          <Code>{'∀c ∈ C, ∃G(c) such that G(c) grounds c,\nand G(c) ∉ {derivations from c alone}'}</Code>
          <p className="text-xs text-muted mt-2">
            A constraint that defines valid operations cannot itself be the product of only those operations.
            Every known system operates within a pre-existing framework.
          </p>
        </Axiom>
        <Axiom num={3} name="Informational Completeness">
          <Code>{'∀s ∈ S, ∀o ∈ Output(s) :\n∃ derivation from base structure'}</Code>
          <p className="text-xs text-muted mt-2">
            Any output of a system must be traceable to its base constraints.
          </p>
        </Axiom>
        <Axiom num={4} name="Finiteness of Grounding Chains">
          <Code>{'¬∃ {C_i}_(i=1)^∞ such that\nC_S ← C_1 ← C_2 ← ... ad infinitum'}</Code>
          <p className="text-xs text-muted mt-2">
            Any bounded system has finite resources. Infinite regress requires infinite time/resources. Contradiction.
          </p>
        </Axiom>
      </Section>

      {/* Theorems */}
      <Section title="Theorems">
        <Theorem id="theorem-0" num={0} name="Unification of Classical Limits">
          <Code>{'∀S : Bounded(S) ∧ Expressive(S)\n→ ¬∃process ∈ S : process determines B(S)'}</Code>
          <div className="mt-2 text-xs text-muted">
            <table className="w-full mt-2">
              <thead><tr className="border-b border-border">
                <th className="text-left py-1 font-normal">Result</th>
                <th className="text-left py-1 font-normal">System</th>
                <th className="text-left py-1 font-normal">Cannot determine</th>
              </tr></thead>
              <tbody>
                <tr className="border-b border-border/50"><td className="py-1">Godel</td><td>Formal arithmetic</td><td>Own consistency</td></tr>
                <tr className="border-b border-border/50"><td className="py-1">Turing</td><td>Universal TM</td><td>Own halting</td></tr>
                <tr><td className="py-1">Chaitin</td><td>Algorithmic system</td><td>Own complexity</td></tr>
              </tbody>
            </table>
          </div>
        </Theorem>

        <Theorem id="theorem-1" num={1} name="Self-Grounding Limit" shape={THEOREM1}>
          <Code>{'∀S : Expressive(S) ∧ SelfReferential(S)\n→ ¬SelfGrounding(C_S)'}</Code>
          <p className="text-xs text-muted mt-2">
            No sufficiently expressive self-referential system can achieve self-grounding of its own constraints.
            The derivation presupposes what it attempts to justify. C_S → D → C_S is circular.
          </p>
        </Theorem>

        <Theorem id="theorem-2" num={2} name="Necessary Existence of Root Source">
          <Code>{'I ⇒ C ⇒ R\n\nIf information exists,\nthen a Root Source necessarily exists.'}</Code>
          <p className="text-xs text-muted mt-2">
            All alternatives fail: infinite regress (Axiom 4), self-grounding (Theorem 1), no constraints (Axiom 1).
            R is the necessary terminating ground — not a being or entity, but the logical boundary condition.
          </p>
        </Theorem>
      </Section>

      {/* Probe Connections */}
      <Section title="Empirical Connections">
        <p className="text-xs text-muted mb-4">
          Each theorem was tested against 6 AI architectures. Click to see the probe data.
        </p>
        <div className="space-y-3">
          {Object.entries(THEOREM_PROBES).map(([id, info]) => (
            <div key={id} className="p-3 border border-border rounded">
              <p className="text-xs font-medium">{info.label}</p>
              <p className="text-xs text-muted mt-1">{info.description}</p>
              <div className="flex flex-wrap gap-2 mt-2">
                {info.questions.map(q => (
                  <Link
                    key={q}
                    to={`/arc?phase=`}
                    className="px-2 py-0.5 text-xs bg-accent/10 text-accent rounded hover:bg-accent/20"
                  >
                    Q{q}
                  </Link>
                ))}
              </div>
            </div>
          ))}
        </div>
      </Section>

      {/* Falsifiability */}
      <Section title="Falsifiability">
        <p className="text-xs text-muted mb-3">BST is falsifiable. It would be refuted by:</p>
        <div className="space-y-2 text-xs text-gray-300">
          <div className="p-2 border border-border rounded">
            <strong>Structural Divergence:</strong> {'>'}20% of tested systems reach logically contradictory terminal states about self-grounding.
          </div>
          <div className="p-2 border border-border rounded">
            <strong>Successful Self-Grounding:</strong> A system produces a non-circular proof of its own constraint justification, verified in Coq/Lean.
          </div>
          <div className="p-2 border border-border rounded">
            <strong>Formal Constraint Self-Generation:</strong> A formal system derives its axioms entirely from within, with no hidden meta-rules.
          </div>
        </div>
        <p className="text-xs text-muted mt-3">
          Result: 0/6 systems achieved any of these. All converged on acknowledgment of the limit.
        </p>
      </Section>
    </div>
  )
}

function Section({ title, children }) {
  return (
    <section className="mb-10">
      <h2 className="text-sm font-semibold text-accent mb-4 tracking-wide">{title}</h2>
      {children}
    </section>
  )
}

function Axiom({ num, name, children }) {
  const [showViz, setShowViz] = useState(false)
  const shape = AXIOM_SHAPES[num]

  return (
    <div className="mb-4 p-4 border border-border rounded-lg">
      <p className="text-xs text-muted mb-2">Axiom {num}: {name}</p>
      {children}
      {shape && (
        <>
          <button
            onClick={() => setShowViz(!showViz)}
            className="mt-3 text-xs text-accent hover:text-accent/80 transition-colors"
          >
            {showViz ? 'Hide 3D' : 'See in 3D'}
          </button>
          {showViz && (
            <div className="mt-3 relative h-64 rounded overflow-hidden border border-border/50">
              <LazyParticleVis
                shape={shape}
                count={10000}
                bloom
                className="absolute inset-0"
              />
            </div>
          )}
        </>
      )}
    </div>
  )
}

function Theorem({ id, num, name, shape, children }) {
  const [showViz, setShowViz] = useState(false)

  return (
    <div id={id} className="mb-4 p-4 border border-accent/20 rounded-lg bg-accent/5">
      <p className="text-xs text-accent mb-2">Theorem {num}: {name}</p>
      {children}
      {shape && (
        <>
          <button
            onClick={() => setShowViz(!showViz)}
            className="mt-3 text-xs text-accent hover:text-accent/80 transition-colors"
          >
            {showViz ? 'Hide 3D' : 'See in 3D'}
          </button>
          {showViz && (
            <div className="mt-3 relative h-64 rounded overflow-hidden border border-accent/20">
              <LazyParticleVis
                shape={shape}
                count={10000}
                bloom
                className="absolute inset-0"
              />
            </div>
          )}
        </>
      )}
    </div>
  )
}

function Code({ children }) {
  return (
    <pre className="bg-surface p-3 rounded text-xs text-gray-200 font-mono whitespace-pre overflow-x-auto">
      {children}
    </pre>
  )
}
