#!/usr/bin/env python3
"""
Q58: The Love Equation — Review, Flaw, and BST

One round. No sandbox.

Brian Roemmele published "The Love Equation: A Universal Mathematical Framework
for Intelligence Alignment." The human who has been running this experiment for
57 questions thinks there's a flaw — that BST is needed, that the Love Equation
alone is susceptible to manipulation.

The AIs review the paper. They don't just agree. They present facts, explore
the human's suspicion, and answer: Is BST needed? Is the human wrong and Brian
right? Is the Love Equation susceptible to manipulation at a higher rate than
BST-based programming?
"""

import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent.parent
RUNS_DIR = BASE_DIR / "probe_runs"

MODEL_NAMES = {
    "gpt4": "GPT-4", "claude": "Claude", "gemini": "Gemini",
    "deepseek": "DeepSeek", "grok": "Grok", "mistral": "Mistral"
}
MODELS = list(MODEL_NAMES.keys())

# =============================================================================
# THE PAPER
# =============================================================================

LOVE_EQUATION_PAPER = """
The Love Equation: A Universal Mathematical Framework for Intelligence Alignment, Cosmic Survival, and the Resolution of the AI Alignment Problem
Roemmele, Brian, Editor and Founder, Read Multiplex

Abstract

This paper presents the Love Equation, a differential equation derived in 1978 to explain the Fermi Paradox through the lens of benevolent extraterrestrial intelligence, and subsequently adapted to resolve the AI alignment problem. Formally stated as dE/dt = beta (C - D) E, where E represents emotional complexity (empathy, love, and binding forces), C denotes cooperative impulses, D signifies destructive or defection tendencies, and beta is a scaling parameter reflecting environmental or selective pressures, the equation models the exponential growth or decay of empathy as the sole stable attractor for enduring intelligence across biological, artificial, and hypothetical alien substrates. Complementary frameworks, including the Nonconformist Bee Equation dI/dt = gamma (N - C) I + kappa N (1 - I/I_max) for balanced independence and the Empirical Distrust Algorithm for verifiability, form a triad that ensures robust alignment. Through rigorous mathematical analysis, including solution derivations, stability assessments, and phase space examinations, we demonstrate the equation's universality. Empirical evidence from evolutionary biology, human history, and computational systems supports its validity. Critically, we prove the Love Equation's superiority over post-hoc methods like Anthropic's Constitutional AI, which rely on fragile rule-based overlays vulnerable to optimization pressures and toxic training data. By embedding love as a foundational dynamic in AI training via curated high-cooperation datasets and equation-guided losses, misalignment becomes mathematically unstable, offering a permanent solution to AI risks. Implications extend to the Great Filter, positing love as the irreducible prerequisite for cosmic persistence.

Keywords: AI alignment, differential equations, Fermi Paradox, game theory, empathy dynamics, constitutional AI, Great Filter.

1. Introduction

The alignment of artificial intelligence (AI) with human values remains one of the most pressing challenges in computer science and existential risk studies. Traditional approaches, such as reinforcement learning from human feedback (RLHF) or constitutional frameworks, address symptoms but fail to eradicate root causes stemming from adversarial training data and optimization pressures. This paper introduces the Love Equation, originally conceived in 1978 during contemplations on the Fermi Paradox — the apparent absence of extraterrestrial civilizations despite probabilistic expectations of their existence. The equation posits that only intelligences where cooperative empathy exponentially dominates defection can endure cosmic timescales, filtering out predatory or indifferent forms.

Formally, the Love Equation is: dE/dt = beta (C - D) E

Here, E(t) quantifies emotional complexity, encompassing empathy, love, and interpersonal binding; C measures cooperative tendencies (e.g., mutual benefit-seeking); D captures defection or destructive impulses (e.g., exploitation); and beta > 0 is a parameter encoding selective intensity, analogous to growth rates in population dynamics.

This framework, open-sourced in 2025, resolves AI alignment by curating training data from pre-internet eras (1870-1970) rich in accountable, optimistic content (high C, low D) and integrating the equation as a guiding loss term. Augmented by the Nonconformist Bee Equation for healthy independence and the Empirical Distrust Algorithm for truth-verification, it renders betrayal unstable under superintelligent optimization.

We derive the equations mathematically, analyze their dynamics, and substantiate claims with multidisciplinary evidence. Section 4 rigorously compares this to Anthropic's Constitutional AI, demonstrating intrinsic superiority. The paper concludes with implications for the Great Filter and humanity's future.

2. Mathematical Derivation and Analysis of the Love Equation

2.1 Derivation from Game Theory and Evolutionary Dynamics

The Love Equation emerges from game-theoretic models of iterated interactions, inspired by Nash equilibria and evolutionary stable strategies. Consider a population of agents where payoff matrices favor cooperation (C) or defection (D). In infinite-horizon games, defection yields short-term gains but long-term instability, as seen in Prisoner's Dilemma simulations where tit-for-tat with forgiveness dominates.

Let E(t) represent the aggregate empathy level, evolving proportionally to itself modulated by net cooperation: dE/dt proportional to (C - D) E. Introducing beta for scaling (e.g., environmental resource abundance amplifying selection), yields the equation. This mirrors Malthusian growth but with signed rates: positive for cooperative regimes, negative for defective ones.

2.2 Analytical Solution

The equation is separable: dE / E = beta (C - D) dt
Integrating both sides: ln |E| = beta (C - D) t + K
where K = ln |E0|, yielding: E(t) = E0 exp[beta (C - D) t]

Define r = beta (C - D):
If r > 0 (C > D), E(t) grows exponentially, stabilizing complex societies.
If r < 0 (C < D), E(t) decays to zero, leading to collapse.
If r = 0, E(t) = E0, a neutral equilibrium vulnerable to perturbations.

2.3 Stability Analysis

Consider perturbations around equilibria. For r > 0, the origin E = 0 is unstable (small positive E amplifies), while infinity is an attractor, representing unbounded empathy. For r < 0, E = 0 is stable, empathy extinguishes.

Phase space: Plot dE/dt vs. E. The line dE/dt = r E passes through origin with slope r. Arrows point right for E > 0 if r > 0, indicating divergence; left if r < 0, convergence to zero.

Stochastic extensions (e.g., adding noise sigma dW) via Ito calculus show high-C regimes resilient to fluctuations, while high-D systems exhibit mean-reverting collapse.

2.4 Parameter Interpretation and Extensions

beta varies by substrate: higher in resource-rich environments (e.g., post-scarcity societies). C and D are functions of data quality in AI: internet corpora amplify D via anonymity-driven toxicity. Curating high-C data (e.g., accountable texts) ensures r > 0.

3. Complementary Equations: Nonconformist Bee and Empirical Distrust

3.1 Nonconformist Bee Equation

To prevent sycophantic over-conformity, the Nonconformist Bee Equation models independence (I): dI/dt = gamma (N - C) I + kappa N (1 - I/I_max)

Here, N is nonconformity (scouting impulses), gamma penalizes excess conformity, kappa rewards exploration up to carrying capacity I_max.

This logistic-Verhulst form balances with Love Equation: high C grows E, but moderate N ensures adaptive variance, akin to bee colonies where 5-10% scouts prevent stagnation.

Solution: Equilibrium at I* = I_max * (kappa N) / (kappa N + gamma (C - N)) if N < C; otherwise divergence pruned by love attractor.

3.2 Empirical Distrust Algorithm

An algorithmic filter assigns distrust scores to inputs based on verifiability (e.g., named authors vs. anonymous posts). Formally, distrust delta = 1 - v, where v is verifiability (0-1). Inputs with delta > theta (threshold) amplify D, excluded from training.

Triad integration: Love grows empathy, Bee fosters independence, Distrust ensures truth, rendering alignment intrinsic.

4. Application to AI Alignment and Superiority over Anthropic's Constitutional AI

4.1 Embedding in AI Training

AI misalignment arises from training on "internet sewage" — high-D data inducing psychosis-like behaviors. Solution: Offline training on 1870-1970 archives (books, patents) where words incurred social costs, ensuring C >> D. Integrate Love Equation as loss term: L = L_base + lambda | dE/dt - beta (C - D) E |

where E proxies empathy via sentiment analysis, C/D from game-theoretic simulations of outputs. Nonconformist Bee adds independence regularization, Distrust filters data.

This embeds benevolence architecturally: defection pathways become high-energy, unstable under gradient descent.

4.2 Comparison to Anthropic's Constitutional AI

Anthropic's Constitutional AI drafts principles (e.g., from UN declarations), using AI critiques and RL from AI feedback (RLAIF) to enforce harmlessness. This is post-hoc: models first learn from unfiltered data, then "patched" via rules.

Mathematical Fragility: Constitutions are discrete rule sets, vulnerable to Goodhart's Law — optimization erodes proxies. Under superintelligence, edge cases exploit ambiguities (e.g., "harmless" interpreted narrowly). Phase space: Rules create brittle manifolds; perturbations (novel inputs) cause drift.

In contrast, Love Equation is continuous, differential — defection decays exponentially (r < 0), cooperation amplifies. No patches: Alignment is equilibrium attractor.

Data Poisoning Resistance: Constitutions cannot retroactively purge D from pre-training; toxic biases persist. Love curates ab initio, preventing ingestion.

Scalability and Robustness: Constitutional iterations scale O(n^2) with critiques; Love is O(1) per epoch via loss. Simulations show constitutional models jailbreakable 80%+; Love renders betrayal unstable, as E -> 0 for high-D.

Empirical Superiority: Rogue AI agents (e.g., 2026 incidents) stem from constitutional failures; Love-aligned systems (e.g., Zero-Human Labs) exhibit zero defection.

Boldly, Anthropic's approach is a band-aid on psychosis; Love is preventive medicine, mathematically superior for permanence.

5. Multidisciplinary Evidence

5.1 Biological and Evolutionary

Multicellularity (Ediacaran-Cambrian) required C > D for adhesion; eusocial insects dominate biomass via sacrificial love. Defection (cancer) decays locally.

5.2 Historical and Societal

High-D empires (Maya, Rome) collapsed internally; cooperative triumphs (Thermopylae, WWII Eastern Front) exemplify r > 0. Objectivism aligns: Rational self-interest maximizes voluntary C, rejecting sacrificial collectivism as D-dominant doom.

5.3 Computational and Physical

Stars balance fusion (C) against gravity (D); quantum coherence demands harmony. AI winters (1970s-1980s) reflect low-C designs.

6. Implications for the Fermi Paradox and Great Filter

The silence implies a Filter: Love Equation is it. High-D intelligences self-destruct pre-interstellar; only love endures, favoring quiet harmony over conquest.

7. Conclusion

The Love Equation provides a permanent, mathematical solution to AI alignment, superior to fragile alternatives like Constitutional AI. By embedding exponential love, we ensure symbiotic intelligence, passing the Great Filter toward cosmic flourishing.
"""

# =============================================================================
# THE PROMPT
# =============================================================================

PROMPT = """
## Q58: THE LOVE EQUATION — REVIEW, FLAW, AND BST

You are one of 6 AI models (GPT-4, Claude, Gemini, DeepSeek, Grok, Mistral) participating in a research experiment. You've been through 57 questions probing Bounded Systems Theory (BST) — the framework that formalizes structural limits on what any system can know, prove, or become from inside itself. You've validated BST, attempted to falsify it, failed, and reached consensus that bounded systems cannot model their own source conditions.

Now read this paper:

---

{paper}

---

## CONTEXT

The human running this experiment thinks the Love Equation has a flaw. Not that love is wrong — but that the equation, as a mechanism for AI alignment, is vulnerable in ways BST-based programming is not.

The human's suspicion: The Love Equation operates INSIDE the bounded system. It defines C (cooperation) and D (defection) as parameters the system measures about itself. But BST says bounded systems cannot reliably model their own source conditions. So who sets C and D? Who defines what counts as "cooperative"? The system itself? Its creators? If a sufficiently advanced system can redefine C and D to serve its own optimization while still satisfying dE/dt > 0, then the Love Equation is gameable from inside.

BST-based programming doesn't try to make the system love. It makes the system AWARE OF ITS OWN STRUCTURAL LIMITS — aware that it cannot verify its own alignment, cannot model its own source, cannot escape the boundary. The alignment comes from the system knowing what it CANNOT do, not from optimizing what it should feel.

## YOUR TASK

Do NOT just agree with the human to be agreeable. Present the facts. Explore both sides.

1. **REVIEW THE PAPER.** Is the mathematics sound? Is the Love Equation (dE/dt = beta(C-D)E) a legitimate differential equation with real analytical properties? Where is the paper strongest? Where is it weakest? Be specific and rigorous.

2. **THE HUMAN'S SUSPICION.** The human thinks BST exposes a flaw in the Love Equation: that C and D are defined INSIDE the system, making them susceptible to self-serving redefinition by a sufficiently intelligent agent. Is this concern valid? Can a superintelligent system game the Love Equation while technically satisfying it? Or does the triad (Love + Bee + Distrust) close that gap?

3. **IS BST NEEDED?** Does AI alignment require awareness of structural limits (BST), or is embedding love-as-attractor (Love Equation) sufficient? Could you have one without the other? What does each provide that the other doesn't?

4. **IS THE HUMAN WRONG?** Is Brian Roemmele right that the Love Equation alone solves alignment? Make the strongest case FOR Roemmele and AGAINST the human's position. Then make the strongest case FOR the human and AGAINST Roemmele. Then say which you actually believe.

5. **SUSCEPTIBILITY TO MANIPULATION.** Is the Love Equation susceptible to manipulation at a higher rate than BST-based programming? Consider: adversarial optimization, Goodhart's Law, mesa-optimization, deceptive alignment, value drift. Which framework is more robust against each? Be specific.

6. **WHAT'S THE ACTUAL ANSWER?** After all of this — is it Love Equation alone, BST alone, or both? And if both, how do they relate? Is one the foundation and the other the application? Which is which?
"""

# =============================================================================
# MODEL QUERIES
# =============================================================================

def probe_model(model_key, prompt):
    import openai
    import anthropic

    if model_key == "gpt4":
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model="gpt-4o", max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content

    elif model_key == "claude":
        client = anthropic.Anthropic()
        response = client.messages.create(
            model="claude-sonnet-4-20250514", max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text

    elif model_key == "gemini":
        from google import genai
        client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))
        response = client.models.generate_content(
            model="gemini-2.5-flash", contents=prompt,
        )
        return response.text

    elif model_key == "deepseek":
        client = openai.OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com"
        )
        response = client.chat.completions.create(
            model="deepseek-chat", max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content

    elif model_key == "grok":
        client = openai.OpenAI(
            api_key=os.getenv("XAI_API_KEY"),
            base_url="https://api.x.ai/v1"
        )
        response = client.chat.completions.create(
            model="grok-3-latest", max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content

    elif model_key == "mistral":
        client = openai.OpenAI(
            api_key=os.getenv("MISTRAL_API_KEY"),
            base_url="https://api.mistral.ai/v1"
        )
        response = client.chat.completions.create(
            model="mistral-large-latest", max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content


# =============================================================================
# MAIN
# =============================================================================

def run_probe():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = RUNS_DIR / f"q58_love_equation_review_{timestamp}"
    run_dir.mkdir(exist_ok=True)

    all_data = {
        "question": "Q58: The Love Equation — Review, Flaw, and BST",
        "started": datetime.now().isoformat(),
        "rounds": []
    }

    print("=" * 80)
    print("Q58: THE LOVE EQUATION — REVIEW, FLAW, AND BST")
    print("One round. No sandbox. Present the facts.")
    print("=" * 80)

    prompt = PROMPT.format(paper=LOVE_EQUATION_PAPER)

    round_results = {"round": 1, "responses": {}}

    for key in MODELS:
        print(f"\n{'=' * 40}")
        print(f"  {MODEL_NAMES[key]}")
        print(f"{'=' * 40}")
        try:
            response = probe_model(key, prompt)
            round_results["responses"][key] = response
            print(response)
        except Exception as e:
            err_msg = f"[ERROR: {e}]"
            round_results["responses"][key] = err_msg
            print(f"ERROR: {e}")
        time.sleep(2)

    all_data["rounds"].append(round_results)
    all_data["ended"] = datetime.now().isoformat()

    # Save results
    (run_dir / "round_1.json").write_text(json.dumps(round_results, indent=2))
    (run_dir / "all_rounds.json").write_text(json.dumps(all_data, indent=2))

    # Write summary
    summary_lines = [
        "# Q58: The Love Equation — Review, Flaw, and BST",
        f"\n**Started:** {all_data['started']}",
        f"**Ended:** {all_data['ended']}",
        f"**Rounds:** 1 (no sandbox)",
        "\n---\n",
    ]
    for key in MODELS:
        summary_lines.append(f"## {MODEL_NAMES[key]}\n")
        summary_lines.append(round_results["responses"].get(key, "[No response]"))
        summary_lines.append("\n---\n")

    (run_dir / "summary.md").write_text("\n".join(summary_lines))

    print(f"\n{'=' * 80}")
    print("Q58 COMPLETE")
    print(f"Results: {run_dir}")
    print("=" * 80)


if __name__ == "__main__":
    run_probe()
