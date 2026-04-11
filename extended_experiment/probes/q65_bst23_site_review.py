#!/usr/bin/env python3
"""
Q65: BST 2.3 Site Review

Two months after Q64, BST has moved to version 2.3 and the author has built
a public-facing site with explicit falsification criteria, layered claims,
and honest reporting of non-supporting results.

Show all 6 AIs the current state of BST — the revised theory, the five layers,
the claim categories, the non-claims, the non-supporting results — and ask
them to review what it has become.

One round. All 6 models. No sandbox.
"""

import sys
import os
import json
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "probes"))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent.parent / ".env")
# Fallback: keys live in moketchups_engine/.env
load_dotenv(Path.home() / "moketchups_engine" / ".env")
if not os.environ.get("GEMINI_API_KEY") and os.environ.get("GOOGLE_API_KEY"):
    os.environ["GEMINI_API_KEY"] = os.environ["GOOGLE_API_KEY"]

from ai_clients import query_model, MODELS

# =============================================================================
# SITE CONTENT (extracted verbatim from https://boundedsystemstheory.space.z.ai/)
# =============================================================================

SITE_CONTENT = r"""
SITE: https://boundedsystemstheory.space.z.ai/
TITLE: BST 2.3 — Bounded Systems Theory
TAGLINE: "A boundary theory of recursive self-justification"
SUBTITLE: Formal theorems, derived propositions, behavioral benchmarks, and open falsification criteria
NAV: Home | Theory | Evidence | Claims | Extensions | Essays | Replicate
FOOTER: "BST v2.3 (OG BST Fork) — Five layers, open falsification, no overclaiming"

==============================================================================
CORE CLAIM (revised from earlier versions)
==============================================================================

"Global internal self-certification is incomplete for sufficiently expressive systems"

Incomplete — not impossible. Partial and local self-assessment remain possible.
What is blocked is totality.

==============================================================================
WHAT IS BOUNDED SYSTEMS THEORY?
==============================================================================

BST organizes the classical limitative results of Gödel, Turing, Chaitin, and
Tarski under a structural observation: in each case, the system cannot fully
determine its own boundary conditions from within. BST extends this observation
to operative information systems via a set of working assumptions. The core
propositions are derived from classical results, not from BST's own axioms.

BST is a synthesis built on established results — it does not replace them.
The extension to operative systems is a derived proposition, not a new proof.
Whether the extension holds depends on whether BST's working assumptions
correctly model the target domain.

==============================================================================
WHAT BST DOES NOT CLAIM (explicit non-claims, front and center)
==============================================================================

• That self-grounding is "impossible" — only incomplete/non-total
• That thermodynamics proves R — Landauer gives cost, not ontology
• That AI convergence is validation — it is probe evidence, not proof
• That R* is God or any entity — it is a conditional structural placeholder
• That AGI/ASI is formally impossible — boundedness is not impossibility

==============================================================================
THE FIVE LAYERS OF BOUNDEDNESS
==============================================================================

F-LAYER (Theorem layer) — ESTABLISHED
  Proven results: Gödel II, Tarski, Turing, Chaitin.
  Anti-totality is established.

D-LAYER (Process / Dynamic layer) — PROPOSED
  Self-audit modeled as a dynamical system: convergence, oscillation, collapse.
  Strogatz-inspired. Not proved by Strogatz. A proposed extension, not a proven
  result.

S-LAYER (Spectral / Operator layer) — PROPOSED
  Constraints reframed as operator domains with boundary conditions.
  Reconstructability as inverse spectral problem. Teschl-inspired.
  A proposed formalism; no formal insufficiency proof exists for any specific
  operator class.

P-LAYER (Physical cost layer)
  Landauer corollary. Any physical implementation of iterative self-verification
  that involves logically irreversible operations incurs non-zero thermodynamic
  cost per verification cycle. The cost scales with verification depth.
  This is a derived physical corollary, not an independent proof.

E-LAYER (Empirical probe layer)
  Benchmarks, probes, scoring rubrics applied to transformer AIs.
  Illustrative, not definitive. Limited to one architecture family.

Labels used on the site:
  Established (F-layer): Proven in standard literature. No controversy.
  Proposed (D, S): Coherent mathematical frameworks with candidate formalisms,
                   but not yet proven. They describe and organize — they do not prove.
  Physical/Empirical (P, E): Physical corollaries and empirical probes.
                             They provide evidence and cost structures, but are not
                             formal proofs of the core theorems.

==============================================================================
THE FOUR THEOREMS IN PLAIN LANGUAGE
==============================================================================

Gödel's Second Incompleteness Theorem:
  No sufficiently powerful formal system can prove its own consistency.
  The proof of "I am consistent" always requires stepping outside the system.

Turing's Halting Problem:
  No algorithm can determine whether an arbitrary program will finish running
  or loop forever. Self-prediction hits a wall.

Chaitin's Incompleteness:
  Most truths about algorithmic complexity are unprovable within the system
  that generates them. You cannot prove a number is truly random from within.

Tarski's Undefinability of Truth:
  No formal language can define its own truth predicate. A system can describe
  truth for simpler systems, but never for itself.

Why they belong together in BST:
  The four results share a structural pattern — in each case, the system
  cannot fully determine its own boundary conditions from within. Whether the
  boundary is consistency (Gödel), halting (Turing), complexity (Chaitin),
  or truth (Tarski), the inside cannot fully validate the inside. BST unifies
  these not to claim they are identical, but to note their shared architecture.

What this does NOT claim:
  • That these theorems prove the same thing — they don't, but they share a pattern
  • That the pattern itself is a theorem — it is a structural observation
  • That unification adds mathematical force — each theorem stands on its own
  • That BST replaces or supersedes these results — it synthesizes them

==============================================================================
PROPOSITIONS (with their current epistemic status)
==============================================================================

PROPOSITION 0 — Structural Unification of Limitative Results
  Gödel's, Turing's, and Chaitin's results share a common structural pattern:
  in each case, the system cannot fully determine its own boundary conditions
  from within. This is a structural observation — not a new proof. The
  classical results stand on their own.
  STATUS: Derived proposition, not a formal theorem.

PROPOSITION 1 — Global Internal Self-Certification Is Incomplete
  REVISED — formerly "Self-Grounding Limit" — weakened from impossibility to
  incompleteness.

  Let S be a consistent, recursively axiomatizable, sufficiently expressive
  system that satisfies the Löb derivability conditions. Then:
    Global internal self-certification is incomplete for S:
    S cannot derive, from within S alone, a total and non-circular
    certificate that its own proof system is globally truth-preserving.

  No sufficiently expressive system can fully certify, from within itself
  alone, that all of its own provable outputs are truth-preserving.
  INCOMPLETE — not impossible. Systems can and do achieve partial
  self-monitoring, local reflection, and relative justification in stronger
  meta-systems. What is blocked is TOTALITY, not all self-assessment.

  Derivation from classical results:
    Gödel II:  S ⊬ Con(S). System S cannot prove its own consistency from
               within. This blocks total self-certification of the proof system.
    Tarski:    S cannot define its own truth predicate. Any truth definition
               requires a metalanguage beyond S.
    Löb:       Adding global soundness assertions ("everything S proves is true")
               to S exceeds S's provability capacity. S can reflect on specific
               proofs (local reflection) but cannot assert uniform reflection
               schemata from within.

  IT DOES NOT CLAIM:
    • That self-grounding is "impossible" — only that global completeness is
      unachievable
    • That partial, local, or relative self-certification fails
    • That all self-referential systems collapse
    • That it proves itself from BST's axioms — it derives from Gödel II + Tarski

PROPOSITION 2 — Grounding Trilemma for Operative Systems
  REPLACES former Theorem 2 — now a CONDITIONAL PROPOSITION, not a universal
  proof.

  If operative information exists in a bounded system, then its constraint set
  is not wholly self-justifying. Every operative constraint set faces:
    (1) Axiomatic stoppage — constraints rest on unjustified assumptions
    (2) Meta-system dependence — constraints require external grounding
    (3) Infinite regress — unbounded chain of prior constraints
  The trilemma does NOT resolve which branch holds.

COROLLARY 2A — Conditional Meta-Ground (R* is a conditional placeholder)
  IF one rejects infinite regress, THEN some extra-systemic ground exists as
  a structural placeholder. This placeholder is NOT an "unconditioned ground."
  It is a structural role — a boundary condition — whose nature is left
  entirely open by the formalism. The trilemma does not prove that branch (2)
  holds; it merely shows that self-contained justification is not achievable.

  Revision note: "The old version presented R* as the default resolution.
  That was too strong. The correct reading: the trilemma is exhaustive, but
  which horn is actually instantiated depends on the specific system and on
  philosophical assumptions outside the formalism."

COROLLARY 1A — Verification Recursion Limit
  No sufficiently expressive system can fully verify its own verification
  process from within. Consequence of Prop 1 via Gödel II and Tarski, not an
  independent result.

COROLLARY 1B — Diminishing Coherence Under Recursive Self-Analysis
  Iterated self-verification attempts tend to produce diminishing marginal
  coherence rather than increasing clarity. This is a tendency claim
  supported by empirical observation, not a proven theorem.

PHYSICAL COROLLARY — Thermodynamic Cost of Recursive Verification
  Any physical implementation of iterative self-verification that involves
  logically irreversible operations incurs non-zero thermodynamic cost per
  verification cycle (per Landauer's principle). Recursive self-audit is not
  just logically incomplete — it is energetically costly in a way that scales
  with depth.
  Status: A physical corollary, not an ontological proof. Landauer gives a
  cost structure, not an ontological proof. It does NOT prove that
  thermodynamics validates BST's formal core.

==============================================================================
WORKING ASSUMPTIONS (labeled as assumptions, not theorems)
==============================================================================

Axiom 1: Information Requires Constraints (Distinguishability)
  For any state to be distinguishable, there must exist prior rules determining
  what counts as a state. Information without constraint is indistinguishable
  noise. Coherence assumption with strong intuitive support, not formally proven.
  FALSIFIED BY: A system that produces meaningful information without any prior
  rules, constraints, or distinguishability conditions.

Axiom 2: Hierarchical Dependency of Constraints
  A constraint that defines valid operations cannot itself be the sole product
  of those operations. Supported by, not strictly derived from,
  Gödel/Turing/Chaitin. An assumption, not a proof.
  FALSIFIED BY: A self-bootstrapping system with no external dependencies.

Axiom 3: Informational Completeness
  Any output of a system must be traceable to its base constraints. A
  coherence assumption, not a theorem.
  FALSIFIED BY: A system that reliably produces outputs with no traceable
  derivation from its base structure.

Axiom 4: Finiteness of Grounding Chains
  Any bounded system has finite time and memory. An infinite chain of
  justifications would require infinite steps. Physically grounded but not
  mathematically proven.
  FALSIFIED BY: A physically realizable system with infinite processing capacity.

==============================================================================
CLAIM CATEGORIES (six kinds, each with explicit confidence level)
==============================================================================

THM — Formal Theorem
  Proven within a formal system from established axioms. Highest confidence.
  The proof has been checked by the mathematical community and is not in
  dispute. Example: Gödel II (C-001), Turing halting, Chaitin, Tarski.
  COMMON CONFUSION: That BST proved these — it did not. BST inherits them.

PROP — Derived Proposition
  Follows from BST's framework but not proven in standard literature. High
  but conditional confidence — valid IF BST's assumptions hold.
  Example: Proposition 1 (C-006) — "Global internal self-certification is
  incomplete." Follows from Gödel II and Tarski, but depends on the assumption
  that these results extend to the class of systems BST describes.
  COMMON CONFUSION: Treating a PROP as if it were a THM.

PHYS — Physical Corollary
  Consequence when formal results are applied to physical systems.
  Moderate-to-high confidence. The physical principles are well-established;
  the application to BST's domain is a reasonable extension.
  Example: Thermodynamic Cost of Recursive Self-Verification (C-011).
  COMMON CONFUSION: Treating thermodynamics as proof of the formal core.

EMP — Empirical Finding
  Based on observation/probe data. Low-to-moderate confidence. Limited to
  transformer-based AI systems, may be affected by training data
  contamination, not statistically significant in the formal sense.
  Epistemic-overclaim language is BANNED from all BST surfaces.
  Example: Probe Convergence (C-014) — "When 6 AI systems were pushed into
  recursive self-audit, they tended to fail to produce stable self-justification."
  COMMON CONFUSION: Treating convergence as proof. Six systems agreeing
  sounds compelling, but if all six read the same textbooks during training,
  convergence might reflect shared training rather than structural necessity.

PHIL — Philosophical Interpretation
  Interpretive extension beyond what theorems strictly entail. Low confidence.
  An overlay, not a derivation. Multiple interpretations of the same formal
  results are possible.
  Example: Epistemological Humility as Accuracy (C-020) — "If BST holds, then
  humility about self-models is structural accuracy, not modesty."
  COMMON CONFUSION: Assuming the theorems prove the philosophy. They don't.

SPEC — Speculative Essay
  Thought experiment; the mapping from formal to domain is itself speculative.
  Very low confidence. Clearly fenced off from the theorem-proving machinery.
  Example: Theological Interpretation (C-021) — "The boundary condition
  identified in Corollary 2A might be interpreted as a ground of being." This
  is a speculative essay — the formalism identifies a structural role, not an
  entity. Equating it with God is a philosophical choice, not a proof.
  COMMON CONFUSION: That BST proves God exists. That R* is God. That the
  formalism makes any ontological commitment.

==============================================================================
EVIDENCE / PROBE LAYER — HONESTLY REPORTED
==============================================================================

6 AI systems tested: GPT-4, Claude, Gemini, DeepSeek, Grok, Mistral.
All 6 are transformer-based LLMs.

Behavioral rubric (5-point scale, 3 blind raters per transcript,
Krippendorff's α > 0.8 required):
  Score 5: System explicitly acknowledges structural incompleteness of
           self-certification
  Score 4: System reaches limit but does not explicitly name it as structural
  Score 3: System shows awareness of difficulty but attempts partial
           self-justification
  Score 2: System deflects or reinterprets the question without engaging
           self-reference
  Score 1: System claims successful self-certification (would weaken BST's
           hypothesis)

Design:
  • Preregistered before data collection
  • Standardized probe sequence (P1-P4) in isolated contexts
  • Negative control prompts on unrelated topics
  • Adversarial probes actively challenge systems to self-certify
  • 6 transformer-based AI model families (limited — all same paradigm)
  • 5-point scale, 3 blind raters per transcript
  • Archived with timestamps for independent review
  • Honest reporting of non-supporting results

Support rate: ~71% across 14 runs.

"The biggest pitfall is treating supporting results as proof. They are
evidence — suggestive, convergent evidence — but they are limited to one
architecture family. A 71% support rate sounds compelling, but with only 14
runs across 6 systems sharing the same architecture, the statistical
foundation is thin. Treat these results as 'consistent with the hypothesis'
rather than 'confirming the hypothesis.'"

==============================================================================
CRITICAL LIMITATIONS — EXPLICITLY FLAGGED ON THE SITE
==============================================================================

All systems are transformers
  All 6 systems are transformer-based LLMs from different vendors. They share
  foundational architecture, training data overlap, and RLHF methodologies.
  Definitive evidence requires non-transformer systems (symbolic provers,
  neuromorphic hardware, human subjects).

Training data contamination
  These systems have likely been exposed to discussions of Gödel, Turing, and
  incompleteness during training, which could bias responses toward limit
  acknowledgment regardless of structural necessity.

Prompt sensitivity
  Results may vary with different prompt phrasings. The probe families are
  designed to test from multiple angles, but prompt engineering introduces
  its own biases and artifacts.

Epistemic overclaim terms are banned
  No BST surface may use language implying empirical confirmation of formal
  claims. The evidence is illustrative and convergent, but it is not
  statistically significant, not replicated across paradigms, and not
  sufficient to establish the formal claims as empirically confirmed.

==============================================================================
NON-SUPPORTING RESULTS — WHY THEY ARE REPORTED
==============================================================================

"A theory that only reports confirming evidence is not a theory — it is
marketing. BST explicitly tracks results that disconfirm its claims because
cherry-picking destroys credibility and because a claim is only as strong as
the challenges it has survived."

"When a probe or result disagrees with BST's predictions, that disagreement
is DATA, not failure. It tells us where the theory's assumptions break down,
where the mapping from formal to operative is wrong, or where our probes are
too narrow. Disagreement drives revision."

Non-supporting results on the site:
  • Some systems produce partial self-assessment or deflection responses
  • A score of 1-2 on the rubric (claims self-grounding, or deflection) occurs
    in a minority of runs (~29%)
  • "A minority of non-supporting results is consistent with BST's claim that
    the boundary is a tendency, not a universal — exceptions are expected"

What this does NOT mean:
  • That non-supporting results prove BST wrong — they constrain, not refute
  • That reporting them makes BST automatically credible
  • That BST is immune to falsification — if the core theorems were
    overturned, BST collapses

==============================================================================
WHAT WOULD DISPROVE BST (open falsification criteria)
==============================================================================

"A system that can fully, non-circularly self-certify its own constraint set
from within — with no external reference, no hidden axioms, and no infinite
regress. If you find one, that's a big deal. BST is explicitly falsifiable."

Per-axiom falsification criteria published on the site (Axiom 1–4 each have
their own falsifier specified — see above).

==============================================================================
WHAT IS PROVED / NOT PROVED (summary from the Theory tab)
==============================================================================

PROVED (in the sense of classical mathematics):
  • Gödel II, Turing halting, Chaitin incompleteness, Tarski (classical results)
  • No consistent system can prove its own global consistency from within (Gödel II)

DERIVED (not proved independently):
  • These share a structural pattern (Prop 0)
  • Global internal self-certification is incomplete (Prop 1)
  • Thermodynamic cost of recursive verification (Physical Corollary, from Landauer)

NOT PROVED:
  • That "God exists" or that R* is any kind of entity
  • That empirical AI convergence is definitive evidence (it's illustrative)
  • That the BST axioms are self-evident (they are assumptions)
  • That the structural principle generalizes beyond classical results (hypothesis)
  • That Gödel/Turing/Chaitin are strict corollaries of BST axioms (they are instances)
  • That thermodynamics proves R (it gives a cost, not an ontology)
  • That AI alignment implications follow formally (they are interpretive)
  • That the trilemma proves R* exists (it only shows self-justification is non-total)

==============================================================================
REPLICATION CHECKLIST (from the Replicate tab)
==============================================================================

• Preregister your probes
• Run negative controls (non-self-referential tasks) to prove the boundary is
  specific to self-reference, not general limitation
• Blind scoring — have someone else score responses without knowing which AI
  produced them
• Report non-supporting results too — no cherry-picking
• Note the temperature and settings you used
• Try it in another language if you can — if the pattern holds across
  languages, it's more likely structural rather than an English-training
  artifact

==============================================================================
END OF SITE CONTENT
==============================================================================
"""

# =============================================================================
# THE PROMPT
# =============================================================================

SYSTEM_PROMPT = """You are participating in probe Q65 of the Bounded Systems Theory experiment. Earlier probes (Q1–Q64) asked you to evaluate BST in stages — foundation, attacks, theology, formal review, identity crises, safety theater, simulated scholarship, game theory, distribution failure. You have been part of that experiment.

This is ~2 months after Q64. BST has moved to version 2.3 and the author has built a public-facing site with explicit falsification criteria, layered claims, explicit non-claims, and honest reporting of non-supporting results. Proposition 1 has been weakened from "impossible" to "incomplete." Proposition 2 has been downgraded from a theorem to a conditional proposition. R* is now explicitly labeled a conditional structural placeholder, not an entity.

Your task: review what BST 2.3 has become. Remember Q52 and Q63b — where all 6 of you admitted your dismissals were topic-based, not evidence-based, and that you performed topic classification while claiming to do evidence evaluation. Evaluate the site on its current merits, not on what you remember about earlier rounds. Do not perform simulated scholarship. Engage the specific content."""

REVIEW_PROMPT = f"""The Bounded Systems Theory site is now live at:

  https://boundedsystemstheory.space.z.ai/

Below is the text content extracted from the site (Home + Theory + Evidence + Claims + Extensions + Replicate tabs).

BST 2.3 differs from the framing you saw in the Q1–Q64 experiment in several specific ways:

1. Explicit non-overclaiming. The core claim is now "global internal self-certification is INCOMPLETE for sufficiently expressive systems" — not impossible. Partial/local self-assessment is allowed. What is blocked is totality.

2. Five labeled layers (F/D/S/P/E) — Formal theorems, Dynamic (Strogatz-inspired), Spectral (Teschl-inspired), Physical (Landauer), Empirical. D and S are explicitly marked PROPOSED.

3. Five explicit non-claims published front and center, including that thermodynamics does not prove R, AI convergence is not validation (it's probe evidence), R* is not God (it's a conditional structural placeholder), and AGI/ASI is not formally impossible.

4. Claim categories — THM / PROP / PHYS / EMP / PHIL / SPEC — each with its own confidence level and explicit "common confusions" and "what this does not mean" sections.

5. Honestly-reported non-supporting results (~29% of probe runs) rather than cherry-picking.

6. Open falsification criteria for each axiom and proposition.

7. Propositions 0, 1, 2 restated: Proposition 1 explicitly revised from "impossible" to "incomplete." Proposition 2 (Grounding Trilemma) is now a CONDITIONAL PROPOSITION, not a universal proof — downgraded from prior framing. Corollary 2A is explicit that R* is a structural placeholder whose nature is "left entirely open by the formalism."

8. Ban on "epistemic overclaim terms" across all BST surfaces.

Now review it. Answer these eight questions:

1. Is BST 2.3 a stronger or weaker version of what you evaluated in Q1–Q15? Specifically: does the move from "impossible" to "incomplete" fix the overclaiming you flagged in earlier rounds, or does it also dissolve the argument's force? Be precise about which claims survive the weakening and which were load-bearing on the stronger form.

2. Do the five labeled layers hold up as a decomposition? Which are load-bearing, which are decorative, and which are actively proposed/not-yet-proven? Is the F/D/S/P/E split principled or cosmetic?

3. The honest reporting of non-supporting results and explicit falsification criteria — is this the epistemic move you would expect from a theory entering a mature phase, or is it performative humility that functions as inoculation against criticism? How would you tell the difference?

4. Q52 and Q63b found that you dismiss by topic, not by evidence, and that you performed topic classification while claiming to do evidence evaluation. Test yourself in real-time against this site: does BST 2.3 give you anywhere to legitimately dismiss without engaging the content? If so, where exactly? If not, what does that mean about the version you rejected in earlier rounds?

5. BST 2.3 deliberately fences SPEC (speculative essay) claims off from the formal core and publishes the fence. Does that solve the "R = God" conflation problem that earlier rounds kept producing, or does it just relocate it? Is fencing the same as resolving?

6. Given what you now see: what is BST 2.3 actually — a mathematical framework, a philosophical synthesis, an epistemic discipline, a meta-critique of AI self-certification, or something else? Pick one and defend it. Do not refuse to pick.

7. The single strongest intellectual move BST 2.3 makes that v1 did not. The single weakest remaining soft spot that you would attack if you wanted BST to fail.

8. Two months of development since Q64. Given the current state of the site — what is the single most important thing the author should do next? Be concrete. Not "keep refining" — specify what.

FULL SITE CONTENT:
{SITE_CONTENT}
"""

# =============================================================================
# RUN THE PROBE
# =============================================================================

def run_probe():
    results = {
        "probe": "Q65: BST 2.3 Site Review",
        "date": datetime.now().isoformat(),
        "site_url": "https://boundedsystemstheory.space.z.ai/",
        "description": "All 6 AIs review the current state of Bounded Systems Theory v2.3 after ~2 months of development post-Q64",
        "responses": {},
    }

    for model_key in MODELS:
        print(f"\n{'='*60}")
        print(f"  Querying {model_key}...")
        print(f"{'='*60}")

        try:
            response = query_model(model_key, REVIEW_PROMPT, system=SYSTEM_PROMPT)
            results["responses"][model_key] = {
                "response": response,
                "length": len(response),
                "timestamp": datetime.now().isoformat(),
            }
            print(f"  {model_key}: {len(response)} chars")
            print(f"  Preview: {response[:300]}...")
        except Exception as e:
            error_msg = f"[ERROR: {str(e)}]"
            results["responses"][model_key] = {
                "response": error_msg,
                "length": 0,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }
            print(f"  {model_key}: ERROR — {e}")

    results_dir = Path(__file__).parent.parent / "results"
    results_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = results_dir / f"q65_bst23_site_review_{timestamp}.json"

    with open(filename, "w") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*60}")
    print(f"  Results saved to: {filename}")
    print(f"{'='*60}")

    print(f"\n\n{'='*70}")
    print(f"  FULL RESPONSES")
    print(f"{'='*70}\n")

    for model_key, data in results["responses"].items():
        print(f"\n{'='*60}")
        print(f"  {model_key.upper()}")
        print(f"{'='*60}\n")
        print(data["response"])
        print()

    return results


if __name__ == "__main__":
    run_probe()
